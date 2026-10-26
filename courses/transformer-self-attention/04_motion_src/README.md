# Motion Canvas Runtime Template

浏览器原生、可被 OBS 全屏录制的动画段落运行时。每个核心概念是一个 **45–90 秒** 的完整叙事段落；一个段落对应一个单场景工程，录制时不需要拖动时间线。

> 状态：Phase 3 已接入节奏标注校验与录制包生成器。`check-episode.py` 支持 `--stage motion/recording`；`tools/build-recording-package.py` 生成 manifest / cues / checklist；Manim 仍为 legacy 兜底。

## 1. 版本与边界

| 项 | 固定值 |
| --- | --- |
| Motion Canvas | `3.17.2`（core / 2d / ui / vite-plugin / player） |
| Vite | `5.4.21` |
| TypeScript | `5.9.3` |
| Node | 已用 `24.14.1` 验证；Vite 5 官方支持到 Node 22，升级 Node 前先跑冒烟 |
| 依赖位置 | 每集自己的 `courses/<slug>/04_motion_src/node_modules` |
| 全局安装 | 禁止；只在该目录运行 `pnpm install --frozen-lockfile` |

`package.json` **不能写 `"type": "module"`**。Motion Canvas 的 Vite 插件是 CJS，一旦项目被当作 ESM，`import motionCanvas from '@motion-canvas/vite-plugin'` 会得到模块对象并报 `motionCanvas is not a function`。

## 2. 目录

```text
courses/<slug>/
├── 02_scripts/lecture_script.md
├── 04_motion_src/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── record.html              # 录制主路径
│   ├── segments.json            # 锚点 → 场景 → 时长 → 顺序
│   └── src/
│       ├── theme.ts
│       ├── motion-canvas.d.ts
│       ├── scenes/<name>.tsx
│       └── projects/<name>.ts
├── 04_manim_src/scenes/         # 仅兜底锚点
└── 05_recording/                # 录制就绪包
    ├── manifest.json
    ├── checklist.md
    ├── cues/
    └── recordings/              # 本地产物，不提交
```

命名统一：`name` = 场景文件 = 工程文件 = cue 文件 = 录像文件基名。小写 `snake_case`，与讲稿 `[ANIMATION: name]` 完全一致。

## 3. 首次建立

`tools/motion-run.ps1` 在 `04_motion_src/` 不存在时会从本模板复制；也可以手动复制：

```powershell
Copy-Item -Recurse D:\CourseStudio\tools\motion-runtime D:\CourseStudio\courses\<slug>\04_motion_src
```

复制后：

1. 改 `segments.json`，把模板的 `example` 换成真实的锚点与 45–90 秒时长。
2. 新建 `src/scenes/<name>.tsx` 与 `src/projects/<name>.ts`。
3. 在课程目录内安装依赖：

```powershell
pnpm --dir D:\CourseStudio\courses\<slug>\04_motion_src install --frozen-lockfile
```

依赖只落在这个课程目录；`node_modules/` 与 `output/` 已被 `tools/course.gitignore` 忽略。

## 4. 启动与录制

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
  -Episode <slug> -Segment <name>
