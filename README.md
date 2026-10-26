# Course Studio

把论文、报告、新闻、数据和工程资料，做成**有来源、可讲解、可复核**的课程或视频材料。人负责最终的讲解、录屏和剪辑；这里负责研究、结构、页面、动画、口播稿和 QA。

## 做什么，不做什么

做：

- 来源研究与主张登记
- 教学/叙事设计、分镜、口播稿
- Slidev 课件（16:9）与静态图；HTML/CSS 作为兼容路径
- 需要时用 ManimCE 做机制动画
- 新闻视频、技术解读与纯音频播客
- 数值、公式、页面、旁白的一致性检查
- 可复现的渲染与浏览器验收

不做：

- 自动 TTS、自动配音、自动剪辑完整长视频
- 自动发布或提交 Git
- 把程序检查通过说成教学效果已经验证
- 用外部“人性化”工具替代事实核验和人工审读

## 三种主要任务

| 任务 | 先读 | 需要时再读 |
| --- | --- | --- |
| 课程制作 | [CLAUDE.md](CLAUDE.md)、[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)、[workflows/episode-pipeline.md](workflows/episode-pipeline.md)、[guides/episode-tutorial.md](guides/episode-tutorial.md)、[guides/editorial-voice.md](guides/editorial-voice.md) | [guides/audience-vs-internal.md](guides/audience-vs-internal.md)、[guides/delivery-quality.md](guides/delivery-quality.md)、Skill 的 `references/*` |
| 新闻解读 | [workflows/news-analysis.md](workflows/news-analysis.md)、[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)、[guides/episode-tutorial.md](guides/episode-tutorial.md)（`news` 模式） | [guides/editorial-voice.md](guides/editorial-voice.md)、[guides/delivery-quality.md](guides/delivery-quality.md) |
| 技术/论文解读 | [workflows/technical-explainer.md](workflows/technical-explainer.md)、[workflows/episode-pipeline.md](workflows/episode-pipeline.md)（`technical` 模式）、[guides/episode-tutorial.md](guides/episode-tutorial.md) | Skill 的 `references/source-and-claims.md`、`references/domain-checks.md`；需要动画时读 `references/manim-workflow.md` |
| 单纯润色 | [guides/editorial-voice.md](guides/editorial-voice.md) + 目标文件 | 不重读整个项目，不重跑研究 |
| 修改已有产物 | 目标源文件 + 对应 `qa/` + 对应 workflow | 不默认重启研究阶段 |

低 Token 原则：**只读任务需要的文件**。不要一次加载全部指南，也不要把所有规范复制进 Skill 主文件。

## 工具分工

| 工具 | 负责 | 不负责 |
| --- | --- | --- |
| Slidev | **默认课件排版**（Episode 流程）：Markdown、代码、公式、Vue | 动画逻辑（交给 `manim-isolation`） |
| manim-isolation | 读取 `[ANIMATION: name]`，写单场景 Manim 源码并渲染 MP4 | 教研、讲稿、页面排版 |
| ManimCE | 公式、矩阵、数据流、状态变化 | 替代页面、替代讲解 |
| paper-search | 检索/下载论文全文 | 事实核验、教学判断 |
| research-to-course-synthesis | `00`–`06` 研究输入包 | 写讲稿/页面 |
| course-studio | 讲稿、研究/教学流程；HTML 兼容路径 | 生成 Slidev 排版（需 prompt 明确覆盖） |
| HTML / CSS | 轻量/兼容课件；不引入 Slidev 时使用 | 默认 Episode 流程 |
| frontend-slides | 零依赖 HTML 演示备选 | 默认 Episode 流程 |

## 目录

```text
D:\CourseStudio\
├── CLAUDE.md               # Agent 出厂约定（先读编排规则）
├── README.md
├── guides/                 # 编辑、受众、交付质量、Episode 教程
├── workflows/
│   ├── claude-orchestrator.md  # 分块状态机、停点、/clear 规则
│   ├── episode-pipeline.md     # 默认：Episode + Slidev + Manim 隔离
│   └── course.md               # 通用课程原则/兼容路径
├── prompts/                # 可直接粘贴的任务入口
├── courses/                # 产物根目录；根仓库忽略，每课独立 Git
│   ├── README.md           # 命名、模式、布局映射
│   └── <slug>/             # 每门课程自己的仓库
├── labs/                   # 本地实验环境；根仓库忽略
├── .gitignore              # 根仓库：只跟踪框架，忽略 courses/* 与 labs/
├── .config/                # 工具本地配置（.env 不提交）
├── tools/
│   ├── new-episode.ps1     # 新建 Episode（按模式，课程本地 .venv）
│   ├── episode-template/   # Episode 目录/文件模板
│   ├── slidev-runtime/     # 共享 Slidev 运行时（node_modules/.pnpm-store 不入库）
│   ├── slidev-run.ps1      # 启动/构建 Slidev
│   ├── render-manim.ps1    # 渲染场景并复制 MP4（180s 超时）
│   ├── check-episode.py    # 锚点/页数/场景/MP4/Manim API/时长检查
│   ├── skills/manim-isolation/  # 独立动画隔离 Skill
│   ├── new-course.ps1      # 旧版 HTML 课程脚手架（兼容）
│   ├── course.gitignore    # 课程仓库忽略模板
│   ├── check-links.py      # 检查 Markdown 相对链接
│   └── paper-search-mcp/   # 论文检索 CLI（项目内隔离）
└── .uv-cache/              # uv 缓存（不提交）
```

