# R2.1 Clean-Room Report

```json
{
  "generated_at": "2026-10-26T14:01:24Z",
  "temp_dir": "<temp>\r2clean-46284",
  "source_head": "e4e744e83b58eee2434d0b056a2e1e7515dd01e2",
  "results": [
    {
      "cmd": "uv sync --frozen",
      "cwd": "<temp>\r2clean-46284\\tools\\contract-runtime",
      "exit_code": 0,
      "stdout_tail": "",
      "stderr_tail": "Using CPython 3.12.10 interpreter at: <home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe\nCreating virtual environment at: .venv\nInstalled 6 packages in 76ms\n + attrs==26.1.0\n + jsonschema==4.26.0\n + jsonschema-specifications==2025.9.1\n + referencing==0.37.0\n + rpds-py==2026.9.1\n + typing-extensions==4.16.0"
    },
    {
      "cmd": "<temp>\r2clean-46284\\tools\\contract-runtime\\.venv\\Scripts\\python.exe tests/contract/validate_with_jsonschema.py",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "jsonschema 4.26.0\nschema meta checks + instance checks: 17\nStatus: PASS",
      "stderr_tail": "<temp>\r2clean-46284\\tests\\contract\\validate_with_jsonschema.py:105: DeprecationWarning: Accessing jsonschema.__version__ is deprecated and will be removed in a future release. Use importlib.metadata directly to query for jsonschema's version.\n  print(f\"jsonschema {jsonschema.__version__ if hasattr(jsonschema, '__version__') else 'unknown'}\")"
    },
    {
      "cmd": "cmd /c <home>\\AppData\\Roaming\\npm\\pnpm.CMD install --frozen-lockfile",
      "cwd": "<temp>\r2clean-46284\\courses\\transformer-self-attention\\04_motion_src",
      "exit_code": 0,
      "stdout_tail": "dependencies:\n+ @motion-canvas/2d 3.17.2\n+ @motion-canvas/core 3.17.2\n+ @motion-canvas/player 3.17.2\n\ndevDependencies:\n+ @motion-canvas/ui 3.17.2\n+ @motion-canvas/vite-plugin 3.17.2\n+ typescript 5.9.3\n+ vite 5.4.21\n\nDone in 1.3s using pnpm v10.34.1",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/qa_runtime.py transformer-self-attention",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "      \"deck\": \"reveal\",\n      \"status\": \"PASS\",\n      \"slides\": 12,\n      \"screenshots\": [\n        \"qa/runtime/screens/slide-1.png\",\n        \"qa/runtime/screens/slide-6.png\",\n        \"qa/runtime/screens/slide-12.png\"\n      ],\n      \"notes\": \"Chrome DOM + representative screenshots; console errors not captured by this runner.\"\n    }\n  ]\n}",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/qa_content.py transformer-self-attention",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 1,
      "stdout_tail": "{\n  \"content_status\": \"FAIL\",\n  \"checks\": 12,\n  \"leaks\": 2,\n  \"orphan_claims\": [],\n  \"orphan_slides\": [],\n  \"delivery_status\": \"NOT_READY\",\n  \"delivery_blockers\": [\n    \"CONTENT_QUALITY=FAIL: audience deck contains internal recording metadata\"\n  ]\n}",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/check-episode.py transformer-self-attention --mode course --stage research",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=research\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/check-episode.py transformer-self-attention --mode course --stage script",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=script\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/check-episode.py transformer-self-attention --mode course --stage motion",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=motion\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/check-episode.py transformer-self-attention --mode course --stage recording",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=recording\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nRecording: checked (manifest=OK, checklist=OK, cues_dir=OK, recordings_dir=optional, recordings=0)",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/check-episode.py transformer-self-attention --mode course --stage slides",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=slides\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe tools/check-episode.py transformer-self-attention --mode course --stage qa --strict",
      "cwd": "<temp>\r2clean-46284",
      "exit_code": 1,
      "stdout_tail": "Status:  FAIL\nDimensions: STRUCTURAL=PASS RUNTIME=PASS CONTENT_QUALITY=FAIL RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\n  - CONTRACT: content-quality evidence status is FAIL\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\nBuild:   SKIPPED (Reveal deck: build check deferred to Phase 4)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nRecording: checked (manifest=OK, checklist=OK, cues_dir=OK, recordings_dir=optional, recordings=0)",
      "stderr_tail": ""
    }
  ],
  "evidence": {
    "runtime": {
      "status": "PASS"
    },
    "content": {
      "status": "FAIL"
    },
    "trace": {
      "coverage": {
        "claims_mapped": 14,
        "claims_total": 14,
        "slides_mapped": 12,
        "slides_total": 12
      }
    },
    "delivery": {
      "status": "NOT_READY",
      "blocking_reasons": [
        "CONTENT_QUALITY=FAIL: audience deck contains internal recording metadata"
      ]
    }
  }
}
```
