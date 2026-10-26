# 04 — Course Input Brief

- 项目：`transformer-self-attention`
- 日期：2026-10-26
- 阶段：R4 研究收束
- 状态：课程输入简报冻结；S1–S4 讲稿、Motion 场景、录制就绪包与 Reveal P2 正文已完成（M1–M7）；slides/QA 通过；下一步整体验收与人工 OBS 准备
- 依据：`00-task-brief.md`、`01-source-inventory.md`、`02-claim-evidence-ledger.csv`（CLM-001–CLM-014）、`03-knowledge-structure.md`

## 1. 受众与预备知识

- 有深度学习基础：理解张量、矩阵乘法、点积、softmax、损失与反向传播的概念。
- 知道 Transformer 是序列模型，但不是注意力专家；可能看过结构图，但说不清 Q/K/V 的作用。
- 不要求实现过 attention，也不要求手推梯度。

## 2. 学习目标（可检验）

看完本集，读者应能：

1. **解释 Q/K/V 的角色**：能说出 query 与 keys 做匹配、values 被聚合；能指出 Q/K/V 在 self-attention 中来自同一输入序列（CLM-001/002/003/004）。
2. **算出一行 score**：给定一行 query 与所有 keys，能写出点积 score，并说明 `S=QK^T` 的形状（CLM-005）。
3. **解释缩放**：能说明 softmax 前除以 `√d_k`；能区分“论文的动机陈述”（CLAIM）与“footnote 假设下的方差推导”（INFERENCE），不把动机说成普适事实（CLM-006/007/008）。
4. **解释 score → weight**：能说明按 query 所在行做 softmax，权重非负且和为 1；能对比“集中权重”和“均匀权重”（CLM-009）。
5. **解释输出**：能说明输出是该行权重对所有 value 的加权和，`O=AV`（CLM-010）。
6. **复述玩具例子**：能在 4-token 例子上指出 `t1` 更关注 `k1`、`t3` 权重均匀，并复算 `o1/o3`（CLM-014，illustrative）。
7. **说清边界**：知道本集不展开多头、mask、位置编码、完整 Encoder–Decoder、训练（CLM-012/013）。

## 3. 本集叙事主线

```text
为什么需要混合不同位置的信息？
  → Q/K/V 三个角色是什么？
  → query 与 key 如何产生 score？
  → 为什么要除以 √d_k？
  → score 如何按行 softmax 成 weight？
  → weight 如何对 V 加权求和得到输出？
  → 哪些内容不在本集？
```

顺序约束：

- **不能先出现 weight 再定义 score**；
- 先 score，再缩放，再 softmax，再加权和；
- Q/K/V 角色在 score 之前建立；
- 输出在权重之后；
- 边界放在最后。

## 4. 证据基线

- **主证据 S01**：`Attention Is All You Need`，Vaswani et al., 2017，`arXiv:1706.03762v7`；重点 §3.2.1 p.4、footnote 4 p.4、Figure 2 left、§3.2.3 p.5。
- **二次材料只做交叉核对**：
  - S02 `The Illustrated Transformer`（Jay Alammar, 2018）：Q/K/V 直觉、逐词 score/softmax/加权和；
  - S03 `The Annotated Transformer`（v2022 / original 2018 Sasha Rush）：公式与代码 `math.sqrt(d_k)`、`softmax(dim=-1)`。
- 所有事实/公式/数字在 `02-claim-evidence-ledger.csv` 中有 CLM 映射；讲稿不得引入台账外的新事实主张。
- 若讲稿需要新的动机/结论，先回 R2 补台账，不在 S1 临时发明。

### 使用的 CLM

| 主题 | CLM |
| --- | --- |
| attention 定义、Q/K/V 角色、values 聚合 | CLM-001、CLM-003、CLM-004 |
| self-attention Q/K/V 同源 | CLM-002 |
| score = query-key 点积 | CLM-005 |
| √d_k 与动机 | CLM-006（FACT）、CLM-007（CLAIM）、CLM-008（INFERENCE） |
| 行 softmax 权重 | CLM-009 |
| 输出加权和 | CLM-010 |
| 单头投影教学框架（不展开） | CLM-011（secondary only） |
| 多头边界 / S02 8/64 caveat | CLM-012、CLM-013 |
| 4-token 玩具例子 | CLM-014（ASSUMPTION / illustrative） |

## 5. 玩具例子如何使用

- 使用 `03-knowledge-structure.md` 已固定的例子：`n=4, d_k=4, d_v=2, √d_k=2`。
- 在第 3 模块展示 `S=QK^T` 的一行；在第 4 模块展示 `/2`；在第 5 模块展示 `t1` 行与 `t3` 行的 softmax 对比；在第 6 模块展示 `O=AV` 的 `o1/o3`。
- 数字只用于教学演示，标 `ASSUMPTION / illustrative only`（CLM-014）；不是 S01 的超参数或训练结果。
- 不展示 `W_Q/W_K/W_V` 投影矩阵；最多一句边界说明：“单头可把 Q/K/V 看作同一输入的不同投影，本集不展开。”（CLM-011，secondary only）

## 6. 唯一动画段落的教学任务

- 名称：`[ANIMATION: scores_to_weights]`
- 目标时长：60–75 秒（框架要求 45–90 秒）。
- 教学任务：用 4 个 token 展示
  `QK^T → /√d_k → 行 softmax → A`。
- 对比重点：`t1` 行对 `k1` 的权重约 0.870（集中）；`t3` 行四个 key 均为 0.25（均匀）。
- 段落边界：动画停在权重矩阵 `A`；**输出 `O=AV` 放在下一静态页（第 6 模块）收束**，避免段落过长。
- 不进入动画：Q/K/V 投影、多头、mask、位置编码、训练、代码实现。
- 该段落只依赖 `03-knowledge-structure.md` 第 5 节的最小公式子集；不实现 Motion/Reveal。

## 7. 范围与明确不做

本集只讲**单头 self-attention 的核心直觉与计算骨架**：

- Q/K/V 角色与同源；
- score、缩放、行 softmax、weight、`O=AV`；
- 4-token 玩具例子；
- √d_k 的论文动机与假设下的方差推导（分层表述）。

明确不做：

- 多头、head 拼接、输出投影；
- mask、cross-attention、完整 Encoder–Decoder；
- 位置编码、LayerNorm、残差、FFN；
- 训练、反向传播、优化器、dropout；
- 代码实现、性能、变体综述、历史。

Manim 不启用；OBS 不调用。S1 只写讲稿，不改 Reveal/Motion。
