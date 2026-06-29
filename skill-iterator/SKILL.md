---
name: skill-iterator
description: >-
  Iteratively improve an existing skill to make it more generalized, robust, and reusable.
  Triggers via `iter_skill({skill_name})` or when the user says: "iterate skill",
  "improve skill", "optimize skill", "generalize skill", "refactor skill", "harden skill",
  "review skill", "make this skill better/broader/more reliable", "this skill is too rigid",
  "the skill keeps failing", or "look at these eval results and fix the skill".
  中文：迭代技能、改进技能、优化技能、泛化技能、重构技能、加固技能、审查技能。
  Does NOT trigger on "create a skill" or "write a skill" — use skill-creator for those.
  Also triggers when a skill has been tested and needs refinement based on feedback or
  self-assessment, even without the word "iterate".
version: 3.8.0
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

- **Rawdata**: test prompts, sample data, or reference materials to exercise against. If none provided, generate 3-5 synthetic test cases: 2 happy-path, 2 edge cases, 1 error case, covering the skill's domain.
- **Requirements**: explicit improvement goals. If none, default to self-evaluation mode.
- **Iteration count**: default 3, adjustable.

### Step 3: Confirm with the User

Before creating the workspace, confirm: target skill (name + path + file manifest), rawdata
plan, iteration goal, and iteration count.

**Self-reference note:** When iterating on iter_skill itself, copy the skill into `01.train/skill/`
and treat that copy as the target. All changes go into the working copy, never the currently
executing instructions. Self-iteration optimizes the SKILL.md text and reference files only —
do not recursively exercise the training pipeline against itself. The skill tells the model
how to run iterations; iterating on it means improving those instructions, not running the
pipeline on the pipeline.

---

## Workspace Structure

```
iter_skill({target_skill_name})/
├── rawdata/                        # Shared, read-only across all iterations
│   └── (test cases, sample data)
├── iter.0001/
│   ├── todo.md                     # Iteration contract (see references/todo-template.md)
│   ├── summarize.md                # Walkthrough + todo review + carryover (see references/summarize-template.md)
│   ├── changelog.md                # Text modifications with reasoning (see references/changelog-template.md)
│   ├── 01.train/
│   │   ├── skill/                  # Complete copy of target skill for this round
│   │   └── result/                 # Outputs, logs, and friction notes from exercise
│   ├── 02.validation/
│   │   ├── generalization.md       # Problem → solution → generalized strategy (see references/generalization-template.md)
│   │   └── benchmark.md            # Assessment snapshot + performance metrics (see references/benchmark-template.md)
│   └── 03.output/                  # Improved skill — ready to deploy
│       └── (complete skill directory)
├── iter.0002/                      # (same structure, skill/ copied from iter.0001/03.output/)
└── iter.NNNN/
```

### Key Rules

- **rawdata/ is read-only.** Never modify after first iteration. All rounds share the same rawdata for consistent comparison.
- **Chain of custody.** Each iteration's `01.train/skill/` is a complete copy from the previous `03.output/` (or the original skill for iter.0001). This makes each iteration self-contained and traceable.
- **todo.md drives the iteration.** Created first, referenced throughout, verified at the end.
- **Validation drives improvement.** Each iteration produces four reporting artifacts: summarize.md (walkthrough + todo review + carryover), changelog.md (text changes + reasoning), generalization.md (problem → solution → generalized strategy), and benchmark.md (assessment snapshot + performance metrics). summarize.md and changelog.md live at the iteration root (they describe changes relative to prior iterations); generalization.md and benchmark.md live in `02.validation/` (they focus on skill capability). Together they form the next round's agenda. Do not rush this stage — without thorough validation, the next iteration starts blind.
- **03.output/ is the deliverable.** The final iteration's output is the improved skill, ready to install.

---

## The Iteration Pipeline

Each iteration follows: **Prepare → Train → Validate → Output**.

### Stage 1: Prepare (`todo.md`)

Create `todo.md` following `references/todo-template.md`. Two sections, each as a table
with columns: **#** (sequential ID), **Status** (`done` / `plan` / `pending` / `deferred` / `dropped`),
**Content** (abstract description in English), **Added in** (which iteration introduced the item).
Use `plan` for items targeted for improvement in the current iteration.

1. **User Requirements** — explicit goals from the user (or self-evaluation targets for iter.0001 with no specific goal). For iter.0002+, carry forward all prior items and append new ones.
2. **Validation Generated** — carryover items from the previous iteration's summarize.md (both "This Iteration Review" unresolved items and "Validation Generated" entries). Mark "N/A" for iter.0001.

### Stage 2: Train (`01.train/`)

**Seed:** Copy the entire skill from the previous `03.output/` (or original for iter.0001) into `01.train/skill/`.

**Exercise:** Apply the skill against every rawdata item. This means *fully executing* the
target skill's tasks — actually performing every step the skill describes, not just
reading the instructions and assessing them conceptually. If the skill generates reports,
generate them. If it processes files, process them. Record into `01.train/result/`:
- Generated outputs and decision logs
- Failure notes (where the skill was unclear or wrong)
- Friction log (timestamped difficulties: ambiguous instructions, missing edge cases, broken references)
- Workarounds used (how each friction point was resolved in the moment)

