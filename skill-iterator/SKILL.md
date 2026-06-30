---
name: skill-iterator
description: "Iteratively improve an existing skill to make it more generalized, robust, and reusable. Triggers via `iter_skill({skill_name})` or when the user says: \"iterate skill\", \"improve skill\", \"optimize skill\", \"generalize skill\", \"refactor skill\", \"harden skill\", \"review skill\", \"make this skill better/broader/more reliable\", \"this skill is too rigid\", \"the skill keeps failing\", or \"look at these eval results and fix the skill\". 中文：迭代技能、改进技能、优化技能、泛化技能、重构技能、加固技能、审查技能。 Does NOT trigger on \"create a skill\" or \"write a skill\" — use skill-creator for those. Also triggers when a skill has been tested and needs refinement based on feedback or self-assessment, even without the word \"iterate\"."
version: 4.0.0
install_method: upload
---

# skill-iterator

A meta-skill for iteratively improving existing skills through a structured training
pipeline. A skill's value is measured by how well it generalizes beyond the examples it was
built from. Every iteration should push toward broader applicability with fewer assumptions
— without losing the specificity that makes it effective.

## Guiding Principle

Skills start narrow. This skill breaks that narrowness incrementally. Generalization means
finding the right abstraction level — not removing detail, but teaching the model *how to
think* about a problem rather than *what to do* for a specific instance. When you find
yourself writing "always do X when Y", ask whether explaining *why* X matters would let
the model figure out the right move even when Y doesn't quite match.

---

## Target Skill Definition

A **target skill** is the entire skill directory at `{agent_skills_parent_dir}/{target_skill_name}/`,
not just SKILL.md. It includes SKILL.md, `references/`, `scripts/`, `assets/`, and any other
bundled files. When copying or modifying a skill, always treat the complete directory as the
unit of work — a skill is more than its instruction file.

---

## Trigger and Confirmation

### Invocation

Triggered by `iter_skill({target_skill_name})` or any natural-language request to improve,
optimize, generalize, refactor, harden, or review an existing skill (in English or Chinese).

### Step 1: Locate the Target Skill

1. Check `{agent_skills_parent_dir}/{target_skill_name}/`
2. If not found, search workspace and project directories using Glob with `**/{target_skill_name}/SKILL.md`
3. If still not found, **stop and ask the user** for the path. Offer: (a) similar skills found nearby, (b) the option to create this skill first.

**Pre-flight check** before proceeding: verify the directory contains SKILL.md. If the skill
is extremely large (>500 lines), flag the Kitchen Sink risk (see Pitfalls below) and ask
the user whether to iterate the whole skill or scope to one concern. If the skill appears
to be a stub (<20 lines with no substance), note that there may be little to iterate on.

Once located, read every file in the skill directory — SKILL.md plus all bundled content.

### Step 2: Parse User Input

- **Rawdata** (input archive): `rawdata/` is the comprehensive archive of **all input files** for the iteration — test prompts, sample data, and every file the user uploads or that participates in exercise execution. Collect all files at workspace setup; completeness ensures every iteration is fully reproducible. Missing inputs make it impossible to verify earlier results or build on them in later rounds. **Archive files that participate in `execute/` execution even if `target_skill/` does not directly reference them** — configuration files, helper data, lookup tables, sample datasets, or reference documents that inform how exercises run. These indirect inputs are often invisible to the skill's instructions but critical to reproducing the exercise and are the most commonly overlooked archive candidates. The directory is shared read-only across iterations for consistent comparison. If no files are provided, generate 3-5 synthetic test cases: 2 happy-path, 2 edge cases, 1 error case, covering the skill's domain.
- **Requirements**: explicit improvement goals. If none, default to self-evaluation mode.
- **Iteration count**: default 3, adjustable.

### Step 3: Confirm with the User

Before creating the workspace, confirm: target skill (name + path + file manifest), rawdata
plan, iteration goal, and iteration count.

**Self-reference note:** When iterating on iter_skill itself, `target_skill/` at the workspace root is the working copy. All changes go into `target_skill/`, never the currently executing instructions at `{SKILLS_LOCATION}/skills/skill-iterator/`. Self-iteration optimizes the SKILL.md text and reference files only — do not recursively exercise the training pipeline against itself. The skill tells the model how to run iterations; iterating on it means improving those instructions, not running the pipeline on the pipeline.

