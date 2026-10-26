"""Check relative Markdown links in a project tree.

Usage:
    python tools/check-links.py [root]

Skips external URLs, anchors, fenced code blocks, and generated/heavy folders.
Exits non-zero if a relative target does not exist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_DIRS = {
    ".venv",
    ".git",
    "rendered",
    "chrome-profile",
    "chrome-profile-test",
    "node_modules",
    ".uv-cache",
    "__pycache__",
}


def markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def main() -> int:
    missing: list[tuple[Path, int, str]] = []
    checked = 0
    for path in markdown_files(ROOT):
        in_fence = False
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for raw in LINK_RE.findall(line):
                target = raw.strip()
                if not target or target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                    continue
                if "://" in target:
                    continue
                target = target.strip("<>").split("#", 1)[0].strip()
                if not target:
                    continue
                checked += 1
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    missing.append((path, lineno, target))
    for path, lineno, target in missing:
        print(f"MISSING {path.relative_to(ROOT)}:{lineno} -> {target}")
    print(f"checked {checked} relative links in {ROOT}")
    print("PASS_VERIFIED" if not missing else f"FAIL: {len(missing)} missing")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
