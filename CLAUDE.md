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

- 根仓库默认只跟踪框架；当前唯一例外是 `courses/transformer-self-attention/` 的源码（大产物仍忽略）。其余课程在 `courses/<slug>/` 内独立 `git init`；不要把 `labs/` 或其它课程提交进根仓库。
- 不全局 `pip install` / `npm install -g`，不改系统 PATH。
- 不在课程外安装依赖：Motion 依赖在课程 `04_motion_src/`；Reveal 用 `tools/reveal-runtime`；Slidev 用 `tools/slidev-runtime`；Manim 兜底用课程自己的 `.venv`。
- 不把 PDF、MP4、`.venv`、`node_modules`、`.pnpm-store`、`03_slides/.vendor/`、`05_recording/recordings/`、`.env` 提交进 Git。
- 不编造来源、公式、实验数字或渲染结果；没有运行检查不得写 `PASS`。
- 新闻与播客可跳过 Reveal/Slidev/Motion/Manim，但不能跳过来源登记与主张台账。

## 主路径（2026-10 起）

- 动画：**Motion Canvas 45–90 秒**叙事段落；用 `record.html?segment=<name>` 独立录制，不默认渲染 MP4。Manim 仅 `engine: "manim"` 兜底。
- 课件：`course` 默认 **Reveal**（`03_slides/index.html`）；`technical` / `news` / 旧课默认 **Slidev**（`slides.md`）。
- 讲稿：每个 motion 段落必须有 `[SEGMENT]` 与 `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]`；`segments.json` 是引擎/时长/顺序的事实来源。
- 录制：`05_recording/` 是录制就绪包；OBS 实拍由人工完成，状态保持 `NOT_RUN`。
- 检查：`--stage script/motion/recording/slides/qa`；Reveal strict 不跑 Slidev build；回归 32 项。

## 关键路径

- 最短开集路径：[guides/quickstart-episode.md](guides/quickstart-episode.md)
- 编排状态机：[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)
- 执行契约：[workflows/episode-pipeline.md](workflows/episode-pipeline.md)
- 分场景教程：[guides/episode-tutorial.md](guides/episode-tutorial.md)
- 硬性要求与清理：[guides/requirements.md](guides/requirements.md)
- 远程与仓库：[guides/repository-and-remote.md](guides/repository-and-remote.md)
- 产物根目录与模式：[courses/README.md](courses/README.md)
- 工具清单：[tools/README.md](tools/README.md)
- Motion 模板：[tools/motion-runtime](tools/motion-runtime)
- Reveal 运行时：[tools/reveal-runtime](tools/reveal-runtime)
- 录制包生成：[tools/build-recording-package.py](tools/build-recording-package.py)
- 动画技能契约：[tools/skills/motion-isolation/SKILL.md](tools/skills/motion-isolation/SKILL.md)