---

## Workspace Structure

```
iter_skill({target_skill_name})/
├── rawdata/                        # Input archive — all files that participate in iteration
│   └── (test cases, sample data, config files)
├── target_skill/                   # Complete target skill — the single working copy (git-managed)
│   ├── .git/                       # Git repository — one branch per iteration (iter.XXXX)
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── iter.0001/
│   ├── todo.md                     # Iteration contract (see references/todo-template.md)
│   ├── 01.train/
│   │   └── execute/                # Target skill's execution workspace — outputs, logs, and friction notes
│   ├── 02.validation/
│   │   ├── generalization.md       # Problem → solution → generalized strategy
│   │   ├── benchmark.md            # Assessment snapshot + performance metrics
│   │   └── automation.md           # Tedium analysis + automation opportunities
│   └── 03.summarize/
│       ├── summarize.md            # Walkthrough + todo review + carryover (see references/summarize-template.md)
│       └── changelog.md            # Git diff summary + reasoning (see references/changelog-template.md)
├── iter.0002/                      # (same structure; target_skill/ persists across iterations)
├── iter.NNNN/
└── {target_skill_name}.zip         # Latest packaged snapshot of target_skill/ (excludes .git/)
```

### Key Rules

- **target_skill/ is the single working copy.** Created once at workspace setup with the full target skill content (SKILL.md + all bundled files), it lives at the workspace root and persists across all iterations. Every iteration reads from and writes improvements to this same directory. There is no per-iteration skill copy.
- **Git tracks every iteration.** `target_skill/` is a git repository. Each iteration creates a branch named `iter.XXXX` (matching the iteration directory name). All improvements are committed on that branch. When starting an iteration, create the branch from the current HEAD; if a branch with the same name already exists, delete it first (`git branch -D iter.XXXX`). This provides full history, diff, and rollback capability across iterations.
- **rawdata/ is the input archive.** Collect all user-uploaded files, test prompts, and reference materials at workspace setup. `rawdata/` archives every file that participates in the iteration — not just files the target skill directly references, but also those consumed during `execute/` (configuration files, helper data, lookup tables, sample datasets). These indirect inputs are the most commonly overlooked archive candidates. Completeness ensures any iteration can be fully reproduced. The directory is shared read-only across all rounds to ensure consistent comparison.
- **todo.md drives the iteration.** Created first, referenced throughout, verified at the end.
- **Validation produces three artifacts in `02.validation/`.** generalization.md captures what was learned, benchmark.md captures how well the skill performs, and automation.md captures what should be mechanized. These artifacts feed Stage 4 (Summarize) — do not skip or rush validation, because the summarize step depends on their analysis.
- **`execute/` is the target skill's execution workspace.** It is where the target skill *actively performs its tasks* — generating outputs, running scripts, encountering friction. Self-correction artifacts produced during exercise (workarounds, improved scripts, refined logic) may originate in `execute/` but should ultimately be considered for promotion to `target_skill/` as optimizations to the skill itself. When reviewing `execute/` during validation, look for process artifacts (logs, intermediate states, workarounds) not just final outputs.
- **Script the scaffolding.** The workspace setup pattern (create directories, initialize target_skill/ with git, verify line counts) repeats identically in every iteration. When running 3+ iterations, create a Python script (e.g., `setup_iter.py`) in `01.train/execute/` to automate it. This eliminates the single most repetitive step in the pipeline and prevents drift between iterations.
- **Scripts must track SKILL.md in the same iteration.** When structural changes are made to the workspace model (directory layout, file paths, git workflow), audit all bundled scripts in `target_skill/scripts/` during the same iteration. Scripts that implement the old architecture while SKILL.md describes the new one create a silent alignment gap — the documentation says one thing, the automation does another. Promote updated scripts to `target_skill/scripts/` alongside the SKILL.md changes they implement.
- **Package after each iteration.** At the end of Stage 5 (Finalize), create a zip archive: `zip -r {target_skill_name}.zip target_skill/ -x "target_skill/.git/*"`. Store at the workspace root. The zip always reflects the latest iteration — same filename, overwritten each round. This provides a portable snapshot for installation or distribution without requiring git access.

