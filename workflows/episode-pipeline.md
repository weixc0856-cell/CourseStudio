# Workflow — Episode Pipeline（Motion Canvas + Reveal；Slidev technical；Manim fallback）

适用于课程、新闻、技术/论文解读与播客的单集生产。**默认布局**：`D:\CourseStudio\courses\<slug>\`，动画主路径是 Motion Canvas **45–90 秒**叙事段落，课件主路径是 Reveal.js；`technical` / 旧课可继续 Slidev；Manim 仅作兜底。

> 本文件是执行主线；最短路径见 [quickstart-episode.md](../guides/quickstart-episode.md)，分块状态机与停点见 [claude-orchestrator.md](claude-orchestrator.md)，分场景教程见 [episode-tutorial.md](../guides/episode-tutorial.md)，硬性验收见 [requirements.md](../guides/requirements.md)。通用课程原则仍见 [course.md](course.md)。

## 0. 模式与默认技术栈

| 模式 | 研究深度 | 动画 | 课件 | 录制 |
| --- | --- | --- | --- | --- |
| `course` | `01_research/00`–`06` | Motion Canvas（45–90s） | **Reveal 默认**（`03_slides/index.html`） | OBS 视频 |
| `technical` | `00`–`06` + 公式检查 | Motion Canvas；必要时 Manim 兜底 | **Slidev 默认**（`03_slides/slides.md`） | OBS 视频 |
| `news` | `source-register` + `claims-ledger` | 可选 Motion | Slidev（3–8 页，可选） | OBS 视频/音频 |
| `podcast` | `source-register` + `claims-ledger` + 提纲 | 不需要 | 不需要 | OBS 音频/视频 |

- 新 `course` 默认流程：**research → script（含节奏标注）→ motion → recording（录制就绪包）→ Reveal slides → qa → 人工 OBS 录制**。
- `technical` / `news` 的 slides 阶段使用 Slidev；旧课不强制迁移。
- **Manim 不是默认动画引擎**。只有 `segments.json` 中 `engine: "manim"` 的兜底锚点才走 Manim；`new-episode.ps1` 默认不安装 Manim。
- `recording` 阶段指生成/校验 `05_recording/` 录制就绪包，**不是** OBS 实拍；实拍在 QA 之后由人工完成，标 `NOT_RUN`。

## 0.1 分块执行与停点

**文件产出 ≠ 验收通过。** 每次只推进一个 Stage 的一个子步骤：写一小块 → 跑检查 → 修到无 `Issues` → 更新 `handoff.md` → 停下等人工确认。

| Stage | 子步骤 | 检查命令 |
| --- | --- | --- |
| research | R1 来源 → R2 台账 → R3 知识结构 → R4 大纲冻结 | `--stage research` |
| script | S1/S2/S3：按大纲 1–2 模块/次，追加写；同步写 `[SEGMENT]` 节奏标注 | `--stage script` |
| motion | M1 冻结 segments → M2 单个 scene/project → M3 下一段 | `--stage motion` |
| recording | RC1 生成/刷新 `05_recording/` 并检查结构 | `--stage recording` |
| slides | 课程 Reveal P1 骨架 → P2 填充；technical Slidev 同理 | `--stage slides` |
| qa | Q1 终检 → Q2 浏览器/视觉 | `--stage qa --strict` |
| record | 人工 OBS 录制；AI 不调用 | 人工，`NOT_RUN` |

检查命令：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage <research|script|motion|recording|slides|manim|qa>
```

- 中间阶段允许 `PARTIAL`，但 `Issues` 必须为空。
- 终检加 `--strict`；警告逐条写入 `handoff.md`。
- 每轮结束更新 `handoff.md` 并停止；**禁止自动跨 Stage**。
- 同一 Issue 连续修复 3 次仍失败：停止报告，不放宽检查、不删证据。

### `/clear` 停点

1. 研究大纲冻结（C1）
2. 讲稿全部模块完成（C2）
3. 每个/每两个 Motion 段落完成（C3）
4. 录制就绪包生成完成（C4）
5. Reveal / Slidev 课件完成（C5）
6. 最终 QA 前（C6）
7. 人工录制前（C7）

