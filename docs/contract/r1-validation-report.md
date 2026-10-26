# R1 Validation Report — Contract Freeze

- **日期**：2026-10-26
- **阶段**：R1 设计/契约冻结
- **结论**：R1 设计交付物已完成并通过本地契约测试；**系统未实现，生产工具未修改，R2 未开始**。
- **工作区**：审计/设计期间未修改任何现有生产脚本、课程讲稿、课件、动画、录制产物或既有文档。新增文件仅为 `R0-engineering-audit.md`、`docs/`、`schemas/`、`tests/`。

---

## 1. 首先复核 R0 基线

| 检查 | 命令 | 实际结果 | 等级 |
| --- | --- | --- | --- |
| 分支/工作区 | `git status --porcelain=v1 -b` | `## main...origin/main`；仅 `?? R0-engineering-audit.md`（R0 报告） | `VERIFIED` |
| HEAD | `git rev-parse HEAD` | `e4e744e83b58eee2434d0b056a2e1e7515dd01e2` | `VERIFIED` |
| 远端 main | `git ls-remote origin refs/heads/main` | 同一 commit `e4e744e...` | `VERIFIED` |
| 严格 QA 现状 | `python tools/check-episode.py transformer-self-attention --mode course --stage qa --strict` | `Status: PASS_VERIFIED`；`Build: SKIPPED`；`real=NOT_VERIFIED`；exit 0 | `VERIFIED` |
| 录制包计划 | `python tools/build-recording-package.py transformer-self-attention --check` | `Status: CHECK_ONLY`；exit 0；未写文件 | `VERIFIED` |
| 真实课程台账 | `head -1 .../02-claim-evidence-ledger.csv` | 8 列：`claim_id, claim, type, source_id, locator, evidence_snippet, scope, notes` | `VERIFIED` |
| 研究样本台账 | `head -1 courses/attention-research-2026-10/02-claim-evidence-ledger.csv` | 15 列 Core 14 字段 | `VERIFIED` |
| 文档声明 | `grep "15 列\|8 字段"` | README 写 15 列；质量报告写 8 字段（自相矛盾） | `VERIFIED` |
| `motion-isolation` 注册 | `test -e ~/.claude/skills/motion-isolation` | **不存在** | `VERIFIED` |
| `manim-isolation` 注册 | 同上 | 存在（junction） | `VERIFIED` |
| `course-studio` / research Skill | 同上 | 存在，但在仓库外 | `VERIFIED` |
| 运行时版本 | 读取 `package.json` | Reveal 6.0.2；Slidev 53.0.0；Motion 3.17.2 | `VERIFIED` |
| Manim | `manim --version` / `import manim` | 未安装 | `VERIFIED` |
| OBS | 检查文档路径 | `obs64.exe` 存在；未录制 | `PARTIAL`（安装存在，运行未执行） |
| 32 项回归（本地） | `python tools/test_check_episode_negative.py` | 未执行（R1 不跑生产回归） | `NOT_RUN` |
| 完整 JSON Schema | `import jsonschema` | 未安装 | `NOT_RUN` |

**与 R0 的差异**：无关键差异。R0 的 P0-01（假绿）、P0-03（cue 顺序）、P1-01（8 vs 15 列）、P0-02（Skill 注册）均在本次复核中再次确认。工作区新增 R0 报告，属于预期。

---

## 2. 新增交付物

| # | 路径 | 内容 |
| --- | --- | --- |
| 1 | [docs/contract/pipeline-contract.md](pipeline-contract.md) | 11 阶段职责、依赖、冻结点、模式矩阵、失效矩阵、失败恢复、trace 派生、治理 |
| 2 | [docs/contract/status-model.md](status-model.md) | 五维状态、阶段 gate、转换表、交付规则、退出码、10 个边界案例、旧状态映射 |
| 3 | [docs/contract/decision-log.md](decision-log.md) | D-01…D-11 决策表（全部 `PROPOSED`，含临时假设） |
| 4 | [docs/contract/migration-map.md](migration-map.md) | `transformer-self-attention` 只读 dry-run 映射、14 条主张、泄漏/页码/运行时缺口、三类迁移结果 |
| 5 | [schemas/episode.schema.json](../../schemas/episode.schema.json) | Episode 状态、stage、artifact、delivery、approval |
| 6 | [schemas/claims.schema.json](../../schemas/claims.schema.json) | Claim Ledger v1（15 字段） |
| 7 | [schemas/segments.schema.json](../../schemas/segments.schema.json) | 分段、引擎、时长、实际时长来源、映射 |
| 8 | [schemas/recording.schema.json](../../schemas/recording.schema.json) | 录制任务、文件哈希、ffprobe、人工验收 |
| 9 | [schemas/qa.schema.json](../../schemas/qa.schema.json) | QA run/check、命令/退出码/日志/哈希/运行时证据 |
| 10 | [schemas/README.md](../../schemas/README.md) | 版本策略、Core 14/15 结论、存储格式、trace 决策 |
| 11 | [tests/contract/run_contract_tests.py](../../tests/contract/run_contract_tests.py) | 24 项正向/反向/故障注入测试 |
| 12 | [tests/contract/mini_schema.py](../../tests/contract/mini_schema.py) | Draft 2020-12 关键字子集校验器 |
| 13 | [tests/contract/fault-cases.json](../../tests/contract/fault-cases.json) | 11 个故障注入案例及预期 |
| 14 | [tests/contract/fixtures/minimal-pass/](../../tests/contract/fixtures/minimal-pass/) | 合成正向 episode（claim/segment/scene/2 slides/package/QA/acceptance） |
| 15 | [tests/contract/fixtures/negative/](../../tests/contract/fixtures/negative/) | 6 个反向 fixture |
| 16 | [tests/contract/README.md](../../tests/contract/README.md) | 测试说明、fixture 合成声明、限制 |
| 17 | [docs/contract/r2-implementation-plan.md](r2-implementation-plan.md) | R2 顺序、交付、验收、停止、回滚 |
| 18 | [docs/contract/human-gates.md](human-gates.md) | 五类人工质量门禁：事实/教学/视觉/音画/录制 |
| 19 | 本文件 | R1 验证报告 |

