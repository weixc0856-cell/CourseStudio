# 06 — Course Outline

- 项目：`transformer-self-attention`
- 日期：2026-10-26
- 阶段：R4 大纲冻结
- 目标成片：**10 分钟**（允许 8–12 分钟）
- 唯一 Motion 段落：`scores_to_weights`（第 5 模块，60–75 秒）
- 课件：Reveal；共 **12 个 `[SLIDE]` 锚点**；除第 5 模块外无 `[ANIMATION]`
- 依据：`04-course-input-brief.md`、`03-knowledge-structure.md`、CLM-001–CLM-014

## 1. 模块顺序与时长

| 模块 | 主题 | 预估时长 | 目标 | 对应 CLM | 锚点 | 依赖 |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | 为什么需要混合不同位置的信息 | 1.5 min | 用问题建立动机；只引出“同一序列内不同位置互相提供信息”，不先给公式 | CLM-001、CLM-002、CLM-003 | `[SLIDE: 01]`、`[SLIDE: 02]` | 无 |
| M2 | Q/K/V 三个角色 | 2.0 min | 建立 query 匹配 keys、values 被聚合；Q/K/V 同源；投影只一句边界 | CLM-001、CLM-003、CLM-004、CLM-011 | `[SLIDE: 03]`、`[SLIDE: 04]` | M1 |
| M3 | score：query-key 点积 | 1.5 min | 写出 `s_ij=q_i·k_j`、`S=QK^T`；用 toy `q1` 一行展示 score | CLM-005 | `[SLIDE: 05]`、`[SLIDE: 06]` | M2 |
| M4 | 缩放 `√d_k` | 1.0 min | 说明 `/√d_k`；区分论文动机（CLAIM）与 footnote 假设下推导（INFERENCE） | CLM-006、CLM-007、CLM-008 | `[SLIDE: 07]` | M3 |
| M5 | score → 行 softmax → weight + 唯一动画 | 2.0 min | 按行 softmax 得到 `A`；对比 `t1` 集中与 `t3` 均匀；动画停在 `A` | CLM-009（动画同时可视化 CLM-005/006） | `[SLIDE: 08]`、`[ANIMATION: scores_to_weights]`、`[SLIDE: 09]` | M4 |
| M6 | 输出：权重对 V 加权和 | 1.5 min | `O=AV`；用 `o1/o3` 说明输出是 value 的混合；不嵌入动画 | CLM-010 | `[SLIDE: 10]`、`[SLIDE: 11]` | M5 |
| M7 | 边界与收束 | 0.5 min | 说明本集不覆盖多头/mask/位置编码/完整 Encoder–Decoder/训练；总结 | CLM-012、CLM-013、CLM-014 | `[SLIDE: 12]` | M6 |

**合计：10.0 分钟**（1.5 + 2.0 + 1.5 + 1.0 + 2.0 + 1.5 + 0.5）。

## 2. 依赖与顺序约束

```text
M1 为什么
  → M2 Q/K/V 对象
  → M3 score（点积）
  → M4 缩放 √d_k
  → M5 行 softmax → weight
  → M6 加权和 → output
  → M7 边界
```

- **不能先出现 weight**：M5 之前只能出现 score/缩放，不出现 softmax 权重。
- **不能先出现 output**：M6 之前不出现 `O=AV`。
- Q/K/V 角色（M2）必须先于 score（M3）。
- score（M3）必须先于缩放（M4）；缩放必须先于 softmax（M5）。
- `[ANIMATION: scores_to_weights]` 只在 M5；其他模块为静态页或口播。
- M7 只做边界说明，不引入新公式。

## 3. 模块内容边界

### M1 — 为什么需要混合不同位置的信息（1.5 min）

- 用一个问题开场：处理一个 token 时，如何利用同一序列中其他位置的信息？
- 只建立“同一序列内互相提供信息”的直觉；不先给 Q/K/V 公式，不先出现 score/weight。
- 可用 S01 §3.2.3 的 self-attention 定义（CLM-002）作为答案的方向；不新增 motivation 事实主张。

