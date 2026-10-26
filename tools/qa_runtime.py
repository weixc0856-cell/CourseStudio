#!/usr/bin/env python3
"""Run real runtime checks for an episode and write qa/runtime.json.

Checks:
  - Motion Canvas: pnpm typecheck + record.html?probe=1 duration
  - Reveal: static server + headless Chrome load + representative screenshots
  - Slidev: build is handled by check-episode's strict QA; this runner reports N/A

This runner writes only under <episode>/qa/runtime and <episode>/qa/runtime.json.
It does not modify course content.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_chrome() -> str | None:
    for candidate in [
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def http_ready(url: str, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def chrome_dump_dom(chrome: str, url: str, user_dir: Path) -> tuple[int, str, str]:
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
        f"--user-data-dir={user_dir}", "--virtual-time-budget=15000",
        "--dump-dom", url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return proc.returncode, proc.stdout, proc.stderr


def chrome_screenshot(chrome: str, url: str, output: Path, user_dir: Path) -> tuple[int, str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
        f"--user-data-dir={user_dir}", "--window-size=1920,1080",
        "--virtual-time-budget=5000", f"--screenshot={output}", url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return proc.returncode, proc.stderr


def kill_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
            capture_output=True, text=True, timeout=20,
        )
    except Exception:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--motion-port", type=int, default=9188)
    parser.add_argument("--reveal-port", type=int, default=3041)
    args = parser.parse_args()

    root = Path(args.root)
    episode = root / "courses" / args.episode
    qa_dir = episode / "qa"
    runtime_dir = qa_dir / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []
    chrome = find_chrome()
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
    pnpm_cmd = (["cmd", "/c", pnpm] if pnpm and pnpm.lower().endswith((".cmd", ".bat")) else ([pnpm] if pnpm else []))

    # --- Motion typecheck -------------------------------------------------
    motion_dir = episode / "04_motion_src"
    segments_path = motion_dir / "segments.json"
    segments = []
    if segments_path.is_file():
        try:
            data = json.loads(segments_path.read_text(encoding="utf-8"))
            segments = [s for s in data.get("segments", []) if isinstance(s, dict)]
        except Exception:
            segments = []

    if motion_dir.is_dir() and (motion_dir / "package.json").is_file():
        if not pnpm_cmd:
            checks.append({"kind": "typecheck", "status": "BLOCKED", "reason": "pnpm not found"})
        else:
            proc = subprocess.run(
                pnpm_cmd + ["--dir", str(motion_dir), "typecheck"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
            )
            log = runtime_dir / "typecheck.log"
            log.write_text((proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8")
            checks.append({
                "kind": "typecheck",
                "status": "PASS" if proc.returncode == 0 else "FAIL",
                "exit_code": proc.returncode,
                "log": "qa/runtime/typecheck.log",
            })
    else:
        checks.append({"kind": "typecheck", "status": "NOT_APPLICABLE", "reason": "no 04_motion_src"})

    # --- Motion probes ----------------------------------------------------
    motion_segments = [s for s in segments if s.get("engine") == "motion"]
    for segment in motion_segments:
        name = segment.get("name")
        declared = segment.get("duration_seconds")
        if not name:
            continue
        if not pnpm_cmd:
            checks.append({"kind": "motion", "name": name, "status": "BLOCKED", "reason": "pnpm not found"})
            continue
        env = os.environ.copy()
        env["MC_SEGMENT"] = str(name)
        env["MC_PORT"] = str(args.motion_port)
        log_path = runtime_dir / f"vite-{name}.log"
        log_handle = log_path.open("w", encoding="utf-8")
        proc = subprocess.Popen(
            pnpm_cmd + ["exec", "vite", "--port", str(args.motion_port), "--strictPort"],
            cwd=str(motion_dir), env=env, stdout=log_handle, stderr=subprocess.STDOUT,
        )
        try:
            url = f"http://localhost:{args.motion_port}/record.html?segment={name}&probe=1"
            if not http_ready(url, timeout=30):
                checks.append({
                    "kind": "motion", "name": name, "status": "FAIL",
                    "reason": "Vite did not become ready", "log": f"qa/runtime/vite-{name}.log",
                })
                continue
            if not chrome:
                checks.append({"kind": "motion", "name": name, "status": "BLOCKED", "reason": "Chrome not found"})
                continue
            user_dir = Path(tempfile.mkdtemp(prefix="cs-chrome-motion-"))
            try:
                code, dom, stderr = chrome_dump_dom(chrome, url, user_dir)
            finally:
                shutil.rmtree(user_dir, ignore_errors=True)
            match = re.search(r'<div id="mc-status">(.*?)</div>', dom, re.S)
            status_json = None
            if match:
                try:
                    status_json = json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    status_json = None
            probe_path = runtime_dir / f"probe-{name}.json"
            if status_json is not None:
                probe_path.write_text(json.dumps(status_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if code != 0 or status_json is None:
                checks.append({
                    "kind": "motion", "name": name, "status": "FAIL",
                    "reason": "Chrome dump failed or mc-status missing",
                    "exit_code": code, "log": f"qa/runtime/probe-{name}.json",
                })
                continue
            seconds = status_json.get("seconds")
            ready = status_json.get("ready") is True
            ok = ready and isinstance(seconds, (int, float)) and isinstance(declared, (int, float)) and abs(float(seconds) - float(declared)) <= 2.0
            checks.append({
                "kind": "motion", "name": name,
                "status": "PASS" if ok else "FAIL",
                "declared_seconds": declared,
                "probe_seconds": seconds,
                "probe_frames": status_json.get("durationFrames"),
                "probe_fps": status_json.get("fps"),
                "log": f"qa/runtime/probe-{name}.json",
            })
        except Exception as exc:
            checks.append({"kind": "motion", "name": name, "status": "BLOCKED", "reason": str(exc)})
        finally:
            log_handle.close()
            kill_process(proc)

    # --- Reveal browser ---------------------------------------------------
    reveal_path = episode / "03_slides" / "index.html"
    if reveal_path.is_file():
        python = shutil.which("python") or sys.executable
        server = subprocess.Popen(
            [python, "-m", "http.server", str(args.reveal_port), "--bind", "127.0.0.1"],
            cwd=str(reveal_path.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            url = f"http://127.0.0.1:{args.reveal_port}/index.html"
            if not http_ready(url, timeout=20):
                checks.append({"kind": "browser", "deck": "reveal", "status": "FAIL", "reason": "static server not ready"})
            elif not chrome:
                checks.append({"kind": "browser", "deck": "reveal", "status": "BLOCKED", "reason": "Chrome not found"})
            else:
                user_dir = Path(tempfile.mkdtemp(prefix="cs-chrome-reveal-"))
                try:
                    code, dom, stderr = chrome_dump_dom(chrome, url + "#/0", user_dir)
                finally:
                    shutil.rmtree(user_dir, ignore_errors=True)
                slides = [int(x) for x in re.findall(r'data-slide\s*=\s*["\'](\d+)["\']', dom)]
                expected = list(range(1, len(slides) + 1))
                screens = []
                if code == 0 and slides == expected and slides:
                    for page in range(1, len(slides) + 1):
                        shot = runtime_dir / "screens" / f"slide-{page}.png"
                        shot_user = Path(tempfile.mkdtemp(prefix="cs-chrome-shot-"))
                        try:
                            shot_code, _ = chrome_screenshot(
                                chrome, f"{url}#/{page - 1}", shot, shot_user
                            )
                        finally:
                            shutil.rmtree(shot_user, ignore_errors=True)
                        if shot_code == 0 and shot.is_file() and shot.stat().st_size > 0:
                            screens.append(f"qa/runtime/screens/slide-{page}.png")
                ok = code == 0 and slides == expected and bool(slides) and bool(screens)
                checks.append({
                    "kind": "browser", "deck": "reveal",
                    "status": "PASS" if ok else "FAIL",
                    "slides": len(slides),
                    "screenshots": screens,
                    f"notes": f"Chrome DOM + all {len(slides)} page screenshots; console errors not captured by this runner.",
                })
        except Exception as exc:
            checks.append({"kind": "browser", "deck": "reveal", "status": "BLOCKED", "reason": str(exc)})
        finally:
            kill_process(server)
    elif (episode / "03_slides" / "slides.md").is_file():
        checks.append({
            "kind": "build", "deck": "slidev", "status": "NOT_APPLICABLE",
            "reason": "Slidev build is executed by check-episode --stage qa --strict",
        })
    else:
        checks.append({"kind": "browser", "deck": "none", "status": "NOT_APPLICABLE", "reason": "no deck"})

    statuses = [check.get("status") for check in checks]
    if "FAIL" in statuses:
        status = "FAIL"
    elif "BLOCKED" in statuses:
        status = "BLOCKED"
    elif all(s in {"PASS", "NOT_APPLICABLE"} for s in statuses):
        status = "PASS"
    else:
        status = "BLOCKED"

    evidence = {
        "contract_version": "1.0.0",
        "episode_id": args.episode,
        "generated_at": utc_now(),
        "status": status,
        "checks": checks,
    }
    (qa_dir / "runtime.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": status, "checks": checks}, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
