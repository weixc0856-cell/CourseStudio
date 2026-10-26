# QA — transformer-self-attention

记录实际运行过的命令、退出码、结果与限制。

状态口径：

- `PASS_VERIFIED`：实际运行并核对
- `PASS_STATIC`：静态检查通过
- `PARTIAL`：部分条件无法验证
- `NOT_RUN`：未执行
- `FAIL`：实际失败

必须记录：

- `check-episode.py` 各阶段结果（research / script / motion / recording / slides / qa）
- `build-recording-package.py` 结果与 `05_recording/` 产物
- Motion：`record.html?segment=<name>` / `?probe=1` 或实拍 `ffprobe` 的真实时长
- 课件：Reveal `data-slide` / 本地资源检查；Slidev 构建/开发服务器结果
- Manim 兜底（仅 `engine=manim`）：渲染命令、MP4、`ffprobe`
- 浏览器逐页检查
- 未执行项与人工评审缺口（OBS 录制保持 `NOT_RUN`）