---

## The Iteration Pipeline

Each iteration follows: **Prepare → Train → Validate → Summarize → Finalize**.

### Stage 1: Prepare (`todo.md`)

Create `todo.md` following `references/todo-template.md`. Two sections, each as a table
with columns: **#** (sequential ID), **Status** (`done` / `plan` / `pending` / `deferred` / `dropped`),
**Content** (see sourcing rules below), **Added in** (which iteration introduced the item).
Use `plan` for items targeted for improvement in the current iteration.

1. **User Requirements** — quote the user's original input text verbatim (preserve their language, phrasing, and wording). If the user wrote in Chinese, the Content column contains Chinese; if English, English. For iter.0002+, carry forward all prior items and append new ones.
2. **Validation Generated** — carryover items from the previous iteration's summarize.md (both "This Iteration Review" unresolved items and "Validation Generated" entries). These use formatted, standardized descriptions (not raw quotes) since they represent distilled, cross-iteration knowledge. Mark "N/A" for iter.0001.

### Stage 2: Train (`01.train/`)

**Seed:** `target_skill/` is already at the workspace root — no copying needed. Create the iteration's git branch: `git checkout -b iter.XXXX` (delete first with `git branch -D iter.XXXX` if it already exists). All subsequent improvements to `target_skill/` are committed on this branch.

