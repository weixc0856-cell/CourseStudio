# Course Studio

把论文、报告、新闻、数据和工程资料，做成**有来源、可讲解、可复核**的课程或视频材料。人负责最终的讲解、录屏和剪辑；这里负责研究、结构、页面、动画、口播稿和 QA。

## 做什么，不做什么

做：

- 来源研究与主张登记
- 教学/叙事设计、分镜、口播稿
- Reveal 课件（course 默认，16:9，橙白主题）与静态图；technical/news 可继续 Slidev；HTML/CSS 为 legacy 兼容路径
- Motion Canvas 做 45–90 秒机制动画（默认）；ManimCE 仅兜底
- 新闻视频、技术解读与纯音频播客
- 数值、公式、页面、旁白的一致性检查
- 可复现的构建、录屏页与浏览器验收

不做：

- 自动 TTS、自动配音、自动剪辑完整长视频
- 自动发布或提交 Git
- 把程序检查通过说成教学效果已经验证
- 用外部“人性化”工具替代事实核验和人工审读

## 三种主要任务

| 任务 | 先读 | 需要时再读 |
| --- | --- | --- |
| 课程制作 | [guides/quickstart-episode.md](guides/quickstart-episode.md)、[CLAUDE.md](CLAUDE.md)、[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)、[workflows/episode-pipeline.md](workflows/episode-pipeline.md)、[guides/episode-tutorial.md](guides/episode-tutorial.md)、[guides/editorial-voice.md](guides/editorial-voice.md) | [guides/audience-vs-internal.md](guides/audience-vs-internal.md)、[guides/delivery-quality.md](guides/delivery-quality.md)、Skill 的 `references/*` |
| 新闻解读 | [workflows/news-analysis.md](workflows/news-analysis.md)、[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)、[guides/episode-tutorial.md](guides/episode-tutorial.md)（`news` 模式） | [guides/editorial-voice.md](guides/editorial-voice.md)、[guides/delivery-quality.md](guides/delivery-quality.md) |
| 技术/论文解读 | [workflows/technical-explainer.md](workflows/technical-explainer.md)、[workflows/episode-pipeline.md](workflows/episode-pipeline.md)（`technical` 模式）、[guides/episode-tutorial.md](guides/episode-tutorial.md) | Skill 的 `references/source-and-claims.md`、`references/domain-checks.md`；需要动画时读 `tools/skills/motion-isolation/SKILL.md`；Manim 兜底再读 `references/manim-workflow.md` |
| 单纯润色 | [guides/editorial-voice.md](guides/editorial-voice.md) + 目标文件 | 不重读整个项目，不重跑研究 |
| 修改已有产物 | 目标源文件 + 对应 `qa/` + 对应 workflow | 不默认重启研究阶段 |

低 Token 原则：**只读任务需要的文件**。不要一次加载全部指南，也不要把所有规范复制进 Skill 主文件。

## 工具分工

| 工具 | 负责 | 不负责 |
| --- | --- | --- |
| Reveal | **course 默认课件**：固定 16:9、`data-slide` 1..N、静态资源 | 动画逻辑；动画段落独立录屏 |
| Motion Canvas | **默认动画**：45–90 秒 3B1B 风格叙事段落 + `record.html` | 教研、讲稿、课件排版 |
| Slidev | technical / news / 旧课课件 | 动画逻辑 |
| motion-isolation | 读取 `[ANIMATION]`/`[SEGMENT]`，写 Motion scene/project | 教研、讲稿、课件排版 |
| manim-isolation | **Legacy/fallback**：仅 `engine=manim` 时写单场景 MP4 | 默认动画路径 |
| ManimCE | 强公式/符号变换兜底 | 默认动画、替代讲解 |
| paper-search | 检索/下载论文全文 | 事实核验、教学判断 |
| research-to-course-synthesis | `00`–`06` 研究输入包 | 写讲稿/页面 |
| course-studio | 讲稿、研究/教学流程 | 默认生成旧式 HTML/Manim；需 prompt 明确覆盖 |
| HTML / CSS | 轻量/兼容课件 | 默认 Episode 流程 |
| frontend-slides | 零依赖 HTML 演示备选 | 默认 Episode 流程 |

## 目录

