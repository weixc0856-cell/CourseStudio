#!/usr/bin/env python3
"""Validate an Episode handoff across stages, modes and Manim limits."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SLIDE_ANCHOR = re.compile(r"\[SLIDE:\s*(\d+)\]")
ANIM_ANCHOR = re.compile(r"\[ANIMATION:\s*([A-Za-z0-9_-]+)\]")
FENCE = re.compile(r"^\s*(```|~~~)")
RESEARCH_FILES = [
    "00-task-brief.md",
    "01-source-inventory.md",
    "02-claim-evidence-ledger.csv",
    "03-knowledge-structure.md",
    "04-course-input-brief.md",
    "05-quality-report.md",
    "06-course-outline.md",
]
FORBIDDEN_MANIM = {
    "manimlib": r"\bmanimlib\b",
    "ThreeDScene": r"\bThreeDScene\b",
    "ThreeDCamera": r"\bThreeDCamera\b",
    "Camera3D": r"\bCamera3D\b",
    "ThreeDAxes": r"\bThreeDAxes\b",
    "Particles": r"\bParticles?\b",
    "ParametricSurface": r"\bParametricSurface\b",
    "Surface": r"\bSurface\s*\(",
}
MAX_SCENE_SECONDS = 20.0


def extract_anchors(text: str) -> list[dict]:
    """Return slide/animation anchors with line numbers and escape status."""
    anchors: list[dict] = []
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

        for match in SLIDE_ANCHOR.finditer(line):
            anchors.append({
                "type": "slide", "value": int(match.group(1)), "line": lineno,
                "escaped": escaped, "text": line.strip(),
            })
        for match in ANIM_ANCHOR.finditer(line):
            anchors.append({
                "type": "animation", "value": match.group(1), "line": lineno,
                "escaped": escaped, "text": line.strip(),
            })
    return anchors


def count_slides(text: str) -> int:
    """Count Slidev slides separated by a line containing only '---'."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]
    blocks = re.split(r"(?m)^\s*---\s*$", text)
    return len([b for b in blocks if b.strip()])


def lint_scene(path: Path) -> dict:
    """Flag forbidden Manim APIs and estimate declared animation duration."""
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = [name for name, pattern in FORBIDDEN_MANIM.items() if re.search(pattern, text)]
    values = [float(m.group(1)) for m in re.finditer(r"run_time\s*=\s*([0-9]+(?:\.[0-9]+)?)", text)]
    values += [float(m.group(1)) for m in re.finditer(r"self\.wait\(\s*([0-9]+(?:\.[0-9]+)?)", text)]
    play_calls = len(re.findall(r"self\.play\(", text))
    explicit_play_times = len(re.findall(r"run_time\s*=", text))
    implicit_play_seconds = max(0, play_calls - explicit_play_times) * 1.0
    return {
        "forbidden": hits,
        "duration_hint": round(sum(values) + implicit_play_seconds, 2),
        "duration_estimated": bool(values) or play_calls > 0,
        "play_calls": play_calls,
    }


def is_nonempty(path: Path) -> bool:
    """True only for an existing text file with non-whitespace content."""
    try:
        if not path.is_file() or path.stat().st_size <= 0:
            return False
        return bool(path.read_text(encoding="utf-8", errors="replace").strip())
    except OSError:
        return False


def research_status(episode: Path, mode: str) -> tuple[bool, str]:
    """Validate research files by presence, non-empty content and ledger keywords."""
    research_dir = episode / "01_research"
    if mode in {"course", "technical"}:
        missing = [name for name in RESEARCH_FILES if not (research_dir / name).is_file()]
        empty = [name for name in RESEARCH_FILES if (research_dir / name).is_file() and not is_nonempty(research_dir / name)]
        if missing or empty:
            parts = []
            if missing:
                parts.append("missing: " + ", ".join(missing))
            if empty:
                parts.append("empty: " + ", ".join(empty))
            return False, "research package invalid: " + "; ".join(parts)
        return True, "00-06 present and non-empty"

    required = ["source-register.md", "claims-ledger.md"]
    missing = [name for name in required if not (research_dir / name).is_file()]
    empty = [name for name in required if (research_dir / name).is_file() and not is_nonempty(research_dir / name)]
    if missing or empty:
        parts = []
        if missing:
            parts.append("missing: " + ", ".join(missing))
        if empty:
            parts.append("empty: " + ", ".join(empty))
        return False, "news/podcast research invalid: " + "; ".join(parts)

    ledger = (research_dir / "claims-ledger.md").read_text(encoding="utf-8", errors="replace")
    if not re.search(r"\b(?:FACT|CLAIM)\b", ledger, re.IGNORECASE):
        return False, "claims-ledger.md contains no FACT/CLAIM entries"
    return True, "source-register.md + claims-ledger.md (FACT/CLAIM present)"


