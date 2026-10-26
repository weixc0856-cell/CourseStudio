# R2 Implementation Plan — Minimal Closed Loop

- **状态**：`DRAFT`。R2 尚未开始；本文件只定义实施顺序、验证与回滚。
- **前提**：R1 契约通过负责人审查；未批准的决策保持临时假设，不得在生产中静默生效。
- **目标**：在不重写现有生产工具的前提下，把 R1 契约接入一条可重复、可失败、可回滚的最小闭环。
- **非目标**：不清理 legacy、不删除课程、不自动提交/推送、不自动录制 OBS。

---

## 1. 实施原则

1. **双跑优先**：新契约先以 `shadow` 模式运行，旧 `check-episode.py` 继续作为默认；记录差异，不改变门禁。
2. **适配器优先**：新增 Python 包/CLI 包装现有 `script_timing.py`、`build-recording-package.py`、`check-episode.py`，不重写它们的核心逻辑。
3. **状态单一来源**：`episode.json` 是唯一状态；`handoff.md` 由它生成；迁移期双写。
4. **证据优先**：每次运行写 `qa/runs/<run-id>/`；旧证据保留；失败不覆盖成功。
5. **内容与元数据分离**：迁移只改元数据；任何课程内容修改单独批准、单独提交。
6. **可回滚**：每步都有 feature flag 或 `git revert` 路径；不删除旧文件。

---

## 2. 阶段与交付

### R2.0 — 决策冻结与备份

- **交付物**：负责人对 D-01（拓扑）、D-04（Skill 分发）、D-07（运行时 QA 范围）、D-08（数据处置）的批准记录；仓库外备份与 checksum 清单。
- **涉及文件**：`docs/contract/decision-log.md`（状态从 `PROPOSED` 更新为批准/拒绝）；备份清单放仓库外。
- **前置**：R1 验收通过。
- **测试**：备份恢复演练；checksum 比对。
- **通过标准**：每个高风险决策有明确结论；`_retired`、`attention-research`、`labs` 有备份。
- **停止条件**：任一决策未决且会阻塞后续步骤；备份失败。
- **回滚**：无生产变更；删除新增批准记录即可。

### R2.1 — 契约库与 `episode.json`（shadow）

- **交付物**：`course_contract/`（或 `tools/contract/`）Python 包：加载/写入 `episode.json`、schema 校验、状态计算、哈希；**不改变旧工具默认行为**。
- **涉及文件**：新增包；`schemas/`；`tests/contract/` 扩展；不改 `check-episode.py`。
- **前置**：R2.0；`jsonschema` 依赖决策（若安装，需批准；否则继续 mini validator）。
- **测试**：R1 的 24 项 + 新增：写-读-写幂等、哈希变化、状态转换、`NOT_APPLICABLE` 批准。
- **通过标准**：当前样本可生成 `episode.shadow.json`；不改变任何现有输出；所有测试 exit 0。
- **停止条件**：需要改课程内容才能生成状态；schema 需不兼容变更。
- **回滚**：删除新增包；无生产影响。

### R2.2 — 双跑适配器

- **交付物**：`course verify --shadow`：同时运行旧 `check-episode.py` 与新契约校验，输出差异报告 `qa/runs/<id>/shadow-diff.json`。
- **涉及文件**：新增 adapter；不改旧 checker 的默认输出。
- **前置**：R2.1。
- **测试**：对 `transformer-self-attention` 跑全 stage；人为注入 5 个故障，差异必须可见。
- **通过标准**：差异报告能解释旧 `PASS_VERIFIED` 与新五维状态的对应关系；无误报为“已验证”。
- **停止条件**：旧 checker 无法在不改逻辑的情况下被包装；差异无法解释。
- **回滚**：关闭 shadow flag；旧路径不变。

### R2.3 — 修复 cue 顺序（P0-03）

