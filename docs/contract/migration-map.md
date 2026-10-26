# CourseStudio Migration Map — transformer-self-attention

- **状态**：`DRY-RUN ONLY`。本文件是只读迁移设计；没有修改任何课程文件。
- **样本**：`courses/transformer-self-attention/`（41 个 tracked 文件）。
- **目标契约**：[claims.schema.json](../../schemas/claims.schema.json)、[segments.schema.json](../../schemas/segments.schema.json)、[recording.schema.json](../../schemas/recording.schema.json)、[episode.schema.json](../../schemas/episode.schema.json)。
- **原则**：保留原始内容；缺字段标记 `TO_VERIFY` / `PENDING`；不自动编造证据状态；不把程序预检查映射为人工已核实；内容修改另行批准。

---

## 1. 迁移总览

| 项 | 现状 | 目标 | 自动可迁 | 需人工 | 需内容修改 |
| --- | --- | --- | --- | --- | --- |
| 主张台账 | 8 列 CSV，14 条 | 15 字段 Claim Ledger v1 | 字段重命名、来源拆分 | 证据/推理/验证/冲突状态、scope 拆分、review decision | 否 |
| 讲稿锚点 | 12 `[SLIDE]`、1 `[ANIMATION]`、1 `[SEGMENT]` | `SLD-01..12`、`SEG-001` | 是 | 无 | 否 |
| 动画段落 | `scores_to_weights` / 68s / order 1 | `SEG-001` | 是 | 实际时长 probe 未跑 | 否 |
| 课件 | 12 页，08/09 含内部 URL | `SLD-01..12` + 内部映射 | 页面映射 | 视觉/教学验收 | **是**（移除泄漏） |
| 录制包 | 1 task，NOT_RUN，0 recordings | `REC-001` + NOT_RUN | 结构映射 | 实拍、ffprobe、录制验收 | 否 |
| QA/handoff | 历史 `PASS_VERIFIED` 文本 | 新 QA run + 维度状态 | 不自动迁移 | 全部需重跑/人工 | 否 |
| 运行时证据 | Motion probe / Reveal 截图缺失 | `qa.runtime` 证据 | 否 | 需实际运行 | 否 |
| 页面计数 | 来源清单写 16 页 | 15 页 | 是（文本修正） | 确认 | **是**（1 处） |
| 数值展示 | deck 行和 0.999/1.001 | 加舍入说明或 4 位 | 否 | 教学确认 | **是**（可选） |

**Dry-run 统计**（只读解析）：

- 主张 14 条，`claim_id` 唯一；类型：FACT 7 / CLAIM 1 / INFERENCE 5 / ASSUMPTION 1。
- 有来源定位的主张 13 条；CLM-014 是 `ASSUMPTION`，来源为 `N/A`（合法）。
- 多来源主张：CLM-009（S01+S03）、CLM-010（S01+S02）、CLM-011（S02+S03）。
- 讲稿：12 个 `[SLIDE]`、1 个 `[ANIMATION]`、1 个 `[SEGMENT]`、6 个节奏标注。
- 课件：12 个 `data-slide`；2 处 `record.html?segment=`（08/09 页）。
- 录制：1 个 manifest task；`record_status=NOT_RUN`；`recordings=0`。
- QA：`qa/` 无实际 run 日志/截图；`04_motion_src/output/still/` 仅 2 张 PNG。
- 历史声明：`handoff.md` 声称 probe 68.0s、headless 截图、12 页检查；无对应持久证据。

---

## 2. 主张逐条映射

**统一规则**：

- `claim` → `claim_text`
- `type` → `claim_type`
- `source_id` → `source_ids`（按 `;` 拆分）
- `locator` + `evidence_snippet` → `source_locators[].locator` / `.excerpt`
- `scope` → `inspection_scope` + `scope_limit`（**TO_SPLIT_HUMAN**）
- `notes` → `review_notes.notes`（**TO_SPLIT_HUMAN**，部分内容应进 `derivation_or_data`）
- `evidence_status` → `NOT_CHECKED`（**不自动填 DIRECTLY_SUPPORTED**）
- `reasoning_status` → `NOT_CHECKED`
- `execution_status` → `NOT_APPLICABLE`（本集无代码/实验；CLM-014 的 toy 复算不算执行）
- `validation_status` → `NOT_RUN`
- `conflict_status` → `NOT_CHECKED`
- `review_notes.decision` → `PENDING`
- `used_in_artifact` → 由讲稿“依据”行静态派生，标记 **DERIVED_STATIC**，需人工确认