---

## 3. 已执行的检查

| 检查 | 命令 | 结果 | 等级 |
| --- | --- | --- | --- |
| 契约测试 | `python tests/contract/run_contract_tests.py` | `24 passed, 0 failed`；exit 0 | `VERIFIED` |
| 链接检查 | `python tools/check-links.py .` | `checked 289 relative links` / `PASS_VERIFIED`；exit 0 | `VERIFIED` |
| JSON 加载 | 测试运行时加载全部 schema/fixture | 无解析错误 | `VERIFIED` |
| 正向 Schema | 6 项 | 全部通过 | `VERIFIED` |
| 正向端到端 | 1 项 | `PASS/0/READY` | `VERIFIED`（合成 fixture，不是真实课程） |
| 反向 Schema/语义 | 6 项 | 全部按预期失败 | `VERIFIED` |
| 故障注入 | 11 项 | 全部得到预期状态/退出码/交付 | `VERIFIED`（合成 fixture） |

### 3.1 24 项测试的构成

- 6 项正向 Schema：episode、claims、segments、recording、qa.static、qa.runtime。
- 1 项正向端到端：`PASS` / exit `0` / `READY`。
- 6 项反向：缺 `claim_text`、`CONTRADICTED` 非法、FACT 无来源、order gap、VERIFIED 无 ffprobe、坏版本。
- 11 项故障注入：缺字段、重复 claim、未知来源、缺 deck 资源、typecheck 失败、实际时长不符、cue 顺序错、缺 runtime 证据、观众版泄漏、人工 PENDING、QA 输入陈旧。

---

## 4. 未执行的检查（如实标注）

| 检查 | 原因 | 状态 |
| --- | --- | --- |
| 完整 JSON Schema Draft 2020-12 验证 | `jsonschema` 未安装；R1 不安装依赖 | `NOT_RUN` |
| 生产工具接入 | R1 边界；R2 才实施 | `NOT_RUN` |
| `check-episode.py` 双跑 | R2.2 | `NOT_RUN` |
| 真实 Motion typecheck / `probe=1` | R1 不运行生产/浏览器任务 | `NOT_RUN` |
| Reveal 浏览器加载/截图 | 同上 | `NOT_RUN` |
| Slidev build | 同上 | `NOT_RUN` |
| Manim 渲染 | 未安装 | `NOT_RUN` |
| OBS 录制 | 人工阶段 | `NOT_RUN` |
| 真实课程迁移写入 | R1 只读 dry-run | `NOT_RUN` |
| 课程内容修改（泄漏、页码、舍入） | 需负责人批准 | `NOT_RUN` |
| 本地 32 项回归 | R1 不跑生产回归 | `NOT_RUN` |
| 仓库外备份 | 需负责人批准与磁盘操作 | `NOT_RUN` |
| Skill 注册/分发变更 | 需负责人批准 D-04 | `NOT_RUN` |
| CI 扩展 | R2.7 | `NOT_RUN` |

---

## 5. 已解决的问题

