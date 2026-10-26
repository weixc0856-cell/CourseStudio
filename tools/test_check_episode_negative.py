#!/usr/bin/env python3
"""Regression tests for check-episode.py gates, including motion/recording."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-episode.py")
BUILDER = Path(__file__).with_name("build-recording-package.py")
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
MOTION_SCENE = """import {makeScene2D} from '@motion-canvas/2d';

export default makeScene2D(function* () {});
"""
MOTION_PROJECT = """import {makeProject} from '@motion-canvas/core';
import scene from '../scenes/demo?scene';

export default makeProject({scenes: [scene]});
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

    def make_motion_course(
        self,
        slug: str = "motion",
        duration: float = 60,
        engine: str | None = "motion",
        include_package: bool = True,
        segments: list[dict] | None = None,
    ) -> Path:
        ep = self.make_course(slug=slug, mode="technical")
        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[SLIDE: 02]\n"
            "[ANIMATION: demo]\n"
            f"[SEGMENT: demo | {duration:g}s | order=1]\n"
            "[VISUAL 00:00] 起手画面\n"
            "[HOLD 00:10] 停 2 秒\n"
            "[EMPHASIS 00:20] 强调关键量\n"
            "[CUT 00:30] 切换视图\n"
            "（口播：示例口播）\n",
            encoding="utf-8",
        )
        motion = ep / "04_motion_src"
        (motion / "src" / "scenes").mkdir(parents=True)
        (motion / "src" / "projects").mkdir(parents=True)
        (motion / "src" / "scenes" / "demo.tsx").write_text(MOTION_SCENE, encoding="utf-8")
        (motion / "src" / "projects" / "demo.ts").write_text(MOTION_PROJECT, encoding="utf-8")

        if segments is None:
            entry = {
                "name": "demo",
                "duration_seconds": duration,
                "order": 1,
                "scene": "demo",
                "record_status": "NOT_RUN",
            }
            if engine is not None:
                entry["engine"] = engine
            segments = [entry]
        (motion / "segments.json").write_text(
            json.dumps({"segments": segments}), encoding="utf-8"
        )

        if include_package:
            package = ep / "05_recording"
            (package / "cues").mkdir(parents=True)
            (package / "recordings").mkdir()
            (package / "cues" / "demo.md").write_text("# demo cue\n", encoding="utf-8")
            (package / "checklist.md").write_text(
                "# checklist\n\nOBS is manual.\n", encoding="utf-8"
            )
            (package / "manifest.json").write_text(
                json.dumps({
                    "segments": [{
                        "name": "demo",
                        "url": "http://localhost:9100/record.html?segment=demo",
                        "declared_seconds": duration,
                        "cue": "cues/demo.md",
                        "order": 1,
                    }]
                }),
                encoding="utf-8",
            )
        return ep

    def motion_script(self, segment: str = "[SEGMENT: demo | 60s | order=1]", cues: list[str] | None = None) -> str:
        if cues is None:
            cues = [
                "[VISUAL 00:00] 起手画面",
                "[HOLD 00:10] 停 2 秒",
                "[EMPHASIS 00:20] 强调关键量",
                "[CUT 00:30] 切换视图",
            ]
        return (
            "[SLIDE: 01]\n[SLIDE: 02]\n[ANIMATION: demo]\n"
            + segment + "\n"
            + "\n".join(cues) + "\n"
            + "（口播：示例口播）\n"
        )

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
        status_mode: str = "legacy",
        extra: list[str] | None = None,
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
            "--status-mode",
            status_mode,
        ]
        if strict:
            args.append("--strict")
        if extra:
            args.extend(extra)
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env or os.environ.copy(),
            timeout=180,
        )

    def run_contract_checker(
        self,
        slug: str,
        mode: str = "technical",
        stage: str = "qa",
        strict: bool = True,
        extra: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        return self.run_checker(
            slug, mode=mode, stage=stage, strict=strict, status_mode="contract", extra=extra
        )

    def run_builder(self, slug: str, *extra: str) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(BUILDER),
            slug,
            "--root",
            str(self.root),
            *extra,
        ]
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
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

    # 8. Motion segment happy path.
    def test_motion_stage_ok(self) -> None:
        self.make_motion_course()
        proc = self.run_checker("motion", stage="motion", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("engine=motion", output)
        self.assertIn("declared=60.0s", output)
        self.assertIn("real=NOT_VERIFIED", output)

    # 9. Missing [SEGMENT] is a hard failure at script stage.
    def test_timing_missing_segment(self) -> None:
        ep = self.make_motion_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            self.motion_script(segment=""), encoding="utf-8"
        )
        proc = self.run_checker("motion", stage="script", strict=True)
        self.assert_fails(proc, "expected exactly one [SEGMENT]")

    # 10. HOLD / EMPHASIS / CUT are required.
    def test_timing_missing_required_cue(self) -> None:
        ep = self.make_motion_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            self.motion_script(cues=[
                "[VISUAL 00:00] 起手画面",
                "[EMPHASIS 00:20] 强调关键量",
                "[CUT 00:30] 切换视图",
            ]),
            encoding="utf-8",
        )
        proc = self.run_checker("motion", stage="script", strict=True)
        self.assert_fails(proc, "missing [HOLD]")

    # 11. Timestamps must be strictly increasing.
    def test_timing_out_of_order(self) -> None:
        ep = self.make_motion_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            self.motion_script(cues=[
                "[VISUAL 00:20] 起手画面",
                "[HOLD 00:10] 停 2 秒",
                "[EMPHASIS 00:30] 强调关键量",
                "[CUT 00:40] 切换视图",
            ]),
            encoding="utf-8",
        )
        proc = self.run_checker("motion", stage="script", strict=True)
        self.assert_fails(proc, "strictly increasing")

    # 12. The last cue may not exceed the declared duration.
    def test_timing_beyond_duration(self) -> None:
        ep = self.make_motion_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            self.motion_script(cues=[
                "[VISUAL 00:00] 起手画面",
                "[HOLD 00:10] 停 2 秒",
                "[EMPHASIS 00:20] 强调关键量",
                "[CUT 01:10] 切换视图",
            ]),
            encoding="utf-8",
        )
        proc = self.run_checker("motion", stage="script", strict=True)
        self.assert_fails(proc, "exceeds declared duration")

    # 13. [SEGMENT] duration/order must match segments.json.
    def test_timing_duration_mismatch(self) -> None:
        ep = self.make_motion_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            self.motion_script(segment="[SEGMENT: demo | 45s | order=1]"),
            encoding="utf-8",
        )
        proc = self.run_checker("motion", stage="script", strict=True)
        self.assert_fails(proc, "differs from segments.json")

    # 14. Motion duration outside 45-90.
    def test_motion_duration_out_of_range(self) -> None:
        self.make_motion_course(duration=20)
        proc = self.run_checker("motion", stage="motion", strict=True)
        self.assert_fails(proc, "outside 45-90s")

    # 15. Engine missing and both engines present.
    def test_motion_engine_ambiguous(self) -> None:
        ep = self.make_motion_course(engine=None)
        (ep / "04_manim_src" / "scenes" / "demo.py").write_text(SCENE_OK, encoding="utf-8")
        proc = self.run_checker("motion", stage="motion", strict=True)
        self.assert_fails(proc, "engine missing and both")

    # 16. Cue is owned by package/recording; motion stage must not depend on it.
    def test_motion_missing_cue(self) -> None:
        ep = self.make_motion_course()
        (ep / "05_recording" / "cues" / "demo.md").unlink()
        motion = self.run_checker("motion", stage="motion", strict=True)
        motion_output = (motion.stdout or "") + (motion.stderr or "")
        self.assertEqual(motion.returncode, 0, motion_output)
        self.assertIn("missing cue", motion_output)
        recording = self.run_checker("motion", stage="recording", strict=False)
        self.assert_fails(recording, "missing cue")

    # 17. Order must be continuous.
    def test_motion_order_gap(self) -> None:
        self.make_motion_course(segments=[{
            "name": "demo",
            "engine": "motion",
            "duration_seconds": 60,
            "order": 2,
            "scene": "demo",
            "record_status": "NOT_RUN",
        }])
        proc = self.run_checker("motion", stage="motion", strict=True)
        self.assert_fails(proc, "continuous 1..N")

    # 18. Recording package is complete; recordings and their directory are optional.
    def test_recording_package_ok(self) -> None:
        ep = self.make_motion_course()
        shutil.rmtree(ep / "05_recording" / "recordings")
        proc = self.run_checker("motion", stage="recording", strict=False)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("Recording: checked", output)
        self.assertIn("recordings_dir=optional", output)
        self.assertIn("recordings=0", output)

    # 19. Recording package missing.
    def test_recording_package_missing(self) -> None:
        self.make_motion_course(include_package=False)
        proc = self.run_checker("motion", stage="recording", strict=False)
        self.assert_fails(proc, "missing or empty 05_recording/manifest.json")

    # 20. Strict QA accepts a complete motion episode and recording package.
    def test_motion_qa_strict_ok(self) -> None:
        self.make_motion_course()
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_checker("motion", stage="qa", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("Build:   PASS", output)
        self.assertIn("Recording: checked", output)

    # 21. Strict QA requires the recording package for motion episodes.
    def test_motion_qa_strict_requires_recording_package(self) -> None:
        self.make_motion_course(include_package=False)
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_checker("motion", stage="qa", strict=True)
        self.assert_fails(proc, "missing or empty 05_recording/manifest.json")

    # 22. Builder generates manifest, cue and checklist from the script.
    def test_builder_generates_package(self) -> None:
        ep = self.make_motion_course()
        proc = self.run_builder("motion")
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)

        manifest = json.loads((ep / "05_recording" / "manifest.json").read_text(encoding="utf-8"))
        segment = manifest["segments"][0]
        self.assertEqual(segment["name"], "demo")
        self.assertEqual(segment["declared_seconds"], 60)
        self.assertIn("record.html?segment=demo", segment["url"])

        cue = (ep / "05_recording" / "cues" / "demo.md").read_text(encoding="utf-8")
        for tag in ("VISUAL", "HOLD", "EMPHASIS", "CUT"):
            self.assertIn(tag, cue)
        self.assertIn("口播", cue)

        checklist = (ep / "05_recording" / "checklist.md").read_text(encoding="utf-8")
        self.assertIn("| 1 | demo |", checklist)
        self.assertIn("record.html?segment=demo", checklist)

    # 23. Builder is idempotent and preserves record_status.
    def test_builder_idempotent_and_preserves_status(self) -> None:
        ep = self.make_motion_course()
        self.assertEqual(self.run_builder("motion").returncode, 0)
        manifest_path = ep / "05_recording" / "manifest.json"
        cue_path = ep / "05_recording" / "cues" / "demo.md"
        checklist_path = ep / "05_recording" / "checklist.md"
        first_manifest = manifest_path.read_text(encoding="utf-8")
        first_cue = cue_path.read_text(encoding="utf-8")
        first_checklist = checklist_path.read_text(encoding="utf-8")

        self.assertEqual(self.run_builder("motion").returncode, 0)
        self.assertEqual(manifest_path.read_text(encoding="utf-8"), first_manifest)
        self.assertEqual(cue_path.read_text(encoding="utf-8"), first_cue)
        self.assertEqual(checklist_path.read_text(encoding="utf-8"), first_checklist)

        data = json.loads(first_manifest)
        data["segments"][0]["record_status"] = "RECORDED"
        manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.assertEqual(self.run_builder("motion").returncode, 0)
        updated = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["segments"][0]["record_status"], "RECORDED")

    # 24. Builder validates before writing; an invalid script leaves the package alone.
    def test_builder_rejects_invalid_timing(self) -> None:
        ep = self.make_motion_course()
        manifest_path = ep / "05_recording" / "manifest.json"
        before = manifest_path.read_text(encoding="utf-8")
        (ep / "02_scripts" / "lecture_script.md").write_text(
            self.motion_script(cues=[
                "[VISUAL 00:00] 起手画面",
                "[EMPHASIS 00:20] 强调关键量",
                "[CUT 00:30] 切换视图",
            ]),
            encoding="utf-8",
        )
        proc = self.run_builder("motion")
        self.assert_fails(proc, "missing [HOLD]")
        self.assertEqual(manifest_path.read_text(encoding="utf-8"), before)

    # 25. Builder requires at least one engine=motion segment.
    def test_builder_requires_motion_entries(self) -> None:
        ep = self.make_motion_course()
        data = json.loads((ep / "04_motion_src" / "segments.json").read_text(encoding="utf-8"))
        data["segments"][0]["engine"] = "manim"
        (ep / "04_motion_src" / "segments.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        proc = self.run_builder("motion")
        self.assert_fails(proc, "no engine=motion")

    # 26. --check validates without writing.
    def test_builder_check_only(self) -> None:
        ep = self.make_motion_course()
        manifest_path = ep / "05_recording" / "manifest.json"
        before = manifest_path.read_text(encoding="utf-8")
        proc = self.run_builder("motion", "--check")
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("CHECK_ONLY", output)
        self.assertEqual(manifest_path.read_text(encoding="utf-8"), before)

    # 27. Reveal deck adapter counts data-slide.
    def test_reveal_deck_adapter(self) -> None:
        ep = self.make_course()
        (ep / "03_slides" / "slides.md").unlink()
        (ep / "03_slides" / "index.html").write_text(
            '<section data-slide="01">One</section>\n'
            '<section data-slide="02">Two</section>\n',
            encoding="utf-8",
        )
        proc = self.run_checker("ep", stage="slides", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("[reveal]", output)
        self.assertIn("Mapping: 2 anchor(s), 2 slide(s)", output)

    # 28. Reveal deck without data-slide is invalid.
    def test_reveal_missing_data_slide(self) -> None:
        ep = self.make_course()
        (ep / "03_slides" / "slides.md").unlink()
        (ep / "03_slides" / "index.html").write_text(
            '<div class="slides"><section class="c-slide">One</section>'
            '<section class="c-slide">Two</section></div>\n',
            encoding="utf-8",
        )
        proc = self.run_checker("ep", stage="slides", strict=True)
        self.assert_fails(proc, "no data-slide")

    # 29. Reveal data-slide values must be strictly 1..N in document order.
    def test_reveal_page_gap(self) -> None:
        ep = self.make_course()
        (ep / "03_slides" / "slides.md").unlink()
        (ep / "03_slides" / "index.html").write_text(
            '<section class="c-slide" data-slide="01">One</section>\n'
            '<section class="c-slide" data-slide="03">Three</section>\n',
            encoding="utf-8",
        )
        proc = self.run_checker("ep", stage="slides", strict=True)
        self.assert_fails(proc, "strictly 1..N")

    # 30. Local Reveal assets must exist.
    def test_reveal_missing_local_asset(self) -> None:
        ep = self.make_course()
        (ep / "03_slides" / "slides.md").unlink()
        (ep / "03_slides" / "index.html").write_text(
            '<link rel="stylesheet" href="./assets/missing.css" />\n'
            '<section class="c-slide" data-slide="01">One</section>\n'
            '<section class="c-slide" data-slide="02">Two</section>\n',
            encoding="utf-8",
        )
        proc = self.run_checker("ep", stage="slides", strict=True)
        self.assert_fails(proc, "missing local asset")

    # 31. Reveal strict QA skips the Slidev build.
    def test_reveal_strict_skips_slidev_build(self) -> None:
        ep = self.make_course()
        (ep / "03_slides" / "slides.md").unlink()
        (ep / "03_slides" / "index.html").write_text(
            '<section class="c-slide" data-slide="01">One</section>\n'
            '<section class="c-slide" data-slide="02">Two</section>\n',
            encoding="utf-8",
        )
        proc = self.run_checker("ep", stage="qa", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("SKIPPED", output)

    # 32. Legacy Manim fallback remains available with a deprecation warning.
    def test_legacy_manim_deprecation(self) -> None:
        ep = self.make_course()
        (ep / "02_scripts" / "lecture_script.md").write_text(
            "[SLIDE: 01]\n[SLIDE: 02]\n[ANIMATION: test]\n", encoding="utf-8"
        )
        (ep / "04_manim_src" / "scenes" / "test.py").write_text(SCENE_OK, encoding="utf-8")
        (ep / "03_slides" / "public" / "test.mp4").write_bytes(b"not-a-real-video")
        proc = self.run_checker("ep", stage="script", strict=False)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertIn("legacy Manim", output)


    # 33. Contract QA blocks when required runtime/content evidence is missing.
    def test_contract_qa_blocks_without_evidence(self) -> None:
        self.make_motion_course()
        proc = self.run_contract_checker("motion", stage="qa", strict=False)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 2, output)
        self.assertIn("BLOCKED", output)
        self.assertIn("RUNTIME=NOT_RUN", output)
        self.assertIn("CONTENT_QUALITY=NOT_RUN", output)
        self.assertNotIn("PASS_VERIFIED", output)

    # 34. Contract QA becomes READY only with both runtime and content evidence.
    def test_contract_qa_ready_with_evidence(self) -> None:
        ep = self.make_motion_course()
        qa = ep / "qa"
        qa.mkdir(exist_ok=True)
        (qa / "runtime.json").write_text(
            json.dumps({
                "status": "PASS",
                "checks": [
                    {"kind": "motion", "name": "demo", "status": "PASS", "probe_seconds": 60.0},
                    {"kind": "build", "status": "PASS"},
                ],
            }),
            encoding="utf-8",
        )
        (qa / "content-quality.json").write_text(
            json.dumps({"status": "PASS", "checks": [{"kind": "content", "status": "PASS"}]}),
            encoding="utf-8",
        )
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_contract_checker("motion", stage="qa", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("READY", output)
        self.assertIn("RUNTIME=PASS", output)
        self.assertIn("CONTENT_QUALITY=PASS", output)
        self.assertIn("DELIVERY=READY", output)

    # 35. Motion stage no longer requires a cue generated by the later package stage.
    def test_contract_motion_without_cue_passes(self) -> None:
        self.make_motion_course(include_package=False)
        proc = self.run_contract_checker("motion", stage="motion", strict=False)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("STRUCTURAL_PASS", output)
        self.assertIn("missing cue", output)

    # 36. Missing handoff is a required structural failure, not a warning-only pass.
    def test_contract_missing_handoff_fails(self) -> None:
        ep = self.make_course()
        (ep / "handoff.md").unlink()
        proc = self.run_contract_checker("ep", stage="script", strict=False)
        self.assert_fails(proc, "missing handoff.md")

    # 37. Legacy status mode remains available for old callers.
    def test_legacy_status_mode_still_reports_pass_verified(self) -> None:
        self.make_motion_course()
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_checker("motion", stage="qa", strict=True, status_mode="legacy")
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("PASS_VERIFIED", output)


    # 38. Runtime failure is a contract FAIL, not a blocked pass.
    def test_contract_qa_runtime_failure_fails(self) -> None:
        ep = self.make_motion_course()
        qa = ep / "qa"; qa.mkdir(exist_ok=True)
        (qa / "runtime.json").write_text(json.dumps({"status": "FAIL", "checks": []}), encoding="utf-8")
        (qa / "content-quality.json").write_text(json.dumps({"status": "PASS", "checks": [{"status": "PASS"}]}), encoding="utf-8")
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_contract_checker("motion", stage="qa", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 1, output)
        self.assertIn("FAIL", output)

    # 39. Content NEEDS_REVIEW is a distinct non-ready state.
    def test_contract_qa_content_needs_review(self) -> None:
        ep = self.make_motion_course()
        qa = ep / "qa"; qa.mkdir(exist_ok=True)
        (qa / "runtime.json").write_text(json.dumps({
            "status": "PASS",
            "checks": [
                {"kind": "motion", "name": "demo", "status": "PASS", "probe_seconds": 60.0},
                {"kind": "build", "status": "PASS"},
            ],
        }), encoding="utf-8")
        (qa / "content-quality.json").write_text(json.dumps({"status": "NEEDS_REVIEW", "checks": [{"status": "NEEDS_REVIEW"}]}), encoding="utf-8")
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_contract_checker("motion", stage="qa", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 2, output)
        self.assertIn("NEEDS_REVIEW", output)

    # 40. Missing runtime tool/evidence is BLOCKED, not NOT_APPLICABLE.
    def test_contract_qa_runtime_blocked(self) -> None:
        ep = self.make_motion_course()
        qa = ep / "qa"; qa.mkdir(exist_ok=True)
        (qa / "runtime.json").write_text(json.dumps({"status": "BLOCKED", "checks": []}), encoding="utf-8")
        (qa / "content-quality.json").write_text(json.dumps({"status": "PASS", "checks": [{"status": "PASS"}]}), encoding="utf-8")
        build = self.root / "tools" / "slidev-run.ps1"
        build.write_text('Write-Output "fake build ok"\nexit 0\n', encoding="utf-8")
        proc = self.run_contract_checker("motion", stage="qa", strict=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 2, output)
        self.assertIn("BLOCKED", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
