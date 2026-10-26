# CourseStudio Status Model — v1.0.0 (R1 draft)

> **SUPERSEDED（2026-10-26，R2.1 政策）**：新方向取消强制 `HUMAN` 审核维度，改用 `CONTENT_QUALITY`（由 AI 多工具交叉自检；`NEEDS_REVIEW` 先自动返工）。负责人保留最终 `pass`/`reject`，不逐项审核。本文件保留为 R1 历史；新工作以 [R2.1 Approval Checklist](../../r2.1/r2.1-approval-checklist.md) 与 [R2.0 Decision Proposal](../../r2.0/r2.0-decision-proposal.md) 为准。`HUMAN` 仅作为旧字段迁移映射。

- **状态**：`DRAFT`。本文件定义状态语义与判定规则，尚未接入生产检查器。
- **目标**：取消单一 `PASS_VERIFIED`；让每个“通过”只代表它实际验证过的维度。
- **配套**：[pipeline-contract.md](../pipeline-contract.md)、[human-gates.md](../human-gates.md)、[../schemas/episode.schema.json](../../../schemas/episode.schema.json)。

---

## 1. 五个独立维度

| 维度 | 允许值 | 含义 | 谁能设置 |
| --- | --- | --- | --- |
| `STRUCTURAL` | `PASS` / `FAIL` / `NOT_RUN` / `NOT_APPLICABLE` | Schema、锚点、引用、资源、链接、映射等确定性检查 | 程序 |
| `RUNTIME` | `PASS` / `FAIL` / `NOT_RUN` / `NOT_APPLICABLE` | typecheck、构建、浏览器加载、probe、ffprobe | 程序 |
| `HUMAN` | `ACCEPTED` / `REJECTED` / `PENDING` / `NOT_REQUIRED` | 事实、教学、视觉、音画、录制质量 | 人 |
| `RECORDING` | `PASS` / `FAIL` / `NOT_RUN` / `NOT_APPLICABLE` | 实际录像文件、完整性、时长、录制验收 | 人 + ffprobe |
| `DELIVERY` | `READY` / `NOT_READY` | 是否满足交付资格 | 程序按规则计算 |

**硬规则**：

1. `STRUCTURAL=PASS` 不得推导出 `RUNTIME=PASS`。
2. `RUNTIME=PASS` 不得推导出 `HUMAN=ACCEPTED`。
3. 缺必需证据时，对应维度只能是 `NOT_RUN`，不能写 `PASS`。
4. `NOT_APPLICABLE` 只能用于模式明确不需要、且有批准记录的阶段；工具缺失是 `NOT_RUN`/`BLOCKED`，不是 `NOT_APPLICABLE`。
5. `DELIVERY=READY` 不能由人直接填写；只能由规则计算。
6. 人工字段 `HUMAN`/`RECORDING` 不得由 LLM 自评填成 `ACCEPTED`/`PASS`。

> `STALE` 不是五维状态的枚举值。它是证据/QA run 的派生状态：当输入哈希与当前产物不一致时，证据标记为 `STALE`，在 gate 计算中等同 `NOT_RUN`。`episode.json` 的五维状态只需写 `NOT_RUN`/`PENDING`，并在 `qa` run 或 artifact 引用中记录 `STALE` 的原因。

---

## 2. 阶段与必需维度

`episode.json` 每个 stage 都保存五个维度；但每个 stage 只有一部分是“必需维度”。其余维度写 `NOT_APPLICABLE` 并附原因。

| Stage | STRUCTURAL | RUNTIME | HUMAN | RECORDING | DELIVERY |
| --- | --- | --- | --- | --- | --- |
| `intake` | 必需 | N/A | 必需 | N/A | N/A |
| `research` | 必需 | N/A | 必需 | N/A | N/A |
| `design` | 必需 | N/A | 必需 | N/A | N/A |
| `script` | 必需 | N/A | 必需 | N/A | N/A |
| `visual` | 必需 | 必需 | 必需 | N/A | N/A |
| `package` | 必需 | N/A | N/A | N/A | N/A |
| `qa.static` | 必需 | N/A | N/A | N/A | N/A |
| `qa.runtime` | N/A | 必需 | N/A | N/A | N/A |
| `human.accept` | N/A | N/A | 必需 | N/A | N/A |
| `record` | N/A | N/A | 必需 | 必需 | N/A |
| `deliver` | N/A | N/A | N/A | N/A | 必需 |

> `visual` 的 `RUNTIME` 包括 typecheck、构建、浏览器加载；`qa.runtime` 是独立的运行时验证阶段，两者不能互相替代。

---

## 3. 阶段级 gate（派生，不存储）

为避免重复存储，`stage_gate` 由五维状态计算，不写入 `episode.json`。

