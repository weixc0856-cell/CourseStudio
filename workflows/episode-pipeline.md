# Workflow — Episode Pipeline（Slidev + Manim Isolation）

适用于新课程、新闻解读、技术/论文解读的单集生产。**默认布局**：`D:\CourseStudio\courses\<slug>\`，使用 Episode 目录契约 + Slidev 排版 + Manim 隔离舱。

> 本文件是执行主线。通用课程原则仍见 [course.md](course.md)；本文件覆盖目录、工具调用、阶段 Gate 和交接契约。
> 分块状态机、每轮模板与停点规则见 [claude-orchestrator.md](claude-orchestrator.md)；分场景操作教程见 [guides/episode-tutorial.md](../guides/episode-tutorial.md)；硬性验收与清理要求见 [guides/requirements.md](../guides/requirements.md)。

## 0. 模式选择

| 模式 | 适用 | 研究深度 | Slidev | Manim | 录制 |
| --- | --- | --- | --- | --- | --- |
| `course` | 系统课程、系列课 | `01_research/00`–`06` | 必需 | 可选 | OBS 视频 |
| `technical` | 论文/技术精读 | `00`–`06` + 公式检查 | 必需 | 机制处使用 | OBS 视频 |
| `news` | 新闻/行业解读 | `source-register` + `claims-ledger` | 3–8 页，可选 | 默认不用 | OBS 视频/音频 |
| `podcast` | 纯音频播客 | `source-register` + `claims-ledger` + 提纲 | 不需要 | 不需要 | OBS 音频/视频 |

新闻与播客可以跳过 `03_slides/` 与 `04_manim_src/`，但**不能跳过**来源登记、主张台账和讲稿。`check-episode.py` 用 `--mode` 区分这些要求。

## 0.1 分块执行与停点（重要）

**文件产出 ≠ 验收通过。** 每个 Stage 必须分块执行：写一小块 → 跑检查 → 修到无 `Issues` → 更新 `handoff.md` → 停下等人工确认。

| Stage | 分块方式 | 检查命令 |
| --- | --- | --- |
| research | R1 来源 → R2 台账 → R3 知识结构 → R4 大纲冻结 | `--stage research` |
| script | 按大纲模块，1–2 模块/次，追加写入 | `--stage script` |
| slides | P1 只建骨架 → P2 逐模块填充 | `--stage slides` |
| manim | 只挑 1–2 个核心锚点，一次一个 | `--stage manim` |
| qa | 全包终检 + 浏览器/抽帧 | `--stage qa --strict` |

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage <stage>
```

- 中间阶段允许 `PARTIAL`，但 `Issues` 必须为空。
- 终检加 `--strict`，无 `Issues`；警告写进 `handoff.md`。
- 每轮结束更新 `handoff.md` 并停止；**禁止自动跨 Stage**。
- 详细状态机与每轮模板见 [claude-orchestrator.md](claude-orchestrator.md)。

### `/clear` 停点

只在以下位置清上下文，不要每步都清：

1. 研究大纲冻结后（C1）
2. 讲稿全部模块完成后（C2）
3. Slidev 填充完成后（C4）
4. 每个/每两个 Manim 锚点后，或上下文明显变长时（C5）
5. 最终 QA 前（C6）
6. 录制前（C7）

`/clear` 不会提升判断力，只是清空上下文；它不是验收，也不能替代检查脚本。

## 1. 目录契约（不可变）

```text
courses/<slug>/
├── 00_raw_materials/              # 原始论文/网页（PDF 不提交）
├── 01_research/
│   ├── 00-task-brief.md
│   ├── 01-source-inventory.md
│   ├── 02-claim-evidence-ledger.csv
│   ├── 03-knowledge-structure.md
│   ├── 04-course-input-brief.md
│   ├── 05-quality-report.md
│   ├── 06-course-outline.md
│   ├── search-results/            # 检索 JSON（提交）
│   ├── downloads/                 # PDF（不提交）
│   └── fulltext/                  # 逐页文本（不提交）
├── 02_scripts/
│   └── lecture_script.md          # 必须含视觉锚点
├── 03_slides/
│   ├── slides.md                  # Slidev
│   ├── public/                    # Manim MP4（不提交）
│   └── dist/                      # 构建产物（不提交）
├── 04_manim_src/
│   ├── scenes/<name>.py
│   └── media/                     # Manim 中间产物（不提交）
├── qa/
├── handoff.md
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
└── .gitignore
```

