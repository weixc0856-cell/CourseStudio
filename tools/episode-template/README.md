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
├── 02_scripts/            # 口播稿（含 [SLIDE] / [ANIMATION] / 节奏标注）
├── 03_slides/             # course: Reveal；technical/news: Slidev
│   ├── index.html         # Reveal（course 默认）
│   ├── assets/deck.css
│   ├── slides.md          # Slidev（technical/news）
│   ├── .vendor/           # reveal-run 同步，不提交
│   └── public/            # legacy/兜底 Manim MP4（不提交）
├── 04_motion_src/         # Motion Canvas 主路径（从 tools/motion-runtime 复制）
│   ├── record.html        # 录制入口
│   ├── segments.json      # 锚点 → 场景 → 45–90 秒时长 → 录制顺序
│   └── src/
├── 04_manim_src/scenes/   # Manim 兜底（仅 -WithManim 创建）
├── 05_recording/          # 录制就绪包（最终交付物）
│   ├── manifest.json
│   ├── checklist.md
│   ├── cues/
│   └── recordings/        # 本地产物，不提交
├── qa/                    # 检查记录
└── handoff.md             # 阶段交接
```

## 常用命令

```powershell
# Motion Canvas 录制页（主路径）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 -Episode {{EPISODE}} -Segment example

# 首次建立 04_motion_src 后安装依赖（runner 会自动执行）
pnpm --dir D:\CourseStudio\courses\{{EPISODE}}\04_motion_src install --frozen-lockfile

# Reveal 课件（course 默认；同步 .vendor 并启动静态服务）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 -Episode {{EPISODE}} -Port 3040

# Slidev 开发服务器（technical/news/旧课）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode {{EPISODE}} -Mode dev

# 构建静态页面
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode {{EPISODE}} -Mode build

# Manim 兜底锚点（仅在 segments.json 标 engine=manim 时）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode {{EPISODE}} -Name example_name -SceneClass ExampleName -Quality l -TimeoutSeconds 180

# 生成/刷新录制就绪包（manifest / cues / checklist）
python D:\CourseStudio\tools\build-recording-package.py {{EPISODE}}

# 检查锚点与资产
python D:\CourseStudio\tools\check-episode.py {{EPISODE}} --mode {{MODE}} --stage qa --strict
```

## 约束

- 讲稿必须包含 `[SLIDE: NN]` 与 `[ANIMATION: name]` 锚点。
- 动画主路径是 `04_motion_src/`：一个 `[ANIMATION: name]` 对应 `src/scenes/name.tsx` 与 `src/projects/name.ts`，目标 45–90 秒。
- 每个 motion 段落必须写 `[SEGMENT]` + `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]`；`--stage script` / `motion` 会硬校验。
- `04_manim_src/` 仅作兜底；只有 `segments.json` 里 `engine: "manim"` 的锚点才走 MP4。
- 录制入口是 `record.html?segment=<name>`；`?present` 仅预览，不进入录制清单。
- `05_recording/` 的 manifest、cues、checklist 段落表由 `build-recording-package.py` 生成，不要手工维护。
- course 脚手架默认保留 Reveal（`index.html` + `assets/`），technical/news 保留 Slidev（`slides.md`）；未使用的一套会被移除。
- Reveal 每页用 `<section class="c-slide" data-slide="01">`，`data-slide` 严格 1..N；本地 `src`/`href` 必须存在；动画页只放占位，不嵌 MP4。默认橙白主题：`theme/white.css` + `assets/deck.css`。
- Reveal 资源由 `reveal-run.ps1` 同步到 `03_slides/.vendor/`，该目录不提交。
- OBS 由人工操作，不安装、不调用、不自动化；相关检查标 `NOT_RUN`。
- 不把 PDF、MP4、`.venv`、`node_modules` 提交进 Git。
