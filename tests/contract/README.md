# Contract Tests — R1

- **状态**：设计/测试 harness，不是生产检查器。
- **运行**：`python tests/contract/run_contract_tests.py`
- **退出码**：`0` 全部通过；`1` 有失败。
- **依赖**：Python 3.12 标准库。**不依赖** `jsonschema`、pnpm、Chrome、ffmpeg 或网络。

## 1. 目录

```text
tests/contract/
├── run_contract_tests.py       # 24 项契约/语义测试（mini_schema）
├── mini_schema.py              # Draft 2020-12 关键字子集的最小校验器
├── validate_with_jsonschema.py # 完整 Draft 2020-12 验证（17 项 schema/instance 检查）
├── fault-cases.json            # 11 个故障注入案例及预期
└── fixtures/
    ├── minimal-pass/           # 正向 fixture：一 claim → 一 segment → 两页 deck → 一 recording task
    │   ├── episode.json
    │   ├── research/{sources.json,claims.jsonl}
    │   ├── design.md
    │   ├── script.md
    │   ├── segments.json
    │   ├── slides/{index.html,assets/deck.css}
    │   ├── motion/{scene.tsx,project.ts}
    │   ├── 05_recording/{manifest.json,cues/seg-001.md,checklist.md,recordings/seg-001.mp4.fixture}
    │   ├── qa/{qa.static.json,qa.runtime.json}
    │   └── acceptance.json
    └── negative/               # 反向 fixture
        ├── claims-missing-field.json
        ├── claims-bad-enum.json
        ├── claims-fact-without-source.json
        ├── segments-order-gap.json
        ├── recording-verified-no-ffprobe.json
        └── episode-bad-version.json
```

## 2. 正向 fixture 的声明

`minimal-pass/` 是**合成 fixture**：

- 来源 `SRC-001` 是 `example.invalid` 的假来源；
- `05_recording/recordings/seg-001.mp4.fixture` 是文本占位文件，不是 MP4；
- `qa/qa.static.json` 与 `qa/qa.runtime.json` 的 PASS 是 fixture 输入，不是真实运行；
- `acceptance.json` 是占位人工验收，不是真实 reviewer。

它的用途是验证契约形状和交叉引用规则，**不能**作为“系统已运行”或“课程已验收”的证据。

## 3. 24 项测试

| 类别 | 数量 | 内容 |
| --- | --- | --- |
| 正向 Schema | 6 | episode、claims、segments、recording、qa.static、qa.runtime |
| 正向端到端 | 1 | 计算为 `PASS/0/READY` |
| 反向 Schema/语义 | 6 | 缺字段、坏枚举、FACT 无来源、order gap、VERIFIED 无 ffprobe、坏版本 |
| 故障注入 | 11 | 见 `fault-cases.json` |

故障注入预期：

每个案例的 `expected` 同时包含 `reason_contains` 与 `log_contains`；实现方必须保证失败日志包含该片段，而不只是退出码正确。

| Case | 预期状态 | 退出码 | 交付 | 关键原因 |
| --- | --- | --- | --- | --- |
| `missing_required_field` | `CONTRACT_ERROR` | 3 | `NOT_READY` | `claim_text` |
| `duplicate_claim_id` | `FAIL` | 1 | `NOT_READY` | duplicate claim |
| `unresolved_source` | `FAIL` | 1 | `NOT_READY` | unknown source |
| `missing_deck_asset` | `FAIL` | 1 | `NOT_READY` | missing local asset |
| `animation_type_error` | `FAIL` | 1 | `NOT_READY` | typecheck |
| `actual_duration_mismatch` | `FAIL` | 1 | `NOT_READY` | actual duration |
| `cue_order_mismatch` | `FAIL` | 1 | `NOT_READY` | order |
| `missing_runtime_evidence` | `BLOCKED` | 2 | `NOT_READY` | runtime |
| `audience_leak` | `FAIL` | 1 | `NOT_READY` | record.html |
| `content_needs_review` | `NEEDS_REVIEW` | 2 | `NOT_READY` | NEEDS_REVIEW |
| `stale_qa` | `BLOCKED` | 2 | `NOT_READY` | stale QA input |

## 4. 限制与完整验证

1. `mini_schema.py` 只实现契约用到的关键字；`format` 被忽略。
2. 完整 Draft 2020-12 验证由项目内 `tools/contract-runtime` 执行：
   `tools/contract-runtime/.venv/Scripts/python.exe tests/contract/validate_with_jsonschema.py`
   （`jsonschema==4.26.0`，17 项检查通过）。
3. 不执行真实 Motion typecheck、Reveal 浏览器、Slidev build、ffprobe 或 OBS。
4. 不接入生产 `check-episode.py`；不修改课程。
5. `stale_qa` 的“输入变化”是通过内存 override 模拟的，不写磁盘。
6. 测试只覆盖契约结构，不覆盖教学设计、事实正确性或视觉质量。
