#!/usr/bin/env python3
"""Contract tests for the R1 design artifacts.

This runner validates the R1 fixtures against schemas/*.schema.json using the
local mini_schema subset, then applies semantic cross-reference and fault
injection checks. It is a design/test harness only; it does not call or modify
any production CourseStudio tool.

Run:
    python tests/contract/run_contract_tests.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import posixpath
import re
import sys
from pathlib import Path

import mini_schema

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SCHEMAS = REPO / "schemas"
FIXTURES = HERE / "fixtures"
PASS_FIXTURE = FIXTURES / "minimal-pass"
NEGATIVE = FIXTURES / "negative"

LEAK_PATTERNS = [
    ("record.html", r"record\.html"),
    ("CLM-###", r"\bCLM-\d+\b"),
    ("S01-style source ID", r"\bS\d{2}\b"),
    ("qa/ path", r"(?:^|/)qa/"),
    ("research/ path", r"(?:^|/)research/"),
    ("NOT_RUN", r"\bNOT_RUN\b"),
    ("PASS_VERIFIED", r"\bPASS_VERIFIED\b"),
]
LOCAL_URL_PREFIXES = ("#", "http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:")
SLIDE_RE = re.compile(r"""data-slide\s*=\s*["'](\d+)["']""")
RESOURCE_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_schema(name: str) -> dict:
    return load_json(SCHEMAS / f"{name}.schema.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_base() -> dict:
    return {
        "root": PASS_FIXTURE,
        "files": {},
        "episode": load_json(PASS_FIXTURE / "episode.json"),
        "claims": load_jsonl(PASS_FIXTURE / "research" / "claims.jsonl"),
        "sources": load_json(PASS_FIXTURE / "research" / "sources.json"),
        "segments": load_json(PASS_FIXTURE / "segments.json"),
        "recording": load_json(PASS_FIXTURE / "05_recording" / "manifest.json"),
        "qa_static": load_json(PASS_FIXTURE / "qa" / "qa.static.json"),
        "qa_runtime": load_json(PASS_FIXTURE / "qa" / "qa.runtime.json"),
        "acceptance": load_json(PASS_FIXTURE / "acceptance.json"),
    }


def read_bytes(data: dict, rel: str) -> bytes | None:
    if rel in data["files"]:
        value = data["files"][rel]
        return value.encode("utf-8") if isinstance(value, str) else value
    path = data["root"] / rel
    if not path.is_file():
        return None
    return path.read_bytes()


def read_text(data: dict, rel: str) -> str | None:
    raw = read_bytes(data, rel)
    return None if raw is None else raw.decode("utf-8", errors="replace")


def exists(data: dict, rel: str) -> bool:
    return read_bytes(data, rel) is not None


def sha256(data: dict, rel: str) -> str | None:
    raw = read_bytes(data, rel)
    return None if raw is None else sha256_bytes(raw)


def resolve_relative(base_file: str, target: str) -> str:
    base_dir = posixpath.dirname(base_file) or "."
    return posixpath.normpath(posixpath.join(base_dir, target))


def schema_errors(data: dict) -> list[str]:
    errors: list[str] = []
    errors.extend(f"episode: {e}" for e in mini_schema.validate(data["episode"], load_schema("episode")))
    claims_schema = load_schema("claims")
    for index, claim in enumerate(data["claims"]):
        errors.extend(f"claims[{index}]: {e}" for e in mini_schema.validate(claim, claims_schema))
    errors.extend(f"segments: {e}" for e in mini_schema.validate(data["segments"], load_schema("segments")))
    errors.extend(f"recording: {e}" for e in mini_schema.validate(data["recording"], load_schema("recording")))
    if data["qa_static"] is not None:
        errors.extend(f"qa.static: {e}" for e in mini_schema.validate(data["qa_static"], load_schema("qa")))
    if data["qa_runtime"] is not None:
        errors.extend(f"qa.runtime: {e}" for e in mini_schema.validate(data["qa_runtime"], load_schema("qa")))
    return errors


def semantic_result(data: dict) -> dict:
    errors: list[str] = []
    blocked: list[str] = []
    pending: list[str] = []

    # --- claims -----------------------------------------------------------
    claim_ids = [claim["claim_id"] for claim in data["claims"]]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("duplicate claim_id in claims")

    source_ids = {source["source_id"] for source in data["sources"].get("sources", [])}
    segment_ids = {segment["segment_id"] for segment in data["segments"]["segments"]}
    segment_by_id = {segment["segment_id"]: segment for segment in data["segments"]["segments"]}

    deck_text = read_text(data, "slides/index.html")
    slide_ids = set()
    if deck_text is not None:
        slide_ids = {f"SLD-{int(value):02d}" for value in SLIDE_RE.findall(deck_text)}

    for claim in data["claims"]:
        ids = set(claim["source_ids"])
        locator_ids = {locator["source_id"] for locator in claim["source_locators"]}
        if ids != locator_ids:
            errors.append(f"{claim['claim_id']}: source_ids and source_locators disagree")
        for source_id in ids:
            if source_id not in source_ids:
                errors.append(f"{claim['claim_id']}: unknown source {source_id}")
        for artifact in claim["used_in_artifact"]:
            if artifact.startswith("SLD-") and artifact not in slide_ids:
                errors.append(f"{claim['claim_id']}: used_in_artifact {artifact} has no deck slide")
            elif artifact.startswith("SEG-") and artifact not in segment_ids:
                errors.append(f"{claim['claim_id']}: used_in_artifact {artifact} has no segment")
            elif artifact.startswith(("CUE-", "REC-")):
                suffix = artifact.split("-", 1)[1]
                if f"SEG-{suffix}" not in segment_ids:
                    errors.append(f"{claim['claim_id']}: used_in_artifact {artifact} has no matching segment")
        if claim["evidence_status"] == "DIRECTLY_SUPPORTED" and claim["validation_status"] == "NOT_RUN":
            errors.append(f"{claim['claim_id']}: DIRECTLY_SUPPORTED requires a completed validation")

    # --- segments ---------------------------------------------------------
    orders = [segment["order"] for segment in data["segments"]["segments"]]
    if orders and sorted(orders) != list(range(1, len(orders) + 1)):
        errors.append("segment order must be continuous 1..N; found " + ", ".join(map(str, orders)))
    if len(segment_ids) != len(data["segments"]["segments"]):
        errors.append("duplicate segment_id in segments")

    for segment in data["segments"]["segments"]:
        if segment["engine"] == "motion" and not (45 <= segment["duration_seconds"] <= 90):
            errors.append(f"{segment['segment_id']}: motion duration outside 45-90s")
        if segment["actual_source"] != "NOT_VERIFIED":
            if segment["actual_seconds"] is None:
                errors.append(f"{segment['segment_id']}: actual_source is set but actual_seconds is null")
            elif abs(float(segment["actual_seconds"]) - float(segment["declared_seconds"])) > 0.5:
                errors.append(
                    f"{segment['segment_id']}: actual duration {segment['actual_seconds']}s "
                    f"does not match declared {segment['declared_seconds']}s"
                )
        for path in (segment["scene"], segment["project"], segment["cue"]):
            if not exists(data, path):
                errors.append(f"{segment['segment_id']}: missing required file {path}")

    # --- recording --------------------------------------------------------
    rec_tasks = data["recording"]["segments"]
    rec_orders = [task["order"] for task in rec_tasks]
    if sorted(rec_orders) != list(range(1, len(rec_tasks) + 1)):
        errors.append("recording order must be continuous 1..N; found " + ", ".join(map(str, rec_orders)))
    if len(rec_tasks) != len(segment_ids):
        errors.append("recording task count does not match segment count")
    for task in rec_tasks:
        if task["segment_id"] not in segment_by_id:
            errors.append(f"recording task {task['segment_id']} has no segment")
            continue
        segment = segment_by_id[task["segment_id"]]
        if task["order"] != segment["order"]:
            errors.append(f"recording order {task['order']} does not match segment order {segment['order']}")
        if task["cue"] != segment["cue"]:
            errors.append(f"recording cue {task['cue']} does not match segment cue {segment['cue']}")
        if task["record_status"] == "VERIFIED":
            if "recording" not in task or "ffprobe" not in task:
                errors.append(f"recording task {task['segment_id']} is VERIFIED without recording/ffprobe")
                continue
            recording_path = task["recording"]["path"]
            actual_sha = sha256(data, recording_path)
            if actual_sha is None:
                errors.append(f"recording task {task['segment_id']}: missing file {recording_path}")
            elif actual_sha != task["recording"]["sha256"]:
                errors.append(f"recording task {task['segment_id']}: file hash mismatch")
            if abs(float(task["ffprobe"]["duration_seconds"]) - float(task["declared_seconds"])) > 2.0:
                errors.append(
                    f"recording task {task['segment_id']}: ffprobe duration differs from declared by more than 2s"
                )

    # --- deck -------------------------------------------------------------
    if deck_text is None:
        errors.append("missing slides/index.html")
    else:
        values = [int(value) for value in SLIDE_RE.findall(deck_text)]
        if values and values != list(range(1, len(values) + 1)):
            errors.append("deck data-slide values must be strictly 1..N")
        for raw in RESOURCE_RE.findall(deck_text):
            value = raw.strip()
            if not value or value.startswith(LOCAL_URL_PREFIXES):
                continue
            path_part = value.split("#", 1)[0].split("?", 1)[0].strip()
            if not path_part:
                continue
            resolved = resolve_relative("slides/index.html", path_part)
            if not exists(data, resolved):
                errors.append(f"missing local asset: {path_part}")
        for label, pattern in LEAK_PATTERNS:
            if re.search(pattern, deck_text):
                errors.append(f"audience leak: {label}")

    # --- QA ---------------------------------------------------------------
    def check_qa(qa: dict | None, label: str) -> None:
        if qa is None:
            blocked.append(f"missing {label} run")
            return
        statuses = [check["status"] for check in qa["checks"]]
        derived = "FAIL" if "FAIL" in statuses else ("BLOCKED" if ("BLOCKED" in statuses or "NOT_RUN" in statuses) else "PASS")
        if qa["status"] != derived:
            errors.append(f"{label}: run status {qa['status']} does not match check statuses {derived}")
        for check in qa["checks"]:
            if check["status"] == "PASS" and check.get("exit_code") not in (0, None):
                errors.append(f"{label}: PASS check {check['check_id']} has non-zero exit code")
            if check["status"] == "FAIL":
                errors.append(f"{label}: QA check failed: {check['check_id']} ({check['scope']})")
            if check["status"] == "NOT_RUN" and not check.get("notes"):
                errors.append(f"{label}: NOT_RUN check {check['check_id']} has no reason")
            for item in check.get("inputs", []):
                actual = sha256(data, item["path"])
                if actual is None:
                    errors.append(f"{label}: missing QA input {item['path']}")
                elif actual != item["sha256"]:
                    blocked.append(f"{label}: stale QA input {item['path']}")

    check_qa(data["qa_static"], "qa.static")
    check_qa(data["qa_runtime"], "qa.runtime")

    # --- episode consistency ---------------------------------------------
    stages = data["episode"]["stages"]
    for stage_name, record in stages.items():
        for dimension, value in record["status"].items():
            if value in ("FAIL", "REJECTED"):
                errors.append(f"episode stage {stage_name}.{dimension} is {value}")
            elif value == "NOT_RUN":
                blocked.append(f"episode stage {stage_name}.{dimension} is NOT_RUN")
            elif value in ("PENDING", "NEEDS_REVIEW"):
                pending.append(f"episode stage {stage_name}.{dimension} is {value}")

    if stages["qa.static"]["status"]["STRUCTURAL"] == "PASS" and (data["qa_static"] is None or data["qa_static"]["status"] != "PASS"):
        errors.append("episode qa.static is PASS but qa.static run is missing or not PASS")
    if stages["qa.runtime"]["status"]["RUNTIME"] == "PASS":
        if data["qa_runtime"] is None:
            blocked.append("episode qa.runtime is PASS but no runtime run exists")
        elif data["qa_runtime"]["status"] != "PASS":
            errors.append("episode qa.runtime is PASS but runtime run is not PASS")
    if stages["content.review"]["status"]["CONTENT_QUALITY"] == "PASS" and data["acceptance"].get("decision") != "PASS":
        errors.append("episode content.review is PASS but acceptance.json is not PASS")
    if stages["record"]["status"]["RECORDING"] == "PASS":
        verified = [task for task in rec_tasks if task["record_status"] == "VERIFIED"]
        if not verified:
            errors.append("episode record is PASS but no VERIFIED recording task exists")

    # Every artifact reference in the episode must match the current file hash.
    for stage_name, record in stages.items():
        for ref in list(record.get("inputs", [])) + list(record.get("outputs", [])):
            actual = sha256(data, ref["path"])
            if actual is None:
                errors.append(f"episode stage {stage_name}: missing artifact {ref['path']}")
            elif actual != ref["sha256"]:
                blocked.append(f"episode stage {stage_name}: stale artifact {ref['path']}")

    if errors:
        status, exit_code = "FAIL", 1
    elif blocked:
        status, exit_code = "BLOCKED", 2
    elif pending:
        status, exit_code = "NEEDS_REVIEW", 2
    else:
        status, exit_code = "PASS", 0

    delivery = "READY" if status == "PASS" else "NOT_READY"
    reasons = errors + blocked + pending
    return {
        "status": status,
        "exit_code": exit_code,
        "delivery": delivery,
        "reasons": reasons,
        "errors": errors,
        "blocked": blocked,
        "pending": pending,
    }


def evaluate(data: dict) -> dict:
    schema = schema_errors(data)
    if schema:
        return {
            "status": "CONTRACT_ERROR",
            "exit_code": 3,
            "delivery": "NOT_READY",
            "reasons": schema,
            "errors": schema,
            "blocked": [],
            "pending": [],
        }
    return semantic_result(data)


def apply_case(case_id: str, base: dict) -> dict:
    data = copy.deepcopy(base)
    data["files"] = {}
    if case_id == "missing_required_field":
        data["claims"][0].pop("claim_text", None)
    elif case_id == "duplicate_claim_id":
        duplicate = copy.deepcopy(data["claims"][0])
        duplicate["claim_text"] = "Duplicate claim fixture."
        data["claims"].append(duplicate)
    elif case_id == "unresolved_source":
        data["claims"][0]["source_ids"] = ["SRC-404"]
        data["claims"][0]["source_locators"] = [{"source_id": "SRC-404", "locator": "fixture://missing"}]
    elif case_id == "missing_deck_asset":
        deck = read_text(data, "slides/index.html") or ""
        data["files"]["slides/index.html"] = deck.replace(
            "</head>", '<link rel="stylesheet" href="./assets/missing.css" />\n  </head>'
        )
    elif case_id == "animation_type_error":
        check = data["qa_runtime"]["checks"][0]
        check["status"] = "FAIL"
        check["exit_code"] = 1
        check["failure"] = {"reason": "synthetic typecheck error", "recovery": "fix the scene"}
        data["qa_runtime"]["status"] = "FAIL"
        data["episode"]["stages"]["qa.runtime"]["status"]["RUNTIME"] = "FAIL"
    elif case_id == "actual_duration_mismatch":
        data["segments"]["segments"][0]["actual_seconds"] = 75.0
    elif case_id == "cue_order_mismatch":
        data["recording"]["segments"][0]["order"] = 2
    elif case_id == "missing_runtime_evidence":
        data["qa_runtime"] = None
        data["episode"]["stages"]["qa.runtime"]["status"]["RUNTIME"] = "NOT_RUN"
    elif case_id == "audience_leak":
        deck = read_text(data, "slides/index.html") or ""
        data["files"]["slides/index.html"] = deck.replace(
            "</body>", '<p>record.html?segment=seg_one</p>\n  </body>'
        )
    elif case_id == "content_needs_review":
        data["acceptance"]["decision"] = "NEEDS_REVIEW"
        data["episode"]["stages"]["content.review"]["status"]["CONTENT_QUALITY"] = "NEEDS_REVIEW"
    elif case_id == "stale_qa":
        script = read_text(data, "script.md") or ""
        data["files"]["script.md"] = script + "\n<!-- changed after QA -->\n"
    else:
        raise ValueError(f"unknown fault case: {case_id}")
    return data


def negative_tests() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    checks = [
        ("claims-missing-field.json", "claims", "claim_text"),
        ("claims-bad-enum.json", "claims", "claim_type"),
        ("claims-fact-without-source.json", "claims", "source_ids"),
        ("recording-verified-no-ffprobe.json", "recording", "ffprobe"),
        ("episode-bad-version.json", "episode", "contract_version"),
    ]
    for filename, schema_name, needle in checks:
        payload = load_json(NEGATIVE / filename)
        errors = mini_schema.validate(payload, load_schema(schema_name))
        found = any(needle in error for error in errors)
        results.append((f"negative schema: {filename}", found, "; ".join(errors[:3])))

    segments_payload = load_json(NEGATIVE / "segments-order-gap.json")
    errors = mini_schema.validate(segments_payload, load_schema("segments"))
    # Schema is allowed to pass; the order gap is a semantic rule.
    if errors:
        results.append(("negative semantic: segments-order-gap.json", False, "; ".join(errors[:3])))
    else:
        orders = [segment["order"] for segment in segments_payload["segments"]]
        ok = sorted(orders) != list(range(1, len(orders) + 1))
        results.append(("negative semantic: segments-order-gap.json", ok, f"orders={orders}"))
    return results


def main() -> int:
    base = load_base()
    failures: list[str] = []
    passed = 0

    # Positive schema validation.
    for index, claim in enumerate(base["claims"]):
        errs = mini_schema.validate(claim, load_schema("claims"))
        if errs:
            failures.append(f"positive claims[{index}]: {errs[0]}")
        else:
            passed += 1
    for name, payload in [
        ("episode", base["episode"]),
        ("segments", base["segments"]),
        ("recording", base["recording"]),
        ("qa.static", base["qa_static"]),
        ("qa.runtime", base["qa_runtime"]),
    ]:
        errs = mini_schema.validate(payload, load_schema(name.split(".")[0]))
        if errs:
            failures.append(f"positive {name}: {errs[0]}")
        else:
            passed += 1

    # Positive end-to-end evaluation.
    result = evaluate(base)
    if (
        result["status"] == "PASS"
        and result["exit_code"] == 0
        and result["delivery"] == "READY"
        and base["episode"]["delivery"]["status"] == result["delivery"]
    ):
        passed += 1
    else:
        failures.append(
            f"positive episode: expected PASS/0/READY with matching delivery, got {result['status']}/{result['exit_code']}/{result['delivery']}: "
            + "; ".join(result["reasons"][:5])
        )

    # Negative fixtures.
    for name, ok, detail in negative_tests():
        if ok:
            passed += 1
        else:
            failures.append(f"{name}: {detail}")

    # Fault injection.
    cases = load_json(HERE / "fault-cases.json")["cases"]
    for case in cases:
        data = apply_case(case["id"], base)
        result = evaluate(data)
        expected = case["expected"]
        reason_text = " | ".join(result["reasons"]).lower()
        ok = (
            result["status"] == expected["status"]
            and result["exit_code"] == expected["exit_code"]
            and result["delivery"] == expected["delivery"]
            and expected["reason_contains"].lower() in reason_text
        )
        if ok:
            passed += 1
        else:
            failures.append(
                f"fault {case['id']}: expected {expected}, got {result['status']}/{result['exit_code']}/{result['delivery']} "
                f"reasons={result['reasons'][:5]}"
            )

    print(f"contract tests: {passed} passed, {len(failures)} failed")
    for failure in failures:
        print(f"  - FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
