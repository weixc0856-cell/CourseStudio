# 五阶段管线兼容性审计

- **审计日期**：2026-10-26
- **产物根目录**：`D:\CourseStudio\courses\`（课程、新闻、技术解读统一放这里）
- **审计对象**：`paper-search`、`research-to-course-synthesis`、`course-studio`、`slidev`、`manim-isolation`，以及 Manim / Slidev / OBS / ffmpeg / Chrome 等运行时
- **总体结论**：`PARTIAL`。研究阶段可完整跑通；脚本与 HTML/Manim 阶段可用；Slidev 运行时缺失；`manim-isolation` 不能作为独立 Skill 安装；paper-search 不是已注册的 MCP 服务。

## 0. 2026-10-26 修复状态（方案 2+3 落地）

| 缺陷 | 状态 | 处理 |
| --- | --- | --- |
| D-01 `manim-isolation` 缺失/重名 | **FIXED** | 新建 `tools/skills/manim-isolation`，frontmatter `name: manim-isolation`；全局 junction 已建立 |
| D-02 paper-search 非 MCP | **DEFERRED** | 继续使用已验证的 CLI + Skill；MCP 注册未做（非必需） |
| D-03 Slidev 运行时缺失 | **FIXED** | `tools/slidev-runtime` 本地安装 `@slidev/cli 53.0.0`；`markdown-it` 锁定 14.1.0；build/dev/public 资源均通过 |
| D-04 三套目录契约 | **FIXED** | Episode 布局定为新项目默认，见 [episode-pipeline.md](episode-pipeline.md) |
| D-05 研究命名不一致 | **FIXED** | 别名表写入 `courses/README.md` 与 Episode 流程 |
| D-06 讲稿无强制锚点 | **FIXED** | 强制 `[SLIDE: NN]` / `[ANIMATION: name]`；新增 `tools/check-episode.py` |
| D-07 Slidev vs HTML 冲突 | **FIXED** | Episode 流程固定 Slidev；`course-studio` 的 prompt 覆盖默认 HTML |
| D-08 版本漂移 | **MITIGATED** | 保留已安装 `course-studio`；不再安装旧 ZIP；版本记录在 `tools/slidev-runtime/README.md` |
| D-09 无阶段交接 | **FIXED** | `handoff.md` 模板与 `/clear` 协议 |
| D-10 无锚点校验 | **FIXED** | `tools/check-episode.py` |
| D-11 OBS 无清单 | **PARTIAL** | 流程写入 OBS 步骤；实际检查清单仍需人工固化为 `qa/recording-checklist.md` |
| D-12 Skill 副本非链接 | **PARTIAL** | `manim-isolation`、`paper-search` 用 junction；其余仍是副本 |
| D-13 Episode 忽略规则 | **FIXED** | `.gitignore` 与课程模板已覆盖 |

新增工具与文件：

- `tools/slidev-runtime/`：项目内 Slidev 运行时（node_modules 不入库）
- `tools/skills/manim-isolation/`：独立 Manim 隔离 Skill
- `tools/episode-template/`：Episode 目录模板
- `tools/new-episode.ps1`：建集脚手架（本地 `.venv` + Manim）
- `tools/slidev-run.ps1`：用共享运行时启动/构建 Slidev
- `tools/render-manim.ps1`：用项目 `.venv` 渲染并把 MP4 放入 `03_slides/public/`
- `tools/check-episode.py`：锚点、页数、场景、MP4 检查

本轮实际验证：

| 项目 | 状态 | 证据 |
| --- | --- | --- |
| Slidev 构建 | `PASS_VERIFIED` | `dist/index.html` 生成 |
| Slidev 开发服务器 | `PASS_VERIFIED` | `http://localhost:3031/` 可访问 |
| Slidev public 资源 | `PASS_VERIFIED` | `public/anim.mp4` 进入 `dist/` |
| Manim 渲染 | `PASS_VERIFIED` | `480p15/smoke.mp4` 生成 |
| `new-episode.ps1 -SkipManim` | `PASS_VERIFIED` | 临时 fixture 目录生成 |
| `new-episode.ps1`（含 Manim） | `PASS_VERIFIED` | Python 3.12 `.venv` + Manim 0.22.0 安装成功 |
| `check-episode.py` | `PASS_VERIFIED` | 普通锚点、防逃逸、禁用 API、podcast 模式 fixture 均按预期 |
| `slidev-run.ps1 -Mode build` | `PASS_VERIFIED` | fixture 构建成功并复制 MP4 |
| `render-manim.ps1` | `PASS_VERIFIED` | fixture 渲染 12,496 字节 MP4；3 秒超时杀掉进程树，无孤儿进程 |
| `manim-isolation` Skill | `PASS_VERIFIED` | 已出现在可用 Skill 列表 |
| Slidev pnpm store | `PASS_VERIFIED` | 从 `D:\.pnpm-store` 迁入 `tools/slidev-runtime/.pnpm-store` |
| OBS | `NOT_RUN` | 常规路径未检测到 |

