# Courses — 课程与新闻产物根目录

`D:\CourseStudio\courses\` 是后续**课程、新闻解读、技术/论文解读**产物的统一根目录。研究实验环境放在 `labs/`，工具与 Skill 放在 `tools/` 和全局技能目录，不混入课程产物。

## 0. 模式

| 模式 | 适用 | 必需 | 可选 |
| --- | --- | --- | --- |
| `course` | 系统课程 | `01_research`、`02_scripts`、`03_slides`、`qa/` | `04_manim_src` |
| `technical` | 论文/技术精读 | 同上 + 公式检查 | `04_manim_src` |
| `news` | 新闻/行业解读 | `01_research` 来源/台账、`02_scripts`、`qa/` | `03_slides`（3–8 页） |
| `podcast` | 纯音频播客 | `01_research` 来源/台账、`02_scripts`、`qa/` | 无 Slidev/Manim |

`check-episode.py --mode` 按模式检查；新闻与播客不要求 Slidev/Manim，但不能跳过来源登记与主张台账。

## 1. 命名

新项目建议使用带类型前缀的 slug：

| 类型 | 目录名 | 例子 |
| --- | --- | --- |
| 课程 | `course-<slug>/` | `course-transformer-attention/` |
| 新闻解读 | `news-<slug>-<YYYYMM>/` | `news-ai-chip-export-202610/` |
| 技术/论文解读 | `technical-<slug>/` | `technical-flashattention/` |
| 纯研究输入 | `<topic>-research-<YYYY-MM>/` | `attention-research-2026-10/` |
| 冒烟测试 | `zz-<purpose>/` | `zz-smoke-test/` |

已有目录不强制改名；新目录按上表执行。一个项目只使用一种布局，不混用。新项目默认使用 **B（Episode + Slidev + Manim 隔离）**；只有明确不需要 Slidev 时才用 A。

## 2. 两种布局（新项目默认 Episode）

### A. CourseStudio 兼容布局（轻量/备用）

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

### B. Episode 四阶段布局（默认；Slidev + Manim 隔离）

```text
course-<slug>/
├── 00_raw_materials/      # 原始 PDF/HTML（PDF 不提交）
├── 01_research/           # 证据台账、知识结构、课程输入简报
├── 02_scripts/            # 口播稿（含 [SLIDE] / [ANIMATION] 锚点）
├── 03_slides/             # Slidev
│   ├── slides.md
│   └── public/            # Manim MP4（不提交）
├── 04_manim_src/scenes/   # Manim 场景源码
├── qa/
└── handoff.md
```

### 布局映射

| Episode 布局 | CourseStudio 默认布局 | 说明 |
| --- | --- | --- |
| `00_raw_materials/` | `sources/` 或 `research/downloads/` | 原始材料；PDF 不提交 |
| `01_research/` | `research/` | 00–06 或 `source-register.md` + `claims-ledger.md` |
| `02_scripts/` | `scripts/` | `narration.md` 或 `speaker-notes.md` |
| `03_slides/` | `course/` 或 `slides/` | Slidev 用 `slides.md` + `public/` |
| `04_manim_src/` | `animations/manim/` | Manim 场景源码 |
| `03_slides/public/*.mp4` | `animations/rendered/` | 只保留一份，避免双份大文件 |
| `qa/` | `qa/` | 状态、限制、失败记录 |

## 3. 每个项目的必备文件

- `README.md`：模式、目标、受众、当前状态、已知限制。
- `.gitignore`：由 [tools/new-episode.ps1](../tools/new-episode.ps1) / [tools/new-course.ps1](../tools/new-course.ps1) 从 [tools/course.gitignore](../tools/course.gitignore) 复制。
- `01_research/`（或兼容布局的 `research/`）：来源与主张台账。
- `02_scripts/lecture_script.md`：口播稿；课程/技术模式必须含视觉锚点。
- `handoff.md`：阶段、输入、输出、命令、状态、未决项。
- `qa/`：实际运行过的检查、退出码、未执行项；录制模式加 `qa/recording-checklist.md`。
- 若使用 Slidev：`03_slides/slides.md`；运行时由 [tools/slidev-runtime](../tools/slidev-runtime) 共享，不需要为每集安装 `node_modules`。
- 若使用 Manim：`04_manim_src/scenes/<name>.py` 与 `03_slides/public/<name>.mp4`。
- 若使用 HTML（兼容布局）：`course/index.html`。

## 4. Git 与提交边界

- 每个项目一个独立 Git 仓库；根仓库只跟踪框架，`.gitignore` 忽略 `/courses/*`（仅保留本 `README.md`）。
- 提交：源码、`uv.lock`、`.python-version`、研究台账、检索 JSON、QA 报告、口播稿、`handoff.md`。
- 不提交：PDF 全文、`01_research/downloads/`、`fulltext/`、`03_slides/public/*.mp4`、`04_manim_src/media/`、`dist/`、`.venv*/`、`node_modules/`、`.pnpm-store/`、`.env`、密钥。
- 大体积成片与授权素材放仓库外或 Git LFS。

## 5. 现有项目

| 目录 | 类型 | 布局 | 状态 |
| --- | --- | --- | --- |
| `transformer-course-pilot/` | 课程试点 | A（HTML + Manim） | 已完成试点，见其 `qa/` |
| `attention-research-2026-10/` | 纯研究输入 | 研究包在根目录 | 研究输入测试完成 |
| `zz-smoke-test/` | 冒烟测试 | A | 不作为交付物 |

这些目录默认不在根仓库中；需要版本管理时，在各自目录内 `git init`。

## 6. 相关文档

- [workflows/episode-pipeline.md](../workflows/episode-pipeline.md)：Episode + Slidev + Manim 隔离默认流程。
- [workflows/claude-orchestrator.md](../workflows/claude-orchestrator.md)：分块状态机、停点与每轮执行模板。
- [guides/episode-tutorial.md](../guides/episode-tutorial.md)：课程 / 新闻 / 播客分场景教程。
- [workflows/course.md](../workflows/course.md)：课程制作通用流程。
- [workflows/pipeline-audit.md](../workflows/pipeline-audit.md)：五阶段管线兼容性审计与修复记录。
- [workflows/news-analysis.md](../workflows/news-analysis.md)：新闻解读流程。
- [workflows/technical-explainer.md](../workflows/technical-explainer.md)：技术/论文解读流程。
