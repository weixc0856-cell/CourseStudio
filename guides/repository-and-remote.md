# 仓库与远程使用指南

本文件记录 CourseStudio 的 Git 布局、远程仓库、克隆重建、课程独立仓库和日常推送流程。适用于本机与后续新机器。

## 1. 当前远程与分支

| 项目 | 值 |
| --- | --- |
| 远程 | `git@github.com:weixc0856-cell/CourseStudio.git` |
| 分支 | `main` |
| 初始提交 | `541cbee` — `chore: initialize CourseStudio framework pipeline` |
| 本地根目录 | `D:\CourseStudio` |
| 协议 | SSH |

验证：

```bash
git remote -v
git status -sb
git ls-remote origin refs/heads/main
```

## 2. 仓库布局

默认采用**根仓库 + 每课独立仓库**：

| 范围 | 是否进根仓库 | 说明 |
| --- | --- | --- |
| `CLAUDE.md`、`README.md`、`.gitignore`、`.gitattributes` | 是 | 框架与规则 |
| `guides/`、`workflows/`、`prompts/` | 是 | 文档与流程 |
| `tools/` | 是 | 脚手架、检查器、运行时配置、Skill |
| `courses/*` | **默认否** | 根 `.gitignore` 默认忽略；例外：`courses/transformer-self-attention/` 源码与 `courses/_retired/README.md` |
| `labs/` | **否** | 本地实验环境 |
| `.uv-cache/`、`.venv*/`、`node_modules/`、`.pnpm-store/` | 否 | 缓存与依赖 |
| `.config/**/.env`、密钥 | 否 | 本地配置 |

根 [.gitignore](../.gitignore) 的关键规则：

```gitignore
/courses/*
!/courses/README.md
!/courses/transformer-self-attention/
!/courses/_retired/
/courses/_retired/*
!/courses/_retired/README.md
/labs/
```

`transformer-self-attention` 的源码进入根仓库；`node_modules`、`.vendor`、`recordings`、`downloads`、`fulltext` 等仍忽略。其它课程仍建议独立仓库。

课程自己的 `.gitignore` 由 `tools/new-episode.ps1` / `tools/new-course.ps1` 从 [tools/course.gitignore](../tools/course.gitignore) 复制。

## 3. 根仓库跟踪什么

提交：

- 框架文档：`CLAUDE.md`、`README.md`、`guides/`、`workflows/`、`prompts/`
- 工具与模板：`tools/new-episode.ps1`、`tools/episode-template/`、`tools/check-episode.py`、`tools/build-recording-package.py`、`tools/motion-run.ps1`、`tools/reveal-run.ps1`、`tools/slidev-run.ps1`、`tools/render-manim.ps1`
- Motion 模板与运行配置：`tools/motion-runtime/`（package/lock/record.html/src）
- Reveal 运行时配置：`tools/reveal-runtime/package.json`、`pnpm-lock.yaml`、`README.md`
- Slidev 运行时配置：`tools/slidev-runtime/package.json`、`pnpm-lock.yaml`、`.npmrc`、`README.md`、`slides.md`
- 动画 Skill：`tools/skills/motion-isolation/`（默认）、`tools/skills/manim-isolation/`（legacy/fallback）
- `paper-search` 源码与本地 Skill：`tools/paper-search-mcp/`（见第 7 节）

不提交：

- `courses/*`（除 `courses/README.md`、`courses/transformer-self-attention/` 源码与 `courses/_retired/README.md`）与 `labs/`
- PDF、MP4、音频、`animations/rendered/`、`media/`
- `.venv*/`、`node_modules/`、`.pnpm-store/`、`.uv-cache/`
- `.env`、密钥、`.mcp.json`、`CLAUDE.local.md`
- `03_slides/.vendor/`、`05_recording/recordings/`（本地生成）

## 4. 新机器克隆与重建

```bash
git clone git@github.com:weixc0856-cell/CourseStudio.git D:/CourseStudio
cd D:/CourseStudio
```

