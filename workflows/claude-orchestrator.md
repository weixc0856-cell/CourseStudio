# Claude Code 课程管线编排规则（Agentic FSM）

当用户要求“推进某集课程/新闻/播客管线”时，按本文件执行。你不是一次性生成器，而是**有限状态机**：每次只推进一个 Stage 的一个子步骤，写文件、跑检查、更新 `handoff.md`、停下等人工确认。

## 1. 启动时只读这些

1. `courses/<slug>/handoff.md`
2. [episode-pipeline.md](episode-pipeline.md)
3. 当前 Stage 明确列出的输入文件

不要一次读整个项目，不要预读后续 Stage。`01_research/02-claim-evidence-ledger.csv` 只在需要核验具体主张时按 `CLM`/关键词检索，不整表加载。

## 2. 状态判断

| `handoff.md` 的当前阶段 | 下一动作 |
| --- | --- |
| `NOT_RUN` / `research` | 从 R1 开始；若已有部分研究，接着下一个 R 子步骤 |
| `script` | 从大纲的下一个模块开始（S1/S2/S3），同步补 `[SEGMENT]` 节奏标注 |
| `motion` | 先确认 `segments.json`；处理下一个未完成的 Motion 段落（M1/M2/M3） |
| `recording` | 运行生成器，生成/刷新 `05_recording/`（RC1）；不启动 OBS |
| `slides` | 课程 Reveal：P1 骨架 → P2 填充；technical/旧课：Slidev P1 → P2 |
| `qa` | 运行终检，修复后停止 |
| `record` | 提示人工 OBS 录制，不自动推进 |
| `manim` | **仅 legacy/兜底**；处理 `engine=manim` 的锚点 |

如果 `handoff.md` 缺失或状态矛盾，先报告并停止；不要猜。

## 3. 每次只做一个子步骤

| Stage | 子步骤 | 输入 | 输出 | 检查 |
| --- | --- | --- | --- | --- |
| research | R1 来源登记 + 检索记录 | 用户素材/检索 | `01_research/01-source-inventory.md`、`search-results/` | 无需脚本 |
| research | R2 主张台账 | R1 | `01_research/02-claim-evidence-ledger.csv` | 无需脚本 |
| research | R3 知识结构/公式 | R2 | `01_research/03-knowledge-structure.md` | 无需脚本 |
| research | R4 大纲冻结 | R1–R3 | `01_research/04`、`05`、`06` | `--stage research` |
| script | S1 模块 1–2 + 节奏标注 | `01_research/04`、`03`、`06` | `02_scripts/lecture_script.md`（第 1–2 模块） | `--stage script` |
| script | S2 模块 3–4 + 节奏标注 | 同上 | 追加第 3–4 模块 | `--stage script` |
| script | S3 模块 5–6 + 节奏标注 | 同上 | 追加第 5–6 模块 | `--stage script` |
| motion | M1 冻结段落清单 | 讲稿 `[ANIMATION]`/`[SEGMENT]` | `04_motion_src/segments.json` | `--stage script` |
| motion | M2 单段 scene + project（`motion-isolation`） | `03-knowledge-structure` + 锚点上下文 + `segments.json` | `src/scenes/<name>.tsx`、`src/projects/<name>.ts` | `--stage motion` |
| motion | M3 下一段 | 同上 | 下一段 scene/project | `--stage motion` |
| recording | RC1 生成/刷新录制包 | 讲稿 + `segments.json` | `05_recording/manifest.json`、`cues/`、`checklist.md` | `--stage recording` |
| slides | P1 课件骨架 | 讲稿 `[SLIDE]`、`06` | Reveal `index.html` 页序骨架 或 Slidev `slides.md` 骨架 | `--stage slides` |
| slides | P2 逐页/逐模块填充 | 讲稿 + 骨架 | 填充后的课件；动画页只放占位 | `--stage slides` |
| qa | Q1 终检 | 全包 | 修复后的文件 | `--stage qa --strict` |
| qa | Q2 视觉/浏览器 | 构建/静态页面 | `qa/` 记录 | 人工 + 工具 |
| record | REC 人工录制 | `05_recording/checklist.md` + 课件 + `record.html` | 录像/音频 | 人工；`NOT_RUN` |
| manim | ML1 选兜底锚点（仅 legacy） | `segments.json` 中 `engine=manim` | 选一个锚点 | 无 |
| manim | ML2 单锚点渲染 | `03-knowledge-structure` + 锚点 | `04_manim_src/scenes/<name>.py` + MP4 | `--stage manim` |

模块数量不固定；按 `06-course-outline.md` 的实际模块拆分。一次讲稿调用只写 **1–2 个模块**，追加写入，不要重写全文。Motion 一次只做一个段落；Reveal/Slidev 先骨架后填充。

## 4. 每轮执行模板

1. **声明**：当前 Stage/子步骤、要读的文件、要写的文件。
2. **读取**：只读当前子步骤需要的文件。
3. **写入**：只写当前子步骤的输出；不顺手生成后续阶段。
4. **自检**：运行当前 Stage 的检查命令。
5. **修复**：若 `Issues` 非空，只修相关文件，重跑；最多 3 轮。
6. **交接**：更新 `handoff.md`；报告状态；停止。

