# todo.md Template

Each iteration's `todo.md` has two table sections. Content sourcing differs by section:
**User Requirements** preserves the user's original input text verbatim (their language,
phrasing, and wording); **Validation Generated** uses formatted, standardized descriptions
in English. Both sections share the same table structure. Status values: `done`, `plan`,
`pending`, `deferred`, `dropped`.

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
| U1 | done/plan/pending/deferred/dropped | [user's original input text, verbatim] | iter.XXXX |
| U2 | ... | ... | ... |
```

Quote the user's original input text in the Content column — preserve their exact language,
phrasing, and wording. If the user wrote in Chinese, keep Chinese; if English, keep English.
Do not paraphrase, abstract, or translate. For iter.0001, these come directly from the user's
invocation prompt. For iter.0002+, carry forward all prior items (resolved and unresolved)
and append new requirements. Items targeted for the current iteration are marked `plan`.

## Section 2: Validation Generated

```markdown
## Validation Generated (from iter.XXXX-1 summarize)

| # | Status | Content | Added in |
|---|--------|---------|----------|
| V1 | done/plan/pending/deferred/dropped | [formatted, standardized description] | iter.XXXX |
| V2 | ... | ... | ... |
```

Unlike User Requirements, Validation Generated items use **formatted descriptions** —
standardized English phrasing that distills the original observation into an actionable,
cross-iteration reference. This distinction matters: user requirements preserve intent
through exact wording; validation items are the model's own distilled findings, and
standardized formatting makes them easier to track, merge, and resolve across iterations.

For iter.0001, mark the section header "N/A — first iteration" with an empty table. For
iter.0002+, copy the carryover items from the previous iteration's **summarize.md**
(both the "This Iteration Review" and "Validation Generated" sections, which use the same
table structure) and from **generalization.md** (where applicable strategies were identified).
Reference todo.md throughout: during training (stay focused), validation (check each item),
and output (confirm completeness).

## Mixed-Language Iterations

When the user communicates in a non-English language, the two sections naturally diverge:
User Requirements appears in the user's language, Validation Generated in English. This is
by design, not an inconsistency to fix. The divergence reflects the provenance distinction —
each section preserves the voice of its source.
