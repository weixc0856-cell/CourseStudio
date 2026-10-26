# 01 — Source Inventory

- 项目：`transformer-self-attention`
- 日期：2026-10-26
- 阶段：R1 来源登记
- 范围：单头 self-attention；Q/K/V 角色；score → weight；√d_k；4-token 玩具例子
- 状态：来源已登记；**R2–R4 已完成，研究 Gate PASS_VERIFIED**；讲稿、课件或动画未写
- 说明：本文件只登记来源与可引用位置，不把来源内容写成已核实主张；主张进入 R2 台账后才可用于讲稿。

## 1. 检索与访问日志

| ID | 操作 | 查询 / URL | 结果 | 记录 |
| --- | --- | --- | --- | --- |
| Q01 | `paper-search search`，源 `arxiv`，`-n 5` | `"Attention Is All You Need"` | 5 条；原始论文在 `papers[1]`，ID `1706.03762v7` | `01_research/search-results/q01-arxiv-attention-is-all-you-need.json` |
| Q02 | `paper-search download arxiv 1706.03762` | arXiv PDF | `status=ok`；`1706.03762.pdf`，2,215,244 bytes | `01_research/search-results/q02-download-arxiv-1706.03762.json` |
| Q03 | 直接访问二次材料 | 两个 URL（见下） | 均 HTTP 200；保存 HTML 快照 | `01_research/search-results/q03-secondary-explainers.json` |
| Q04 | √d_k 补充来源决策 | 原始论文 §3.2.1 + S03 代码 | 未额外收集第三份来源；理由见记录 | `01_research/search-results/q04-sqrt-dk-source-decision.json` |

Q01 的 5 条结果中有若干同名/衍生标题（如 Tool Attention、Not All Attention 等）；原始论文按 **arXiv ID + 标题 + 作者列表** 选中，未把其他结果当作来源。

## 2. 来源清单

### S01 — 原始论文（主证据）

| 字段 | 内容 |
| --- | --- |
| 类型 | 原始论文（primary） |
| 标题 | Attention Is All You Need |
| 作者 | Ashish Vaswani; Noam Shazeer; Niki Parmar; Jakob Uszkoreit; Llion Jones; Aidan N. Gomez; Lukasz Kaiser; Illia Polosukhin |
| 年份 | 2017（arXiv v7；记录更新日期 2023-08-02） |
| 标识 | `arXiv:1706.03762v7`；arXiv 记录无 DOI |
| URL | `https://arxiv.org/abs/1706.03762v7`；PDF `https://arxiv.org/pdf/1706.03762v7` |
| 访问状态 | **已下载**：PDF 2,215,244 bytes；`pdfinfo` 显示 16 页；已提取全文 |
| 本地路径 | `01_research/downloads/1706.03762.pdf`；`01_research/fulltext/1706.03762.txt`（均不提交） |
| SHA-256 | `bdfaa68d8984f0dc02beaca527b76f207d99b666d31d1da728ee0728182df697` |
| 本集相关性 | §3.2.1 Scaled Dot-Product Attention（PDF p.4 / printed p.4）：Q/K/V、点积、缩放、softmax、加权和、公式 (1)；Figure 2 left（p.4）；footnote 4（p.4）：点积方差/softmax 梯度动机；§3.2.3（p.5）：self-attention 中 Q/K/V 来自同一处 |
| 主证据候选 | **§3.2.1 p.4**（Q/K/V 维度、点积、缩放、softmax、公式 (1)、输出）；**footnote 4 p.4**（√d_k 动机）；**§3.2.3 p.5**（self-attention 定义）；**Figure 2 left p.4**（结构图） |
| 仅边界/不展开 | §3.2.2 Multi-Head Attention（p.4–5）、§3.2.3 中 decoder masking/cross-attention（p.5）、§3.3 FFN、§3.4 Embeddings（p.5）——只用于说明“不在本集范围”，不作为本集主张证据 |

### S02 — 二次讲解（直觉核对）

| 字段 | 内容 |
| --- | --- |
| 类型 | 高质量二次讲解（secondary；博客） |
| 标题 | The Illustrated Transformer |
| 作者 | Jay Alammar |
| 年份 | 2018 |
| URL | `https://jalammar.github.io/illustrated-transformer/` |
| 访问状态 | **可访问（已保存 HTML 快照）**：HTTP 200；47,552 bytes |
| 本地路径 | `01_research/downloads/illustrated-transformer.html`（不提交） |
| SHA-256 | `375d8acf1096832ddfff288d93ff0ace405b6a4897bb96e280e6d71f3d353556` |
| 本集相关性 | `#self-attention-at-a-high-level`：self-attention 的直觉；`#self-attention-in-detail`：从词向量生成 Q/K/V、score、softmax、加权和；`#matrix-calculation-of-self-attention`：X → Q/K/V 矩阵形式 |
| 主证据候选 | 仅作 **直觉/表述交叉核对**，不替代 S01；可对照 Q/K/V 的“查询/键/值”直觉与 score→weight 的逐步解释 |
| 仅边界/不展开 | `#the-beast-with-many-heads`、positional encoding、residuals、decoder、training；其 512/64 维度是 **multi-head architecture choice**，不要写成单头硬性要求 |

### S03 — 二次教材/代码核对（公式与实现）

