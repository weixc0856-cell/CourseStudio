# Episode 管线审计：当前状态、历史修复与待办

- **更新日期**：2026-10-26
- **适用范围**：`D:\CourseStudio\courses\` 下的课程、新闻、技术解读与播客
- **远程**：`git@github.com:weixc0856-cell/CourseStudio.git`（`main`）
- **结论摘要**：Motion Canvas + Reveal 框架升级完成，严格 QA 与 32 项回归已落地；第一集 `transformer-self-attention` 已到**录制就绪**，人工 OBS/后期仍为 `NOT_RUN`。

> 本文件分为三部分：当前状态、历史审计与已修复记录、已知限制与待办。历史章节中的 `BLOCKED` / `PARTIAL` 是当时的审计结论，不代表当前状态。

---

## 1. 当前状态与最新验收结论

### 1.1 当前架构

```text
Episode 目录契约
  → paper-search + research-to-course-synthesis（研究输入）
  → course-studio（讲稿 + [SLIDE]/[ANIMATION] + [SEGMENT] 节奏标注）
  → motion-isolation（45–90s Motion Canvas 叙事段落）
  → build-recording-package.py（05_recording 录制就绪包）
  → Reveal（course 默认）/ Slidev（technical/news/旧课）
  → check-episode.py --stage qa --strict
  → OBS 人工录制（NOT_RUN）

