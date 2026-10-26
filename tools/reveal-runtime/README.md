# Reveal.js Runtime

共享、固定版本的 Reveal.js 运行时。

- 版本：`reveal.js@6.0.2`（精确 pin）
- 安装：`pnpm --dir D:\CourseStudio\tools\reveal-runtime install`
- 不构建、不全局安装、不引入额外 Node 服务器依赖。
- `tools/reveal-run.ps1` 会把 `node_modules/reveal.js/dist` 同步到课程的
  `03_slides/.vendor/reveal/`，然后用 `python -m http.server` 服务 `03_slides`。
- `03_slides/.vendor/` 是生成目录，不进 Git。

课程默认策略：

- `course`：Reveal（`03_slides/index.html` + `assets/deck.css`）。
- `technical` / `news` / 旧课：Slidev（`03_slides/slides.md`）。
- 动画段落始终由 `04_motion_src/record.html?segment=<name>` 独立录屏；Reveal 课件只放占位，不嵌 MP4。
