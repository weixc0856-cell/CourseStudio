# AI Review Gates — R2.1

- **状态**：`ADOPTED_FOR_R2_1_IMPLEMENTATION`（工程实施基线）。
- **政策**：AI 多工具交叉自检；**不设置强制人工审核门禁**；负责人保留最终 `pass`/`reject`，不逐项审核。
- **历史**：R1 人工门禁文档存档于 [archive/human-gates-r1.md](archive/human-gates-r1.md)。
- **配套**：[status-model.md](status-model.md)、[pipeline-contract.md](pipeline-contract.md)、[R2.1 Approval Checklist](../r2.1/r2.1-approval-checklist.md)。

---

## 1. 五个 AI 审查域

| Gate | 审查域 | 输入 | 自动检查 | 失败/升级 |
| --- | --- | --- | --- | --- |
| `AI-1` | 事实与证据 | `claims.jsonl`、`sources.json`、原始来源/本地快照 | 来源存在、定位有效、原文片段、主张支持关系、冲突 | `FAIL` 或 `NEEDS_REVIEW` → 自动返工/降级表述 |
| `AI-2` | 教学结构与讲稿 | 大纲、讲稿、片段映射 | 目标可观察、模块顺序、术语一致、锚点/时长 | `FAIL`/`NEEDS_REVIEW` → script/design |
| `AI-3` | 视觉与课件 | 真实渲染截图/页面、deck 资源 | 溢出、遮挡、文字密度、对比度、版式一致 | `FAIL`/`NEEDS_REVIEW` → visual |
| `AI-4` | 口播与画面同步 | 讲稿、cues、probe/录像 | 分段映射、时间轴、动画关键状态 | `FAIL`/`NEEDS_REVIEW` → script/visual |
| `AI-5` | 录制与交付包 | 录像、ffprobe、manifest、交付清单 | 文件/哈希、时长、画幅、音画、清单一致 | `FAIL`/`NEEDS_REVIEW` → record/package |

**没有人工签字节点。** 每个 Gate 由至少一个确定性检查和/或独立 AI 验证路径给出结果；模型互相同意不算证据。

---

## 2. 记录格式

`qa/content-review.json`（或 `qa/recording.json`）示例：

```json
{
  "contract_version": "1.0.0",
  "episode_id": "course-example",
  "gate": "AI-1",
  "decision": "PASS",
  "method": ["source-locator-check", "independent-model-cross-check"],
  "reviewed_at": "2026-10-26T12:00:00Z",
  "scope": ["CLM-001", "CLM-002"],
  "artifact_hashes": [{"path": "research/claims.jsonl", "sha256": "..."}],
  "checks": [{"check_id": "AI1-SOURCE", "status": "PASS", "evidence": "..."}],
  "notes": "覆盖范围、已知盲区、未解决问题。",
  "return_to": null
}
```

规则：

- `decision`：`PASS` / `FAIL` / `NEEDS_REVIEW`；不是人工审批。
- `method`：列出实际使用的验证路径/工具/模型类别，不写“AI 认为正确”。
- `reviewed_at`：ISO 时间；不是负责人签字时间。
- `scope`：实际覆盖的主张/页面/片段，不得把抽样写成全量。
- `artifact_hashes`：审查时输入哈希；输入变化后自动 `STALE`。
- `return_to`：`NEEDS_REVIEW`/`FAIL` 时填写返回阶段。
- `notes`：必须写未解决/不确定项；空字符串无效。

---

## 3. 自动返工

| 情况 | 处理 |
| --- | --- |
| 结构/格式可自动修复 | 自动修复并重跑相关检查 |
| 来源不足/失效 | 重新检索、收窄表述或删除不可靠主张 |
| 视觉溢出/遮挡 | 调整布局并重新截图 |
| 时长/probe 不符 | 调整片段或重新 probe |
| 工具冲突 | 保留双方结果，用原始来源/实际运行解决 |
| 无法自动解决 | 标记 `NEEDS_REVIEW`/`BLOCKED`/`PARTIAL`，提供选项给负责人 |
| 负责人最终决定 | 接受、拒绝或要求返工；不要求逐项审核 |

---

## 4. 机器可检查 vs AI 判断

| 项 | 确定性程序 | AI 交叉检查 |
| --- | --- | --- |
| 文件/哈希/引用/资源 | 是 | — |
| Schema/契约/链接/泄漏 | 是 | — |
| 构建/浏览器/渲染/probe/ffprobe | 是 | — |
| 来源定位/主张支持 | 部分（结构） | 语义复核 |
| 讲稿/画面映射 | 部分（锚点/时间） | 语义/视觉复核 |
| 视觉可读性 | 截图/尺寸/像素检查 | 截图语义检查 |
| 教学有效性 | 否 | 只能给出风险提示，不能宣称已验证 |

---

## 5. 结论

- 取消人工审核不等于降低标准；证据、执行和交叉检查仍然必需。
- 没有实际运行/渲染/截图/来源定位，不得标记 `PASS`。
- 负责人只做最终 `pass`/`reject`；日常质量由 AI 自检和自动返工闭环处理。