| Claim | Type | source_ids | source_locators（locator） | used_in_artifact（派生） | 新状态字段 | 处理 |
| --- | --- | --- | --- | --- | --- | --- |
| CLM-001 | FACT | S01 | §3.2.1 p.4；formula (1) | SLD-01, SLD-02, SLD-03 | evidence NOT_CHECKED / validation NOT_RUN | 自动字段 + 人工核验 |
| CLM-002 | FACT | S01 | §3.2.3 p.5 | SLD-01, SLD-04 | 同上 | 自动字段 + 人工核验 |
| CLM-003 | FACT | S01 | §3.2.1 p.4；formula (1) | SLD-01, SLD-02, SLD-03 | 同上 | 自动字段 + 人工核验 |
| CLM-004 | INFERENCE | S02 | #self-attention-in-detail | SLD-03 | 同上 | 自动字段 + 人工核验 |
| CLM-005 | FACT | S01 | §3.2.1 p.4；formula (1) QK^T | SLD-05, SLD-06, SEG-001 | 同上 | 自动字段 + 人工核验 |
| CLM-006 | FACT | S01 | §3.2.1 p.4；formula (1)；footnote 4 | SLD-07, SEG-001 | 同上 | 自动字段 + 人工核验；注意 pdftotext 丢根号 |
| CLM-007 | CLAIM | S01 | §3.2.1 p.4 | SLD-07, SEG-001 | 同上 | 自动字段 + 人工核验；保留 “We suspect” |
| CLM-008 | INFERENCE | S01 | footnote 4 p.4 | SLD-07 | 同上 | 自动字段 + 人工核验；`derivation_or_data` 填方差推导 |
| CLM-009 | INFERENCE | S01, S03 | S01 §3.2.1 formula (1)；S03 `softmax(dim=-1)` | SLD-08, SLD-09, SEG-001 | 同上 | 自动字段 + 人工核验；两来源分别建 locator |
| CLM-010 | FACT | S01, S02 | S01 formula (1)；S02 #self-attention-in-detail | SLD-10, SLD-11 | 同上 | 自动字段 + 人工核验 |
| CLM-011 | INFERENCE | S02, S03 | S02 #self-attention-in-detail / #matrix-calculation；S03 投影代码 | SLD-04 | 同上 | 自动字段 + 人工核验；标为教学框架 |
| CLM-012 | FACT | S01 | §3.2.2 p.5 | SLD-12 | 同上 | 自动字段 + 人工核验；边界 |
| CLM-013 | INFERENCE | S02 | #self-attention-in-detail | SLD-12 | 同上 | 自动字段 + 人工核验；8/64 caveat |
| CLM-014 | ASSUMPTION | N/A | R3 toy example（无外部来源） | SLD-05..11, SEG-001 | 同上 | `source_ids=[]`、`source_locators=[]`；人工确认 toy 数字 |

### 2.1 `inspection_scope` / `scope_limit` 建议拆分（仍需人工）

| Claim | 建议 inspection_scope | 建议 scope_limit |
| --- | --- | --- |
| CLM-001 | Definition of attention | single-head reading |
| CLM-002 | Encoder self-attention | single-head reduction; not cross-attention |
| CLM-003 | Single-head attention; one query row | 同左 |
| CLM-004 | Pedagogical framing | secondary only |
| CLM-005 | Single-head; score matrix before softmax | 同左 |
| CLM-006 | Single-head; d_k is query/key dimension | 同左 |
| CLM-007 | Motivation as stated by the paper | not an independent empirical result |
| CLM-008 | Illustrative derivation | explicit assumptions; not trained-model distributions |
| CLM-009 | Single-head; each query row normalized over keys | 同左 |
| CLM-010 | Single-head; per-position output | 同左 |
| CLM-011 | Single-head teaching abstraction | secondary only |
| CLM-012 | Boundary/out of scope | multi-head not covered |
| CLM-013 | Pedagogical caveat | prevents treating 8/64 as universal |
| CLM-014 | Illustrative only | no source claim |

