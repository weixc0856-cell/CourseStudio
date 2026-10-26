# Handoff — transformer-self-attention

| 字段 | 内容 |
| --- | --- |
| 模式 | `course` |
| 阶段 | `recording`（内容阶段完成；录制清单收尾；OBS 未运行） |
| 内容阶段 | 完成（research → script → motion → recording package → Reveal P2；slides/QA PASS） |
| 子步骤 | 录制准备收尾（已完成）；下一步仅人工 OBS 录制与后期拼接 |
| 模块进度 | 7 / 7（M1–M7） |
| 段落进度 | 1 / 1 已实现；`record_status=NOT_RUN`，`real=NOT_VERIFIED` |
| 动画引擎 | `motion`（本集不使用 Manim） |
| 课件类型 | Reveal（`03_slides/index.html`，12 页正文完成） |
| 录制包 | 已生成：`manifest.json` / `cues/scores_to_weights.md` / `checklist.md`；清单含实际 URL、order、启动/ffprobe 命令与 OBS 注意事项 |
| 输入文件 | `01_research/04-course-input-brief.md`、`03-knowledge-structure.md`、`02-claim-evidence-ledger.csv`、`06-course-outline.md` |
| 输出文件 | `02_scripts/lecture_script.md`（M1–M7）；`04_motion_src/src/scenes/scores_to_weights.tsx`；`04_motion_src/src/projects/scores_to_weights.ts`；`05_recording/`；`03_slides/index.html`；`03_slides/assets/deck.css` |
| 已运行命令 | R1–R4；S1–S4；`build-recording-package.py`；`motion-run.ps1`；`reveal-run.ps1`；`check-episode --stage motion` / `--stage recording` / `--stage slides` / `--stage qa` / `--stage qa --strict`；headless Chrome Motion seek 抽帧 + Reveal 12 页截图；`check-links` |
| 最后检查 | `--stage slides` / `--stage qa` / `--stage qa --strict` → **PASS_VERIFIED**；Reveal Build **SKIPPED**；`--stage motion` / `--stage recording` PASS；橙白主题下 Motion 探针 68.0s、关键帧抽检；Reveal 12 页抽检；`check-links` PASS；录制清单已复核 |
| 验证状态 | 内容阶段完成；Reveal P2 与 slides/QA **PASS_VERIFIED**；Motion/录制包结构 **PASS_VERIFIED**；橙白视觉已抽检；真实录像、人工音画/全屏、OBS `NOT_RUN` |
| 未决事项 | 人工 OBS 实拍；真实时长/音画同步复核；后期拼接 |
| 下一步 | **仅人工 OBS 录制与后期拼接**；不进入新功能开发，不启用 Manim，不调用 OBS |

> 每次 `/clear` 前更新本文件。下一阶段只读本文件 + 指定输入，不重读整个项目。
>
> OBS 由人工录制；本阶段不安装、不调用 OBS，`record_status` 保持 `NOT_RUN`。
>
> 本集按新主路径新建；未复用、未修改历史 `transformer-course-pilot` 旧产物。

## 任务边界摘要

- **受众**：有深度学习基础（张量、矩阵乘法、点积、softmax、反向传播概念），但不是注意力专家。
- **学习目标**：能独立讲清 Q/K/V 角色、score → softmax → weight 的含义、单头 self-attention 的计算骨架，以及为什么按行归一化。
- **范围**：单头 self-attention；一个 4-token 玩具例子；`S=QK^T → S/√d_k → 行 softmax A → O=AV`。
- **明确不做**：多头、完整 Encoder–Decoder、cross-attention、mask、位置编码、LayerNorm/残差/FFN、训练/反向传播、代码实现、性能、变体综述。
- **唯一 Motion 段落**：`scores_to_weights`，68 秒；`QK^T → /√d_k → 行 softmax → A`，停在 A，不进入 `O=AV`。

## R1 主来源

| ID | 来源 | 访问 | 主证据候选 |
| --- | --- | --- | --- |
| S01 | **Attention Is All You Need**，Vaswani et al., 2017，`arXiv:1706.03762v7` | 已下载 PDF（2,215,244 bytes） | §3.2.1 p.4（Q/K/V、点积、√d_k、softmax、公式 1）；footnote 4 p.4；Figure 2 left；§3.2.3 p.5（self-attention 定义） |
| S02 | **The Illustrated Transformer**，Jay Alammar, 2018 | 可访问，已保存 HTML | `#self-attention-at-a-high-level`、`#self-attention-in-detail`、`#matrix-calculation-of-self-attention` |
| S03 | **The Annotated Transformer**，v2022 / original 2018 Sasha Rush | 可访问，已保存 HTML | “Attention” 节；`math.sqrt(d_k)`、`softmax(dim=-1)`、`p_attn @ value` |

