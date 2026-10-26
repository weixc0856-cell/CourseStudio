# Courses — 课程与新闻产物根目录

`D:\CourseStudio\courses\` 是后续**课程、新闻解读、技术/论文解读**产物的统一根目录。研究实验环境放在 `labs/`，工具与 Skill 放在 `tools/` 和全局技能目录，不混入课程产物。

## 0. 模式

| 模式 | 适用 | 必需 | 可选 |
| --- | --- | --- | --- |
| `course` | 系统课程 | `01_research`、`02_scripts`、`03_slides`（Reveal 默认；旧课可 Slidev）、`qa/` | `04_motion_src`（动画主路径）、`05_recording`（录制就绪包）、`04_manim_src`（兜底） |
| `technical` | 论文/技术精读 | `01_research`、`02_scripts`、`03_slides`（Slidev 默认）、`qa/` + 公式检查 | `04_motion_src`（动画主路径）、`05_recording`（录制就绪包）、`04_manim_src`（兜底） |
| `news` | 新闻/行业解读 | `01_research` 来源/台账、`02_scripts`、`qa/` | `03_slides`（3–8 页） |
| `podcast` | 纯音频播客 | `01_research` 来源/台账、`02_scripts`、`qa/` | 无 Slidev/Manim |

`check-episode.py --mode` 按模式检查；新闻与播客不要求 Reveal/Slidev/Manim，但不能跳过来源登记与主张台账。`source-register.md` 与 `claims-ledger.md` 必须同时存在且非空，台账必须含 `FACT` 或 `CLAIM` 条目。

> 2026-10 起，新 `course`/`technical` 默认使用 `04_motion_src`（Motion Canvas）。Manim 仅在 `new-episode.ps1 -WithManim` 或 `segments.json` 的 `engine: "manim"` 时使用，作为兜底。讲稿中每个 motion 段落必须写 `[SEGMENT]` + `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]`；`tools/build-recording-package.py` 生成 `05_recording/`。检查器新增 `--stage motion`（场景/工程/cue、45–90 秒、顺序、节奏标注）与 `--stage recording`（`05_recording/` 的 manifest、checklist、cues；不要求录像文件已存在）；终检 `--stage qa --strict` 会同时检查 motion 段落与录制包结构。course 默认 `03_slides/index.html`（Reveal）；technical/news 继续 `slides.md`（Slidev）；旧课不强制迁移。Reveal 资源由 `reveal-run.ps1` 同步到 `03_slides/.vendor/`（不提交）；动画页只放占位，动画仍由 `record.html?segment=<name>` 独立录制，不嵌 MP4。检查器在 Reveal 路径下校验 `data-slide` 1..N 与本地 `src`/`href`，strict 跳过 Slidev build。

## 1. 命名

新项目建议使用带类型前缀的 slug：

| 类型 | 目录名 | 例子 |
| --- | --- | --- |
| 课程 | `course-<slug>/` | `course-transformer-attention/` |
| 新闻解读 | `news-<slug>-<YYYYMM>/` | `news-ai-chip-export-202610/` |
| 技术/论文解读 | `technical-<slug>/` | `technical-flashattention/` |
| 纯研究输入 | `<topic>-research-<YYYY-MM>/` | `attention-research-2026-10/` |
| 冒烟测试 | `zz-<purpose>/` | `zz-tmp-test/` |

已有目录不强制改名；新目录按上表执行。一个项目只使用一种布局，不混用。新项目默认使用 **B（Episode + Motion Canvas；course 用 Reveal，technical/news 用 Slidev；Manim 为可选兜底）**。A 是 legacy 兼容布局，仅用于维护旧项目，不用于新项目。最短路径见 [guides/quickstart-episode.md](../guides/quickstart-episode.md)。

## 2. 两种布局（新项目默认 Episode）

### A. CourseStudio 兼容布局（legacy；仅维护旧项目）

```text
course-<slug>/
├── README.md
├── .gitignore
├── pyproject.toml
├── uv.lock
├── .python-version
├── research/              # 00–06 或 source-register + claims-ledger
├── design/                # 目标、大纲、分镜
├── course/index.html      # HTML 课件（或 slides/ 放 Slidev）
├── scripts/narration.md   # 口播稿
├── animations/manim/      # Manim 源码
├── animations/rendered/   # 渲染产物（不提交）
└── qa/
```

### B. Episode 布局（默认；Motion Canvas 主路径 + Reveal/Slidev 课件）

```text
course-<slug>/
├── 00_raw_materials/      # 原始 PDF/HTML（PDF 不提交）
├── 01_research/           # 证据台账、知识结构、课程输入简报
├── 02_scripts/            # 口播稿（含 [SLIDE] / [ANIMATION] 锚点）
├── 03_slides/             # course: Reveal；technical/news: Slidev
│   ├── index.html         # Reveal（course 默认）
│   ├── assets/deck.css
│   ├── slides.md          # Slidev（technical/news）
│   ├── .vendor/           # reveal-run 同步，不提交
│   └── public/            # legacy/兜底 Manim MP4（不提交）
├── 04_motion_src/         # Motion Canvas 主路径（录制页 + 场景）
│   ├── record.html
│   ├── segments.json
│   └── src/
├── 04_manim_src/scenes/   # Manim 兜底（可选）
├── 05_recording/          # 录制就绪包（最终交付物）
├── qa/
└── handoff.md
```

### 布局映射

| Episode 布局 | CourseStudio 默认布局 | 说明 |
| --- | --- | --- |
| `00_raw_materials/` | `sources/` 或 `research/downloads/` | 原始材料；PDF 不提交 |
| `01_research/` | `research/` | 00–06 或 `source-register.md` + `claims-ledger.md` |
| `02_scripts/` | `scripts/` | `narration.md` 或 `speaker-notes.md` |
| `03_slides/` | `course/` 或 `slides/` | Reveal 用 `index.html` + `assets/`；Slidev 用 `slides.md` + `public/` |
| `04_motion_src/` | `animations/motion/` | Motion Canvas 主路径；录制页 + `segments.json` |
| `04_manim_src/` | `animations/manim/` | Manim 兜底源码 |
| `05_recording/` | `recording/` | 录制就绪包：manifest、checklist、cues；录像不提交 |
| `03_slides/public/*.mp4` | `animations/rendered/` | 只保留一份，避免双份大文件 |
| `qa/` | `qa/` | 状态、限制、失败记录 |

## 3. 每个项目的必备文件

- `README.md`：模式、目标、受众、当前状态、已知限制。
- `.gitignore`：由 [tools/new-episode.ps1](../tools/new-episode.ps1) / [tools/new-course.ps1](../tools/new-course.ps1) 从 [tools/course.gitignore](../tools/course.gitignore) 复制。
- `01_research/`（或兼容布局的 `research/`）：来源与主张台账。
- `02_scripts/lecture_script.md`：口播稿；课程/技术模式必须含视觉锚点。
- `handoff.md`：阶段、输入、输出、命令、状态、未决项。
- `qa/`：实际运行过的检查、退出码、未执行项；录制清单放在 `05_recording/checklist.md`。
- 录制就绪包：`05_recording/manifest.json`、`checklist.md`、`cues/`；录像放 `recordings/`，不提交。
- 若使用 Reveal（course 默认）：`03_slides/index.html` + `assets/deck.css`；`.vendor/reveal` 由 [tools/reveal-run.ps1](../tools/reveal-run.ps1) 从 [tools/reveal-runtime](../tools/reveal-runtime) 同步，不提交。
- 若使用 Slidev（technical/news/旧课）：`03_slides/slides.md`；运行时由 [tools/slidev-runtime](../tools/slidev-runtime) 共享，不需要为每集安装 `node_modules`。
- 若使用 Motion Canvas：`04_motion_src/src/scenes/<name>.tsx`、`src/projects/<name>.ts`、`segments.json`，录制入口 `record.html?segment=<name>`。
- 若使用 Manim（兜底）：`04_manim_src/scenes/<name>.py` 与 `03_slides/public/<name>.mp4`。
- 若使用 HTML（兼容布局）：`course/index.html`。

## 4. Git 与提交边界

- 每个项目一个独立 Git 仓库；根仓库默认只跟踪框架。当前例外：`transformer-self-attention/` 的源码进入根仓库，但 `node_modules`、`.vendor`、`recordings`、`downloads`、`fulltext` 等仍忽略。
- 提交：源码、`uv.lock`、`.python-version`、研究台账、检索 JSON、QA 报告、口播稿、`handoff.md`。
- 不提交：PDF 全文、`01_research/downloads/`、`fulltext/`、`03_slides/public/*.mp4`、`03_slides/.vendor/`、`04_manim_src/media/`、`04_motion_src/node_modules/`、`04_motion_src/output/`、`05_recording/recordings/`、`dist/`、`.venv*/`、`node_modules/`、`.pnpm-store/`、`.env`、密钥。
- 大体积成片与授权素材放仓库外或 Git LFS。
- 远程仓库、克隆重建与推送流程见 [guides/repository-and-remote.md](../guides/repository-and-remote.md)。

## 5. 现有项目

| 目录 | 类型 | 布局 | 状态 |
| --- | --- | --- | --- |
| `transformer-self-attention/` | 第一集 course | B（Motion + Reveal） | 内容/QA `PASS_VERIFIED`；录制就绪，待人工 OBS |
| `attention-research-2026-10/` | 纯研究输入样本 | 研究包在根目录 | 不是默认课程模板；00–06、检索 JSON 与台账保留 |
| `_retired/transformer-course-pilot/` | 历史 HTML + Manim 试点 | A（legacy） | 已退役；仅作对照，不参与当前流程 |
| `_retired/course-attention/` | 历史 Slidev + Manim 课程 | A/B 混合 legacy | 已退役；`.venv` 已删除，源码与 QA 保留 |

除 `transformer-self-attention/` 源码进入根仓库外，其它目录默认不在根仓库中；需要版本管理时在各自目录内 `git init`。`_retired/` 不用于新建课程或作为示例。

## 6. 相关文档

- [workflows/episode-pipeline.md](../workflows/episode-pipeline.md)：Episode + Motion Canvas + Reveal 默认流程；technical 用 Slidev，Manim 仅兜底。
- [workflows/claude-orchestrator.md](../workflows/claude-orchestrator.md)：分块状态机、停点与每轮执行模板。
- [guides/episode-tutorial.md](../guides/episode-tutorial.md)：课程 / 新闻 / 播客分场景教程。
- [guides/requirements.md](../guides/requirements.md)：QA、清理与 Git 硬性要求。
- [workflows/course.md](../workflows/course.md)：课程制作通用流程。
- [workflows/pipeline-audit.md](../workflows/pipeline-audit.md)：Episode 管线审计与修复记录。
- [workflows/news-analysis.md](../workflows/news-analysis.md)：新闻解读流程。
- [workflows/technical-explainer.md](../workflows/technical-explainer.md)：技术/论文解读流程。