`/clear` 只清上下文，不是验收。

## 1. 目录契约

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
│   └── lecture_script.md          # [SLIDE] / [ANIMATION] / [SEGMENT] / 节奏标注
├── 03_slides/
│   ├── index.html                 # Reveal（course 默认）
│   ├── assets/deck.css
│   ├── slides.md                  # Slidev（technical/news/旧课）
│   ├── .vendor/                   # reveal-run 同步（不提交）
│   ├── public/                    # legacy/兜底 Manim MP4（不提交）
│   └── dist/                      # Slidev 构建产物（不提交）
├── 04_motion_src/
│   ├── record.html                # 录制主路径
│   ├── segments.json              # 段落事实来源
│   ├── package.json / pnpm-lock.yaml / vite.config.ts / tsconfig.json
│   └── src/{scenes,projects,theme.ts}
├── 04_manim_src/scenes/           # 仅 -WithManim 创建；兜底
├── 05_recording/
│   ├── manifest.json
│   ├── checklist.md
│   ├── cues/<name>.md
│   └── recordings/                # 实拍文件（不提交）
├── qa/
├── handoff.md
├── README.md
├── pyproject.toml / uv.lock / .python-version   # podcast 可无
└── .gitignore
```

命名别名：

| 外部名 | 实际文件 |
| --- | --- |
| `evidence_ledger.csv` | `01_research/02-claim-evidence-ledger.csv` |
| `knowledge_structure.md` | `01_research/03-knowledge-structure.md` |
| `lecture_script.md` | `02_scripts/lecture_script.md` |
| `scene` | `04_motion_src/src/scenes/<name>.tsx` |
| `segments` | `04_motion_src/segments.json` |
| `cue` | `05_recording/cues/<name>.md` |
| `manifest` | `05_recording/manifest.json` |
| `scene.py`（legacy） | `04_manim_src/scenes/<name>.py` |

## 2. 工具与真实调用名

| 用途 | 调用名 | 位置 / 说明 |
| --- | --- | --- |
| 检索/下载 | `paper-search` | `tools/paper-search-mcp/bin/paper-search` |
| 研究输入 | `research-to-course-synthesis` | 全局 Skill |
| 讲稿 | `course-studio` | 全局 Skill（目录名 `course-studio-skill`） |
| Motion 动画 | `motion-isolation` | `tools/skills/motion-isolation/SKILL.md` |
| 录制页 | `motion-run.ps1` | 启动 `record.html?segment=<name>` |
| 录制包 | `build-recording-package.py` | 生成 `05_recording/` |
| Reveal 课件 | `reveal-run.ps1` | 同步 `.vendor` + Python 静态服务 |
| Slidev 课件 | `slidev-run.ps1` | `technical` / `news` / 旧课 |
| Manim 兜底 | `manim-isolation` + `render-manim.ps1` | 仅 `engine=manim` |
| 润色（可选） | `humanizer` | 全局 Skill |
| OBS | 人工 | 非 Skill；`NOT_RUN` |

**预览与录制的区别**：`?present` 只用于快速预览；录制必须用 `record.html?segment=<name>`。`?present` 全屏仍保留演示控件。

## 3. 阶段与 Gate

### Stage 0 — 建集

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name <slug> -Mode <course|technical|news|podcast>
```

- 创建目录契约、`.gitignore`、模板、`04_motion_src/`、`05_recording/` 与 `handoff.md`；
- `course` 默认 Reveal（`index.html` + `assets/`），移除 `slides.md`；
- `technical` / `news` 保留 Slidev（`slides.md`），移除 Reveal 模板；`podcast` 不要求课件（脚手架可能保留空模板，可删除）；
- 默认不安装 Manim；`-WithManim` 才在课程 `.venv` 安装 Manim 并创建 `04_manim_src/`；
- 不自动 `git init`、不提交、不渲染、不安装 Motion 依赖（首次 `motion-run` 时安装）。

**Gate G0**：目录存在；`02_scripts/lecture_script.md`、`04_motion_src/segments.json`、`05_recording/`、`handoff.md` 存在；`course` 有 `03_slides/index.html`，`technical`/`news` 有 `slides.md`；Manim 仅在明确要求时存在。

