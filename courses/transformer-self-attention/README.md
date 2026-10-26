# transformer-self-attention

**模式**：course  
**状态**：录制就绪；内容与 QA `PASS_VERIFIED`；OBS 实拍 `NOT_RUN`

## 课程定位

- **受众**：有深度学习基础（张量、矩阵乘法、点积、softmax、反向传播概念），但不是注意力专家。
- **学习目标**：能讲清 Q/K/V 角色、score → softmax → weight 的含义、单头 self-attention 的计算骨架，以及为什么按行归一化。
- **时长**：目标约 10 分钟；唯一 Motion 段落声明 68 秒。
- **核心问题**：处理一个 token 时，如何利用同一序列中其他位置的信息？

## 本集产物

```text
transformer-self-attention/
├── 00_raw_materials/
├── 01_research/                 # 00–06、search-results
├── 02_scripts/lecture_script.md # M1–M7、[SLIDE] / [SEGMENT] / 节奏标注
├── 03_slides/
│   ├── index.html               # Reveal，12 页，data-slide 01–12
│   └── assets/deck.css          # 麦肯锡橙白主题
├── 04_motion_src/
│   ├── record.html              # 录制入口
│   ├── segments.json            # scores_to_weights / 68s / order 1
│   └── src/scenes|projects      # scores_to_weights
├── 05_recording/
│   ├── manifest.json
│   ├── checklist.md
│   ├── cues/scores_to_weights.md
│   └── recordings/              # 本地产物，不提交
├── qa/
└── handoff.md
```

本集**不使用 Manim**，也不使用 Slidev；`04_motion_src` + Reveal 是主路径。

## 常用命令

```powershell
# Motion 录制页（主路径）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
  -Episode transformer-self-attention -Segment scores_to_weights

# Reveal 课件（同步 .vendor + 静态服务）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 `
  -Episode transformer-self-attention -Port 3040

# 生成/刷新录制就绪包
python D:\CourseStudio\tools\build-recording-package.py transformer-self-attention

# 阶段检查
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage motion
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage recording
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage slides
python D:\CourseStudio\tools\check-episode.py transformer-self-attention --mode course --stage qa --strict
```

Motion 页面：`http://localhost:9100/record.html?segment=scores_to_weights`。不要用 `?present` 录制。

## 约束

- 锚点：`[SLIDE: NN]` 严格 1..N；唯一 `[ANIMATION: scores_to_weights]`；`[SEGMENT]` 与 `segments.json` 一致。
- 动画：68 秒，`QK^T → /√d_k → 行 softmax → A`，停在 A，不进入 `O=AV`。
- Reveal：12 页 `data-slide` 01–12；动画页只放占位，不嵌 MP4。
- 视觉：暖白 `#FAFAF7`、近黑 `#1A1A1A`、McKinsey 橙 `#E87722`；Motion 与 Reveal 同一套橙白 token。
- 录制：`05_recording/` 是录制就绪包；OBS 由人工完成，`record_status` 保持 `NOT_RUN` 直到实际录制。
- 不提交：PDF 全文、`01_research/downloads/`、`fulltext/`、`03_slides/.vendor/`、`04_motion_src/node_modules/`、`05_recording/recordings/`、`.venv/`、`.meta` 元数据。

## 状态与下一步

- 研究 Gate、讲稿、Motion、录制包、Reveal P2、slides/QA/strict QA 均已通过。
- 播放器探针 `4080 frames / 60 fps = 68.0s`。
- 下一步仅人工 OBS 录制、真实时长/音画检查与后期拼接。

详细进度见 [handoff.md](handoff.md)；新集流程见 [guides/quickstart-episode.md](../../guides/quickstart-episode.md)。
