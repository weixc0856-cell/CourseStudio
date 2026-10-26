# Human Quality Gates — v1.0.0 (R1 draft)

> **SUPERSEDED（2026-10-26，R2.1 政策）**：不再设置强制人工审核门禁。事实、代码、视觉和交付由 AI 多工具交叉自检；`NEEDS_REVIEW` 先自动返工，必要时由负责人决定。负责人保留最终 `pass`/`reject`，不逐项审核。本文件仅保留为 R1 历史与迁移参考；现行规则见 [R2.1 Approval Checklist](../../r2.1/r2.1-approval-checklist.md)。

- **状态**：`DRAFT`。定义人工验收的输入、责任人、记录格式与拒绝回退；不实现自动评审。
- **原则**：机器只能检查“证据是否齐全、哈希是否一致、字段是否合法”；不能证明科学主张真实、教学有效或视觉可读。
- **配套**：[status-model.md](../status-model.md)、[pipeline-contract.md](../pipeline-contract.md)、[migration-map.md](../migration-map.md)。

---

## 1. 五个独立门禁

| Gate | 名称 | 负责确认 | 必需输入 | 拒绝后返回 |
| --- | --- | --- | --- | --- |
| `H1` | 事实与证据质量 | 领域审查人（对主题有专业判断） | `claims.jsonl`、`sources.json`、`quality.md`、原始来源快照/定位 | `research` |
| `H2` | 教学目标与内容连贯性 | 教学设计负责人 | `design.md`、`outline.md`、`script.md` | `design` 或 `script` |
| `H3` | 视觉表达与信息可读性 | 视觉/设计审查人 | deck、截帧/截图、`segments.json`、视觉基线 | `visual` |
| `H4` | 口播与画面同步 | 主讲/剪辑负责人 | `script.md`、cues、Motion probe/录像、时间轴 | `script` 或 `visual` |
| `H5` | 实际录制质量 | 剪辑/发布负责人 | 录像文件、ffprobe JSON、清单、抽帧 | `record` |

**门禁独立性**：H3 通过不代表 H1/H2 通过；H5 通过不代表 H4 通过。每个 Gate 单独记录。

---

## 2. 每个 Gate 的最小审查内容

### H1 — 事实与证据

必须逐条确认：

- `claim_type` 是否正确（尤其 FACT vs CLAIM vs INFERENCE）；
- `evidence_status` 是否有依据（`DIRECTLY_SUPPORTED` 必须真的检查过来源）；
- `source_locators` 是否能回到原文/原始数据；
- `scope_limit` 是否诚实；
- `conflict_status` 是否检查过反证；
- `used_in_artifact` 是否覆盖了实际使用该主张的页面/段落；
- 是否存在为了让检查通过而弱化限定。

**不能**因为“来源存在”就写 `DIRECTLY_SUPPORTED`；不能因为“没找到反证”就写 `NONE`。

### H2 — 教学目标与连贯性

- 学习目标是否可观察/可复述；
- 模块顺序是否有前置依赖；
- 每个模块是否有例子/边界/收束；
- 讲稿是否解释画面而不是念 bullet；
- 是否出现“为了完整”而超出范围的内容。

### H3 — 视觉与可读性

- 16:9 全屏、无控制条/录制 UI；
- 字体、对比度、矩阵/公式可读；
- 颜色语义一致（Q/K/V、强调、警告）；
- 动画末态稳定，关键信息不只在运动中；
- 截图/抽帧与 deck 一致；
- 无内部元数据（`record.html`、CLM ID、qa 路径）。

### H4 — 口播与画面同步

- 每个 `[SEGMENT]` 的 cue 与画面节拍对齐；
- 时间戳递增且在声明时长内；
- 口播不逐字念页面；
- 停顿/强调/切换有对应画面；
- 录像与 cue 的开头/中间/结尾抽帧一致。

### H5 — 录制质量

