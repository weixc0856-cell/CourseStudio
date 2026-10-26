#!/usr/bin/env python3
"""Negative tests for the check-episode.py hard-fail gates."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-episode.py")
RESEARCH_FILES = [
    "00-task-brief.md",
    "01-source-inventory.md",
    "02-claim-evidence-ledger.csv",
    "03-knowledge-structure.md",
    "04-course-input-brief.md",
    "05-quality-report.md",
    "06-course-outline.md",
]
SLIDES_2 = """---
theme: default
title: Test
---

# One

---

# Two
"""
SLIDES_4 = """---
theme: default
title: Test
---

# One

---

# Two

---

# Three

---

# Four
"""
SCENE_OK = """from manim import *

class Test(Scene):
    def construct(self):
        self.play(Create(Circle()), run_time=1)
"""


class CheckEpisodeNegativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "courses").mkdir()
        (self.root / "tools").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def make_course(self, slug: str = "ep", mode: str = "technical") -> Path:
        ep = self.root / "courses" / slug
        (ep / "01_research").mkdir(parents=True)
        (ep / "02_scripts").mkdir()
        (ep / "03_slides" / "public").mkdir(parents=True)
        (ep / "04_manim_src" / "scenes").mkdir(parents=True)

        if mode in {"course", "technical"}:
            for name in RESEARCH_FILES:
                (ep / "01_research" / name).write_text(
                    f"content for {name}\n", encoding="utf-8"
                )
        else:
            (ep / "01_research" / "source-register.md").write_text(
                "# Sources\n\n- source A\n", encoding="utf-8"
            )
            (ep / "01_research" / "claims-ledger.md").write_text(
                "CLM-001 FACT: something\nCLM-002 CLAIM: someone says\n",
                encoding="utf-8",
            )

        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[SLIDE: 02]\n", encoding="utf-8"
        )
        (ep / "03_slides" / "slides.md").write_text(SLIDES_2, encoding="utf-8")
        (ep / "handoff.md").write_text("# Handoff\n\nstage: test\n", encoding="utf-8")
        return ep

    def add_fake_ffprobe(self, seconds: str = "25.0") -> dict | None:
        """Create a POSIX ffprobe shim so CI does not need ffmpeg installed."""
        if os.name == "nt":
            return None
        bin_dir = self.root / "fakebin"
        bin_dir.mkdir(exist_ok=True)
        path = bin_dir / "ffprobe"
        path.write_text(f"#!/bin/sh\necho {seconds}\n", encoding="utf-8")
        path.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        return env

    def run_checker(
        self,
        slug: str,
        mode: str = "technical",
        stage: str = "qa",
        strict: bool = True,
        env: dict | None = None,
    ) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(CHECKER),
            slug,
            "--root",
            str(self.root),
            "--mode",
            mode,
            "--stage",
            stage,
        ]
        if strict:
            args.append("--strict")
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env or os.environ.copy(),
            timeout=180,
        )

    def assert_fails(self, proc: subprocess.CompletedProcess, needle: str) -> None:
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertNotEqual(proc.returncode, 0, f"expected non-zero exit\n{output}")
        self.assertIn(needle, output, f"expected {needle!r} in output\n{output}")

    # 1. Required research file exists but is empty.
    def test_empty_research(self) -> None:
        ep = self.make_course()
        (ep / "01_research" / "03-knowledge-structure.md").write_text("", encoding="utf-8")

        strict_proc = self.run_checker("ep", stage="script", strict=True)
        self.assert_fails(strict_proc, "empty:")

        qa_proc = self.run_checker("ep", stage="qa", strict=False)
        self.assert_fails(qa_proc, "empty:")

    # 2. Duplicate slide anchors.
    def test_duplicate_anchors(self) -> None:
        ep = self.make_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[SLIDE: 02]\n[SLIDE: 02]\n", encoding="utf-8"
        )
        proc = self.run_checker("ep", stage="script", strict=True)
        self.assert_fails(proc, "strictly 1..N")

    # 3. Animation anchor without an MP4.
    def test_missing_mp4(self) -> None:
        ep = self.make_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[ANIMATION: test]\n", encoding="utf-8"
        )
        (ep / "04_manim_src" / "scenes" / "test.py").write_text(SCENE_OK, encoding="utf-8")
        proc = self.run_checker("ep", stage="manim", strict=True)
        self.assert_fails(proc, "missing MP4")

    # 4. A real MP4 longer than 20 seconds.
    def test_timeout_mp4(self) -> None:
        ep = self.make_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[ANIMATION: test]\n", encoding="utf-8"
        )
        (ep / "04_manim_src" / "scenes" / "test.py").write_text(SCENE_OK, encoding="utf-8")
        mp4 = ep / "03_slides" / "public" / "test.mp4"
        env = None
        if shutil.which("ffmpeg") and shutil.which("ffprobe"):
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", "color=c=black:s=64x64:d=25",
                    "-r", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(mp4),
                ],
                capture_output=True, check=True, timeout=120,
            )
        else:
            mp4.write_bytes(b"not-a-real-video")
            env = self.add_fake_ffprobe("25.0")
            if env is None:
                self.skipTest("ffmpeg/ffprobe not available and no POSIX fake")
        proc = self.run_checker("ep", stage="manim", strict=True, env=env)
        self.assert_fails(proc, "exceeds 20s")

    # 5. Slidev build returns non-zero.
    def test_build_fail(self) -> None:
        self.make_course()
        build_script = self.root / "tools" / "slidev-run.ps1"
        build_script.write_text(
            'Write-Output "forced build failure"\nexit 1\n', encoding="utf-8"
        )
        proc = self.run_checker("ep", stage="qa", strict=True)
        self.assert_fails(proc, "Slidev build failed")

    # 6. N >= M is allowed and reported; buffer pages are legal.
    def test_mapping_buffer_ok(self) -> None:
        ep = self.make_course()
        (ep / "03_slides" / "slides.md").write_text(SLIDES_4, encoding="utf-8")
        proc = self.run_checker("ep", stage="slides", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("Mapping: 2 anchor(s), 4 slide(s), buffer 2", output)

    # 7. M > N must fail.
    def test_mapping_too_many_anchors(self) -> None:
        ep = self.make_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[SLIDE: 02]\n[SLIDE: 03]\n", encoding="utf-8"
        )
        proc = self.run_checker("ep", stage="slides", strict=True)
        self.assert_fails(proc, "exceed Slidev slide count")


if __name__ == "__main__":
    unittest.main(verbosity=2)
