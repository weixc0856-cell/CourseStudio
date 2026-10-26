# 研究输入（01_research）

本目录由 `research-to-course-synthesis` 生成。标准文件：

| 文件 | 内容 |
| --- | --- |
| `00-task-brief.md` | 任务范围、受众、目标 |
| `01-source-inventory.md` | 来源清册与检索记录 |
| `02-claim-evidence-ledger.csv` | 15 列主张—证据台账 |
| `03-knowledge-structure.md` | 概念依赖、公式、冲突 |
| `04-course-input-brief.md` | 课程内容底稿 |
| `05-quality-report.md` | Four-Gate QA |
| `06-course-outline.md` | 排课大纲 |

别名（外部管线常用）：

- `evidence_ledger.csv` → `02-claim-evidence-ledger.csv`
- `knowledge_structure.md` → `03-knowledge-structure.md`
- `course-input-brief.md` → `04-course-input-brief.md`

辅助目录：

- `search-results/`：检索原始 JSON（提交）
- `downloads/`：PDF（不提交）
- `fulltext/`：逐页文本（不提交）
- `scripts/`：抽取与核验脚本（提交）

## news / podcast

不使用 00–06 时，必须提供：

- `source-register.md`（非空）
- `claims-ledger.md`（非空，且含 `FACT` 或 `CLAIM` 条目）

`check-episode.py --mode news|podcast --stage research` 会严格检查这两个文件。