每门课程是独立的 uv 项目（`course`/`technical` 模式）或纯文档项目（`news`/`podcast` 可跳过 Python）。默认 Episode 布局：

```text
courses/<slug>/
├── .gitignore              # 由 new-episode.ps1 复制
├── 00_raw_materials/       # 原始 PDF/HTML（PDF 不提交）
├── 01_research/            # 00–06、search-results/、downloads/、fulltext/
├── 02_scripts/lecture_script.md
├── 03_slides/slides.md     # Slidev（news/podcast 可无）
│   └── public/             # Manim MP4（不提交）
├── 04_manim_src/scenes/    # Manim 场景源码（可无）
├── qa/
├── handoff.md              # 阶段/子步骤/进度/最后检查
├── README.md
├── pyproject.toml          # course/technical
├── uv.lock                 # course/technical
└── .python-version         # course/technical
```

旧版 `course/index.html` + `research/` + `design/` 布局仍兼容，见 [workflows/course.md](workflows/course.md)。

## 环境隔离

- 不在系统 Python 或全局环境安装课程依赖。
- 课程依赖只进入该课程的 `.venv`；用 `uv add` / `uv run`；uv cache 固定到 `D:\CourseStudio\.uv-cache`。
- Slidev 依赖只进入 [tools/slidev-runtime](tools/slidev-runtime)；pnpm store 固定到 `tools/slidev-runtime/.pnpm-store`，不写全局 npm。
- `news` / `podcast` 模式可跳过 Python 与 Manim；需要时再在课程内 `uv add manim`。
- 不修改系统 PATH 或全局配置来绕过渲染问题。
- 课程/技术模式保留 `pyproject.toml`、`uv.lock` 和 `.python-version`。

## 仓库与忽略规则

- **根仓库只跟踪框架**：`CLAUDE.md`、`README.md`、`guides/`、`workflows/`、`prompts/`、`tools/`（不含缓存与运行时依赖）。
- 根 [.gitignore](.gitignore) 忽略 `/courses/*`（仅保留 `courses/README.md`）与 `/labs/`；课程文档不在根仓库。
- **每门课程在 `courses/<slug>/` 内独立 `git init`**；课程自己的 `.gitignore`（由 `new-episode.ps1` 复制）管理课程文档与产物。
- 课程仓库提交：源码、`uv.lock`、`.python-version`、研究台账、检索 JSON、QA 报告、页面与动画源码。
- 课程仓库不提交：PDF 全文、`01_research/downloads/`、`fulltext/`、`03_slides/public/*.mp4`、`04_manim_src/media/`、`dist/`、`.venv/`、`node_modules/`、`.pnpm-store/`、`.env` 与密钥。
- 大体积成片与授权素材放仓库外或 Git LFS。
- `tools/paper-search-mcp` 是外部仓库；如果根仓库要跟踪它，使用 submodule，不要直接嵌入 `.git`。
- 完整边界见 [episode-pipeline.md](workflows/episode-pipeline.md) 与 [tools/README.md](tools/README.md)；远程与克隆流程见 [guides/repository-and-remote.md](guides/repository-and-remote.md)。

## 质量与状态

使用五种状态，并给出实际证据：

- `PASS_VERIFIED`：实际运行并核对
- `PASS_STATIC`：静态检查通过
- `PARTIAL`：部分条件无法验证
- `NOT_RUN`：未执行
- `FAIL`：实际失败

程序检查通过只证明程序检查通过。内容正确性、视觉质量和教学效果是不同层次的判断；没有人工评审或学习者测试时，不要写成“已验证”。

`--stage qa --strict` 在 `course`/`technical` 下会实际运行 Slidev build；构建失败、ffprobe 时长超限、研究文件为空或 slide 编号重复/跳号，都不能算通过。检查器自身用 `python tools/test_check_episode_negative.py` 做 7 项负向回归；`[SLIDE]` 锚点数 `M` 与页数 `N` 必须满足 `M <= N`，并输出 mapping 报告。

## 开始一次新任务

