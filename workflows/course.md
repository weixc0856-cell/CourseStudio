# Workflow — Course

适用于论文、教材、技术文档、系列资料转课程。产出是**可讲解、可复核的课程包**，不是自动生成的长视频。

**产物根目录**：`D:\CourseStudio\courses\<slug>`。命名与两种布局见 [courses/README.md](../courses/README.md)；五阶段管线的兼容性与缺陷见 [pipeline-audit.md](pipeline-audit.md)。

**新项目默认流程**：Episode + Slidev + Manim 隔离，见 [episode-pipeline.md](episode-pipeline.md)；分块状态机与停点见 [claude-orchestrator.md](claude-orchestrator.md)。本文件保留通用课程原则与 HTML 兼容路径。

本流程把两类工作分开：

- **研究输入**：来源、全文证据、主张台账、知识结构、课程输入简报。
- **课程生产**：设计、页面、动画、旁白、QA、交付。

没有完成研究 Gate，不进入页面和动画生产。

---

## 0. 两种仓库布局（先选一种）

| 布局 | 适用 | 做法 | 注意 |
| --- | --- | --- | --- |
| **A. 每课独立仓库（默认）** | 课程各自交付、独立历史 | `courses/<course>` 内 `git init`；根目录不作为仓库 | 使用 `tools/course.gitignore`；根 `.gitignore` 仅作兜底 |
| **B. 根目录单仓库** | 统一管理所有课程与工具 | 根目录 `git init`；课程作为子目录 | 不要保留嵌套 `.git`；需要时改用 submodule |

当前约定是 **A**。`tools/new-course.ps1` 会：

1. 创建独立 uv 项目与 `.venv`；
2. 安装锁定版本的 ManimCE；
3. 复制 [tools/course.gitignore](../tools/course.gitignore) 到课程根目录；
4. **不会**自动 `git init`、提交或推送。

根目录 [.gitignore](../.gitignore) 只在布局 B 生效；它同时作为“哪些文件永远不该进 Git”的说明。

---

## 1. 快速开始

```powershell
# 新建课程（独立环境 + .gitignore）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-course.ps1 -Name <course>
cd D:\CourseStudio\courses\<course>

# 由人工决定是否建仓
git init
git status --short

# 验证环境
uv run manim checkhealth
```

只做研究、不做页面时，可以建立独立的研究目录（例如 `courses/<topic>-research-YYYY-MM/`），把研究交付物放在根目录；正式课程统一放在 `research/` 下。

---

## 2. 读取顺序（低 Token）

1. 本文件。
2. [guides/editorial-voice.md](../guides/editorial-voice.md)。
3. [guides/audience-vs-internal.md](../guides/audience-vs-internal.md)。
4. [guides/delivery-quality.md](../guides/delivery-quality.md)。
5. Skill 的 `references/source-and-claims.md`、`references/teaching-design.md`。
6. 只有确实使用 Manim 时，读 Skill 的 `references/manim-workflow.md`。
7. 只有需要领域检查时，读 Skill 的 `references/domain-checks.md`。

如果已有完整研究包：**先读 `research/00`、`research/04`、`research/05`**；`02` 台账只按需检索，不线性通读。

不要一次加载整个 Skill 或整个项目。

---

## 3. 阶段

### 0. 工作区与仓库检查

- 当前目录、Git 状态、README、已有课程、工具版本。
- 目标课程目录是否已存在；不要覆盖。
- 确认采用布局 A 还是 B；不要在根仓库里嵌套普通 Git 仓库。
- 可用渲染、浏览器、网络和文档读取工具。
- 记录实际环境（命令、版本、退出码），不沿用旧结论。

**出口**：明确课程目录、仓库布局、可用工具；没有未处理的已有改动。

### 1. 编辑契约

写清：

- 受众与先备知识。
- 学习目标（可观察、可检查）。
- 核心问题。
- 范围与排除项。
- 目标时长与拆分（单讲/多讲）。
- 必需交付物。
- 高风险主张（需要额外核验）。

默认中文、面向好奇的非 specialist；用户指定则覆盖。

**出口**：契约写入 `design/learning-objectives.md` 或任务说明；范围无歧义。

