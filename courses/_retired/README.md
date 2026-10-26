# Retired courses (legacy archive)

This directory is **not** part of the active course set. Do not use it as a template or as evidence for the current pipeline.

| Directory | Retired because | What is kept |
| --- | --- | --- |
| `transformer-course-pilot/` | Historical HTML + Manim pilot; not the current Motion Canvas + Reveal path | HTML deck, Manim source/renders, research/QA records for reference |
| `course-attention/` | Historical Slidev + Manim course created before the Motion/Reveal default; `.venv` was removed because it is rebuildable | Research, script, Slidev deck, Manim source, QA records |

Rules:

- New episodes are created under `courses/<slug>/` with `tools/new-episode.ps1`; use `course` for Motion + Reveal or `technical` for Motion + Slidev.
- These directories are excluded from the root Git repository (`/courses/*`). If retained in a course repository, mark them `legacy` and never describe them as the default path.
- For current documentation, start at `README.md`, `courses/README.md`, and `guides/quickstart-episode.md`.