| 字段 | 内容 |
| --- | --- |
| 类型 | 教材级 annotated paper / 代码讲解（secondary） |
| 标题 | The Annotated Transformer |
| 作者 | v2022: Austin Huang; Suraj Subramanian; Jonathan Sum; Khalid Almubarak; Stella Biderman；original 2018: Sasha Rush |
| 年份 | 2022（当前版本；原始 2018） |
| URL | `https://nlp.seas.harvard.edu/annotated-transformer/` |
| 访问状态 | **可访问（已保存 HTML 快照）**：HTTP 200；9,453,410 bytes |
| 本地路径 | `01_research/downloads/annotated-transformer.html`（不提交） |
| SHA-256 | `ee355423ba684165fca361da0f3d3b1c8fd0c79964732116af54d2f2ed73cb4a` |
| 本集相关性 | “Attention” 节：Scaled Dot-Product Attention 的文字与公式；代码标记 `scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)`、`p_attn = scores.softmax(dim=-1)`；“Applications of Attention in our Model” 可核对 self-attention 定义 |
| 主证据候选 | 仅作 **公式/代码交叉核对**，不替代 S01；可用于确认 softmax 是在最后一维（keys）上做、缩放因子位置、输出为 `p_attn @ value` |
| 仅边界/不展开 | Multi-Head Attention、masking、training、decoding；代码中的 mask/dropout 路径不在本集范围 |

## 3. 后续主张的主证据候选映射

| 候选主题 | 首选证据位置 | 用途 | R2/R3 注意 |
| --- | --- | --- | --- |
| Q/K/V 的维度与角色 | S01 §3.2.1 p.4 | 主证据 | 论文把 Q/K/V 作为 attention 输入；不要把 §3.2.1 直接表述为“X 乘三个矩阵”的单头定义 |
| score = query 与 key 的点积 | S01 §3.2.1 p.4，公式 (1) | 主证据 | `pdftotext` 会丢失根号；R3 以 PDF 视觉/HTML/公式为准 |
| 缩放 √d_k | S01 §3.2.1 p.4 + footnote 4 p.4 | 主证据 | 论文给出方差/gradient 动机；S03 代码仅交叉核对 |
| 行 softmax 得到权重 | S01 §3.2.1 p.4；S03 `softmax(dim=-1)` | 主证据 + 代码核对 | 要说明“每个 query 一行、对 keys 归一化”；不要只说“softmax” |
| 加权求和得到输出 | S01 §3.2.1 p.4；S02 `#self-attention-in-detail` | 主证据 + 直觉核对 | 输出是 values 的加权和，权重来自该行 |
| self-attention 的 Q/K/V 来自同一处 | S01 §3.2.3 p.5 | 主证据（定义） | 与 encoder-decoder/cross-attention 区分；decoder masking 不在本集 |
| Q/K/V 是 X 的线性投影 | S02 `#self-attention-in-detail` / `#matrix-calculation-of-self-attention`；S03 “Attention” 代码 | **二次教学框架** | S01 §3.2.2 的投影在 multi-head 语境；R2/R3 需明确“单头教学抽象”，不要把 multi-head 的 h/维度写成单头要求 |
| 为什么按行 softmax | S01 公式 (1)；S03 `softmax(dim=-1)` | 主证据 + 代码核对 | 行 = query；列 = key；权重和为 1 |

## 4. 范围外 / 仅作边界

- **S01**：§3.2.2 Multi-Head Attention（p.4–5）、§3.2.3 的 decoder masking/cross-attention（p.5）、§3.3 FFN、§3.4 Embeddings（p.5）。
- **S02**：multi-head、positional encoding、residuals、decoder、training；其 512/64 维度不作为单头要求。
- **S03**：Multi-Head Attention、masking、training/decoding；代码中的 mask/dropout 分支不进入本集。
- 以上内容如需在讲稿中提及，只能作为一句边界说明，不进入推导或动画。

## 5. 访问状态与可复现性

- S01 为开放 arXiv；S02/S03 为开放网页；本次未遇到付费墙或登录限制。
- 原始 PDF、HTML 快照与提取全文放在 `01_research/downloads/` 与 `01_research/fulltext/`；课程 `.gitignore` 排除这些目录，不提交。
- 检索/访问记录 JSON 放在 `01_research/search-results/`，随课程保留。
- 所有快照记录 SHA-256；重新下载时可核对版本是否漂移。

## 6. R2–R4 衔接 / S1 待执行

- R2 已建立 `02-claim-evidence-ledger.csv`（14 条：7 FACT / 1 CLAIM / 5 INFERENCE / 1 ASSUMPTION）；R3 已建立 `03-knowledge-structure.md`（符号表冻结、4-token 例子固定）；R4 已建立 `04/05/06`，研究 Gate PASS_VERIFIED。
- 未改讲稿、Reveal、Motion、`05_recording`；未启用 Manim；未调用 OBS。
- R3 将核对符号、公式、形状与 4-token 玩具数字，重点处理：
  1. `pdftotext` 丢失根号的问题；
  2. 单头教学抽象与 S01 multi-head 投影语境的区分；
  3. 4-token 玩具数值的可复算性；
  4. 是否需要在后续补一份独立的 √d_k 解释来源（当前 S01 footnote 4 + S03 代码已足够）。
