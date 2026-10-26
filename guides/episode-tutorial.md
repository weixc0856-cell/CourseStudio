# Episode 使用教程（课程 / 新闻 / 播客）

本教程是 [episode-pipeline.md](../workflows/episode-pipeline.md) 的操作版。所有产物放在 `D:\CourseStudio\courses\<slug>\`；所有环境在项目内构建，不装全局 Python/npm 包。

## 0. 先决条件

| 组件 | 状态 | 位置 |
| --- | --- | --- |
| Slidev 运行时 | 已安装（项目内） | `tools/slidev-runtime/` |
| Manim | 每集安装到自己的 `.venv` | `new-episode.ps1` 自动执行 |
| `manim-isolation` Skill | 已注册 | `tools/skills/manim-isolation` → 全局 junction |
| `paper-search` | 已安装（CLI + Skill） | `tools/paper-search-mcp/bin/paper-search` |
| OBS | 需人工确认安装 | 非 Skill；未在常规路径检测到 |

先确认：

```powershell
Test-Path D:\CourseStudio\tools\slidev-runtime\node_modules\@slidev\cli
uv --version
```

> 不要用 `slidev --version` 做检查（可能启动 CLI）。Slidev 是否可用，以 `node_modules/@slidev/cli` 存在 + 一次 `slidev-run.ps1 -Mode build` 为准。Manim 版本用课程 `.venv` 的 `uv run manim --version`。

## 0.1 一条主指令（推荐）

不要每次复制五段长 Prompt。把 [workflows/claude-orchestrator.md](../workflows/claude-orchestrator.md) 作为主规则，每次只发一句：

> 请严格按照 `workflows/claude-orchestrator.md` 的规则，推进 `courses/<slug>` 的管线。当前模式：`course|technical|news|podcast`。先读 `handoff.md` 判断状态，只执行下一个子步骤；写完后运行对应的 `--stage` 检查，更新 `handoff.md` 并停下等我确认。

它每次只做一个子步骤：写文件 → 跑 `check-episode.py --stage ...` → 修到无 `Issues` → 更新 `handoff.md` → 停止。**不要一次要求它生成 `00`–`06`、整份讲稿、整份页面和所有动画。**

## 1. 选模式

| 模式 | 用途 | 必需 | 可跳过 |
| --- | --- | --- | --- |
| `course` | 系统课程 | `01_research` 00–06、`02_scripts`、`03_slides` | `04_manim_src` |
| `technical` | 论文/技术精读 | 同上 + 公式检查 | `04_manim_src` |
| `news` | 新闻/行业视频 | `01_research` 来源/台账、`02_scripts` | Manim |
| `podcast` | 纯音频播客 | `01_research` 来源/台账、`02_scripts` | Slidev、Manim |

模式决定 `check-episode.py --mode` 的检查项；新闻/播客不要求课件，但不能跳过来源与主张台账。

## 2. 建集

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-attention -Mode course
```

生成：

```text
courses/course-attention/
├── 00_raw_materials/
├── 01_research/
├── 02_scripts/lecture_script.md
├── 03_slides/slides.md
├── 03_slides/public/
├── 04_manim_src/scenes/
├── qa/recording-checklist.md
├── handoff.md
├── README.md
└── .gitignore
```

脚本会把 Python 固定到 3.12，并在课程 `.venv` 安装 Manim；不会 `git init`。

**G0 检查**：

```powershell
cd D:\CourseStudio\courses\course-attention
uv run manim --version
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode build
```

## 3. 阶段一：研究输入（分四轮）

不要一次生成 `00`–`06`。按 R1→R4 分轮，每轮只写该轮产物。

### R1 来源登记

> 只做 R1：在 `01_research/` 生成 `01-source-inventory.md` 与 `search-results/`。用 `paper-search` 检索原始论文与代表性后续研究，记录检索式、来源、标识符、访问状态。不要写台账、讲稿或页面。

```bash
P=/d/CourseStudio/tools/paper-search-mcp/bin/paper-search
$P search "<query>" -s fast -n 5 --source-timeout 30 > 01_research/search-results/q01.json
$P download arxiv 1706.03762 -o 01_research/downloads
```

