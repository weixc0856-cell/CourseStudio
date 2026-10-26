# CourseStudio Status Model — R2.1

- **状态**：`ADOPTED_FOR_R2_1_IMPLEMENTATION`（工程实施基线，不是负责人签署的批准记录）。
- **政策**：AI 多工具交叉自检；不设置强制人工审核门禁；负责人保留最终 `pass`/`reject`，不逐项审核。
- **历史**：R1 版本存档于 [archive/status-model-r1.md](archive/status-model-r1.md)。
- **配套**：[pipeline-contract.md](pipeline-contract.md)、[human-gates.md](human-gates.md)、[../schemas/episode.schema.json](../../schemas/episode.schema.json)。

---

## 1. 五个独立维度

| 维度 | 允许值 | 含义 | 谁设置 |
| --- | --- | --- | --- |
| `STRUCTURAL` | `PASS` / `FAIL` / `BLOCKED` / `PARTIAL` / `NOT_RUN` / `NOT_APPLICABLE` | Schema、契约、文件、引用、资源、链接 | 确定性程序 |
| `RUNTIME` | 同上 | 实际构建、浏览器加载、类型检查、渲染、probe、ffprobe | 确定性程序 |
| `CONTENT_QUALITY` | `PASS` / `FAIL` / `BLOCKED` / `PARTIAL` / `NEEDS_REVIEW` / `NOT_RUN` / `NOT_APPLICABLE` | 事实证据、讲稿一致性、教学结构、视觉质量、交叉自检 | AI 多工具 + 确定性检查 |
| `RECORDING` | 同上（无 `NEEDS_REVIEW`） | 实际录像、文件完整性、媒体探测、录制质量 | 程序 + AI 检查 |
| `DELIVERY` | `READY` / `NOT_READY` | 交付包完整性、证据、可复现性、阻塞项 | 程序按规则计算 |

**硬规则**：

1. 任何单维度通过都不能推导出 `DELIVERY=READY`。
2. 必需检查未执行 → `NOT_RUN`/`BLOCKED`，不得写 `PASS`。
3. 工具缺失 → `BLOCKED`，不是 `NOT_APPLICABLE`。
4. `NOT_APPLICABLE` 必须有任务范围说明。
5. `NEEDS_REVIEW` 先自动返工；不是必须人工审核。
6. 负责人最终 `pass`/`reject` 不属于自动门禁；它是对 AI 自检结果的最终处置。
7. `HUMAN` 不是新流程的维度；仅作为历史字段迁移映射。

---

## 2. 阶段与必需维度

| Stage | STRUCTURAL | RUNTIME | CONTENT_QUALITY | RECORDING | DELIVERY |
| --- | --- | --- | --- | --- | --- |
| `intake` | 必需 | N/A | N/A | N/A | N/A |
| `research` | 必需 | N/A | 必需 | N/A | N/A |
| `design` | 必需 | N/A | 必需 | N/A | N/A |
| `script` | 必需 | N/A | 必需 | N/A | N/A |
| `visual` | 必需 | 必需 | 必需 | N/A | N/A |
| `package` | 必需 | N/A | N/A | N/A | N/A |
| `qa.static` | 必需 | N/A | N/A | N/A | N/A |
| `qa.runtime` | N/A | 必需 | N/A | N/A | N/A |
| `content.review` | N/A | N/A | 必需 | N/A | N/A |
| `record` | N/A | N/A | N/A | 必需（video scope） | N/A |
| `deliver` | N/A | N/A | N/A | N/A | 必需 |

> `RECORDING` 默认 `NOT_APPLICABLE`（只交付制作包）；`--delivery-scope video` 时必需。

---

## 3. 阶段 gate（派生）

```text
function stage_gate(stage, dimensions, approvals):
    required = REQUIRED_DIMENSIONS[stage]
    if any(required[d] == FAIL for d in required): return FAIL
    if any(required[d] in {BLOCKED, NOT_RUN} for d in required): return BLOCKED
    if any(required[d] == NEEDS_REVIEW for d in required): return NEEDS_REVIEW
    if any(required[d] == NOT_APPLICABLE and not approved_skip(stage, d)): return BLOCKED
    if all(required[d] in {PASS, READY, NOT_APPLICABLE} for d in required): return PASS
    return IN_PROGRESS
```

优先级：`FAIL` > `BLOCKED` > `NEEDS_REVIEW` > `PASS`。

---

## 4. 状态转换

