# Tools — CourseStudio

所有工具与运行时都放在本目录或课程目录内；不安装全局 Python/npm 包，不改系统 PATH。

## 1. 默认 Episode 流程

| 工具 | 用途 | 环境 |
| --- | --- | --- |
| `new-episode.ps1` | 按模式创建 Episode；course/technical 在课程 `.venv` 安装 Manim，news/podcast 跳过 | 课程自己的 `.venv` |
| `episode-template/` | Episode 目录与文件模板（含锚点讲稿、Slidev、handoff） | 纯文本 |
| `slidev-runtime/` | 共享 Slidev 运行时（`@slidev/cli` + 默认主题） | 本目录 `node_modules` |
| `slidev-run.ps1` | 用共享运行时启动/构建某集 Slidev | 不写课程 `node_modules` |
| `render-manim.ps1` | 用课程 `.venv` 渲染单个场景并复制 MP4 到 `03_slides/public/`；默认 180s 超时，超时杀进程树 | 课程 `.venv` |
| `check-episode.py` | 检查锚点防逃逸、严格 1..N 编号、页数、场景、MP4、Manim API、ffprobe 真实时长、非空研究包；终检实际 build Slidev；支持 `--mode` 与 `--stage` | 系统 Python / 任意 Python 3 |
| `skills/manim-isolation/` | 独立 Manim 隔离 Skill 实体（全局 junction） | 只写 `04_manim_src/scenes` |

## 2. 常用命令

```powershell
# 新建一集
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-attention -Mode course

# 开发服务器
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode dev -Port 3030

# 构建静态页面
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode build

# 渲染一个动画锚点
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode course-attention -Name navier_stokes -SceneClass NavierStokes -Quality l -TimeoutSeconds 180

# 检查交接
python D:\CourseStudio\tools\check-episode.py course-attention --mode course --stage qa --strict
```

## 3. 兼容/维护工具

| 工具 | 用途 |
| --- | --- |
| `new-course.ps1` | 旧版 CourseStudio HTML 布局脚手架（保留兼容） |
| `course.gitignore` | 课程仓库忽略模板；`new-course.ps1` / `new-episode.ps1` 使用 |
| `check-links.py` | 检查 Markdown 相对链接 |
| `paper-search-mcp/` | 论文检索 CLI + Skill 实体（本地 `.venv`，全局 junction） |

## 4. 环境边界

- `slidev-runtime/node_modules`、`slidev-runtime/.pnpm-store`、课程 `.venv`、`04_manim_src/media`、`03_slides/public/*.mp4` 都不进 Git。
- 需要重建 Slidev：在 `slidev-runtime/` 运行 `pnpm install`；不要把 `node_modules` 复制进课程。
- 需要重建课程环境：在课程目录运行 `uv sync` / `uv add manim`；不要全局 `pip install`。
- 任何新工具先放本目录，确认隔离后再接入 `workflows/episode-pipeline.md`。
- 硬性验收、清理与 Git 规则见 [guides/requirements.md](../guides/requirements.md)。
