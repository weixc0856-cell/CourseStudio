# CourseStudio Pipeline Contract — v1.0.0 (R1 draft)

> **R2.1 更新**：`HUMAN` 维度已替换为 `CONTENT_QUALITY`（AI 多工具交叉自检）；`human.accept` 阶段已替换为 `content.review`。不设强制人工审核门禁；负责人保留最终 `pass`/`reject`。详见 [R2.1 Approval Checklist](../r2.1/r2.1-approval-checklist.md)。

- **状态**：`DRAFT`。本文件是设计契约，不是当前生产工具已执行的流程。
- **适用**：`courses/<slug>/` 下的 course / technical / news / podcast。
- **配套**：[status-model.md](status-model.md)、[human-gates.md](human-gates.md)、[decision-log.md](decision-log.md)、[migration-map.md](migration-map.md)、[../schemas/README.md](../../schemas/README.md)。
- **原则**：先冻结契约，再验证最小闭环；先保护现有数据，再逐步迁移；先证明检查结果可信，再扩大自动化范围。

---

## 1. 阶段与唯一职责

```text
intake → research → design → script → visual → package
                                      ↘         ↙
                                       qa.static
                                           ↓
                                       qa.runtime
                                           ↓
                                      content.review
                                           ↓
                                         record
                                           ↓
                                         deliver
```

`visual` 与 `package` 是 `script` 冻结后的**兄弟阶段**，不是严格的先后依赖。这样 `visual` 不需要等待 `package` 生成的 cue，`package` 也不需要等待 `visual` 生成的 scene 文件；两者只依赖已冻结的 `script` + `segments`。

| Stage | 执行者 | 唯一职责 | 必需输入 | 输出 | 前置条件 | 失败条件 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `intake` | 人 + LLM | 冻结任务、受众、目标、模式、原始材料与来源清单 | 用户材料、任务 brief | `episode.json` 初稿、`00_raw_materials/`、`research/sources.json` | 工作区干净、slug 合法 | 受众/目标/范围未冻结；来源清单为空 | intake 记录、材料哈希 |
| `research` | LLM + 人审 | 主张、来源定位、证据状态、冲突、研究质量 | 冻结的 intake、来源 | `claims.jsonl`、`knowledge.md`、`quality.md`、`outline.md` | intake 冻结 | 缺来源定位；`CLM` 重复；证据状态未记录 | 研究 QA run（L1/L2） |
| `design` | LLM + 人审 | 教学目标、知识顺序、示例、练习、评估 | 冻结的 research | `design.md` | research 冻结 | 目标不可测；模块顺序循环；无评估 | 设计审查记录 |
| `script` | LLM | 讲稿、`[SLD]`/`[SEG]`/`[CLM]` 锚点、时间戳、分段定义 | 冻结的 design、claims | `script.md`、`segments.json` | design 冻结 | 锚点不连续；45–90s 越界；引用不存在的 claim | script QA run |
| `visual` | LLM | 课件、动画源码、资源、与讲稿的映射 | 冻结的 script、segments、design | `slides/index.html` 或 `slides.md`、`scenes/*.tsx`、`projects/*.ts`、`assets/` | script 冻结 | 缺资源；data-slide 跳号；typecheck 失败；浏览器加载失败 | visual QA run（L1/L2） |
| `package` | 确定性脚本 | manifest、cues、checklist | 冻结的 script、segments | `recording/manifest.json`、`cues/*.md`、`checklist.md` | script 冻结 | 缺 cue 源；ID/顺序不一致；URL 非法 | package QA run |
| `qa.static` | 确定性脚本 | Schema、引用、资源、链接、泄漏、映射检查 | script、visual、package、claims | `qa/runs/<id>/static/*`、`trace-report.json` | visual + package 完成 | 任一 BLOCKER/ERROR 检查失败 | static QA run（L1） |
| `qa.runtime` | 确定性脚本 + AI 交叉检查 | 构建、类型检查、浏览器加载、动画探针、时长、日志 | visual、package、运行时依赖 | `qa/runs/<id>/runtime/*` | visual + package 完成 | 构建/类型/浏览器/probe/ffprobe 失败 | runtime QA run（L2/L3） |
| `content.review` | AI 多工具 | 事实、教学、视觉、音画、录制质量的 AI 自动审查 | static + runtime 证据、产物 | `acceptance.json` | QA 完成；证据齐全 | 任一必需项 FAIL/NEEDS_REVIEW | AI 审查方法、范围、时间 |
| `record` | AI 质量检查 + ffprobe | 实际录像、文件完整性、录制质量 | checklist、record.html、content.review | `recordings/*`、`recording.json` 更新 | 录制质量 AI 检查通过 | 缺文件/时长异常/音画不同步 | ffprobe JSON、抽帧、AI 审查 |
| `deliver` | 确定性脚本 | 汇总交付资格及依赖证据 | 全部 stage、acceptance、recording | `deliverable.json`、`episode.json.delivery` | 所有必需维度 PASS | 任一必需维度 FAIL/BLOCKED/NEEDS_REVIEW/STALE | 交付清单 + 哈希 |