检索/访问记录：`01_research/search-results/q01–q04*.json`；Q04 记录“不额外收集第三份 √d_k 来源”的决定。

## R2 主张台账

`01_research/02-claim-evidence-ledger.csv`：**14 条**（FACT 7 / CLAIM 1 / INFERENCE 5 / ASSUMPTION 1）。

- 核心：CLM-001/003/004/011（Q/K/V 角色与投影）、CLM-005（点积 score）、CLM-006/007/008（√d_k 与动机）、CLM-009（行 softmax）、CLM-010（加权和）。
- 边界：CLM-012/013（multi-head h=8、S02 的 8/64 caveat）、CLM-014（4-token toy 为 ASSUMPTION）。
- 风险处理：CLM-006/007/008 notes 记录 `pdftotext` 丢根号；CLM-011 明确投影是 secondary pedagogical framing，不把 S01 §3.2.2 multi-head 写成单头定义。

## R3 知识结构（已冻结）

`01_research/03-knowledge-structure.md`：

- **符号表冻结**：`X, n, d_model`（不强调/不使用）；`Q,K,V`；`d_k,d_v`；`S,s_ij`；`√d_k`；`A,α_ij`；`O,o_i`；`W_Q/W_K/W_V` 仅教学框架；`h` 仅边界。
- **公式**：`s_ij=q_i·k_j`、`S=QK^T`、`S/√d_k`、`A=row_softmax(S/√d_k)`、`O=AV`、`Attention(Q,K,V)=softmax(QK^T/√d_k)V`；均回注 CLM。
- **√d_k**：CLM-006 方法 FACT；CLM-007 原文 “We suspect” 为 CLAIM；CLM-008 footnote 4 假设下方差 `d_k` 为 INFERENCE；不把动机说成普适事实。
- **玩具例子固定**：`n=4, d_k=4, d_v=2, √d_k=2`；`S`、`scaled`、`A`、`O` 全部给出；`A` 四行和均为 1；`t1` 对 `k1` 权重约 0.870（集中），`t3` 四 key 均 0.25（均匀）。
- **动画最小子集**：`QK^T → /√d_k → 行 softmax → A`；不进入投影、多头、mask、位置编码、训练、`O=AV`。

## R4 大纲冻结摘要

- 文件：`04-course-input-brief.md`、`05-quality-report.md`、`06-course-outline.md`。
- 目标成片 **10.0 分钟**（允许 8–12 分钟）；7 个模块；12 个 `[SLIDE]` 锚点；唯一 `[ANIMATION: scores_to_weights]`。
- 决策：**不展开 Q/K/V 投影矩阵**；唯一 Motion 在 M5，停在 `A`；`O=AV` 在 M6 静态页收束；不进入多头/mask/位置编码/完整 Encoder–Decoder/训练。
- 模块：M1 为什么（1.5）→ M2 Q/K/V（2.0）→ M3 score（1.5）→ M4 √d_k（1.0）→ M5 softmax/weight + 动画（2.0）→ M6 output（1.5）→ M7 边界（0.5）。
- 研究 Gate：`--stage research` **PASS_VERIFIED**（00–06 齐、非空；退出码 0）。

## 讲稿与动画摘要

- 文件：`02_scripts/lecture_script.md`；**M1–M7**，`[SLIDE: 01]`–`[SLIDE: 12]`。
- 唯一动画：M5 `scores_to_weights`，`[SEGMENT: scores_to_weights | 68s | order=1]`。
- 节奏：`[VISUAL 00:00]` → `[HOLD 00:08]` → `[EMPHASIS 00:20]` → `[CUT 00:34]` → `[EMPHASIS 00:48]` → `[VISUAL 01:02]`；时间戳严格递增，最后 62s ≤ 68s。
- 动画语义：score 矩阵 → 除以 2 → 逐行 softmax → `t1` 集中 / `t3` 均匀 → 停在 `A`；没有 `O=AV`。
- 动画数值来自 R3：`S` / `scaled` / `A` 与讲稿一致；显示值四舍五入到 3 位小数。

## Motion 实现