Manim：仅 segments.json engine="manim" 的兜底路径，不是默认。
```

默认布局与约束见 [episode-pipeline.md](episode-pipeline.md)；分块状态机见 [claude-orchestrator.md](claude-orchestrator.md)；硬性要求见 [requirements.md](../guides/requirements.md)。

### 1.2 组件状态

| 组件 | 当前状态 | 说明 |
| --- | --- | --- |
| `paper-search` | `PASS_VERIFIED` | CLI + Skill 可用；25 个来源；**不是 MCP** |
| `research-to-course-synthesis` | `PASS_VERIFIED` | 曾用 11 篇全文跑通 `00`–`06`、46 条主张、91/91 定位 |
| `course-studio` | `PASS_STATIC` | 已注册，5 个 reference 完整；新 prompt 要求节奏标注与 Motion 主路径 |
| Motion Canvas | `PASS_VERIFIED` | 3.17.2 + Vite 5.4.21；45s probe；`record.html` 真浏览器可播 |
| Reveal 运行时 | `PASS_VERIFIED` | 6.0.2；`reveal-run` 同步 `.vendor` + Python 静态服务；data-slide/资源检查 |
| Slidev 运行时 | `PASS_VERIFIED` | `@slidev/cli 53.0.0`；technical/news/旧课 |
| `motion-isolation` | `PASS_VERIFIED` | 3B1B 风格、45–90s、`[ANIMATION]`/`[SEGMENT]`/`record.html` |
| `manim-isolation` | `PASS_VERIFIED`（legacy） | 仅 `engine=manim` 兜底 |
| Manim 运行时 | `PASS_VERIFIED`（legacy） | 0.22.0；仅兜底；≤20s |
| `check-episode.py` | `PASS_VERIFIED` | motion/recording/slides/qa；Reveal 静态、Slidev build、32 项回归 |
| `render-manim.ps1` | `PASS_VERIFIED`（legacy） | 180s 超时；失败保留日志；成功清理 |
| `new-episode.ps1` | `PASS_VERIFIED` | course 默认 Reveal；technical/news Slidev；默认不装 Manim |
| GitHub Actions | `PASS_VERIFIED` | `ubuntu-24.04`；py_compile + link check + 32 项回归 |
| OBS | `NOT_RUN` | 未在常规路径检测到；录制为人工阶段 |
| Playwright PDF 导出 | `NOT_RUN` | 未安装；不影响 dev/build |

### 1.3 最新验收证据

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 回归测试 | 32/32 `OK` | `python tools/test_check_episode_negative.py` |
| 链接检查 | `PASS_VERIFIED` | `tools/check-links.py` |
| 严格研究拦截 | PASS | 空/缺文件在 `--strict` 或 `qa` 下返回非零 |
| Slide 映射 | PASS | 输出 `Mapping: M anchor(s), N slide(s), buffer ...`；`M > N` FAIL |
| Motion 时长 probe | PASS | 45s 示例 = 2700 帧 / 60fps |
| Reveal 静态检查 | PASS | data-slide 1..N、本地资源、strict 跳过 Slidev build |
| 录制包 | PASS | 生成器幂等；非法源失败不写包 |
| Slidev build | PASS（technical/旧课） | `dist/index.html` 生成；非 0 即 QA FAIL |
| legacy Manim ffprobe | PASS（兜底） | 2.4s 通过；27s FAIL |
| 建集回滚 | PASS | 失败后无残留课程目录 |
| CI | `PASS_VERIFIED` | 最近一次 `main` 推送的 `CourseStudio CI` 通过 |

### 1.4 课程目录状态

| 目录 | 状态 |
| --- | --- |
| `transformer-self-attention/` | 第一集 course；Motion 68s + Reveal 12 页 + `05_recording`；内容/QA `PASS_VERIFIED`，待人工 OBS |
| `attention-research-2026-10/` | 研究输入样本；`00`–`06`、检索 JSON、台账保留；不是默认课程模板 |
| `_retired/transformer-course-pilot/` | 历史 HTML + Manim 试点；已退役归档，不参与当前流程 |
| `_retired/course-attention/` | 历史 Slidev + Manim 课程；已退役归档，`.venv` 已删除 |

### 1.5 当前结论

- 工具链、严格 QA、32 项回归和 CI 已就绪；Motion Canvas + Reveal 主路径已完成框架升级。
- 第一集 `transformer-self-attention` 已端到端跑到录制就绪：research → script → motion → recording package → Reveal → qa。
- 下一步仅人工 OBS 实拍、真实时长/音画检查与后期拼接；不进入新功能开发。

---

## 2. 历史审计与已修复记录

> 以下 v1.x 记录的是 legacy Manim/Slidev 时代；现行主路径见第 1 节。历史中的“≤20 秒”仅适用于 legacy Manim 兜底，不是 Motion 约束。

### 2.1 初始审计发现（历史）

| ID | 历史问题 | 当时状态 | 当前处理 |
| --- | --- | --- | --- |
| D-01 | `manim-isolation` 缺失/与 `course-studio` 重名 | `BLOCKED` | 新建独立 `manim-isolation` Skill；旧 ZIP 不安装 |
| D-02 | `paper-search` 不是 MCP | `PARTIAL` | 继续用 CLI + Skill；MCP 注册仍为可选 |
| D-03 | Slidev 运行时缺失 | `BLOCKED` | 本地安装 Slidev 53；`markdown-it` 锁 14.1.0 |
| D-04 | 三套目录契约冲突 | `PARTIAL` | Episode 布局定为默认 |
| D-05 | 研究输出命名不一致 | `PARTIAL` | 别名表写入 `courses/README.md` 与流程 |
| D-06 | 讲稿无强制视觉锚点 | `PARTIAL` | 强制 `[SLIDE]` / `[ANIMATION]` + 检查器 |
| D-07 | Slidev 与 `course-studio` 默认 HTML 冲突 | `PARTIAL` | 历史：当时固定 Slidev；现行 course 默认 Reveal、technical/news 用 Slidev；prompt 明确覆盖 |
| D-08 | 安装版本与 ZIP 版本漂移 | `PARTIAL` | 保留已安装版本；旧 ZIP 不再安装 |
| D-09 | 阶段之间无交接契约 | `PARTIAL` | `handoff.md` + 分块状态机 |
| D-10 | 无锚点/资产校验 | `PARTIAL` | `check-episode.py` + 回归测试 |
| D-11 | OBS 无检查清单 | `PARTIAL` | 已加 `05_recording/checklist.md`；`qa/recording-checklist.md` 仅保留为指针；OBS 仍未安装 |
| D-12 | Skill 目录是复制而非链接 | `PARTIAL` | `manim-isolation`/`paper-search` 用 junction；其余仍为副本 |
| D-13 | `.gitignore` 不覆盖 Episode 布局 | `FIXED` | 已覆盖 PDF/MP4/media/downloads 等 |

### 2.2 修复时间线

**v1.1 — 隔离与运行时**

- 锚点防逃逸：代码块/引用块/注释中的锚点判 FAIL。
- Manim API 锁：禁用 `manimlib`、3D 摄像机、粒子等。
- 历史：Manim 兜底声明时长 ≤20 秒；渲染 180 秒超时（现行 Motion 主路径为 45–90 秒）。
- Python 固定 3.12；支持 course/technical/news/podcast。
- OBS 改为高容错：允许口误，停顿 2 秒重念，后期剪辑。

**v1.2 — 分块状态机**

- 新增 `claude-orchestrator.md`，每次只推进一个子步骤。
- `check-episode.py --stage` 按阶段检查，中间阶段不误报缺失 MP4。
- 讲稿按模块 1–2 个/轮；Slidev 先骨架后填充；Manim 只做 1–2 个核心锚点。
- `handoff.md` 增加阶段、子步骤、模块/动画进度。

**v1.3 — 严格校验与真实构建**

- Slide 编号严格 1..N；重复、跳号、乱序 FAIL。
- 研究文件非空；news/podcast 要求 source + claim + `FACT`/`CLAIM`。
- 历史：legacy Manim ffprobe 读取真实 MP4 时长，超 20 秒 FAIL（现行 Motion 主路径 45–90 秒）。
- `--stage qa --strict` 实际运行 Slidev build，非 0 FAIL。
- 渲染失败保留日志；Manim 版本锁定 0.22.0；建集失败回滚。

**v1.4 — 退出码与负向回归**

- `--strict` 或 `qa` 下研究缺失/空文件直接进 `issues`，不再降级 warning。
- 资产缺失、ffprobe 不可用、时长超限在严格模式下硬失败。
- 输出 `Mapping: M anchor(s), N slide(s), buffer ...`；`M > N` FAIL。
- 新增 `test_check_episode_negative.py`，当时 7 项负向测试（现已扩展到 32 项回归）。

**v1.5 — CI 与文档同步**

- 替换通用 Python workflow：不再 flake8 扫描 vendored 代码，不再跑空 pytest。
- Runner 固定 `ubuntu-24.04`；`actions/checkout@v7` / `actions/setup-python@v7`（Node 24），消除迁移与 Node 20 弃用告警。
- CI 增加回归测试步骤。
- 修复 vendored `citeseerx.py` 缺失的 `import os`。
- 清理文档中已删除课程与历史故障的过期描述。

### 2.3 历史故障与修复

| 故障 | 修复 |
| --- | --- |
| CI flake8 报 `citeseerx.py` F821 | 补 `import os`；CI 不再扫描 vendored 代码 |
| CI 链接到未跟踪的课程文件 | 改为纯文本路径，不再做相对链接 |
| Slidev 53 搭配 markdown-it 15 报导出错误 | 锁定 `markdown-it@14.1.0` |
| pnpm store 写到 `D:\.pnpm-store` | 迁入 `tools/slidev-runtime/.pnpm-store` |
| 建集误用 Python 3.14 | `uv python pin 3.12` |
| 渲染失败后日志被 `finally` 删除 | 失败保留日志并打印 `LOG=` |
| 建集失败留下半成品目录 | `try/catch` 回滚 |
| Slide 编号重复被 `set()` 掩盖 | 改为严格序列比较 |

---

## 3. 已知限制与待办

### 3.1 已知限制

| 限制 | 影响 | 当前状态 |
| --- | --- | --- |
| OBS 未安装/未检测到 | 录制只能人工；无法自动化 | `NOT_RUN` |
| Playwright 未安装 | Slidev PDF/PPTX 导出不可用 | `NOT_RUN` |
| `paper-search` 不是 MCP | 只能通过 CLI/Skill 调用 | 已接受 |
| 第一集已到录制就绪，实拍未跑 | 端到端内容/时序已验证；OBS 画面与音画同步未验证 | `PARTIAL` |
| `course-studio` 未完整端到端 | 讲稿长度/节奏仍需实测 | `PARTIAL` |
| CI 不构建 Slidev / 不渲染 Manim | Runner 固定 `ubuntu-24.04`；CI 只保证语法、链接、回归测试 | 已知 |
| CI 的 ffmpeg/PowerShell 依赖 | Linux 使用 fake `ffprobe`，32 项回归测试全部执行；Windows 无 ffmpeg 时该用例跳过 | 已容错 |
| Skill 副本非全部链接 | 版本可能漂移 | `PARTIAL` |
| 人工教学评审缺失 | 教学效果未验证 | `NOT_RUN` |

### 3.2 待办

1. 跑第一集真实 Episode，记录实际耗时、上下文长度与失败点。
2. 确认/安装 OBS，按 `05_recording/checklist.md` 完成一次录制。
3. 如需 PDF 导出，安装 Playwright 并验证 `slidev export`。
4. 视需要把 `paper-search` 注册为 stdio MCP。
5. 评估把 `course-studio`、`research-to-course-synthesis`、`slidev` 统一为版本化 junction。
6. 如 CI 需要覆盖 Slidev build，增加 Node/pnpm 与运行时安装步骤。

### 3.3 最终判断

当前工具链可以进入内容生产，但“工具通过”不等于“课程质量通过”。真实 Episode 的内容正确性、教学效果与录制质量仍需人工验收。
