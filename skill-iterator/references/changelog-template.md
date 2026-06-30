# changelog.md Template

The changelog.md records **what changed and why**, sourced from the `git diff` of
`target_skill/` for the current iteration branch.

**Source data:** Run `git diff main..iter.XXXX` (or `git log --oneline main..iter.XXXX`
for commit-level summary) inside `target_skill/` to collect the authoritative diff.
The "What Changed" column derives from this diff; the "Why" column is added manually
to capture the reasoning behind each modification.

```markdown
# Changelog: iter.XXXX

## Summary
One paragraph: focus of this iteration and what changed at a high level.

## Text Modifications

| # | File | Section | What Changed | Why |
|---|------|---------|-------------|-----|
| 1 | [filename] | [section name or heading] | [from git diff] | [reason for the change] |

(Omit files with no changes.)

## Git Diff Summary
Paste the key portions of `git diff` output (or a summary of it) here as supporting
evidence. For large diffs, include only the most significant hunks.

## Line Count Summary

| File | Previous | Current | Delta |
|------|----------|---------|-------|
| [filename] | [N] | [N] | [±] |
```

The "Why" column is the most important — it captures the reasoning that led to each change,
making the changelog useful for understanding design decisions across iterations.
