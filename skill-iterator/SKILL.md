---
name: skill-iterator
description: "Iteratively improve an existing skill to make it more generalized, robust, and reusable. Triggers via `iter_skill({skill_name})` or when the user says: \"iterate skill\", \"improve skill\", \"optimize skill\", \"generalize skill\", \"refactor skill\", \"harden skill\", \"review skill\", \"make this skill better/broader/more reliable\", \"this skill is too rigid\", \"the skill keeps failing\", or \"look at these eval results and fix the skill\". 中文：迭代技能、改进技能、优化技能、泛化技能、重构技能、加固技能、审查技能。 Does NOT trigger on \"create a skill\" or \"write a skill\" — use skill-creator for those. Also triggers when a skill has been tested and needs refinement based on feedback or self-assessment, even without the word \"iterate\"."
---

# skill-iterator

A meta-skill for iteratively improving existing skills through a structured training
pipeline. A skill's value is measured by how well it generalizes beyond the examples it was
built from. Every iteration should push toward broader applicability with fewer assumptions
— without losing the specificity that makes it effective.

## Meta Principles

Five principles govern skill iteration. Every stage, improvement decision, and assessment
dimension traces back to one or more of these.

- **Simplicity.** Use the simplest approach that works. Do not add complexity, abstractions,
  or edge-case handling until a real failure demands it — if a three-line solution works,
  don't build a framework. Every added line is a line the model must follow, and complexity
  rarely gets removed once added.
- **Mechanize.** Any procedure executed more than once should exist as a script, tool, or
  template — not as text instructions re-executed from scratch each time. Text-based
  procedures produce subtle drift on every re-run and waste tokens on re-interpretation.
  Once encoded, execution is deterministic, cheap, and reusable across iterations.
- **Generalize.** When you find yourself writing "always do X when Y", ask whether explaining
  *why* X matters covers both this case and unseen ones. Adding a rule for each failing case
  produces a skill that passes known inputs but fails on anything new — find the broader
  principle instead.
- **Abstract.** Explain *why* the correct approach matters rather than *what to do* for a
  specific instance — but stay grounded. If your explanation could be summarized as "handle
  it appropriately", you have gone too far; the right abstraction level teaches the model
  *how to think* about a problem class, not to punt on the decision.
- **Right-Size.** Cover one concern well per skill. When a skill covers 3+ distinct concerns,
  recommend splitting into separate skills. A 200-line skill covering 90% beats a 500-line
  skill covering 95% — long skills are not followed carefully, they are skimmed.

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
is extremely large (>500 lines), flag the Right-Size risk (see Meta Principles) and ask
the user whether to iterate the whole skill or scope to one concern. If the skill appears
to be a stub (<20 lines with no substance), note that there may be little to iterate on.

Once located, read every file in the skill directory — SKILL.md plus all bundled content.

### Step 2: Parse User Input

- **Rawdata** (input archive): `rawdata/` is the comprehensive archive of **all input files**
  for the iteration — test prompts, sample data, and every file the user uploads or that
  participates in training execution. Collect all files at workspace setup; completeness
  ensures every iteration is fully reproducible. The directory is shared read-only across
  iterations for consistent comparison.
  - **Indirect inputs:** Archive files that participate in `execute/` execution even if
    `target_skill/` does not directly reference them — configuration files, helper data,
    lookup tables, sample datasets, or reference documents that inform how training runs.
    These are the most commonly overlooked archive candidates.
  - **No files provided:** Generate 3-5 synthetic test cases: 2 happy-path, 2 edge cases,
    1 error case, covering the skill's domain.
- **Requirements**: explicit improvement goals. If none, default to self-evaluation mode.
- **Iteration count**: default 3, adjustable.

### Step 3: Confirm with the User

Before creating the workspace, confirm: target skill (name + path + file manifest), rawdata
plan, iteration goal, and iteration count.

### Step 4: Create or Locate the Workspace

**Initial iteration (iter.0001):**  This directory is the main workspace — it will contain
`rawdata/`, `target_skill/`, iteration directories, and the final zip.

**Continuing iteration (iter.0002+):** The user must specify the path to the existing
`iter_skill({target_skill_name})/` workspace. If the path is not provided, search for it
using `Glob("**/iter_skill({target_skill_name})/SKILL.md")` and confirm with the user.
Never create a new workspace for a continuing iteration — always resume in the existing one
so that `target_skill/` (with its git history) and prior `iter.XXXX/` directories are
preserved.

