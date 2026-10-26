# 00 — Task Brief: Transformer Self-Attention

- 项目：`transformer-self-attention`
- 模式：`course`
- 日期：2026-10-26
- 状态：任务边界冻结；**R1–R4 研究、S1–S4 讲稿、Motion 场景、录制就绪包与 Reveal P2 正文均已完成；slides/QA 通过**；下一步整体验收与人工 OBS 准备
- 说明：本文件只定义范围与目标，不写未登记的事实主张；所有事实/公式/数字在 R1–R3 进入台账后才可作为讲稿依据。

## 1. 核心问题

1. Self-Attention 为什么需要 Q / K / V 三个角色，而不是直接比较输入向量？
2. 一个 token 的 score 如何变成它对其他 token 的权重？
3. 为什么 softmax 要按行做、权重为什么要和为 1？
4. 加权求和后的输出，直观上代表什么？

## 2. 受众

- 有一定深度学习基础：理解张量、矩阵乘法、点积、softmax、损失与反向传播的概念。
- 知道 Transformer 是序列模型，但**不是注意力专家**；可能看过结构图，但说不清 Q/K/V 的具体作用。
- 不需要读者手推梯度，也不要求实现过 attention。

## 3. 学习目标

看完本集，读者应能独立讲清：

1. **Q/K/V 的角色**：Query 是“我在找什么”，Key 是“我能提供什么”，Value 是“我实际被取用的内容”；三者都是输入 X 的线性投影。
2. **score → weight 的含义**：score 表示 query 与 key 的匹配程度；按 query 所在行做 softmax，得到该 token 对其他 token 的注意力权重。
3. **计算骨架**：能从形状层面走通
   `X → Q,K,V → QK^T/√d_k → 行 softmax → 加权求和 V`。
4. **权重性质**：每一行权重非负、和为 1；高权重意味着该 key 对应的 value 对当前 token 的输出贡献更大。
5. **缩放因子**：能说明除以 `√d_k` 是为了控制点积随维度增大的方差，而不是改变“相似度”的语义（细节由 R3 核对）。

## 4. 范围

本集只覆盖**单头 self-attention 的核心直觉与计算骨架**：

- 一个长度为 `n` 的序列，一个玩具例子（计划 4 个 token）。
- `X [n, d_model]`、`W_Q/W_K/W_V [d_model, d_k]`、`Q/K/V [n, d_k]`。
- `scores = QK^T / √d_k` 的形状 `[n, n]`。
- 逐行 softmax 得到 `weights [n, n]`。
- `output = weights · V`，形状 `[n, d_v]`。
- 用几何/逐步构建解释：点积作为相似度、行作为 query、列作为 key、softmax 作为归一化、加权和作为混合。
- 目标公式（符号与适用条件待 R3 核对）：

  ```text
  Attention(Q, K, V) = softmax(QK^T / √d_k) V
  ```

- 预计成片 8–12 分钟（待 R4 大纲确认）；只做 **1 个 Motion 段落**，其余由 Reveal 静态页与口播承担。

## 5. 明确不做什么

本集**不展开**以下内容；如讲稿需要提及，只能作为一句边界说明，不进入推导或动画：

- 多头注意力、head 拼接、输出投影。
- 完整 Encoder–Decoder、cross-attention。
- 因果掩码 / padding mask / 训练时的 mask 细节。
- 位置编码、LayerNorm、残差、FFN。
- 训练、反向传播、优化器、dropout、学习率。
- KV cache、推理加速、FlashAttention、线性注意力等变体。
- 代码实现、框架 API、性能 benchmark。
- 论文综述、历史沿革、与 RNN/CNN 的全面对比。
- 任何“教学效果已验证”的声明；没有人工评审就写 `NOT_RUN`。

## 6. 唯一 Motion 段落候选

**一句话**：用 4 个 token 的玩具序列，把 score 矩阵逐行 softmax 成权重，再用权重条与加权求和展示“分数如何变成权重”。

- 目标时长：60–75 秒（落在 45–90 秒内）。
- 录制入口：`04_motion_src/record.html?segment=<name>`；不嵌入 Reveal，不默认渲染 MP4。
- 段落名在 M1 冻结时写入 `segments.json`；候选名 `scores_to_weights`。

## 7. 交付形态

- 1 个 course episode：`courses/transformer-self-attention/`。
- 1 个 Motion 段落（45–90 秒），独立录屏。
- 1 套 Reveal 课件（course 默认），动画页只放占位与前后衔接说明。
- 1 个 `05_recording/` 录制就绪包（manifest / cues / checklist）。
- 不使用 Manim；OBS 由人工录制，AI 不安装、不调用。

## 8. 成功标准

- 读者能用自己的话解释 Q/K/V 的角色，以及 score → softmax → weighted sum 的含义。
- 公式、矩阵形状、玩具数字、讲稿、动画、页面使用同一条事实基线。
- 唯一 Motion 段落 45–90 秒；`--stage motion` 无 Issues。
- Reveal `data-slide` 1..N；`--stage slides` 通过。
- 录制包完整；`--stage recording` 通过；实拍文件不强制存在。
- 未运行/未验证的项标 `NOT_RUN` / `PARTIAL`，不写假 `PASS`。

## 9. 证据与来源策略（R1–R4 与 S1–S3 已完成；S4 待执行）

- R1 优先登记原始 Transformer 论文（Vaswani et al., 2017）与至少一条独立解释来源；本文件不引用具体页码或结论。
- R2 为“Q/K/V 角色、score 含义、softmax 行归一化、缩放因子、输出含义”建立 `CLM-XXX` 台账。
- R3 核对符号、形状、单位/量纲与玩具例子的可复算性。
- 本任务边界不替代来源登记；没有台账的主张不得进入讲稿。

## 10. 风险与未决

- **数学深度**：公式与直觉的顺序；计划先直觉、再公式、再一个 worked example，具体由 R4 大纲定。
- **玩具数字**：4 个 token 的 Q/K/V 与 score 必须在 R3 固定并可复算；不凭记忆写数。
- **单段落承载**：只做 1 个 Motion 段落，score→weight 的核心必须在 60–75 秒内讲清；其余靠静态页与口播。
- **来源可得性**：R1 需确认原始论文与独立解释来源可访问；冲突保留双方证据。
- **范围蔓延**：多头、mask、位置编码、训练细节均不在本集；如需扩展，先由用户确认改任务边界。

## 11. 下一步

R1–R4、S1–S4 与 Motion/录制包已完成：研究包见 `01_research/`，M1–M7 讲稿见 `02_scripts/lecture_script.md`；`segments.json` 为 `scores_to_weights`（68s/order 1）；scene/project/cue/manifest/checklist 已生成；`--stage motion` 与 `--stage recording` 均 PASS_VERIFIED。

**下一步**（待用户确认）：做整体验收与人工 OBS 录制准备；人工复核 12 页、Motion 段落与讲稿的数字/口径一致性。不启用 Manim；OBS 由人工录制，`record_status` 保持 `NOT_RUN`。
