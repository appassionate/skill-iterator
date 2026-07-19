# JSON Schemas

This document defines the JSON schemas used by skill-iterator. All schemas include
`iteration` and `generated_at` for cross-iteration traceability.

---

## iter.json

The structured iteration record — source of truth for each iteration. Located at
`iter.XXXX/iter.json`. Created in Stage 1 (start), updated in Stage 4 (end + validation).

```json
{
  "iteration": "iter.0001",
  "generated_at": "2026-07-19 10:00 UTC",
  "start": {
    "prompt": "Full original user request, verbatim",
    "items": [
      { "id": "1", "source": "user", "priority": "high", "content": "decomposed task" },
      { "id": "2", "source": "system", "priority": "medium", "content": "carryover from prior iter" }
    ]
  },
  "end": null,
  "validation": null
}
```

**Fields:**
- `iteration`: Identifier in `iter.XXXX` format
- `generated_at`: Timestamp (YYYY-MM-DD HH:MM UTC)
- `start.prompt`: User's original request, preserved verbatim
- `start.items[]`: Prompt decomposed into actionable items
  - `id`: Sequential number (string)
  - `source`: `"user"` (from prompt) or `"system"` (carryover from prior iteration's validation)
  - `priority`: `"high"` / `"medium"` / `"low"`
  - `content`: Task description. User items use the user's language; system items use standardized descriptions
- `end`: Null until Stage 4, then populated with solutions
- `validation`: Null until Stage 4, then populated with carryover items

### end section (filled in Stage 4)

```json
{
  "end": {
    "walkthrough": "One paragraph overview of how the skill performed against rawdata.",
    "friction": [
      { "item": "rawdata item id", "difficulty": "medium", "root_cause": "instruction gap", "resolution": "added guidance" }
    ],
    "items": [
      { "id": "1", "content": "original requirement text", "status": "done", "solution": "one sentence recording fulfillment" }
    ],
    "changelog": [
      { "file": "SKILL.md", "change": "Added section X", "why": "Cover gap identified in training" }
    ]
  }
}
```

**Fields:**
- `end.walkthrough`: One paragraph overview of skill performance
- `end.friction[]`: Friction entries with root cause and resolution
  - `item`: Rawdata item identifier
  - `difficulty`: Severity level
  - `root_cause`: What caused the difficulty
  - `resolution`: How it was resolved
- `end.items[]`: SOLUTIONS items, 1:1 mapping with `start.items` by `id`
  - `content`: Original requirement text (used as hover tooltip in HTML)
  - `status`: Item fulfillment status
    - `"done"` — fulfilled during this iteration
    - `"plan"` — planned but not yet implemented
    - `"pending"` — blocked by unresolved dependency
    - `"deferred"` — postponed with reason
    - `"dropped"` — will not do (with justification)
  - `solution`: One sentence recording how the requirement was fulfilled
- `end.changelog[]`: Changes from `git diff iter.(XXXX-1)..iter.XXXX` inside `target_skill/`
  - `file`: File path relative to `target_skill/`
  - `change`: What was changed
  - `why`: Why it was changed

### validation section (filled in Stage 4)

```json
{
  "validation": {
    "items": [
      { "id": "1", "source": "system", "priority": "medium", "content": "verify fix for edge case" }
    ]
  }
}
```

**Fields:**
- `validation.items[]`: Carryover items for the next iteration
  - `source`: `"system"` (auto-generated) or `"user"` (user-added)
  - `priority`: `"high"` (blocks next iteration) / `"medium"` (should address soon) / `"low"` (nice to have)
  - `content`: Item description. System items become carryover source for next iteration's `start.items`

---

## train.json

Friction entries and execution summary from sub-agent training. Located at
`iter.XXXX/01.train/train.json`. Created during Stage 2 Train by the sub-agent.

```json
{
  "iteration": "iter.0001",
  "generated_at": "2026-07-19 10:30 UTC",
  "friction": [
    {
      "id": "1",
      "category": "missing",
      "description": "No guidance for handling empty input files",
      "workaround": "Generated synthetic default content to proceed",
      "affected_items": ["2", "4"]
    },
    {
      "id": "2",
      "category": "environmental",
      "description": "Missing Python dependency (pandas)",
      "workaround": "Installed via pip during execution",
      "affected_items": ["1"]
    }
  ],
  "summary": {
    "item_results": [
      {"name": "sample-report.pdf", "status": "succeeded"},
      {"name": "scanned-image.png", "status": "failed", "failure_reason": "OCR script crashed on scanned format"},
      {"name": "data-export.csv", "status": "succeeded"}
    ],
    "scripts_created": [
      { "name": "validate_input.py", "purpose": "Validate input file format before processing" }
    ],
    "notes": "Overall execution went well. Main friction was missing input validation guidance."
  }
}
```

**Fields:**
- `friction[]`: Categorized friction entries encountered during training
  - `id`: Sequential identifier
  - `category`: Root cause classification
    - `"ambiguous"` — instruction is unclear, multiple interpretations possible
    - `"missing"` — skill lacks guidance for this scenario
    - `"incorrect"` — instruction or script produces wrong results for this case
    - `"environmental"` — external factor (missing deps, data issues, config problems)
    - `"edge_case"` — valid but unusual input the skill doesn't handle gracefully
  - `description`: What went wrong or was difficult
  - `workaround`: How the sub-agent worked around it during execution
  - `affected_items`: IDs of rawdata items affected by this friction
- `summary`: Execution summary
  - `item_results[]`: Per-item execution results
    - `name`: Rawdata item filename
    - `status`: `"succeeded"` or `"failed"`
    - `failure_reason`: (failed items only) Why the item failed
  - `scripts_created[]`: Scripts created during execution in `execute/scripts/`
    - `name`: Script filename
    - `purpose`: What the script does
  - `notes`: Free-form execution summary

---

## validation.json

Merged validation artifact — benchmark, generalization, and automation in one file. Located at
`iter.XXXX/02.validation/validation.json`. Created in Stage 3 Validate.

```json
{
  "iteration": "iter.0001",
  "generated_at": "2026-07-19 12:00 UTC",
  "benchmark": {
    "performance": [
      { "metric": "Rawdata pass rate", "current": "4/5" },
      { "metric": "Friction count", "current": "2" },
      { "metric": "Efficiency (SKILL.md)", "current": "385 lines" },
      { "metric": "Efficiency (default ctx)", "current": "385 lines" }
    ],
    "assessment": [
      { "dimension": "Trigger Coverage", "rating": "strong", "issue": "Good synonym coverage" },
      { "dimension": "Generality", "rating": "adequate", "issue": "Hardcoded assumptions in Stage 2" },
      { "dimension": "Clarity", "rating": "strong", "issue": "Ordered by pipeline stage" },
      { "dimension": "Completeness", "rating": "weak", "issue": "No guidance for empty rawdata" },
      { "dimension": "Efficiency", "rating": "adequate", "issue": "Stage 2/3 overlap" },
      { "dimension": "Why-Depth", "rating": "adequate", "issue": "Meta Principles cover why" }
    ]
  },
  "generalization": {
    "strategies": [
      {
        "problem": "Agent skipped validation when time pressure was high",
        "strategy": "Every stage must produce a verifiable artifact before proceeding",
        "recommendation": "Add gate check to all stage transitions"
      }
    ]
  },
  "automation": {
    "tedium": [
      { "step": "CSV to JSON conversion for each rawdata item", "root_cause": "manual data transform" }
    ],
    "opportunities": [
      { "step": "CSV to JSON conversion", "approach": "Python script: CSV→JSON with type inference", "priority": "high", "status": "done" }
    ],
    "scripts": [
      { "name": "csv_to_json.py", "location": "01.train/execute/scripts/", "purpose": "Convert CSV rawdata to JSON" }
    ]
  }
}
```

**Fields:**

`benchmark`:
- `performance[]`:
  - `metric`: One of `"Rawdata pass rate"`, `"Friction count"`, `"Efficiency (SKILL.md)"`, `"Efficiency (default ctx)"`
  - `current`: Current iteration value
- `assessment[]`: 6-dimension ratings from Stage 2 Evaluate
  - `dimension`: One of `"Trigger Coverage"`, `"Generality"`, `"Clarity"`, `"Completeness"`, `"Efficiency"`, `"Why-Depth"`
  - `rating`: `"strong"` / `"adequate"` / `"weak"` / `"missing"`
  - `issue`: Key issue for this dimension

`generalization`:
- `strategies[]`:
  - `problem`: Specific problem encountered during skill execution
  - `strategy`: Broader principle applicable beyond this case — the key artifact
  - `recommendation`: Actionable item for next iteration, or omit if no action needed

`automation`:
- `tedium[]`:
  - `step`: What was slow or repetitive
  - `root_cause`: Why (boilerplate / manual transform / repeated file ops)
- `opportunities[]`:
  - `step`: Step to automate
  - `approach`: Script description — concrete enough to implement directly
  - `priority`: `"high"` (3+ iters or >5min) / `"medium"` (2 iters or 2-5min) / `"low"` (one-off)
  - `status`: `"planned"` / `"done"` / `"deferred"`
- `scripts[]`:
  - `name`: Script filename
  - `location`: `"01.train/execute/scripts/"` (iteration-local) or `"target_skill/scripts/"` (promoted, ships with skill)
  - `purpose`: What the script automates