### v1.1 增量（2026-10-26 晚）

- **锚点防逃逸**：`check-episode.py` 检测被代码块、引用块、HTML 注释包裹的 `[SLIDE]`/`[ANIMATION]`，判 FAIL。
- **Manim API 锁**：静态检查 `manimlib`、`ThreeDScene`、`Camera3D`、`ThreeDAxes`、`ParametricSurface`、粒子等禁用项。
- **时长上限**：按声明的 `run_time`/`wait` 估算，超过 20 秒判 FAIL。
- **渲染超时**：`render-manim.ps1 -TimeoutSeconds` 默认 180 秒，超时 `taskkill /T` 杀进程树。
- **Python 版本**：`new-episode.ps1` 增加 `uv python pin 3.12`，避免误用 3.14。
- **模式支持**：`check-episode.py --mode course|technical|news|podcast`；新闻/播客可无 Slidev/Manim。
- **OBS 高容错**：允许口误、停顿 2 秒重念、后期剪辑；不再要求完美掐点。
- **教程**：[guides/episode-tutorial.md](../guides/episode-tutorial.md)。

### v1.2 增量（分块状态机）

- **状态机**：新增 [claude-orchestrator.md](claude-orchestrator.md)，每次只推进一个子步骤，写完即检查，检查完即停。
- **阶段检查**：`check-episode.py --stage research|script|slides|manim|qa`；中间阶段不误报缺失 MP4。
- **分块生成**：讲稿按大纲模块 1–2 个/轮；Slidev 先骨架后填充；Manim 只做 1–2 个核心锚点。
- **交接字段**：`handoff.md` 增加阶段、子步骤、模块进度、动画进度、最后检查。
- **教程重写**：研究 R1–R4、讲稿 S1–S3、课件 P1–P2、动画 M1–M2、终检 Q1–Q2 的分轮 prompt。

## 1. 名称归一化结果

方法：扫描 `%USERPROFILE%\.claude\skills\*\SKILL.md` 的 `name:` 字段；对 ZIP 解包后比对文件；解析 `%USERPROFILE%\.claude.json` 的 `mcpServers`；用命令探测运行时。

| 管线中的名称 / ZIP | 实际安装位置 | Skill 调用名 | 状态 | 依据 |
| --- | --- | --- | --- | --- |
| `paper-search-mcp-main.zip` | `D:\CourseStudio\tools\paper-search-mcp` | `paper-search`（全局 junction） | **可用（CLI/Skill）** | `sources` 返回 25 个来源；检索/下载已实际使用 |
| `research-to-course-synthesis-ccswitch.zip` | `~\.claude\skills\research-to-course-synthesis` | `research-to-course-synthesis` | **可用** | ZIP 与已安装目录 `diff -rq` 无差异；11 篇来源的 00–06 包已实际产出 |
| `course-studio-skill.zip` | `~\.claude\skills\course-studio-skill` | `course-studio` | **可用（未端到端执行）** | 已安装版本比 ZIP 新；5 个 reference 全部存在 |
| `course-studio-skill-manim-isolation-v1.1.zip` | **未安装** | 无 | **BLOCKED（不能按名称调用）** | ZIP 内 `name: course-studio`，是旧版 course-studio 副本，不是独立 `manim-isolation` Skill |
| `slidev-main.zip` | `~\.claude\skills\slidev`（Skill 另装） | `slidev` | **PARTIAL** | ZIP 是 Slidev 框架源码 v53.0.0，不是 Skill；Skill 已安装且 53 个 reference 完整；`slidev` CLI 未安装 |
| `humanizer-main.zip` | `~\.claude\skills\humanizer-main` | `humanizer` | **可用（可选）** | frontmatter `name: humanizer` |
| `frontend-slides-main`（未在管线中列出） | `~\.claude\skills\frontend-slides-main` | `frontend-slides` | **可用替代** | 零依赖 HTML 课件，已安装 |

