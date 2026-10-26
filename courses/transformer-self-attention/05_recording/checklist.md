# Recording Checklist — transformer-self-attention

## 本集录制参数

| 项 | 值 |
| --- | --- |
| Episode | `transformer-self-attention` |
| Segment | `scores_to_weights` |
| Order | `1`（唯一 Motion 段落） |
| Declared | `68s` |
| URL | `http://localhost:9100/record.html?segment=scores_to_weights` |
| Cue | `05_recording/cues/scores_to_weights.md` |
| Output | `05_recording/recordings/scores_to_weights.mp4`（本地，不提交） |
| Record status | `NOT_RUN`（录完再回填） |

## 启动命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:/CourseStudio/tools/motion-run.ps1 `
  -Episode transformer-self-attention -Segment scores_to_weights -Port 9100
```

启动后打开：`http://localhost:9100/record.html?segment=scores_to_weights`。不要用 `?present`。

## 段落清单（由 build-recording-package.py 生成）

> 重新生成：`python tools/build-recording-package.py transformer-self-attention`
> 生成器以 `02_scripts/lecture_script.md` 与 `04_motion_src/segments.json` 为源，可重复执行。

<!-- RECORDING-SEGMENTS:START -->
| Order | Segment | URL | Declared | Cue |
| --- | --- | --- | --- | --- |
| 1 | scores_to_weights | http://localhost:9100/record.html?segment=scores_to_weights | 68s | cues/scores_to_weights.md |
<!-- RECORDING-SEGMENTS:END -->

## 录制前

- [ ] `04_motion_src/segments.json` 已冻结：每个段落 45–90 秒，`order` 连续
- [ ] 每个段落有 `src/scenes/<name>.tsx` 与 `src/projects/<name>.ts`
- [ ] 讲稿中每个 motion 段落有完整 `[SEGMENT]` + `[VISUAL]` / `[HOLD]` / `[EMPHASIS]` / `[CUT]`
- [ ] `python tools/build-recording-package.py transformer-self-attention` 已运行且无错误
- [ ] `motion-run.ps1 -Episode transformer-self-attention -Segment scores_to_weights` 能启动并打印 `record.html?segment=scores_to_weights`
- [ ] 浏览器打开录制 URL；**不要用 `?present`**（全屏后仍有 SLIDES 面板与控件）
- [ ] Chrome 全屏；等待 2 秒，避开全屏提示条
- [ ] 鼠标移出画面并隐藏；页面已设置 `cursor: none`
- [ ] OBS 已安装（人工）：参考路径 `D:\Program Files\obs-studio\bin\64bit\obs64.exe`
- [ ] OBS 源：**Display Capture** 或 **Window Capture (Windows Graphics Capture)**
- [ ] 不使用 BitBlt / GDI 窗口采集；Chrome 画面会全黑
- [ ] OBS 画布 1920×1080、60fps；4K + 150% 缩放下对源缩放，不改画布尺寸
- [ ] OBS 场景：动画画面 + 麦克风；不采集浏览器声音
- [ ] OBS 输出：`05_recording/recordings/scores_to_weights.mp4`；磁盘空间与备份路径可用
- [ ] 确认 `manifest.json` 的 `record_status` 仍为 `NOT_RUN`，录完再回填

## 每个段落

- [ ] 按 `manifest.json` 的 `order` 录制，不跳段
- [ ] 打开 `record.html?segment=scores_to_weights`；页面从第 0 帧开始
- [ ] 录制前留 2 秒静止；段落结束后再留 2 秒静止，作为拼接切点
- [ ] 口播与 cue 文件中的画面指令对齐；口误允许，停顿 2 秒后重念
- [ ] 录完停止 OBS，不在同一文件里接下一段

## 录制后

- [ ] 用 `ffprobe` 读取真实时长：

  ```powershell
  ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 `
    "05_recording/recordings/scores_to_weights.mp4"
  ```

- [ ] 与 `segments.json` / manifest 的 `declared_seconds=68s` 对比；含 2 秒前后留白时约 72s 可接受，明显偏差时检查起止点或重录
- [ ] 超出 45–90 秒必须重录
- [ ] 抽帧检查开头 / 中间 / 结尾
- [ ] 音画同步；无爆音、无长时间静音
- [ ] 录像已备份；更新 `05_recording/manifest.json` 的 `record_status`（生成器会保留该字段）
- [ ] 未录制的段落保持 `NOT_RUN`，不要写 `PASS`

> OBS 不是由 AI 调用的工具。未安装/未运行时，本阶段标 `NOT_RUN`。
