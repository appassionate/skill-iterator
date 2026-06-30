# summarize.md Template

The summarize.md serves three purposes: (1) retrospective walkthrough of what happened
during training, (2) review of current iteration's todo items and their outcomes, and
(3) structured carryover source for the next iteration's todo.md. The carryover sections
use the same table format as todo.md so items can be directly copied.

**Generation order:** summarize.md is generated **after** the three Phase A validation
artifacts (generalization.md, benchmark.md, automation.md) are complete. This allows the
walkthrough and Validation Generated sections to incorporate findings from the full
validation analysis — producing a more complete and accurate carryover list.

```markdown
# Summarize: iter.XXXX

## Walkthrough Summary
One paragraph overview of how the skill performed against rawdata.

## Friction and Resolution Table

| # | Rawdata Item | Difficulty Encountered | Root Cause | How It Was Resolved |
|---|-------------|----------------------|------------|--------------------|
| 1 | [item]      | [what went wrong]    | [why]      | [workaround used]  |

## Patterns Observed

- **Recurring issues**: [systemic problems across multiple items]
- **Successful patterns**: [what worked well, preserve these]
- **Missed opportunities**: [where the skill could have helped more]

## This Iteration Review

Review of todo.md items targeted in this iteration (items marked `plan` at the start).
Use the same table structure as todo.md:

| # | Status | Content | Added in |
|---|--------|---------|----------|
| U? | done/pending | [item from User Requirements that was worked on] | iter.XXXX |
| V? | done/pending | [item from Validation Generated that was worked on] | iter.XXXX |

## Validation Generated

Items for the next iteration's todo.md. Includes two sources:
(a) unresolved items from this iteration's todo, and
(b) new items the model independently identified during this iteration as areas
    the target skill should improve.

| # | Status | Content | Added in |
|---|--------|---------|----------|
| V1 | pending/plan | [actionable improvement or unresolved item] | iter.XXXX |
| V2 | ... | ... | ... |
```

Each row of the friction table traces a real difficulty to its root cause. The "This
Iteration Review" closes the loop on what was planned. The "Validation Generated" table
distills everything into actionable items for the next round. For deeper analysis of
generalized strategies, see generalization.md. For quantitative assessment, see benchmark.md.
