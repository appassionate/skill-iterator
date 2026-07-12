# todo.md Template

Each iteration's `todo.md` has up to four sections:

- **start** — requirements and original prompt (Stage 1)
- **end** — walkthrough, friction, and unified items review (Stage 4)
- **validation - system** — auto-generated validation items with priority (Stage 4)
- **validation - user** — user-added requirements with priority, editable in HTML (Stage 4)

Table columns (by section):

| Section | Columns |
|---------|---------|
| start | #, Source, Priority, Content |
| end (items) | #, Source, Priority, Status, Content |
| validation - system | #, Source, Priority, Content |
| validation - user | #, Priority, Content |

Priority values: `high`, `medium`, `low`.
Status values (end section only): `done`, `plan`, `pending`, `deferred`, `dropped`.
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

Single unified table with both Priority and Status columns:

| # | Source | Priority | Status | Content |
|---|--------|----------|--------|---------|
| 1 | user   | high     | done   | [start item, status updated to final] |
| 2 | system | medium   | pending | [new item discovered during iteration] |
```

## Section: validation - system

Auto-generated validation items discovered during the iteration. Each has a **Priority**
column (`high` / `medium` / `low`). In the HTML viewer, priority is editable via dropdown.

Both validation sections have a **Render** button that opens a dismissible modal dialog
showing all validation items formatted as a concise, LLM-friendly prompt text.

```markdown
## validation - system

| # | Source | Priority | Content |
|---|--------|----------|---------|
| 1 | system | high     | [actionable improvement] |
| 2 | system | medium   | [another improvement] |
```

## Section: validation - user

User-added requirements with editable priority. This section is **interactive in HTML**:
users can add items, edit content and priority inline, and delete items.

```markdown
## validation - user

| # | Priority | Content |
|---|----------|---------|
| 1 | high     | [user-defined requirement] |
```

## HTML and JSON Output

After writing or updating todo.md, generate two output files:
`python generate_todo_html.py --input todo.md --output todo.html`.

| File | Purpose | Contains data? |
|------|---------|---------------|
| `todo.html` | Self-contained HTML with embedded data | Yes — data embedded inline |
| `data_todo.json` | Structured data for tooling | Yes — same data as pure JSON |

The script embeds the JSON data directly into the HTML template
(replacing the `__TODO_DATA__` placeholder).

**Render feature:** Both validation sections have a **Render** button. Clicking it opens
a dismissible modal dialog (Tailwind styled) showing all validation items (system + user)
formatted as a concise, LLM-friendly prompt text, sorted by priority. The modal includes
a **Copy** button for clipboard export. Close via the X button, Close button, backdrop click,
or Escape key.

## Mixed-Language Iterations

When the user communicates in a non-English language, the prompt block preserves the
original language verbatim. Task table items may appear in the user's language (for `user`
source) or English (for `system` source). This is by design.