**Self-reference note:** When iterating on iter_skill itself (`iter_skill(skill-iterator)`),
`target_skill/` at the workspace root is the working copy. All changes go into `target_skill/`,
never the currently executing instructions at `{agent_skills_parent_dir}/skill-iterator/`.
Self-iteration optimizes the SKILL.md text and reference files only — **skip the 01.train
sub-agent execution entirely** (do not spawn an executor sub-agent to run the training
pipeline against itself — this would cause infinite recursion). The orchestrator performs
Stage 2 directly: the user's requirements ARE the rawdata, and the changes to SKILL.md,
templates, and scripts ARE the training outputs. Proceed straight to Evaluate → Promote.

---

## Workspace Structure

```
iter_skill({target_skill_name})/    # Always create a new workspace directory named as mentioned, or continue from user specified
├── rawdata/                        # Input archive — all files that participate in iteration
│   └── (test cases, sample data, config files)
├── target_skill/                   # Complete target skill — the single working copy (git-managed)
│   ├── .git/                       # Git repository — one branch per iteration (iter.XXXX)
│   ├── SKILL.md                    # continuous developing: target_skill SKILL.md
│   ├── assets/                     # continuous developing: target_skill Static HTML templates 
│   ├── references/                 # continuous developing: target_skill reference markdown content
│   └── scripts/                    # continuous developing: scripts used by target_skill
├── iter.0001/
│   ├── iter.json                   # Structured JSON iteration record (source of truth)
│   ├── iter.html                   # Self-contained HTML viewer with embedded data
│   ├── 01.train/
│   │   ├── execute/              # Target skill's working directory — ALL outputs from running the skill go here
│   │   │   ├── scripts/          # Reusable scripts created during execution
│   │   │   └── (all deliverables produced by target skill)
│   │   ├── train.json            # Friction entries + execution summary (merged)
│   │   └── train.html            # Self-contained HTML viewer with embedded data (auto-generated from train.json)
│   └── 02.validation/
│       ├── validation.json         # Merged validation data: benchmark + generalization + automation
│       └── validation.html         # Self-contained HTML viewer with sidebar nav (auto-generated from JSON)
├── iter.0002/                      # (same structure; target_skill/ persists across iterations)
├── iter.NNNN/
├── overview.html                   # Iteration overview with sidebar nav and summary table (auto-generated)
└── {target_skill_name}.zip         # Latest packaged snapshot of target_skill/ (excludes .git/)
```

### Key Procedure Rules

- **target_skill/ — single working copy.** Entire skill directory, persists across all iterations. *(See Stage 2: Seed)*
- **Git — one branch per iteration.** `iter.XXXX` branches track each iteration's changes. *(See Stage 2: Seed)*
- **rawdata/ — complete input archive, read-only.** *(See Step 2: Parse User Input)*
- **iter.json — drives the iteration.** Created first, referenced throughout, verified at the end. *(See Stage 1)*
- **01.train/ — training workspace.** `execute/` holds deliverables; `train.json` holds friction + summary; `train.html` renders them. *(See Stage 2)*
- **02.validation/ — merged validation artifact.** `validation.json` holds benchmark + generalization + automation; `validation.html` renders them with sidebar nav. Do not skip or rush — Stage 4 depends on this analysis. *(See Stage 3)*
- **Package after each iteration.** Run `zip -r {name}.zip target_skill/ -x 'target_skill/.git/*'` at Stage 5 to keep zip current. *(See Stage 5)*

---

## Localization

**Think in English, output in the target skill's language.** During iteration, always reason
and think in English to preserve analytical precision — unless the user explicitly requests
otherwise. All output artifacts (validation reports, iter.json, and the
improved SKILL.md) use the same language as the target skill's SKILL.md. This applies to
both the skill content itself and all iteration-generated content. The user may override the
output language by explicitly requesting a different one. Workspace file names (iter.json,
iter.html, etc.) always remain in English for cross-iteration consistency.

---

## The Iteration Pipeline

Each iteration follows: **Prepare → Train → Validate → Summarize → Finalize**.

### Stage 1: Prepare (`iter.json`)

Create `iter.json` — the structured iteration record.
Schema: `references/schemas.md` (iter.json section).

**`start.prompt`** — the user's original request, preserved verbatim.

**`start.items`** — the prompt decomposed into small, actionable items. The original prompt text does NOT appear in items.

**Priority inheritance:** Items carried over from prior iterations inherit the priority from the previous `validation` section. User-prompt items get priority based on the user's analysis.

