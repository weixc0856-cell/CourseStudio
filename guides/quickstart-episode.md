# 从零开一集 — 最短路径

适用：`course` 与 `technical`。完整契约见 [requirements.md](requirements.md)、[episode-pipeline.md](../workflows/episode-pipeline.md)；本页只给可照做的顺序与命令。

约定示例 slug：`course-example`。所有命令从 `D:\CourseStudio` 运行。

## 0. 先决条件

| 项 | 要求 |
| --- | --- |
| Python | 3.12；用于检查器、录制包生成器、静态服务器 |
| Node / pnpm | Node 24 + pnpm 10；Motion 依赖只装课程内，Reveal/Slidev 用共享运行时 |
| 浏览器 | Chrome；录制全屏使用 |
| OBS | 人工安装与操作；AI 不调用，状态保持 `NOT_RUN` |

## 1. 建集

```powershell
# course：Motion Canvas + Reveal
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 `
  -Name course-example -Mode course

# technical：Motion Canvas + Slidev
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 `
  -Name technical-example -Mode technical
```

- 默认 **不安装 Manim**；只有极强公式兜底才加 `-WithManim`。
- `course` 保留 `03_slides/index.html`（Reveal），删除 Slidev 模板。
- `technical` 保留 `03_slides/slides.md`（Slidev），删除 Reveal 模板。
- 不在根仓库 `git add courses/`；需要版本管理时在课程目录内 `git init`。

建集后检查：

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage research
```

R0 之前只有模板，研究检查通常不是 PASS；这是预期，不要伪造研究文件。

## 2. 研究 R0–R4（每轮停下）

| 轮次 | 只做的事 | 产物 |
| --- | --- | --- |
| R0 | 冻结受众、目标、范围、非目标、动画候选 | `01_research/00-task-brief.md` |
| R1 | 登记来源、访问方式、主证据定位 | `01-source-inventory.md`、`search-results/` |
| R2 | 建主张台账，区分 FACT/CLAIM/INFERENCE/ASSUMPTION | `02-claim-evidence-ledger.csv` |
| R3 | 冻结符号、公式、形状、玩具数字、动画最小子集 | `03-knowledge-structure.md` |
| R4 | 冻结课程输入简报、质量报告、大纲 | `04`、`05`、`06` |

- **每轮只写该轮文件**；写完更新 `handoff.md` 并停下等确认。
- R4 完成后跑：

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage research
```

- 研究文件必须非空；关键主张必须有 `CLM-XXX` 与页码/公式/表格定位。

## 3. 讲稿 S1–S4

按大纲模块每次写 1–2 个，**追加**到 `02_scripts/lecture_script.md`。

```text
[SLIDE: 05]
[ANIMATION: attention_scores]
[SEGMENT: attention_scores | 68s | order=1]
[VISUAL 00:00] 建立 score 矩阵
[HOLD 00:08] 停 4 秒
[EMPHASIS 00:20] 高亮缩放
[CUT 00:34] 切到行 softmax
[EMPHASIS 00:48] 对比集中与均匀
[VISUAL 01:02] 停在 A
```

硬规则：

- `[SLIDE: NN]` 严格 1..N，纯文本独立成行；不要包在代码块、引用或 HTML 注释里。
- 每个 motion 段落恰好一个 `[SEGMENT]`；45–90 秒；至少各一条 `HOLD` / `EMPHASIS` / `CUT`；时间戳严格递增且不超过声明时长。
- name / 时长 / order 必须与 `04_motion_src/segments.json` 一致。
- 不在第 1 个模块里写后面的公式或结论。

每轮检查：

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage script
```

## 4. Motion：segments.json → scene/project → record.html

先冻结 `04_motion_src/segments.json`：

```json
{
  "canvas": {"width": 1920, "height": 1080, "fps": 60},
  "segments": [
    {
      "name": "attention_scores",
      "engine": "motion",
      "duration_seconds": 68,
      "order": 1,
      "scene": "attention_scores",
      "project": "attention_scores",
      "record_status": "NOT_RUN"
    }
  ]
}
```

再写两个文件：

```text
04_motion_src/src/scenes/attention_scores.tsx
04_motion_src/src/projects/attention_scores.ts
```

- 使用 `04_motion_src/src/theme.ts` 的橙白视觉 token；显式 `fontFamily={theme.fontFamily}`。
- 一个段落一个 scene/project；45–90 秒；最后停在可录制的稳定画面。
- 不渲染 MP4、不把动画嵌进 Reveal。

启动录制页：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
  -Episode course-example -Segment attention_scores
```

打开打印的：

```text
http://localhost:9100/record.html?segment=attention_scores
```

- **不要用 `?present` 录制**：全屏仍有演示控件。
- 首次运行会在课程 `04_motion_src/` 内安装依赖；不要全局 `npm install -g`。
- QA 探针可用 `&probe=1` 读取时长；录制时不要带 `probe`/`loop`。