**命名结论**：调用时必须使用 `course-studio`，不是 `course-studio-skill`；`humanizer` 不是 `humanizer-main`；`slidev` 不是 `slidev-main`。

## 2. 五阶段状态矩阵

| 阶段 | 期望工具/Skill | 实际状态 | 说明 |
| --- | --- | --- | --- |
| 阶段一：检索 | paper-search MCP | `PARTIAL` | 已注册 MCP 只有 `mcp-image` / `Stitch`；paper-search 是 CLI + Skill，不是 MCP 工具 |
| 阶段一：研究清洗 | research-to-course-synthesis | `PASS_VERIFIED` | 已用 11 篇全文实际跑通 00–06、46 条主张、91/91 定位 |
| 阶段二：讲稿 | course-studio | `PASS_STATIC` | Skill 已注册，references 完整；本审计未运行完整讲稿生产 |
| 阶段二：润色 | humanizer | `PASS_STATIC` | 可选；本次未调用 |
| 阶段三：静态课件 | slidev | `PARTIAL` | Skill 完整；`slidev` CLI、项目依赖未安装；无 `package.json` / `slides.md` |
| 阶段三：动画 | course-studio + Manim | `PASS_VERIFIED`（运行时） | `courses/transformer-course-pilot/.venv` 中 Manim 0.22.0 可执行 |
| 阶段三：动画隔离 | manim-isolation | `BLOCKED` | 没有独立 Skill；ZIP 不是隔离 Skill，且与 `course-studio` 重名 |
| 阶段四：录制 | OBS | `NOT_RUN` | 未在 PATH、Program Files、LocalAppData 常规路径检测到 `obs64.exe`；需人工确认 |
| 辅助：视频处理 | ffmpeg | `PASS_VERIFIED` | 8.1 可用 |
| 辅助：浏览器验收 | Chrome | `PASS_VERIFIED` | 默认路径存在 |
| 辅助：Node/Slidev 前置 | Node/npm/pnpm | `PASS_VERIFIED` | Node 24.14.1、npm 11.11.0、pnpm 10.34.1 |

## 3. 主要缺陷

### P0 — 会直接阻断管线

**D-01 `manim-isolation` 不能作为独立 Skill 调用**

- ZIP `course-studio-skill-manim-isolation-v1.1.zip` 解包后只有 `course-studio-skill/`，`SKILL.md` 的 `name:` 是 `course-studio`。
- 已安装的 `course-studio` 比该 ZIP 新：多了任务路由、观众/内部分层规则、`references/manim-workflow.md` 与 Manim Runtime Isolation Policy。
- 若把 ZIP 装到 `~/.claude/skills/manim-isolation`，会出现同名 Skill 冲突，或被当成重复的 `course-studio`；它不是“只做 Manim 的隔离舱”。
- **影响**：按管线原文“必须调用 Skill 5”无法执行。
- **建议**：不要安装该 ZIP。Manim 隔离能力已经在 `course-studio` 的 `references/manim-workflow.md` 中；如确需独立 Skill，应新建一个 `name: manim-isolation` 的最小 Skill，只包含运行时隔离、场景输入/输出契约和渲染验收，不复制整套 course-studio。

**D-02 paper-search 不是已注册的 MCP 服务**

- `%USERPROFILE%\.claude.json` 顶层 `mcpServers` 只有 `mcp-image`、`Stitch`；`claude mcp list` 也没有 paper-search。
- 实际可用的是 `D:\CourseStudio\tools\paper-search-mcp\bin\paper-search` CLI，以及全局 `paper-search` Skill。
- **影响**：如果管线要求“MCP 工具调用”，该环节不成立；CLI/Skill 环节本身可用。
- **建议**：二选一——继续用 CLI/Skill（推荐，已验证），或显式注册 stdio MCP 服务。

