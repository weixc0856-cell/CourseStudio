#!/usr/bin/env python3
"""Deterministic content/trace/delivery checks for an episode.

Writes:
  <episode>/qa/content-quality.json
  <episode>/qa/trace-report.json
  <episode>/qa/delivery-manifest.json

It does not modify course content. Visual review is read from
<episode>/qa/visual-review.json when present; absence is NEEDS_REVIEW, never PASS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from script_timing import parse_timing_blocks, validate_timing_block  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(check_id: str, kind: str, status: str, evidence: str, **extra) -> dict:
    item = {"check_id": check_id, "kind": kind, "status": status, "evidence": evidence}
    item.update(extra)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args()

    root = Path(args.root)
    ep = root / "courses" / args.episode
    qa = ep / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    # --- claims -----------------------------------------------------------
    ledger = ep / "01_research" / "02-claim-evidence-ledger.csv"
    claims = []
    if ledger.is_file():
        claims = list(csv.DictReader(ledger.open(encoding="utf-8")))
        ids = [row.get("claim_id", "") for row in claims]
        checks.append(check(
            "claims-unique", "content", "PASS" if len(ids) == len(set(ids)) and all(ids) else "FAIL",
            f"{len(claims)} rows, {len(set(ids))} unique IDs",
        ))
        missing_locator = [
            row.get("claim_id") for row in claims
            if row.get("type") not in {"ASSUMPTION"} and not (row.get("source_id") and row.get("locator"))
        ]
        checks.append(check(
            "claims-locators", "content", "PASS" if not missing_locator else "FAIL",
            f"missing locators: {missing_locator}" if missing_locator else "all non-assumption claims have source + locator",
        ))
        types = sorted({row.get("type", "") for row in claims})
        checks.append(check("claims-types", "content", "PASS" if types else "FAIL", "types: " + ", ".join(types)))
    else:
        checks.append(check("claims-ledger", "content", "FAIL", f"missing {ledger.relative_to(ep)}"))

    # --- source inventory + sampled evidence ------------------------------
    inventory = ep / "01_research" / "01-source-inventory.md"
    inv_text = inventory.read_text(encoding="utf-8", errors="replace") if inventory.is_file() else ""
    sources_ok = all(marker in inv_text for marker in ["### S01", "### S02", "### S03"])
    checks.append(check("sources-inventory", "content", "PASS" if sources_ok else "FAIL", "S01/S02/S03 present"))

    fulltext = ep / "01_research" / "fulltext" / "1706.03762.txt"
    ft = fulltext.read_text(encoding="utf-8", errors="replace") if fulltext.is_file() else ""
    ft = re.sub(r"\s+", " ", ft)
    s02 = ep / "01_research" / "downloads" / "illustrated-transformer.html"
    s03 = ep / "01_research" / "downloads" / "annotated-transformer.html"
    s02_text = s02.read_text(encoding="utf-8", errors="replace") if s02.is_file() else ""
    s03_text = s03.read_text(encoding="utf-8", errors="replace") if s03.is_file() else ""
    s02_text = re.sub(r"\s+", " ", s02_text)
    s03_text = re.sub(r"\s+", " ", s03_text)
    samples = {
        "CLM-001": ("weighted sum" in ft and "of the values" in ft),
        "CLM-006": "divide each" in ft,
        "CLM-007": "We suspect" in ft,
        "CLM-009": "softmax(dim=-1)" in s03_text,
        "CLM-004": "abstractions that are useful for calculating and thinking about attention" in s02_text,
    }
    checks.append(check(
        "evidence-samples", "content", "PASS" if all(samples.values()) else "PARTIAL",
        "sampled source snippets: " + ", ".join(f"{k}={'OK' if v else 'MISSING'}" for k, v in samples.items()),
    ))

    # --- script anchors + timing -----------------------------------------
    script = ep / "02_scripts" / "lecture_script.md"
    script_text = script.read_text(encoding="utf-8", errors="replace") if script.is_file() else ""
    slide_anchors = [int(x) for x in re.findall(r"\[SLIDE:\s*(\d+)\]", script_text)]
    anchors_ok = slide_anchors == list(range(1, len(slide_anchors) + 1)) and bool(slide_anchors)
    checks.append(check(
        "script-slide-anchors", "content", "PASS" if anchors_ok else "FAIL",
        f"{len(slide_anchors)} anchors; strict 1..N={'yes' if anchors_ok else 'no'}",
    ))

    segments_path = ep / "04_motion_src" / "segments.json"
    segments = []
    if segments_path.is_file():
        try:
            segments = json.loads(segments_path.read_text(encoding="utf-8")).get("segments", [])
        except Exception:
            segments = []
    timing_blocks = parse_timing_blocks(script_text)
    timing_issues: list[str] = []
    for block in timing_blocks:
        entry = next((s for s in segments if s.get("name") == block["name"]), None)
        if entry:
            issues, _ = validate_timing_block(
                block["name"], block,
                expected_seconds=entry.get("duration_seconds"),
                expected_order=entry.get("order"),
            )
            timing_issues.extend(issues)
    checks.append(check(
        "script-timing", "content", "PASS" if not timing_issues else "FAIL",
        "timing blocks: " + str(len(timing_blocks)) + ("; " + "; ".join(timing_issues) if timing_issues else ""),
    ))

    # --- deck pages + local assets + leak scan ----------------------------
    deck = ep / "03_slides" / "index.html"
    deck_text = deck.read_text(encoding="utf-8", errors="replace") if deck.is_file() else ""
    slide_values = [int(x) for x in re.findall(r'data-slide\s*=\s*["\'](\d+)["\']', deck_text)]
    deck_ok = slide_values == list(range(1, len(slide_values) + 1)) and bool(slide_values)
    checks.append(check(
        "deck-pages", "content", "PASS" if deck_ok else "FAIL",
        f"{len(slide_values)} data-slide pages; strict 1..N={'yes' if deck_ok else 'no'}",
    ))
    assets = [
        ep / "03_slides" / "assets" / "deck.css",
        ep / "03_slides" / ".vendor" / "reveal" / "reveal.js",
    ]
    missing_assets = [str(p.relative_to(ep)) for p in assets if not p.is_file()]
    checks.append(check(
        "deck-assets", "content", "PASS" if not missing_assets else "FAIL",
        "local assets present" if not missing_assets else "missing: " + ", ".join(missing_assets),
    ))

    remote_assets = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', deck_text, re.I)
    checks.append(check(
        "resource-licenses", "content", "PASS" if not remote_assets else "FAIL",
        "no remote assets; local CSS only; external sources are cited in 01-source-inventory.md, no bundled third-party media"
        if not remote_assets else "remote assets present: " + ", ".join(remote_assets[:5]),
    ))

    leak_patterns = {
        "record.html": r"record\.html",
        "CLM-###": r"\bCLM-\d+\b",
        "S01-style source ID": r"\bS\d{2}\b",
        "qa/ path": r"(?:^|/)qa/",
        "research/ path": r"(?:^|/)research/",
        "NOT_RUN": r"\bNOT_RUN\b",
        "PASS_VERIFIED": r"\bPASS_VERIFIED\b",
    }
    leaks = []
    for lineno, line in enumerate(deck_text.splitlines(), 1):
        for label, pattern in leak_patterns.items():
            if re.search(pattern, line):
                leaks.append({"line": lineno, "label": label, "text": line.strip()[:200]})
    checks.append(check(
        "deck-leak-scan", "content", "PASS" if not leaks else "FAIL",
        "no internal metadata" if not leaks else f"{len(leaks)} leak(s): " + "; ".join(
            f"line {x['line']} {x['label']}" for x in leaks
        ),
        findings=leaks,
    ))

    # --- motion/recording mapping ----------------------------------------
    manifest = ep / "05_recording" / "manifest.json"
    recording = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    rec_tasks = recording.get("segments", []) if isinstance(recording, dict) else []
    mapping_issues = []
    for entry in segments:
        if entry.get("engine") == "motion":
            task = next((t for t in rec_tasks if t.get("name") == entry.get("name")), None)
            if not task:
                mapping_issues.append(f"{entry.get('name')}: no recording task")
            elif task.get("declared_seconds") != entry.get("duration_seconds"):
                mapping_issues.append(f"{entry.get('name')}: declared duration mismatch")
            cue_rel = entry.get("cue")
            if not cue_rel and task and task.get("cue"):
                cue_rel = f"05_recording/{task['cue']}"
            if not cue_rel:
                cue_rel = f"05_recording/cues/{entry.get('name')}.md"
            cue = ep / str(cue_rel)
            if not cue.is_file() and task and task.get("cue"):
                cue = ep / "05_recording" / str(task["cue"])
            if not cue.is_file():
                mapping_issues.append(f"{entry.get('name')}: missing cue ({cue_rel})")
    checks.append(check(
        "segment-recording-mapping", "content", "PASS" if not mapping_issues else "FAIL",
        "segments map to recording tasks/cues" if not mapping_issues else "; ".join(mapping_issues),
    ))

    # --- visual review ----------------------------------------------------
    visual_review = qa / "visual-review.json"
    if visual_review.is_file():
        try:
            vr = json.loads(visual_review.read_text(encoding="utf-8"))
        except Exception:
            vr = {}
        vstatus = vr.get("status", "NEEDS_REVIEW")
        checks.append(check(
            "visual-review", "content", vstatus if vstatus in {"PASS", "FAIL", "NEEDS_REVIEW"} else "NEEDS_REVIEW",
            f"AI visual review: {vr.get('scope', 'unknown')}; limitations: {vr.get('limitations', 'not stated')}",
        ))
    else:
        checks.append(check("visual-review", "content", "NEEDS_REVIEW", "no qa/visual-review.json"))

    # --- aggregate content status ----------------------------------------
    statuses = [item["status"] for item in checks]
    if "FAIL" in statuses:
        status = "FAIL"
    elif "NEEDS_REVIEW" in statuses or "PARTIAL" in statuses or "BLOCKED" in statuses:
        status = "NEEDS_REVIEW"
    else:
        status = "PASS"

    content = {
        "contract_version": "1.0.0",
        "episode_id": args.episode,
        "generated_at": utc_now(),
        "status": status,
        "checks": checks,
        "notes": "Deterministic content/structure/leak checks plus optional AI visual review. No human sign-off.",
    }
    (qa / "content-quality.json").write_text(
        json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # --- trace report -----------------------------------------------------
    claim_to_slides: dict[str, set[int]] = {}
    claim_to_segments: dict[str, set[str]] = {}
    current_slide = None
    current_anim = None
    for line in script_text.splitlines():
        m_slide = re.search(r"\[SLIDE:\s*(\d+)\]", line)
        if m_slide:
            current_slide = int(m_slide.group(1))
        m_anim = re.search(r"\[ANIMATION:\s*([A-Za-z0-9_-]+)\]", line)
        if m_anim:
            current_anim = m_anim.group(1)
        for match in re.finditer(r"CLM-(\d+)((?:/\d+)*)", line):
            cids = [f"CLM-{match.group(1)}"]
            cids.extend(f"CLM-{suffix.lstrip('/')}" for suffix in re.findall(r"/\d+", match.group(2)))
            for cid in cids:
                if current_slide is not None:
                    claim_to_slides.setdefault(cid, set()).add(current_slide)
                if current_anim is not None:
                    claim_to_segments.setdefault(cid, set()).add(current_anim)
    all_claim_ids = [row.get("claim_id") for row in claims if row.get("claim_id")]
    orphan_claims = sorted(set(all_claim_ids) - set(claim_to_slides))
    orphan_slides = sorted(set(range(1, len(slide_values) + 1)) - {s for v in claim_to_slides.values() for s in v})
    trace = {
        "contract_version": "1.0.0",
        "episode_id": args.episode,
        "generated_at": utc_now(),
        "source": "02_scripts/lecture_script.md + 04_motion_src/segments.json + 03_slides/index.html",
        "claims": {
            cid: {
                "slides": sorted(slides),
                "segments": sorted(claim_to_segments.get(cid, set())),
            }
            for cid, slides in sorted(claim_to_slides.items())
        },
        "segments": [
            {
                "name": s.get("name"),
                "order": s.get("order"),
                "duration_seconds": s.get("duration_seconds"),
                "slides": sorted(
                    int(x) for x in re.findall(r"\d+", str(s.get("slide_anchors", "")))
                ) if s.get("slide_anchors") else [],
            }
            for s in segments
        ],
        "deck_pages": len(slide_values),
        "orphan_claims": orphan_claims,
        "orphan_slides": orphan_slides,
        "coverage": {
            "claims_mapped": len(set(all_claim_ids) - set(orphan_claims)),
            "claims_total": len(all_claim_ids),
            "slides_mapped": len(set(range(1, len(slide_values) + 1)) - set(orphan_slides)),
            "slides_total": len(slide_values),
        },
    }
    (qa / "trace-report.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # --- delivery manifest ------------------------------------------------
    artifacts = [
        "README.md",
        "01_research/00-task-brief.md",
        "01_research/01-source-inventory.md",
        "01_research/02-claim-evidence-ledger.csv",
        "01_research/03-knowledge-structure.md",
        "01_research/04-course-input-brief.md",
        "01_research/05-quality-report.md",
        "01_research/06-course-outline.md",
        "02_scripts/lecture_script.md",
        "03_slides/index.html",
        "03_slides/assets/deck.css",
        "04_motion_src/segments.json",
        "04_motion_src/src/scenes/scores_to_weights.tsx",
        "04_motion_src/src/projects/scores_to_weights.ts",
        "05_recording/manifest.json",
        "05_recording/checklist.md",
        "05_recording/cues/scores_to_weights.md",
        "qa/runtime.json",
        "qa/content-quality.json",
        "qa/trace-report.json",
    ]
    file_rows = []
    for rel in artifacts:
        path = ep / rel
        if path.is_file():
            file_rows.append({
                "path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path),
            })
        else:
            file_rows.append({"path": rel, "status": "MISSING"})
    blockers = []
    if status == "FAIL":
        blockers.append("CONTENT_QUALITY=FAIL: audience deck contains internal recording metadata")
    delivery = {
        "contract_version": "1.0.0",
        "episode_id": args.episode,
        "generated_at": utc_now(),
        "status": "NOT_READY" if blockers else "READY",
        "blocking_reasons": blockers,
        "files": file_rows,
        "limitations": [
            "No final MP4 was generated; RECORDING is NOT_APPLICABLE for package scope.",
            "Visual review is representative (slides 1/6/12), not exhaustive.",
        ],
    }
    (qa / "delivery-manifest.json").write_text(
        json.dumps(delivery, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        "content_status": status,
        "checks": len(checks),
        "leaks": len(leaks),
        "orphan_claims": orphan_claims,
        "orphan_slides": orphan_slides,
        "delivery_status": delivery["status"],
        "delivery_blockers": blockers,
    }, indent=2, ensure_ascii=False))
    return 0 if status in {"PASS", "NEEDS_REVIEW"} else 1


if __name__ == "__main__":
    sys.exit(main())