- 场景：`04_motion_src/src/scenes/scores_to_weights.tsx`；工程：`04_motion_src/src/projects/scores_to_weights.ts`。
- 画布：1920×1080 / 60fps；`segments.json` 声明 68s / order 1。
- 结构：四个 token 行、`S` 矩阵、缩放公式、`A` 矩阵、逐行 softmax 箭头；A 矩阵逐行揭示，`t1` 与 `t3` 高亮。
- 时长控制：场景内 `beat()` 记录每个动画节拍，`holdTo()` 对齐 `00:08`、`00:12`、`00:20`、`00:34`、`00:37`、`00:40`、`00:43`、`00:46`、`00:56`、`01:02`、`01:05`；末尾断言总时长 68s。
- 主题：橙白 token（`theme.ts`）、显式 `theme.fontFamily` / `theme.monoFamily`；无粒子、无 3D、无装饰运镜。
- 视觉抽查：橙白主题下用 headless Chrome CDP seek 到 8s / 35s / 50s / 64s / 67s 并截图；矩阵白底、深灰边框、深色文字，橙色关键行可读。

## 录制就绪包

- `tools/build-recording-package.py transformer-self-attention` → `Status: WRITTEN`。
- `05_recording/manifest.json`：1 段，`record_status=NOT_RUN`，URL `http://localhost:9100/record.html?segment=scores_to_weights`，declared 68s。
- `05_recording/cues/scores_to_weights.md`：6 个节拍，含口播。
- `05_recording/checklist.md`：段落表已刷新为 `scores_to_weights`；已补全实际 URL、order=1、启停命令、OBS 输出路径、ffprobe 命令与 OBS 注意事项。
- 运行器：`motion-run.ps1` 打印 `record.html?segment=scores_to_weights`；Vite 在 `localhost:9100` 正常服务。
- 播放器探针：`ready=true`，`durationFrames=4080`，`fps=60`，`seconds=68`，`loop=false`。
- 未生成 `recordings/` 媒体文件；OBS 实拍由人工完成。

## Reveal P2 正文

- 文件：`03_slides/index.html` + `03_slides/assets/deck.css`。
- 12 个 `<section class="c-slide" data-slide="01" … "12">`，与讲稿 `[SLIDE: 01]`–`[SLIDE: 12]` 一一对应。
- 01–07、10–12 已填充正文、关键公式与 R3 toy 数字；每页一个主要教学点，未粘贴整段讲稿。
- 08/09 保留 M5 动画占位：`scores_to_weights`、68s、`record.html?segment=scores_to_weights`、独立录屏、不嵌入 MP4。
- 12 页均使用本地 `.vendor/reveal`（`theme/white.css`）与 `assets/deck.css`；橙白视觉、无远程字体/脚本、高对比 1920×1080。
- `Reveal.initialize` 保持录制友好：1920×1080、margin 0、center false、controls/progress/slideNumber false、transition none、hash true。
- 视觉抽查：橙白主题下 headless Chrome 逐页截图检查 12 页；修正 06 矩阵居中、08 “每行和”位置、05 表头大小写。

## 检查记录

```text
--stage slides     -> PASS_VERIFIED (12/12 mapping; Issues empty; local assets OK)
--stage qa         -> PASS_VERIFIED (Issues empty)
--stage qa --strict-> PASS_VERIFIED (Build: SKIPPED — Reveal deck)
--stage motion     -> PASS_VERIFIED (Issues empty; scene/project/cue OK; declared=68.0s; real=NOT_VERIFIED)
--stage recording  -> PASS_VERIFIED (manifest/checklist/cues_dir OK; recordings=0)
record.html probe  -> 68.0s (4080 frames @ 60 fps)
check-links        -> PASS_VERIFIED
```

## 下一步（仅人工 OBS 录制与后期拼接）

1. 运行 `motion-run.ps1 -Episode transformer-self-attention -Segment scores_to_weights`，按清单打开 `record.html?segment=scores_to_weights`。
2. 人工用 OBS 录制：1920×1080、60fps，Display Capture 或 Windows Graphics Capture；录前后各留 2 秒静止。
3. 用清单中的 `ffprobe` 命令读取真实时长，抽帧检查开头/中间/结尾与音画同步。
4. 回填 `05_recording/manifest.json` 的 `record_status` 与真实时长；未录制前保持 `NOT_RUN`。
5. 后期拼接；不进入新功能开发，不启用 Manim，不调用 OBS。
