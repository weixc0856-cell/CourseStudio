# Tools — CourseStudio

所有工具与运行时都放在本目录或课程目录内；不安装全局 Python/npm 包，不改系统 PATH。最短开集路径见 [guides/quickstart-episode.md](../guides/quickstart-episode.md)。

## 1. 默认 Episode 流程

| 工具 | 用途 | 环境 |
| --- | --- | --- |
| `new-episode.ps1` | 按模式创建 Episode；course 默认 Reveal（`03_slides/index.html`），technical/news 保留 Slidev（`slides.md`），podcast 不要求课件；默认复制 `04_motion_src` 与 `05_recording`，不安装 Manim；`-WithManim` 才安装 Manim | 课程自己的 `.venv`（仅 `-WithManim`） |
| `episode-template/` | Episode 目录与文件模板（含锚点讲稿、Reveal/Slidev 课件、`05_recording`、handoff） | 纯文本 |
| `motion-runtime/` | Motion Canvas 运行时模板（MC 3.17.2 + Vite 5.4.21，精确版本）；复制到课程 `04_motion_src`，每集独立安装 | 课程自己的 `node_modules` |
| `motion-run.ps1` | 按段落启动 Motion Canvas 录制页；缺 `04_motion_src` 时从模板复制，缺依赖时在课程目录内 `pnpm install --frozen-lockfile`；打印 `record.html?segment=<name>` | 课程 `04_motion_src` |
| `script_timing.py` | checker 与生成器共享的节奏标注解析/校验模块（`[SEGMENT]` / `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]`） | 纯 Python |
| `build-recording-package.py` | 从讲稿 + `segments.json` 生成/刷新 `05_recording/` 的 manifest、cues、checklist；严格校验、幂等、缺源报错 | 系统 Python |
| `slidev-runtime/` | 共享 Slidev 运行时（`@slidev/cli` + 默认主题） | 本目录 `node_modules` |
| `slidev-run.ps1` | 用共享运行时启动/构建某集 Slidev | 不写课程 `node_modules` |
| `reveal-runtime/` | 共享 Reveal.js 6.0.2 运行时（`pnpm install`，不构建、不全局） | 本目录 `node_modules` |
| `reveal-run.ps1` | 同步 reveal dist 到 `03_slides/.vendor/reveal/`（gitignore），用 `python -m http.server` 服务 `03_slides` 并打印 URL | 系统 Python，不引入 Node 服务器 |
| `render-manim.ps1` | 用课程 `.venv` 渲染单个场景并复制 MP4 到 `03_slides/public/`；默认 180s 超时，超时杀进程树 | 课程 `.venv` |
| `check-episode.py` | 检查锚点、页数映射、研究包；按 `segments.json` 分派 motion/manim，校验 45–90 秒、scene/project/cue、节奏标注、录制包结构；Reveal 检查 data-slide 1..N 与本地资源，strict 跳过 Slidev build；Slidev 仍实际 build | 系统 Python / 任意 Python 3 |
| `test_check_episode_negative.py` | 32 项回归：旧 Manim + motion 时长/引擎/cue/顺序 + 节奏标注 + recording 包 + 生成器幂等/失败不写包 + Reveal data-slide/资源/strict 跳过 build | 系统 Python / 任意 Python 3 |
| `skills/motion-isolation/` | 默认动画 Skill 实体：3B1B 风格、45–90 秒、`[ANIMATION]`/`[SEGMENT]`/`record.html` | 只写 `04_motion_src` 的 scenes/projects |
| `skills/manim-isolation/` | **Legacy/fallback** Manim 隔离 Skill；仅 `engine=manim` | 只写 `04_manim_src/scenes` |

## 2. 常用命令

```powershell
# 新建一集
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-example -Mode course

# Motion Canvas 录制页（主路径）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 -Episode course-example -Segment attention_scores

# Reveal 课件（course 默认；同步 .vendor 并启动静态服务）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 -Episode course-example -Port 3040

# Slidev 课件（technical/news/旧课）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-example -Mode dev -Port 3030

# 构建静态页面
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-example -Mode build

# 渲染一个 Manim 兜底锚点（仅 engine=manim）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode course-example -Name navier_stokes -SceneClass NavierStokes -Quality l -TimeoutSeconds 180

# Motion Canvas 段落检查
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage motion

# 录制就绪包结构检查
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage recording

# 生成/刷新录制就绪包
python D:\CourseStudio\tools\build-recording-package.py course-example

# 检查交接
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage qa --strict

# 检查器回归（旧 Manim + motion + recording）
python D:\CourseStudio\tools\test_check_episode_negative.py
```

## 3. 兼容/维护工具

| 工具 | 用途 |
| --- | --- |
| `new-course.ps1` | 旧版 CourseStudio HTML 布局脚手架（legacy；新项目用 `new-episode.ps1`） |
| `course.gitignore` | 课程仓库忽略模板；`new-course.ps1` / `new-episode.ps1` 使用 |
| `check-links.py` | 检查 Markdown 相对链接 |
| `paper-search-mcp/` | 论文检索 CLI + Skill 实体（本地 `.venv`，全局 junction） |

## 4. 环境边界

- `slidev-runtime/node_modules`、`slidev-runtime/.pnpm-store`、课程 `.venv`、`04_manim_src/media`、`03_slides/public/*.mp4` 都不进 Git。
- Reveal：`tools/reveal-runtime/node_modules` 与课程的 `03_slides/.vendor/` 都不进 Git；`reveal-run.ps1` 只做 dist 同步 + Python 静态服务，不引入额外 Node 服务器。
- 动画段落仍由 `04_motion_src/record.html?segment=<name>` 独立录屏；课件只放占位，不嵌 MP4。
- Motion Canvas 依赖在 `courses/<slug>/04_motion_src/node_modules`；录制文件在 `05_recording/recordings/`，都不进 Git。
- OBS 由人工安装和操作，参考路径 `D:\Program Files\obs-studio\bin\64bit\obs64.exe`；本仓库不安装、不调用、不自动化 OBS，相关检查标 `NOT_RUN`。
- 需要重建 Slidev：在 `slidev-runtime/` 运行 `pnpm install`；不要把 `node_modules` 复制进课程。
- 需要重建课程环境：在课程目录运行 `uv sync` / `uv add manim`；不要全局 `pip install`。
- 任何新工具先放本目录，确认隔离后再接入 `workflows/episode-pipeline.md`。
- 硬性验收、清理与 Git 规则见 [guides/requirements.md](../guides/requirements.md)。
