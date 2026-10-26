# {{EPISODE}}

**模式**：{{MODE}}

**状态**：`NOT_RUN`

## 课程定位

- 受众：
- 学习目标：
- 时长：
- 核心问题：

## 目录契约

```text
{{EPISODE}}/
├── 00_raw_materials/      # 原始 PDF/HTML（PDF 不提交）
├── 01_research/           # 研究输入包
├── 02_scripts/            # 口播稿（含视觉锚点）
├── 03_slides/             # Slidev
│   ├── slides.md
│   └── public/            # Manim MP4（不提交）
├── 04_manim_src/scenes/   # Manim 场景源码
├── qa/                    # 检查记录
└── handoff.md             # 阶段交接
```

## 常用命令

```powershell
# Slidev 开发服务器
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode {{EPISODE}} -Mode dev

# 构建静态页面
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode {{EPISODE}} -Mode build

# 渲染一个 Manim 锚点
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode {{EPISODE}} -Name example_name -SceneClass ExampleName -Quality l -TimeoutSeconds 180

# 检查锚点与资产
python D:\CourseStudio\tools\check-episode.py {{EPISODE}} --mode {{MODE}} --stage qa --strict
```

## 约束

- 讲稿必须包含 `[SLIDE: NN]` 与 `[ANIMATION: name]` 锚点。
- Slidev 只负责排版；动画由 `manim-isolation` 单独生成。
- 不把 PDF、MP4、`.venv`、`node_modules` 提交进 Git。
