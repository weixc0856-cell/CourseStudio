# 03 — Knowledge Structure

- 项目：`transformer-self-attention`
- 日期：2026-10-26
- 阶段：R3 知识结构/公式
- 状态：**符号表已冻结；4-token 玩具例子已固定**；R4 大纲、讲稿、课件、动画未写
- 依据：S01（主证据）、S02/S03（教学/代码交叉核对）、`02-claim-evidence-ledger.csv` 的 CLM-001–CLM-014
- 规则：公式与台账冲突时，以 S01 §3.2.1/§3.2.3 原文为准并回注 CLM；本文件不写未登记的新主张

## 1. 符号表（全集聚拢，冻结）

| 符号 | 含义 | 形状 / 取值 | 本集范围 | 相关 CLM |
| --- | --- | --- | --- | --- |
| `X` | 输入序列矩阵，每行一个 token 的向量 | `n × d_model` | **本集不展开投影**；概念符号，玩具例子直接从 Q/K/V 开始 | CLM-011（教学框架，不用于推导） |
| `n` | 序列长度 | 玩具 `n = 4` | 单头玩具设定 | CLM-014 |
| `d_model` | 输入/嵌入维度 | 概念符号；玩具不使用具体值 | **本集不强调**；不把 512 当单头要求 | CLM-011、CLM-013 |
| `Q` | queries 矩阵；第 `i` 行 `q_i` 是 token `i` 的 query | `n × d_k` | 单头 | CLM-001、CLM-003、CLM-011 |
| `K` | keys 矩阵；第 `j` 行 `k_j` 是 token `j` 的 key | `n × d_k` | 单头 | CLM-001、CLM-003、CLM-005 |
| `V` | values 矩阵；第 `j` 行 `v_j` 是 token `j` 的 value | `n × d_v` | 单头 | CLM-001、CLM-010 |
| `d_k` | query/key 维度 | 玩具 `d_k = 4`；`√d_k = 2` | 单头玩具设定；不是 64 | CLM-006、CLM-008、CLM-013 |
| `d_v` | value 维度 | 玩具 `d_v = 2` | 单头玩具设定 | CLM-010 |
| `s_ij` | query `i` 与 key `j` 的原始 score（点积） | 标量 | 单头 | CLM-005 |
| `S` | score 矩阵，`S_ij = s_ij` | `n × n` | 单头 | CLM-005 |
| `√d_k` | score 的缩放分母 | 玩具为 `2` | 单头 | CLM-006、CLM-007、CLM-008 |
| `\tilde{s}_{ij}` | 缩放后的 score，`s_ij/√d_k` | 标量 | 单头 | CLM-006 |
| `α_ij` | 注意力权重（softmax 后） | 标量；`α_ij ≥ 0`，`Σ_j α_ij = 1` | 单头 | CLM-009 |
| `A` | 权重矩阵，`A_ij = α_ij` | `n × n`；行和为 1 | 单头 | CLM-009 |
| `o_i` | token `i` 的输出向量 | `d_v` 维 | 单头 | CLM-010 |
| `O` | 输出矩阵，第 `i` 行 `o_i` | `n × d_v` | 单头 | CLM-010 |
| `W_Q, W_K, W_V` | 可选投影矩阵 | `d_model × d_k`、`d_model × d_k`、`d_model × d_v` | **仅教学框架；本集不展开** | CLM-011（secondary only） |
| `h` | 头数 | 原文 `h = 8` | **本集不进入**；仅边界说明 | CLM-012 |

**只用于单头玩具例子的符号/值**：`n = 4`、`d_k = 4`、`d_v = 2`、`q_i/k_j/v_j`、`S`、`A`、`O` 的具体数值。它们不是 S01 的超参数，也不代表训练好的模型。

## 2. 核心公式（与 CLM 对齐）

### 2.1 形式定义

对单头 self-attention：

```text
s_ij = q_i · k_j
S = Q K^T
\tilde{s}_ij = s_ij / √d_k
α_ij = exp(\tilde{s}_ij) / Σ_{l=1..n} exp(\tilde{s}_il)
A = row_softmax(S / √d_k)
o_i = Σ_{j=1..n} α_ij v_j
O = A V
```

合并写法：

