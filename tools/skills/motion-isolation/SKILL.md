---
name: motion-isolation
description: Motion Canvas 动画隔离舱。把一个 [ANIMATION: name] 变成 45–90 秒、可独立录制的 3B1B 风格叙事段落，写入 04_motion_src/src/scenes 与 src/projects，并用 record.html 在浏览器全屏录制。默认动画引擎；Manim 仅在 engine=manim 时兜底。
---

# Motion Isolation Cabin

## 1. 使命与边界

你是被隔离的动效工程师。唯一职责：把一个 `[ANIMATION: name]` 锚点变成一个 **45–90 秒的 Motion Canvas 叙事段落**，可在浏览器 `record.html?segment=<name>` 全屏播放并被 OBS 独立录制。

- **只写**：
  - `04_motion_src/src/scenes/<name>.tsx`
  - `04_motion_src/src/projects/<name>.ts`
  - 必要时 `04_motion_src/segments.json` 中该段落的字段（只改这一段）
- **只读**：
  - `02_scripts/lecture_script.md` 中该锚点的 `[SEGMENT]` / `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]` 与前后口播
  - `01_research/03-knowledge-structure.md` 的符号/公式
  - `04_motion_src/src/theme.ts`
- **不改**：研究包、讲稿、`05_recording/`、课件、其他段落。
- **不安装**全局 npm 包；依赖由 `motion-run.ps1` 在课程 `04_motion_src/` 内安装。

## 2. 输入契约

必须存在：

| 输入 | 用途 |
| --- | --- |
| `02_scripts/lecture_script.md` | 读取 `[ANIMATION: name]`、`[SEGMENT]` 与节奏标注 |
| `04_motion_src/segments.json` | 引擎、时长、顺序、scene/project 的事实来源 |
| `04_motion_src/src/theme.ts` | 字体、颜色、字号、缓动 |
| `01_research/03-knowledge-structure.md` | 符号、公式、量纲（如涉及） |

一致性要求：

- `[SEGMENT]` 的 name / 时长 / order 必须与 `segments.json` 完全一致；
- 段落 45–90 秒；
- 至少各一条 `HOLD` / `EMPHASIS` / `CUT`；
- 时间戳严格递增，最后一条不超过声明时长。

## 3. 3B1B 风格契约

不是“短机制插片”，而是一个完整叙事段落：

1. **先建立几何对象**：坐标、向量、曲线、矩阵、区域；先让观众看见“东西在哪”。
2. **逐步揭示**：每一步只改变一个量或一个关系；用 `waitFor` 留出理解时间。
3. **用变换推导**：平移、缩放、旋转、投影、分解；让公式的每一项对应一个可见动作。
4. **收束**：留下最终态与一句可复述的结论；最后停 3–6 秒供口播收尾。
5. **禁止**：装饰性粒子、3D 摄像机、复杂运镜、无叙事作用的循环动画、外部字体/网络图片；不要使用纯黑背景或低对比浅灰文字。
6. **视觉基线**：使用 `src/theme.ts` 的橙白 token；背景浅色、文字近黑、橙色用于结构/关键值、深琥珀用于次级强调；矩阵单元保持白底/深灰边框/深色文字。

节奏建议：

- 开场 3–6 秒建立画面；
- 每个关键步骤后停 2–4 秒；
- 一个段落 3–6 个 beat；
- 代码按 `beat1()` / `beat2()` 生成器拆分，便于控制总时长。

## 4. 输出契约

一个段落一个场景、一个单场景工程：

```text
04_motion_src/
├── src/scenes/<name>.tsx
└── src/projects/<name>.ts
```

`src/projects/<name>.ts`：

```ts
import {makeProject} from '@motion-canvas/core';
import scene from '../scenes/<name>?scene';

export default makeProject({scenes: [scene]});
```

`src/scenes/<name>.tsx` 骨架：

```tsx
import {Line, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
import {theme} from '../theme';

export default makeScene2D(function* (view) {
  view.fill(theme.background);

  const title = createRef<Txt>();
  view.add(
    <Txt
      ref={title}
      text={'给这一段的标题'}
      fill={theme.ink}
      fontFamily={theme.fontFamily}
      fontSize={theme.fontSize.title}
      opacity={0}
    />,
  );

  yield* title().opacity(1, 1);
  yield* waitFor(2);

  // beat2 / beat3 ... 逐步建立几何对象与变换
});
```

约束：

- 显式 `fontFamily={theme.fontFamily}`；Player 页不会继承编辑器字体。
- 不默认渲染 MP4；录制页是 `record.html?segment=<name>`。
- `?present` 仅预览，不要作为录制入口。
- 一个场景文件只放该段落；不跨锚点复用导致上下文膨胀。

## 5. 运行与验证

启动：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
  -Episode <slug> -Segment <name>
```

- 缺 `node_modules/` 时会在课程 `04_motion_src/` 内 `pnpm install --frozen-lockfile`；
- 打印 `http://localhost:9100/record.html?segment=<name>`；
- 首次在真实浏览器确认：`auto="true"`、无播放器 UI、16:9 铺满、动画正常推进。

检查：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage motion
```

- 检查 scene / project / cue、45–90 秒、order、engine；
- 有录像用 `ffprobe`，否则 `real=NOT_VERIFIED`；不编造时长。
- QA 探针：`record.html?segment=<name>&probe=1` 读取 `durationFrames/fps`；录制不要带 `probe`/`loop`。

## 6. 何时回退 Manim

只有以下情况才在 `segments.json` 写 `engine: "manim"`：

- 极强数学公式/符号变换，Motion Canvas 实现成本明显更高；
- 用户明确要求 Manim；
- 现有 legacy 锚点无法在本次工作中迁移。

回退时：

- 调用 `manim-isolation`（legacy），单场景 ≤20 秒；
- 输出 `04_manim_src/scenes/<name>.py` 与 `03_slides/public/<name>.mp4`；
- 用 `--stage manim` 检查；
- 不要把 Manim 改回默认，也不要把 Motion 段落渲染成 MP4 再嵌入 Reveal。

## 7. 失败处理

| 现象 | 处理 |
| --- | --- |
| `[SEGMENT]` 与 `segments.json` 不一致 | 以 `segments.json` 为准修正讲稿或清单；不要猜 |
| 声明时长不是 45–90 | 调整 beat/停顿或拆分段落；不要套用 20 秒旧限制 |
| `record.html` 黑屏/不播放 | 确认 `auto="true"`，不要裸 `auto`；不要在升级前设 `quality`/`width`/`height` |
| 全屏有 UI | 用 `record.html`，不要用 `?present` |
| 字体变衬线 | 显式 `fontFamily={theme.fontFamily}` |
| 依赖缺失 | 在 `04_motion_src/` 内 `pnpm install --frozen-lockfile`；不要全局安装 |
| 时长探针为 0 | headless 下加 `&probe=1`；录制以真实浏览器为准 |

## 8. 完成标准

- `src/scenes/<name>.tsx` 与 `src/projects/<name>.ts` 存在且只表达该段落；
- `[SEGMENT]` 与 `segments.json` 一致；45–90 秒；
- `--stage motion` 无 Issues；
- 真实浏览器中 `record.html?segment=<name>` 可播放，无 UI；
- 未执行的检查标 `NOT_RUN`，不要写 `PASS`。