### R2 主张台账

> 只做 R2：基于 R1 的来源，生成 `01_research/02-claim-evidence-ledger.csv`。每条关键主张有 `CLM-XXX`、页码/公式定位；区分 `FACT` / `CLAIM` / `INFERENCE` / `ASSUMPTION`；冲突保留双方证据。不要写讲稿。

### R3 知识结构

> 只做 R3：生成 `01_research/03-knowledge-structure.md`。记录公式、符号、量纲、适用条件、冲突与未决项。符号必须与 R2 台账一致；不要写讲稿。

### R4 冻结大纲

> 只做 R4：基于 R1–R3 生成 `01_research/00-task-brief.md`、`04-course-input-brief.md`、`05-quality-report.md`、`06-course-outline.md`。`06` 必须给出模块划分与递进逻辑；`05` 写明 `NOT_RUN` / `PARTIAL`。不要写讲稿或页面。

**G1 检查**：

```powershell
python D:\CourseStudio\tools\check-episode.py course-attention --mode technical --stage research
```

- `04-course-input-brief.md` 能直接支持讲稿；
- `06-course-outline.md` 有模块顺序；
- `05-quality-report.md` 写明未决项。

完成后更新 `handoff.md`（阶段 `research`，子步骤 `R4`，模块进度 `0/N`），建议 `/clear`（C1）。

## 4. 阶段二：讲稿（按模块分轮）

新会话调用 `course-studio`。必须覆盖它默认的 HTML 倾向。**每次只写 1–2 个模块，追加到同一文件，不要重写全文，也不要提前写后续模块。**

### S1 模块 1–2

> 本课程采用 Episode + Slidev 布局。只写 `02_scripts/lecture_script.md`；不要生成 HTML 课件。本次仅撰写 `06-course-outline.md` 的第 1–2 模块，追加写入，不重写已有内容。必须使用纯文本独立成行的 `[SLIDE: NN]` 和 `[ANIMATION: snake_case_name]`。禁止包在代码块（三反引号）、引用块（`>`）或 HTML 注释（`<!-- -->`）中。引用 `01_research/04-course-input-brief.md` 与 `03-knowledge-structure.md`。

### S2 模块 3–4

> 继续写第 3–4 模块，追加到 `02_scripts/lecture_script.md`；不要重写第 1–2 模块，不要提前写第 5 模块之后。锚点规则同上。

### S3 模块 5–6

> 继续写第 5–6 模块，追加；不要重写已有内容。锚点规则同上。

锚点示例：

```text
[SLIDE: 05]

（口播）

[ANIMATION: navier_stokes]

（口播：说明动画中发生了什么）
```

**每批后检查**：

```powershell
python D:\CourseStudio\tools\check-episode.py course-attention --mode technical --stage script
```

- 中间阶段允许 `PARTIAL`（尚无 MP4），但 `Issues` 必须为空；
- 重点看锚点是否纯净、`[SLIDE]` 是否连续、页数是否匹配。

全部模块完成后更新 `handoff.md`（阶段 `script`，模块进度 `N/N`），建议 `/clear`（C2）。

## 5. 阶段三：Slidev 排版（先骨架，后填充）

新会话调用 `slidev`。只做排版，不写动画。**先 P1 骨架，再 P2 逐模块填充。**

### P1 骨架

> 只修改 `03_slides/slides.md`。读取 `02_scripts/lecture_script.md` 的所有 `[SLIDE: NN]`，先生成仅包含标题、分页和必要 frontmatter 的骨架；不要填充正文，不要写动画代码，不要改讲稿。

检查页数：

```powershell
python D:\CourseStudio\tools\check-episode.py course-attention --mode technical --stage slides
```

### P2 填充

> 按模块逐步填充 `03_slides/slides.md`；本次只填第 1–2 模块，保持已有骨架页序不变。动画只写 `<video src="/name.mp4" controls class="w-full" />` 占位；不要生成 Manim 代码，不要改讲稿。每页一个主要教学目标，16:9，代码/公式可读。