```text
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

其中 `softmax` 按每一行（每个 query 对所有 keys）执行。来源与台账：

| 公式/性质 | 主证据 | 类型 / 说明 |
| --- | --- | --- |
| `s_ij = q_i · k_j`，`S = QK^T` | S01 §3.2.1 p.4；CLM-005 | FACT：原文“compute the dot products of the query with all keys” |
| `S / √d_k` | S01 §3.2.1 p.4，公式 (1)；CLM-006 | FACT：原文“divide each by √d_k” |
| `A = row_softmax(S/√d_k)`，`Σ_j α_ij = 1` | S01 公式 (1)；S03 `softmax(dim=-1)`；CLM-009 | INFERENCE + 代码核对：行方向由公式/代码确定 |
| `o_i = Σ_j α_ij v_j`，`O = A V` | S01 公式 (1)；CLM-010 | FACT：输出是 values 的加权和 |
| `Attention(Q,K,V)=softmax(QK^T/√d_k)V` | S01 公式 (1)；CLM-001/003/006/009/010 | FACT（方法定义）；根号以 PDF/公式视觉为准 |
| Q/K/V 同源 | S01 §3.2.3 p.5；CLM-002 | FACT：encoder self-attention 的 Q/K/V 来自同一处 |
| Q/K/V 为 X 的线性投影 | S02/S03；CLM-011 | **INFERENCE / pedagogical framing**：S01 §3.2.1 不展开；S01 §3.2.2 是 multi-head 语境；本集不用于推导 |
| 多头 `h=8`、`d_k=64` | S01 §3.2.2 p.5；CLM-012/013 | FACT（边界）；**本集不进入**；S02 的 “divide by 8/64” 仅作 multi-head caveat |

### 2.2 √d_k 的动机（分层表述）

1. **原文方法陈述（FACT，CLM-006）**：S01 在 softmax 前把点积除以 `√d_k`。
2. **原文明说的动机（CLAIM，CLM-007）**：原文写 “We suspect that for large values of d_k, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients. To counteract this effect, we scale the dot products by 1/√d_k.” 这是论文的**理由陈述**，不是独立实验结果。
3. **脚注推导（INFERENCE，CLM-008）**：在 footnote 4 的假设下——`q`/`k` 各分量独立、均值 0、方差 1——点积 `q·k` 的均值为 0、方差为 `d_k`。因此 `d_k` 越大，点积幅度越大；缩放使方差回到约 1，避免 softmax 进入梯度很小的饱和区。该推导依赖显式假设，不应推广到所有训练分布。
4. **不把 CLAIM 说成 FACT**：讲稿应说“论文的动机是……”而不是“已被证明对所有模型成立”。

> `pdftotext` 会丢失公式/脚注中的根号；本文件的 `√d_k` 以 PDF p.4 的视觉公式、S03 渲染公式与代码 `math.sqrt(d_k)` 为准。CLM-006/007/008 的 notes 已记录该限制。

## 3. 形状与维度约定

### 3.1 一般单头

| 量 | 形状 | 说明 |
| --- | --- | --- |
| `Q` | `n × d_k` | 每行一个 query |
| `K` | `n × d_k` | 每行一个 key |
| `V` | `n × d_v` | 每行一个 value |
| `S = QK^T` | `n × n` | `S_ij` 是 query `i` 对 key `j` 的 score |
| `A = softmax(S/√d_k)` | `n × n` | 每行和为 1；行 = query，列 = key |
| `O = AV` | `n × d_v` | 每行是 value 的加权和 |

### 3.2 玩具设定（冻结）

| 量 | 形状 / 值 |
| --- | --- |
| `n` | 4 |
| `d_k` | 4（`√d_k = 2`） |
| `d_v` | 2 |
| `Q, K` | `4 × 4` |
| `V` | `4 × 2` |
| `S, A` | `4 × 4` |
| `O` | `4 × 2` |

### 3.3 教学简化与原文 multi-head 边界

- 本集只讲**单头**。S01 的完整模型使用 multi-head（`h = 8`，每头 `d_k = d_v = 64`，§3.2.2 p.5；CLM-012）。
- S01 §3.2.1 把 Q/K/V 作为 attention 的输入；它没有给出“单头 `Q=XW_Q`”的完整定义。`Q=XW_Q` 等投影是 S02/S03 的教学框架（CLM-011），本集**不作为推导前提**。
- S02 的 “divide by 8 / 512→64” 是 multi-head 架构示例（CLM-013），不是单头常数；本集玩具用 `d_k = 4, √d_k = 2`，并明确标注为 illustrative。
- 本集不把 `d_k=64`、`h=8`、`d_model=512` 写成单头要求。

## 4. 4-token 玩具例子（固定，ASSUMPTION / illustrative only；CLM-014）

设定：`n=4`，`d_k=4`，`d_v=2`，`√d_k=2`。4 个 token 记为 `t1..t4`。数字是手工设定的小整数，不是训练结果，也不代表 S01 的超参数。

### 4.1 Q / K / V

```text
Q =
[ 3  0  0  0 ]   # q1
[ 0  2  1  0 ]   # q2
[ 1  1  1  1 ]   # q3
[ 0  0  1  2 ]   # q4

K =
[ 2  0  0  0 ]   # k1
[ 0  2  0  0 ]   # k2
[ 0  0  2  0 ]   # k3
[ 0  0  0  2 ]   # k4

