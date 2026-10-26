#!/usr/bin/env python3
"""Regression tests for audience-deck internal metadata leakage.

These tests inspect the final audience HTML files, not only templates or source
generators. They intentionally use a narrow, justified pattern set.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REAL_DECK = REPO / "courses" / "transformer-self-attention" / "03_slides" / "index.html"
TEMPLATE_DECK = REPO / "tools" / "episode-template" / "03_slides" / "index.html"
REAL_RECORDING = REPO / "courses" / "transformer-self-attention" / "05_recording"

# Narrow patterns: internal recording control and production paths only.
# Do not include generic labels such as "S02" that can be legitimate section names.
FORBIDDEN = [
    "record.html",
    "?segment=",
    "05_recording/",
    "qa/",
    "research/",
    "CLM-",
    "NOT_RUN",
    "PASS_VERIFIED",
]


class AudienceDeckLeakTests(unittest.TestCase):
    def assert_clean(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = [pattern for pattern in FORBIDDEN if pattern in text]
        self.assertEqual(hits, [], f"{path.relative_to(REPO)} contains internal metadata: {hits}")

    def test_real_audience_deck_has_no_internal_metadata(self) -> None:
        self.assert_clean(REAL_DECK)

    def test_template_audience_deck_has_no_internal_metadata(self) -> None:
        self.assert_clean(TEMPLATE_DECK)

    def test_real_deck_keeps_teaching_content(self) -> None:
        text = REAL_DECK.read_text(encoding="utf-8", errors="replace")
        self.assertIn("scores_to_weights", text)
        self.assertEqual(text.count('data-slide="'), 12)

    def test_internal_recording_metadata_keeps_control_url(self) -> None:
        expected = "record.html?segment=scores_to_weights"
        manifest = json.loads((REAL_RECORDING / "manifest.json").read_text(encoding="utf-8"))
        urls = [segment.get("url", "") for segment in manifest.get("segments", [])]
        self.assertTrue(any(expected in url for url in urls), urls)
        checklist = (REAL_RECORDING / "checklist.md").read_text(encoding="utf-8")
        self.assertIn(expected, checklist)
        cue = (REAL_RECORDING / "cues" / "scores_to_weights.md").read_text(encoding="utf-8")
        self.assertIn(expected, cue)


if __name__ == "__main__":
    unittest.main(verbosity=2)
