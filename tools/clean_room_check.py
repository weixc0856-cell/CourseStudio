#!/usr/bin/env python3
"""Clean-room reproduction for the R2.1 contract and real course.

Creates a short-path temp tree, restores the project-local contract runtime,
copies source (without node_modules/.vendor), reinstalls Motion dependencies,
runs runtime checks, content checks, and the contract checker.

Writes docs/r2.1/clean-room-report.md. Removes the temp tree at the end.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EPISODE = "transformer-self-attention"
REPORT = REPO / "docs" / "r2.1" / "clean-room-report.md"
EXCLUDE_DIRS = {"node_modules", ".vendor", "output", "recordings", "__pycache__", ".pytest_cache"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], cwd: Path, env: dict | None = None) -> dict:
    proc = subprocess.run(
        cmd, cwd=str(cwd), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600,
    )
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-12:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-12:]),
    }


def copy_tree(src: Path, dst: Path) -> None:
    def ignore(directory, names):
        return [name for name in names if name in EXCLUDE_DIRS]
    shutil.copytree(src, dst, ignore=ignore)


def main() -> int:
    temp_base = Path(tempfile.gettempdir())
    if os.name == "nt":
        temp_base = Path(temp_base.anchor)
    temp = Path(tempfile.mkdtemp(prefix=f"r2clean-{os.getpid()}-", dir=temp_base))
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    results: list[dict] = []
    try:
        # Source tools + schemas + tests
        (temp / "tools").mkdir()
        for name in ["check-episode.py", "script_timing.py", "build-recording-package.py", "qa_runtime.py", "qa_content.py"]:
            shutil.copy2(REPO / "tools" / name, temp / "tools" / name)
        shutil.copytree(REPO / "schemas", temp / "schemas")
        shutil.copytree(REPO / "tests" / "contract", temp / "tests" / "contract", ignore=shutil.ignore_patterns("__pycache__"))

        # Project-local contract runtime
        runtime = temp / "tools" / "contract-runtime"
        runtime.mkdir()
        for name in ["pyproject.toml", "uv.lock", ".python-version"]:
            src = REPO / "tools" / "contract-runtime" / name
            if src.is_file():
                shutil.copy2(src, runtime / name)
        env = os.environ.copy()
        env["UV_CACHE_DIR"] = str(REPO / ".uv-cache")
        results.append(run(["uv", "sync", "--frozen"], runtime, env))
        py = runtime / ".venv" / "Scripts" / "python.exe"
        results.append(run([str(py), "tests/contract/validate_with_jsonschema.py"], temp))

        # Course source (no node_modules/.vendor/render outputs)
        course_dst = temp / "courses" / EPISODE
        copy_tree(REPO / "courses" / EPISODE, course_dst)

        # Restore Reveal runtime dependency into the clean course
        reveal_src = REPO / "tools" / "reveal-runtime" / "node_modules" / "reveal.js" / "dist"
        reveal_dst = course_dst / "03_slides" / ".vendor" / "reveal"
        if reveal_src.is_dir():
            shutil.copytree(reveal_src, reveal_dst)

        # Reinstall Motion dependencies in the clean course
        motion = course_dst / "04_motion_src"
        pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
        pnpm_cmd = (["cmd", "/c", pnpm] if pnpm and pnpm.lower().endswith((".cmd", ".bat")) else ([pnpm] if pnpm else []))
        results.append(run(pnpm_cmd + ["install", "--frozen-lockfile"], motion))

        # Runtime checks in clean room
        results.append(run([sys.executable, "tools/qa_runtime.py", EPISODE], temp))

        # Content/trace/delivery checks in clean room
        results.append(run([sys.executable, "tools/qa_content.py", EPISODE], temp))

        # Contract checker stages
        for stage in ["research", "script", "motion", "recording", "slides"]:
            results.append(run([sys.executable, "tools/check-episode.py", EPISODE, "--mode", "course", "--stage", stage], temp))
        results.append(run([sys.executable, "tools/check-episode.py", EPISODE, "--mode", "course", "--stage", "qa", "--strict"], temp))

        # Collect evidence statuses
        runtime_json = course_dst / "qa" / "runtime.json"
        content_json = course_dst / "qa" / "content-quality.json"
        trace_json = course_dst / "qa" / "trace-report.json"
        delivery_json = course_dst / "qa" / "delivery-manifest.json"
        evidence = {}
        for key, path in [("runtime", runtime_json), ("content", content_json), ("trace", trace_json), ("delivery", delivery_json)]:
            if path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                evidence[key] = {k: data.get(k) for k in ("status", "coverage", "blocking_reasons") if k in data}
        report = {
            "generated_at": utc_now(),
            "temp_dir": str(temp),
            "source_head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
            "results": results,
            "evidence": evidence,
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            "# R2.1 Clean-Room Report\n\n```json\n" + json.dumps(report, indent=2, ensure_ascii=False) + "\n```\n",
            encoding="utf-8",
        )
        print(json.dumps({"temp_dir": str(temp), "results": results, "evidence": evidence}, indent=2, ensure_ascii=False))
        failed = [r for r in results if r["exit_code"] not in (0, 1)]
        return 1 if failed else 0
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