**Exercise:** Apply the skill against every rawdata item. This means *fully executing* the
target skill's tasks — actually performing every step the skill describes, not just
reading the instructions and assessing them conceptually. If the skill generates reports,
generate them. If it processes files, process them. Record into `execute/` (inside the current iteration's `01.train/`):
- Generated outputs and decision logs
- Failure notes (where the skill was unclear or wrong)
- Friction log (timestamped difficulties: ambiguous instructions, missing edge cases, broken references)
- Workarounds used (how each friction point was resolved in the moment)

When parts of the task are scriptable (data transformation, file manipulation, structured
output), use Python scripts rather than pure reasoning. Persist useful scripts in
`execute/` — this continuous internalization of reusable logic feeds
generalization.md with concrete, verifiable patterns rather than abstract assessments.

**Execution methodology for new tasks and scenarios:**

1. **Simplicity first.** Solve the current problem with the simplest approach that works.
   Do not add complexity, abstractions, or edge-case handling until a real failure demands
   it. *Entities should not be multiplied beyond necessity* — if a three-line script solves
   it, don't build a framework.
2. **Prefer scripts over reasoning.** When the task involves data processing, file I/O, or
   structured output, write a script. A script produces deterministic, verifiable output;
   reasoning about the same task risks subtle hallucination (plausible but wrong results
   that look correct). Scripts ground the exercise in reality.
3. **Automate repetitive steps across iterations.** If a step is performed identically in
   two or more iterations (e.g., data preprocessing, file format conversion, workspace setup,
   validation checks), extract it into a reusable Python script and persist it in
   `execute/`. Subsequent iterations should invoke the script rather than redo the
   work manually. This reduces friction, eliminates drift between iterations, and produces
   concrete artifacts that feed generalization.md. When in doubt, prefer Python — it has the
   broadest ecosystem for the data-processing and file-manipulation tasks typical in skill
   exercise.

**Assess and Improve:** This is a three-step checkpoint within Stage 2 — exercise first,
evaluate second, promote third. All three must complete before moving to Stage 3 (Validate).

1. **Exercise:** Run the target skill against every rawdata item. Record all outputs, friction logs, failure notes, and workarounds into `execute/`.
2. **Evaluate:** Re-read everything in `execute/` — generated outputs, friction logs, failure notes, workarounds, and persisted scripts. Assess the exercise results against the Assessment Framework (below) and todo.md items, scoring each of the six dimensions. Identify which friction points trace to skill instructions (gaps, ambiguities, wrong assumptions) versus environmental factors (missing dependencies, data issues). This evaluation is the bridge between raw exercise data and actionable improvements.
3. **Promote to target_skill/:** Apply improvements directly to `target_skill/` based on the evaluation findings. Each change should trace back to a specific observation from execute/ — if you cannot point to the evidence that motivated a change, reconsider whether it is needed. Commit the improvements on the current iteration branch.

Improvement principles (with their associated pitfalls):

- **Generalize, don't special-case.** When a specific instruction fails, find the broader principle covering both cases. *Pitfall: The Overfitting Trap — adding rules for each failing case creates a skill that passes known inputs but fails on anything new.*
- **Add reasoning before adding rules.** Explain *why* the correct approach matters. Only add explicit rules when reasoning alone doesn't fix the behavior.
- **Preserve what works.** Change what needs changing, leave what doesn't. *Pitfall: The Style Rewrite — rewriting just because you'd phrase it differently, without a functional reason.*
- **Keep examples as examples.** Ground abstract instructions with specifics, but frame them as illustrating patterns, not templates to copy.
- **Prefer progressive disclosure.** Move detailed reference material to separate files loaded on demand. *Pitfall: The Bloat Spiral — each iteration adds edge case handling until the skill is too long to follow carefully. A 200-line skill covering 90% beats a 500-line skill covering 95%.*
- **Right-size the skill.** If during assessment the skill covers 3+ distinct concerns, recommend splitting. If the user insists on iterating rather than splitting, scope the iteration to one concern at a time and note the split recommendation in todo.md for future reference. *Pitfall: The Kitchen Sink — one skill trying to do everything. Recommend splitting into separate skills rather than building a mega-skill.*
- **Stay actionable, not vague.** *Pitfall: The Abstraction Ladder — generalizing too far produces guidance like "handle it appropriately" instead of specific, actionable instructions.*

### Stage 3: Validate (`02.validation/`) — The Most Critical Stage

This stage directly determines the quality of all subsequent stages. Rushing it produces compounding errors. *Pitfall: Skipping Validation — treating it as a formality. Without thorough validation, the Summarize stage has nothing meaningful to synthesize.*

**Core principle: make implicit workflow steps explicit.** During training, the model often relies on assumptions — unstated steps, implicit data formats, or reasoning shortcuts that worked but were never documented. Validation is where those hidden dependencies must surface.

Stage 3 produces three artifacts in `02.validation/`:

**1. Generalization (02.validation/generalization.md):** Create `generalization.md` following `references/generalization-template.md`. For each problem encountered, document: the specific problem, how it was solved, and the **generalized strategy** — the broader principle that applies beyond this specific case. This file is where concrete friction points become reusable knowledge.

**2. Benchmark (02.validation/benchmark.md):** Create `benchmark.md` following `references/benchmark-template.md`. Tracks the target skill's health across iterations: performance metrics (rawdata pass rate, friction count, line counts), assessment snapshot (6-dimension ratings), and generalization metrics (strategies generated vs applied, carryover resolution rate).

**3. Automation (02.validation/automation.md):** Create `automation.md` following `references/automation-template.md`. Review **all** iterations' `execute/` directories — not just the current one — and reflect on three questions: (1) Which steps were tedious or repetitive? (2) What made them tedious? (3) How could a Python script automate them? Prioritize automating steps that recur across iterations. Automation candidates should be promoted into `target_skill/scripts/` when they prove stable.

### Stage 4: Summarize (`03.summarize/`)

This stage synthesizes the validation results into cross-iteration records. It depends on Stage 3 being complete — summarize.md and changelog.md are summaries of the validation analysis.

**1. Walkthrough (03.summarize/summarize.md):** Re-read every file in `execute/` **and all validation artifacts**. Create `summarize.md` following `references/summarize-template.md`. Contains: the friction-and-resolution table, a **This Iteration Review** section (closing the loop for items marked `plan` in todo.md), and a **Validation Generated** section formatted identically to todo.md. The Validation Generated section is the direct carryover source for the next iteration's todo.md.

**2. Changelog (03.summarize/changelog.md):** Create `changelog.md` following `references/changelog-template.md`. Collects the `git diff` output from `target_skill/` for the current iteration branch, then adds a **Why** column explaining the reasoning behind each change. The git diff provides an authoritative, complete record of what changed; the "Why" column captures the design decisions for traceability. Run: `git diff main..iter.XXXX` (or `git log --oneline main..iter.XXXX` for commit-level summary) inside `target_skill/` to gather the diff data.

### Stage 5: Finalize

The improved skill is already in `target_skill/` from Stage 2 — there is no separate output copy. Before finalizing, verify:

1. Re-read the full skill — does it hold together coherently?
2. Update the description if capabilities changed.
3. Spot-check against 2+ rawdata items.
4. Check for regressions — did generalization remove constraints important for common cases?
5. Verify all bundled files are present and consistent (no orphaned references).
6. Confirm todo.md completeness — every item done or explicitly deferred.
7. Commit the final state on the iteration branch (`git add -A && git commit`).
8. **Package target_skill/** as a zip archive: `zip -r {target_skill_name}.zip target_skill/ -x "target_skill/.git/*"`. Store at the workspace root. The filename is always `{target_skill_name}.zip` — same name each iteration, always reflecting the latest version.

**Alternate outcomes:** If the assessment concluded the skill should be split rather than iterated, the output is a decomposition plan (identifying split boundaries and proposed new skills) instead of an improved single skill.

---

## Assessment Framework

Score each dimension as **strong / adequate / weak / missing**, then focus improvement on the weakest first.

### 1. Trigger Coverage (Description)

Does the description cover the full range of user intents, including common synonyms and near-miss scenarios? Is it specific enough to avoid false triggers? Common failure: listing what the skill *is* rather than what the user might *say*.

### 2. Generality (Instructions)

Are instructions principle-based rather than example-based? Are there hardcoded assumptions limiting applicability? Common failure: instructions that read like a tutorial for one case rather than a guide for a class of problems.

### 3. Clarity (Structure)

Is information ordered so the model encounters it when needed? Are mandatory vs. aspirational instructions distinguishable? Common failure: critical constraints buried in the middle of long paragraphs.

### 4. Completeness (Edge Cases)

What happens with empty, malformed, or ambiguous input? Trivially simple or extremely complex tasks? Missing prerequisites? Common failure: perfect for "normal" inputs, no guidance for degenerate cases.

### 5. Efficiency (Token Budget)

Are there redundant sections? Content the model could infer? Reference material that could be loaded on-demand? Common failure: skills that try to be self-contained encyclopedias instead of focused guides.

### 6. Why-Depth (Reasoning)

Do major instructions explain *why* they matter? Could the model derive correct behavior for novel scenarios from the principles given? Common failure: "always do X" and "never do Y" with no reasoning.

---

## Two Modes of Operation

**User-Driven Mode:** The user provides explicit feedback ("fails when...", "should also handle...", "output was wrong because..."). Trace the complaint to root cause in the skill's instructions, fix the root cause to handle the entire class of similar inputs, and verify the fix doesn't break what already works.

**Self-Evaluation Mode:** No explicit complaint. Run through the Assessment Framework, identify highest-impact issues, address them. Prioritize silent failures (plausible but wrong output) over loud failures (model asks for clarification).

---

## Iteration Cadence and Stopping

A good rhythm: iter.0001 fixes obvious gaps (highest ROI), iter.0002-0003 runs deep exercises and addresses structural issues, iter.0004+ polishes and trims. Don't iterate for the sake of it — if all dimensions are adequate or strong and summarize.md reports no remaining friction, say so and stop. A shipped skill is worth more than a perfect one still being tweaked.

**Proportionality:** For trivially simple skills (<50 lines), consider a lighter process — skip the full workspace ceremony and do a focused assessment + improvement pass. For extremely complex skills (>500 lines), scope the iteration to one concern at a time or address the Kitchen Sink risk first.

---

## Localization

**Think in English, output in the target skill's language.** During iteration, always reason and think in English to preserve analytical precision — unless the user explicitly requests otherwise. All output artifacts (validation reports, summarize.md, changelog.md, and the improved SKILL.md) use the same language as the target skill's SKILL.md. This applies to both the skill content itself and all iteration-generated content. The user may override the output language by explicitly requesting a different one. Workspace file names (todo.md, summarize.md, etc.) always remain in English for cross-iteration consistency.