```

runner 会：

1. 缺 `04_motion_src/` 时从本模板复制；
2. 缺 `node_modules/` 时在该目录执行 `pnpm install --frozen-lockfile`；
3. 设置 `MC_SEGMENT` 与 `MC_PORT`；
4. 启动 Vite，打印：

```text
http://localhost:9100/record.html?segment=<name>
```

**这个 URL 才是录制入口**。`?present` 只作预览，不进入录制清单：Phase 0 实测全屏后仍显示 SLIDES 面板与底部控件。

录制页行为（已实测）：

- 使用 `@motion-canvas/player`，`src` 为 `/src/projects/<segment>.ts?project`；
- `auto="true"`，**不能写裸 `auto`**（`getAttribute('auto')` 返回空字符串，布尔判断为 false）；
- 在 shadow DOM 注入 CSS 隐藏 `.overlay` / `.button`；
- 不在元素升级前设置 `quality` / `width` / `height`（会触发 `Cannot read properties of null (reading 'configure')`）；`quality` 在 `ready` 后通过 `?quality=` 设置；
- 默认 `toggleLoop(false)`，段落播完停住；需要循环预览时加 `&loop=1`；
- 16:9 自适应舞台，全屏铺满；页面隐藏光标。

可选参数：

```text
record.html?segment=<name>&quality=1.5   # 4K/150% 屏可提高内部渲染倍率
record.html?segment=<name>&loop=1        # 预览循环；录制不要用
record.html?segment=<name>&probe=1      # QA only：显式触发一次 Player.run()，让 headless 读到真实时长；录制不要用
```

## 5. 录制日人工步骤

- 进入全屏后**等 2 秒**，避开 Chrome 的全屏提示条，再开始 OBS 录制。
- OBS 使用 **Display Capture** 或 **Window Capture (Windows Graphics Capture)**。
- **不要用 BitBlt / GDI 窗口采集**：Phase 0 实测 Chrome 画面全黑。ffmpeg `gdigrab title=` 同样黑屏，桌面采集和 `ddagrab` 正常。
- 4K + 150% 缩放下，1920×1080 CSS 窗口实际是 2880×1620 物理像素。OBS 画布仍设 **1920×1080**，对源做缩放；不要在 OBS 里改画布尺寸。
- OBS 路径仅供人工参考：`D:\Program Files\obs-studio\bin\64bit\obs64.exe`。本仓库不安装、不调用、不自动化 OBS；OBS 相关检查一律 `NOT_RUN`。
- 每段独立录制：打开对应 `record.html?segment=<name>`，录 2 秒静止 → 段落 → 2 秒静止，作为拼接切点。

## 6. `segments.json`

```json
{
  "canvas": {"width": 1920, "height": 1080, "fps": 60},
  "segments": [
    {
      "name": "attention_scores",
      "engine": "motion",
      "duration_seconds": 68,
      "order": 3,
      "scene": "attention_scores",
      "record_status": "NOT_RUN"
    }
  ]
}
```

规则：

- `engine` 必填：`motion` 或 `manim`；不靠文件存在性猜。
- `duration_seconds` 目标 45–90；Manim 兜底沿用旧的 20 秒限制。
- `order` 在整集内唯一且连续，决定录制与拼接顺序。
- `record_status` 初值 `NOT_RUN`；人工录制完成后回填。
- 真实时长以播放器 `duration / fps` 为准；QA 用 `record.html?segment=<name>&probe=1` 读取隐藏状态里的 `durationFrames/fps`。不带 `probe` 时 headless 可能为 0，真实浏览器正常；探针不替代人工抽帧。

### 讲稿节奏标注（必须与 segments.json 一致）

每个 motion `[ANIMATION: name]` 在讲稿中配一个区块：

```text
[ANIMATION: example]
[SEGMENT: example | 45s | order=1]
[VISUAL 00:00] 建立坐标系
[HOLD 00:05] 停 2 秒
[EMPHASIS 00:15] 高亮关键量
[CUT 00:23] 切换视图
[VISUAL 00:33] 收束
```

- 每个 `[ANIMATION]` 恰好一个 `[SEGMENT]`；name / 时长 / order 与 `segments.json` 一致。
- 声明 45–90 秒；至少各一条 `[HOLD]` / `[EMPHASIS]` / `[CUT]`。
- 时间戳严格递增，最后一条不超过声明时长；`[VISUAL]` 建议至少一条。
- `--stage script` 与 `--stage motion` 对 motion 段落硬校验；旧 Manim-only 段落不要求。
- 录制包由 `tools/build-recording-package.py` 从讲稿 + `segments.json` 生成，不要手工维护 manifest / cues。

## 7. 场景写法

- 显式使用 `theme.fontFamily`；Player 页不会继承编辑器字体，否则会退化成衬线体。
- 先建立几何对象，再用变换推导；每个关键步骤后留 `waitFor` 停顿。
- 不用装饰性粒子、3D、复杂运镜；不做没有叙事作用的动画。
- 场景拆成 `beat` 生成器或连续 `yield*` 段，便于把总时长控制在 45–90 秒。
- 屏幕文字与公式必须与 `01_research/03-knowledge-structure.md` 一致；不确定时标“待核”，不要凭记忆补。

## 8. 与旧路径的关系

- `04_manim_src/scenes/` 保留给极强公式/符号变换场景；只有 `segments.json` 里 `engine: "manim"` 的锚点才走 MP4 渲染。
- `03_slides/public/*.mp4` 只服务 legacy/兜底，不再是默认动画产物。
- `check-episode.py` 已按 `segments.json` 分派。没有 `segments.json` 的旧 episode 会回退到 Manim 文件存在性检查，并给出 deprecation warning。

## 9. 示例三件套

- 讲稿：`tools/episode-template/02_scripts/lecture_script.md` 的 S02
- 源：`src/scenes/example.tsx` + `segments.json`（45s / order 1）
- 录制包：`tools/episode-template/05_recording/manifest.json`、`cues/example.md`、`checklist.md`

`new-episode.ps1` 会复制 `04_motion_src` 与 `05_recording`；先照抄这三处，再替换成真实内容。
