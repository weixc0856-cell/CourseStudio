#!/usr/bin/env python3
"""Full JSON Schema Draft 2020-12 validation for the R2.1 contract.

Run with the project-local runtime:
  tools/contract-runtime/.venv/Scripts/python.exe tests/contract/validate_with_jsonschema.py

This script intentionally fails if jsonschema is unavailable; use mini_schema.py
only as a lightweight fallback, never as a substitute for this check.
"""
from __future__ import annotations

import json
import sys
from importlib.metadata import version
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except Exception as exc:  # pragma: no cover - explicit availability check
    print(f"BLOCKED: jsonschema unavailable: {exc}")
    raise SystemExit(2)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SCHEMAS = REPO / "schemas"
FIXTURES = HERE / "fixtures"
PASS_FIXTURE = FIXTURES / "minimal-pass"
NEGATIVE = FIXTURES / "negative"

SCHEMA_FILES = {
    "episode": "episode.schema.json",
    "claims": "claims.schema.json",
    "segments": "segments.schema.json",
    "recording": "recording.schema.json",
    "qa": "qa.schema.json",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate(instance, schema: dict) -> list[str]:
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in errors]


def main() -> int:
    schemas = {}
    failures: list[str] = []
    checks = 0

    for name, filename in SCHEMA_FILES.items():
        schema = load_json(SCHEMAS / filename)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            failures.append(f"schema {filename} is not valid Draft 2020-12: {exc}")
            continue
        schemas[name] = schema
        checks += 1

    positive = [
        ("episode", load_json(PASS_FIXTURE / "episode.json")),
        ("segments", load_json(PASS_FIXTURE / "segments.json")),
        ("recording", load_json(PASS_FIXTURE / "05_recording" / "manifest.json")),
        ("qa", load_json(PASS_FIXTURE / "qa" / "qa.static.json")),
        ("qa", load_json(PASS_FIXTURE / "qa" / "qa.runtime.json")),
    ]
    for index, claim in enumerate(load_jsonl(PASS_FIXTURE / "research" / "claims.jsonl")):
        positive.append(("claims", claim))

    for name, instance in positive:
        errors = validate(instance, schemas[name])
        checks += 1
        if errors:
            failures.append(f"positive {name}: {errors[:3]}")

    negative = [
        ("claims", NEGATIVE / "claims-missing-field.json", "claim_text"),
        ("claims", NEGATIVE / "claims-bad-enum.json", "claim_type"),
        ("claims", NEGATIVE / "claims-fact-without-source.json", "source_ids"),
        ("recording", NEGATIVE / "recording-verified-no-ffprobe.json", "ffprobe"),
        ("episode", NEGATIVE / "episode-bad-version.json", "contract_version"),
    ]
    for name, path, needle in negative:
        errors = validate(load_json(path), schemas[name])
        checks += 1
        if not errors:
            failures.append(f"negative {path.name}: expected a schema error, got none")
        elif not any(needle in error for error in errors):
            failures.append(f"negative {path.name}: errors do not mention {needle}: {errors[:3]}")

    # Semantic negative (order gap) is valid at schema level; it is covered by run_contract_tests.py.
    segments_gap = load_json(NEGATIVE / "segments-order-gap.json")
    errors = validate(segments_gap, schemas["segments"])
    checks += 1
    if errors:
        failures.append(f"segments-order-gap should be schema-valid but was not: {errors[:3]}")

    print(f"jsonschema {version('jsonschema')}")
    print(f"schema meta checks + instance checks: {checks}")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Status: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