### 2. 研究输入（关键阶段）

按课程体量选一条路径：

| 路径 | 适用 | 产物 |
| --- | --- | --- |
| **轻量** | 单一来源、短解读 | `research/source-register.md`、`research/claims-ledger.md` |
| **完整** | 技术课程、多来源、需要证据分级 | `research/00`–`06` 全套 + 台账 CSV + 引文核验 |

完整路径使用 `research-to-course-synthesis` Skill，建议目录：

```text
research/
├── 00-task-brief.md
├── 01-source-inventory.md
├── 02-claim-evidence-ledger.csv
├── 03-knowledge-structure.md
├── 04-course-input-brief.md
├── 05-quality-report.md
├── 06-course-outline.md
├── search-results/          # 检索原始 JSON（提交）
├── downloads/               # PDF（不提交）
├── fulltext/                # 逐页文本（不提交）
├── scripts/                 # 抽取、定位、核验脚本（提交）
├── claims.json
├── quote-verification.csv
├── extraction-report.json
├── metrics.json
└── qa-check.json
```

#### 2.1 检索

使用项目内 `paper-search`，显式记录检索式、来源、条数、时间：

```bash
P=/d/CourseStudio/tools/paper-search-mcp/bin/paper-search
$P search "<query>" -s fast -n 5 --source-timeout 30 > research/search-results/q01.json
```

- 优先原始论文与代表性后续研究；不要用模型记忆补来源。
- 0 结果时缩短检索式重试，并把失败记录留在 `01-source-inventory.md`。
- 不声称“系统综述/穷尽检索”，除非方法确实满足。

#### 2.2 全文获取与核验

```bash
$P download arxiv 1706.03762 -o research/downloads
```

- 下载状态必须记录（`ok` / 失败原因），不编造阅读结果。
- 需要页码级定位时，用 `pypdf` 抽取逐页文本；不要只用摘要。
- 可复用项目内已装环境，不往课程 `.venv` 里重复装工具：

```bash
/d/CourseStudio/tools/paper-search-mcp/.venv/Scripts/python.exe research/scripts/extract_pdf.py
```

#### 2.3 主张台账

- 每条关键主张分配稳定 `CLM-XXX`。
- 区分 `FACT` / `CLAIM` / `INFERENCE` / `ASSUMPTION` / `REPRODUCED_RESULT`。
- 记录证据状态、推理状态、执行状态、验证状态、冲突状态。
- 来源定位到页码/公式/表格；定位不到就标缺失，不编造。
- 冲突保留双方证据、定义与适用范围；不强行统一。

#### 2.4 研究 Gate（进入设计前必须检查）

| Gate | 检查 | 通过标准 |
| --- | --- | --- |
| G1 来源与范围 | 版本、访问状态、一手/二手、覆盖范围 | 来源身份可追溯；未超范围 |
| G2 证据与主张 | 每条关键主张有定位；作者主张有归属 | 引文核验率报告；冲突已记录 |
| G3 技术与逻辑 | 公式、维度、复杂度、实验条件 | 适用检查通过；未做的标 `PARTIAL`/`NOT_RUN` |

**出口**：`04-course-input-brief.md` + `06-course-outline.md` 可供下游直接使用；`05-quality-report.md` 写明未决项。未通过 G1/G2 不进入第 3 阶段。

### 3. 教学设计与分镜

- `design/learning-objectives.md`
- `design/lesson-outline.md`
- `design/visual-storyboard.md`

每个场景一个主要教学目标。说明画面、动画步骤、旁白、来源/主张、限定、过渡、录制注意。

**出口**：大纲覆盖全部学习目标；概念依赖顺序正确；每节有 `CLM` 标签或来源。

### 4. 共享事实基线

公式、数字、形状、符号、颜色映射只保留一个来源：

- 优先一个共享模块（如 `animations/manim/attention_example.py`）。
- 用脚本核验（独立实现/手算交叉核对）。
- 页面、旁白、动画、图表引用同一组值。
- 任何改动先改基线，再改产物，再重跑一致性检查。

**出口**：基线脚本可运行；页面/旁白/动画引用同一组值。

### 5. 生产

HTML：