### Stage 1 — 研究输入

工作目录：`courses/<slug>/`，研究产物写入 `01_research/`。

使用 `paper-search`：

```bash
P=/d/CourseStudio/tools/paper-search-mcp/bin/paper-search
$P search "<query>" -s fast -n 5 --source-timeout 30 > 01_research/search-results/q01.json
$P download arxiv 1706.03762 -o 01_research/downloads
```

使用 `research-to-course-synthesis`，按四轮推进，不要一次生成 `00`–`06`：

1. **R1 来源**：`01-source-inventory.md` + `search-results/`；
2. **R2 台账**：`02-claim-evidence-ledger.csv`；
3. **R3 知识结构**：`03-knowledge-structure.md`（公式、符号、量纲）；
4. **R4 冻结大纲**：`00`、`04`、`05`、`06`。

要求：

- 每条关键主张有 `CLM-XXX` 与页码/公式/表格定位；
- 区分 `FACT` / `CLAIM` / `INFERENCE` / `ASSUMPTION`；
- 冲突保留双方证据与适用范围；
- `05-quality-report.md` 写明 `NOT_RUN` / `PARTIAL`；
- `course`/`technical` 的 `00`–`06` 全部非空；`news`/`podcast` 的 `source-register.md` 与 `claims-ledger.md` 非空，且台账含 `FACT`/`CLAIM`。

**Gate G1**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage research
```

未过 Gate 不写讲稿。完成后更新 `handoff.md`，建议 `/clear`（C1）。

### Stage 2 — 讲稿与节奏标注

按 `06-course-outline.md` 的模块分批：每次只写 1–2 个模块，追加到 `02_scripts/lecture_script.md`，不重写全文。

Prompt 必须覆盖 `course-studio` 的旧默认：

> 本课程使用 Episode + Motion Canvas 主路径。只写 `02_scripts/lecture_script.md`；不要生成 HTML 课件，不要默认 Manim。本次仅写模块 `<X–Y>`，追加写入。使用纯文本独立成行的 `[SLIDE: NN]` 与 `[ANIMATION: name]`；每个 motion 段落在 `[ANIMATION]` 后紧跟一个 `[SEGMENT: name | NNs | order=N]`，并写 `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]` 节奏标注。引用 `01_research/04-course-input-brief.md` 与 `03-knowledge-structure.md`。锚点禁止包在代码块、引用块或 HTML 注释中。

节奏标注示例：

```text
[ANIMATION: example]
[SEGMENT: example | 45s | order=1]
[VISUAL 00:00] 建立坐标系
[HOLD 00:05] 停 2 秒
[EMPHASIS 00:15] 高亮关键量
[CUT 00:23] 切换视图
[VISUAL 00:33] 收束
（口播：先把 a 接上 b；从原点指向终点的箭头就是 a + b。）
```

规则：

- 每个 `[ANIMATION]` 恰好一个 `[SEGMENT]`；name / 时长 / order 与 `04_motion_src/segments.json` 一致；
- 声明 **45–90 秒**（不是旧的 ≤20 秒）；
- 至少各一条 `HOLD` / `EMPHASIS` / `CUT`；`VISUAL` 建议至少一条；
- 时间戳严格递增，最后一条不超过声明时长；
- 旧 Manim-only 段落不要求这套标注。

**Gate G2**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage script
```

缺标注、时长越界、时间戳乱序、与 `segments.json` 不一致均为 **Issues**。全部模块完成后更新 `handoff.md`，建议 `/clear`（C2）。

### Stage 3 — Motion Canvas 段落

调用 `motion-isolation`（读取 `tools/skills/motion-isolation/SKILL.md`）。**不要给每个公式都做动画**；只为核心概念做完整叙事段落。一次只处理一个段落。

**M1 冻结段落清单**：把讲稿中的 `[ANIMATION]` / `[SEGMENT]` 写入 `04_motion_src/segments.json`：

```json
{
  "canvas": {"width": 1920, "height": 1080, "fps": 60},
  "segments": [
    {
      "name": "example",
      "engine": "motion",
      "duration_seconds": 45,
      "order": 1,
      "scene": "example",
      "record_status": "NOT_RUN"
    }
  ]
}
```

