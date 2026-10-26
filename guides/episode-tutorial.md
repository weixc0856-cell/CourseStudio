# Episode 使用教程（课程 / 新闻 / 播客）

本教程是 [episode-pipeline.md](../workflows/episode-pipeline.md) 的操作版；最短路径见 [quickstart-episode.md](quickstart-episode.md)，分块状态机见 [claude-orchestrator.md](../workflows/claude-orchestrator.md)，硬性验收与 Git 规则见 [requirements.md](requirements.md)。所有产物放在 `D:\CourseStudio\courses\<slug>\`；所有环境在项目内构建，不装全局 Python/npm 包。

## 0. 先决条件

| 组件 | 位置 / 说明 |
| --- | --- |
| Motion Canvas 模板 | `tools/motion-runtime/`；第一次 `motion-run.ps1` 时在课程 `04_motion_src/` 内安装 |
| Reveal 运行时 | `tools/reveal-runtime/`（`reveal.js@6.0.2`）；`pnpm install` 一次 |
| Slidev 运行时 | `tools/slidev-runtime/`（technical / news / 旧课） |
| Python | 系统 Python 3.12；`check-episode.py` / `build-recording-package.py` / `python -m http.server` |
| OBS | 人工确认安装；AI 不调用，相关项 `NOT_RUN` |

> 不运行全局 `npm install -g` / `pip install`，不改系统 PATH。

## 0.1 一条主指令（推荐）

不要每次复制长 Prompt。把 [claude-orchestrator.md](../workflows/claude-orchestrator.md) 作为主规则，每次只发一句：

> 请严格按照 `workflows/claude-orchestrator.md` 的规则，推进 `courses/<slug>` 的管线。当前模式：`course|technical|news|podcast`。先读 `handoff.md` 判断状态，只执行下一个子步骤；写完后运行对应 `--stage` 检查，更新 `handoff.md` 并停下等我确认。

它每次只做一个子步骤：写文件 → 跑 `check-episode.py --stage ...` → 修到无 `Issues` → 更新 `handoff.md` → 停止。

## 1. 默认技术栈与模式

| 模式 | 动画 | 课件 | 研究 |
| --- | --- | --- | --- |
| `course` | Motion Canvas 45–90s | **Reveal 默认**（`03_slides/index.html`） | `00`–`06` |
| `technical` | Motion Canvas；Manim 兜底 | **Slidev 默认**（`03_slides/slides.md`） | `00`–`06` + 公式 |
| `news` | 可选 Motion | Slidev 3–8 页，可选 | `source-register` + `claims-ledger` |
| `podcast` | 无 | 无 | `source-register` + `claims-ledger` + 提纲 |

新 `course` 的顺序是：

```text
research → script（含节奏标注）→ motion → recording（录制就绪包）→ Reveal slides → qa → 人工 OBS 录制
```

`recording` 阶段是生成 `05_recording/`，不是 OBS 实拍；实拍在 QA 之后由人工完成。

## 2. 建集

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 `
  -Name course-example -Mode course
```

生成（course）：

```text
courses/course-example/
├── 01_research/
├── 02_scripts/lecture_script.md
├── 03_slides/
│   ├── index.html            # Reveal（course 默认）
│   └── assets/deck.css
├── 04_motion_src/
│   ├── record.html
│   ├── segments.json
│   └── src/{scenes,projects,theme.ts}
├── 05_recording/
│   ├── manifest.json
│   ├── checklist.md
│   └── cues/example.md
├── qa/
├── handoff.md
└── .gitignore
```

- 默认**不安装 Manim**；需要兜底时加 `-WithManim`。
- `technical` / `news` 默认保留 Slidev，移除 Reveal 模板；`podcast` 不要求课件。
- 不自动 `git init`、不提交、不渲染。

**G0**：目录、讲稿、`segments.json`、`05_recording/`、`handoff.md` 存在；course 有 `index.html`，technical/news 有 `slides.md`。

## 3. 研究输入（R1–R4）

不要一次生成 `00`–`06`。按轮推进，每轮只写该轮产物：

1. **R1 来源登记**：`01-source-inventory.md` + `search-results/`；
2. **R2 主张台账**：`02-claim-evidence-ledger.csv`；
3. **R3 知识结构**：`03-knowledge-structure.md`；
4. **R4 冻结大纲**：`00`、`04`、`05`、`06`。

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage research
```