```text
function stage_gate(stage, dimensions, approvals):
    required = REQUIRED_DIMENSIONS[stage]

    if any(required[d] == FAIL or required[d] == REJECTED for d in required):
        return FAIL
    if any(required[d] == NOT_RUN for d in required):
        return BLOCKED
    if any(required[d] == NOT_APPLICABLE and not approved_skip(stage, d)):
        return BLOCKED
    if any(required[d] == PENDING for d in required):
        return PENDING
    if all(required[d] in {PASS, ACCEPTED, READY} for d in required):
        return PASS
    return IN_PROGRESS
```

优先级：`FAIL/REJECTED` > `NOT_RUN` > 未批准 `NOT_APPLICABLE` > `PENDING` > `PASS`。

---

## 4. 状态转换表

| 当前 | 事件 | 下一状态 | 说明 |
| --- | --- | --- | --- |
| `NOT_STARTED` | 阶段开始 | `IN_PROGRESS` | 写入 `episode.json`，记录输入哈希 |
| `IN_PROGRESS` | 必需检查全部通过 | `PASS` | 五维按规则满足 |
| `IN_PROGRESS` | 任一必需检查失败 | `FAIL` | 保留失败证据 |
| `IN_PROGRESS` | 必需证据缺失/未运行 | `BLOCKED` | 不得用 warning 绕过 |
| `FAIL` | 修复后重跑 | `IN_PROGRESS` | 新 `run-id`；旧证据保留 |
| `BLOCKED` | 补齐证据/工具 | `IN_PROGRESS` | 不得把缺失改成 N/A |
| `PASS` | 输入哈希变化 | `STALE` | 下游全部失效 |
| `STALE` | 重跑 | `IN_PROGRESS` | 必须重新执行，不得复用 |
| `HUMAN=PENDING` | 人接受 | `HUMAN=ACCEPTED` | 记录 reviewer/time/scope |
| `HUMAN=PENDING` | 人拒绝 | `HUMAN=REJECTED` | 记录返回阶段 |
| `HUMAN=REJECTED` | 回到上游修改 | 上游 `IN_PROGRESS` | 当前及下游 `STALE` |
| `RECORDING=NOT_RUN` | 完成录制 + ffprobe | `RECORDING=PASS` | 文件 + 哈希 + 时长 + 人工验收 |
| `RECORDING=PASS` | 文件变化/缺失 | `RECORDING=FAIL` | 不得只改状态 |
| `DELIVERY=NOT_READY` | 所有必需维度满足 | `DELIVERY=READY` | 仅由规则计算 |
| `DELIVERY=READY` | 任一输入变化 | `DELIVERY=NOT_READY` | 重新计算 |

**`STALE` 的语义**：已有证据存在，但其输入/输出哈希与当前产物不一致。`STALE` 在 gate 中等同 `NOT_RUN`，不得复用。

---

## 5. 交付判定规则

`DELIVERY=READY` 当且仅当：

1. 所有模式必需阶段的 `stage_gate == PASS`；
2. 必需 `STRUCTURAL` 检查全部 `PASS`；
3. 必需 `RUNTIME` 检查全部 `PASS`，且证据未 `STALE`；
4. 必需 `HUMAN` 项全部 `ACCEPTED`；
5. 必需 `RECORDING` 项全部 `PASS`，且 ffprobe 与人工录制验收齐全；
6. 没有未解决的 `BLOCKER` 或 `ERROR`；
7. 所有跳过的阶段/维度都有 `APPROVED` 记录；
8. `episode.json` 中所有 artifact 哈希与当前文件一致；
9. 没有 `STALE` 的 QA run 被引用；
10. `delivery.blocking_reasons` 为空。

否则 `DELIVERY=NOT_READY`，并列出每个阻塞原因 `{code, message, stage}`。

### 5.1 Warning 阻断策略

| 严重度 | 默认行为 | 示例 |
| --- | --- | --- |
| `BLOCKER` | 永远阻断交付 | 缺必需证据、观众版泄漏、录像文件损坏 |
| `ERROR` | 阻断交付 | 资源缺失、probe 与声明不符、cue 顺序错 |
| `WARNING` | 默认不阻断；按阶段策略决定 | 无 `[VISUAL]` cue、非关键格式建议 |
| `INFO` | 不阻断 | 工具版本提示、统计信息 |

阶段策略必须显式列出“哪些 WARNING 在本阶段升级为阻断”。未列出的 WARNING 只记录，不阻断。

---

## 6. 退出码

| 退出码 | 含义 | 触发条件 |
| --- | --- | --- |
| `0` | PASS | 所有必需检查已执行且通过；允许非阻断 WARNING |
| `1` | FAIL | 至少一个已执行检查失败，或 `HUMAN=REJECTED` |
| `2` | BLOCKED | 必需检查/证据未运行、缺失、`STALE`，或工具不可用 |
| `3` | CONTRACT_ERROR | Schema/版本/状态文件无效，无法判定 |
| `4` | NOT_APPLICABLE | 阶段按模式与批准记录明确跳过 |