**D-03 Slidev 运行时未安装**

- `slidev` Skill 已安装，53 个 reference 无缺失；但系统没有 `slidev` 可执行文件，课程目录也没有 `package.json` / `slides.md`。
- `npx --no-install slidev` 失败；`slidev-main.zip` 是框架源码（v53.0.0），不是可直接演示的课件工程。
- Node 24、npm 11、pnpm 10 满足创建项目的前置条件。
- **影响**：阶段三的 Slidev 排版无法立即执行；可以安装，但需要网络与项目级依赖。
- **建议**：若确定用 Slidev，先在 `03_slides/` 内用 `pnpm create slidev` 建项目（会产生 `node_modules/`，已被忽略）；否则改用已安装的 `frontend-slides` 或现有 HTML/CSS 路径。

### P1 — 会造成返工或产物不一致

**D-04 三套目录契约互相冲突**

- 管线原文：`00_raw_materials/`、`01_research/`、`02_scripts/`、`03_slides/`、`04_manim_src/`。
- `course-studio` 默认：`sources/`、`research/source-register.md`、`research/claim-ledger.md`、`docs/`、`course/index.html`、`animations/`、`scripts/speaker-notes.md`、`qa/`。
- 当前 `workflows/course.md`：`research/00–06`、`design/`、`course/`、`scripts/narration.md`、`animations/`、`qa/`。
- **影响**：同一门课在不同 Skill 下会生成不同路径，下游找不到输入。
- **建议**：每个项目开工前只选一种布局；跨布局时使用 `courses/README.md` 的映射表，不混用。默认推荐 CourseStudio 布局。

**D-05 研究输出命名与管线预期不一致**

- 管线预期：`01_research/evidence_ledger.csv`、`knowledge_structure.md`、`course-input-brief.md`。
- 实际 Skill：`02-claim-evidence-ledger.csv`（Core 14 字段）、`03-knowledge-structure.md`、`04-course-input-brief.md`，另有 `00/01/05/06`。
- **影响**：按文件名直接查找会失败；需要正则/别名映射。
- **建议**：建立固定别名：
  - `evidence_ledger.csv` → `02-claim-evidence-ledger.csv`
  - `knowledge_structure.md` → `03-knowledge-structure.md`
  - `course-input-brief.md` → `04-course-input-brief.md`

**D-06 course-studio 的讲稿契约与管线预期不一致**

- 管线预期：`02_scripts/lecture_script.md`，并要求 `[👀 视觉触发：…]`、`[🎬 播放 Manim：…]` 锚点。
- `course-studio` 默认：`scripts/speaker-notes.md`，要求“narration script aligned to scene IDs”，但没有强制的视觉锚点语法。
- **影响**：脚本阶段不会自动产出 Slidev 与 Manim 可消费的锚点。
- **建议**：在项目内增加 `scripts/anchor-convention.md` 或在讲稿模板中固定两种锚点；stage 3 只按锚点消费，不自行改写讲稿。

**D-07 course-studio 与 Slidev 的框架指引冲突**

- `course-studio` 明确说 Slidev 是可选，且“不要无具体收益就引入第二套演示框架”；默认交付是 `course/index.html`。
- 管线原文则强制 Slidev 作为阶段三唯一排版引擎。
- **影响**：Skill 会倾向生成 HTML，而不是 `03_slides/slides.md`。
- **建议**：在项目 brief 中明确写“本课程使用 Slidev，禁止生成 HTML 课件”，把冲突变成显式约束；否则默认走 HTML + `frontend-slides`。

**D-08 安装版本与 ZIP 版本漂移**

- `research-to-course-synthesis`：ZIP 与已安装完全一致。
- `course-studio`：已安装版本比 `course-studio-skill.zip` 与 `manim-isolation-v1.1.zip` 都新；两个 ZIP 都缺少任务路由、观众/内部分层规则。
- Skill 目录是普通复制，不是 symlink/junction（只有 `paper-search` 是 junction）。
- **影响**：再次“按 ZIP 安装”会回退能力；更新不会自动同步。
- **建议**：以已安装目录为准；记录版本/校验和；更新前先 diff。