1. **Core 14 / 15 字段歧义**：冻结为 **Claim Ledger v1（15 字段）**；`Core 14` 名称退役；给出逐字段必填/类型/枚举与旧 8 列映射。
2. **单一 `PASS_VERIFIED`**：替换为五维状态 + 阶段 gate + 交付规则；明确静态/运行时/人工/录制/交付的边界与退出码。
3. **Motion 与 recording 的 cue 循环**：`visual` 不读取 `05_recording/`；`package` 只依赖 script+segments；`qa.static` 统一检查。上游不再依赖下游生成的文件。
4. **trace 是否持久化**：决定不新增 `trace.schema.json`；从 `used_in_artifact`、`script_anchor`、`slide_anchors`、`segment_id`、QA 输入哈希派生 `trace-report.json`。
5. **真实课程迁移**：产出 14 条主张的字段映射、12 页/1 段/1 cue 映射、3 类迁移结果与未解决问题清单；未修改课程。
6. **可执行的正/反向/边界测试**：24 项测试 + 11 个故障案例全部通过本地 harness。
7. **人工质量门禁**：H1–H5 的输入、责任人、记录格式、拒绝回退与“LLM 不得自评”规则已单独定义。
8. **R2 计划**：给出顺序、交付、验收、停止条件和回滚。

---

## 6. 仍未解决的问题

1. **负责人决策未批准**：D-01 仓库拓扑、D-02 Reveal/Slidev 边界、D-03 Manim 去留、D-04 Skill 分发、D-06 状态模型、D-07 运行时 QA 范围、D-08 数据处置、D-09 CI 分层、D-10 命名。见 [decision-log.md](decision-log.md)。
2. **完整 JSON Schema 验证缺失**：`mini_schema` 只覆盖本契约使用的关键字；不能声称“完整 Draft 2020-12 通过”。
3. **生产未接入**：`check-episode.py` 仍输出旧状态；`episode.json` 尚未成为生产状态源。
4. **真实课程证据缺口**：14 条主张的 `evidence_status`/`reasoning_status`/`validation_status`/`conflict_status` 未填；Motion probe、Reveal 浏览器、录像均未跑。
5. **内容问题未修**：deck 08/09 的内部 `record.html` 泄漏、来源清单 16→15 页、权重表舍入说明，均需批准后单独处理。
6. **Skill 注册未改**：`motion-isolation` 仍未注册；仓库外 Skill 未 vendored/pinned。
7. **数据备份未执行**：`_retired`、`attention-research`、`labs` 仍无仓库外备份。
8. **CI 未扩展**：仍未验证真实课程产物。
9. **R2 运行时依赖未批准**：Chrome/Node/pnpm 可用，但 L2 CI 的资源与稳定性未决。

---

## 7. R1 验收条件逐项核对

| # | R1 条件 | 状态 | 证据/说明 |
| --- | --- | --- | --- |
| 1 | 阶段依赖无循环/前后矛盾 | **PASS** | 11 阶段依赖表；visual/package 兄弟化；cue 问题已解 |
| 2 | 状态词表/转换/交付资格可机器判定 | **PASS** | 五维状态、gate 伪代码、退出码、10 个边界案例 |
| 3 | Schema 字段一致；Core 14 歧义解决 | **PASS** | 15 字段 Claim Ledger v1；`schemas/README.md` |
| 4 | 真实课程迁移可生成字段映射与未解决问题 | **PASS** | `migration-map.md`；只读 dry-run |
| 5 | 正向/反向/边界测试有可执行预期 | **PASS** | 24 项测试 exit 0；11 故障案例 |
| 6 | 研究证据/程序验证/人工验收严格区分 | **PASS** | 五维状态；`review_notes` 由人填；LLM 不自评 |
| 7 | 备份/拓扑/Skill 分发未被静默决定 | **PASS（记录）** | 全部在 decision log 标 `PROPOSED`；未执行备份/注册 |
| 8 | R2 有实施顺序/失败恢复/停止/回滚 | **PASS** | `r2-implementation-plan.md` |
| 9 | 未执行检查如实标注 | **PASS** | 本报告第 4 节 |
| 10 | 负责人可逐项审查并批准 | **PASS（待审）** | 交付物齐全；批准本身未发生 |

**结论**：R1 的**设计验收条件**满足；但这不等于系统已实现。生产工具、课程内容、Skill 注册、CI、真实运行时均未改变。

---

## 8. 建议的 R2 顺序

1. R2.0：负责人批准 D-01/D-04/D-07/D-08；完成仓库外备份。
2. R2.1：契约库 + `episode.json`（shadow，不改变旧输出）。
3. R2.2：旧 checker / 新契约双跑，产出差异报告。
4. R2.3：修复 cue 顺序；新增新 episode 顺序测试。
5. R2.4：`qa.static`（claims schema、trace、leak、hash）。
6. R2.5：`qa.runtime`（Motion typecheck/probe、Reveal 浏览器、Slidev build）。
7. R2.6：Skill vendored/pinned + `motion-isolation` 注册。
8. R2.7：CI L1 + L2 可选 job。
9. R2.8：clean-room smoke + 11 故障注入。
10. R2.9：真实课程只读迁移 → 元数据 sidecar；内容修改单独批准。
11. R2.10：退出评审。

**R1 到此停止；不进入 R2，不自动提交/推送。**
