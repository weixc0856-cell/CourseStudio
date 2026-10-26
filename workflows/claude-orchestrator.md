# Claude Code 课程管线编排规则（Agentic FSM）

当用户要求“推进某集课程/新闻/播客管线”时，按本文件执行。你不是一次性生成器，而是**有限状态机**：每次只推进一个 Stage 的一个子步骤，写文件、跑检查、更新 `handoff.md`、停下等人工确认。

## 1. 启动时只读这些

1. `courses/<slug>/handoff.md`
2. [episode-pipeline.md](episode-pipeline.md)
3. 当前 Stage 明确列出的输入文件

不要一次读整个项目，不要预读后续 Stage 的文件。`01_research/02-claim-evidence-ledger.csv` 只在需要核验具体主张时按 `CLM`/关键词检索，不整表加载。

## 2. 状态判断

| `handoff.md` 的当前阶段 | 下一动作 |
| --- | --- |
| `NOT_RUN` / `research` | 从 R1 开始；若已有部分研究，接着下一个 R 子步骤 |
| `script` | 从大纲的下一个模块开始（S1/S2/S3） |
| `slides` | 若 `slides.md` 无骨架，先 P1；否则 P2 |
| `manim` | 处理下一个未完成的 `[ANIMATION]` |
| `qa` | 运行终检，修复后停止 |
| `recording` | 提示人工录制，不自动推进 |

如果 `handoff.md` 缺失或状态矛盾，先报告并停止；不要猜。

## 3. 每次只做一个子步骤

| Stage | 子步骤 | 输入 | 输出 | 检查 |
| --- | --- | --- | --- | --- |
| research | R1 来源登记 + 检索记录 | 用户素材/检索 | `01_research/01-source-inventory.md`、`search-results/` | 无需脚本 |
| research | R2 主张台账 | R1 | `01_research/02-claim-evidence-ledger.csv` | 无需脚本 |
| research | R3 知识结构/公式 | R2 | `01_research/03-knowledge-structure.md` | 无需脚本 |
| research | R4 大纲冻结 | R1–R3 | `01_research/04`、`05`、`06` | `--stage research` |
| script | S1 模块 1–2 | `01_research/04`、`03`、`06` | `02_scripts/lecture_script.md`（第 1–2 模块） | `--stage script` |
| script | S2 模块 3–4 | 同上 | 追加第 3–4 模块 | `--stage script` |
| script | S3 模块 5–6 | 同上 | 追加第 5–6 模块 | `--stage script` |
| slides | P1 骨架 | 讲稿 | `03_slides/slides.md`（仅标题/分页） | `--stage slides` |
| slides | P2 填充 | 讲稿 + 骨架 | 逐模块填充页面 | `--stage slides` |
| manim | M1 选锚点 | 讲稿 | 选 1–2 个核心 `[ANIMATION]` | 无 |
| manim | M2 单锚点 | `03-knowledge-structure` + 锚点上下文 | `04_manim_src/scenes/<name>.py` | `--stage manim` |
| qa | Q1 终检 | 全包 | 修复后的文件 | `--stage qa --strict`（course/technical 会真实 build Slidev） |
| qa | Q2 视觉/浏览器 | 构建页面 | `qa/` 记录 | 人工 + 工具 |
| recording | R 录制 | 讲稿 + 页面 | 录像/音频 | 人工 |

模块数量不固定；按 `06-course-outline.md` 的实际模块拆分。一次讲稿调用只写 **1–2 个模块**，追加写入，不要重写全文。

## 4. 每轮执行模板

1. **声明**：当前 Stage/子步骤、要读的文件、要写的文件。
2. **读取**：只读当前子步骤需要的文件。
3. **写入**：只写当前子步骤的输出；不顺手生成后续阶段。
4. **自检**：运行当前 Stage 的检查命令。
5. **修复**：若 `Issues` 非空，只修相关文件，重跑；最多 3 轮。
6. **交接**：更新 `handoff.md`；报告状态；停止。

