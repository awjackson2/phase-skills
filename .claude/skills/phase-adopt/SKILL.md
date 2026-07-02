---
name: phase-adopt
description: Use to retrofit the phase workflow into an EXISTING project that already has code and git history. Trigger when the user says "adopt the phase workflow here", "set up phases in this existing repo", "start using phases on this project", "retrofit the workflow", or drops these skills into a project that already has commits. Unlike phase-project-init (which bootstraps an empty repo), this works with an established, possibly-shared default branch: it adds development/phase_log/ via a docs-lane PR, optionally backfills a light phase history reconstructed from git, settles where the first new phase number starts, then hands off to phase-decompose/phase-loop or phase-tracker.
---

# Phase Adopt

This skill brings the phase workflow to a project that **already exists** — it has source code, a git history, probably a shared default branch, maybe a `CLAUDE.md`. It is the existing-repo counterpart to `phase-project-init` (use that one only for an empty/new repo).

Key difference from init: the default branch is already established and may be protected and shared, so adoption does **not** make a bootstrap commit straight to it. The scaffolding lands through a **docs-lane PR**, exactly like any other doc change in a live repo.

It is **not a phase** (no plan/log for adopting). It reuses the same templates `phase-project-init` installs.

## Procedure

### Step 1: Survey the repo

Determine: is it a git repo (it should be — if not, the user wants `phase-project-init` instead)? What is the default branch? Is there a `CLAUDE.md`? Is there already a `development/phase_log/`? If the log already exists, **stop** — the project is adopted; run `phase-recap` to load state instead.

### Step 2: Decide the numbering origin

The repo has prior work that predates the workflow. Settle with the user where new tracked phases begin. Default and recommended:

- Treat **all pre-workflow history as legacy** that simply isn't phase-numbered, and start the first *new* tracked effort at **Major 1** (`1.1.0`), or at a fresh Major if the user wants to reserve low numbers for backfill.
- Honor appendability going forward: once adopted, related future work appends near its theme like any phase ([TERMINOLOGY.md → Core principle](../../../TERMINOLOGY.md)).

Confirm the choice; it affects every future number.

### Step 3: Optional — backfill a light history

If the user wants `phase-recap` to have a baseline on day one, reconstruct a **handful** of retroactive index entries from real git signals — tags, merge commits, PR titles, major commit messages. Rules:

- **Do not fabricate.** Each backfilled line is summarized from a real commit/PR/tag and marked `(reconstructed from git history)`. No invented plan/log files, or at most a stub log that says it was reconstructed.
- Keep it to milestones, not every commit — a readable baseline, not a transcript.
- Number backfilled entries as a clearly-legacy block (e.g. `0.x` or a "pre-adoption" note) so they don't collide with the new numbering origin from Step 2.
- If the user doesn't want backfill, seed an empty index with a one-line note that history predates the workflow.

### Step 4: Install the scaffolding (docs-lane branch)

On a fresh `docs/adopt-phase-workflow` branch cut from the up-to-date default branch:

- Create `development/phase_log/` and copy the three templates from `phase-project-init/assets/development/phase_log/` (`phase_plan_template.md`, `phase_log_template.md`, `phase_index.md`). The seeded index gets the Step 3 backfill (or the empty-with-note form).
- If the project will keep living design docs, create `development/design/` and mention `phase-tracker` Step 3.5 will sync them.
- Add `.claude/worktrees/` to the project's `.gitignore` (create the file if absent) — every phase worktree is created there and must never be tracked by the primary checkout.
- Optionally install the conventions at the project root (`TERMINOLOGY.md`, `templates/recap_template.md`, `templates/response_templates.md`, `phase_project.md`) so the skills' links resolve and the repo self-documents.

### Step 5: Seed or update CLAUDE.md

Add the **phase workflow charter** by pasting the content of `phase_project.md` (everything below its `---`). If a `CLAUDE.md` exists, **append** the charter (don't overwrite the project's existing guidance); if not, create one with it. `phase_project.md` is the single source for this section — don't hand-write a divergent version. Include it in the same docs-lane PR as the scaffolding.

### Step 6: Open the docs-lane PR

Stage the scaffolding with an explicit file list, commit (`docs: adopt phase workflow scaffolding`, with the `Co-Authored-By:` trailer), push, and open a PR to the default branch. Merge it before starting the first phase — adoption is itself a normal change going through the normal gate, not a privileged direct commit.

### Step 7: Hand off to the first phase

Route the first tracked effort:

- **Large multi-step goal** → `phase-decompose` to build the umbrella, then `phase-loop`.
- **One concrete effort** → `phase-tracker` at the Step 2 origin number.

## Setup summary

Report: default branch detected, numbering origin chosen, backfill done/skipped (and how many entries), scaffolding PR opened, CLAUDE.md appended/created (or not), and the proposed first phase with the skill that will run it.

## What this skill should not do

- Do not use it on an empty repo (use `phase-project-init`) or an already-adopted one (use `phase-recap`).
- Do not commit the scaffolding straight to the default branch — it goes through a docs-lane PR.
- Do not fabricate backfilled history; reconstruct only from real git signals and mark it as reconstructed.
- Do not renumber or rewrite the project's existing git history.
- Do not treat adoption as a phase; it needs no plan or log.