### 2.2 证据状态不得自动填充

R0 只做了**片段存在性抽查**：CLM-001/005/006/007/008 的 snippet 在 `fulltext/1706.03762.txt` 中存在；CLM-009 的 `softmax(dim=-1)` 在 S03 HTML 中存在；CLM-004/011 的 S02 短语存在。这不等于“来源直接支持该主张”的语义审查。因此：

- 全部 `evidence_status=NOT_CHECKED`；
- 全部 `reasoning_status=NOT_CHECKED`；
- 全部 `validation_status=NOT_RUN`；
- 全部 `conflict_status=NOT_CHECKED`；
- 由领域审查人逐条改为 `DIRECTLY_SUPPORTED/PARTIAL/...`，并填写 `review_notes`。

---

## 3. 讲稿、分段与课件映射

| 源 | 目标 | 说明 |
| --- | --- | --- |
| `[SLIDE: 01]` … `[SLIDE: 12]` | `SLD-01` … `SLD-12` | 一一对应；deck 的 `data-slide` 也是 01–12 |
| `[ANIMATION: scores_to_weights]` | `SEG-001` | `name=scores_to_weights` |
| `[SEGMENT: scores_to_weights \| 68s \| order=1]` | `segments.json` `SEG-001` | `duration_seconds=68`、`declared_seconds=68`、`order=1` |
| `[VISUAL 00:00]` … `[VISUAL 01:02]` | cue 文件 | 6 个节奏块；时间戳保持原样 |
| `04_motion_src/src/scenes/scores_to_weights.tsx` | `SEG-001.scene` | 现有文件 |
| `04_motion_src/src/projects/scores_to_weights.ts` | `SEG-001.project` | 现有文件 |
| `05_recording/manifest.json` | `REC-001` | `record_status=NOT_RUN`；`recordings=0` |
| `05_recording/cues/scores_to_weights.md` | `CUE-001` | 生成物；映射到 `SEG-001` |

**注意**：`segments.json` 目前没有 `segment_id`，只有 `name`；迁移时新增 `SEG-001`，保留 `name`。`actual_seconds=null`、`actual_source=NOT_VERIFIED`，不得把 68 写成实际时长。

---

## 4. 录制与 QA 映射

### 4.1 录制

| 现状 | 目标 | 状态 |
| --- | --- | --- |
| manifest 1 task | `REC-001` | 结构可迁 |
| `record_status=NOT_RUN` | `REC-001.record_status=NOT_RUN` | 保留 |
| `recordings=0` | `recording=null` | 保留 |
| 无 ffprobe | `RECORDING=NOT_RUN` | 不得写 PASS |
| 无人工录制验收 | `human_acceptance=PENDING` | 不得写 ACCEPTED |

### 4.2 QA / handoff 声明

| 历史声明 | 现状证据 | 迁移结论 |
| --- | --- | --- |
| `--stage qa --strict → PASS_VERIFIED` | 本次重跑 exit 0，但 `Build: SKIPPED`、`real=NOT_VERIFIED` | 只能映射为 `STRUCTURAL=PASS`，不能映射为 runtime/human/recording PASS |
| Motion probe 68.0s / 4080 帧 | 无 probe JSON；仅 handoff 文本 | `RUNTIME=NOT_RUN`，需重跑 |
| Reveal 12 页截图 | `qa/` 无截图 | `RUNTIME=NOT_RUN`，需重跑 |
| headless Chrome seek 8/35/50/64/67s | 仅 2 张 PNG（000217/000974） | `PARTIAL`，不足；需重跑并落盘 |
| 录制包结构 PASS | 本次 `--stage recording` exit 0 | `STRUCTURAL=PASS`（仅结构） |
| OBS 实拍 | 无录像 | `RECORDING=NOT_RUN` |

