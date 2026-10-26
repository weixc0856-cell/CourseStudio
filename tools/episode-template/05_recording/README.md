# 录制就绪包 — {{EPISODE}}

本目录是每个 Episode 的最终交付物，不是中间产物。它描述「按什么顺序、打开哪个页面、录多长时间、录完检查什么」。

- `manifest.json`：段落顺序、录制 URL、声明时长、cue 文件与 `record_status`。由 `tools/build-recording-package.py` 从 `02_scripts/lecture_script.md` 与 `04_motion_src/segments.json` 生成；不要手工维护，`record_status` 会被生成器保留。
- `checklist.md`：录制日人工清单；`<!-- RECORDING-SEGMENTS:START -->` 与 `END` 之间的段落表由生成器刷新。
- `cues/`：每个段落的口播 + 画面指令，由讲稿切出；`example.md` 是与模板讲稿对齐的样例，生成器会覆盖。
- `recordings/`：实际录屏，本地产物，不进 Git；目录或文件缺失不算录制包不完整。

重新生成：

```powershell
python D:\CourseStudio\tools\build-recording-package.py {{EPISODE}}
```

OBS 由人工启动和操作；本仓库不安装、不调用、不自动化 OBS。所有 OBS 相关检查标 `NOT_RUN`。