- 固定 16:9 舞台；每页一个主要教学目标。
- 章节、静态图、导航、总结、自测。
- 不依赖未确认的 CDN/外部运行时。

Manim：

- 只做适合时间演化的机制、数据流、几何/矩阵变换。
- 少量高质量场景，不以数量为目标。
- 先低质量预览；审查后再正式渲染。
- 记录场景源码、命令、版本、输出路径。

旁白：

- 与页面分开写；解释画面，不逐字复述。
- 遵循 [guides/editorial-voice.md](../guides/editorial-voice.md)。
- 技术限定条件保留。

**出口**：页面可浏览；动画有低质量预览；旁白与画面一致。

### 6. 观众版与内部 QA 分层

- 观众版只放理解所需内容、必要限定、可读来源。
- 失败记录、未跑测试、claim ID、路径、渲染元数据放 `qa/` 和 `research/`。
- 最后一页是继续阅读或观众相关范围，不是审计清单。
- 详细规则见 [guides/audience-vs-internal.md](../guides/audience-vs-internal.md)。

**出口**：观众版不含内部审计字段；内部材料可追溯。

### 7. 预览与 QA

- 抽帧检查动画：开头、中间、结尾、最终态。
- 浏览器检查：逐页布局、导航、视频、控制台。
- 数值/一致性检查：公式、数字、形状、页面/旁白/动画。
- 观众版泄漏扫描。
- 内容审阅：来源覆盖、限定、反证。
- 链接检查：`python tools/check-links.py courses/<course>`。
- 记录命令、退出码、结果、未执行项。

**自动修复循环**：发现问题 → 记录 → 修来源/主张/内容 → 重跑受影响的检查 → 在 `qa/` 记录修复前后状态。不得删证据、改状态、无限重跑。

**出口**：QA 报告区分 `PASS_VERIFIED` / `PASS_STATIC` / `PARTIAL` / `NOT_RUN` / `FAIL`。

### 8. 正式渲染

- 只对内容/视觉审查通过且受影响的场景做正式渲染。
- 改了屏幕文字/公式/布局/动画才重渲染；纯口播改动不触发重渲染。
- 渲染后重新抽帧检查实际产物。
- 记录命令、版本、输出路径；渲染产物默认不进 Git。

**出口**：成片与预览一致；抽帧检查通过。

### 9. 交付

- `README.md`、研究材料、设计、页面、动画、口播、QA。
- 状态区分 `PASS_VERIFIED` / `PASS_STATIC` / `PARTIAL` / `NOT_RUN` / `FAIL`。
- 不自动提交 Git、推送或发布。
- 没有人工教学评估时，不宣称教学效果已验证。
- 大体积成片、授权素材放仓库外或 Git LFS；普通 Git 历史只保留源码与文本。

**出口**：交付 README 能独立说明“已完成/未完成/限制”。

### 10. Git 与交接

- 人工确认 `git status --short` 后再提交；不自动提交、不自动推送。
- 提交前检查：没有 `.env`、密钥、PDF 全文、抽取文本、渲染视频、`.venv`、缓存。
- 建议提交粒度：研究输入、设计、生产、QA、交付各一次；提交信息带课程名。
- 交接包：课程路径、当前状态、已运行命令、未决事项、下一步。

**出口**：工作区干净；交接说明可让下一次会话直接继续。

---

## 4. 产物与 Git 边界

| 类别 | 例子 | Git |
| --- | --- | --- |
| 源码与配置 | `course/index.html`、`animations/manim/*.py`、`scripts/*`、`pyproject.toml`、`uv.lock`、`.python-version` | **提交** |
| 研究与设计文本 | `research/00`–`06`、台账 CSV、`design/*.md`、口播稿 | **提交** |
| 检索与核验记录 | `search-results/*.json`、`claims.json`、`quote-verification.csv`、`extraction-report.json`、`metrics.json`、`qa-check.json` | **提交** |
| PDF 全文 | `research/downloads/*.pdf` | 不提交（体积/许可） |
| 抽取文本 | `research/fulltext/` | 不提交（可重建） |
| 渲染与媒体 | `animations/rendered/`、`media/`、`*.mp4/*.mov/*.wav` | 不提交（大文件） |
| 环境与缓存 | `.venv/`、`.uv-cache/`、`__pycache__/`、`node_modules/` | 不提交 |
| 浏览器/QA 中间件 | `qa/chrome-profile*/`、`qa/rendered-frames/`、`*.har` | 不提交 |
| 密钥与本地配置 | `.env`、`*.key`、`.mcp.json`、`CLAUDE.local.md` | 不提交 |

