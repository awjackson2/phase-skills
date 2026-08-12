---
name: phase-project-init
version: 1.2.0
description: Use to bootstrap a fresh project for the phase-driven workflow. Trigger when the user is starting a brand-new project, says "initialize the project", "set up the project", "bootstrap this repo", "set up the phase workflow here", "phase init", or otherwise wants the scaffolding (development directories, phase-log templates, optionally git) in place before any phase work begins. Asks whether the project should use git (it is optional), sets up the development/phase_log/ structure, the plan/log/index templates, and the conventions the phase-tracker and phase-recap skills expect, then hands off to phase-tracker or phase-loop for the first phase.
---

# Phase Project Init

This skill prepares an empty or new project so the rest of the phase workflow has the structure it expects. Run it once, at the very start of a project.

> **Empty repo only.** If the project already has code and git history, use `phase-adopt` instead — it lands the same scaffolding through a docs-lane PR rather than the direct bootstrap commit below.

It is **not itself a phase** — bootstrapping needs no phase plan or log. In a git-tracked project it is the one time it is acceptable to make a direct commit to the default branch (the initial scaffold commit), because there is nothing yet to branch from. Every commit after this one goes through the branch + worktree + PR cycle.

## What "set up" means

By the end, the project has:

1. A decision about git — and, if the user wants it, a repository with an initial commit and a known default branch. **Git is optional**; the workflow runs without it.
2. A **knowledge bundle** at `development/` — a `design/` layer, a `phase_log/` layer with the three templates and a seeded `phase_index.md`, and the reserved root files.
3. The conventions the phase skills rely on, optionally documented at the project root.
4. A clear answer to "what's the first phase?" — handed off to `phase-tracker` (single effort) or `phase-loop` (large umbrella plan).

## Procedure

### Step 1: Confirm the project root and intent

Confirm the directory to initialize and that it is meant to be a new phase-workflow project. If it already has a `development/phase_log/`, stop — it's already initialized; offer `phase-recap` instead. Ask the user one question if anything is ambiguous: project name, whether this project will keep living design docs, and — always — **whether they want to use git** (see Step 2).

### Step 2: Ask about git, then initialize it (or don't)

**Ask the user whether this project should use git — never assume it.** Git buys the workflow its branch/worktree/PR discipline, but the phase workflow itself (plans before code, logs after, the index) works fine without it. Put the question plainly: *"Do you want this project under git? The phase workflow works either way — with git each Minor gets its own branch and PR; without it, phases are just tracked in `development/phase_log/`."*

**If the user wants git:**

- If not already a repo, `git init` and set the default branch (`git branch -M main`, or ask if they want another name).
- Create a `.gitignore` if none exists — minimal and appropriate to the stack the user names (don't guess heavily; a near-empty `.gitignore` is fine to start). Include `.worktrees/` — every phase worktree is created there and must never be tracked by the primary checkout.
- Note the **branch-protection convention** to the user: the default branch is protected by policy — all later changes reach it only through PRs. Local git can't enforce this; if a remote exists, suggest enabling branch protection there. Record it as a rule, not an enforced setting.

**If the user declines git:**

- Skip everything git-related, here and in every later phase: no branches, worktrees, commits, or PRs. The phase cycle reduces to plan → approve → implement → log + index.
- Tell them git is **easy to add later**: run `git init`, commit everything as the baseline, and follow the workflow's git rules from that point on — no restructuring needed, because the phase artifacts are ordinary files that git picks up as-is. Any phase skill can help do this when asked.

### Step 3: Create the knowledge bundle

`development/` is a **knowledge bundle**: everything inside it is a concept — a
document with YAML front matter, following the shape the templates carry.
Evidence and analysis (audits, triage notes, scratch research) live *outside*
it, so the directory explains itself.

Copy this skill's bundled payload wholesale — the asset tree is already the
target shape:

- `assets/development/` → `development/`
  - `index.md`, `log.md` — the reserved root files.
  - `design/index.md`, `design/_element_template.md` — the curated
    current-state layer.
  - `phase_log/phase_plan_template.md`, `phase_log/phase_log_template.md`,
    `phase_log/phase_index.md` — the phase-history layer, seeded and empty.

There is no separate schema file or validator tool — the templates *are* the
contract, and upholding it (complete front matter, one `## OKF relationships`
footer per phase record, no stray files in the bundle) is part of writing each
record.

Keep `design/` even if the project has nothing to document yet; the layer costs
one index file and `phase-tracker` Step 3.5 fills it in as phases land.

### Step 4: Install the conventions (optional but recommended)

The phase skills each embed their own conventions, so they work without these files. Installing them at the project root makes the project self-documenting and lets the skills' reference links resolve:

- `TERMINOLOGY.md` — the Major / Minor / Patch glossary and the scoped-recap rules.
- `templates/recap_template.md` and `templates/response_templates.md` — the recap report format and the labeled response banners.
- `phase_project.md` — the portable workflow charter (used in Step 5).

If the full phase-skills suite is available alongside the skills, copy those files to the project root. If only the individual skills were dropped in, skip this — nothing breaks.

### Step 5: Seed or update the project's CLAUDE.md

Add the **phase workflow charter** to the project's `CLAUDE.md`: paste the content of `phase_project.md` (everything below its `---`). It is self-sufficient — it drives the workflow even without the skills, and it carries the terminology, response banners, and git rules into the project. If a `CLAUDE.md` exists, **append** the charter (don't overwrite the project's existing guidance); if not, create one with it. `phase_project.md` is the single source for this section — don't hand-write a divergent version.

### Step 6: Initial commit (git projects only)

If the project uses git, stage the scaffolding with an explicit file list (the `development/` tree, `.gitignore`, any conventions/CLAUDE.md added) and commit to the default branch:

```
chore: bootstrap phase workflow scaffolding
```

End with the `Co-Authored-By:` trailer. This is the only sanctioned direct-to-default-branch commit; say so when you make it. In a project without git, skip this step.

### Step 7: Hand off to the first phase

Determine the first unit of work with the user and route to the right skill:

- **One concrete effort** → `phase-tracker`, starting at `1.1.0` (the first Minor of Major 1). In a git project, cut the branch + worktree (under `.worktrees/`) and write the plan; without git, just write the plan.
- **A large multi-step plan / umbrella** → `phase-decompose` to chunk it into a quality roadmap, then `phase-loop` to run the cycles until complete. The umbrella/roadmap plan is `1.0.0` (`MAJOR.0.0`).

Numbering starts at Major 1. Reserve `MAJOR.0.0` for a Major's umbrella/roadmap plan; the first real feature is `1.1.0`.

## Setup summary

When done, give the user a short report: git set up (default branch) or deliberately skipped, `development/phase_log/` created with templates + seeded index, conventions installed (or skipped), CLAUDE.md created/updated (or not), initial commit made (git projects), and the proposed first phase with the skill that will run it.

## What this skill should not do

- Do not run it on an already-initialized project (one that has `development/phase_log/`). Use `phase-recap` to load state instead.
- Do not initialize git without asking. Git is optional; the user decides, and declining it must not degrade the rest of the setup.
- Do not put anything but concepts inside `development/`. Audits, triage notes, scratch research, and tooling go elsewhere in the project — keeping the bundle clean is the point.
- Do not treat the bootstrap as a phase — no plan/log for the setup itself.
- Do not commit project source code in the bootstrap commit; this commit is scaffolding only. Real work starts on a branch in the next step.
- Do not invent project specifics (stack, design docs, branch names) — ask when unsure.