**Content sourcing by source type:**
- `user` — decomposed, actionable task descriptions derived from the user's original prompt. If the user wrote in Chinese, content is in Chinese.
- `system` — carryover items from the previous iteration's `validation` section. Use formatted, standardized descriptions. Empty array `[]` for iter.0001.

**HTML output:** After writing `iter.json`, generate the HTML viewer:
`python show_iter.py --input iter.json --output iter.html`.
Each `iter.html` is fully self-contained with embedded data.

**Carryover management:** To prevent unbounded growth across iterations:
- Each iteration should target at most 5-7 items. Prioritize by impact on the six assessment dimensions.
- Items carried over for 3+ consecutive iterations without being addressed should be re-evaluated: include, defer with a reason, or drop.
- Total carryover items should not exceed 15. If approaching this limit, consolidate related items or drop low-priority ones.

### Stage 2: Train (`01.train/`)

**Seed:** Create the iteration's git branch as described in Key Rules. `target_skill/` is already at the workspace root — no copying needed.

**Train (delegated to sub-agent):** Spawn a sub-agent to execute the target skill
against every rawdata item. The sub-agent operates in isolation — it has no access to
the orchestrator's conversation history. It receives only the parameters below.

**`execute/` is the target skill's working directory.** All outputs produced by running the target skill — documents, reports, generated code, intermediate data, scripts — MUST be written inside `01.train/execute/` but any other directory in current iteration.

**Spawn prompt template:**

```
Execute this skill against rawdata items:
- Skill path: <workspace>/target_skill/SKILL.md
- Rawdata path: <workspace>/rawdata/
- Working directory: <workspace>/iter.XXXX/01.train/execute/
- Train path: <workspace>/iter.XXXX/01.train/
- Read agents/executor.md for your operating instructions
- Task context: <what this iteration is testing, if applicable>
ALL outputs must be written to the working directory above.
```

The sub-agent reads `agents/executor.md` as its operating instructions, loads the
target skill's SKILL.md, processes each rawdata item, and writes outputs to `execute/`,
friction + summary to `train.json`. Schema: `references/schemas.md` (train.json section).

**HTML output:** After the sub-agent writes `train.json`, generate the HTML viewer:
`python show_train.py --input train.json --output train.html`.

**When to delegate vs execute inline vs skip:**
- **Delegate** (preferred): The target skill has executable tasks (file processing, report generation, data transformation, code execution).
- **Execute inline** (fallback): The target skill is purely instructional (writing style, design principles) with no concrete deliverables to produce.
- **Skip** (self-iteration only): When `target_skill` IS `skill-iterator`, follow the self-iteration path described in Step 4.

**After the sub-agent completes**, the orchestrator reviews `01.train/`:
1. Read `train.json` — friction entries (categorized, with workarounds) and execution summary
2. Inspect outputs in `execute/` for quality
3. Proceed to the Evaluate step using these artifacts as evidence

**Execution methodology for new tasks and scenarios:**

1. **Simplicity first.** *See Meta Principle: Simplicity.* Start with the simplest approach
   that works; add complexity only when a real failure demands it.
2. **Prefer scripts over reasoning.** *See Meta Principle: Mechanize.* When the task involves data processing, file I/O, or
   structured output, write a script. A script produces deterministic, verifiable output;
   reasoning about the same task risks subtle hallucination (plausible but wrong results
   that look correct). Scripts ground the training in reality.
3. **Automate repetitive steps across iterations.** *See Meta Principle: Mechanize.* If a step is performed identically in
   two or more iterations (e.g., data preprocessing, file format conversion,
   validation checks), extract it into a reusable Python script and persist it in
   `execute/`. Subsequent iterations should invoke the script rather than redo the
   work manually. This reduces friction, eliminates drift between iterations, and produces
   concrete artifacts that feed validation.json. When in doubt, prefer Python — it has the
   broadest ecosystem for the data-processing and file-manipulation tasks typical in skill
   training.

**Assess and Improve:** This is a three-step checkpoint within Stage 2 — train first,
evaluate second, promote third. All three must complete before moving to Stage 3 (Validate).

