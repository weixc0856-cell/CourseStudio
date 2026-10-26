# QA — {{EPISODE}}

记录实际运行过的命令、退出码、结果与限制。

状态口径：

- `PASS_VERIFIED`：实际运行并核对
- `PASS_STATIC`：静态检查通过
- `PARTIAL`：部分条件无法验证
- `NOT_RUN`：未执行
- `FAIL`：实际失败

必须记录：

- `check-episode.py` 结果
- Slidev 构建/开发服务器结果
- Manim 渲染命令与输出文件
- 浏览器逐页检查
- 未执行项与人工评审缺口
