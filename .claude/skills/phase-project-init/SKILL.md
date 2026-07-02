---
name: phase-project-init
description: Use to bootstrap a fresh project for the phase-driven workflow. Trigger when the user is starting a brand-new project, says "initialize the project", "set up the project", "bootstrap this repo", "set up the phase workflow here", "phase init", or otherwise wants the scaffolding (git, development directories, phase-log templates) in place before any phase work begins. Sets up git, the development/phase_log/ structure, the plan/log/index templates, and the conventions the phase-tracker and phase-recap skills expect, then hands off to phase-tracker or phase-loop for the first phase.
---

# Phase Project Init

This skill prepares an empty or new project so the rest of the phase workflow has the structure it expects. Run it once, at the very start of a project.

> **Empty repo only.** If the project already has code and git history, use `phase-adopt` instead — it lands the same scaffolding through a docs-lane PR rather than the direct bootstrap commit below.

It is **not itself a phase** — bootstrapping needs no phase plan or log. It is the one time it is acceptable to make a direct commit to the default branch (the initial scaffold commit), because there is nothing yet to branch from. Every commit after this one goes through the branch + worktree + PR cycle.

## What "set up" means

By the end, the project has:

1. A git repository with an initial commit and a known default branch.
2. `development/phase_log/` containing the three templates and a seeded `phase_index.md`.
3. The conventions the phase skills rely on, optionally documented at the project root.
4. A clear answer to "what's the first phase?" — handed off to `phase-tracker` (single effort) or `phase-loop` (large umbrella plan).

## Procedure

### Step 1: Confirm the project root and intent

Confirm the directory to initialize and that it is meant to be a new phase-workflow project. If it already has a `development/phase_log/`, stop — it's already initialized; offer `phase-recap` instead. Ask the user one question if anything is ambiguous: project name, default branch name (`main` unless they say otherwise), and whether this project will keep living design docs.

### Step 2: Initialize git

- If not already a repo, `git init` and set the default branch (`git branch -M main` or the chosen name).
- Create a `.gitignore` if none exists — minimal and appropriate to the stack the user names (don't guess heavily; a near-empty `.gitignore` is fine to start). Include `.claude/worktrees/` — every phase worktree is created there and must never be tracked by the primary checkout.
- Note the **branch-protection convention** to the user: the default branch is protected by policy — all later changes reach it only through PRs. Local git can't enforce this; if a remote exists, suggest enabling branch protection there. Record it as a rule, not an enforced setting.

### Step 3: Create the development structure

- Create `development/` and `development/phase_log/`.
- Copy this skill's bundled templates into `development/phase_log/`:
  - `assets/development/phase_log/phase_plan_template.md`
  - `assets/development/phase_log/phase_log_template.md`
  - `assets/development/phase_log/phase_index.md`  (the seeded, empty index)
- If the user wants living design docs (Step 1), create `development/design/` and tell them `phase-tracker` Step 3.5 will keep those in sync with the phase log. Otherwise leave it out — it's optional.

### Step 4: Install the conventions (optional but recommended)

The phase skills each embed their own conventions, so they work without these files. Installing them at the project root makes the project self-documenting and lets the skills' reference links resolve:

- `TERMINOLOGY.md` — the Major / Minor / Patch glossary and the scoped-recap rules.
- `templates/recap_template.md` and `templates/response_templates.md` — the recap report format and the labeled response banners.
- `phase_project.md` — the portable workflow charter (used in Step 5).

If the full phase-skills suite is available alongside the skills, copy those files to the project root. If only the individual skills were dropped in, skip this — nothing breaks.

### Step 5: Seed or update the project's CLAUDE.md

Add the **phase workflow charter** to the project's `CLAUDE.md`: paste the content of `phase_project.md` (everything below its `---`). It is self-sufficient — it drives the workflow even without the skills, and it carries the terminology, response banners, and git rules into the project. If a `CLAUDE.md` exists, **append** the charter (don't overwrite the project's existing guidance); if not, create one with it. `phase_project.md` is the single source for this section — don't hand-write a divergent version.

### Step 6: Initial commit

Stage the scaffolding with an explicit file list (the `development/` tree, `.gitignore`, any conventions/CLAUDE.md added) and commit to the default branch:

```
chore: bootstrap phase workflow scaffolding
```

End with the `Co-Authored-By:` trailer. This is the only sanctioned direct-to-default-branch commit; say so when you make it.

### Step 7: Hand off to the first phase

Determine the first unit of work with the user and route to the right skill:

- **One concrete effort** → `phase-tracker`, starting at `1.1.0` (the first Minor of Major 1). Cut the branch + worktree (under `.claude/worktrees/`) and write the plan.
- **A large multi-step plan / umbrella** → `phase-decompose` to chunk it into a quality roadmap, then `phase-loop` to run the cycles until complete. The umbrella/roadmap plan is `1.0.0` (`MAJOR.0.0`).

Numbering starts at Major 1. Reserve `MAJOR.0.0` for a Major's umbrella/roadmap plan; the first real feature is `1.1.0`.

## Setup summary

When done, give the user a short report: repo initialized (default branch), `development/phase_log/` created with templates + seeded index, conventions installed (or skipped), CLAUDE.md created/updated (or not), initial commit made, and the proposed first phase with the skill that will run it.

## What this skill should not do

- Do not run it on an already-initialized project (one that has `development/phase_log/`). Use `phase-recap` to load state instead.
- Do not treat the bootstrap as a phase — no plan/log for the setup itself.
- Do not commit project source code in the bootstrap commit; this commit is scaffolding only. Real work starts on a branch in the next step.
- Do not invent project specifics (stack, design docs, branch names) — ask when unsure.