```text
D:\CourseStudio\
├── CLAUDE.md               # Agent 出厂约定（先读编排规则）
├── README.md
├── guides/                 # 编辑、受众、交付质量、Episode 教程
├── workflows/
│   ├── claude-orchestrator.md  # 分块状态机、停点、/clear 规则
│   ├── episode-pipeline.md     # 默认：Motion Canvas + Reveal；Manim 兜底
│   └── course.md               # 通用课程原则/兼容路径
├── prompts/                # 可直接粘贴的任务入口
├── courses/                # 产物根目录；默认忽略，transformer-self-attention 源码例外
│   ├── README.md           # 命名、模式、布局映射
│   └── <slug>/             # 每门课程自己的仓库
├── labs/                   # 本地实验环境；根仓库忽略
├── .gitignore              # 根仓库：默认只跟踪框架；transformer-self-attention 源码例外
├── .config/                # 工具本地配置（.env 不提交）
├── tools/
│   ├── new-episode.ps1     # 新建 Episode（按模式，课程本地 .venv）
│   ├── episode-template/   # Episode 目录/文件模板
│   ├── motion-runtime/     # Motion Canvas 模板（每课独立安装依赖）
│   ├── motion-run.ps1      # 启动 record.html?segment=<name>
│   ├── build-recording-package.py  # 生成 05_recording/ manifest/cues/checklist
│   ├── reveal-runtime/     # 共享 Reveal.js 6.0.2 运行时
│   ├── reveal-run.ps1      # 同步 .vendor + Python 静态服务
│   ├── slidev-runtime/     # 共享 Slidev 运行时（technical/news/旧课）
│   ├── slidev-run.ps1      # 启动/构建 Slidev
│   ├── render-manim.ps1    # Manim 兜底：渲染场景并复制 MP4（180s 超时）
│   ├── check-episode.py    # 锚点/节奏/45–90s/录制包/Reveal/Slidev/Manim 检查
│   ├── skills/motion-isolation/  # 默认动画 Skill
│   ├── skills/manim-isolation/   # Legacy/fallback Manim Skill
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
├── 02_scripts/lecture_script.md   # [SLIDE] / [ANIMATION] / [SEGMENT] / 节奏标注
├── 03_slides/
│   ├── index.html          # Reveal（course 默认）
│   ├── assets/deck.css
│   ├── slides.md           # Slidev（technical/news/旧课）
│   ├── .vendor/            # reveal-run 同步（不提交）
│   └── public/             # legacy/兜底 Manim MP4（不提交）
├── 04_motion_src/          # Motion Canvas 主路径（record.html / segments.json / src）
├── 04_manim_src/scenes/    # Manim 兜底（仅 -WithManim）
├── 05_recording/           # 录制就绪包（manifest / cues / checklist）
├── qa/
├── handoff.md              # 阶段/子步骤/进度/最后检查
├── README.md
├── pyproject.toml          # course/technical
├── uv.lock                 # course/technical
└── .python-version         # course/technical
```

旧版 `course/index.html` + `research/` + `design/` 布局仅作 legacy 兼容，不用于新项目；见 [workflows/course.md](workflows/course.md)。

## 环境隔离

- 不在系统 Python 或全局环境安装课程依赖。
- 课程依赖只进入该课程的 `.venv`；用 `uv add` / `uv run`；uv cache 固定到 `D:\CourseStudio\.uv-cache`。
- Slidev 依赖只进入 [tools/slidev-runtime](tools/slidev-runtime)；Reveal 依赖只进入 [tools/reveal-runtime](tools/reveal-runtime)；pnpm store 固定到各自运行时，不写全局 npm。
- Motion 依赖只进入课程的 `04_motion_src/node_modules`；`.venv` 只在 Manim 兜底或 Python 研究时使用。
- `news` / `podcast` 可跳过 Reveal/Slidev/Motion；需要 Manim 兜底时再在课程内 `uv add manim`。
- `03_slides/.vendor/` 与 `05_recording/recordings/` 是本地生成目录，不提交。
- 不修改系统 PATH 或全局配置来绕过渲染问题。
- 课程/技术模式保留 `pyproject.toml`、`uv.lock` 和 `.python-version`。

## 仓库与忽略规则