### 4.3 缺失的运行时证据

- Motion：`typecheck`、`record.html?segment=scores_to_weights&probe=1`、实际帧数/秒数。
- Reveal：`reveal-run.ps1` 启动、Chrome 12 页加载/截图、控制台错误。
- Slidev：本集不使用，`NOT_APPLICABLE`。
- Manim：本集不使用，`NOT_APPLICABLE`。
- ffprobe：无录像，`NOT_APPLICABLE` 直到录制。

---

## 5. 观众版泄漏

| 位置 | 内容 | 判定 | 处理 |
| --- | --- | --- | --- |
| `03_slides/index.html:172` | `68 秒 · record.html?segment=scores_to_weights · 独立录屏，不嵌入 MP4` | 内部路径/制作元数据 → `ERROR` | 需内容修改：改为演讲者备注或录制专用页 |
| `03_slides/index.html:202` | `动画段落 scores_to_weights · 68s · record.html?segment=scores_to_weights` | 同上 | 同上 |
| 讲稿 `（依据：CLM-...；内部备注，不口播）` | 内部备注 | 不在观众版，安全 | 保留 |
| 讲稿 `## S1 批次边界（历史）` | 制作历史 | 不在观众版，安全 | 保留 |

**R1 不执行修改**；这两处需要负责人在 R2/R3 批准内容变更。

---

## 6. 三类迁移结果

### 6.1 纯元数据迁移（不需要改课程内容）

- claim 字段重命名/拆分/数组化；
- 新增 15 字段中的状态字段，但全部填 `NOT_CHECKED` / `NOT_RUN` / `PENDING`；
- `used_in_artifact` 从讲稿“依据”行派生；
- `SEG-001`、`SLD-01..12`、`CUE-001`、`REC-001` 的 ID 映射；
- `episode.json` 的 stage/artifact 引用；
- QA run 包装为 `qa/runs/<id>/run.json`，状态填 `NOT_RUN` 或 `PARTIAL`；
- `handoff.md` 保留为历史参考，不迁移为已验证状态。

### 6.2 必须修改的内容（需批准）

1. 移除 deck 08/09 的 `record.html?segment=...`（改为演讲者备注或录制专用页）。
2. 来源清单页码 16 → 15（`01-source-inventory.md:33`）。
3. 可选：deck 权重表的舍入说明（当前 0.999/1.001，caption 写“每行和 = 1”）。
4. 可选：把 `qa/` 的历史声明改为“历史声明，未复跑”。

### 6.3 无法自动迁移（必须人工）

- 14 条主张的 `evidence_status`、`reasoning_status`、`validation_status`、`conflict_status`；
- 每条 `source_locators` 的语义核对（片段存在 ≠ 支持主张）；
- `inspection_scope` / `scope_limit` 的拆分；
- `review_notes` 的 reviewer/time/decision；
- 5 类人工验收（事实、教学、视觉、音画、录制）；
- 实际 Motion probe / Reveal 浏览器 / 录像 / ffprobe；
- `used_in_artifact` 的语义确认（当前是静态派生，不是人工确认）。

---

## 7. 迁移顺序建议（R2/R3，不在 R1 执行）

1. 只读解析旧 CSV，生成 `claims.migrated.jsonl`（状态字段全部 `NOT_CHECKED`/`NOT_RUN`/`PENDING`）。
2. 生成 `segments.migrated.json`、`recording.migrated.json`、`episode.migrated.json`。
3. 双跑：旧 `check-episode.py` vs 新契约校验；记录差异。
4. 人工逐条补 14 条主张状态；不通过就保持 `NOT_CHECKED`，不得为了通过而填 `DIRECTLY_SUPPORTED`。
5. 运行 runtime QA（Motion typecheck/probe、Reveal 浏览器）；落盘证据。
6. 人工视觉/教学/音画/录制验收。
7. 只有全部证据齐全，才把 `episode.json.delivery.status` 计算为 `READY`。
8. 内容修改（泄漏/页码）单独提交、单独审查；不与元数据迁移混在同一批次。
