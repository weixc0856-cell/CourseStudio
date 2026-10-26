#!/usr/bin/env python3
"""Validate an Episode handoff across stages, modes and animation engines."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from script_timing import (
    ANIM_ANCHOR,
    SLIDE_ANCHOR,
    parse_timing_blocks,
    scan_lines,
    validate_timing_block,
)

REVEAL_SLIDE = re.compile(r"""data-slide\s*=\s*["'](\d+)["']""")
RESOURCE_ATTR = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
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
# Motion Canvas narrative segments are long-form; Manim is a legacy fallback.
MOTION_MIN_SECONDS = 45.0
MOTION_MAX_SECONDS = 90.0
MANIM_MAX_SCENE_SECONDS = 20.0
RECORDING_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov"}
# Kept for callers that imported the old name. New code uses the split constants.
MAX_SCENE_SECONDS = MANIM_MAX_SCENE_SECONDS


def extract_anchors(text: str) -> list[dict]:
    """Return slide/animation anchors with line numbers and escape status."""
    anchors: list[dict] = []
    for lineno, line, escaped in scan_lines(text):
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


def count_reveal_slides(text: str) -> tuple[int, list[str]]:
    """Count Reveal slides and require data-slide 1..N in document order."""
    values = [int(m.group(1)) for m in REVEAL_SLIDE.finditer(text)]
    issues: list[str] = []
    if not values:
        issues.append("03_slides/index.html has no data-slide attributes")
        return 0, issues
    if len(values) != len(set(values)):
        issues.append("03_slides/index.html has duplicate data-slide values")
    if values != list(range(1, len(values) + 1)):
        issues.append(
            "03_slides/index.html data-slide values must be strictly 1..N in document order; found "
            + ", ".join(str(value) for value in values)
        )
    return len(values), issues


def check_reveal_resources(deck_path: Path) -> list[str]:
    """Check local src/href targets under 03_slides; ignore remote/data/anchor URLs."""
    try:
        text = deck_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"cannot read {deck_path.name}: {exc}"]

    issues: list[str] = []
    base = deck_path.parent.resolve()
    for raw in RESOURCE_ATTR.findall(text):
        value = raw.strip()
        if not value or value.startswith(
            ("#", "http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:")
        ):
            continue
        path_part = value.split("#", 1)[0].split("?", 1)[0].strip()
        if not path_part:
            continue
        target = (base / path_part).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            issues.append(f"03_slides/index.html references a path outside 03_slides: {value}")
            continue
        if not target.exists():
            issues.append(f"03_slides/index.html references missing local asset: {value}")
    return issues


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


def relative_display(path: Path, episode: Path) -> str:
    try:
        return str(path.relative_to(episode))
    except ValueError:
        return str(path)


def find_recording(episode: Path, name: str) -> Path | None:
    """Find a recorded take by segment basename; recordings are optional."""
    recordings = episode / "05_recording" / "recordings"
    if not recordings.is_dir():
        return None
    for path in sorted(recordings.iterdir()):
        if path.is_file() and path.stem == name and path.suffix.lower() in RECORDING_EXTENSIONS:
            return path
    return None