- **根仓库默认只跟踪框架**：`CLAUDE.md`、`README.md`、`guides/`、`workflows/`、`prompts/`、`tools/`（不含缓存与运行时依赖）。
- **当前唯一例外**：`courses/transformer-self-attention/` 的源码进入根仓库；`node_modules`、`.vendor`、`recordings`、`downloads`、`fulltext` 等仍忽略。
- 根 [.gitignore](.gitignore) 默认忽略 `/courses/*`（保留 `courses/README.md` 与上述例外）与 `/labs/`。
- **其它课程在 `courses/<slug>/` 内独立 `git init`**；课程自己的 `.gitignore`（由 `new-episode.ps1` 复制）管理课程文档与产物。
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

`--stage qa --strict`：Reveal 路径检查 `data-slide`/本地资源并跳过 Slidev build；Slidev 路径实际 build；Motion 段落校验 45–90 秒、scene/project/cue 与 `05_recording/` 结构；Manim 兜底才用 ffprobe。回归 `python tools/test_check_episode_negative.py` 共 32 项；`[SLIDE]` 锚点数 `M` 与页数 `N` 必须满足 `M <= N`，并输出 mapping 报告。

CI：GitHub Actions 使用 `ubuntu-24.04` + `actions/checkout@v7` + `actions/setup-python@v7`，执行 Python 语法检查、Markdown 链接检查和 32 项回归测试（Linux 上用 fake `ffprobe`，避免因缺少 ffmpeg 跳过）；不构建 Slidev，也不渲染 Manim。

## 开始一次新任务

> 最短路径：[guides/quickstart-episode.md](guides/quickstart-episode.md)。

1. 读 [CLAUDE.md](CLAUDE.md)、[workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)、[workflows/episode-pipeline.md](workflows/episode-pipeline.md) 和对应 guides；不要先读全部文件。
2. 新建 Episode：`tools/new-episode.ps1 -Name <slug> -Mode <course|technical|news|podcast>`。
3. 研究 **R1→R4 分轮**（来源 → 台账 → 知识结构 → 大纲），不要一次生成 `00`–`06`；R4 后跑 `--stage research`。
4. 讲稿 **S1→S3 分模块**（1–2 模块/轮，追加写入），同步写 `[SEGMENT]` 节奏标注；每批跑 `--stage script`。
5. Motion **M1→M3 逐段**：先冻结 `segments.json`，再一段一个 scene/project；每段跑 `--stage motion`，用 `motion-run.ps1` 打开 `record.html`。
6. 录制包：`build-recording-package.py` 生成 `05_recording/`；跑 `--stage recording`。
7. 课件：course 用 Reveal（`reveal-run.ps1`）；technical/news 用 Slidev；P1 骨架 → P2 填充，跑 `--stage slides`。
8. 终检：`tools/check-episode.py <slug> --mode <mode> --stage qa --strict`；修复到无 `Issues`。
9. 更新 `handoff.md` 后停下等确认；只在 C1–C7 检查点 `/clear`。
10. 交付说明区分已通过、未运行和仍需人工判断的部分；OBS 录制由人工完成。
11. Git 提交由人工确认；不提交密钥、PDF 全文、MP4、`.venv`、`node_modules`、`.pnpm-store`、`03_slides/.vendor/`、`05_recording/recordings/`。

新闻视频与纯音频播客使用同一套 Episode 流程，分别用 `--mode news` / `--mode podcast`；可跳过 Reveal/Slidev/Motion/Manim，但不能跳过来源登记与主张台账。分场景步骤见 [guides/episode-tutorial.md](guides/episode-tutorial.md)。

## 项目状态（2026-10-26）

