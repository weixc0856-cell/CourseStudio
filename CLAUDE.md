# CourseStudio — Agent 工作约定

本仓库用于制作课程、新闻解读与技术/论文讲解。所有产物放在 `D:\CourseStudio\courses\<slug>\`。

## 接到课程/新闻/播客任务时

1. 先读 [workflows/claude-orchestrator.md](workflows/claude-orchestrator.md) 与 [workflows/episode-pipeline.md](workflows/episode-pipeline.md)。
2. 再读目标项目的 `handoff.md`，判断当前阶段与子步骤。
3. **每次只推进一个子步骤**；不要一次性生成 `00`–`06`、整份讲稿、整份页面和所有动画。
4. 写完立即运行 `python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage <stage>`。
5. `Issues` 必须为空；中间阶段允许 `PARTIAL`。终检用 `--stage qa --strict`。
6. 更新 `handoff.md` 后停止，等用户确认；不要自动跨阶段。
7. 只有检查点才建议 `/clear`，不是每步都清。

## 硬约束

- 根仓库只跟踪框架；课程在 `courses/<slug>/` 内独立 `git init`。不要在根仓库提交 `courses/*` 或 `labs/`。
- 不全局 `pip install` / `npm install -g`，不改系统 PATH。
- 不在课程外安装依赖；Slidev 用 `tools/slidev-runtime`，Manim 用课程自己的 `.venv`。
- 不把 PDF、MP4、`.venv`、`node_modules`、`.pnpm-store`、`.env` 提交进 Git。
- 不编造来源、公式、实验数字或渲染结果；没有运行检查不得写 `PASS`。
- 新闻与播客可跳过 Slidev/Manim，但不能跳过来源登记与主张台账。

## 关键路径

- 编排状态机：[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)
- 执行契约：[workflows/episode-pipeline.md](workflows/episode-pipeline.md)
- 分场景教程：[guides/episode-tutorial.md](guides/episode-tutorial.md)
- 远程与仓库：[guides/repository-and-remote.md](guides/repository-and-remote.md)
- 产物根目录与模式：[courses/README.md](courses/README.md)
- 工具清单：[tools/README.md](tools/README.md)