def load_segments(episode: Path, hard: bool) -> tuple[list[dict] | None, list[str], list[str], bool]:
    """Load and validate 04_motion_src/segments.json.

    Returns (entries, issues, warnings, present). ``present`` is True even when
    the file is malformed, so callers do not fall back to legacy Manim logic.
    """
    path = episode / "04_motion_src" / "segments.json"
    if not path.is_file():
        return None, [], [], False

    issues: list[str] = []
    warnings: list[str] = []

    def report(message: str) -> None:
        (issues if hard else warnings).append(message)

    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError) as exc:
        report(f"segments.json invalid: {exc}")
        return [], issues, warnings, True

    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        report("segments.json must contain a segments list")
        return [], issues, warnings, True

    entries: list[dict] = []
    seen_names: set[str] = set()
    for index, raw in enumerate(data["segments"], start=1):
        label = f"segments.json entry #{index}"
        if not isinstance(raw, dict):
            report(f"{label} is not an object")
            continue

        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            report(f"{label} has no name")
            continue
        name = name.strip()
        if name in seen_names:
            report(f"duplicate segment name: {name}")
        seen_names.add(name)

        scene = raw.get("scene") or name
        if not isinstance(scene, str) or not scene.strip():
            report(f"{name}: invalid scene")
            scene = name
        else:
            scene = scene.strip()
            if scene.endswith(".tsx"):
                scene = scene[:-4]

        project = raw.get("project") or scene
        if not isinstance(project, str) or not project.strip():
            report(f"{name}: invalid project")
            project = scene
        else:
            project = project.strip()
            if project.endswith(".ts"):
                project = project[:-3]

        cue = raw.get("cue") or f"05_recording/cues/{name}.md"
        if not isinstance(cue, str) or not cue.strip():
            report(f"{name}: invalid cue")
            cue = f"05_recording/cues/{name}.md"
        else:
            cue = cue.strip()

        duration = raw.get("duration_seconds")
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            report(f"{name}: missing or invalid duration_seconds")
            duration = None
        else:
            duration = float(duration)

        order = raw.get("order")
        if isinstance(order, bool) or not isinstance(order, int):
            report(f"{name}: missing or invalid order")
            order = None

        engine = raw.get("engine")
        motion_scene = episode / "04_motion_src" / "src" / "scenes" / f"{scene}.tsx"
        manim_scene = episode / "04_manim_src" / "scenes" / f"{name}.py"
        if engine is None:
            if motion_scene.exists() and manim_scene.exists():
                report(f"{name}: engine missing and both motion and Manim scene files exist")
            elif motion_scene.exists():
                engine = "motion"
                warnings.append(f"{name}: engine missing; inferred motion")
            elif manim_scene.exists():
                engine = "manim"
                warnings.append(f"{name}: engine missing; inferred manim")
            else:
                report(f"{name}: engine missing and no motion or Manim scene file found")
        elif engine not in {"motion", "manim"}:
            report(f"{name}: unsupported engine {engine!r}")
            engine = None

        entries.append({
            "name": name,
            "engine": engine,
            "duration_seconds": duration,
            "order": order,
            "scene": scene,
            "project": project,
            "cue": cue,
        })

    orders = [entry["order"] for entry in entries if isinstance(entry["order"], int)]
    if entries and len(orders) == len(entries):
        if sorted(orders) != list(range(1, len(entries) + 1)):
            report(
                "segment order must be continuous 1..N; found "
                + ", ".join(str(order) for order in orders)
            )

    return entries, issues, warnings, True


