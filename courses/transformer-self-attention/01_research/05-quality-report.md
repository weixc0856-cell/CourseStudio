# 05 — Quality Report

- 项目：`transformer-self-attention`
- 日期：2026-10-26
- 阶段：R4 研究收束；S1–S4 讲稿；Motion 实现与录制就绪包；Reveal P2 正文
- 结论口径：**研究输入包、M1–M7 讲稿、唯一 Motion 场景、录制就绪包与 Reveal P2 正文已完成；OBS 实拍、人工音画/教学效果未完成**
- 研究 Gate：**PASS_VERIFIED**（00–06 齐、非空；2026-10-26）

## 1. 已完成

| 项 | 状态 | 证据 |
| --- | --- | --- |
| 任务边界 `00-task-brief.md` | 完成 | 受众、目标、范围、禁区、唯一 Motion 候选 |
| 来源登记 `01-source-inventory.md` | 完成 | S01 已下载 PDF；S02/S03 HTTP 200；检索 JSON q01–q04 |
| 主张台账 `02-claim-evidence-ledger.csv` | 完成 | 14 条；FACT 7 / CLAIM 1 / INFERENCE 5 / ASSUMPTION 1 |
| 知识结构 `03-knowledge-structure.md` | 完成 | 符号表冻结；公式与 CLM 对齐；形状约定 |
| 4-token 玩具例子 | 完成（illustrative） | `n=4,d_k=4,d_v=2,√d_k=2`；`S`/`A`/`O` 已复算；四行权重和 = 1 |
| 课程输入简报 `04-course-input-brief.md` | 完成 | 受众、目标、叙事线、证据基线、动画任务 |
| 课程大纲 `06-course-outline.md` | 完成 | 7 模块；10.0 分钟；12 个 slide 锚点；唯一 Motion 在 M5 |
| 讲稿 M1–M7 | 完成 | `02_scripts/lecture_script.md`；12/12 映射；1 motion；timing 1 block；`--stage script` **PASS_VERIFIED** |
| Motion `scores_to_weights` | 完成 | scene/project 已实现；`segments.json` 68s/order 1；`--stage motion` **PASS_VERIFIED** |
| Motion 实际时长探针 | 完成（播放器） | `durationFrames=4080`，`fps=60`，`seconds=68`；`real=NOT_VERIFIED` 指无录像 |
| 录制就绪包 `05_recording/` | 完成 | manifest / cues / checklist；`--stage recording` **PASS_VERIFIED**；`recordings=0` |
| Reveal P2 正文 `03_slides/index.html` | 完成 | 12 页 `data-slide` 01–12；08/09 保留 `scores_to_weights` 68s / `record.html` 占位；`--stage slides` / `qa` / `qa --strict` **PASS_VERIFIED**；Reveal Build **SKIPPED** |
| 本地来源快照 | 完成（不提交） | PDF/HTML/fulltext 在 `downloads/`、`fulltext/`；SHA-256 记录在清单/JSON |
| CSV 结构校验 | 完成 | 14 行、8 字段、ID 唯一、无空字段 |
| `check-links courses/transformer-self-attention` | PASS | 1 个相对链接 |
| 研究 Gate `--stage research` | **PASS_VERIFIED** | 00–06 齐、非空；退出码 0 |

## 2. PARTIAL

| 项 | 原因 |
| --- | --- |
| 人工视觉/音画 QA | headless Chrome 已 seek 并抽查 Motion 5 个关键帧与 Reveal 12 页；尚未做人工全屏、OBS 画面与音画同步检查 |
| 单头 Q/K/V 投影表述 | `Q=XW_Q` 是 S02/S03 的教学框架（CLM-011）；S01 §3.2.1 把 Q/K/V 作为 attention 输入，S01 §3.2.2 是 multi-head 语境。本集只写一句边界，不展开投影 |
| √d_k 的“为什么” | 原文用 “We suspect”（CLM-007，CLAIM）；footnote 4 的方差 `d_k` 依赖独立/零均值/单位方差假设（CLM-008，INFERENCE）。不能写成普适已证明事实 |
| 4-token 玩具例子 | 数字是 ASSUMPTION / illustrative（CLM-014），不是训练结果/原文超参数；只用于教学 |
| S02 的 8/64 与 512/64 | 属于 multi-head 语境（CLM-012/013）；本集只作 caveat，不作为单头要求 |
| 成片时长 10 分钟 | 是 R4 目标值；Motion 段落 68s 已由播放器探针确认，全片尚未录制/实测 |
| 来源独立性 | S01 为主；S02/S03 仅交叉核对；未额外收集第三份 √d_k 来源（Q04 记录） |