命名别名（外部管线常用）：

| 外部名 | 实际文件 |
| --- | --- |
| `evidence_ledger.csv` | `01_research/02-claim-evidence-ledger.csv` |
| `knowledge_structure.md` | `01_research/03-knowledge-structure.md` |
| `course-input-brief.md` | `01_research/04-course-input-brief.md` |
| `lecture_script.md` | `02_scripts/lecture_script.md` |
| `slides.md` | `03_slides/slides.md` |
| `scene.py` | `04_manim_src/scenes/<name>.py` |

## 2. 工具与真实调用名

| 用途 | 调用名 | 位置 / 说明 |
| --- | --- | --- |
| 检索/下载 | `paper-search` | `D:\CourseStudio\tools\paper-search-mcp\bin\paper-search` |
| 研究输入 | `research-to-course-synthesis` | 全局 Skill |
| 讲稿 | `course-studio` | 全局 Skill（目录名 `course-studio-skill`） |
| 排版 | `slidev` | 全局 Skill；运行时在 `tools/slidev-runtime` |
| 动画隔离 | `manim-isolation` | 全局 junction → `tools/skills/manim-isolation` |
| 润色（可选） | `humanizer` | 全局 Skill（目录名 `humanizer-main`） |
| OBS | 人工 | 非 Skill；未在常规路径检测到 |

## 3. 阶段与 Gate

### Stage 0 — 建集

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name <slug> -Mode <course|technical|news|podcast>
```

- 创建目录契约、`.gitignore`、模板与 `handoff.md`；
- `course`/`technical` 在**课程自己的** `.venv` 中安装 Manim；
- `news`/`podcast` 默认跳过 Manim；需要时在课程内 `uv add manim`；
- 不自动 `git init`、不提交、不渲染。

**Gate G0**：目录存在；`lecture_script.md` / `handoff.md` 存在；`course`/`technical` 还需 `.venv` 可 `uv run manim --version` 且 `slides.md` 存在；`news`/`podcast` 可无 Slidev/Manim。

### Stage 1 — 研究输入

工作目录：`courses/<slug>/`（研究产物写入 `01_research/`）。

使用 `paper-search`：

```bash
P=/d/CourseStudio/tools/paper-search-mcp/bin/paper-search
$P search "<query>" -s fast -n 5 --source-timeout 30 > 01_research/search-results/q01.json
$P download arxiv 1706.03762 -o 01_research/downloads
```

使用 `research-to-course-synthesis`，在 `01_research/` 中运行（或在课程根生成后移动到该目录）。**不要一次生成 `00`–`06`**；按四轮推进：

1. **R1 来源**：`01-source-inventory.md` + `search-results/`；
2. **R2 台账**：`02-claim-evidence-ledger.csv`；
3. **R3 知识结构**：`03-knowledge-structure.md`（公式、符号、量纲）；
4. **R4 冻结大纲**：`00`、`04`、`05`、`06`。

每轮只写该轮产物；下一轮开始前确认上一轮文件已存在。要求：

- 每条关键主张有 `CLM-XXX` 与页码级定位；
- 区分 `FACT` / `CLAIM` / `INFERENCE` / `ASSUMPTION`；
- 冲突保留双方证据与适用范围；
- `05-quality-report.md` 写明 `NOT_RUN` / `PARTIAL`；
- 文件必须非空：`course`/`technical` 检查 `00`–`06`；`news`/`podcast` 必须同时有非空 `source-register.md` 与 `claims-ledger.md`，且台账含 `FACT` 或 `CLAIM`。

**Gate G1**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage research
```

`04-course-input-brief.md` 与 `06-course-outline.md` 可直接用于讲稿；关键主张可定位；未决项已列出。未过 Gate 不写讲稿。完成后更新 `handoff.md`，建议 `/clear`（C1）。

### Stage 2 — 讲稿（带视觉锚点）