- `segments.json` 是引擎、时长、顺序与录制顺序的唯一事实来源；
- `engine` 必填：`motion` 或 `manim`；不靠文件存在性猜；
- 缺 `segments.json` 的旧 episode 才回退 Manim 文件存在性检查，并给 deprecation warning。

**M2 单个场景/工程**：只写 `src/scenes/<name>.tsx` 与 `src/projects/<name>.ts`。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
  -Episode <slug> -Segment <name>
```

- 首次运行会在课程目录内 `pnpm install --frozen-lockfile`；
- 打印 `record.html?segment=<name>`；用 Chrome 全屏，等待 2 秒再录制；
- `record.html` 使用 `@motion-canvas/player`，`auto="true"`，隐藏播放器 UI；`?present` 仅预览；
- 3B1B 风格：先建立几何对象 → 用变换推导 → 每个关键步骤 `waitFor` 停顿；禁止装饰性粒子、3D、复杂运镜；
- 显式使用 `theme.fontFamily`；目标 45–90 秒；
- 不默认渲染 MP4；Manim 渲染仅作兜底/归档。

**M3 下一段**：重复 M2；每完成一个段落运行：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage motion
```

**Gate G3**：每个 motion 段落有 scene / project / cue；声明 45–90 秒；`order` 连续；引擎不歧义；有录像时 `ffprobe` 读取，否则 `NOT_VERIFIED`。未通过不进入下一段。

### Stage 4 — 录制就绪包

运行生成器：

```powershell
python D:\CourseStudio\tools\build-recording-package.py <slug>
```

生成/刷新：

- `05_recording/manifest.json`：按 `order` 列出 motion 段落，URL 指向 `record.html?segment=<name>`；
- `05_recording/cues/<name>.md`：`[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]` 与对应口播行；
- `05_recording/checklist.md`：刷新段落表与 URL 提示。

要求：

- 以讲稿 + `segments.json` 为源；不要手工维护 manifest / cues；
- 严格校验，缺源/缺标注/时长或顺序不一致直接失败，**不写空包**；
- 可重复执行（幂等）；`record_status` 保留；
- 覆盖所有 `engine=motion` 段落；
- `recordings/` 与实拍文件不强制存在。

**Gate G4**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage recording
```

manifest / checklist / cues 完整；`recordings/` 可选；OBS 实拍仍为 `NOT_RUN`。

### Stage 5 — 课件（Reveal 默认 / Slidev compatible）

#### 5.1 Course：Reveal（默认）

- 文件：`03_slides/index.html` + `assets/deck.css`；默认橙白主题 `theme/white.css`；
- 每页 `<section class="c-slide" data-slide="01">…</section>`，`data-slide` 严格 1..N，顺序与 `[SLIDE: NN]` 对应；
- `Reveal.initialize` 固定：`width:1920, height:1080, margin:0, center:false, controls:false, progress:false, slideNumber:false, transition:'none', hash:true`；
- 动画页只放占位：段落名、声明时长、`record.html?segment=<name>` 提示；**不嵌 MP4**；
- 本地 `src`/`href` 必须存在；`.vendor/reveal` 由 `reveal-run.ps1` 同步（不提交）。

分两步：P1 只建页序骨架；P2 填充内容。每 1–2 页检查一次。

```powershell
# 同步 .vendor 并启动静态服务（另开终端跑检查）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 `
  -Episode <slug> -Port 3040
```

**Gate G5a**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode course --stage slides
```

Reveal：`data-slide` 1..N、本地资源存在、`[SLIDE]` 映射通过；strict 不跑 Slidev build。缺 `data-slide`、跳号、资源缺失均 FAIL。

#### 5.2 Technical / news / 旧课：Slidev

- 文件：`03_slides/slides.md`；
- P1 骨架 → P2 填充；动画只放占位；
- Manim 兜底 MP4 可写 `<video src="/name.mp4" controls class="w-full" />`；Motion 段落仍用 `record.html` 独立录制，不嵌入；
- `slidev-run.ps1 -Mode dev/build`；构建由终检实际执行。