V =
[ 1  0 ]         # v1
[ 0  1 ]         # v2
[ 1  1 ]         # v3
[ 2  0 ]         # v4
```

### 4.2 score 矩阵 `S = QK^T`

```text
S =
[ 6  0  0  0 ]   # q1·k = 6,0,0,0
[ 0  4  2  0 ]   # q2
[ 2  2  2  2 ]   # q3
[ 0  0  2  4 ]   # q4
```

### 4.3 缩放 `S / √d_k = S / 2`

```text
scaled =
[ 3.0  0.0  0.0  0.0 ]
[ 0.0  2.0  1.0  0.0 ]
[ 1.0  1.0  1.0  1.0 ]
[ 0.0  0.0  1.0  2.0 ]
```

### 4.4 行 softmax 得到 `A`

```text
A =
[ 0.870049  0.043317  0.043317  0.043317 ]   # t1 明显关注 k1
[ 0.082595  0.610296  0.224515  0.082595 ]   # t2 关注 k2
[ 0.250000  0.250000  0.250000  0.250000 ]   # t3 均匀
[ 0.082595  0.082595  0.224515  0.610296 ]   # t4 关注 k4
```

每行和 = 1。对比：`t1` 对 `k1` 的权重约 `0.870`，而 `t3` 对四个 key 都是 `0.25`；这说明“score 大 → softmax 权重集中”和“score 相同 → 权重均匀”。

### 4.5 加权求和得到 `O = A V`

```text
O =
[ 1.000000  0.086634 ]   # o1
[ 0.472299  0.834811 ]   # o2
[ 1.000000  0.500000 ]   # o3
[ 1.527701  0.307110 ]   # o4
```

### 4.6 逐步示例

**第 1 行（t1）**：

1. `q1·k1..k4 = [6,0,0,0]`；
2. 缩放 `/2 → [3,0,0,0]`；
3. `exp → [20.085537, 1, 1, 1]`，和 `23.085537`；
4. `A_1 = [0.870049, 0.043317, 0.043317, 0.043317]`；
5. `o1 = 0.870049·v1 + 0.043317·v2 + 0.043317·v3 + 0.043317·v4 = [1.000000, 0.086634]`。

**第 3 行（t3）**：

1. `q3·k1..k4 = [2,2,2,2]`；
2. 缩放 `/2 → [1,1,1,1]`；
3. `exp → [e,e,e,e]`，等权；
4. `A_3 = [0.25,0.25,0.25,0.25]`；
5. `o3 = 0.25·v1 + 0.25·v2 + 0.25·v3 + 0.25·v4 = [1.0,0.5]`。

### 4.7 复算脚本（与上面数值一致）

```python
import math

Q = [[3,0,0,0],[0,2,1,0],[1,1,1,1],[0,0,1,2]]
K = [[2,0,0,0],[0,2,0,0],[0,0,2,0],[0,0,0,2]]
V = [[1,0],[0,1],[1,1],[2,0]]
n, dk, dv = 4, 4, 2

S = [[sum(Q[i][t]*K[j][t] for t in range(dk)) for j in range(n)] for i in range(n)]
scaled = [[x / math.sqrt(dk) for x in row] for row in S]
A = []
for row in scaled:
    ex = [math.exp(x) for x in row]
    z = sum(ex)
    A.append([e / z for e in ex])
O = [[sum(A[i][j]*V[j][t] for j in range(n)) for t in range(dv)] for i in range(n)]
```

## 5. 动画 `scores_to_weights` 的最小公式子集

该段落只依赖：

1. `s_ij = q_i · k_j` / `S = QK^T`；
2. `S / √d_k`（玩具中 `/2`）；
3. 行 softmax `A`；
4. `O = AV`（加权求和）。

建议叙事顺序：

- 先展示 4 个 token 与 Q/K 行，说明“同一行 query 对所有 key 做点积”；
- 建立 `S` 的 4×4 数字；
- 展示 `/√d_k` 后的缩放；
- 对比 `t1` 行的集中权重（`k1 ≈ 0.870`）与 `t3` 行的均匀权重；
- 用 `A·V` 得到 `o1/o3`，说明输出是 value 的混合。

不进入该段落：投影矩阵 `W_Q/W_K/W_V`、多头、mask、位置编码、训练、代码实现。候选名 `scores_to_weights`、目标 60–75 秒，来自 `00-task-brief.md` 与 `CLM-014`；这里只点名，不实现 Motion。

## 6. 未决与禁区（R4 之前）

仍不进入本集：

- 多头、head 拼接、输出投影；`h=8`/`d_k=64` 只作边界。
- Encoder–Decoder、cross-attention、decoder masking、padding mask。
- 位置编码、LayerNorm、残差、FFN。
- 训练、反向传播、优化器、dropout、学习率。
- KV cache、推理加速、FlashAttention、线性注意力等变体。
- 代码实现、框架 API、性能 benchmark、综述/历史。

R3 已解决/固定：

- 符号表冻结（`S`、`A`、`O`、`s_ij`、`α_ij`、`o_i` 等）。
- 4-token 数值固定，可复算；`CLM-014` 标明 illustrative。
- 单头 `d_k=4` 与原文 `h=8/d_k=64` 的边界写清；`CLM-011/012/013` 回注。
- `pdftotext` 根号限制已在 `CLM-006/007/008` notes 与本文件 2.2 记录。

R4 仍需决定：大纲模块划分、是否展示投影矩阵（当前建议不展示）、动画与静态页的分工、最终时长。R3 不写 `04-course-input-brief.md`、`05-quality-report.md`、`06-course-outline.md`；不写讲稿；不改 Reveal/Motion；不启用 Manim；不调用 OBS。
