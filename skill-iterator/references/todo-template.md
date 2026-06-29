# todo.md Template

Each iteration's `todo.md` has two table sections. Content is written in **English, abstract
form** — short self-contained descriptions without referencing specific file paths or line
numbers. Status values: `done`, `plan`, `pending`, `deferred`, `dropped`.

- `done` — completed in a prior or current iteration.
- `plan` — targeted for improvement in the current iteration.
- `pending` — not yet addressed, carried from a previous iteration.
- `deferred` — intentionally postponed with a reason.
- `dropped` — no longer relevant.

## Section 1: User Requirements

```markdown
## User Requirements

| # | Status | Content | Added in |
|---|--------|---------|----------|
| U1 | done/plan/pending/deferred/dropped | [abstract description of requirement] | iter.XXXX |
| U2 | ... | ... | ... |
```

For iter.0001, these come from user input. For iter.0002+, carry forward all prior items
(resolved and unresolved) and append new requirements. Items targeted for the current
iteration are marked `plan`.

## Section 2: Validation Generated

```markdown
## Validation Generated (from iter.XXXX-1 summarize)

| # | Status | Content | Added in |
|---|--------|---------|----------|
| V1 | done/plan/pending/deferred/dropped | [abstract description of generated item] | iter.XXXX |
| V2 | ... | ... | ... |
```

For iter.0001, mark the section header "N/A — first iteration" with an empty table. For
iter.0002+, copy the carryover items from the previous iteration's **summarize.md**
(both the "This Iteration Review" and "Validation Generated" sections, which use the same
table structure) and from **generalization.md** (where applicable strategies were identified).
Reference todo.md throughout: during training (stay focused), validation (check each item),
and output (confirm completeness).