### 4.1 重建 paper-search 环境

```powershell
cd D:\CourseStudio\tools\paper-search-mcp
uv sync --frozen --python 3.12
```

`uv sync` 会创建 `tools/paper-search-mcp/.venv`（不提交）。`.config/paper-search-mcp/.env` 需要本地重建：

```powershell
mkdir D:\CourseStudio\.config\paper-search-mcp -Force
copy D:\CourseStudio\tools\paper-search-mcp\.env.example D:\CourseStudio\.config\paper-search-mcp\.env
```

再按需填入 API key；不要提交该文件。

### 4.2 重建 Reveal / Slidev 运行时

```powershell
cd D:\CourseStudio\tools\reveal-runtime
pnpm install

cd D:\CourseStudio\tools\slidev-runtime
pnpm install
```

Reveal 用于 course 课件；Slidev 用于 technical / news / 旧课。两者的 `node_modules/` 与 `.pnpm-store/` 都不提交。

### 4.3 挂载全局 Skill

Windows 使用目录 junction（无需管理员）：

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\motion-isolation" -Target "D:\CourseStudio\tools\skills\motion-isolation"
New-Item -ItemType Junction -Path "$HOME\.claude\skills\manim-isolation" -Target "D:\CourseStudio\tools\skills\manim-isolation"
New-Item -ItemType Junction -Path "$HOME\.claude\skills\paper-search" -Target "D:\CourseStudio\tools\paper-search-mcp\skill\paper-search"
```

如果目标已存在，先确认内容再替换。

### 4.4 验证

```powershell
uv --version
pnpm --version
cd D:\CourseStudio\tools\paper-search-mcp
.venv\Scripts\paper-search.exe sources
```

## 5. 新建课程并单独建仓库

根仓库默认不跟踪课程；`transformer-self-attention` 是当前源码例外。其它新课程仍在自己的目录里初始化：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-example -Mode technical
cd D:\CourseStudio\courses\course-example

git init -b main
git add .
git status --short          # 确认没有 PDF/MP4/.venv
git commit -m "course(course-example): scaffold"
git remote add origin git@github.com:weixc0856-cell/course-example.git
git push -u origin main
```

课程仓库的忽略规则来自 `tools/course.gitignore`，默认不提交：

- `01_research/downloads/`、`fulltext/`
- `03_slides/public/*.mp4`
- `04_manim_src/media/`
- `03_slides/dist/`
- `.venv*/`、`node_modules/`、`.pnpm-store/`
- `.env`、密钥

## 6. 日常更新与推送

根框架：

```bash
cd D:/CourseStudio
git status --short
git add -A
git diff --cached --stat
git commit -m "docs: update episode workflow"
git push
```

课程：

```bash
cd D:/CourseStudio/courses/course-example
git status --short
git add -A
git commit -m "course: script modules 1-2"
git push
```

规则：

- 提交前先看 `git diff --cached --stat` 和 `git status --short`。
- 不自动提交、不自动推送；人工确认后执行。
- 课程与框架分开提交；除 `courses/transformer-self-attention/` 源码外，不要从根仓库 `git add courses/`。

## 6.1 GitHub Actions

- Workflow：[.github/workflows/python-app.yml](../.github/workflows/python-app.yml)
- Runner：`ubuntu-24.04`（固定，避免 `ubuntu-latest` 迁移）
- Actions：`actions/checkout@v7`、`actions/setup-python@v7`（Node 24，避免 Node 20 弃用告警）
- 步骤：
  1. `python -m py_compile tools/check-episode.py tools/check-links.py`
  2. `python tools/check-links.py .`
  3. `python tools/test_check_episode_negative.py`（Linux 上用 fake `ffprobe`，不需要安装 ffmpeg）
- 不做：flake8 扫描 vendored `paper-search-mcp`、空 pytest、Slidev build、Manim 渲染。

本地等效检查：

