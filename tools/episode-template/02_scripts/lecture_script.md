# Lecture Script — {{EPISODE}}

> 锚点契约（不可省略）：
> - `[SLIDE: NN]`：翻到第 NN 页
> - `[ANIMATION: <name>]`：一个 45–90 秒的动画段落；主路径对应 `04_motion_src/src/scenes/name.tsx`
> - 动画名使用小写 snake_case；Manim 兜底才对应 `04_manim_src/scenes/name.py` 与 `03_slides/public/name.mp4`
> - 每个 motion `[ANIMATION: <name>]` 必须配一个 `[SEGMENT: name | NNs | order=N]`，声明 45–90 秒
> - 段落内至少各一条 `[HOLD mm:ss]`、`[EMPHASIS mm:ss]`、`[CUT mm:ss]`；`[VISUAL mm:ss]` 记录画面指令
> - 时间戳严格递增，最后一条不超过声明时长；缺少或乱序会被 `--stage script` / `--stage motion` 判 FAIL
> - `[SEGMENT]` 的 name / 时长 / order 必须与 `04_motion_src/segments.json` 一致
> - 锚点必须纯文本独立成行；禁止包在代码块、引用块或 HTML 注释中（会被 `check-episode.py` 判 FAIL）
> - 录制包由 `tools/build-recording-package.py` 从本讲稿 + `segments.json` 生成；不要手工维护 manifest / cues
> - 讲稿只描述画面，不重复页面全文

## S01 — 开场

[SLIDE: 01]

（口播内容）

## S02 — 机制

[SLIDE: 02]

[ANIMATION: example]
[SEGMENT: example | 45s | order=1]
[VISUAL 00:00] 网格与标题淡入，建立坐标平面
[HOLD 00:05] 停 2 秒，让观众看清 a、b 的起点
[EMPHASIS 00:15] 高亮平移后的 b 与平行四边形
[CUT 00:23] 切到合力箭头，保留旧元素
[VISUAL 00:33] 收束到 a + b，停留到段落结束
（口播：先把 a 接上 b；从原点指向终点的箭头就是 a + b。）


## S03 — 证据与边界

[SLIDE: 03]

（口播内容）
