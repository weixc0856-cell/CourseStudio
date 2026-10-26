# CourseStudio Decision Log — R1

- **状态**：全部为 `PROPOSED`，未获负责人批准。
- **规则**：本文件中的“推荐方案”只是设计建议，不构成已批准的架构选择。R1 文档使用的临时假设在每项末尾标注；临时假设不改变现有生产工具。
- **配套**：[pipeline-contract.md](pipeline-contract.md)、[status-model.md](status-model.md)、[migration-map.md](migration-map.md)。

---

## D-01 仓库拓扑

- **当前事实**：文档称“每课独立仓库、根仓库只跟踪框架”（`guides/requirements.md:15,198`；`workflows/course.md:22`），但实际没有任何课程嵌套 `.git`；根仓库跟踪 `courses/transformer-self-attention/` 的 41 个文件；`new-episode.ps1` 明确不执行 `git init`。`R0-engineering-audit.md` 已记录该矛盾。
- **可选方案**：
  1. 根仓库 + 课程白名单（现状事实化）
  2. 每课独立仓库（文档化 + 脚手架自动 `git init`）
  3. 根仓库 + submodule
- **推荐**：方案 1（短期）→ 方案 3（长期，若课程数量增长）。理由：迁移成本最低，不破坏现有历史；submodule 可后续按课程逐个引入。
- **成本/风险**：方案 1 使根仓库体积随课程增长；方案 2 会产生嵌套仓库/多远端管理；方案 3 需要所有协作者理解 submodule。
- **可逆性**：高。方案 1 可随时拆分为独立仓库；历史可通过 `git subtree split` 保留。
- **需批准**：是。影响 Git 历史、CI、备份与发布。
- **R1 临时假设**：拓扑中性；契约只要求 `episode.json` 与产物路径，不规定仓库边界。

## D-02 Reveal 与 Slidev 的职责边界

- **当前事实**：`course` 默认 Reveal（`03_slides/index.html`）；`technical`/`news`/旧课默认 Slidev（`03_slides/slides.md`）。Reveal 6.0.2 与 Slidev 53.0.0 均已安装；Reveal 路径没有构建步骤，strict QA 跳过 build；Slidev 路径 strict QA 会实际 build。
- **可选方案**：
  1. 保持双轨（course=Reveal，technical/news=Slidev）
  2. 全部统一到 Reveal
  3. 全部统一到 Slidev
- **推荐**：方案 1。理由：已有真实课程与运行时；双轨的成本主要是检查器分支，而不是内容生产。
- **成本/风险**：两套模板/两套检查/两套视觉规范；用户需要理解模式差异。统一可降低维护，但要重写现有课程和运行时。
- **可逆性**：中。切换默认需要迁移课件与 QA。
- **需批准**：是。
- **R1 临时假设**：保持现状；契约用 `deck_kind` 区分，不把任一框架写成唯一。

## D-03 Motion Canvas 主路径与 Manim 可选定位

- **当前事实**：Motion 3.17.2 + Vite 5.4.21 已安装，真实课程有 68s 段落；Manim 0.22.0 文档声明但当前机器未安装，无活跃 `.venv`。Manim 在 `segments.json` 中仅 `engine=manim` 时使用。
- **可选方案**：
  1. Motion 主路径 + Manim 可选 adapter（现状）
  2. 只保留 Motion，退役 Manim
  3. 恢复 Manim 为主路径
- **推荐**：方案 1，但把 Manim 标为“未安装、需显式安装”的可选 adapter；不建议现在退役，因为旧课程仍引用。
- **成本/风险**：Manim 维护/安装成本；不安装时 `engine=manim` 会 BLOCKED。退役会破坏旧课程对照。
- **可逆性**：高。Manim 可按课程启用/禁用。
- **需批准**：是（是否保留 Manim 作为支持能力）。
- **R1 临时假设**：Motion 主路径；Manim `NOT_RUN` 且不作为默认。

## D-04 Skill 的仓库内版本控制与分发

- **当前事实**：`course-studio`、`research-to-course-synthesis` 只在 `~/.claude/skills`；仓库内只有 `motion-isolation`/`manim-isolation`；`motion-isolation` 未注册，`manim-isolation` 已注册。`paper-search` 是 junction。
- **可选方案**：
  1. 核心 Skill 全部 vendored 到仓库，安装脚本创建 junction
  2. 保持外部，仓库记录 commit/hash（`skills.lock`）
  3. 使用 Claude Code plugin/市场分发
- **推荐**：方案 1 + `skills.lock` 校验。理由：干净环境可复现；版本可审计；不依赖用户级配置。
- **成本/风险**：仓库增加 Skill 副本；需要同步机制；junction 在 Windows 之外的平台需要替代。
- **可逆性**：高。可随时改回外部依赖。
- **需批准**：是。涉及用户级配置与分发方式。
- **R1 临时假设**：契约只引用 Skill 名称与版本，不假设安装位置；R2 再选分发。

## D-05 研究台账 Schema（Core 14 / 15 字段）

- **当前事实**：研究 Skill 列出的字段名有 15 个；`attention-research-2026-10` 表头 15 列；真实课程 `transformer-self-attention` 只有 8 列，但 README 写“15 列”、质量报告写“8 字段”。
- **可选方案**：
  1. 采用 15 字段 Claim Ledger v1（推荐）
  2. 采用 14 字段（需删除/合并某个字段）
  3. 承认 8 字段简化版，修改 Skill 与文档
