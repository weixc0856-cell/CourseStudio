# Handoff — {{EPISODE}}

| 字段 | 内容 |
| --- | --- |
| 模式 | {{MODE}} |
| 阶段 | research / script / motion / recording / slides / qa / record |
| 子步骤 | R1 / S1 / M1 / RC1 / P1 / Q1 / REC … |
| 模块进度 | 例如 2/6 |
| 段落进度 | 例如 1/3（Motion） |
| 动画引擎 | motion / manim（仅兜底） |
| 课件类型 | Reveal / Slidev |
| 录制包 | 未生成 / 已生成 / 已检查 |
| 输入文件 | |
| 输出文件 | |
| 已运行命令 | |
| 最后检查 | 命令 + 状态 |
| 验证状态 | `NOT_RUN` |
| 未决事项 | |
| 下一步 | |

> 每次 `/clear` 前更新本文件。下一阶段只读本文件 + 指定输入，不重读整个项目。
>
> 新 course 的阶段顺序：research → script（含节奏标注）→ motion → recording（录制就绪包）→ Reveal slides → qa → record（人工 OBS）。
> `recording` 是 `05_recording/` 包，不是 OBS 实拍；OBS 相关状态保持 `NOT_RUN`，直到人工完成。
> Manim 只用于 `segments.json` 中 `engine: "manim"` 的兜底锚点，不是默认路径。