## 3. NOT_RUN

| 项 | 状态 | 说明 |
| --- | --- | --- |
| OBS 录制 | NOT_RUN | 人工阶段；AI 不安装、不调用；`record_status=NOT_RUN` |
| 真实录像时长/音画同步 | NOT_RUN | 未录制；播放器探针 68.0s 不等于实拍验证 |
| 人工全屏视觉 QA | NOT_RUN | headless 抽帧不能替代人眼全屏检查 |
| 教学效果/学习者测试 | NOT_RUN | 无人工评审 |

## 4. 已知限制与处理

1. **`pdftotext` 丢根号**：CLM-006/007/008 的 locator 以 S01 §3.2.1 p.4、公式 (1)、footnote 4 为准；notes 记录提取限制；R3 以 PDF 视觉/S03 渲染公式与代码核对。
2. **单头投影是教学抽象**：S01 §3.2.1 把 Q/K/V 作为 attention 输入；`Q=XW_Q` 等来自 S02/S03（CLM-011）。S01 完整模型是 multi-head h=8/d_k=64（CLM-012）；S02 的 divide-by-8/64 只作 caveat（CLM-013）。讲稿不得把投影写成 S01 单头定义。
3. **玩具数字是 ASSUMPTION**：CLM-014；只用于演示 score→weight→output，不作为论文证据；R3 已固定并可复算。
4. **√d_k 动机分层**：CLM-007 是原文 CLAIM（“We suspect”），CLM-008 是假设下 INFERENCE；不得说成“已证明对所有模型成立”。
5. **M1 的“为什么”**：M1 只做问题引入，答案只使用 CLM-001/002/003；不新增 motivation 事实主张。若需要更强动机，必须先回 R2 补台账。
6. **来源冲突**：未发现 S01 与 S02/S03 的直接事实冲突；差异是教学抽象与 multi-head 维度，已在台账 notes 保留双方语境。
7. **S02/S03 不是主证据**：S02 是博客、S03 是 annotated teaching notebook；仅用于直觉/公式/代码交叉核对，不替代 S01。
8. **Motion 视觉抽查是 headless**：CDP seek 能验证画面对象与文字排列，但不能验证人工全屏、OBS 捕获、音画同步；这些仍是 `NOT_RUN`。

## 5. Gate 记录

```powershell
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage research
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage script
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage motion
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage slides
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage qa
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage qa --strict
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage recording
```

- `research`：**PASS_VERIFIED**（00–06 齐、非空；退出码 0）。
- `script`：**PASS_VERIFIED**（12/12；1 motion；timing 1 block；scene/project/cue OK；退出码 0）。
- `motion`：**PASS_VERIFIED**（scene/project/cue OK；declared=68.0s；real=NOT_VERIFIED；退出码 0）。
- `recording`：**PASS_VERIFIED**（manifest/checklist/cues_dir OK；recordings=0；退出码 0）。
- `slides`：**PASS_VERIFIED**（12/12 映射；Issues 为空；退出码 0）；`reveal-run.ps1` 正常服务 `http://127.0.0.1:3040/index.html`；headless Chrome 逐页截图检查 12 页。
- `qa`：**PASS_VERIFIED**（Issues 为空；退出码 0）。
- `qa --strict`：**PASS_VERIFIED**（Build: SKIPPED — Reveal deck；退出码 0）。
- 播放器探针：`ready=true`，`durationFrames=4080`，`fps=60`，`seconds=68`，`loop=false`。
- 通过以上检查只表示输入、结构与时序可用；不代表课件视觉、OBS 实拍或教学效果已验证。

## 6. 不写成已验证的项

- S1–S4、Motion/录制包与 Reveal P2 已运行；`script` / `motion` / `recording` / `slides` / `qa` / `qa --strict` 均 PASS_VERIFIED；人工全屏、OBS 实拍、音画同步未运行，不能写录制/视觉 PASS。
- 播放器探针只验证时长与页面可加载，不替代真实录像。
- 没有人工评审/学习者测试，不能写教学效果 PASS。
- 没有 OBS 录制，保持 `NOT_RUN`。
