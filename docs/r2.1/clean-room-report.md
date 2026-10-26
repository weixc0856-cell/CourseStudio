# R2.1 Clean-Room Report

```json
{
  "generated_at": "2026-10-26T14:36:20Z",
  "temp_dir": "<temp>",
  "source_head": "e4e744e83b58eee2434d0b056a2e1e7515dd01e2",
  "results": [
    {
      "cmd": "uv sync --frozen",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "",
      "stderr_tail": "Using CPython 3.12.10 interpreter at: <home>"
    },
    {
      "cmd": "<temp>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "jsonschema 4.26.0\nschema meta checks + instance checks: 17\nStatus: PASS",
      "stderr_tail": ""
    },
    {
      "cmd": "cmd /c <home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "dependencies:\n+ @motion-canvas/2d 3.17.2\n+ @motion-canvas/core 3.17.2\n+ @motion-canvas/player 3.17.2\n\ndevDependencies:\n+ @motion-canvas/ui 3.17.2\n+ @motion-canvas/vite-plugin 3.17.2\n+ typescript 5.9.3\n+ vite 5.4.21\n\nDone in 3s using pnpm v10.34.1",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "        \"qa/runtime/screens/slide-6.png\",\n        \"qa/runtime/screens/slide-7.png\",\n        \"qa/runtime/screens/slide-8.png\",\n        \"qa/runtime/screens/slide-9.png\",\n        \"qa/runtime/screens/slide-10.png\",\n        \"qa/runtime/screens/slide-11.png\",\n        \"qa/runtime/screens/slide-12.png\"\n      ],\n      \"notes\": \"Chrome DOM + all 12 page screenshots; console errors not captured by this runner.\"\n    }\n  ]\n}",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "{\n  \"content_status\": \"PASS\",\n  \"checks\": 13,\n  \"leaks\": 0,\n  \"orphan_claims\": [],\n  \"orphan_slides\": [],\n  \"delivery_status\": \"READY\",\n  \"delivery_blockers\": []\n}",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=research\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=script\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nEvidence: runtime=PASS content=PASS recording=NOT_APPLICABLE",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=motion\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nEvidence: runtime=PASS content=PASS recording=NOT_APPLICABLE",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=recording\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nRecording: checked (manifest=OK, checklist=OK, cues_dir=OK, recordings_dir=optional, recordings=0)\nEvidence: runtime=PASS content=PASS recording=NOT_APPLICABLE",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "Episode: transformer-self-attention  mode=course  stage=slides\nStatus:  STRUCTURAL_PASS\nDimensions: STRUCTURAL=PASS RUNTIME=NOT_APPLICABLE CONTENT_QUALITY=NOT_APPLICABLE RECORDING=NOT_APPLICABLE DELIVERY=NOT_READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nEvidence: runtime=PASS content=PASS recording=NOT_APPLICABLE",
      "stderr_tail": ""
    },
    {
      "cmd": "<home>",
      "cwd": "<temp>",
      "exit_code": 0,
      "stdout_tail": "Status:  READY\nDimensions: STRUCTURAL=PASS RUNTIME=PASS CONTENT_QUALITY=PASS RECORDING=NOT_APPLICABLE DELIVERY=READY\nResearch: OK (00-06 present and non-empty)\nSlides:  12 slide(s) [reveal]\nMapping: 12 anchor(s), 12 slide(s), buffer 0 (N >= M allowed)\nSegments: 1 entr(ies), 1 motion\nAnims:   ['scores_to_weights']\nTiming:  1 block(s)\nBuild:   SKIPPED (Reveal deck: build check deferred to Phase 4)\n  - scores_to_weights: engine=motion, scene=OK, project=OK, cue=OK, declared=68.0s, real=NOT_VERIFIED\nRecording: checked (manifest=OK, checklist=OK, cues_dir=OK, recordings_dir=optional, recordings=0)\nEvidence: runtime=PASS content=PASS recording=NOT_APPLICABLE",
      "stderr_tail": ""
    }
  ],
  "evidence": {
    "runtime": {
      "status": "PASS"
    },
    "content": {
      "status": "PASS"
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
      "status": "READY",
      "blocking_reasons": []
    }
  }
}
```