---

## 2. 阶段依赖与冻结点

| 冻结点 | 冻结内容 | 冻结后允许的变更 | 失效范围 |
| --- | --- | --- | --- |
| F1 `intake` | 模式、受众、目标、范围、来源清单 | 只能通过带原因的 unfreeze | research 及下游全部失效 |
| F2 `research` | 主张文本、来源定位、证据/推理/冲突状态 | 只能通过新版本 claim + 重新审查 | design、script、visual、package、qa、content.review、record、deliver |
| F3 `design` | 教学目标、模块顺序、评估 | 只能通过 re-design | script、visual、package、qa、content.review、record、deliver |
| F4 `script` | 讲稿、锚点、segments、声明时长 | 只能通过新 script 版本 | visual、package、qa、content.review、record、deliver |
| F5 `visual` + `package` | 课件、场景、manifest、cues | 只能通过新版本 + 对应 QA | qa.static、qa.runtime、content.review、record、deliver |
| F6 `qa` | static/runtime 证据 | 输入变化即失效 | content.review、record、deliver |
| F7 `content.review` | AI 自检 + 负责人最终决定 | 自动返工或重新自检 | record、deliver |
| F8 `record` | 录像文件 + ffprobe + 录制验收 | 只能重录 | deliver |

**规则**：任何输入哈希变化都会使其下游证据标记为 `STALE`，不得复用。`STALE` 等同于 `NOT_RUN`，见 [status-model.md](status-model.md)。

---

## 3. 阶段独立性

| 阶段 | 可独立执行？ | 说明 |
| --- | --- | --- |
| `intake` | 是 | 只需要用户材料 |
| `research` | 是（intake 冻结后） | 不依赖 design/script/visual |
| `design` | 是（research 冻结后） | 不依赖 script/visual |
| `script` | 是（design + claims 冻结后） | 不依赖 visual/package |
| `visual` | 是（script + segments 冻结后） | **不读取 `05_recording/`**，不要求 cue |
| `package` | 是（script + segments 冻结后） | **不要求 scene/project 文件已存在**；只写 manifest/cues/checklist |
| `qa.static` | 是（visual + package 完成后） | 只读，不写产物 |
| `qa.runtime` | 是（visual 完成、依赖可用） | 需要 Node/pnpm/Chrome/ffmpeg；不依赖 content.review |
| `content.review` | 是（static + runtime 证据齐全） | AI 多工具执行；不是人工签字 |
| `record` | 是（录制质量 AI 检查通过） | 人 + OBS；不自动 |
| `deliver` | 是（全部必需维度满足） | 只计算，不生成内容 |

---

## 4. Motion 与 recording 的 cue 顺序问题（P0-03 的修复）

旧流程的问题：

- `check-episode.py --stage motion` 要求 `05_recording/cues/<name>.md`；
- cue 由更晚的 `build-recording-package.py` 生成；
- 因此上游 `visual` 依赖了下游 `package` 的文件。

新契约的规则：

1. **`visual` 不读取 `05_recording/`**。它只检查 `script.md`、`segments.json`、scene/project、课件资源和 typecheck。
2. **`package` 只依赖 `script.md` + `segments.json`**。它生成 manifest、cues、checklist；不要求 scene/project 文件存在，只记录路径。
3. **`qa.static` 统一检查**：scene/project/cue 是否存在、manifest 与 segments 是否一致、cue 顺序是否与 manifest 一致。
4. **`qa.runtime` 统一检查**：scene typecheck、`probe=1` 实际时长、课件构建/浏览器。
5. `visual` 与 `package` 可以并行；谁先完成都可以。`qa.static` 必须等两者都完成。

这样不存在“上游必须依赖下游生成文件”的循环。

---

## 5. 模式矩阵与跳过策略