忽略规则：

- 根目录：`D:\CourseStudio\.gitignore`
- 课程模板：`D:\CourseStudio\tools\course.gitignore`
- 新课程由 `new-course.ps1` 自动复制模板；已有课程已安装同一份。

---

## 5. 最低产物

> Episode + Slidev 默认布局的最低产物见 [episode-pipeline.md](episode-pipeline.md) 第 1 节；下面是通用/HTML 兼容布局。

```text
course-project/
├── README.md
├── .gitignore
├── pyproject.toml
├── uv.lock
├── .python-version
├── course/index.html
├── research/
│   ├── 00-task-brief.md          # 完整路径
│   ├── 01-source-inventory.md
│   ├── 02-claim-evidence-ledger.csv
│   ├── 03-knowledge-structure.md
│   ├── 04-course-input-brief.md
│   ├── 05-quality-report.md
│   ├── 06-course-outline.md
│   ├── search-results/
│   └── scripts/
├── design/
│   ├── learning-objectives.md
│   ├── lesson-outline.md
│   └── visual-storyboard.md
├── scripts/narration.md
├── animations/manim/
├── animations/rendered/          # 不提交
└── qa/
```

轻量路径可只保留 `source-register.md` 与 `claims-ledger.md`；但同样要区分事实、作者主张与推断。

---

## 6. 完成定义（Definition of Done）

- [ ] 编辑契约与学习目标已写清。
- [ ] 研究 Gate G1/G2 通过；G3 的 `PARTIAL`/`NOT_RUN` 已披露。
- [ ] 每条关键主张有 `CLM` 或来源定位。
- [ ] 设计与分镜覆盖全部目标。
- [ ] 共享事实基线唯一，且通过一致性检查。
- [ ] 页面可浏览，16:9，导航正常。
- [ ] 动画预览通过抽帧检查；只对受影响场景正式渲染。
- [ ] 旁白与画面一致，技术限定保留。
- [ ] 观众版无内部 QA 泄漏。
- [ ] QA 报告列出命令、退出码、状态、未执行项。
- [ ] `git status` 干净；未提交密钥/PDF/渲染产物。
- [ ] README 能独立说明交付范围与限制。

---

## 7. 命令模板

```powershell
# 新建课程
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-course.ps1 -Name <course>
cd D:\CourseStudio\courses\<course>
uv run manim checkhealth

# 生产与核验
uv run python scripts/verify_<topic>.py
uv run python scripts/check_consistency.py
node qa/browser_check.mjs

# 链接检查（在 D:\CourseStudio 下）
python tools/check-links.py courses/<course>
```

```bash
# 研究检索与下载
P=/d/CourseStudio/tools/paper-search-mcp/bin/paper-search
$P search "<query>" -s fast -n 5 --source-timeout 30 > research/search-results/q01.json
$P download arxiv 1706.03762 -o research/downloads

# 逐页抽取（使用已装好的环境，不新装工具）
/d/CourseStudio/tools/paper-search-mcp/.venv/Scripts/python.exe research/scripts/extract_pdf.py
```

```bash
# Git 只做人工确认后的操作
git status --short
git check-ignore -v research/downloads
git add <files>
git commit -m "course(<name>): <stage>"
```

---

## 8. 硬性规则

- 先研究，再写脚本、页面和动画。
- 不把程序检查通过等同于内容正确或教学有效。
- 不把内部 QA 状态写进观众版。
- 不自动 TTS、不自动拼长视频、不自动发布。
- 不自动 `git init`、提交、推送；提交前由人工确认。
- 不提交 `.env`、密钥、PDF 全文、抽取文本、渲染视频、`.venv`、缓存。
- 保留 `uv.lock` 与 `.python-version`；不要为了“干净”忽略可复现性文件。
- 修改前检查文件和 Git 状态，保留用户已有改动。
