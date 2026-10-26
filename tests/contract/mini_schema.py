"""Minimal JSON Schema validator for the CourseStudio R1 contract subset.

This is NOT a full Draft 2020-12 implementation. It intentionally supports only
the keywords used by schemas/*.schema.json:

  $ref (local #/$defs/...), type, required, properties, additionalProperties,
  enum, const, pattern, minLength, maxLength, minimum, maximum, minItems,
  maxItems, uniqueItems, items, allOf, anyOf, oneOf, if/then/else.

`format` is ignored. External $refs are rejected. The production contract must
be validated with a full implementation (for example the `jsonschema` package)
once that dependency is approved; that step is NOT_RUN in R1.
"""
from __future__ import annotations

import re
from typing import Any


class SchemaError(Exception):
    pass


def _resolve_local_ref(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise SchemaError(f"only local $ref is supported, got {ref!r}")
    node: Any = root
    for raw in ref[2:].split("/"):
        part = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"cannot resolve $ref {ref!r}")
        node = node[part]
    if not isinstance(node, dict):
        raise SchemaError(f"$ref {ref!r} does not point to an object")
    return node


def _is_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise SchemaError(f"unsupported type {expected!r}")


def validate(instance: Any, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    """Return a list of human-readable errors. Empty list means valid."""
    if root is None:
        root = schema
    errors: list[str] = []

    if "$ref" in schema:
        target = _resolve_local_ref(schema["$ref"], root)
        return validate(instance, target, root, path)

    for sub in schema.get("allOf", []):
        errors.extend(validate(instance, sub, root, path))

    if "anyOf" in schema:
        branches = [validate(instance, sub, root, path) for sub in schema["anyOf"]]
        if not any(not branch for branch in branches):
            errors.append(f"{path}: no anyOf branch matched")

    if "oneOf" in schema:
        branches = [validate(instance, sub, root, path) for sub in schema["oneOf"]]
        if sum(1 for branch in branches if not branch) != 1:
            errors.append(f"{path}: oneOf requires exactly one matching branch")

    if "if" in schema:
        condition_ok = not validate(instance, schema["if"], root, path)
        if condition_ok and "then" in schema:
            errors.extend(validate(instance, schema["then"], root, path))
        elif not condition_ok and "else" in schema:
            errors.extend(validate(instance, schema["else"], root, path))

    if "type" in schema:
        expected = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(instance, item) for item in expected):
            errors.append(f"{path}: expected type {expected}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} is not in enum {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: string longer than {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: string does not match pattern {schema['pattern']!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value {instance} is below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value {instance} is above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array has fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array has more than {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            seen = []
            for item in instance:
                if item in seen:
                    errors.append(f"{path}: duplicate item {item!r}")
                seen.append(item)
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], root, f"{path}[{index}]"))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate(value, properties[key], root, f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(validate(value, additional, root, f"{path}.{key}"))

    return errors
