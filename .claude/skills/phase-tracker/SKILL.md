---
name: phase-tracker
description: Use whenever the user starts non-trivial development work, says things like "let's start phase X", "start the phase", "let's begin a new feature", "next we're going to...", "phase X is done", "close the phase", "write up the phase log", or describes upcoming work that will involve multiple commits or files. Generates a phase plan file at the start of a phase and a phase log file at the end, both under development/phase_log/, following a strict phase-driven workflow. Every meaningful development effort is part of a numbered phase — if the user describes work that does not match a current plan, surface that and offer to draft a plan before coding. Trigger even when the user does not explicitly say "phase".
---

# Phase Tracker

This skill drives a phase-based development workflow. Every meaningful development effort is tracked as a numbered **phase**. Each phase has two markdown files under `development/phase_log/`:

- `phase_<NUM>_plan.md` — written **before** the work, captures the plan to be used
- `phase_<NUM>_log.md` — written **after** the work, captures what actually happened

Two templates live alongside the phase files and define the required structure:

- `development/phase_log/phase_plan_template.md`
- `development/phase_log/phase_log_template.md`

Always follow the template structure. Templates exist so future readers (and Claude in future sessions) can scan any phase quickly without learning a new layout each time. If the templates don't exist yet, run `phase-project-init` first (it scaffolds them).

A chronological table of contents for every phase lives at `development/phase_log/phase_index.md`. Keep it in sync whenever a new phase log is written (see Mode 2, Step 3).

## Terminology

Follows [TERMINOLOGY.md](../../../TERMINOLOGY.md). A phase identifier is the three-digit `MAJOR.MINOR.PATCH` (digits only — never a letter suffix). The levels nest: a **Major** contains Minors; a **Minor** contains Patches.

- **Major** — a milestone. **Minor** — a feature / self-contained effort (own branch, worktree, PR). **Patch** — an iteration / fix / sub-step, committed onto the Minor's branch.
- Always capitalize **Major / Minor / Patch** when they name a phase.
- **"Start the phase"** and **"close the phase"** mean the *entire* opening / closing process below, not a single step.

## The phase cycle

Each phase runs the same pipeline — the **phase cycle** — all of it inside a git worktree on the phase branch:

prompt → discussion → refinement → determine the phase number → cut the phase branch → create the local worktree → move into the branch + worktree → write the phase plan → **🟦 plan confirmation** → **🟩 development approval** → implement → give a change summary and wait for confirmation → write the phase log → sync any living design docs → commit to the branch → pull the default branch to stay current → resolve conflicts → open the PR → **🏁 phase done**.

Branch granularity is the **Minor** (`MAJOR.MINOR`) — one branch, one worktree, one PR per Minor. **Patches** (`MAJOR.MINOR.PATCH`) are commits on that same branch; they keep their own plan/log but get no separate branch, worktree, or PR. See "Git and worktree rules".

## Response banners

Turns in the phase workflow open with a labeled header banner so the user always knows the current mode (full set in [templates/response_templates.md](../../../templates/response_templates.md)). This skill uses four:

- **🟦 Plan Confirmation** — plan written, "is the plan right?" (Mode 1, Step 4)
- **🟩 Development Approval** — plan locked, "shall I start coding?" (Mode 1, Step 5)
- **🏁 Phase Done** — phase finished, summarizing + proposing next (Mode 2, Step 5)
- **🔧 Fix** — a corrective change; classify it as a Patch or as trivial (Mode 3)

## When to trigger

1. **Starting a phase.** "Let's start phase X", "start the phase", "begin a new feature", "next we're going to...", or describing upcoming work likely to span multiple files or commits.
2. **Closing a phase.** "Phase X is done", "close the phase", "write up the phase log", or describing work as complete.
3. **Mid-phase drift.** Non-trivial work that doesn't clearly belong to the current plan. Surface the mismatch and offer to write a plan before coding.
4. **Implicit phase work.** Directions for a substantial change without mentioning phases. Pause and confirm which phase the work belongs to first.

Trivial work — single-line bug fixes, doc edits, exploratory questions, code reading — needs no phase. Use judgment: a commit-worthy change spanning multiple files or shifting behavior is phase work.

## Mode 1: Drafting a phase plan

Use this mode at the **start** of a phase, before writing code.

> **Plan before code — always, no exceptions.** The `phase_<NUM>_plan.md` file must be written (and confirmed) before any implementation code is touched — even when an umbrella/roadmap plan already enumerates the work. Each concrete phase gets its own plan file *first*. Never implement and backfill the plan afterward; if you catch yourself coding without a plan file, stop and write it.