def check_motion_segment(episode: Path, entry: dict) -> tuple[dict, list[str], list[str]]:
    """Check one Motion Canvas segment without inventing a real duration."""
    name = entry["name"]
    scene_path = episode / "04_motion_src" / "src" / "scenes" / f"{entry['scene']}.tsx"
    project_path = episode / "04_motion_src" / "src" / "projects" / f"{entry['project']}.ts"
    cue_path = episode / entry["cue"]

    problems: list[str] = []
    warnings: list[str] = []
    scene_exists = is_nonempty(scene_path)
    project_exists = is_nonempty(project_path)
    cue_exists = is_nonempty(cue_path)

    if not scene_exists:
        problems.append(f"{name}: missing motion scene ({relative_display(scene_path, episode)})")
    if not project_exists:
        problems.append(f"{name}: missing motion project ({relative_display(project_path, episode)})")
    if not cue_exists:
        problems.append(f"{name}: missing cue ({relative_display(cue_path, episode)})")

    duration = entry["duration_seconds"]
    duration_ok = False
    if isinstance(duration, (int, float)):
        duration_ok = MOTION_MIN_SECONDS <= float(duration) <= MOTION_MAX_SECONDS
        if not duration_ok:
            problems.append(
                f"{name}: declared duration {float(duration):.1f}s is outside "
                f"{MOTION_MIN_SECONDS:.0f}-{MOTION_MAX_SECONDS:.0f}s"
            )

    recording = find_recording(episode, name)
    real_duration: float | None = None
    probe_error = "no recording (NOT_VERIFIED)"
    if recording is not None:
        real_duration, probe_error = probe_duration(recording)
        if real_duration is None:
            problems.append(f"{name}: recorded duration NOT_VERIFIED ({probe_error})")
        else:
            if not (MOTION_MIN_SECONDS <= real_duration <= MOTION_MAX_SECONDS):
                problems.append(
                    f"{name}: recorded duration {real_duration:.2f}s is outside "
                    f"{MOTION_MIN_SECONDS:.0f}-{MOTION_MAX_SECONDS:.0f}s"
                )
            if isinstance(duration, (int, float)) and abs(real_duration - float(duration)) > 6.0:
                warnings.append(
                    f"{name}: recording differs from declared duration by "
                    f"{real_duration - float(duration):+.1f}s (pre/post-roll is expected)"
                )

    result = {
        "name": name,
        "engine": "motion",
        "scene": relative_display(scene_path, episode),
        "scene_exists": scene_exists,
        "project": relative_display(project_path, episode),
        "project_exists": project_exists,
        "cue": relative_display(cue_path, episode),
        "cue_exists": cue_exists,
        "declared_seconds": duration,
        "duration_ok": duration_ok,
        "recording": relative_display(recording, episode) if recording else None,
        "real_duration": real_duration,
        "duration_probe_error": probe_error,
    }
    return result, problems, warnings


def check_manim_segment(episode: Path, name: str) -> tuple[dict, list[str], list[str]]:
    """Legacy Manim checks. Hard failures and asset failures are separated."""
    scene = episode / "04_manim_src" / "scenes" / f"{name}.py"
    mp4 = episode / "03_slides" / "public" / f"{name}.mp4"
    hard: list[str] = []
    assets: list[str] = []
    item = {
        "name": name,
        "engine": "manim",
        "scene": relative_display(scene, episode),
        "scene_exists": scene.exists(),
        "mp4": relative_display(mp4, episode),
        "mp4_exists": mp4.exists() and mp4.stat().st_size > 0,
        "lint": None,
        "real_duration": None,
        "duration_probe_error": "",
    }
    if not scene.exists():
        assets.append(f"missing scene for {name}")
    else:
        lint = lint_scene(scene)
        item["lint"] = lint
        if lint["forbidden"]:
            hard.append(f"{name}: forbidden Manim API {lint['forbidden']}")
        if lint["duration_estimated"] and lint["duration_hint"] > MANIM_MAX_SCENE_SECONDS:
            hard.append(
                f"{name}: declared duration {lint['duration_hint']}s exceeds "
                f"{MANIM_MAX_SCENE_SECONDS:.0f}s"
            )

    if not item["mp4_exists"]:
        assets.append(f"missing MP4 for {name}")
        item["duration_probe_error"] = "mp4 missing"
    else:
        real_duration, probe_error = probe_duration(mp4)
        item["real_duration"] = real_duration
        item["duration_probe_error"] = probe_error
        if real_duration is None:
            assets.append(f"{name}: real MP4 duration NOT_VERIFIED ({probe_error})")
        elif real_duration > MANIM_MAX_SCENE_SECONDS:
            hard.append(
                f"{name}: real MP4 duration {real_duration:.2f}s exceeds "
                f"{MANIM_MAX_SCENE_SECONDS:.0f}s"
            )
    return item, hard, assets


