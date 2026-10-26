# Schemas — Contract v1.0.0 (R2.1)

> **R2.1 迁移（2026-10-26）**：`episode.schema.json` 已把 `HUMAN` 替换为 `CONTENT_QUALITY`，并把阶段 `human.accept` 替换为 `content.review`。`HUMAN` 仅作为历史字段迁移映射（见 `docs/contract/status-model.md` 第 8 节）。完整 Draft 2020-12 验证由项目内 `tools/contract-runtime`（`jsonschema==4.26.0`）执行；`tests/contract/validate_with_jsonschema.py` 已通过 17 项 schema/instance 检查。

本目录是 R1 的**契约草案**，不是当前生产工具已在执行的 Schema。生产 `check-episode.py` 已接入 contract 状态模式，但尚未把 `episode.json` 作为唯一状态源；R2.2 才会双跑。

## 1. 版本策略

- 当前版本：`1.0.0`，状态 `DRAFT`。
- 版本号采用 SemVer：
  - **MAJOR**：删除/重命名字段、改变字段类型、删除枚举值、改变必填性、改变状态语义。必须提供迁移脚本与迁移报告。
  - **MINOR**：新增可选字段、新增枚举值、新增向后兼容检查。旧数据仍可读。
  - **PATCH**：文档、fixture、错误信息修正，不改变数据契约。
- 每个 `episode.json`、`claims` 文件、`segments.json`、`recording.json`、`qa` run 都必须声明 `contract_version`。
- 读取方规则：MAJOR 不匹配 → `CONTRACT_ERROR`（exit 3）；MINOR 高于读取方 → 警告但可读；PATCH 不比较。
- 未知字段：默认 `additionalProperties: false`。扩展只能放在 Episode 的 `extensions` 对象中，其他契约不允许扩展字段。
- 弃用：字段标记 `deprecated` 后至少保留一个 MAJOR；迁移报告必须列出仍在使用旧字段的课程。
- 历史数据：不原地改写。迁移采用“读旧 → 生成新 → 双跑对照 → 人工确认 → 切换”的流程。

## 2. Core 14 / 15 字段歧义的冻结结论

**结论：canonical Claim Ledger v1 有 15 个字段。`Core 14` 这个名称退役，不再使用。**

原因：

1. 研究 Skill 列出的 CSV 字段名有 **15 个**；
2. `attention-research-2026-10` 的真实表头也是 **15 列**；
3. “Core 14”很可能是把 `source_ids/source_locators`、`inspection_scope/scope_limit` 等成对字段按语义分组后得到的旧称，但从未有一份可执行的 14 字段定义；
4. 继续混用会让迁移无法机器判定。

最终字段（顺序即 CSV 列顺序）：

| # | 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `claim_id` | 是 | string `^CLM-[0-9]{3,}$` | 稳定 ID；一个主张一个 ID |
| 2 | `claim_text` | 是 | string | 主张原文；不是标题 |
| 3 | `claim_type` | 是 | enum | `FACT` / `CLAIM` / `INFERENCE` / `ASSUMPTION` / `REPRODUCED_RESULT` |
| 4 | `source_ids` | 是 | array<string> | 来源 ID 集合；必须与 `source_locators[].source_id` 的集合一致 |
| 5 | `source_locators` | 是 | array<object> | 每项 `{source_id, locator, excerpt?, url?}`；定位必须能回到原文 |
| 6 | `inspection_scope` | 是 | string | 本次实际检查了什么 |
| 7 | `scope_limit` | 是 | string | 结论适用范围/限制 |
| 8 | `derivation_or_data` | 是 | string | 推导、数据、公式或 `N/A` |
| 9 | `evidence_status` | 是 | enum | `DIRECTLY_SUPPORTED` / `PARTIAL` / `UNSUPPORTED` / `NOT_CHECKED` / `NOT_APPLICABLE` |
| 10 | `reasoning_status` | 是 | enum | `VALID` / `FLAWED` / `INCOMPLETE` / `NOT_APPLICABLE` / `NOT_CHECKED` |
| 11 | `execution_status` | 是 | enum | `NOT_RUN` / `THEORETICAL_ONLY` / `EXECUTED` / `REPRODUCED` / `BLOCKED` / `NOT_APPLICABLE` |
| 12 | `validation_status` | 是 | enum | `PASSED` / `FAILED` / `PARTIAL` / `NOT_RUN` / `BLOCKED` |
| 13 | `conflict_status` | 是 | enum | `NONE` / `POTENTIAL_CONFLICT` / `CONFIRMED_CONFLICT` / `NOT_CHECKED` |
| 14 | `used_in_artifact` | 是 | array<string> | `SEG-###` / `SLD-##` / `CUE-###` / `REC-###`；空数组表示未使用 |
| 15 | `review_notes` | 是 | object | `{notes, decision, reviewer?, reviewed_at?}`；`decision` 由人工填，LLM 不得自评 |