| Stage | `course` | `technical` | `news` | `podcast` |
| --- | --- | --- | --- | --- |
| `intake` | 必需 | 必需 | 必需 | 必需 |
| `research` | 必需 | 必需 | 必需 | 必需 |
| `design` | 必需 | 必需 | 简化但必需 | 简化但必需 |
| `script` | 必需 | 必需 | 必需 | 必需 |
| `visual` | 必需（Reveal + Motion） | 必需（Slidev + Motion） | 可选（Slidev 或纯口播） | `NOT_APPLICABLE` |
| `package` | 必需（有 Motion 时） | 必需（有 Motion 时） | 可选（有 Motion 时） | `NOT_APPLICABLE` |
| `qa.static` | 必需 | 必需 | 必需 | 必需（research/script） |
| `qa.runtime` | 必需（Reveal + Motion） | 必需（Slidev + Motion） | 有课件/动画时必需 | `NOT_APPLICABLE` |
| `content.review` | 必需（AI 5 域） | 必需（AI 5 域） | 必需（相关 4 类） | 必需（事实/教学/口播/录制） |
| `record` | 必需（视频） | 必需（视频） | 必需（视频或音频） | 必需（音频） |
| `deliver` | 必需 | 必需 | 必需 | 必需 |

**跳过规则**：

- 任何跳过都必须写入 `episode.json.approvals`，包含 `approval_id`、`scope`、`decision=APPROVED`、`approved_by`、`approved_at`、`notes`。
- 跳过的阶段在 `stages.<name>.status` 中写 `NOT_APPLICABLE`，并在 `notes` 说明原因。
- 跳过会影响 `deliver`：`deliver` 必须列出被跳过的维度；`DELIVERY` 只有在“跳过已获批准且不影响必需维度”时才能 `READY`。
- 不得因为工具缺失而自动跳过必需阶段；工具缺失 → `BLOCKED`，不是 `NOT_APPLICABLE`。

---

## 6. 输入变化的失效矩阵

| 变化 | 立即失效 | 必须重跑 | 可复用 |
| --- | --- | --- | --- |
| intake 受众/目标/来源清单 | research 及全部下游 | research → deliver | 原始材料文件 |
| claim 文本/来源/状态 | design（若引用）、script、visual、package、qa、content.review、record、deliver | design → deliver | intake、未被引用的 claim |
| design 目标/模块 | script、visual、package、qa、content.review、record、deliver | script → deliver | research |
| script 文本/锚点/时长 | visual（映射）、package、qa、content.review、record、deliver | visual/package → deliver | research、design、未受影响的 scene |
| segments 顺序/时长/引擎 | visual、package、qa.runtime、content.review、record、deliver | visual/package → deliver | script 文本 |
| scene/project 代码 | qa.runtime、content.review（视觉）、record、deliver | qa.runtime → deliver | script、package、未受影响的段落 |
| deck 页面/资源 | qa.static、qa.runtime、content.review、record、deliver | qa → deliver | script、package |
| package URL/顺序/checklist | qa.static、record、deliver | qa.static → deliver | visual、script |
| QA 工具/版本 | 对应 QA run | qa.static 或 qa.runtime | 产物 |
| QA 输入哈希变化 | 该 run 及其下游 | 对应 stage | 未变化的 run |
| content.review 决定 | record、deliver | record → deliver | QA 证据 |
| recording 文件 | deliver | deliver | 其他维度 |

**规则**：失效不是删除；旧证据保留并标记 `STALE`，新 run 使用新 `run-id`。

---

## 7. 失败、恢复与证据保护

1. **失败不覆盖成功证据**：每次运行写新的 `qa/runs/<run-id>/`；失败的 run 保留。
2. **阶段失败**：该 stage `FAILED`；下游标记 `BLOCKED`；上游已完成产物保持不变。
3. **恢复**：从失败 stage 重跑；如果输入未变，可复用上游成功证据（哈希匹配）。
4. **部分写入**：所有生成器必须先完整校验，再写临时文件，最后原子 rename；不得留下半包。
5. **状态损坏**：`episode.json` 无效 → `CONTRACT_ERROR`（exit 3）；不得猜测或自动修复；从备份恢复。
6. **内容质量拒绝/需返工**：`content.review` 记录 `NEEDS_REVIEW` + 返回阶段（research/design/script/visual/record）；下游全部失效。
7. **不可恢复**：同一失败修复 3 次仍失败 → 停止，保留现场，报告命令/退出码/日志。
8. **禁止**：删除证据、改检查脚本以通过、把 `NOT_RUN` 写成 `PASS`、用历史 handoff 替代当前证据。

---

## 8. QA 分层与证据目录

