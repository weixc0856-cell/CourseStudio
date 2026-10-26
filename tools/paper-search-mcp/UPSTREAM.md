# Upstream — paper-search-mcp

- Source: <https://github.com/openags/paper-search-mcp>
- Vendored commit: `cab1b5cc276a0cd004a0044003926a6440088049`
- Vendored on: 2026-10-26
- License: MIT (see `LICENSE`)

## Local additions

- `bin/paper-search` / `bin/paper-search.cmd`：项目内启动器，固定 venv 与 `.config/paper-search-mcp/.env`。
- `skill/paper-search/SKILL.md`：Claude Code Skill 实体（全局 junction 指向这里）。
- `UPSTREAM.md`：本文件。

## Environment

- `.venv/` 由 `uv sync --frozen --python 3.12` 在本地创建，不提交。
- 上游 `.git` 已移到 `D:\CourseStudio\.uv-cache\paper-search-mcp-upstream.git`，保留本地历史，不进入根仓库。

## Update

重新克隆或对比上游后，把改动应用到本目录，并保留 `bin/`、`skill/` 与 `UPSTREAM.md`。不要删除本地启动器。