### 2.1 存储格式

- **canonical**：`claims.jsonl`，每行一个完整对象，对应 `claims.schema.json`。
- **legacy CSV**：现有 `02-claim-evidence-ledger.csv` 保留读取；迁移时按 `docs/contract/migration-map.md` 映射。
- CSV 中的 `source_locators` / `review_notes` 用 JSON 字符串编码；不再新增 CSV-only 字段。
- 语义规则（JSON Schema 不能表达，由 `qa.static` 检查）：
  - `source_ids` 必须等于 `source_locators[].source_id` 的去重集合；
  - `used_in_artifact` 的每个 ID 必须能在 segments / deck / recording 中找到；
  - `claim_id` 全局唯一；
  - `REPRODUCED_RESULT` 必须有 `execution_status=REPRODUCED` 且 `validation_status=PASSED`（Schema 已表达）；
  - `evidence_status=DIRECTLY_SUPPORTED` 时，`validation_status` 不得为 `NOT_RUN`。

## 3. 其他契约的要点

| 契约 | 核心约束 |
| --- | --- |
| `episode.schema.json` | 11 个 stage 必须存在；每个 stage 有 5 维状态；`delivery` 只能由规则计算，不能手填 READY |
| `segments.schema.json` | `segment_id` 唯一；`order` 连续 1..N；Motion 45–90s；Manim ≤20s；`actual_source` 只能是 probe/ffprobe/recording/NOT_VERIFIED |
| `recording.schema.json` | `record_status=VERIFIED` 必须有真实文件、sha256、ffprobe、录制人；文件存在不等于 VERIFIED |
| `qa.schema.json` | 每次 run 绑定输入/输出哈希；`FAIL` 必须有 failure/recovery；`NOT_RUN` 必须有 notes；退出码与状态一致 |

## 4. 是否需要 `trace.schema.json`

**结论：不新增持久化的 trace schema。**

理由：

- `claims.used_in_artifact`、`segments.script_anchor/slide_anchors`、`recording.segment_id`、`qa.check.inputs` 已经包含追溯所需的主键；
- 再存一份 trace 会形成第二个事实来源，容易出现两边不一致；
- 追溯关系应由 `qa.static` 从上述数据**派生**为 `trace-report.json`（报告，不是源数据），并用交叉引用规则校验。

派生规则见 `docs/contract/pipeline-contract.md` 第 9 节。

## 5. 验证状态

- 本目录 Schema 使用 JSON Schema Draft 2020-12 语法。
- 当前环境**没有安装 `jsonschema`**；R1 的 fixture 测试使用 `tests/contract/mini_schema.py` 覆盖本契约实际使用的关键字子集。
- 完整 Draft 2020-12 验证、生产接入、CI 接入均为 `NOT_RUN`，属于 R2。
- 任何“Schema 已生效”的说法都必须等到 R2 的真实读写与双跑对照完成。