def check_recording_package(episode: Path, motion_entries: list[dict]) -> tuple[dict, list[str], list[str]]:
    """Validate 05_recording structure. Recorded media files are optional."""
    package = episode / "05_recording"
    manifest_path = package / "manifest.json"
    checklist_path = package / "checklist.md"
    cues_dir = package / "cues"
    recordings_dir = package / "recordings"
    problems: list[str] = []
    warnings: list[str] = []

    info = {
        "checked": True,
        "manifest": relative_display(manifest_path, episode),
        "manifest_exists": is_nonempty(manifest_path),
        "checklist": relative_display(checklist_path, episode),
        "checklist_exists": is_nonempty(checklist_path),
        "cues_dir": relative_display(cues_dir, episode),
        "cues_dir_exists": cues_dir.is_dir(),
        "recordings_dir": relative_display(recordings_dir, episode),
        "recordings_dir_exists": recordings_dir.is_dir(),
        "manifest_segments": [],
        "recordings": 0,
    }

    if not is_nonempty(manifest_path):
        problems.append("missing or empty 05_recording/manifest.json")
    if not is_nonempty(checklist_path):
        problems.append("missing or empty 05_recording/checklist.md")
    if not cues_dir.is_dir():
        problems.append("missing 05_recording/cues/ directory")
    # recordings/ is local-only and gitignored; do not require the directory
    # or any media files at the recording stage.

    manifest_names: set[str] = set()
    if is_nonempty(manifest_path):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"05_recording/manifest.json invalid: {exc}")
            manifest = None
        if isinstance(manifest, dict) and isinstance(manifest.get("segments"), list):
            for index, raw in enumerate(manifest["segments"], start=1):
                if not isinstance(raw, dict):
                    problems.append(f"recording manifest entry #{index} is not an object")
                    continue
                name = raw.get("name")
                if not isinstance(name, str) or not name.strip():
                    problems.append(f"recording manifest entry #{index} has no name")
                    continue
                name = name.strip()
                manifest_names.add(name)
                info["manifest_segments"].append(name)
                url = raw.get("url")
                if not isinstance(url, str) or "record.html" not in url:
                    problems.append(f"recording manifest {name}: url must target record.html")
                declared = raw.get("declared_seconds", raw.get("duration_seconds"))
                if isinstance(declared, bool) or not isinstance(declared, (int, float)):
                    warnings.append(f"recording manifest {name}: no declared_seconds")
                elif not (MOTION_MIN_SECONDS <= float(declared) <= MOTION_MAX_SECONDS):
                    problems.append(
                        f"recording manifest {name}: declared_seconds {float(declared):.1f}s "
                        f"is outside {MOTION_MIN_SECONDS:.0f}-{MOTION_MAX_SECONDS:.0f}s"
                    )
                cue = raw.get("cue")
                if not isinstance(cue, str) or not cue.strip():
                    warnings.append(f"recording manifest {name}: no cue path")
                else:
                    cue_value = cue.strip()
                    if not (
                        is_nonempty(episode / cue_value)
                        or is_nonempty(package / cue_value)
                    ):
                        warnings.append(
                            f"recording manifest {name}: cue file not found ({cue_value})"
                        )
        else:
            problems.append("05_recording/manifest.json must contain a segments list")

    if motion_entries:
        if not manifest_names:
            problems.append("recording manifest has no segment entries")
        for entry in motion_entries:
            if entry["name"] not in manifest_names:
                problems.append(f"recording manifest missing segment: {entry['name']}")

    if recordings_dir.is_dir():
        info["recordings"] = sum(
            1
            for path in recordings_dir.iterdir()
            if path.is_file() and path.suffix.lower() in RECORDING_EXTENSIONS
        )
    return info, problems, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", help="Episode slug under courses/")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--mode", choices=["course", "technical", "news", "podcast"], default="course")
    parser.add_argument(
        "--stage",
        choices=["research", "script", "slides", "motion", "manim", "qa", "recording"],
        default="qa",
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
        hard_fail = stage == "research" or stage == "qa" or args.strict
        (issues if hard_fail else warnings).append(research_detail)

    script_path = episode / "02_scripts" / "lecture_script.md"
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

    slidev_path = episode / "03_slides" / "slides.md"
    reveal_path = episode / "03_slides" / "index.html"
    deck_kind = "none"
    deck_path: Path | None = None
    if reveal_path.is_file():
        deck_kind = "reveal"
        deck_path = reveal_path
        if slidev_path.is_file():
            warnings.append("both 03_slides/index.html and slides.md exist; using index.html")
    elif slidev_path.is_file():
        deck_kind = "slidev"
        deck_path = slidev_path

    deck_text = deck_path.read_text(encoding="utf-8", errors="replace") if deck_path else ""
    reveal_issues: list[str] = []
    if deck_kind == "reveal":
        slide_count, reveal_issues = count_reveal_slides(deck_text)
    elif deck_kind == "slidev":
        slide_count = count_slides(deck_text)
    else:
        slide_count = 0

    deck_issue_stages = {"slides", "manim", "qa", "recording"}
    resource_issues = check_reveal_resources(reveal_path) if deck_kind == "reveal" else []
    deck_problems = reveal_issues + resource_issues
    if deck_problems:
        (issues if stage in deck_issue_stages or args.strict else warnings).extend(deck_problems)

    if deck_kind == "none":
        if args.mode in {"course", "technical"}:
            (issues if stage in deck_issue_stages or args.strict else warnings).append(
                "missing 03_slides/slides.md or 03_slides/index.html"
            )
        elif args.mode == "news":
            warnings.append("no Slidev/Reveal deck (news mode)")

    anchors = extract_anchors(script_text)
    escaped = [a for a in anchors if a["escaped"]]
    plain = [a for a in anchors if not a["escaped"]]
    for a in escaped:
        issues.append(
            f"{a['type']} anchor at line {a['line']} is wrapped in code/quote/comment: {a['text']}"
        )

    slide_anchors = [a["value"] for a in plain if a["type"] == "slide"]
    anim_anchors = [a["value"] for a in plain if a["type"] == "animation"]
    anim_names = sorted(set(anim_anchors))

    if args.mode in {"course", "technical"} and not slide_anchors and stage in {"script", "slides", "motion", "manim", "qa", "recording"}:
        warnings.append("no [SLIDE: NN] anchors in lecture_script.md")
    if slide_anchors and deck_kind == "none":
        (issues if stage in deck_issue_stages or args.strict else warnings).append(
            "slide anchors exist but no 03_slides/slides.md or 03_slides/index.html is present"
        )

    unique_slide_anchors = len(set(slide_anchors))
    slide_mapping = {
        "anchors": unique_slide_anchors,
        "slides": slide_count,
        "buffer": slide_count - unique_slide_anchors,
        "deck_kind": deck_kind,
    }
    if slide_anchors:
        expected = list(range(1, len(slide_anchors) + 1))
        if slide_anchors != expected:
            issues.append(
                "slide anchors must be strictly 1..N with no duplicates, gaps or out-of-order entries; found "
                + ", ".join(str(x) for x in slide_anchors)
            )
        if unique_slide_anchors > slide_count:
            deck_label = "Reveal" if deck_kind == "reveal" else "Slidev"
            issues.append(
                f"slide anchors {unique_slide_anchors} exceed {deck_label} slide count {slide_count}"
            )

    motion_is_issue = stage in {"motion", "recording"} or args.strict
    manim_is_issue = stage == "manim" or args.strict
    recording_is_issue = stage == "recording" or args.strict

    segments, seg_issues, seg_warnings, manifest_present = load_segments(episode, motion_is_issue)
    issues.extend(seg_issues)
    warnings.extend(seg_warnings)

    animations: list[dict] = []
    motion_entries: list[dict] = []

    if manifest_present:
        entries = segments or []
        by_name = {entry["name"]: entry for entry in entries}
        for name in anim_names:
            if name not in by_name:
                message = f"[ANIMATION: {name}] has no 04_motion_src/segments.json entry"
                (issues if motion_is_issue else warnings).append(message)
        for entry in entries:
            name = entry["name"]
            if name not in anim_names:
                message = f"segments.json segment {name} has no [ANIMATION] anchor"
                (issues if motion_is_issue else warnings).append(message)

            if entry["engine"] == "motion":
                motion_entries.append(entry)
                item, problems, item_warnings = check_motion_segment(episode, entry)
                (issues if motion_is_issue else warnings).extend(problems)
                warnings.extend(item_warnings)
                animations.append(item)
            elif entry["engine"] == "manim":
                item, hard, assets = check_manim_segment(episode, name)
                issues.extend(hard)
                (issues if manim_is_issue else warnings).extend(assets)
                animations.append(item)
    else:
        if anim_names:
            warnings.append(
                "no 04_motion_src/segments.json; using legacy Manim file detection (deprecated)"
            )
        for name in anim_names:
            item, hard, assets = check_manim_segment(episode, name)
            issues.extend(hard)
            (issues if manim_is_issue else warnings).extend(assets)
            animations.append(item)

    timing_is_issue = stage in {"script", "motion", "recording"} or args.strict
    timing_blocks = parse_timing_blocks(script_text)
    blocks_by_name: dict[str, dict] = {}
    duplicate_blocks: list[str] = []
    for block in timing_blocks:
        name = block["name"]
        if name in blocks_by_name:
            duplicate_blocks.append(name)
        blocks_by_name[name] = block
    if duplicate_blocks:
        message = "duplicate [ANIMATION] timing block(s): " + ", ".join(sorted(set(duplicate_blocks)))
        (issues if timing_is_issue else warnings).append(message)

    motion_by_name = {entry["name"]: entry for entry in motion_entries}
    for entry in motion_entries:
        name = entry["name"]
        block = blocks_by_name.get(name)
        if block is None:
            message = f"{name}: missing [ANIMATION] timing block"
            (issues if timing_is_issue else warnings).append(message)
            continue
        block_issues, block_warnings = validate_timing_block(
            name,
            block,
            expected_seconds=entry["duration_seconds"],
            expected_order=entry["order"],
        )
        (issues if timing_is_issue else warnings).extend(block_issues)
        warnings.extend(block_warnings)

    # Validate a motion-looking block even when segments.json is not written yet
    # (script stage) or the manifest entry is ambiguous. Manim-only blocks do not
    # require timing tags.
    for block in timing_blocks:
        name = block["name"]
        if name in motion_by_name:
            continue
        entry = next((item for item in (segments or []) if item["name"] == name), None)
        if entry is not None and entry["engine"] == "manim":
            continue
        if not block.get("segments"):
            continue
        block_issues, block_warnings = validate_timing_block(name, block)
        (issues if timing_is_issue else warnings).extend(block_issues)
        warnings.extend(block_warnings)

    recording_info: dict = {"checked": False}
    if (
        args.mode in {"course", "technical"}
        and motion_entries
        and (stage == "recording" or (stage == "qa" and args.strict))
    ):
        recording_info, rec_problems, rec_warnings = check_recording_package(episode, motion_entries)
        (issues if recording_is_issue else warnings).extend(rec_problems)
        warnings.extend(rec_warnings)

    if not handoff:
        warnings.append("missing handoff.md")

    build_info = {"ran": False, "exit_code": None, "output_tail": "", "deck_kind": deck_kind}
    if stage == "qa" and args.strict and args.mode in {"course", "technical"} and deck_kind == "slidev":
        build_ok, build_code, build_output = run_slidev_build(root, args.episode)
        build_info = {"ran": True, "exit_code": build_code, "output_tail": build_output, "deck_kind": deck_kind}
        if not build_ok:
            issues.append(
                f"Slidev build failed (exit {build_code}):\n{build_output}"
            )
    elif stage == "qa" and args.strict and args.mode in {"course", "technical"} and deck_kind == "reveal":
        build_info["skipped"] = "Reveal deck: build check deferred to Phase 4"

    status = "FAIL" if issues else ("PASS_VERIFIED" if not warnings else "PARTIAL")
    result = {
        "episode": args.episode,
        "mode": args.mode,
        "stage": stage,
        "status": status,
        "research_ok": research_ok,
        "research_detail": research_detail,
        "deck_kind": deck_kind,
        "slide_anchors": slide_anchors,
        "slide_count": slide_count,
        "slide_mapping": slide_mapping,
        "animation_anchors": anim_names,
        "escaped_anchors": escaped,
        "segments": [
            {
                "name": entry["name"],
                "engine": entry["engine"],
                "duration_seconds": entry["duration_seconds"],
                "order": entry["order"],
                "scene": entry["scene"],
                "project": entry["project"],
                "cue": entry["cue"],
            }
            for entry in (segments or [])
        ],
        "segments_present": manifest_present,
        "timing_blocks": len(timing_blocks),
        "animations": animations,
        "recording_package": recording_info,
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
        deck_label = deck_kind if deck_kind != "none" else "none"
        print(f"Slides:  {slide_count} slide(s) [{deck_label}]")
        if slide_count or slide_anchors:
            print(
                f"Mapping: {unique_slide_anchors} anchor(s), {slide_count} slide(s), "
                f"buffer {slide_mapping['buffer']} (N >= M allowed)"
            )
        if manifest_present:
            motion_count = sum(1 for entry in (segments or []) if entry["engine"] == "motion")
            print(f"Segments: {len(segments or [])} entr(ies), {motion_count} motion")
        else:
            print("Segments: legacy Manim mode (no segments.json)")
        print(f"Anims:   {anim_names or 'none'}")
        print(f"Timing:  {len(timing_blocks)} block(s)")
        if build_info["ran"]:
            build_status = "PASS" if build_info["exit_code"] == 0 else "FAIL"
            print(f"Build:   {build_status} (exit {build_info['exit_code']})")
        elif build_info.get("skipped"):
            print(f"Build:   SKIPPED ({build_info['skipped']})")
        for a in animations:
            if a.get("engine") == "motion":
                real_text = (
                    f"{a['real_duration']:.2f}s"
                    if a.get("real_duration") is not None
                    else "NOT_VERIFIED"
                )
                declared = a.get("declared_seconds")
                declared_text = f"{float(declared):.1f}s" if isinstance(declared, (int, float)) else "invalid"
                print(
                    f"  - {a['name']}: engine=motion, "
                    f"scene={'OK' if a['scene_exists'] else 'MISSING'}, "
                    f"project={'OK' if a['project_exists'] else 'MISSING'}, "
                    f"cue={'OK' if a['cue_exists'] else 'MISSING'}, "
                    f"declared={declared_text}, real={real_text}"
                )
            else:
                lint = a.get("lint")
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
                    f"  - {a['name']}: engine=manim, "
                    f"scene={'OK' if a['scene_exists'] else 'MISSING'}, "
                    f"mp4={'OK' if a['mp4_exists'] else 'MISSING'}, lint={lint_text}"
                )
        if recording_info.get("checked"):
            print(
                "Recording: checked "
                f"(manifest={'OK' if recording_info['manifest_exists'] else 'MISSING'}, "
                f"checklist={'OK' if recording_info['checklist_exists'] else 'MISSING'}, "
                f"cues_dir={'OK' if recording_info['cues_dir_exists'] else 'MISSING'}, "
                f"recordings_dir={'OK' if recording_info['recordings_dir_exists'] else 'optional'}, "
                f"recordings={recording_info['recordings']})"
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