- **推荐**：方案 1。理由：只有 15 字段版本有真实样本和完整字段列表；14 字段没有可执行定义；8 字段缺少证据/验证/冲突状态，无法满足可追溯要求。
- **成本/风险**：需要迁移 14 条主张；需要人工补 `evidence_status`/`reasoning_status`/`validation_status`/`conflict_status`/`used_in_artifact`，不能自动编造。
- **可逆性**：中。字段迁移可保留旧 CSV，双读一段时间。
- **需批准**：是。影响研究产物与 Skill。
- **R1 临时假设**：15 字段为 canonical；旧 8 列只读兼容；迁移未执行。

## D-06 课程状态模型

- **当前事实**：旧模型用单一 `PASS_VERIFIED`，但 strict QA 在 `Build: SKIPPED`、`real=NOT_VERIFIED` 时仍输出 `PASS_VERIFIED`；warnings 不阻断。
- **可选方案**：
  1. 五维状态（STRUCTURAL/RUNTIME/HUMAN/RECORDING/DELIVERY）+ 阶段 gate
  2. 保留单一状态，但增加子字段
  3. 只分“机器/人工”两类
- **推荐**：方案 1。理由：能表达“结构通过但运行时没跑”“运行时通过但人未验收”等真实状态；规则可机器判定。
- **成本/风险**：需要改 checker 输出、handoff、CI 与文档；旧状态需要兼容映射。
- **可逆性**：高。可保留旧输出作为兼容字段。
- **需批准**：是。
- **R1 临时假设**：五维模型作为设计目标；生产仍输出旧状态。

## D-07 运行时 QA 的执行范围

- **当前事实**：Reveal 路径无构建/浏览器检查；Motion 无 typecheck/probe gate；Slidev 只在 strict QA 的 technical/news 路径 build；Playwright 未安装；Chrome、ffmpeg、Node、pnpm 可用。
- **可选方案**：
  1. 最小运行时：typecheck + Reveal 静态服务/Chrome 加载 + Motion probe + Slidev build
  2. 完整运行时：再加逐页截图、视觉 diff、音画分析
  3. 不做运行时，继续靠人工
- **推荐**：方案 1（L2），L3 的逐页/抽帧由人工在发布前完成。理由：成本可控，能覆盖最危险的“编译/加载/时长”问题。
- **成本/风险**：CI 需要 Node/pnpm/Chrome；浏览器检查可能不稳定；需要证据留存。
- **可逆性**：高。按 stage 开关。
- **需批准**：是（CI 资源与运行时依赖）。
- **R1 临时假设**：L2 是目标；R1 不实现。

## D-08 课程、研究样本、legacy 与 labs 的数据处置

- **当前事实**：`courses/transformer-self-attention/` 被根仓库跟踪；`attention-research-2026-10/`（350KB）未跟踪；`_retired/`（49MB）未跟踪；`labs/`（197K）被忽略。没有仓库外备份记录。
- **可选方案**：
  1. 全部先备份，再逐项决定（推荐）
  2. 只保留活跃课程，其余归档到仓库外
  3. 全部纳入根仓库
- **推荐**：方案 1。先做仓库外备份与 checksum 清单；活跃课程保留；研究样本与 legacy 由负责人决定是否独立仓库/归档包。
- **成本/风险**：备份需要磁盘；纳入根仓库会增大体积；删除不可逆。
- **可逆性**：备份后可逆；删除不可逆。
- **需批准**：是。涉及数据保留与删除。
- **R1 临时假设**：不删除、不移动；只记录。

## D-09 CI 分层

- **当前事实**：CI 只做 py_compile、链接检查、32 项回归；run `40319878317` 成功；不跑真实课程、不构建、不渲染。
- **可选方案**：
  1. L1 必跑；L2 可选 job；L3 人工/发布前
  2. 所有检查都在 CI
  3. 只保留 L1
- **推荐**：方案 1。理由：L1 快且稳定；L2 需要 Node/Chrome，适合独立 job；L3 依赖人工/OBS，不适合 CI。
- **成本/风险**：L2 增加 CI 时间与不稳定性；需要缓存 pnpm/浏览器。
- **可逆性**：高。
- **需批准**：是。
- **R1 临时假设**：L1 必跑；L2 设计但不实现。

## D-10 新课程命名规则

- **当前事实**：`courses/README.md` 建议 `course-<slug>` / `technical-<slug>` / `news-<slug>-<YYYYMM>`；实际活跃课程是 `transformer-self-attention`；`attention-research-2026-10` 是研究样本。
- **可选方案**：
  1. 新集强制前缀，旧集保留例外（推荐）
  2. 全部重命名
  3. 不强制
- **推荐**：方案 1。理由：不破坏现有路径与历史；新集可预测。
- **成本/风险**：目录名与 slug 不完全一致；脚本需要处理例外清单。
- **可逆性**：高。
- **需批准**：是。
- **R1 临时假设**：旧集不改名；契约用 `episode_id`，不依赖目录前缀。

## D-11 是否持久化 trace

- **当前事实**：claims 有 `used_in_artifact`，segments 有 `script_anchor`/`slide_anchors`，recording 有 `segment_id`/`cue`，QA 有输入哈希；这些足以派生追溯关系。
- **可选方案**：
  1. 不持久化 trace，只生成 `trace-report.json`（推荐）
  2. 持久化 `trace.json` 作为第二事实来源
- **推荐**：方案 1。理由：避免双写不一致；报告可由 `qa.static` 重建。
- **成本/风险**：每次需要重新派生；需要交叉引用检查。
- **可逆性**：高。
- **需批准**：否（属于设计细节，已在本文件记录）。
- **R1 临时假设**：不新增 `trace.schema.json`；`trace-report.json` 是报告，不是源数据。
