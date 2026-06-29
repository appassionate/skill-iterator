# automation.md Template

The automation.md captures a structured reflection on the tedium and repetition observed
during training, and proposes concrete automation opportunities. It answers three questions:
what was tedious, why, and how to automate it. This file bridges the gap between friction
noted during exercise and reusable scripts that eliminate that friction in future iterations.

```markdown
# Automation: iter.XXXX

## Tedium Analysis

| # | Iteration(s) | Tedious / Repetitive Step | Root Cause of Tedium |
|---|-------------|--------------------------|---------------------|
| 1 | [iter.NNNN] | [what was slow or repetitive] | [boilerplate / manual data transform / repeated file ops / etc.] |

## Automation Opportunities

| # | Step to Automate | Proposed Script / Approach | Priority | Status |
|---|-----------------|---------------------------|----------|--------|
| 1 | [step name] | [Python script description: inputs, outputs, logic] | high/medium/low | planned/done/deferred |

## Scripts Created or Updated

| Script | Location | Purpose | Status |
|--------|----------|---------|--------|
| [filename.py] | 01.train/execute/ or scripts/ | [what it automates] | new/updated/unchanged |

## Notes

[Free-form discussion of automation trade-offs, which scripts were promoted to the skill's
scripts/ directory, and which remain as one-off helpers in execute/.]
```

The "Root Cause of Tedium" column is the key diagnostic — it distinguishes symptoms
("this took 10 minutes") from causes ("I had to manually convert CSV to JSON three times
across iterations"). The "Proposed Script / Approach" column should be concrete enough to
implement directly: name the script, describe its inputs and outputs, and sketch the logic.

Priority guidance: **high** = recurs in 3+ iterations or takes >5 min each time;
**medium** = recurs in 2 iterations or takes 2-5 min; **low** = one-off or trivial.