**Gate G5b**：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode technical --stage slides
```

### Stage 6 — QA 与交接

```powershell
# 先刷新录制包（幂等）
python D:\CourseStudio\tools\build-recording-package.py <slug>

# Reveal：先同步 .vendor；Slidev：无需
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 `
  -Episode <slug> -Port 3040   # 另开终端；同步后可按 Ctrl+C

python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage qa --strict
python D:\CourseStudio\tools\check-links.py courses\<slug>
python D:\CourseStudio\tools\test_check_episode_negative.py
```

`check-episode.py` 检查：

- 讲稿锚点未包裹；`[SLIDE]` 严格 1..N；
- motion：`segments.json` 分派；scene / project / cue；45–90 秒；顺序；节奏标注；
- recording：`05_recording/` 的 manifest、checklist、cues；实拍文件不强制；
- Reveal：`data-slide` 1..N、本地资源、映射；strict 跳过 Slidev build；
- Slidev：实际 build；Manim 兜底：禁用 API、≤20 秒、`ffprobe` 真实时长；
- 研究包完整性；`handoff.md` 存在。

再执行：

- 浏览器逐页检查（Reveal 全屏、无控制条；Slidev 16:9、导航、视频、控制台）；
- Motion 抽帧/真实时长（`record.html?segment=<name>&probe=1` 或实拍 `ffprobe`）；
- 观众版泄漏扫描；
- 命令、退出码、结果写入 `qa/`。

**Gate G6**：`--strict` 返回 0 且 `Issues` 为空；映射 `M <= N`；Reveal 资源/页序通过或 Slidev build 通过；回归 32/32；QA 报告区分 `PASS_VERIFIED` / `PASS_STATIC` / `PARTIAL` / `NOT_RUN` / `FAIL`。

### Stage 7 — OBS 录制（人工，高容错）

1. 打开 `05_recording/checklist.md`；
2. Reveal 课件用 `reveal-run.ps1` / Slidev 用 `slidev-run.ps1`，浏览器全屏；
3. Motion 段落逐段打开 `record.html?segment=<name>`，不要在 `?present` 里录；
4. OBS 使用 Display Capture 或 Window Capture (Windows Graphics Capture)，**不要用 BitBlt/GDI 窗口采集**；
5. 4K + 150% 缩放下 OBS 画布仍设 1920×1080，对源缩放；进入全屏后等 2 秒；
6. 每段前/后各留 2 秒静止；允许口误，停顿 2 秒重念；后期拼接；
7. 录完用 `ffprobe` 核对时长，更新 `05_recording/manifest.json` 的 `record_status`；
8. 录像放 `05_recording/recordings/`（不提交）。

> OBS 不是由 AI 调用的工具。未安装/未运行时，本阶段标 `NOT_RUN`。

### Stage 8 — Manim 兜底（可选，非默认）

仅当 `segments.json` 的某个锚点 `engine: "manim"`，或用户明确要求：

- `new-episode.ps1 -WithManim` / 课程内 `uv add manim==0.22.0`；
- 调用 `manim-isolation`（legacy），输出 `04_manim_src/scenes/<name>.py` 与 `03_slides/public/<name>.mp4`；
- 单场景 ≤20 秒，禁用 3D/粒子/manimlib；`render-manim.ps1` 默认 180 秒超时；
- 检查：`--stage manim`；真实 MP4 用 `ffprobe`；
- 不要把 Manim 改回默认路径，也不要把 Motion 段落改成 MP4 嵌入。

## 4. 阶段交接文件

每次 `/clear` 前更新 `handoff.md`：

| 字段 | 内容 |
| --- | --- |
| 模式 | course / technical / news / podcast |
| 阶段 | research / script / motion / recording / slides / qa / record |
| 子步骤 | R1 / S1 / M1 / RC1 / P1 / Q1 / REC … |
| 模块进度 | 例如 2/6 |
| 段落进度 | 例如 1/3（motion） |
| 动画引擎 | motion / manim（仅兜底） |
| 课件类型 | Reveal / Slidev |
| 录制包 | 未生成 / 已生成 / 已检查 |
| 输入文件 | |
| 输出文件 | |
| 已运行命令 | |
| 最后检查 | 命令 + 状态 |
| 验证状态 | PASS_VERIFIED / PASS_STATIC / PARTIAL / NOT_RUN / FAIL |
| 未决事项 | |
| 下一步 | |