> **Branch and worktree before plan.** Before writing the plan, cut the phase branch and create its local worktree **under `.claude/worktrees/<branch-name>` (never anywhere else)**, then move into them. The plan file is written inside the worktree, not the primary checkout.

**Model tip (optional).** Planning benefits from stronger reasoning; implementation doesn't need it. This is a natural point to switch to a stronger-reasoning model — e.g. `/model opus` — for drafting the plan. Claude can't switch models on its own, so do it yourself if you want it; nothing below depends on it. Switch back before implementation starts (see Step 5).

### Step 1: Determine the phase number

Look at the existing files in `development/phase_log/` for the highest numbers in use, then:

- **Cluster related work near its theme.** A phase number signals topic, not just sequence: if Minor 8.2 is notifications, later notification work lands as Patch `8.2.1`, `8.2.2`, … on the same theme rather than at a distant unrelated number.
- **New feature** → bump the Minor, reset Patch to 0 (`8.2.0` → `8.3.0`).
- **Follow-up on an existing feature** → bump the Patch (`8.2.0` → `8.2.1`). A **Patch** is appropriate when the work is a small fix-set against a Minor that just shipped (typo / overflow / visual polish), the user said "fixes" / "polish" / "follow-up to X.Y" and the scope stays inside that Minor's theme, or the next Minor is already reserved for unrelated work.
- **New milestone** → bump the Major and reset (`8.x` → `9.0.0`). A Major's umbrella/roadmap plan is itself `MAJOR.0.0`.

**Digits only — never letter suffixes.** A phase identifier is purely numeric dotted form (`9.4.1`); never `9.4.1A`. This holds everywhere the number appears — filenames, index entries, commit messages, headers, todos, in-conversation shorthand. To break a plan's work into labelled chunks, use plain sub-sections *within* the document (`### 1.`, `### Step 2`) — not a letter on the number. Chunks big enough for their own identity are separate phases with their own numeric `MAJOR.MINOR.PATCH`.

If unsure which number to use, ask. Phase numbers show up in commits, branch names, and cross-references.

### Step 2: Capture intent from the user