每 1–2 个模块后检查一次；全部填充后构建：

```powershell
# 开发服务器
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode dev -Port 3030

# 构建
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode build
```

**G3 检查**：`03_slides/dist/index.html` 存在；浏览器逐页检查无溢出；`public/` 资源可访问；页数与 `[SLIDE]` 匹配。

完成后更新 `handoff.md`（阶段 `slides`），建议 `/clear`（C4）。

## 6. 阶段四：Manim 隔离舱（少而精）

新会话调用 `manim-isolation`。**不要给每个公式都做动画**；只挑 1–2 个核心锚点。一次只做一个，完成后检查，再做下一个。

**建议 prompt**：

> 为 `[ANIMATION: navier_stokes]` 生成 `04_manim_src/scenes/navier_stokes.py`。这是本课程的第 1/2 个动画。只读 `01_research/03-knowledge-structure.md` 的符号；只写这一个场景。
>
> 隔离约束：
> 1. Manim Community v0.22.0（`from manim import *`），禁用 `manimlib`。
> 2. 禁用 `ThreeDScene`、`ThreeDCamera`、`Camera3D`、`ThreeDAxes`、`ParametricSurface` 与粒子系统；只做基础 2D 几何与文本。
> 3. 单场景不超过 20 秒。
> 4. 不引入外部字体、图片、网络资源。
>
> 用项目本地 `.venv` 渲染；输出到 `03_slides/public/navier_stokes.mp4`。不要改讲稿或 Slidev。

渲染：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 `
  -Episode course-attention -Name navier_stokes -SceneClass NavierStokes -Quality l -TimeoutSeconds 180
```

- 迭代用 `-Quality l`；定稿用 `-Quality h`。
- 超过 180 秒会杀掉整棵进程树；不要靠延长超时硬跑。
- 成功后输出 `OUTPUT=...`、`BYTES=...`、`STATUS=PASS_VERIFIED`。

**每个锚点完成后检查**：

```powershell
python D:\CourseStudio\tools\check-episode.py course-attention --mode technical --stage manim
```

检查：场景文件存在、MP4 非空、无禁用 API、声明时长 ≤20 秒。再抽帧看开头/中间/结尾。通过后再做下一个锚点；上下文明显变长时 `/clear`（C5）。

## 7. 阶段五：QA 与交接

```powershell
python D:\CourseStudio\tools\check-episode.py course-attention --mode technical --stage qa --strict
python D:\CourseStudio\tools\check-links.py courses\course-attention
```

检查项：

- 锚点是否被代码块/引用/注释包裹；
- Slidev 页数与锚点是否匹配；
- 每个动画的 `.py` 与 `.mp4`；
- Manim 禁用 API 与 20 秒上限；
- 研究包完整性；
- `handoff.md` 是否存在。

若 `Issues` 非空：只修相关文件并重跑；同一问题连续 3 次修不好就停下报告，不要放宽检查或删证据。`Warnings` 逐条写入 `handoff.md`。再把浏览器检查、抽帧结果写入 `qa/`。**G5**：`Issues` 为空；状态区分 `PASS_VERIFIED` / `PASS_STATIC` / `PARTIAL` / `NOT_RUN` / `FAIL`。

## 8. 阶段六：OBS 录制（高容错）

1. `slidev-run.ps1 -Mode dev` 启动；
2. 浏览器全屏，确认 16:9；
3. OBS：课件全屏 + 麦克风；
4. **允许口误，不强求掐点**：出错停顿 2 秒重念，后期一刀切；
5. 连续录制，用 2 秒静音/拍手作为切点；
6. 录制后抽帧核对，填写 `qa/recording-checklist.md`。

OBS 不归 AI 调用；未安装/未运行时标 `NOT_RUN`。