1. **Train:** Performed above — the sub-agent processed every rawdata item, wrote outputs to `execute/`, and recorded friction + summary in `train.json`.
2. **Evaluate:** Re-read everything in `01.train/` — `train.json` (categorized friction-workaround pairs + summary), outputs in `execute/`, and persisted scripts in `execute/scripts/`. Assess the training results against the Assessment Framework (below) and `iter.json` items, scoring each of the six dimensions. Identify which friction points trace to skill instructions (gaps, ambiguities, wrong assumptions) versus environmental factors (missing dependencies, data issues). This evaluation is the bridge between raw training data and actionable improvements.
3. **Promote to target_skill/:** Apply improvements directly to `target_skill/` based on the evaluation findings. Each change should trace back to a specific observation from execute/ — if you cannot point to the evidence that motivated a change, reconsider whether it is needed. Commit the improvements on the current iteration branch.

Improvement principles (with Meta Principle references):

- **Generalize, don't special-case.** When a specific instruction fails, find the broader principle covering both cases. *Pitfall: Overfitting — see Meta Principle: Generalize.*
- **Add reasoning before adding rules.** Explain *why* the correct approach matters. Only add explicit rules when reasoning alone doesn't fix the behavior. *Pitfall: Abstraction Ladder — see Meta Principle: Abstract.*
- **Preserve what works.** Change what needs changing, leave what doesn't. *Pitfall: The Style Rewrite — rewriting just because you'd phrase it differently, without a functional reason.*
- **Keep examples as examples.** Ground abstract instructions with specifics, but frame them as illustrating patterns, not templates to copy.
- **Prefer progressive disclosure.** Move detailed reference material to separate files loaded on demand. *Pitfall: Bloat — see Meta Principle: Right-Size.*
- **Right-size the skill.** If during assessment the skill covers 3+ distinct concerns, recommend splitting. *Pitfall: Kitchen Sink — see Meta Principle: Right-Size.*

### Stage 3: Validate (`02.validation/`) — The Most Critical Stage

This stage directly determines the quality of all subsequent stages. Rushing it produces compounding errors. *Pitfall: Skipping Validation — treating it as a formality. Without thorough validation, the Summarize stage has nothing meaningful to synthesize.*

**Core principle: make implicit workflow steps explicit.** During training, the model often relies on assumptions — unstated steps, implicit data formats, or reasoning shortcuts that worked but were never documented. Validation is where those hidden dependencies must surface.

Stage 3 produces one merged JSON file and its HTML viewer in `02.validation/`. Write `validation.json` first, then generate the HTML viewer:
`python show_validation.py --input validation.json --output validation.html`

Schema: `references/schemas.md` (validation.json section). The file contains three sections:

**`benchmark`** — performance metrics (rawdata pass rate, friction count, line counts) and 6-dimension assessment snapshot (ratings from Stage 2 Evaluate).

**`generalization`** — for each problem encountered, document: the specific problem and the **generalized strategy** — the broader principle that applies beyond this specific case. This is where concrete friction points become reusable knowledge.

**`automation`** — review **all** iterations' `01.train/execute` directories — not just the current one — and reflect on three questions: (1) Which steps were tedious or repetitive? (2) What made them tedious? (3) How could a Python script automate them? Prioritize automating steps that recur across iterations. Automation candidates should be promoted into `target_skill/scripts/` when they prove stable.

### Stage 4: Summarize (`iter.json "end"`)

This stage synthesizes validation results. It depends on Stage 3 being complete.

**1. Fill in `iter.json` "end" and "validation" sections:** Re-read every file in `01.train/` (train.json, execute/ outputs) **and all validation artifacts**. Update `iter.json` with:

**End section (SOLUTIONS):** Schema: `references/schemas.md` (iter.json → end section).
- **`end.walkthrough`** — one paragraph overview of how the skill performed against rawdata.
- **`end.friction`** — friction encountered during training with root cause and resolution.
- **`end.items`** — SOLUTIONS items. Each corresponds to a `start.items` requirement by matching `id` (1:1 mapping). `solution`: one sentence recording how the requirement was fulfilled.
- **`end.changelog`** — changes from `git diff iter.(XXXX-1)..iter.XXXX` inside `target_skill/`. Rendered as a Changelog table (File / Change / Why) in the SOLUTIONS section of iter.html.

**Validation section:** Schema: `references/schemas.md` (iter.json → validation section).
- **`validation.items`** — carryover items for the next iteration. System items become the carryover source for the next iteration's `start.items`.

After updating `iter.json`, regenerate the HTML: `python show_iter.py --input iter.json --output iter.html`.

### Stage 5: Finalize

The improved skill is already in `target_skill/` from Stage 2 — there is no separate output copy. Before finalizing, verify:

1. Re-read the full skill — does it hold together coherently?
2. Update the description if capabilities changed.
3. Spot-check against 2+ rawdata items.
4. Check for regressions — did generalization remove constraints important for common cases?
5. Verify all bundled files are present and consistent (no orphaned references).
6. Confirm `iter.json` completeness — every item done or explicitly deferred.
7. **Review changes:** Verify all changes from the iteration (see `end.changelog`) are intentional and well-documented.
8. Commit the final state on the iteration branch (`git add -A && git commit`).
9. **Generate overview:** Run `python show_overview.py --workspace . --output overview.html` from the workspace root.
10. **Package target_skill/** by running `zip -r {target_skill_name}.zip target_skill/ -x 'target_skill/.git/*'` from the workspace root.

**Alternate outcomes:** If the assessment concluded the skill should be split rather than iterated, the output is a decomposition plan (identifying split boundaries and proposed new skills) instead of an improved single skill.

---

## Assessment Framework

Score each dimension as **strong / adequate / weak / missing**, then focus improvement on the weakest first.

### 1. Trigger Coverage (Description)

Does the description cover the full range of user intents, including common synonyms and near-miss scenarios? Is it specific enough to avoid false triggers? Common failure: listing what the skill *is* rather than what the user might *say*.

### 2. Generality (Instructions) — *see Meta Principle: Generalize, Abstract*

Are instructions principle-based rather than example-based? Are there hardcoded assumptions limiting applicability? Common failure: instructions that read like a tutorial for one case rather than a guide for a class of problems.

### 3. Clarity (Structure)

Is information ordered so the model encounters it when needed? Are mandatory vs. aspirational instructions distinguishable? Common failure: critical constraints buried in the middle of long paragraphs.

### 4. Completeness (Edge Cases)

What happens with empty, malformed, or ambiguous input? Trivially simple or extremely complex tasks? Missing prerequisites? Common failure: perfect for "normal" inputs, no guidance for degenerate cases.

### 5. Efficiency (Token Budget) — *see Meta Principles: Right-Size, Mechanize*

Are there redundant sections? Content the model could infer? Reference material that could be loaded on-demand? Common failure: skills that try to be self-contained encyclopedias instead of focused guides.

### 6. Why-Depth (Reasoning)

Do major instructions explain *why* they matter? Could the model derive correct behavior for novel scenarios from the principles given? Common failure: "always do X" and "never do Y" with no reasoning.

---

## Two Modes of Operation

**User-Driven Mode:** The user provides explicit feedback ("fails when...", "should also handle...", "output was wrong because..."). Trace the complaint to root cause in the skill's instructions, fix the root cause to handle the entire class of similar inputs, and verify the fix doesn't break what already works.

**Self-Evaluation Mode:** No explicit complaint. Run through the Assessment Framework, identify highest-impact issues, address them. Prioritize silent failures (plausible but wrong output) over loud failures (model asks for clarification).

**Mode selection rules:**
- If the user provides specific failure reports, error examples, or explicit improvement goals → **User-Driven Mode**. Focus on the reported issues first.
- If the user says "iterate", "improve", or "review" without specifics, or if Step 2 parsed no explicit requirements → **Self-Evaluation Mode**. Run the full Assessment Framework.
- Mixed signals (user gives one example but also says "make it better overall") → Start in User-Driven Mode for the specific issue, then switch to Self-Evaluation Mode for remaining gaps.

---

## Iteration Cadence and Stopping

A good rhythm: iter.0001 fixes obvious gaps (highest ROI), iter.0002-0003 runs deep training and addresses structural issues, iter.0004+ polishes and trims. Don't iterate for the sake of it — a shipped skill is worth more than a perfect one still being tweaked.

**Stopping criteria** — stop iterating when **all** of the following are true:
1. All six Assessment Framework dimensions are rated `adequate` or `strong` for two consecutive iterations.
2. Friction count in the latest iteration is 0 (no unresolved difficulties during training).
3. No carryover items remain unaddressed — all items from prior iterations have been resolved, deferred, or dropped.
4. Rawdata pass rate is 100% with no regressions from the previous iteration.

If these conditions are met, say so explicitly and recommend stopping. If the user requests more iterations despite meeting all criteria, note this in `iter.json` and scope to a single new concern.

**Proportionality:** For trivially simple skills (<50 lines), consider a lighter process — skip the full workspace ceremony and do a focused assessment + improvement pass. For extremely complex skills (>500 lines), scope the iteration to one concern at a time or address the Right-Size concern first (see Meta Principles).