CI 将 `1/2/3` 视为失败；`4` 仅在存在对应 `APPROVED` 记录时视为非失败。

---

## 7. 边界案例

### 案例 1 — 静态通过、运行时未跑、人工待审

- `STRUCTURAL=PASS`、`RUNTIME=NOT_RUN`、`HUMAN=PENDING`
- `visual` 必需 `RUNTIME` → `stage_gate=BLOCKED`
- 交付：`NOT_READY`，阻塞原因 `RUNTIME_NOT_RUN`
- 退出码：`2`

### 案例 2 — 运行时通过、人工拒绝

- `RUNTIME=PASS`、`HUMAN=REJECTED`
- `stage_gate=FAIL`
- 返回阶段：`visual` 或 `script`（由 reviewer 指定）
- 交付：`NOT_READY`；退出码 `1`

### 案例 3 — podcast 没有视觉/录制包

- `visual`、`package`、`qa.runtime` 为 `NOT_APPLICABLE`
- 必须有 `approvals` 记录，scope 指向该模式
- 其他必需维度通过 → `DELIVERY=READY`
- 若没有批准记录 → `BLOCKED`，退出码 `2`

### 案例 4 — 动画声明 68s，但没有 probe

- `segments.duration_seconds=68`、`actual_seconds=null`、`actual_source=NOT_VERIFIED`
- `RUNTIME=NOT_RUN` → `BLOCKED`
- 不得用声明时长代替实际时长；交付 `NOT_READY`；退出码 `2`

### 案例 5 — QA run 存在但输入哈希已变

- `qa.checks[].inputs[].sha256` 与当前文件不一致 → `STALE`
- 该 run 等同 `NOT_RUN`；必须重跑
- 交付 `NOT_READY`；退出码 `2`

### 案例 6 — 缺 `episode.json` 或版本不匹配

- 无法读取状态 → `CONTRACT_ERROR`
- 不得猜测阶段；不得从 `handoff.md` 自动迁移为 PASS
- 退出码 `3`

### 案例 7 — 观众版泄漏内部路径

- `qa.static` 的 leak check 返回 `ERROR`
- `stage_gate=FAIL`；交付 `NOT_READY`；退出码 `1`
- 返回阶段：`visual`（修改 deck）或 `script`（修改口播）

### 案例 8 — 录像文件存在，但没有 ffprobe

- `recording.record_status=RECORDED_UNVERIFIED`，不是 `VERIFIED`
- `RECORDING=FAIL` 或 `BLOCKED`；交付 `NOT_READY`
- 文件存在不等于录制通过

### 案例 9 — `engine=manim` 但 Manim 未安装

- `RUNTIME=NOT_RUN` → `BLOCKED`
- 不得改成 `NOT_APPLICABLE`；必须安装、改用 Motion，或由负责人批准显式跳过

### 案例 10 — 只有非阻断 WARNING

- `STRUCTURAL=PASS`、`RUNTIME=PASS`、`HUMAN=ACCEPTED`、`RECORDING=PASS`
- 一个未列入阻断策略的 `WARNING`（如无 `[VISUAL]`）
- `DELIVERY=READY`，但 `delivery.blocking_reasons=[]` 且 `qa.summary.warnings` 记录该警告
- 若该 WARNING 在阶段策略中列为阻断 → `NOT_READY`

---

## 8. 与旧状态词表的映射（只读兼容）

| 旧值 | 新语义 | 说明 |
| --- | --- | --- |
| `PASS_VERIFIED` | 最多 `STRUCTURAL=PASS` | 不再作为总体状态；必须补 runtime/human/recording |
| `PASS_STATIC` | `STRUCTURAL=PASS` | 不推导 runtime/human |
| `PARTIAL` | 一个或多个维度 `NOT_RUN`/`PENDING` | 细分到维度 |
| `NOT_RUN` | 对应维度 `NOT_RUN` | 保留 |
| `FAIL` | 对应维度 `FAIL` | 保留 |

**历史 handoff 不得自动迁移**：旧 handoff 中的 `PASS_VERIFIED` 只能作为“当时可能跑过结构检查”的线索；没有日志/哈希时，新状态必须是 `NOT_RUN`。

---

## 9. 机器可判定性

本模型的每条规则都可以实现为纯函数：

```text
required_dimensions(stage, mode) -> set
approved_skip(episode, stage, dimension) -> bool
is_stale(qa_run, artifact_hashes) -> bool
stage_gate(stage, dimensions, approvals) -> enum
delivery_ready(episode, qa_runs, acceptance, recording) -> {READY|NOT_READY, reasons}
exit_code(gate) -> 0|1|2|3|4
```

R2 必须为这些函数提供正向/反向 fixture；在实现前，本文件只是设计。