调用 `course-studio`，但必须在 prompt 中覆盖其默认 HTML 倾向。**按 `06-course-outline.md` 的模块分批**：每次只写 1–2 个模块，追加到 `02_scripts/lecture_script.md`，不要重写全文，也不要提前生成后续模块。

> 本课程采用 Episode + Slidev 布局。只写 `02_scripts/lecture_script.md`；不要生成 HTML 课件。本次仅撰写模块 `<X–Y>`，追加写入，不重写已有内容。必须使用 `[SLIDE: NN]` 标记翻页，使用 `[ANIMATION: name]` 标记需要 Manim 的推导。动画名用小写 snake_case，对应 `04_manim_src/scenes/name.py` 与 `03_slides/public/name.mp4`。严禁省略视觉锚点。引用 `01_research/04-course-input-brief.md` 与 `03-knowledge-structure.md`。
>
> **防逃逸**：锚点必须作为纯文本独立成行。禁止把 `[SLIDE: XX]` 或 `[ANIMATION: xxx]` 包在 Markdown 代码块（三反引号）、引用块（`>`）或 HTML 注释（`<!-- -->`）中。`check-episode.py` 会把任何被包裹的锚点判为 FAIL。

锚点契约：

```text
[SLIDE: 05]
[ANIMATION: navier_stokes]
```

- `[SLIDE: NN]` 必须与 `03_slides/slides.md` 的实际页序一致；
- `[ANIMATION: name]` 一个名字只对应一个场景；
- 讲稿解释画面，不逐字复述页面。

**Gate G2**：每个学习目标有对应段落；每段有来源/主张；锚点完整、纯文本、未被代码块/引用块/注释包裹；无未标注的公式或数字。每批后运行：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage script
```

全部模块完成后更新 `handoff.md`，建议 `/clear`（C2）。

### Stage 3 — Slidev 排版

调用 `slidev` Skill。只做排版，不写动画逻辑。**分两步**：

**P1 骨架**：读取讲稿的 `[SLIDE: NN]`，只生成标题与分页骨架，不填充正文。运行 `--stage slides` 检查页数。

**P2 填充**：按模块逐段填充页面；每 1–2 个模块后检查一次。动画只写占位：

```html
<video src="/name.mp4" controls class="w-full" />
```

约束：

- 页面写入 `03_slides/slides.md`；
- 不在 Slidev 里生成 Manim 代码；
- 页面标题与讲稿 `[SLIDE: NN]` 对齐；
- 不要一次生成全部页面后才发现页序错位。

运行：

```powershell
# 开发服务器（OBS/浏览器预览）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 `
  -Episode <slug> -Mode dev -Port 3030

# 静态构建
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 `
  -Episode <slug> -Mode build
```

**Gate G3**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage slides
```

`pnpm ... slidev build` 退出码 0；`03_slides/dist/index.html` 存在；逐页浏览器检查无溢出；`public/` 资源可访问。P1 骨架完成后可先检查页数；P2 填充完成后再构建。完成后更新 `handoff.md`，建议 `/clear`（C4）。

### Stage 4 — Manim 隔离舱

调用 `manim-isolation` Skill。**不要给每个公式都做动画**；只挑 1–2 个核心锚点。一次只处理一个锚点，完成并渲染后再处理下一个。

> 为 `[ANIMATION: navier_stokes]` 生成 `04_manim_src/scenes/navier_stokes.py`。
>
> **隔离约束**：
> 1. 只读 `01_research/03-knowledge-structure.md` 的符号；只写这一个场景。
> 2. **语法锁定**：Manim Community v0.22.0（`from manim import *`），禁用 `manimlib`。
> 3. **API 边界**：禁用 `ThreeDScene`、`ThreeDCamera`、`Camera3D`、`ThreeDAxes`、`ParametricSurface` 与粒子系统；只做基础 2D 几何与文本变换。
> 4. **时长上限**：单场景不超过 20 秒；`check-episode.py` 会按声明的 `run_time`/`wait` 估算并判错。
> 5. 不引入外部字体、图片、网络资源。
>
> 用项目本地 `.venv` 渲染；输出到 `03_slides/public/navier_stokes.mp4`。不要改讲稿或 Slidev。

渲染：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 `
  -Episode <slug> -Name navier_stokes -SceneClass NavierStokes -Quality l -TimeoutSeconds 180