### M2 — Q/K/V 三个角色（2.0 min）

- Query：当前 token 用来“找”什么；Key：其他 token“提供”什么；Value：被聚合的内容（CLM-001/003/004）。
- 强调 Q/K/V 同源：同一输入序列（CLM-002）。
- 投影只一句边界：“单头可把 Q/K/V 看作同一输入的不同投影，本集不展开。”（CLM-011，secondary only）
- 不展示 `W_Q/W_K/W_V` 矩阵，不展示多头维度。

### M3 — score：query-key 点积（1.5 min）

- 标量：`s_ij = q_i · k_j`；矩阵：`S = QK^T`（CLM-005）。
- 形状：`Q,K: n×d_k`，`S: n×n`。
- 用 toy `q1` 行展示 `[6,0,0,0]`；说明“一行 query 对所有 key 打分”。
- 不出现 softmax。

### M4 — 缩放 √d_k（1.0 min）

- 方法：`S/√d_k`；toy 中 `/2`（CLM-006）。
- 论文动机：大 `d_k` 下点积变大，softmax 进入小梯度区域；原文用 “We suspect”，标 CLAIM（CLM-007）。
- footnote 4 假设下点积方差为 `d_k`，标 INFERENCE（CLM-008）；不推广到所有分布。
- 不把缩放说成“已经证明对所有模型必要”。

### M5 — score → 行 softmax → weight + 唯一动画（2.0 min）

- 行 softmax：`A = row_softmax(S/√d_k)`；每行和为 1（CLM-009）。
- 对比：`t1` 行对 `k1` 约 0.870；`t3` 行四个 key 均 0.25。
- `[ANIMATION: scores_to_weights]`：60–75 秒；`QK^T → /√d_k → 行 softmax → A`；停在 `A`。
- 动画不展示投影、多头、mask、位置编码、训练，也不展示 `O=AV`（留给 M6）。
- 动画后的 `[SLIDE: 09]` 用静态页复述“权重是 query 对其他 token 的分配比例”。

### M6 — 输出：权重对 V 加权和（1.5 min）

- 输出：`o_i = Σ_j α_ij v_j`；矩阵 `O = A V`（CLM-010）。
- 用 toy `o1=[1.0,0.0866]`、`o3=[1.0,0.5]` 说明“输出是 value 的混合”。
- 不嵌入动画/MP4；静态页 + 口播收束。

### M7 — 边界与收束（0.5 min）

- 不覆盖：多头、mask、位置编码、完整 Encoder–Decoder、训练（CLM-012/013）。
- toy 数字是 ASSUMPTION/illustrative（CLM-014）。
- 总结：score → weight → weighted sum；下一集可进入多头/位置编码（不在本集）。

## 4. 动画与静态页分工

| 内容 | 载体 |
| --- | --- |
| Q/K/V 角色、同源、投影边界 | 静态页 + 口播（M2） |
| score `QK^T`、缩放、行 softmax、`A` | **Motion `scores_to_weights`（M5）** |
| 权重集中/均匀对比 | Motion + M5 静态复述 |
| `O=AV`、`o1/o3` | 静态页 + 口播（M6） |
| 多头/mask/位置编码边界 | 静态页（M7） |

- 全片唯一 `[ANIMATION]`：`scores_to_weights`。
- 不把 Motion 段落渲染成 MP4 嵌入 Reveal；独立 `record.html` 录制（后续阶段）。
- 不启用 Manim。

## 5. 后续 S1 的写作约束

- 按 M1–M7 顺序写，每次 1–2 个模块，追加到 `02_scripts/lecture_script.md`。
- 每个模块使用上表的 `[SLIDE]` 锚点；只在 M5 写 `[ANIMATION: scores_to_weights]`。
- 不写投影矩阵推导；不写多头/mask/位置编码/训练。
- 所有数字使用 `03-knowledge-structure.md` 的固定 toy 值；不即兴改数。
- 讲稿不得引入台账外的新事实主张；需要新主张时先回 R2。

R4 不写讲稿、Reveal、Motion；不启用 Manim；不调用 OBS。
