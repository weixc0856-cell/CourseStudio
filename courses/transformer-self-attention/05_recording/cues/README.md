# Cues

每个 motion 段落一个 `<name>.md`，由 `tools/build-recording-package.py` 从
`02_scripts/lecture_script.md` 的 `[SEGMENT]` / `[VISUAL]` / `[HOLD]` /
`[EMPHASIS]` / `[CUT]` 区块与对应口播行生成。

本集使用 `scores_to_weights.md`，由生成器从讲稿切出并覆盖。
不要手工维护 cue 文件；讲稿才是唯一事实来源。
