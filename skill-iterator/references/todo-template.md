# todo.md Template

Each iteration's `todo.md` has up to three sections:

- **start** (REQUIREMENTS) — requirements and original prompt (Stage 1)
- **end** (SOLUTIONS) — walkthrough, friction, and items with status + solution (Stage 4). Each solution item corresponds to a requirements item by # number (1:1).
- **validation** — merged system-generated and user-defined validation items with priority (Stage 4)

Table columns (by section):

| Section | Columns |
|---------|---------|
| start | #, Source, Priority, Content |
| end (items) | #, Status, Solution |
| validation | #, Source, Priority, Content |

Priority values: `high`, `medium`, `low`.
Status values (end section only): `done`, `plan`, `pending`, `deferred`, `dropped`.
Solution values (end section only): one sentence describing how the requirement was fulfilled.
Source values: `user` (from user's request), `system` (auto-generated from validation).

**Priority inheritance:** Start items derive their priority from the corresponding
validation section item that generated them. User-prompt items get priority from
the user's own analysis of importance.

## Section: start

Filled in at Stage 1 (Prepare). Contains the **original prompt** (verbatim user input) as a
description block, plus an **items table** with decomposed, actionable items.

**Prompt block:** The full original user request, preserved verbatim. Marked with
`**Original Prompt:**`.

**Items table:** The prompt is decomposed into small, executable items. Each row includes
a **Priority** column indicating importance. `user` items contain the decomposed task
description. `system` items carry over from previous iterations.

```markdown
# Todo: iter.XXXX

## start

**Original Prompt:**

[Full original user request text, verbatim]

| # | Source | Priority | Content |
|---|--------|----------|---------|
| 1 | user   | high     | [decomposed task from prompt] |
| 2 | system | medium   | [carryover from prior iter] |
```

## Section: end

Filled in at Stage 4 (Summarize). Contains the iteration's walkthrough, friction analysis,
and a unified items table.

```markdown
## end

### Walkthrough Summary

One paragraph overview of how the skill performed against rawdata.

### Friction and Resolution

| # | Rawdata Item | Difficulty Encountered | Root Cause | How It Was Resolved |
|---|-------------|----------------------|------------|--------------------|
| 1 | [item]      | [what went wrong]    | [why]      | [workaround used]  |

### Items

SOLUTIONS table — each row corresponds to a REQUIREMENTS item by # number.
Hover over # to see the full requirement text.

| # | Status | Solution |
|---|--------|----------|
| 1 | done   | [one sentence: how this requirement was fulfilled] |
| 2 | pending | [one sentence or —] |

### Changelog

Summarize `git diff iter.(XXXX-1)..iter.XXXX` from `target_skill/`:

| File | Change | Why |
|------|--------|-----|
| [file path] | [brief description] | [reasoning] |
```

## Section: validation

Single merged section combining system-generated and user-defined validation items.
The Source column values are `system` (auto-generated) or `user` (user-added).
Priority is `high` / `medium` / `low`.

| # | Source | Priority | Content |
|---|--------|----------|---------|
| 1 | system | medium   | [system-generated carryover item] |
| 2 | user   | high     | [user-defined requirement] |

## HTML and JSON Output

After writing or updating todo.md, generate two output files:
`python gen_todo.py --input todo.md --output todo.html`.

| File | Purpose | Contains data? |
|------|---------|---------------|
| `todo.html` | Self-contained HTML with embedded data | Yes — data embedded inline |
| `data_todo.json` | Structured data for tooling | Yes — same data as pure JSON |

The script embeds the JSON data directly into the HTML template
(replacing the `__TODO_DATA__` placeholder).

**Validation buttons:** The validation section header includes three buttons (left to right):
- **Reset** — restores validation items to their original state (as loaded from the initial embedded data).
- **+ Add** — appends a new empty item for user input.
- **Render** — opens a dismissible modal dialog showing all validation items formatted as a concise,
LLM-friendly prompt text with field descriptions (e.g., `[priority: high] [source: system] content`),
sorted by priority. The modal includes a **Copy** button for clipboard export.
Close via the X button, Close button, backdrop click, or Escape key.

## Mixed-Language Iterations

When the user communicates in a non-English language, the prompt block preserves the
original language verbatim. Task table items may appear in the user's language (for `user`
source) or English (for `system` source). This is by design.