`00`–`06` 必须非空；每条关键主张有 `CLM-XXX` 与定位。完成后更新 `handoff.md`，建议 `/clear`。

## 4. 讲稿与节奏标注

按大纲模块，每次写 1–2 个模块，追加到 `02_scripts/lecture_script.md`。不要生成 HTML 课件，不要默认 Manim。

### 4.1 锚点

```text
[SLIDE: 05]
[ANIMATION: attention_scores]
```

- 锚点必须纯文本独立成行；禁止包在代码块、引用块或 HTML 注释中。
- `[SLIDE: NN]` 严格 1..N，与课件页序对应。
- `[ANIMATION: name]` 对应一个 Motion 段落。

### 4.2 节奏标注

每个 motion 段落紧跟：

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

- 每个 `[ANIMATION]` 恰好一个 `[SEGMENT]`；
- 45–90 秒；
- 至少各一条 `HOLD` / `EMPHASIS` / `CUT`；
- 时间戳严格递增，最后一条不超过声明时长；
- name / 时长 / order 与 `04_motion_src/segments.json` 一致。

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage script
```

缺标注、时长越界、时间戳乱序、与 `segments.json` 不一致都会 FAIL。

## 5. Motion Canvas 段落

技能契约：[tools/skills/motion-isolation/SKILL.md](../tools/skills/motion-isolation/SKILL.md)。

### 5.1 冻结 `segments.json`

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

`segments.json` 是引擎、时长、顺序与录制顺序的唯一事实来源。Manim 仅 `engine: "manim"` 时使用。

### 5.2 写一个段落

```text
04_motion_src/
├── src/scenes/example.tsx
└── src/projects/example.ts
```

3B1B 风格：

- 先建立几何对象 → 用变换推导 → 每个关键步骤 `waitFor` 停顿；
- 不用装饰性粒子 / 3D / 复杂运镜；
- 显式 `fontFamily={theme.fontFamily}`；
- 一个段落 45–90 秒；代码拆成 `beat1()` / `beat2()`。

启动录制页：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
  -Episode course-example -Segment example
```

打开打印的 `http://localhost:9100/record.html?segment=example`。第一次会安装课程内依赖。

- **不要用 `?present` 录制**：全屏仍有演示控件。
- 页面使用 `@motion-canvas/player`，`auto="true"`，隐藏播放器 UI。
- 全屏后等 2 秒，再开始 OBS。
- QA 可用 `record.html?segment=example&probe=1` 读取真实时长；录制不要带 `probe`/`loop`。

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage motion
```

每个段落 scene / project / cue 齐全，45–90 秒，order 连续。完成后更新 `handoff.md`，建议 `/clear`。

## 6. 录制就绪包

```powershell
python D:\CourseStudio\tools\build-recording-package.py course-example
```

生成/刷新：

- `05_recording/manifest.json`：顺序、`record.html?segment=<name>`、声明时长、cue、`record_status`；
- `05_recording/cues/<name>.md`：画面指令与口播行；
- `05_recording/checklist.md`：段落表与 URL。

生成器严格校验、幂等；缺源/缺标注直接失败，不写空包；`record_status` 保留。

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage recording
```

`recordings/` 与实拍文件不强制存在；OBS 仍未开录，标 `NOT_RUN`。

## 7. 课件

### 7.1 Course：Reveal（默认）

- `03_slides/index.html` + `assets/deck.css`；
- 每页 `<section class="c-slide" data-slide="01">…</section>`，`data-slide` 严格 1..N；
- `Reveal.initialize` 固定 `1920×1080`、`margin:0`、`center:false`、无 controls/progress/slideNumber、`transition:'none'`、`hash:true`；
- 动画页只放占位（段落名、声明时长、`record.html?segment=<name>`），**不嵌 MP4**。

先同步 `.vendor` 并启动静态服务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 `
  -Episode course-example -Port 3040
```