Before writing the plan, you must understand: **Phase name**, **Purpose** (why it exists, what it proves/de-risks), **Concrete goals** (the verifiable changes), **Scope boundaries** (what's deferred), and **Starting point** (relevant current state).

If any are unclear, ask. Do not invent scope. "While we're at it" extensions go in "Out Of Scope" unless the user confirms them in.

### Step 3: Write the plan file

Create `development/phase_log/phase_<NUM>_plan.md` using the structure in `phase_plan_template.md`. Required sections: Phase (number, name, status="Planned", date drafted), Purpose, Immediate Goal (numbered deliverables), Confirmed Starting Point (with real file paths), Scope For This Phase (In / Out), Recommended Implementation Direction, Technical Plan, Test Plan, Key Decisions, Expected Limitations At End Of Phase, What Comes Next, Summary.

Style: reference real file paths (the plan is a working document, not a pitch); be specific about what will and won't change; follow each rule with its reasoning; keep "Out Of Scope" honest; the Test Plan covers the scoped tests this phase's modules need — the full suite is the PR's CI job, not a plan step.

### Step 4: 🟦 Plan Confirmation (first gate)

Show the user the plan file path and a one-paragraph summary. Use the Plan Confirmation banner:

```
### 🟦 PLAN CONFIRMATION · Phase <NUM> — <name>

**Plan file:** development/phase_log/phase_<NUM>_plan.md
**In one paragraph:** <what this phase will do and why>
**In scope:** <short list>   **Out of scope:** <short list>

Confirm this plan is right, or tell me what to change. I won't touch code until you approve it.
```

Wait for the user to confirm the plan is correct. Don't write code yet.

### Step 5: 🟩 Development Approval (second gate)

Once the plan is confirmed, get the explicit go-ahead to implement:

```
### 🟩 DEVELOPMENT APPROVAL · Phase <NUM> — <name>

**Plan:** confirmed ✓   **Branch:** phase-<MAJOR.MINOR>-<slug>   **Worktree:** .claude/worktrees/phase-<MAJOR.MINOR>-<slug>
**About to build:**
- <deliverable 1>
- <deliverable 2>

Approve to start development? (yes / adjust)
```

Only begin implementation after approval. (If the user approves the plan and development in one breath, you may collapse the two gates — but the plan file still exists first.)

**Model tip (optional).** If you switched models for planning, switch back now — e.g. `/model sonnet` — before implementation begins; coding doesn't need the heavier model.

## Mode 2: Writing the phase log

Use this mode at the **end** of a phase, after the work is done (or explicitly stopped).

### Step 0: Summarize and wait for confirmation

Before writing the log, summarize the changes the phase actually made and wait for the user's confirmation that the work is complete and correct. The log records a closed phase, not one still under review.

### Step 1: Reconstruct what actually happened

Read: the plan file (what was promised), `git log` for the phase branch / commit range (what shipped), test files added or changed, any review artifacts. If the plan and the commits disagree, the log reports the truth — the plan is aspirational, the log is historical.

### Step 2: Write the log file

Create `development/phase_log/phase_<NUM>_log.md` using `phase_log_template.md`. Required sections: Phase (number, name, status="Completed"/"Stopped", date completed), Phase Goal (2-4 sentences, as it actually applied), Major Additions, Major Changes, Progress Made, Key Decisions, Current Limitations, Artifacts Produced (with file paths), What Comes Next, Summary.

Style: reference real file paths; be honest about what was deferred (list it under Current Limitations, don't bury it); call out in-phase course corrections under Major Changes; don't over-claim (if a feature works in tests but wasn't validated end-to-end, say so).

### Step 3: Append the phase to the index

**Append** a new entry to the bottom of the **Timeline** list in `development/phase_log/phase_index.md`. The index is maintained in **chronological (log-written) order, not numeric** — new entries go at the bottom, so the bottom is always the most-recently-logged phase (the convention `phase-recap` relies on). Don't slot into numeric position; append.

Line format:

```
- **Phase X.Y.Z** (YYYY-MM-DD) — [plan](phase_X.Y.Z_plan.md) · [log](phase_X.Y.Z_log.md) — One-sentence super-simple summary.
```

Summary rules: a single plain-English sentence for a non-engineer skimming history (say *what shipped*, not how it works); when the phase ran tests, close with the run result in parentheses (e.g. `(412 passed, 1 skipped)`) if you have a real number; drop the plan link if there's no plan file, or note "planned — not yet shipped" if planned but unshipped; the date is the phase's completion date from the log header.

Because every phase appends to this one file, two phase branches open at the same time will conflict here at merge. The resolution is always to **keep both lines** — order is chronological by merge, so the later-merged phase's line sits below. Sequential PR-per-Minor avoids the conflict entirely; a stacked effort (each branch cut from the previous tip) does too.

### Step 3.5: Sync any living design docs

If the project keeps curated "current state" docs (architecture/design docs, a data dictionary, a behavior-tracking README section), those are the curated present; the phase log is the immutable history. Before committing: identify which docs the phase touched, update their content, set their "last synced" marker (e.g. `Last synced: Phase X.Y.Z (YYYY-MM-DD)`) to this phase, append one row to any phase-history table, and stage these edits with the phase commit so log + index + design docs land as one unit. If the phase touched no design doc, say so in the log instead of skipping silently. If the project has no such docs, skip this step.

### Step 4: Commit the phase, then sync with the default branch

After the log is written and the index entry appended, **commit the phase's work** — the commit is the last step of every phase, not something to wait for the user to request.

- Before committing, run the **scoped** tests for the modules the phase touched (per-file / by-name / by-keyword) and confirm they pass. Don't run the full suite locally — that's the PR's CI check. If scoped coverage was thin, note it in the log. When a Patch edits code shared with earlier phases (a function or module they also exercise), re-run those earlier phases' tests for that module too — the blast radius includes them.
- Message format: `Phase X.Y.Z: <short summary>`.
- **Commit to the phase branch, never to the default branch.** The default branch is protected. The phase is already on its `phase-<MAJOR.MINOR>-slug` branch; Patches commit onto that same branch.
- Stage the phase's code, tests, plan/log/index files, and any synced design docs together with an explicit file list (never `git add -A`) so the phase is one atomic, revertable unit. End the message with the `Co-Authored-By:` trailer.
- **After committing, pull/rebase onto the latest default branch and resolve conflicts.** Re-run affected scoped tests if new code merged in.
- **Open the PR when the Minor wraps** — one PR per Minor: push the branch and open a PR to the default branch (`gh pr create`), title `Phase X.Y.Z: <summary>`, body summarizing the log(s). If the Minor has planned Patches (e.g. `2.1.0` then `2.1.1`), wait until the **last** planned phase on the branch is committed, then open a single PR covering them all — not one PR per phase. A Patch raised *after* the Minor's PR merged is a new cycle: its own branch off the latest default branch, its own PR. Merge only after CI is green.

### Step 5: 🏁 Phase Done

Close out with the Phase Done banner:

```
### 🏁 PHASE DONE · Phase <NUM> — <name> · <Completed | Stopped>

**Shipped:**
- <what now works that didn't before>
**Close-out:** log written ✓ · index updated ✓ · committed ✓ · PR opened <link / pending>
**Scoped tests:** <result>
**Deferred / limitations:** <or "none">
**What's next:** <proposed next Minor / Patch and why>

Anything missing before I close this phase?
```

## Mode 3: Mid-phase mismatch and fixes

If the user asks for work that does not match the current plan:

1. Identify which phase plan should govern the work. Read the latest `phase_<NUM>_plan.md`.
2. If the work fits the plan, proceed.
3. If it clearly exceeds the plan, say so directly and offer two options: defer it to a follow-up phase (add a one-line note to "What Comes Next"), or bump the current plan's scope explicitly (with the user's agreement) and update the plan file.
4. Never silently expand a phase. Silent expansion is what the phase system exists to prevent.

For a **corrective change**, decide first whether it is a **Patch** on the current Minor (commit-worthy → gets a number, its own plan/log, a commit on the Minor's branch) or **trivial** (no phase). State which with the Fix banner:

```
### 🔧 FIX · Phase <NUM> <or: trivial — no phase>

**Problem:** <what's wrong>   **Fix:** <what changed>
**Classification:** <Patch <NUM> on Minor X.Y | trivial, no phase tracking>
**Verified:** <scoped tests / manual check>
```

## File-naming convention

- Plans: `phase_<NUM>_plan.md` (e.g. `phase_8.2.0_plan.md`, `phase_8.2.1_plan.md`). Logs: `phase_<NUM>_log.md`.
- `<NUM>` is always the three-digit `MAJOR.MINOR.PATCH` form — even the first version of a feature (`phase_8.2.0_plan.md`). The Patch digit is reserved from the start for fixes / iterations on the same `MAJOR.MINOR.0` scope; reserve it explicitly rather than renaming later. Two dots in the filename is intentional.
- One plan and one log per phase. If the plan changes substantially mid-phase, edit it in place rather than forking a second file — the log narrates the change under "Major Changes".

## Git and worktree rules

These make the phase cycle safe and revertable. The skill is self-contained — it does not depend on a separate rules file in the project.

- **Never develop on the default branch.** It is protected; every change reaches it only through a merged PR.
- **Cut a `phase-<MAJOR.MINOR>-slug` branch from an up-to-date default branch** at phase start, and create a dedicated worktree for it **under `.claude/worktrees/<branch-name>` — never anywhere else**. Keep `.claude/worktrees/` gitignored so the checkouts never pollute the primary working tree. Do all development inside that worktree.
- One branch / worktree / PR per **Minor**. **Patches** are commits on that same branch — never separate branches, worktrees, or PRs.
- Commit with explicit reviewed file lists (never `git add -A`), a `Phase X.Y.Z:` message, and a `Co-Authored-By:` trailer.
- After committing, pull/rebase onto the latest default branch and resolve conflicts; re-run affected scoped tests if new code merged in.
- Open the PR when the phase wraps. Merge only after CI is green.
- Remove a phase's worktree when the phase wraps (`git worktree remove <path>`); keep the branch ref until the PR merges.

**Stacked multi-phase efforts:** cut the first branch from an up-to-date default branch; cut each subsequent phase from the previous phase's branch tip (`git checkout -b phase-13.2-slug phase-13.1-slug`). Give each stacked phase its own commits, plan/log, index entry, and design-doc sync. Open one consolidated PR at the end from the final phase's branch — not one per phase. After it merges, delete every branch (local + remote) and prune leftover worktrees. If two phases are genuinely independent, cut both from the default branch instead.

## What this skill should not do

- Do not write the plan or log without first reading the templates. They may have been updated.
- Do not invent goals the user did not state.
- Do not summarize the codebase in place of describing the phase. Reference files, don't duplicate them.
- Do not skip "Confirmed Starting Point" in plans — it is the only section that locks in the baseline.
- Do not run the full suite locally or gate the commit on it. Scoped tests gate iteration; the full suite is the PR's CI check.
- Do not forget to append the phase to `phase_index.md` after writing the log. The index is the project's only at-a-glance timeline.