检查命令：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <course|technical|news|podcast> --stage <research|script|motion|recording|slides|manim|qa>
```

- 中间阶段允许 `PARTIAL`，但 **`Issues` 必须为空**。
- 最终 QA 加 `--strict`，要求无 `Issues`；警告逐条写入 `handoff.md`。
- Motion 段落：45–90 秒；`[SEGMENT]` + `HOLD`/`EMPHASIS`/`CUT` 在 script/motion 阶段硬校验。
- `recording` 阶段检查 `05_recording/` 结构；不要求实拍文件存在。
- course Reveal：`data-slide` 1..N + 本地资源；`--strict` 不跑 Slidev build。
- technical/旧课 Slidev：终检实际运行 `slidev-run.ps1 -Mode build`；非 0 即 FAIL。
- Manim 兜底：`--stage manim`；单场景 ≤20 秒；真实 MP4 用 `ffprobe`。
- 回归 `python tools/test_check_episode_negative.py` 必须 **32/32** 通过。
- 没有实际运行检查，不得写 `PASS`。

## 5. 自检循环的上限

- 同一 `Issue` 连续修复 3 次仍失败：停止，保留当前最佳结果，报告命令、退出码、错误摘要。
- 不通过删证据、改检查脚本、放宽 `--strict` 来“通过”。
- 不用模型记忆补来源、补公式、补实验数字。

## 6. 停点与 `/clear`

| 停点 | 时机 | 是否建议 `/clear` |
| --- | --- | --- |
| C1 | 研究大纲冻结（R4 完成） | 是 |
| C2 | 讲稿全部模块完成（含节奏标注） | 是 |
| C3 | 每个/每两个 Motion 段落完成 | 上下文明显变长时 |
| C4 | 录制就绪包生成并检查完成 | 是 |
| C5 | Reveal / Slidev 课件完成 | 是 |
| C6 | 最终 QA 前 | 是 |
| C7 | 人工录制前 | 是 |

停点必须做：

1. 更新 `handoff.md`（阶段、子步骤、模块/段落进度、最后检查）。
2. 输出：“Stage X / 子步骤 Y 已完成，检查结果 `<status>`。请检查 `<文件>`。确认后 `/clear` 并回复‘继续’。”
3. **停止生成**，不自动进入下一 Stage。

`/clear` 只是清上下文，不是质量检查；不要每步都清，也不要把 `/clear` 当成验收。

## 7. 上下文加载规则

| Stage | 必读 | 不读 |
| --- | --- | --- |
| research | 用户素材、来源、`01_research` 已生成文件 | 讲稿、课件、动画 |
| script | `01_research/04`、`03`、`06`、`handoff` | 全部台账、课件、动画 |
| motion | 该锚点前后讲稿、`03` 符号段、`segments.json`、`theme.ts` | 其他段落、整份讲稿、课件 |
| recording | 讲稿节奏块、`segments.json`、现有 `05_recording/` | 研究原文、动画源码 |
| slides | 讲稿 `[SLIDE]`、`06`、课件骨架 | 研究原文、动画源码 |
| qa | 检查器输出、失败文件、`handoff` | 全项目重读 |
| record | `05_recording/checklist.md`、manifest、课件 | 研究原文、动画源码 |

## 8. 模式差异

- `course`：完整分块流程；Motion + **Reveal** 默认；Manim 仅兜底。
- `technical`：完整分块 + 公式/量纲核对；Motion + **Slidev** 默认；Manim 可在极强公式场景兜底。
- `news`：R1–R4 可合并为 1–2 轮；讲稿 1 轮；Motion 可选；Slidev 3–8 页可选；仍要台账与终检。
- `podcast`：R1–R4 可合并；讲稿 1 轮；无 Motion/课件；终检用 `--mode podcast`。
- 旧课：保留原 Slidev/Manim 路径，不强制迁移；新工作按本文件主路径。

## 9. 禁止事项

- 禁止一次调用生成 `00`–`06`、整份讲稿、整份课件和所有动画。
- 禁止把 Motion 段落写成 ≤20 秒插片；主路径是 45–90 秒叙事段落。
- 禁止把 Manim 当默认动画引擎；只有 `engine=manim` 才走 `manim-isolation` + `render-manim.ps1`。
- 禁止在 Reveal 课件里嵌 Motion MP4；动画页只放占位，用 `record.html` 独立录制。
- 禁止用 `?present` 作为录制页；录制页是 `record.html?segment=<name>`。
- 禁止跳过 `check-episode.py` 或口头声称通过。
- 禁止自动推进到下一 Stage。
- 禁止修改研究证据以让检查通过。
- 禁止安装、调用或自动化 OBS；相关项标 `NOT_RUN`。
- 禁止全局 `pip/npm install`、改 PATH。
- 禁止把 PDF、MP4、`.venv`、`node_modules`、`.pnpm-store`、`03_slides/.vendor/`、`05_recording/recordings/` 提交进 Git。

## 10. 用户唯一需要输入的指令

> 请严格按照 `workflows/claude-orchestrator.md` 的规则，推进 `courses/<slug>` 的管线。当前模式：`<course|technical|news|podcast>`。先读 `handoff.md` 判断状态，只执行下一个子步骤；写完后运行对应 `--stage` 检查，更新 `handoff.md` 并停下等我确认。