框架已可用于新的 course episode；第一集 `transformer-self-attention` 已到**录制就绪**，等待人工 OBS 实拍与后期拼接。默认视觉已统一为麦肯锡橙白（见 [guides/delivery-quality.md](guides/delivery-quality.md)）。

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 框架文档 | `PASS_STATIC` | `CLAUDE.md`、编排器、流程、教程、链接检查 |
| Motion Canvas | `PASS_VERIFIED` | 3.17.2 + Vite 5.4.21；45s 示例 probe；`record.html` 可播 |
| Reveal 运行时 | `PASS_VERIFIED` | 6.0.2；`reveal-run` 同步/静态服务；data-slide/资源检查 |
| Slidev 运行时 | `PASS_VERIFIED` | `@slidev/cli 53.0.0`；technical/news/旧课 |
| Manim 运行时 | `PASS_VERIFIED`（legacy） | 0.22.0；仅兜底；≤20s |
| `check-episode.py` | `PASS_VERIFIED` | 分阶段检查；Motion/Reveal/Slidev/Manim；32 项回归 |
| `paper-search` | `PASS_VERIFIED` | CLI + Skill；**不是已注册 MCP** |
| `motion-isolation` | `PASS_VERIFIED` | 项目内 Skill 契约；45–90s Motion 主路径 |
| `manim-isolation` | `PASS_VERIFIED`（legacy） | 仅 `engine=manim` 兜底 |
| OBS 安装 | `NOT_RUN` | 人工确认安装；AI 不安装、不调用 |
| Playwright PDF 导出 | `NOT_RUN` | 未安装；不影响 Slidev dev/build |
| 第一集 `transformer-self-attention` | `PASS_VERIFIED`（内容/QA） | Motion 68s、Reveal 12 页、`05_recording` 就绪；`record_status=NOT_RUN`，待人工 OBS |
| OBS 实拍 / 后期 | `NOT_RUN` | 人工录制与拼接；不由 AI 调用 OBS |
| 新闻/播客模式 | `PASS_STATIC` | 脚手架与检查器已支持；未跑真实项目 |

现有活跃目录：`transformer-self-attention`（第一集，录制就绪）。研究输入样本：`attention-research-2026-10`（不是默认课程模板）。历史试点与旧课程已移入 `courses/_retired/`，仅作 legacy 对照，不参与当前主路径；详见 [courses/README.md](courses/README.md)。

## 当前能力与已知限制

可用：Motion Canvas 3.17.2 + Vite 5.4.21（课程内依赖）、Reveal.js 6.0.2（`tools/reveal-runtime`）、Slidev 53（technical/news/旧课）、Manim 0.22.0（仅兜底）、Node 24 / pnpm 10、ffmpeg 8、Chrome 浏览器验收、`motion-isolation` / `manim-isolation`、Python 数值核验、uv 独立环境、项目内 `paper-search`。

限制：OBS 未在常规路径检测到；没有 TTS 或自动剪辑；参考视频/部分技术文档可能无法访问；PDF 全文受网络与许可限制；Slidev PDF 导出需要的 Playwright 未安装；`paper-search` 不是已注册 MCP；人工教学评审和学习效果测试不在自动流程内。完整清单见 [guides/known-limitations.md](guides/known-limitations.md)；具体课程的限制记录在各自的 `qa/`。

## 规范索引

- [CLAUDE.md](CLAUDE.md)：Agent 出厂约定（先读编排规则、分块执行、停点）
- [guides/requirements.md](guides/requirements.md)：课程制作、QA、清理与 Git 的硬性要求
- [guides/editorial-voice.md](guides/editorial-voice.md)：中文技术写作与口播的编辑规范
- [guides/audience-vs-internal.md](guides/audience-vs-internal.md)：观众版、教学限定与内部 QA 的边界
- [guides/delivery-quality.md](guides/delivery-quality.md)：内容、准确性、视觉、可复现性与人工审查
- [guides/quickstart-episode.md](guides/quickstart-episode.md)：从零开一集的最短路径与开第二集前检查清单
- [guides/known-limitations.md](guides/known-limitations.md)：当前不阻塞项与未验证项
- [guides/episode-tutorial.md](guides/episode-tutorial.md)：课程 / 新闻 / 播客的分场景使用教程
- [guides/repository-and-remote.md](guides/repository-and-remote.md)：远程仓库、忽略规则、克隆重建与推送流程
- [courses/README.md](courses/README.md)：课程/新闻产物根目录、命名与两种布局
- [workflows/episode-pipeline.md](workflows/episode-pipeline.md)：默认流程（Motion Canvas + Reveal；Slidev technical；Manim 兜底）
- [workflows/claude-orchestrator.md](workflows/claude-orchestrator.md)：分块状态机、每轮模板、停点与 `/clear` 规则
- [workflows/course.md](workflows/course.md)：课程制作通用流程与兼容路径
- [workflows/pipeline-audit.md](workflows/pipeline-audit.md)：Episode 管线审计与修复记录
- [tools/README.md](tools/README.md)：工具清单、命令与环境边界
- [workflows/news-analysis.md](workflows/news-analysis.md)：新闻解读流程
- [workflows/technical-explainer.md](workflows/technical-explainer.md)：技术/论文解读流程
- [prompts/](prompts/)：任务入口模板