1. 读 [CLAUDE.md](CLAUDE.md)、[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)、[workflows/episode-pipeline.md](workflows/episode-pipeline.md) 和对应 guides；不要先读全部文件。
2. 新建 Episode：`tools/new-episode.ps1 -Name <slug> -Mode <course|technical|news|podcast>`。
3. 研究 **R1→R4 分轮**（来源 → 台账 → 知识结构 → 大纲），不要一次生成 `00`–`06`；R4 后跑 `--stage research`。
4. 讲稿 **S1→S3 分模块**（1–2 模块/轮，追加写入）；每批跑 `--stage script`。
5. 课件 **P1 骨架 → P2 填充**；每阶段跑 `--stage slides`，再用 `slidev-run.ps1` 构建。
6. 动画只挑 **1–2 个核心锚点**，一次一个；每个跑 `--stage manim` 并抽帧检查。
7. 终检：`tools/check-episode.py <slug> --mode <mode> --stage qa --strict`；修复到无 `Issues`。
8. 更新 `handoff.md` 后停下等确认；只在 C1/C2/C4/C5/C6/C7 检查点 `/clear`。
9. 交付说明区分已通过、未运行和仍需人工判断的部分。
10. Git 提交由人工确认；不提交密钥、PDF 全文、MP4、`.venv`、`node_modules`、`.pnpm-store`。

新闻视频与纯音频播客使用同一套 Episode 流程，分别用 `--mode news` / `--mode podcast`；可跳过 Slidev/Manim，但不能跳过来源登记与主张台账。分场景步骤见 [guides/episode-tutorial.md](guides/episode-tutorial.md)。

## 项目状态（2026-10-26）

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 框架文档 | `PASS_STATIC` | `CLAUDE.md`、编排器、流程、教程、链接检查 |
| Slidev 运行时 | `PASS_VERIFIED` | `@slidev/cli 53.0.0`；build/dev/public 资源已验证；本地 store |
| Manim 运行时 | `PASS_VERIFIED` | 0.22.0；课程本地 `.venv`；渲染与 180s 超时已验证 |
| `check-episode.py` | `PASS_VERIFIED` | 分阶段检查；锚点防逃逸、API/时长、四种模式 |
| `paper-search` | `PASS_VERIFIED` | CLI + Skill；**不是已注册 MCP** |
| `manim-isolation` | `PASS_VERIFIED` | 项目内 Skill + 全局 junction |
| OBS | `NOT_RUN` | 常规路径未检测到；录制为人工阶段 |
| Playwright PDF 导出 | `NOT_RUN` | 未安装；不影响 Slidev dev/build |
| 真实 Episode | `NOT_RUN` | 尚未跑第一集真实课程 |
| 新闻/播客模式 | `PASS_STATIC` | 脚手架与检查器已支持；未跑真实项目 |

现有目录：`transformer-course-pilot`（HTML 试点）、`attention-research-2026-10`（研究输入测试）。`transformer-course-pilot` 的 `.venv` 与浏览器 profile 已清理，按需 `uv sync` 重建；`attention-research` 的 PDF/全文已清理，保留研究文档与检索 JSON。按默认布局，它们不在根仓库中；需要版本管理时在各自目录 `git init`。

## 当前能力与已知限制

可用：ManimCE 0.22.0（课程本地 `.venv`）、Slidev 53（`tools/slidev-runtime`，项目内）、Node 24 / pnpm 10、ffmpeg 8、Chrome 浏览器验收、`manim-isolation`（独立 Skill）、Python 数值核验、uv 独立环境、项目内 `paper-search`（arXiv/OpenAlex 等 20+ 来源，CLI + Skill）。

限制：OBS 未在常规路径检测到；没有 TTS 或自动剪辑；参考视频/部分技术文档可能无法访问；PDF 全文受网络与许可限制；Slidev PDF 导出需要的 Playwright 未安装；`paper-search` 不是已注册 MCP；人工教学评审和学习效果测试不在自动流程内。具体课程的限制记录在各自的 `qa/known-limitations.md`。

## 规范索引

- [CLAUDE.md](CLAUDE.md)：Agent 出厂约定（先读编排规则、分块执行、停点）
- [guides/requirements.md](guides/requirements.md)：课程制作、QA、清理与 Git 的硬性要求
- [guides/editorial-voice.md](guides/editorial-voice.md)：中文技术写作与口播的编辑规范
- [guides/audience-vs-internal.md](guides/audience-vs-internal.md)：观众版、教学限定与内部 QA 的边界
- [guides/delivery-quality.md](guides/delivery-quality.md)：内容、准确性、视觉、可复现性与人工审查
- [guides/episode-tutorial.md](guides/episode-tutorial.md)：课程 / 新闻 / 播客的分场景使用教程
- [guides/repository-and-remote.md](guides/repository-and-remote.md)：远程仓库、忽略规则、克隆重建与推送流程
- [courses/README.md](courses/README.md)：课程/新闻产物根目录、命名与两种布局
- [workflows/episode-pipeline.md](workflows/episode-pipeline.md)：默认流程（Episode + Slidev + Manim 隔离）
- [workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)：分块状态机、每轮模板、停点与 `/clear` 规则
- [workflows/course.md](workflows/course.md)：课程制作通用流程与兼容路径
- [workflows/pipeline-audit.md](workflows/pipeline-audit.md)：五阶段管线兼容性审计与修复记录
- [tools/README.md](tools/README.md)：工具清单、命令与环境边界
- [workflows/news-analysis.md](workflows/news-analysis.md)：新闻解读流程
- [workflows/technical-explainer.md](workflows/technical-explainer.md)：技术/论文解读流程
- [prompts/](prompts/)：任务入口模板