## 9. 新闻视频模式

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name news-example -Mode news
```

与课程相同，但更短：

- 研究：`01_research/source-register.md` + `claims-ledger.md`（或 00–06 的轻量版）；
- 讲稿：`02_scripts/lecture_script.md`，3–8 个 `[SLIDE]`；
- 默认不做 Manim；
- 检查：

```powershell
python D:\CourseStudio\tools\check-episode.py news-example --mode news --stage qa --strict
```

新闻仍要区分“事件事实 / 来源主张 / 推断”，不把标题当证据。

## 10. 播客模式

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name podcast-example -Mode podcast
```

纯音频，不需要 Slidev/Manim：

- 研究：来源登记 + 主张台账 + 提纲；
- 讲稿：`02_scripts/lecture_script.md`，可不含视觉锚点；
- 录制：OBS 音频轨或独立录音；
- 检查：

```powershell
python D:\CourseStudio\tools\check-episode.py podcast-example --mode podcast --stage qa --strict
```

播客讲稿仍然要标注来源、日期、适用范围与未核实项。

## 11. `/clear` 交接与停点

只在检查点清上下文，不要每步都清：

| 停点 | 时机 | 建议 |
| --- | --- | --- |
| C1 | 研究大纲冻结（R4） | `/clear` |
| C2 | 讲稿全部模块完成 | `/clear` |
| C3 | Slidev 骨架完成 | 可选 |
| C4 | Slidev 填充完成 | `/clear` |
| C5 | 每个/每两个 Manim 锚点 | 上下文变长时 `/clear` |
| C6 | 最终 QA 前 | `/clear` |
| C7 | 录制前 | `/clear` |

每次 `/clear` 前更新 `handoff.md`：

```markdown
| 字段 | 内容 |
| --- | --- |
| 模式 | course / technical / news / podcast |
| 阶段 | research / script / slides / manim / qa / recording |
| 子步骤 | R1 / S1 / P1 / M1 / Q1 … |
| 模块进度 | 例如 2/6 |
| 动画进度 | 例如 1/2 |
| 输入文件 | |
| 输出文件 | |
| 已运行命令 | |
| 最后检查 | 命令 + 状态 |
| 验证状态 | PASS_VERIFIED / PASS_STATIC / PARTIAL / NOT_RUN / FAIL |
| 未决事项 | |
| 下一步 | |
```

下一阶段只读 `handoff.md` + 指定输入，不重读整个项目。完整状态机见 [workflows/claude-orchestrator.md](../workflows/claude-orchestrator.md)。

## 12. 故障排查

| 现象 | 处理 |
| --- | --- |
| `check-episode.py` 报锚点被包裹 | 把 `[SLIDE]`/`[ANIMATION]` 改成纯文本独立成行 |
| 动画被报禁用 API | 去掉 `ThreeDScene`/`Camera3D`/粒子等，改 2D |
| 场景声明超过 20 秒 | 拆分锚点或减少 `run_time`/`wait` |
| 渲染超 180 秒 | 脚本已杀进程树；简化场景，不要延长超时硬跑 |
| Slidev 报 `markdown-it` 导出错误 | 确认 `tools/slidev-runtime` 锁定 `markdown-it@14.1.0` |
| `slidev` 不在 PATH | 用 `slidev-run.ps1`，不要全局安装 |
| 课程 `.venv` Python 版本不对 | `uv python pin 3.12`，删除 `.venv` 后 `uv sync` |
| OBS 找不到 | 人工安装/确认；录制阶段 `NOT_RUN` |

## 13. 一页速查

```powershell
# 建集
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name <slug> -Mode <mode>

# Slidev 开发/构建
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode <slug> -Mode dev -Port 3030
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode <slug> -Mode build

# 渲染单个动画
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode <slug> -Name <name> -SceneClass <Class> -Quality l -TimeoutSeconds 180

# 检查（按阶段）
python D:\CourseStudio\tools\check-episode.py <slug> --mode <course|technical|news|podcast> --stage <research|script|slides|manim>
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage qa --strict
```

阶段顺序固定：**研究 → 讲稿 → Slidev → Manim → QA → OBS**。每个子步骤写 `handoff.md`；只在 C1/C2/C4/C5/C6/C7 检查点 `/clear`，不是每步都清。