- 文件存在、非空、sha256 与 manifest 一致；
- ffprobe 时长与声明在允许偏差内；
- 分辨率/帧率符合 1920×1080/60fps（或批准的目标）；
- 无黑屏、无爆音、无长时间静音；
- 前后留白可用于拼接；
- 录制环境/操作者/时间记录。

---

## 3. 验收记录格式

每个 Gate 写一个 `acceptance/<gate>.json`（或合并到 `acceptance.json` 的 `gates` 数组）：

```json
{
  "contract_version": "1.0.0",
  "episode_id": "course-example",
  "gate_id": "H1",
  "decision": "ACCEPTED",
  "reviewer": "name-or-role",
  "reviewed_at": "2026-10-26T12:00:00Z",
  "scope": ["CLM-001", "CLM-002"],
  "artifact_hashes": [
    {"path": "research/claims.jsonl", "sha256": "..."}
  ],
  "notes": "What was checked and what remains uncertain.",
  "return_to": null
}
```

字段规则：

- `decision`：`PENDING` / `ACCEPTED` / `REJECTED`；只能由人填写。
- `reviewer`：真实责任人或角色；不得写 `LLM`、`AI`、`auto`。
- `reviewed_at`：ISO 时间；不接受“历史 handoff”代替。
- `scope`：本次审查覆盖的 claim/页面/段落；不是“全部”时不得写全部。
- `artifact_hashes`：审查时的输入哈希；输入变化后该验收自动 `STALE`。
- `return_to`：拒绝时必填，取值 `research`/`design`/`script`/`visual`/`record`。
- `notes`：必须写出未解决/不确定项；空字符串视为无效。

---

## 4. 状态与回退

| Gate 状态 | 对交付的影响 | 下游 |
| --- | --- | --- |
| `PENDING` | `DELIVERY=NOT_READY` | 不得进入 `record`/`deliver` |
| `ACCEPTED` | 该 Gate 通过；仍需其他 Gate | 可进入下一阶段 |
| `REJECTED` | `DELIVERY=NOT_READY` | 返回 `return_to`；下游全部 `STALE` |
| `STALE`（输入哈希变化） | 等同 `PENDING` | 必须重新审查 |

**规则**：

1. 任何一个必需 Gate `PENDING`/`REJECTED`/`STALE` → 不得 `READY`。
2. `H1` 拒绝 → `research` 修正 claim/来源；不得直接改讲稿绕过。
3. `H2` 拒绝 → `design` 或 `script`；由 reviewer 指定。
4. `H3` 拒绝 → `visual`；不得只改 deck 文案而不改动画映射。
5. `H4` 拒绝 → `script` 或 `visual`；必须重跑对应 cue/probe。
6. `H5` 拒绝 → `record`；必须重录，不得只改 `record_status`。
7. 拒绝记录保留；不得删除或覆盖为 ACCEPTED。
8. 人工验收不能由 LLM 自评；LLM 可以整理证据，但不能填 `decision`/`reviewer`。

---

## 5. 机器可检查 vs 人工判断

| 项 | 机器 | 人工 |
| --- | --- | --- |
| 证据文件存在/哈希一致 | 是 | — |
| `decision` 字段合法 | 是（格式） | 必须由人填值 |
| claim 是否有来源/定位 | 是（结构） | 来源是否真的支持主张 |
| 讲稿锚点/时长/时间戳 | 是 | 讲解是否清楚、节奏是否合适 |
| deck 资源/页面/泄漏 | 是 | 视觉是否可读、信息层级是否合理 |
| Motion typecheck/probe | 是 | 动画是否帮助理解 |
| 录像 ffprobe/文件哈希 | 是 | 音画是否同步、是否可发布 |
| 教学有效性/学习效果 | 否 | 需学习者测试或教学评审 |

---

## 6. 最小证据集

每个 Gate 至少保留：

- 验收 JSON（签名/角色/时间/scope/哈希）；
- 被审查产物的哈希；
- 关键截图/抽帧/日志路径；
- 未解决项清单。

没有这些证据，Gate 只能是 `PENDING`，不能是 `ACCEPTED`。