## 5. 失败处理

| 现象 | 处理 |
| --- | --- |
| 锚点被包在代码块/引用块/注释里 | 判 FAIL；改成纯文本独立成行 |
| `[SLIDE]` 重复、跳号或乱序 | 判 FAIL；改成严格 `01, 02, 03...` |
| motion 缺 `[SEGMENT]` / HOLD / EMPHASIS / CUT | `--stage script`/`motion` 判 FAIL；补标注 |
| motion 时长不是 45–90 | 判 FAIL；调整段落节奏或重新拆分 |
| 时间戳乱序或超过声明时长 | 判 FAIL；按时间顺序重写 cue |
| `[SEGMENT]` 与 `segments.json` 不一致 | 判 FAIL；以 `segments.json` 为准修正讲稿或清单 |
| engine 缺失且 motion/Manim 文件都在 | 判 FAIL；在 `segments.json` 明确 engine |
| motion 缺 scene/project/cue | `--stage motion` 判 FAIL；补齐实际文件 |
| 录制包缺 manifest/checklist/cues | `--stage recording` 判 FAIL；重新运行生成器 |
| 生成器缺源/缺标注 | 直接失败，不写空包；补讲稿或 `segments.json` |
| Reveal 缺 `data-slide` / 跳号 | `--stage slides` 判 FAIL；按 1..N 补页序 |
| Reveal 本地资源缺失 | 检查 `assets/` 与 `.vendor/reveal`；先运行 `reveal-run.ps1` |
| `reveal-run` 报运行时缺失 | 在 `tools/reveal-runtime` 运行 `pnpm install` |
| Reveal 里嵌了 MP4 | 删除；动画页只放占位，用 `record.html` 独立录制 |
| `record.html` 不播放 | 确认 `auto="true"`，不要裸 `auto`；不要在元素升级前设 `quality`/`width`/`height` |
| 用 `?present` 录制 | 错误路径；控件会入镜，改用 `record.html?segment=<name>` |
| Slidev 构建失败 | `--stage qa --strict` 判 FAIL；修 `slides.md` 或依赖 |
| Manim 使用 3D/粒子/manimlib | 兜底阶段判 FAIL；改回基础 2D |
| legacy Manim MP4 超过 20 秒 | legacy `--stage manim` 判 FAIL；拆分场景；这不是 Motion 约束 |
| `ffprobe` 不可用 | 终检/录像校验判 FAIL；确认 ffmpeg 在 PATH |
| 研究文件为空 | 判 FAIL；补内容，不要留占位 |
| 中间阶段 `PARTIAL` | 正常；`Issues` 为空即可继续，Warnings 写 `handoff.md` |
| OBS 未安装 | 人工安装/确认；录制阶段 `NOT_RUN` |

## 6. 不要做

- 不要把 Motion 段落限制回 ≤20 秒；主路径是 45–90 秒叙事段落。
- 不要把 Manim 当默认动画引擎；它是兜底。
- 不要把 course 默认课件改回 Slidev；Reveal 是 course 默认，technical/旧课可用 Slidev。
- 不要把 Motion 段落渲染成 MP4 再嵌进 Reveal；用 `record.html` 独立录制。
- 不要让 `?present` 进入录制清单。
- 不要在同一个会话里同时做研究、讲稿、动画、录制包和课件；每阶段写 `handoff.md` 后停。
- 不要让 `motion-isolation` 改讲稿/课件；不要让 `reveal-run` 写动画逻辑。
- 不要跳过来源登记与主张台账；新闻/播客同样需要。
- 不要全局 `pip install` / `npm install -g` / 改 PATH。
- 不要把 PDF、MP4、`.venv`、`node_modules`、`.pnpm-store`、`03_slides/.vendor/`、`05_recording/recordings/` 提交进 Git。
- 不要安装、调用或自动化 OBS。
