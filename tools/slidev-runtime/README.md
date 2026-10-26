# Slidev Runtime (project-local)

本目录是 CourseStudio 的共享 Slidev 运行时，所有依赖都装在 `node_modules/`，不安装全局 npm 包。

## 版本

- `@slidev/cli` 53.0.0
- `@slidev/theme-default` 0.25.0
- `vue` 3.5.44
- `markdown-it` 14.1.0（锁定；`@comark/markdown-it` 只支持 14.x，15.x 会导致 `ERR_PACKAGE_PATH_NOT_EXPORTED`）

## 用法

在 `D:\CourseStudio` 下运行：

```powershell
# 开发服务器（OBS/浏览器预览）
powershell -NoProfile -ExecutionPolicy Bypass -File tools\slidev-run.ps1 -Episode <episode> -Mode dev -Port 3030

# 构建静态站点
powershell -NoProfile -ExecutionPolicy Bypass -File tools\slidev-run.ps1 -Episode <episode> -Mode build
```

或直接：

```bash
pnpm --dir D:\CourseStudio\tools\slidev-runtime exec slidev D:\CourseStudio\courses\<episode>\03_slides\slides.md --port 3030
```

## 说明

- `slides.md` 与 `public/` 位于课程目录；本目录只提供 CLI 和依赖。
- pnpm store 固定在本目录 `.pnpm-store/`（由 `.npmrc` 指定），不会写到 `D:\.pnpm-store`。
- 重新安装：`pnpm install`（在本目录）。
- 不要删除 `pnpm-lock.yaml`；它锁定了可用组合。
- `dist-smoke/` 是构建冒烟测试产物，可删除。