```

- 迭代用 `-Quality l`；
- 内容/视觉确认后用 `-Quality h`；
- 默认 180 秒超时；超时会用 `taskkill /T` 杀掉整棵进程树，避免 Manim 暴走；
- 脚本会检查 MP4 存在且非空，输出 `STATUS=PASS_VERIFIED`。

**Gate G4**：每个 `[ANIMATION]` 有对应 `.py` 与 `.mp4`；MP4 非空；场景通过 API/时长 lint（ManimCE 0.22、无 3D/粒子、≤20s）；渲染未超时；抽帧检查开头/中间/结尾；未渲染的标 `NOT_RUN`。每完成一个锚点运行：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage manim
```

检查通过后再处理下一个锚点；上下文明显变长时 `/clear`（C5）。

### Stage 5 — QA 与交接

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage qa --strict
python D:\CourseStudio\tools\check-links.py courses\<slug>
python D:\CourseStudio\tools\test_check_episode_negative.py
```

若出现 `Issues`：只修相关文件，重跑；同一问题连续 3 次修不好就停下报告，不要放宽检查或删证据。

`check-episode.py` 检查：

- 讲稿锚点是否被代码块/引用块/注释包裹（包裹即 FAIL）；
- `[SLIDE: NN]` 是否严格按 1..N 递增；重复、跳号、乱序均 FAIL；
- 讲稿锚点数 `M` 与 Slidev 页数 `N` 的映射：允许 `N >= M` 并输出 buffer；`M > N` FAIL；
- Slidev 页数（`news`/`podcast` 可无 Slidev）；
- 每个动画的 `.py` 与 `.mp4`；
- Manim 场景是否使用禁用 API、声明时长是否超过 20 秒；
- 真实 MP4 用 `ffprobe` 读取时长；超过 20 秒 FAIL；无法读取时终检 FAIL；
- 研究包完整性：`course`/`technical` 的 00–06 必须非空；`news`/`podcast` 的 source/claim 必须非空且台账含 `FACT`/`CLAIM`；
- `course`/`technical` 在 `--stage qa --strict` 下会实际运行 `slidev-run.ps1 -Mode build`；构建非 0 即 FAIL；
- `handoff.md` 是否存在。

再执行：

- 浏览器逐页检查（16:9、导航、视频、控制台）；
- 抽帧检查 Manim；
- 观众版泄漏扫描；
- 将命令、退出码、结果写入 `qa/`。

**Gate G5**：`check-episode.py --mode <mode> --stage qa --strict` 返回 0 且 `Issues` 为空；映射满足 `M <= N`；`course`/`technical` 的 Slidev build 必须实际通过；`test_check_episode_negative.py` 7/7 通过；QA 报告区分 `PASS_VERIFIED` / `PASS_STATIC` / `PARTIAL` / `NOT_RUN` / `FAIL`。

### Stage 6 — OBS 录制（人工，高容错）

1. `slidev-run.ps1 -Mode dev` 启动（`podcast` 模式可只开音频）；
2. 浏览器全屏，确认 16:9；
3. OBS 场景：课件全屏 + 麦克风；
4. **实战录制**：按讲稿念诵并翻页。**允许口误，不强求掐点**；出错停顿 2 秒重念，后期一刀切掉废片；
5. 用“2 秒静音”或拍手作为切点；连续录制，不按段重来；
6. 录制后抽帧核对，记录 `qa/recording-checklist.md`。

> OBS 未在常规路径检测到；使用前先人工确认安装。AI 不参与录制。

### Stage 7 — 交付与 Git

- `README.md` 写清状态、限制、未执行项；
- `handoff.md` 更新到最终状态；
- 根仓库只跟踪框架；课程在 `courses/<slug>/` 内独立 `git init`/提交；
- 不提交 PDF、`01_research/downloads/`、`fulltext/`、`03_slides/public/*.mp4`、`04_manim_src/media/`、`dist/`、`.venv/`、`node_modules/`、`.pnpm-store/`；
- 人工确认 `git status --short` 后提交；不自动推送。

## 4. 阶段交接文件

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

下一阶段只读 `handoff.md` + 指定输入，不重读整个项目。检查点与 `/clear` 规则见 [claude-orchestrator.md](claude-orchestrator.md)。

## 5. 失败处理

| 现象 | 处理 |
| --- | --- |
| 锚点被包在代码块/引用块/注释里 | `check-episode.py` 判 FAIL；把锚点改成纯文本独立成行 |
| `[SLIDE]` 重复、跳号或乱序 | 判 FAIL；改成严格 `01, 02, 03...`，不要重复编号 |
| 研究文件存在但为 0 字节 | 判 FAIL；补内容，不要留占位空文件 |
| news/podcast 缺 source/claim 或台账无 `FACT`/`CLAIM` | 判 FAIL；补 `source-register.md`、`claims-ledger.md` 与条目 |
| Manim 使用 `ThreeDScene`/`Camera3D`/粒子等 | `check-episode.py` 列出禁用 API；改回基础 2D 几何与文本 |
| 单场景声明时长超过 20 秒 | `check-episode.py` 判 FAIL；拆分锚点或减少 `run_time`/`wait` |
| 真实 MP4 时长超过 20 秒 | `ffprobe` 判 FAIL；裁剪视频或拆分动画 |
| `ffprobe` 不可用 | 终检/动画阶段判 FAIL；确认 ffmpeg 的 `ffprobe` 在 PATH |
| 渲染超过 180 秒 | `render-manim.ps1` 杀掉进程树；简化场景，不要靠超时硬跑 |
| 渲染失败 | 日志会保留；按控制台 `LOG=` 路径查看，不要反复重跑掩盖错误 |
| Slidev 构建失败 | `--stage qa --strict` 判 FAIL；修 `slides.md`、视频路径或依赖后重跑 |
| Slidev 构建报 `markdown-it` 导出错误 | 确认 `tools/slidev-runtime/package.json` 锁定 `markdown-it@14.1.0` |
| `slidev` 命令不存在 | 用 `slidev-run.ps1`，不要全局安装；运行时在 `tools/slidev-runtime` |
| Manim 渲染找不到输出 | 检查 `--media_dir` 与 `--output_file`；`render-manim.ps1` 会递归查找 |
| 动画锚点没有 MP4 | `check-episode.py` 会列出；回到 Stage 4 补渲染 |
| 讲稿/课件阶段报 missing MP4 | 用 `--stage script` 或 `--stage slides`，不要加 `--strict`；MP4 属于 Stage 4 |
| 中间阶段状态是 PARTIAL | 正常；只要 `Issues` 为空即可继续，`Warnings` 记入 `handoff.md` |
| 课程 `.venv` 用了错误 Python 版本 | `uv python pin 3.12` 后重建 `.venv`；新集由 `new-episode.ps1` 固定 3.12 |
| 新建集失败留下半成品目录 | `new-episode.ps1` 会自动回滚；若仍残留，人工确认后删除 |
| 研究包缺文件 | 回 Stage 1；不要用模型记忆补 |
| OBS 未安装 | 人工安装/确认；录制阶段 `NOT_RUN` |

## 6. 不要做

- 不要把锚点包在代码块、引用块或 HTML 注释里；它必须独立成行。
- 不要让 Manim 使用 `manimlib`、`ThreeDScene`、`Camera3D`、粒子系统或外部网络资源。
- 不要在 OBS 阶段追求完美掐点；允许口误，停顿 2 秒重念，后期剪掉。
- 不要在同一个会话里同时做研究、讲稿、排版、动画；每阶段结束写 `handoff.md` 后 `/clear`。
- 不要让 `course-studio` 生成 HTML 课件；本流程固定 Slidev。
- 不要让 `slidev` 写动画逻辑；动画只走 `manim-isolation`。
- 不要让 `manim-isolation` 改讲稿或页面。
- 不要跳过来源登记与主张台账；新闻/播客同样需要。
- 不要全局 `pip install` / `npm install -g` / 改 PATH。
- 不要把 PDF、MP4、`.venv`、`node_modules`、`.pnpm-store` 提交进 Git。
