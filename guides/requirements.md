# 课程制作与维护要求

本文件把当前管线中**可执行、可检查**的要求集中列出。凡是标为“必须”的项，都有对应的脚本或流程强制；没有实际运行检查，不得写成 `PASS`。

- 版本：2026-10-26
- 适用：`D:\CourseStudio\courses\<slug>` 下的课程、新闻、播客与技术解读
- 配套：[workflows/episode-pipeline.md](../workflows/episode-pipeline.md)、[guides/episode-tutorial.md](episode-tutorial.md)、[guides/repository-and-remote.md](repository-and-remote.md)

## 1. 仓库与目录

| 要求 | 规则 |
| --- | --- |
| 产物根目录 | 统一放在 `D:\CourseStudio\courses\<slug>` |
| 根仓库范围 | 只跟踪框架：`CLAUDE.md`、`README.md`、`guides/`、`workflows/`、`prompts/`、`tools/` |
| 课程仓库 | 每门课程在 `courses/<slug>` 内独立 `git init`；根仓库忽略 `/courses/*`，仅保留 `courses/README.md` |
| 实验环境 | `labs/` 不进根仓库；不是课程交付物 |
| 禁止提交 | `.env`、密钥、PDF 全文、`01_research/downloads/`、`fulltext/`、`03_slides/public/*.mp4`、`04_manim_src/media/`、`dist/`、`.venv*/`、`node_modules/`、`.pnpm-store/` |

## 2. 研究输入

| 模式 | 必须 | 检查命令 |
| --- | --- | --- |
| `course` / `technical` | `01_research/00`–`06` 全部存在且非空 | `--stage research` |
| `news` / `podcast` | `source-register.md` 与 `claims-ledger.md` 同时存在且非空；台账含 `FACT` 或 `CLAIM` | `--stage research` |

内容要求：

- 每条关键主张有 `CLM-XXX` 与页码/公式/表格定位。
- 区分 `FACT` / `CLAIM` / `INFERENCE` / `ASSUMPTION`。
- 冲突保留双方证据、定义与适用范围。
- `05-quality-report.md` 写明 `NOT_RUN` / `PARTIAL` / 未决项。
- 空文件、只有标题没有内容的台账、无 `FACT`/`CLAIM` 的台账，均不能通过。

## 3. 讲稿与视觉锚点

必须使用纯文本、独立成行的锚点：

```text
[SLIDE: 01]
[ANIMATION: navier_stokes]
```

| 要求 | 规则 |
| --- | --- |
| Slide 编号 | 严格 `01, 02, 03...`；重复、跳号、乱序均 `FAIL` |
| Animation 命名 | 小写 `snake_case`；一个名字对应一个场景 |
| 禁止包裹 | 不得放在代码块（三反引号）、引用块（`>`）或 HTML 注释（`<!-- -->`）中 |
| 与页面一致 | `[SLIDE]` 编号不得超过 `slides.md` 的实际页数 |
| 分块写作 | 按大纲模块 1–2 个/轮追加；不要一次写完再检查 |

检查：`python D:\CourseStudio\tools\check-episode.py <slug> --mode <mode> --stage script`

## 4. Slidev 课件

| 要求 | 规则 |
| --- | --- |
| 文件 | `03_slides/slides.md` |
| 分步 | P1 只建标题/分页骨架 → P2 逐模块填充 |
| 动画 | 只写 `<video src="/name.mp4" controls class="w-full" />`，不写 Manim 代码 |
| 资源 | MP4 放在 `03_slides/public/`；构建产物在 `dist/`（不提交） |
| 构建 | `slidev-run.ps1 -Mode build` 退出码必须为 0 |

检查：`--stage slides`；构建由 `tools/slidev-run.ps1` 执行。

## 5. Manim 动画

| 要求 | 规则 |
| --- | --- |
| 版本 | Manim Community **0.22.0**；`uv add manim==0.22.0` |
| 语法 | `from manim import *`；禁用 `manimlib` / ManimGL |
| 禁用 API | `ThreeDScene`、`ThreeDCamera`、`Camera3D`、`ThreeDAxes`、`ParametricSurface`、`Surface(...)`、粒子系统 |
| 场景 | 单文件、单场景；只做基础 2D 几何与文本 |
| 时长 | 声明时长与真实 MP4 时长都必须 ≤20 秒 |
| 资源 | 不使用外部字体、网络图片、远程视频 |
| 环境 | 只用课程自己的 `.venv`；不全局 `pip install` |
| 渲染 | `render-manim.ps1` 默认 180 秒超时；超时杀进程树 |
| 失败日志 | 渲染失败时日志保留，按控制台 `LOG=` 路径排查；成功才清理 |
| 输出 | `03_slides/public/<name>.mp4` |

检查：`--stage manim`；真实时长由 `ffprobe` 读取。

## 6. 终检（QA）

`course` / `technical` 的终检命令：

```powershell
python D:\CourseStudio\tools\check-episode.py <slug> --mode technical --stage qa --strict
python D:\CourseStudio\tools\check-links.py courses\<slug>
```

必须满足：