When parts of the task are scriptable (data transformation, file manipulation, structured
output), use Python scripts rather than pure reasoning. Persist useful scripts in
`01.train/result/` — this continuous internalization of reusable logic feeds
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

**Assess and Improve:** Run the Assessment Framework (below) informed by the exercise results and todo.md. Apply improvements directly to `01.train/skill/`.

Improvement principles (with their associated pitfalls):

- **Generalize, don't special-case.** When a specific instruction fails, find the broader principle covering both cases. *Pitfall: The Overfitting Trap — adding rules for each failing case creates a skill that passes known inputs but fails on anything new.*
- **Add reasoning before adding rules.** Explain *why* the correct approach matters. Only add explicit rules when reasoning alone doesn't fix the behavior.
- **Preserve what works.** Change what needs changing, leave what doesn't. *Pitfall: The Style Rewrite — rewriting just because you'd phrase it differently, without a functional reason.*
- **Keep examples as examples.** Ground abstract instructions with specifics, but frame them as illustrating patterns, not templates to copy.
- **Prefer progressive disclosure.** Move detailed reference material to separate files loaded on demand. *Pitfall: The Bloat Spiral — each iteration adds edge case handling until the skill is too long to follow carefully. A 200-line skill covering 90% beats a 500-line skill covering 95%.*
- **Right-size the skill.** If during assessment the skill covers 3+ distinct concerns, recommend splitting. If the user insists on iterating rather than splitting, scope the iteration to one concern at a time and note the split recommendation in todo.md for future reference. *Pitfall: The Kitchen Sink — one skill trying to do everything. Recommend splitting into separate skills rather than building a mega-skill.*
- **Stay actionable, not vague.** *Pitfall: The Abstraction Ladder — generalizing too far produces guidance like "handle it appropriately" instead of specific, actionable instructions.*

### Stage 3: Validate (`02.validation/`) — The Most Critical Stage

This stage directly determines the quality of all subsequent iterations. Rushing it produces compounding errors. *Pitfall: Skipping Validation — treating the walkthrough as a formality. The summarize.md is the memory connecting iterations; without it, the next round starts blind and repeats the same mistakes.*

Stage 3 produces four artifacts. Two are **iteration-level reports** at the iteration root — they describe what changed relative to prior iterations. Two are **validation artifacts** in `02.validation/` — they focus on the skill's capability.

**1. Walkthrough (summarize.md, at iteration root):** Re-read every file in `01.train/result/`. Create `summarize.md` following `references/summarize-template.md`. Contains: the friction-and-resolution table, a **This Iteration Review** section (closing the loop on items marked `plan` in todo.md — what was done, what wasn't), and a **Validation Generated** section formatted identically to todo.md. The Validation Generated section includes both unresolved items from this iteration and new items the model independently identified as areas the target skill should improve (marked `plan`). This section is the direct carryover source for the next iteration's todo.md.

**2. Changelog (changelog.md, at iteration root):** Create `changelog.md` following `references/changelog-template.md`. Records **what text was changed and why** — each row identifies the file, section, the change made, and the reasoning behind it. This captures design decisions for traceability across iterations.

**3. Generalization (02.validation/generalization.md):** Create `generalization.md` following `references/generalization-template.md`. For each problem encountered, document: the specific problem, how it was solved, and the **generalized strategy** — the broader principle that applies beyond this specific case. This file is where concrete friction points become reusable knowledge. It informs the next iteration's todo.md decisions alongside summarize.md.

**4. Benchmark (02.validation/benchmark.md):** Create `benchmark.md` following `references/benchmark-template.md`. Tracks the target skill's health across iterations: performance metrics (rawdata pass rate, friction count, line counts), assessment snapshot (6-dimension ratings), and generalization metrics (strategies generated vs applied, carryover resolution rate).

### Stage 4: Output (`03.output/`)

Copy the improved skill from `01.train/skill/` to `03.output/`. Before finalizing, verify:

1. Re-read the full skill — does it hold together coherently?
2. Update the description if capabilities changed.
3. Spot-check against 2+ rawdata items.
4. Check for regressions — did generalization remove constraints important for common cases?
5. Verify all bundled files are present and consistent (no orphaned references).
6. Confirm todo.md completeness — every item done or explicitly deferred.

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

**Default policy:** All output artifacts — workspace reports, validation files, and the
improved SKILL.md — use the same language as the target skill. If the target skill's SKILL.md
is written in Chinese, produce all outputs in Chinese. If English, produce all outputs in
English. This preserves linguistic consistency within the skill being iterated and avoids
introducing a language mismatch between instructions and generated content.

**User override:** The user may explicitly request a different output language (e.g.,
"output in Chinese", "translate SKILL.md to English"). When this happens, produce the
translation as the iteration's output. Preserve all structural elements (sections, tables,
code blocks) — translate the prose, not the architecture. The original-language version
remains the canonical source for future iterations.

**Reasoning language:** When the user communicates in a language different from the
target skill's language, **think in English** during iteration (to preserve reasoning
precision), but **output in the target skill's language** unless overridden.

**Workspace file names** (todo.md, summarize.md, changelog.md, etc.) always remain in
English for cross-iteration consistency.

Do not auto-generate or maintain parallel translated copies of SKILL.md unless the user
explicitly requests one.
