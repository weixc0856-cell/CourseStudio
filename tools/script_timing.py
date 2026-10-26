#!/usr/bin/env python3
"""Parse and validate Motion Canvas timing annotations in lecture scripts.

The syntax is line-based and intentionally strict:

    [ANIMATION: name]
    [SEGMENT: name | 45s | order=1]
    [VISUAL 00:00] ...
    [HOLD 00:05] ...
    [EMPHASIS 00:20] ...
    [CUT 00:30] ...

Quoted, fenced, and HTML-comment lines are ignored for timing purposes so the
contract section at the top of a script is not mistaken for real cues.
"""
from __future__ import annotations

import re
from collections import Counter

SLIDE_ANCHOR = re.compile(r"\[SLIDE:\s*(\d+)\]")
ANIM_ANCHOR = re.compile(r"\[ANIMATION:\s*([A-Za-z0-9_-]+)\]")
FENCE = re.compile(r"^\s*(```|~~~)")
SEGMENT_TAG = re.compile(
    r"^\s*\[SEGMENT:\s*([A-Za-z0-9_-]+)\s*\|\s*(\d+(?:\.\d+)?)\s*s\s*\|\s*order=(\d+)\s*\]\s*$"
)
TIMING_TAG = re.compile(
    r"^\s*\[(VISUAL|HOLD|EMPHASIS|CUT)\s+(\d{1,3}):([0-5]\d)\]\s*(.*)$",
    re.IGNORECASE,
)
HEADING = re.compile(r"^\s*#{1,6}\s")
SEPARATOR = re.compile(r"^\s*---\s*$")
MOTION_MIN_SECONDS = 45.0
MOTION_MAX_SECONDS = 90.0


def scan_lines(text: str):
    """Yield (lineno, line, escaped) with the same escape rules as anchors."""
    in_fence = False
    in_comment = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if FENCE.match(line):
            in_fence = not in_fence
            continue

        escaped = in_fence
        if in_comment:
            escaped = True
            if "-->" in line:
                in_comment = False
        else:
            if stripped.startswith(">"):
                escaped = True
            if "<!--" in line:
                escaped = True
                tail = line.split("<!--", 1)[1]
                if "-->" not in tail:
                    in_comment = True
        yield lineno, line, escaped


def parse_timing_blocks(text: str) -> list[dict]:
    """Return one block per standalone [ANIMATION: name] line."""
    blocks: list[dict] = []
    current: dict | None = None

    for lineno, line, escaped in scan_lines(text):
        if escaped:
            if current is not None:
                current["raw"].append((lineno, line, True))
            continue

        stripped = line.strip()
        animation = ANIM_ANCHOR.fullmatch(stripped)
        slide = SLIDE_ANCHOR.search(line)
        is_heading = HEADING.match(line)
        is_separator = SEPARATOR.match(line)

        if current is not None and (animation or slide or is_heading or is_separator):
            blocks.append(current)
            current = None

        if animation:
            current = {
                "name": animation.group(1),
                "line": lineno,
                "segments": [],
                "timing": [],
                "narration": [],
                "raw": [],
            }
            continue

        if current is None:
            continue

        current["raw"].append((lineno, line, False))

        segment = SEGMENT_TAG.match(line)
        if segment:
            current["segments"].append({
                "name": segment.group(1),
                "seconds": float(segment.group(2)),
                "order": int(segment.group(3)),
                "line": lineno,
            })
            continue

        timing = TIMING_TAG.match(line)
        if timing:
            current["timing"].append({
                "tag": timing.group(1).upper(),
                "seconds": int(timing.group(2)) * 60 + int(timing.group(3)),
                "text": timing.group(4).strip(),
                "line": lineno,
            })
            continue

        if stripped:
            current["narration"].append({"line": lineno, "text": stripped})

    if current is not None:
        blocks.append(current)
    return blocks


def validate_timing_block(
    name: str,
    block: dict,
    expected_seconds: float | None = None,
    expected_order: int | None = None,
) -> tuple[list[str], list[str]]:
    """Validate one motion block; return (issues, warnings)."""
    issues: list[str] = []
    warnings: list[str] = []

    segments = block.get("segments") or []
    if len(segments) != 1:
        issues.append(
            f"{name}: expected exactly one [SEGMENT] tag; found {len(segments)}"
        )
        if not segments:
            return issues, warnings

    segment = segments[0]
    if segment["name"] != name:
        issues.append(
            f"{name}: [SEGMENT] name {segment['name']!r} does not match [ANIMATION]"
        )

    seconds = segment["seconds"]
    if not (MOTION_MIN_SECONDS <= seconds <= MOTION_MAX_SECONDS):
        issues.append(
            f"{name}: [SEGMENT] duration {seconds:g}s is outside "
            f"{MOTION_MIN_SECONDS:.0f}-{MOTION_MAX_SECONDS:.0f}s"
        )
    if expected_seconds is not None and abs(seconds - float(expected_seconds)) > 0.5:
        issues.append(
            f"{name}: [SEGMENT] duration {seconds:g}s differs from segments.json "
            f"{float(expected_seconds):g}s"
        )
    if expected_order is not None and segment["order"] != expected_order:
        issues.append(
            f"{name}: [SEGMENT] order {segment['order']} differs from "
            f"segments.json order {expected_order}"
        )

    counts = Counter(item["tag"] for item in block.get("timing", []))
    for required in ("HOLD", "EMPHASIS", "CUT"):
        if counts.get(required, 0) == 0:
            issues.append(f"{name}: missing [{required}] cue")
    if counts.get("VISUAL", 0) == 0:
        warnings.append(f"{name}: no [VISUAL] cue")

    times = [item["seconds"] for item in block.get("timing", [])]
    if len(times) != len(set(times)) or times != sorted(times):
        issues.append(
            f"{name}: timing cues must be strictly increasing; found "
            + ", ".join(f"{value // 60:02d}:{value % 60:02d}" for value in times)
        )
    if times and max(times) > seconds:
        issues.append(
            f"{name}: cue at {max(times) // 60:02d}:{max(times) % 60:02d} exceeds "
            f"declared duration {seconds:g}s"
        )

    return issues, warnings