**D-09 阶段之间没有机器可读的交接契约**

- 管线依赖人工 `/clear`；清空后没有统一 manifest 说明上一阶段产物、版本、状态、未决项。
- **影响**：下一阶段可能读错文件或重复研究；失败状态容易丢失。
- **建议**：每个阶段输出一个 `handoff.md`（或 `handoff.json`），至少包含：stage、输入文件、输出文件、命令、状态、未决项、下一步。`/clear` 前先写。

### P2 — 影响效率或可维护性

**D-10 没有视觉锚点的强制校验**

- 当前没有脚本检查“讲稿锚点 ↔ Slidev 页面 / Manim 视频”是否一一对应。
- **建议**：加一个轻量检查器，扫描 `[👀 …]` 与 `[🎬 …]`，对照 `slides.md` 的页标题与 `public/*.mp4` 文件名。

**D-11 OBS 录制没有检查清单**

- OBS 未在常规路径检测到；即使安装，也没有“场景顺序、分辨率、麦克风、备份录制”的固定清单。
- **建议**：在 `qa/recording-checklist.md` 固化：1920×1080、30/60fps、麦克风电平、逐场景切换、备份、录制后抽帧核对。

**D-12 技能目录是复制而非链接**

- `course-studio-skill`、`research-to-course-synthesis`、`slidev`、`humanizer-main` 都是普通目录；只有 `paper-search` 是 junction。
- **影响**：ZIP 更新不会反映到已安装 Skill；多份副本容易漂移。
- **建议**：统一用“版本化目录 + 校验和”，或改为 junction/symlink（Windows 需开发者模式或 junction）。

**D-13 `.gitignore` 原不覆盖 Episode 布局**

- 已在本审计中补充：`00_raw_materials/**/*.pdf`、`01_research/downloads/`、`03_slides/public/*.mp4`、`04_manim_src/media/` 等。
- 现在两种布局都能避免把 PDF、视频、Manim 中间产物提交进 Git。

## 4. 推荐的标准管线

```text
D:\CourseStudio\courses\<slug>\
  ├── 00 工作区与契约        → README / design brief
  ├── 01 研究输入            → paper-search + research-to-course-synthesis
  ├── 02 讲稿                → course-studio（+ humanizer 可选）
  ├── 03 视觉                → Slidev 或 frontend-slides + Manim
  ├── 04 合成                → OBS 人工录制
  └── 05 QA/交付             → qa/ + README
```

阶段 Gate：

| Gate | 通过条件 | 不通过时 |
| --- | --- | --- |
| G1 研究 | 来源可追溯；关键主张有定位；冲突与未决项已记录 | 不写讲稿 |
| G2 讲稿 | 学习目标覆盖；每段有来源/主张；视觉锚点完整 | 不做页面 |
| G3 视觉 | 每个锚点有对应页面或视频；Manim 渲染实际通过 | 不进入录制 |
| G4 录制 | 16:9、音画同步、抽帧核对 | 不交付 |

## 5. 本审计实际执行与未执行

**已执行**：

- 扫描全局 Skill frontmatter，建立目录名 → 调用名映射。
- 解包并 diff：`research-to-course-synthesis`、`course-studio`、`manim-isolation`、`slidev-main`。
- 检查 Skill reference 完整性：`course-studio` 5/5、`slidev` 53/53。
- 解析 Claude MCP 配置；运行 `claude mcp list`。
- `paper-search sources` 冒烟（25 个来源）。
- `manim --version`（0.22.0）、Node/npm/pnpm、ffmpeg、Chrome、OBS 路径探测。
- `.gitignore` 增补 Episode 布局并做临时仓库忽略测试。

**未执行（`NOT_RUN`）**：

- 用 Slidev 创建并渲染一个真实 deck。
- 用 `manim-isolation` 渲染一个场景（该 Skill 不存在）。
- 用 OBS 录制。
- 五阶段端到端跑完一门新课程。
- 对 `course-studio` 做完整讲稿/页面生产。

**结论**：研究阶段可以立即开始；讲稿阶段可以用 `course-studio`；视觉阶段必须先决定 Slidev 还是 HTML，并解决 D-01/D-03。当前不建议按管线原文直接开工。