```bash
python -m py_compile tools/check-episode.py tools/check-links.py
python tools/check-links.py .
python tools/test_check_episode_negative.py
```

## 7. 外部仓库与 vendoring

`tools/paper-search-mcp` 来自：

- 上游：`https://github.com/openags/paper-search-mcp`
- vendored commit：`cab1b5cc276a0cd004a0044003926a6440088049`
- 本地附加：`bin/paper-search`、`bin/paper-search.cmd`、`skill/paper-search/`、`UPSTREAM.md`

为避免根仓库把它记录成无效 gitlink，上游 `.git` 已移到：

```text
D:\CourseStudio\.uv-cache\paper-search-mcp-upstream.git
```

该目录被 `.uv-cache/` 忽略，本地仍保留历史。更新上游时：

1. 重新克隆/对比上游；
2. 应用改动到 `tools/paper-search-mcp`；
3. 保留 `bin/`、`skill/`、`UPSTREAM.md`；
4. 更新 `UPSTREAM.md` 的 commit 记录；
5. 重新 `uv sync --frozen --python 3.12` 并跑 `sources` 冒烟。

## 8. 换行符与可执行位

根 [.gitattributes](../.gitattributes) 已固定：

- `*.py`、`*.sh`、`*.md`、`*.json`、`*.yaml`、`*.toml`、`*.lock`：LF
- `*.ps1`、`*.cmd`、`*.bat`：CRLF
- 图片、PDF、音视频、ZIP：binary
- `tools/paper-search-mcp/bin/paper-search`：LF 且保留可执行位

如果克隆后出现大量换行符改动：

```bash
git config core.autocrlf false
git add --renormalize .
```

## 9. 密钥与大文件检查

提交前：

```bash
git diff --cached --name-only | grep -E '(^|/)(\.env$|\.venv|node_modules|\.pnpm-store|\.pdf$|\.mp4$|\.zip$)'
```

应无输出。

如果误提交 `.env`：

1. 立即撤销提交并更换相关 key；
2. 从索引移除：`git rm --cached .config/paper-search-mcp/.env`；
3. 确认 `.gitignore` 已覆盖；
4. 已推到远程时，按需使用 `git filter-repo` 清理历史；这会改写历史，先备份。

GitHub 单文件限制 100 MB；大视频与授权素材放仓库外或 Git LFS。

## 10. 常见问题

| 现象 | 处理 |
| --- | --- |
| `Permission denied (publickey)` | `ssh -T git@github.com`；确认 SSH key 已加到 GitHub |
| 远程为空，`git ls-remote` 无输出 | 首次 `git push -u origin main` 即可 |
| 根仓库出现课程目录 | 检查 `.gitignore` 的 `/courses/*` 与放行规则；仅 `transformer-self-attention` 源码和 `_retired/README.md` 应出现 |
| 课程被记录成 gitlink | 课程应在自己目录 `git init`，不要嵌套进根仓库 |
| `paper-search-mcp` 被记录成 gitlink | 不要恢复其 `.git`；按第 7 节 vendoring |
| 换行符大量变更 | `git config core.autocrlf false` + `git add --renormalize .` |
| 推送被拒（远程有新提交） | `git pull --rebase origin main` 后再推送；不要强推 |
| 大文件误入暂存区 | `git restore --staged <file>`，加入 `.gitignore`，再提交 |

## 11. 验证清单

- [ ] `git status -sb` 干净
- [ ] `git remote -v` 指向 `git@github.com:weixc0856-cell/CourseStudio.git`
- [ ] `git ls-remote origin refs/heads/main` 与本地 HEAD 一致
- [ ] 暂存区没有 `.env`、PDF、MP4、ZIP、`.venv`、`node_modules`、`.pnpm-store`
- [ ] 根仓库的 `courses/` 只含 `README.md`、`transformer-self-attention/` 源码与 `_retired/README.md`，不含大产物
- [ ] 课程自己的仓库单独提交、单独推送