| 层 | 内容 | 依赖 | 运行时机 |
| --- | --- | --- | --- |
| L1 | Schema、单元、负向、链接、泄漏、引用完整性 | Python 标准库 | 每次提交/CI |
| L2 | clean-room 建集、课件构建、Motion typecheck、浏览器加载 | Node/pnpm/Chrome | 合并前/可选 CI |
| L3 | 运行时 probe、抽帧、ffprobe、AI 审查、实际录像 | OBS/AI/ffmpeg | 发布前 |

证据目录：

```text
qa/runs/<run-id>/
├── run.json                  # QA run 元数据（qa.schema.json）
├── commands.log              # 实际命令、时间、退出码
├── environment.json          # 工具版本、OS、路径
├── static/
│   ├── schema.json
│   ├── claims.json
│   ├── segments.json
│   ├── resources.json
│   ├── leak-scan.json
│   └── mapping.json
├── runtime/
│   ├── typecheck.log
│   ├── build.log
│   ├── browser/*.png
│   ├── probe.json
│   └── ffprobe.json
├── review/
│   └── content-review.json
└── artifacts.sha256          # 输入/输出哈希清单
```

- **必须落盘**：run.json、commands.log、environment.json、失败日志、probe/ffprobe JSON、输入/输出哈希、AI 审查。
- **保留摘要即可**：构建产物、`dist/`、大截图；记录路径+哈希+大小，不复制整棵目录。
- **不落盘**：PDF 全文、录像原片（放仓库外/本地）、`.venv`、`node_modules`。
- **保留期**：至少保留到交付后 90 天；发布证据长期保留。
- **历史 handoff**：只能作为参考；没有日志/哈希的声明不得迁移为 `PASS`。

---

## 9. 追溯关系（由数据派生，不另存）

`qa.static` 生成 `trace-report.json`（报告，不是源数据）：

| 关系 | 派生方式 |
| --- | --- |
| claim → artifact | `claims.used_in_artifact` |
| artifact → segment | `segments.segment_id` + `script_anchor` |
| segment → slide | `segments.slide_anchors` |
| segment → cue | `segments.cue` / `recording.segments[].cue` |
| segment → recording | `recording.segments[].segment_id` |
| QA → artifact | `qa.checks[].inputs[].path` + sha256 |

检查规则：

- 每个 `used_in_artifact` ID 必须存在；
- 每个 Motion segment 必须有一个 cue 和一个 recording task；
- 每个 `[SLD]` 锚点必须对应 deck 页；
- 每个 deck 页必须至少有一个 claim，或显式标记 `NO_CLAIM_REQUIRED`（如封面/目录）；
- 每个 QA check 的输入哈希必须与当前产物一致；
- 报告列出 `orphan_claims`、`orphan_slides`、`orphan_segments`、`orphan_cues`、`coverage`。

---

## 10. AI 质量门禁

AI 多工具交叉自检分为五个独立 Gate，详细输入、AI 验证方法、记录格式与返工回退见 [human-gates.md](human-gates.md)：

| Gate | 内容 | NEEDS_REVIEW/FAIL 后返回 |
| --- | --- | --- |
| `AI-1` | 事实与证据质量 | `research` |
| `AI-2` | 教学目标与内容连贯性 | `design` 或 `script` |
| `AI-3` | 视觉表达与信息可读性 | `visual` |
| `AI-4` | 口播与画面同步 | `script` 或 `visual` |
| `AI-5` | 实际录制质量 | `record` |

规则：

- `decision` 由 AI 自检/自动返工填写；负责人保留最终 `pass`/`reject`；模型不得自评已证实。
- 任何必需 Gate `FAIL`/`NEEDS_REVIEW`/`STALE` → `DELIVERY=NOT_READY`。
- 输入哈希变化使对应验收 `STALE`，必须重新审查。
- 机器只检查证据存在/哈希/字段合法；不判断科学真实性、教学效果或视觉质量。

---

## 11. 契约治理

- 本契约版本：`1.0.0`，状态 `DRAFT`。
- 修改流程：提案（decision log）→ 影响分析 → fixture 更新 → 双跑对照 → 负责人批准 → 版本升级。
- 任何阶段/字段/状态语义变化都必须升级 MAJOR 或 MINOR，并更新 `docs/contract/*` 与 `schemas/*`。
- 未批准的决策不得写成既定事实；见 [decision-log.md](decision-log.md)。
- 生产接入前，`check-episode.py` 的旧输出与契约输出必须双跑并记录差异；双跑通过前，契约不生效。