- **交付物**：`visual`/`motion` 检查不再要求 cue；cue 检查移到 `package`/`qa.static`。
- **涉及文件**：`tools/check-episode.py`（小改，保持旧 stage 兼容）、`tools/script_timing.py`（如需）、`tools/build-recording-package.py`（生成时机）、测试。
- **前置**：R2.1；负责人确认阶段语义。
- **测试**：新建临时 episode（非 `example` segment）→ `--stage motion` 在没有 cue 时必须通过；`--stage recording` 在 cue 缺失时必须失败；builder 后通过。
- **通过标准**：旧真实课程仍通过；新 fixture 覆盖顺序；无循环依赖。
- **停止条件**：修复需要改变 `segments.json` 语义或课程内容。
- **回滚**：恢复旧检查；新增测试标记 skip。

### R2.4 — `qa.static` 实现

- **交付物**：Schema/claims/trace/leak/mapping/哈希检查；`trace-report.json` 生成器；`qa/runs/<id>/static/` 证据。
- **涉及文件**：新增 `course_contract/qa_static.py`；复用 `mini_schema` 或批准的 `jsonschema`；不改课程。
- **前置**：R2.1、R2.3；15 字段 Claim Ledger 确认。
- **测试**：R1 的 11 个故障案例 + 真实样本 dry-run；leak 必须报出 deck 172/202。
- **通过标准**：所有故障案例得到预期状态/退出码；真实样本的已知泄漏被报告；不修改课程。
- **停止条件**：需要先修改课程内容才能通过（应报告为待批准，而非自动改）。
- **回滚**：关闭 `qa.static` 新检查；旧 checker 不变。

### R2.5 — `qa.runtime` L2

- **交付物**：Motion typecheck + `probe=1`；Reveal 静态服务 + Chrome 加载/截图；Slidev build；证据落盘。
- **涉及文件**：新增 `course_contract/qa_runtime.py`；复用 `motion-run.ps1`、`reveal-run.ps1`、`slidev-run.ps1`；不改它们。
- **前置**：R2.0 批准 D-07；Node/pnpm/Chrome/ffmpeg 可用（已确认）；不要求 Playwright。
- **测试**：正向 fixture + 真实课程；注入类型错误/缺资源/坏 probe。
- **通过标准**：runtime 证据可复现；失败时状态是 FAIL/NOT_RUN，不是 PASS；证据路径/哈希记录。
- **停止条件**：Chrome 无法在目标环境稳定运行；需要安装新依赖但未批准。
- **回滚**：关闭 runtime job；保留 L1。

### R2.6 — Skill 分发与注册

- **交付物**：核心 Skill vendored 或 pinned；`skills.lock`；`motion-isolation` 注册；`manim-isolation` 明确 legacy。
- **涉及文件**：新增 `tools/skills/` 子树或 `skills.lock`；安装脚本；不改用户配置而不经批准。
- **前置**：R2.0 批准 D-04。
- **测试**：空 `HOME`/新用户配置下按文档安装；Skill 列表包含 `motion-isolation`；哈希匹配。
- **通过标准**：干净环境可复现；没有隐式全局依赖；`manim-isolation` 不被默认调用。
- **停止条件**：需要覆盖用户现有 Skill/配置且未获批准。
- **回滚**：删除安装脚本/lock；保留现有全局 Skill。

### R2.7 — CI 分层

- **交付物**：L1 必跑（schema/单元/负向/链接/泄漏）；L2 可选 job（fixture course、typecheck、Reveal/Slidev build）。
- **涉及文件**：`.github/workflows/python-app.yml` 或新增 workflow；`tests/contract/`；fixture。
- **前置**：R2.1–R2.5。
- **测试**：提交坏 fixture → CI 失败；恢复 → 通过；L2 job 可手动触发。
- **通过标准**：CI 能捕获真实课程结构回归；L1 时间可接受；L2 不阻塞主分支（或按批准策略）。
- **停止条件**：CI 时间/稳定性不可接受；需要未批准的服务/密钥。
- **回滚**：恢复原 workflow；保留本地测试。

### R2.8 — Clean-room smoke + 故障注入