打开 `http://127.0.0.1:3040/index.html`，F11 全屏。

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage slides
```

`data-slide` 跳号、缺页序、本地资源缺失均 FAIL；strict 不跑 Slidev build。

### 7.2 Technical / news / 旧课：Slidev

`03_slides/slides.md`；P1 骨架 → P2 填充；动画只放占位。Manim 兜底 MP4 才可写 `<video>`；Motion 段落仍用 `record.html` 独立录制。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 `
  -Episode course-example -Mode dev -Port 3030
```

## 8. QA

```powershell
python D:\CourseStudio\tools\build-recording-package.py course-example
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage qa --strict
python D:\CourseStudio\tools\check-links.py courses\course-example
python D:\CourseStudio\tools\test_check_episode_negative.py
```

- Reveal 先运行 `reveal-run.ps1` 同步 `.vendor`；可另开终端跑检查。
- `Issues` 必须为空；`Warnings` 写进 `handoff.md`。
- `test_check_episode_negative.py` 必须 32/32。
- 浏览器逐页检查；Reveal 全屏无控制条；Slidev 16:9、导航、视频、控制台。
- OBS 录制仍为 `NOT_RUN`。

## 9. 人工 OBS 录制

1. 打开 `05_recording/checklist.md`；建议**先录 Motion 动画段，再录 Reveal/Slidev 课件页**；
2. Reveal 用 `reveal-run.ps1`，Slidev 用 `slidev-run.ps1`，浏览器全屏；
3. Motion 段落在 `record.html?segment=<name>` 逐段录；
4. OBS 用 Display Capture / Windows Graphics Capture，**不要用 BitBlt/GDI 窗口采集**；
5. 4K + 150% 缩放下 OBS 画布仍 1920×1080，对源缩放；全屏后等 2 秒；
6. 每段前/后各留 2 秒；允许口误，停顿 2 秒重念；
7. 录完 `ffprobe` 核对，更新 manifest `record_status`；
8. 录像放 `05_recording/recordings/`（不提交）。

> OBS 不由 AI 调用；未安装/未运行时标 `NOT_RUN`。

## 10. handoff

| 字段 | 内容 |
| --- | --- |
| 模式 | course / technical / news / podcast |
| 阶段 | research / script / motion / recording / slides / qa / record |
| 子步骤 | R1 / S1 / M1 / RC1 / P1 / Q1 / REC |
| 模块进度 | 例如 2/6 |
| 段落进度 | 例如 1/3 |
| 动画引擎 | motion / manim（仅兜底） |
| 课件类型 | Reveal / Slidev |
| 录制包 | 未生成 / 已生成 / 已检查 |
| 验证状态 | PASS_VERIFIED / PASS_STATIC / PARTIAL / NOT_RUN / FAIL |

## 11. 常见失败

| 现象 | 处理 |
| --- | --- |
| 缺 `[SEGMENT]` / HOLD / EMPHASIS / CUT | 补节奏标注；script/motion 阶段硬失败 |
| motion 时长不是 45–90 | 调整段落；不要套用 Manim 的 20 秒限制 |
| `[SEGMENT]` 与 `segments.json` 不一致 | 以 `segments.json` 为准修正 |
| 缺 scene/project/cue | 补文件；cue 可由生成器从讲稿生成 |
| `record.html` 不播放 | 确认 `auto="true"`；不要在升级前设 `quality`/`width`/`height` |
| 用 `?present` 录制 | 改 `record.html?segment=<name>` |
| Reveal 缺 `data-slide` / 跳号 | 按 1..N 修正 |
| Reveal 本地资源缺失 | 先运行 `reveal-run.ps1` 同步 `.vendor` |
| Reveal 里嵌了 MP4 | 删除；动画用 `record.html` 独立录制 |
| Slidev 构建失败 | 修 `slides.md` 或依赖；终检会实际 build |
| legacy Manim 超过 20 秒 | 仅兜底路径；拆分场景或改回 Motion |

## 12. Legacy / fallback

- **Manim**：仅 `segments.json` 的 `engine: "manim"`；单场景 ≤20 秒；`manim-isolation` + `render-manim.ps1`；不是默认。
- **Slidev**：`technical` / `news` / 旧课；不是新 course 默认。
- 旧课不强制迁移；新 episode 按 Motion + Reveal（course）或 Motion + Slidev（technical）推进。