| 当前 | 事件 | 下一状态 |
| --- | --- | --- |
| `NOT_STARTED` | 阶段开始 | `IN_PROGRESS` |
| `IN_PROGRESS` | 必需检查通过 | `PASS` |
| `IN_PROGRESS` | 任一必需检查失败 | `FAIL` |
| `IN_PROGRESS` | 必需检查未运行/工具缺失 | `BLOCKED` |
| `IN_PROGRESS` | 内容质量需返工 | `NEEDS_REVIEW` |
| `NEEDS_REVIEW` | 自动修复后复验通过 | `PASS` |
| `NEEDS_REVIEW` | 自动修复失败/冲突 | `BLOCKED` 或 `PARTIAL` |
| `FAIL` | 修复后重跑 | `IN_PROGRESS` |
| `BLOCKED` | 补齐工具/证据 | `IN_PROGRESS` |
| `PASS` | 输入哈希变化 | `STALE`（等同 `NOT_RUN`） |
| `STALE` | 重跑 | `IN_PROGRESS` |
| `RECORDING=NOT_RUN` | 完成录像 + ffprobe | `RECORDING=PASS` |
| `DELIVERY=NOT_READY` | 所有必需维度满足 | `DELIVERY=READY` |
| `DELIVERY=READY` | 任一输入变化 | `DELIVERY=NOT_READY` |

`STALE` 是证据派生状态，不写入五维枚举；在 gate 中等同 `NOT_RUN`。

---

## 5. 交付判定

`DELIVERY=READY` 当且仅当：

1. 所有模式必需阶段 `stage_gate == PASS`；
2. 必需 `STRUCTURAL`、`RUNTIME`、`CONTENT_QUALITY` 全部 `PASS`；
3. 若 `delivery_scope=video`，`RECORDING=PASS`；否则 `NOT_APPLICABLE`；
4. 没有未解决的 `BLOCKER`/`ERROR`；
5. 所有 `NOT_APPLICABLE` 有任务范围说明或批准记录；
6. 所有 artifact 哈希与当前文件一致；
7. 没有 `STALE` QA run 被引用；
8. `delivery.blocking_reasons` 为空。

负责人最终 `pass`/`reject` 在 `DELIVERY=READY` 之后进行；它不是自动门禁，也不改变 AI 自检状态。

---

## 6. 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | `READY` 或阶段级 `STRUCTURAL_PASS` |
| `1` | `FAIL` |
| `2` | `BLOCKED` 或 `NEEDS_REVIEW` |
| `3` | `CONTRACT_ERROR`（Schema/状态/证据格式无效） |
| `4` | `NOT_APPLICABLE`（有范围说明的跳过） |

---

## 7. 边界案例

1. **静态通过、运行时未跑**：`RUNTIME=NOT_RUN` → `BLOCKED`，不输出 `READY`。
2. **运行时通过、内容质量为 NEEDS_REVIEW**：`NEEDS_REVIEW` → 自动返工；仍失败则 `BLOCKED`/`PARTIAL`。
3. **podcast 无视觉/录制**：`visual`/`qa.runtime`/`RECORDING=NOT_APPLICABLE`，记录 scope；其他必需维度通过可 `READY`。
4. **Motion 声明 68s、无 probe**：`RUNTIME=NOT_RUN` → `BLOCKED`；声明值不能代替实际值。
5. **QA run 输入哈希变化**：`STALE` → 等同 `NOT_RUN` → `BLOCKED`。
6. **缺 `episode.json`/版本不匹配**：`CONTRACT_ERROR`，退出码 3。
7. **观众版泄漏内部路径**：`CONTENT_QUALITY=FAIL` → `DELIVERY=NOT_READY`。
8. **录像文件存在但无 ffprobe**：`RECORDING=NOT_RUN`/`FAIL`，文件存在不等于通过。
9. **Manim 未安装但 `engine=manim`**：`RUNTIME=BLOCKED`，不是 `NOT_APPLICABLE`。
10. **只有非阻断 warning**：`DELIVERY=READY` 可成立，但 warning 必须记录；阻断策略按阶段显式定义。

---

## 8. 旧 `HUMAN` 映射

| 旧值 | 新语义 |
| --- | --- |
| `HUMAN=PENDING` | `CONTENT_QUALITY=NEEDS_REVIEW` |
| `HUMAN=ACCEPTED` | `CONTENT_QUALITY=PASS` |
| `HUMAN=REJECTED` | `CONTENT_QUALITY=FAIL` |
| `HUMAN=NOT_REQUIRED` | `CONTENT_QUALITY=NOT_APPLICABLE` |
| stage `human.accept` | stage `content.review` |

历史记录保留原字段；迁移时显式映射，不静默丢弃。
