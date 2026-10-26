# Known limitations

记录当前已知、但不阻塞新集创建的限制。没有实际复测的项不要升级成 `PASS`。

| 项 | 状态 | 说明 / 处理 |
| --- | --- | --- |
| OBS 实拍 | `NOT_RUN` | OBS 由人工安装与操作；本仓库不安装、不调用、不自动化。`record_status` 保持 `NOT_RUN`，直到人工录制完成 |
| 真实录像时长/音画同步 | `NOT_RUN` | `transformer-self-attention` 的 68s 是 Motion 播放器探针结果，不是 OBS 实拍；录制后用 `ffprobe` 与抽帧复核 |
| 人工全屏视觉 QA | `NOT_RUN` | 已用 headless Chrome 逐页/关键帧截图；仍不能替代人眼全屏与 OBS 画面检查 |
| Reveal 的构建检查 | 设计如此 | Reveal 路径无构建步骤；`--stage qa --strict` 输出 `Build: SKIPPED (Reveal deck...)` |
| Slidev PDF 导出 | `NOT_RUN` | 需要 Playwright；当前未安装。不影响 Slidev dev/build 与 Reveal 流程 |
| `paper-search` | 已知 | 是项目内 CLI + Skill，不是已注册 MCP |
| Manim | legacy | 仅 `segments.json` 的 `engine: "manim"` 兜底；单场景 ≤20s，不是默认动画路径 |
| 旧课程 | 已退役 | `courses/_retired/` 仅作对照；不作为模板、不作为默认路径、不保证可重建 |
| Node/Vite | 已知 | Motion 使用 Node 24 + Vite 5.4.21；Vite 会打印 CJS Node API deprecation warning，当前不影响运行 |
| 自动 TTS/剪辑 | 未实现 | 本仓库不自动配音、不自动合并长视频；录音与后期由人工完成 |
| 教学效果 | `NOT_RUN` | 没有学习者测试或人工教学评审，不能写教学效果 `PASS` |

处理原则：

- 小问题先记录，不扩散成新的大重构。
- 阻塞录制/交付的问题才修改核心实现；改检查器前先确认是文档/一致性需求。
- 未运行的检查保持 `NOT_RUN`；部分完成的写 `PARTIAL`。
