# benchmark.md Template

The benchmark.md tracks the target skill's quantitative and qualitative health across
iterations. It carries forward the Assessment Snapshot and Performance Metrics that were
previously part of changelog.md, giving them a dedicated home for cross-iteration comparison.

```markdown
# Benchmark: iter.XXXX

## Performance Metrics

| Metric                  | Previous      | Current       | Delta  |
|-------------------------|---------------|---------------|--------|
| Rawdata pass rate       | [X/Y or N/A]  | [X/Y]         | [±]    |
| Friction count          | [N or N/A]    | [N]           | [±]    |
| Efficiency (SKILL.md)   | [N] lines     | [N] lines     | [±]    |
| Efficiency (default ctx)| [N] lines     | [N] lines     | [±]    |

## Assessment Snapshot

| Dimension       | Rating    | Key Issue |
|-----------------|-----------|-----------|
| Trigger Coverage| [rating]  | [issue]   |
| Generality      | [rating]  | [issue]   |
| Clarity         | [rating]  | [issue]   |
| Completeness    | [rating]  | [issue]   |
| Efficiency      | [rating]  | [issue]   |
| Why-Depth       | [rating]  | [issue]   |

Ratings: **strong** / **adequate** / **weak** / **missing**.

## Generalization Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| New generalized strategies identified | [N] | From generalization.md |
| Strategies applied in this iteration  | [N] | How many were acted upon |
| Carryover items resolved              | [N/M] | Resolved vs total from previous iter |
| New carryover items generated         | [N] | From Validation Generated section |
```

For iter.0001, mark "Previous" as N/A (baseline). Subsequent iterations compare against
the prior round. The Generalization Metrics section tracks the health of the iteration
pipeline itself — are strategies being generated and applied, or accumulating unused?