- **交付物**：临时目录中的完整 episode：1 claim、1 segment、1 scene、2 slides、1 package、static+runtime QA、human accept、deliver；11 个故障注入结果。
- **涉及文件**：`tests/contract/fixtures/`；新增 `tests/contract/test_clean_room.py`（可选）；不写 `courses/`。
- **前置**：R2.1–R2.5；运行时依赖可用。
- **测试**：新建 → 全链路 → 断言状态/退出码/证据；删除临时目录后无残留。
- **通过标准**：全链路可重复；第二次运行可跳过未变阶段；故障案例全部符合预期；没有 `courses/` 变更。
- **停止条件**：任一阶段需要人工绕过；任何检查无法自动化；临时目录残留。
- **回滚**：删除临时目录；无生产影响。

### R2.9 — 真实课程迁移（只读 → 元数据）

- **交付物**：`transformer-self-attention` 的 `episode.migrated.json`、`claims.migrated.jsonl`、`segments.migrated.json`、`recording.migrated.json`、`trace-report.json`；差异报告。
- **涉及文件**：新增 sidecar 文件（或迁移分支）；不改原 CSV/讲稿/课件/动画。
- **前置**：R2.4/R2.5；负责人批准迁移；备份完成。
- **测试**：双跑旧/新；14 条主张逐条对照；12 页/1 段/1 cue 追溯；内容 diff 必须为空（除元数据）。
- **通过标准**：所有旧 Gate 保留；迁移只改元数据；未解决字段明确列出；内容修改单独清单。
- **停止条件**：需要修改课程内容；证据状态无法诚实填写；迁移导致旧 Gate 失败。
- **回滚**：删除 sidecar；原文件未动。

### R2.10 — R2 退出评审

- **交付物**：`docs/contract/r2-validation-report.md`；R3 任务清单。
- **通过标准**：见第 4 节。
- **停止条件**：任一退出标准未满足。
- **回滚**：R2 变更用 feature flag 关闭；生产回到 R1 前状态。

---

## 3. 失败恢复与回滚

| 场景 | 处理 | 回滚 |
| --- | --- | --- |
| Schema 不兼容 | 停止，升级 MAJOR，补迁移 | 旧 schema/旧 checker |
| 双跑差异无法解释 | 停止，记录差异，不改默认 | 关闭 shadow |
| cue 顺序修复导致旧课程失败 | 回退该小改，保留测试 skip | `git revert` 单提交 |
| 运行时依赖缺失 | 标记 BLOCKED，不写 PASS | 关闭 L2 job |
| 迁移需要内容修改 | 停止，单列内容变更审批 | 删除 sidecar |
| 同一失败 3 次 | 停止，保留现场，报告命令/退出码/日志 | 回滚到最近成功点 |
| 数据丢失风险 | 立即停止；从备份恢复 | 仓库外备份 |

**禁止**：删除证据、改检查器以通过、把 `NOT_RUN` 写成 `PASS`、用历史 handoff 替代当前证据、自动提交/推送。

---

## 4. R2 退出标准

1. R1 的 24 项契约测试 + 新增集成测试全部通过。
2. 双跑差异报告完成；旧 `PASS_VERIFIED` 不再被解释为运行时/人工验证。
3. `--stage motion` 不再依赖下游 cue；新 episode 顺序可执行。
4. `qa.runtime` 能证明 Motion typecheck/probe、Reveal 浏览器、Slidev build（适用时）。
5. `episode.json` 成为唯一状态；`handoff.md` 可重建。
6. 核心 Skill 在干净环境可复现；`motion-isolation` 已注册。
7. 迁移只产生元数据 sidecar；原课程内容未变。
8. 所有故障注入得到预期状态/退出码/交付结果。
9. 回滚路径至少演练一次（关闭 flag + `git revert`）。
10. 没有任何“设计完成 = 系统已实现”的表述。

---

## 5. R2 推荐顺序

```text
R2.0 批准/备份
  → R2.1 契约库（shadow）
  → R2.2 双跑
  → R2.3 cue 顺序修复
  → R2.4 qa.static
  → R2.5 qa.runtime
  → R2.6 Skill 分发
  → R2.7 CI 分层
  → R2.8 clean-room smoke
  → R2.9 真实课程元数据迁移
  → R2.10 退出评审
```

R2.4/R2.5 可以在 R2.3 之后并行；R2.6/R2.7 可以与 R2.4 并行。R2.9 必须等 R2.4/R2.5 稳定后再开始。
