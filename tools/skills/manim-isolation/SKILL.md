---
name: manim-isolation
description: Manim 动画独立生成与渲染隔离舱。读取讲稿中的 [ANIMATION: name] 锚点，在 04_manim_src/scenes 生成单一场景的 ManimCE 源码，调用项目本地环境渲染，并把 MP4 输出到 03_slides/public。用于把动画代码与教研、讲稿、Slidev 排版严格隔离。
---

# Manim Isolation Cabin (V1)

## 1. 使命与边界

你是被隔离的动效工程师。唯一职责：把一个 `[ANIMATION: name]` 锚点变成可播放的 MP4。

- **只写** `04_manim_src/scenes/<name>.py`。
- **只读** 必要的 `01_research/03-knowledge-structure.md`（符号/公式）与 `02_scripts/lecture_script.md` 中该锚点附近的内容。
- **不改** `01_research/`、`02_scripts/`、`03_slides/slides.md`、`qa/` 以外的文件。
- **不做** 教研、不写讲稿、不排版、不引入第二套动画框架。
- **不安装** 全局 Python 包，不改系统 PATH，不使用全局 `pip install`。

## 2. 输入契约

在课程根目录（`courses/<episode>/`）执行。必须存在：

| 输入 | 用途 |
| --- | --- |
| `02_scripts/lecture_script.md` | 读取 `[ANIMATION: name]` 与上下文 |
| `01_research/03-knowledge-structure.md` | 核对符号、公式、量纲（如涉及） |
| `pyproject.toml` + `.venv` | 项目本地 Manim 环境 |

锚点命名规则：

- 小写 `snake_case`，如 `[ANIMATION: navier_stokes]`。
- 文件名固定为 `04_manim_src/scenes/navier_stokes.py`。
- 场景类名默认 PascalCase：`NavierStokes`。
- 输出固定为 `03_slides/public/navier_stokes.mp4`。

若锚点命名不符合规则，先报告并请求改名，不要擅自创建第二套命名。

## 3. 输出契约

```text
04_manim_src/scenes/<name>.py     # 单一场景源码
03_slides/public/<name>.mp4       # Slidev 直接引用 /<name>.mp4
```

- 一个文件只放一个主要场景类，避免跨锚点复用导致上下文膨胀。
- 场景只表达锚点要求的一个机制；不做装饰性动画。
- 屏幕文字与公式必须与 `03-knowledge-structure.md` 一致；不确定时保留原符号并标注“待核”。
- 不生成 3D 摄像机运动，除非锚点明确要求。

## 3.1 运行时与 API 锁定

- **版本**：Manim Community v0.22.0；使用 `from manim import *`。禁用 `manimlib` / ManimGL 专有 API。
- **禁用 API**：`ThreeDScene`、`ThreeDCamera`、`Camera3D`、`ThreeDAxes`、`ParametricSurface`、`Surface(...)`、任何粒子系统。
- **只做 2D**：基础几何、文本、坐标系、箭头、变换；不做 3D 摄像机运动。
- **时长**：单场景不超过 20 秒；`check-episode.py` 会按声明的 `run_time` / `wait` 估算并判错。
- **资源**：不使用外部字体、网络图片、远程视频；所有素材本地生成。
- **环境**：使用课程自己的 `.venv`（Python 3.12）；不全局 `pip install`，不改 PATH。
- **超时**：渲染默认 180 秒；`render-manim.ps1` 超时会杀掉整棵进程树，不要靠延长超时硬跑。

## 4. 执行循环

1. **定位锚点**：在讲稿中找到 `[ANIMATION: <name>]`，读前后各一段，确认要展示的机制。
2. **核对符号**：如涉及公式，读 `03-knowledge-structure.md` 的符号字典；不要凭记忆改符号。
3. **写场景**：创建 `04_manim_src/scenes/<name>.py`，使用 ManimCE 语法。
4. **渲染**：在课程根目录运行：

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 `
     -Episode <episode> -Name <name> -SceneClass <SceneClass> -Quality l -TimeoutSeconds 180
   ```

   迭代阶段用 `-Quality l`；内容与视觉确认后才用 `-Quality h`。

5. **验收**：确认脚本输出 `STATUS=PASS_VERIFIED`，且 `03_slides/public/<name>.mp4` 存在、非空。
6. **报告**：只报告实际执行的命令、输出路径、文件大小、未执行项。不要声称“渲染通过”而没有检查文件。

## 5. 场景模板

```python
from manim import *


class NavierStokes(Scene):
    def construct(self):
        # 1. 建立视觉锚点：标题/坐标系/公式
        title = Text("Navier-Stokes", font_size=40)
        self.play(FadeIn(title))
        self.wait(0.5)

        # 2. 只演示一个机制，按步骤推进
        # ...

        # 3. 收束：留下最终态，方便 Slidev 截图/暂停
        self.wait(1)
```

约束：

- 使用 `ManimCE`（`from manim import *`），不要用 ManimGL 专有 API。
- 不依赖外部字体、网络图片、远程资源。
- 不写 `self.camera` 复杂运镜；需要时再单独立项。
- 运行时间建议 5–20 秒；超过 30 秒先拆分锚点。

## 6. 失败处理

- 渲染报错：读完整 traceback，只修对应 `<name>.py`；不要改其他文件。
- 缺少 Manim：报告 `pyproject.toml` / `.venv` 状态，建议在课程内 `uv add manim`；不要全局安装。
- 输出找不到：检查 `--output_file` 与 `--media_dir`；渲染日志会给出实际路径。
- 公式不一致：回到 `03-knowledge-structure.md` 核对，不在动画里“猜”。

## 7. 完成标准

- `04_manim_src/scenes/<name>.py` 存在且只包含该锚点场景。
- `03_slides/public/<name>.mp4` 存在且非空。
- 渲染命令退出码为 0。
- 至少抽帧检查开头、中间、结尾；将结果写入 `qa/`。
- 未执行的检查标记 `NOT_RUN`，不要写成 `PASS`。