- `Issues` 为空；中间阶段允许 `PARTIAL`，终检不放行缺失资源。
- `[SLIDE]` 严格 1..N；研究文件非空；MP4 真实时长 ≤20 秒。
- `course` / `technical` 会**实际运行** `slidev-run.ps1 -Mode build`；非 0 即 `FAIL`。
- 浏览器逐页检查：16:9、导航、视频、控制台。
- Manim 抽帧检查：开头、中间、结尾。
- `handoff.md` 已更新；`Warnings` 逐条记录。
- 状态只用 `PASS_VERIFIED` / `PASS_STATIC` / `PARTIAL` / `NOT_RUN` / `FAIL`。

**文件生成不等于验收通过。** 只有实际运行并通过检查的项才能写 `PASS_VERIFIED`。

## 7. 过期文件与课程清理

### 7.1 可以清理（可重建/无交付价值）

| 类型 | 例子 | 说明 |
| --- | --- | --- |
| 测试/冒烟项目 | `zz-smoke-test/`、`zz-*/` | 无正式交付内容 |
| 课程虚拟环境 | `courses/<slug>/.venv` | 用 `uv sync` 重建 |
| 浏览器验收缓存 | `qa/chrome-profile*` | 可重新生成 |
| 构建产物 | `03_slides/dist/`、`animations/rendered/`、`04_manim_src/media/` | 由源码重建 |
| 研究原始大件 | `01_research/downloads/`、`fulltext/` | 可按来源重新下载/抽取 |
| 空 Git 仓库 | 无任何 commit 的 `.git` | 无历史可保留 |
| 缓存 | `.uv-cache/`、pnpm store | 用 `uv cache prune` / `pnpm store prune` |

### 7.2 必须保留

- 课程源码：`course/` 或 `03_slides/`、`04_manim_src/`、`design/`、`scripts/`
- 研究结论：`00`–`06`、`search-results/`、`claims.json`、`quote-verification.csv`、`source-register.md`、`claims-ledger.md`
- QA 报告：`qa/*.md`、必要的截图/抽帧证据
- 复现文件：`pyproject.toml`、`uv.lock`、`.python-version`、`.gitignore`
- 最终交付视频（如果已生成且不再重渲）

### 7.3 清理顺序

1. 确认目标不是活跃课程；`git status` 干净或已备份。
2. 有价值但不确定的内容，先复制到仓库外备份。
3. 删除可重建环境与缓存（逐项路径，不要整盘通配）。
4. 更新 `README.md` 与 `courses/README.md` 的“现有项目/状态”。
5. 运行 `tools/check-links.py .`。
6. 人工确认后提交/推送。

### 7.4 安全命令

```powershell
# 课程环境（可重建）
Remove-Item D:\CourseStudio\courses\<slug>\.venv -Recurse -Force

# 浏览器 profile（可重建）
Remove-Item D:\CourseStudio\courses\<slug>\qa\chrome-profile* -Recurse -Force

# 研究大件（可重取）
Remove-Item D:\CourseStudio\courses\<slug>\01_research\downloads -Recurse -Force
Remove-Item D:\CourseStudio\courses\<slug>\01_research\fulltext -Recurse -Force

# 缓存（只清未使用）
$env:UV_CACHE_DIR = 'D:\CourseStudio\.uv-cache'
uv cache prune
pnpm --dir D:\CourseStudio\tools\slidev-runtime store prune
```

不要删除：

- `tools/slidev-runtime/node_modules` 或 `.pnpm-store`（会破坏当前 Slidev 运行时；需要时用 `pnpm install` 重建）
- `tools/paper-search-mcp/.venv`（paper-search CLI 依赖；需要时 `uv sync` 重建）
- 正在使用的课程 `.venv`
- 唯一的最终成片或授权素材

## 8. Git 与推送

| 要求 | 规则 |
| --- | --- |
| 根仓库 | 只提交框架；`courses/*` 与 `labs/` 不进入根仓库 |
| 课程仓库 | 在课程目录独立提交；不要用根仓库 `git add courses/` |
| 提交前 | `git diff --cached --stat` + `git status --short`；确认无密钥/大文件 |
| 推送 | 人工确认后 `git push`；不自动推送 |
| 远程 | `git@github.com:weixc0856-cell/CourseStudio.git`，分支 `main` |
| 换行 | `.gitattributes`：源码/文档 LF，PowerShell/cmd CRLF |

## 9. 要求与执行工具对照

| 要求 | 强制工具 |
| --- | --- |
| 严格 slide 编号、防逃逸、非空研究、ffprobe、Slidev build | `tools/check-episode.py` |
| Manim API/时长/真实时长 | `check-episode.py` + `manim-isolation` Skill |
| 渲染超时与失败日志 | `tools/render-manim.ps1` |
| Manim 版本锁定、建集回滚 | `tools/new-episode.ps1` |
| 课程/根仓库边界 | `.gitignore` + `tools/course.gitignore` |
| 远程与克隆 | [repository-and-remote.md](repository-and-remote.md) |
| 分块与停点 | [claude-orchestrator.md](../workflows/claude-orchestrator.md) |

## 10. 当前例外与未验证项

- OBS 未在常规路径检测到；录制为人工阶段，状态 `NOT_RUN`。
- Slidev PDF 导出需要 Playwright；当前未安装。
- `paper-search` 是 CLI + Skill，不是已注册 MCP。
- 人工教学评审与学习者测试不在自动流程内。
- 真实 Episode 尚未开跑；当前只有临时 fixture 验证。