检查：

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage motion
```

## 5. 录制就绪包

```powershell
python D:\CourseStudio\tools\build-recording-package.py course-example
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage recording
```

生成：

- `05_recording/manifest.json`：顺序、URL、声明时长、cue、`record_status`
- `05_recording/cues/<name>.md`：画面节拍 + 口播
- `05_recording/checklist.md`：段落表与录制清单

`recording` 阶段只验证包结构；**不是 OBS 实拍**。录像文件仍为 `NOT_RUN` / `NOT_VERIFIED`，直到人工录制。

## 6. Reveal P1 → P2

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 `
  -Episode course-example -Port 3040
```

打开 `http://127.0.0.1:3040/index.html`，F11 全屏。

- P1：先搭 12 页骨架，`data-slide` 1..N。
- P2：每页一个主要教学点，填公式/数字/要点；不要把整段讲稿粘进页面。
- 动画页只放 `record.html?segment=<name>` 占位卡，不嵌 MP4。
- `.vendor/reveal/` 由 `reveal-run.ps1` 同步，不提交。

检查：

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage slides
```

## 7. QA

```powershell
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage qa
python D:\CourseStudio\tools\check-episode.py course-example --mode course --stage qa --strict
python D:\CourseStudio\tools\check-links.py courses\course-example
python D:\CourseStudio\tools\test_check_episode_negative.py
```

- `Issues` 必须为空。
- Reveal 的 strict QA 会跳过 Slidev build；这是预期。
- 回归测试当前 **32 项**。
- 浏览器逐页检查；Motion 关键帧抽帧检查。

## 8. 人工 OBS 录制

建议顺序：**先录 Motion 动画段，再录 Reveal 课件页**。

Motion 段：

1. 运行 `motion-run.ps1`，打开 `record.html?segment=<name>`。
2. Chrome 全屏，等 2 秒避开全屏提示。
3. OBS 用 **Display Capture** 或 **Window Capture (Windows Graphics Capture)**；不要用 BitBlt/GDI，Chrome 会黑屏。
4. OBS 画布 1920×1080 / 60fps；4K + 150% 缩放下对源缩放，不改画布。
5. 每段录前/后各留 2 秒；录完停止，不在同一文件接下一段。
6. 用 `ffprobe` 核对时长；回填 `manifest.json` 的 `record_status`。

课件页：

1. `reveal-run.ps1` 启动，Chrome 全屏。
2. 按页序录制；不要用 `?present`。
3. 录完核对导航、字体、无控制条。

OBS 由人工完成；本仓库不安装、不调用、不自动化 OBS。

## 9. 常见失败

| 现象 | 原因 / 处理 |
| --- | --- |
| `record.html` 不播放 | `auto` 必须写 `auto="true"`；裸 `auto` 会被当成 false |
| 全屏有 UI | 用了 `?present`；改用 `record.html?segment=<name>` |
| OBS 捕获 Chrome 全黑 | 用了 BitBlt/GDI；改用 Display Capture 或 Windows Graphics Capture |
| Motion 依赖装到全局 | 只用 `motion-run.ps1` / 课程内 `pnpm install --frozen-lockfile` |
| Vite 插件报 `motionCanvas is not a function` | `package.json` 不要写 `"type": "module"` |
| Node 版本异常 | 当前验证 Node 24 + Vite 5.4.21；先跑模板冒烟，不要直接升 Node |
| `--stage motion` 缺 cue | 先运行 `build-recording-package.py`，不要让 cue 永久缺失 |
| Reveal 缺资源 | 先运行 `reveal-run.ps1` 同步 `.vendor` |
| `data-slide` 跳号/缺页 | 按 1..N 修正；`M > N` 会 FAIL |
| strict QA 说 Build SKIPPED | Reveal 路径预期；Slidev 才实际 build |

## 10. 开第二集前检查清单

- [ ] 已读 `CLAUDE.md` 与本页，确认当前主路径是 Motion Canvas + Reveal（technical 用 Slidev）
- [ ] 新建目录后已在课程内 `git init`，没有在根仓库 `git add courses/`
- [ ] `segments.json`、讲稿 `[SEGMENT]` 与声明时长一致
- [ ] 每个 Motion 段落有 scene/project/cue，且 45–90 秒
- [ ] Reveal 12 页 `data-slide` 严格 1..N；无远程字体/脚本
- [ ] `05_recording/checklist.md` 已有实际 URL、顺序、OBS 输出路径
- [ ] `--stage qa --strict` 无 Issues；Reveal Build 可 SKIPPED
- [ ] 32 项回归测试通过
- [ ] OBS 人工录制前，`record_status` 仍为 `NOT_RUN`
- [ ] 人工录完后回填 `record_status`、真实时长与抽帧结果