def probe_duration(mp4: Path) -> tuple[float | None, str]:
    """Read real media duration with ffprobe; return (seconds, error)."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None, "ffprobe not found on PATH"
    try:
        proc = subprocess.run(
            [
                ffprobe, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(mp4),
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"ffprobe failed: {exc}"
    if proc.returncode != 0:
        return None, f"ffprobe exit {proc.returncode}: {proc.stderr.strip()[:200]}"
    raw = proc.stdout.strip()
    try:
        return float(raw), ""
    except ValueError:
        return None, f"unparseable ffprobe duration: {raw!r}"


def run_slidev_build(root: Path, slug: str) -> tuple[bool, int | None, str]:
    """Run the real Slidev build for final QA."""
    script = root / "tools" / "slidev-run.ps1"
    if not script.is_file():
        return False, None, f"missing build script: {script}"
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        return False, None, "PowerShell not found on PATH"
    try:
        proc = subprocess.run(
            [
                powershell, "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(script), "-Episode", slug, "-Mode", "build",
            ],
            cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
        )
    except subprocess.TimeoutExpired:
        return False, None, "Slidev build timed out after 300s"
    except OSError as exc:
        return False, None, f"Slidev build failed to start: {exc}"
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    tail = "\n".join(output.splitlines()[-20:])
    return proc.returncode == 0, proc.returncode, tail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", help="Episode slug under courses/")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--mode", choices=["course", "technical", "news", "podcast"], default="course")
    parser.add_argument(
        "--stage", choices=["research", "script", "slides", "manim", "qa"], default="qa",
        help="Only enforce what this stage is expected to have produced.",
    )
    parser.add_argument("--strict", action="store_true", help="Final QA: missing scenes/MP4s fail and Slidev build must pass")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.root)
    episode = root / "courses" / args.episode
    stage = args.stage
    issues: list[str] = []
    warnings: list[str] = []

    if not episode.is_dir():
        print(f"FAIL: episode not found: {episode}")
        return 2

    research_ok, research_detail = research_status(episode, args.mode)
    if not research_ok:
        (issues if stage == "research" else warnings).append(research_detail)

    script_path = episode / "02_scripts" / "lecture_script.md"
    slides_path = episode / "03_slides" / "slides.md"
    handoff = (episode / "handoff.md").exists()

    if stage == "research":
        if not handoff:
            warnings.append("missing handoff.md")
        status = "FAIL" if issues else ("PASS_VERIFIED" if not warnings else "PARTIAL")
        result = {
            "episode": args.episode, "mode": args.mode, "stage": stage, "status": status,
            "research_ok": research_ok, "research_detail": research_detail,
            "handoff": handoff, "issues": issues, "warnings": warnings,
        }
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Episode: {args.episode}  mode={args.mode}  stage={stage}")
            print(f"Status:  {status}")
            print(f"Research: {'OK' if research_ok else 'MISSING'} ({research_detail})")
            for i in issues:
                print(f"  - ISSUE: {i}")
            for w in warnings:
                print(f"  - WARN:  {w}")
        return 1 if issues else 0

    script_text = ""
    if not script_path.exists():
        issues.append(f"missing {script_path.relative_to(episode)}")
    else:
        script_text = script_path.read_text(encoding="utf-8", errors="replace")

    slides_text = ""
    if slides_path.exists():
        slides_text = slides_path.read_text(encoding="utf-8", errors="replace")
    elif args.mode in {"course", "technical"}:
        (issues if stage in {"slides", "manim", "qa"} else warnings).append(
            f"missing {slides_path.relative_to(episode)}"
        )
    elif args.mode == "news":
        warnings.append(f"no Slidev deck: {slides_path.relative_to(episode)}")

    anchors = extract_anchors(script_text)
    escaped = [a for a in anchors if a["escaped"]]
    plain = [a for a in anchors if not a["escaped"]]
    for a in escaped:
        issues.append(
            f"{a['type']} anchor at line {a['line']} is wrapped in code/quote/comment: {a['text']}"
        )

    slide_anchors = [a["value"] for a in plain if a["type"] == "slide"]
    anim_anchors = [a["value"] for a in plain if a["type"] == "animation"]
    slide_count = count_slides(slides_text) if slides_text else 0

    if args.mode in {"course", "technical"} and not slide_anchors and stage in {"script", "slides", "manim", "qa"}:
        warnings.append("no [SLIDE: NN] anchors in lecture_script.md")
    if slide_anchors and not slides_text:
        (issues if stage in {"slides", "manim", "qa"} else warnings).append(
            "slide anchors exist but 03_slides/slides.md is missing"
        )
    if slide_anchors:
        expected = list(range(1, len(slide_anchors) + 1))
        if slide_anchors != expected:
            issues.append(
                "slide anchors must be strictly 1..N with no duplicates, gaps or out-of-order entries; found "
                + ", ".join(str(x) for x in slide_anchors)
            )
        if slide_count and slide_anchors[-1] > slide_count:
            issues.append(
                f"slide anchor {slide_anchors[-1]} exceeds Slidev slide count {slide_count}"
            )

    animations = []
    for name in sorted(set(anim_anchors)):
        scene = episode / "04_manim_src" / "scenes" / f"{name}.py"
        mp4 = episode / "03_slides" / "public" / f"{name}.mp4"
        item = {
            "name": name,
            "scene": str(scene.relative_to(episode)),
            "scene_exists": scene.exists(),
            "mp4": str(mp4.relative_to(episode)),
            "mp4_exists": mp4.exists() and mp4.stat().st_size > 0,
            "lint": None,
        }
        asset_is_issue = stage == "manim" or (stage == "qa" and args.strict)
        if not item["scene_exists"]:
            (issues if asset_is_issue else warnings).append(f"missing scene for {name}")
        else:
            item["lint"] = lint_scene(scene)
            if item["lint"]["forbidden"]:
                issues.append(f"{name}: forbidden Manim API {item['lint']['forbidden']}")
            if item["lint"]["duration_estimated"] and item["lint"]["duration_hint"] > MAX_SCENE_SECONDS:
                issues.append(
                    f"{name}: declared duration {item['lint']['duration_hint']}s exceeds {MAX_SCENE_SECONDS:.0f}s"
                )
        if not item["mp4_exists"]:
            (issues if asset_is_issue else warnings).append(f"missing MP4 for {name}")
            item["real_duration"] = None
            item["duration_probe_error"] = "mp4 missing"
        else:
            real_duration, probe_error = probe_duration(mp4)
            item["real_duration"] = real_duration
            item["duration_probe_error"] = probe_error
            if real_duration is None:
                (issues if asset_is_issue else warnings).append(
                    f"{name}: real MP4 duration NOT_VERIFIED ({probe_error})"
                )
            elif real_duration > MAX_SCENE_SECONDS:
                issues.append(
                    f"{name}: real MP4 duration {real_duration:.2f}s exceeds {MAX_SCENE_SECONDS:.0f}s"
                )
        animations.append(item)

    if not handoff:
        warnings.append("missing handoff.md")

    build_info = {"ran": False, "exit_code": None, "output_tail": ""}
    if stage == "qa" and args.strict and args.mode in {"course", "technical"} and slides_text:
        build_ok, build_code, build_output = run_slidev_build(root, args.episode)
        build_info = {"ran": True, "exit_code": build_code, "output_tail": build_output}
        if not build_ok:
            issues.append(
                f"Slidev build failed (exit {build_code}):\n{build_output}"
            )

    status = "FAIL" if issues else ("PASS_VERIFIED" if not warnings else "PARTIAL")
    result = {
        "episode": args.episode,
        "mode": args.mode,
        "stage": stage,
        "status": status,
        "research_ok": research_ok,
        "research_detail": research_detail,
        "slide_anchors": slide_anchors,
        "slide_count": slide_count,
        "animation_anchors": sorted(set(anim_anchors)),
        "escaped_anchors": escaped,
        "animations": animations,
        "handoff": handoff,
        "slidev_build": build_info,
        "issues": issues,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Episode: {args.episode}  mode={args.mode}  stage={stage}")
        print(f"Status:  {status}")
        print(f"Research: {'OK' if research_ok else 'MISSING'} ({research_detail})")
        print(f"Slides:  {slide_count} slide(s), anchors {slide_anchors or 'none'}")
        print(f"Anims:   {sorted(set(anim_anchors)) or 'none'}")
        if build_info["ran"]:
            build_status = "PASS" if build_info["exit_code"] == 0 else "FAIL"
            print(f"Build:   {build_status} (exit {build_info['exit_code']})")
        for a in animations:
            lint = a["lint"]
            lint_text = "n/a"
            if lint:
                lint_text = "OK" if not lint["forbidden"] else f"FORBIDDEN {lint['forbidden']}"
                if lint["duration_estimated"]:
                    lint_text += f", ~{lint['duration_hint']}s"
            if a.get("real_duration") is not None:
                lint_text += f", real={a['real_duration']:.2f}s"
            elif a.get("mp4_exists"):
                lint_text += ", real=UNVERIFIED"
            print(
                f"  - {a['name']}: scene={'OK' if a['scene_exists'] else 'MISSING'}, "
                f"mp4={'OK' if a['mp4_exists'] else 'MISSING'}, lint={lint_text}"
            )
        if escaped:
            print("Escaped anchors:")
            for a in escaped:
                print(f"  - line {a['line']}: {a['text']}")
        if issues:
            print("Issues:")
            for i in issues:
                print(f"  - {i}")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  - {w}")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