检查命令：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <course|technical|news|podcast> --stage <research|script|slides|manim|qa>
```

- 中间阶段允许 `PARTIAL`，但 **`Issues` 必须为空**。
- 最终 QA 加 `--strict`，要求无 `Issues`；警告逐条写入 `handoff.md`。
- `course`/`technical` 的终检会实际运行 `slidev-run.ps1 -Mode build`；构建非 0 即 FAIL。
- 终检还会用 `ffprobe` 校验真实 MP4 时长，并拒绝空研究文件、重复/跳号/乱序的 slide 锚点。
- 终检输出 `Mapping: M anchor(s), N slide(s), buffer ...`；`M > N` 即 FAIL。
- 检查器负向回归 `python tools/test_check_episode_negative.py` 必须 7/7 通过。
- 没有实际运行检查，不得写 `PASS`。

## 5. 自检循环的上限

- 同一 `Issue` 连续修复 3 次仍失败：停止，保留当前最佳结果，报告命令、退出码、错误摘要。
- 不通过删证据、改检查脚本、放宽 `--strict` 来“通过”。
- 不用模型记忆补来源、补公式、补实验数字。

## 6. 停点与 `/clear`

| 停点 | 时机 | 是否建议 `/clear` |
| --- | --- | --- |
| C1 | 研究大纲冻结（R4 完成） | 是 |
| C2 | 讲稿全部模块完成 | 是 |
| C3 | Slidev 骨架完成 | 可选 |
| C4 | Slidev 填充完成 | 是 |
| C5 | 每个/每两个 Manim 锚点完成 | 上下文明显变长时 |
| C6 | 最终 QA 前 | 是 |
| C7 | 录制前 | 是 |

停点必须做：

1. 更新 `handoff.md`（阶段、子步骤、模块进度、最后检查）。
2. 输出：“Stage X / 子步骤 Y 已完成，检查结果 `<status>`。请检查 `<文件>`。确认后 `/clear` 并回复‘继续’。”
3. **停止生成**，不自动进入下一 Stage。

`/clear` 只是清上下文，不是质量检查；不要在每一步都清，也不要把 `/clear` 当成验收。

## 7. 上下文加载规则

| Stage | 必读 | 不读 |
| --- | --- | --- |
| research | 用户素材、来源、`01_research` 已生成文件 | 讲稿、页面、动画 |
| script | `01_research/04`、`03`、`06`、`handoff` | 全部台账、页面、动画 |
| slides | `02_scripts/lecture_script.md`、`06`、`slides.md` 骨架 | 研究原文、动画源码 |
| manim | 该锚点前后讲稿、`03` 的符号段 | 其他锚点、整份讲稿 |
| qa | 检查器输出、失败文件、`handoff` | 全项目重读 |

## 8. 模式差异

- `course` / `technical`：完整分块流程；technical 必须核对公式/量纲。
- `news`：R1–R4 可合并为 1–2 轮；讲稿 1 轮；跳过 Slidev/Manim；仍要台账与终检。
- `podcast`：R1–R4 可合并；讲稿 1 轮；无 Slidev/Manim；终检用 `--mode podcast`。

## 9. 禁止事项

- 禁止一次调用生成 `00`–`06`、整份讲稿、整份课件和所有动画。
- 禁止跳过 `check-episode.py` 或口头声称通过。
- 禁止自动推进到下一 Stage。
- 禁止修改研究证据以让检查通过。
- 禁止全局 `pip/npm install`、改 PATH。
- 禁止把 PDF、MP4、`.venv`、`node_modules`、`.pnpm-store` 提交进 Git。

## 10. 用户唯一需要输入的指令

> 请严格按照 `workflows/claude-orchestrator.md` 的规则，推进 `courses/<slug>` 的管线。当前模式：`<course|technical|news|podcast>`。先读 `handoff.md` 判断状态，只执行下一个子步骤；写完后运行对应 `--stage` 检查，更新 `handoff.md` 并停下等我确认。
