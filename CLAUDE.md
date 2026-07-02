# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is an **authoring workspace for the "phase" series of Claude Code skills** — not an application. The deliverables are `SKILL.md` files meant to be dropped into the `.claude/skills/` directory of *any* project so Claude runs a consistent, phase-driven development workflow. There is no build, test, or run step; the work is editing markdown.

The skills must stay **project-agnostic and self-contained** — each one should read clearly on its own, with no assumptions baked in about any particular codebase. When editing, prefer generic illustrative examples over references to a specific project, language, or framework.

## Canonical conventions — read these first

These three files are the source of truth for terminology and formatting across every phase skill. When a skill's wording disagrees with them, they win; when you add or edit a skill, conform to them.

- `TERMINOLOGY.md` — the glossary. Defines the **Major / Minor / Patch** hierarchy, the capitalization rule (always capitalize them as phase nouns), "start/close the phase" meaning the whole process, and the **scoped phase recap** rules (a recap reports the prior phases *within the current phase's scope*).
- `templates/recap_template.md` — the format `phase-recap` uses to produce a scoped recap report.
- `templates/response_templates.md` — the eight labeled response modes (Plan Confirmation, Development Approval, Phase Done, Fix, Outside Question, Tangent, Loop Progress, Phase Recap), each opening with a header banner so the user always knows the current mode.
- `phase_project.md` — the **portable workflow charter**: a self-sufficient markdown block meant to be pasted into any project's `CLAUDE.md` (fresh or existing) to integrate the workflow. `phase-project-init` and `phase-adopt` install it as the project's CLAUDE.md "Phase Workflow" section. Keep it in sync with the above when conventions change.

## Repository contents

Seven skills, each a directory with a `SKILL.md`:

- `phase-tracker/SKILL.md` — generates the per-phase `phase_<NUM>_plan.md` (before code) and `phase_<NUM>_log.md` (after code) under `development/phase_log/`, and maintains `phase_index.md`. The **producer** of phase state. Owns the response banners 🟦 Plan Confirmation, 🟩 Development Approval, 🏁 Phase Done, 🔧 Fix.
- `phase-recap/SKILL.md` — a **context-loading** skill (writes nothing). Two modes: ambient (silent state-load) and scoped (prints a 🧭 recap report of the phases preceding the current one, within scope). The **consumer** of phase state.
- `phase-project-init/SKILL.md` — bootstraps a **fresh/empty** project: git, the `development/phase_log/` structure, the templates, conventions. Carries its installable payload under `phase-project-init/assets/`.
- `phase-adopt/SKILL.md` — the existing-repo counterpart to init: retrofits the workflow into a project that already has code/history, via a docs-lane PR (no bootstrap commit), with optional git-history backfill.
- `phase-decompose/SKILL.md` — turns a large goal into the `MAJOR.0.0` umbrella roadmap, applying a chunk-quality bar (tiny/testable, dependency-ordered, risk-tagged, numbering room left). Feeds `phase-loop`.
- `phase-loop/SKILL.md` — the **orchestrator**. Drives a whole effort to completion by looping the phase cycle against the umbrella roadmap, using `/loop` to self-pace. Resumes half-finished efforts (Mode B). Owns the 🔁 Loop Progress banner.
- `phase-audit/SKILL.md` — checks integrity of the phase log + git state (orphan plans, broken index links, stale design-doc sync, dangling worktrees), reports via the 🩺 banner, fixes safe drift via a docs-lane PR. Read-only by default; the only skill that reads git for its own sake.

Plus one **maintenance skill** that is *not* shipped into other projects — it operates on this repo only:

- `phase-amend/SKILL.md` — applies a change to a shared phase convention consistently across its whole sync surface (canonical docs, every embedded skill copy, the template assets, the charter, `CLAUDE.md`, and the memory), verifies no drift remains, and overrides the installed `.claude/skills/` copies. Use it whenever a change touches a shared rule rather than one skill's private wording — the duplication that keeps skills self-contained is exactly what makes hand-editing drift.

`revere_portal_CLAUDE.md` is a **reference artifact only**, kept for context: a complete CLAUDE.md from a real project that used these skills. It is not part of any shipped skill and is not authoritative for the generalized skills. Do not edit it, and do not copy its project-specific details into the skills.

## Skill architecture (the big picture)

At the core, `phase-tracker` and `phase-recap` are two halves of one loop and must stay mutually consistent — editing one usually forces a matching edit in the other. The other skills build on the same conventions:

- **phase-tracker writes** the artifacts (`phase_<NUM>_plan.md`, `phase_<NUM>_log.md`, `phase_index.md`); **phase-recap reads** them. Conventions defined in one are relied on by the other. Two that recur and must agree across both files:
  - **`phase_index.md` is chronological (append at the bottom = newest), not numeric.** Both skills state this; a high phase number can sit above a lower one logged later.
  - **Phase-number grammar.** Uniform three-digit `MAJOR.MINOR.PATCH`, numeric dotted form only (`9.4.1`, never `9.4.1A`). `MAJOR.MINOR` = one branch / one worktree / one PR (a feature); `MAJOR.MINOR.PATCH` iterations are commits on that feature's branch. MAJOR = milestone, MINOR = feature, PATCH = iteration/fix.
  - **Phases are always appendable** (see `TERMINOLOGY.md` → Core principle, and the `phases-always-appendable` memory). A Major is never sealed; related future work is numbered *near its theme*, not pushed to a distant number. There is deliberately no milestone/closeout step. `phase-audit` must not flag late additions to old themes as drift; `phase-decompose` must leave numbering room.

- **The "phase cycle"** is the core unit of work: new worktree + branch + phase plan → implement → phase log + commit → PR (or branch stack). phase-tracker describes this pipeline end to end; the term "phase cycle" is used consistently across the phase skills. phase-tracker also notes an optional model-switch convention at the plan/implement boundary (stronger reasoning for planning, a faster model for implementation) — a text reminder only, since Claude cannot switch its own model.

- **The skills are self-contained.** They do not defer to a project's CLAUDE.md for rules (git discipline, testing, worktrees) — those rules are stated inside `phase-tracker` itself, so the workflow holds even in a fresh project with no CLAUDE.md.

## How the skills fit together

Lifecycle, with the shared state being `development/phase_log/`:

```
setup:   phase-project-init (empty repo)  |  phase-adopt (existing repo)
plan:    phase-decompose  → umbrella MAJOR.0.0 roadmap
run:     phase-loop (big effort, loops the cycle)  |  phase-tracker (single effort)
            └ each cycle: phase-recap (read) → phase-tracker (plan→implement→log→commit→PR)
health:  phase-audit (verify the log + git state anytime)
```

- **Producers/consumers of phase state:** `phase-tracker` writes plan/log/index; `phase-recap` and `phase-audit` read them; `phase-decompose` writes the umbrella; `phase-loop` calls recap + tracker in a loop. init/adopt create the structure they all use.
- Three skills write into `development/phase_log/` (tracker, decompose, and audit's fixes); the rest read. All writes except init's one bootstrap commit go through a branch + PR.

## Working conventions for editing these skills

- Each skill is a single `SKILL.md` with YAML frontmatter (`name`, `description`). The `description` is the trigger contract — it is how Claude decides to invoke the skill, so it must enumerate the situations and trigger phrases precisely.
- Keep all skills in sync when you change shared conventions, and keep every skill consistent with the same phase-number grammar, capitalization (Major/Minor/Patch), chronological index ordering, response banners, and "phase cycle" terminology.
- Reference paths the skill establishes (`development/phase_log/`, the templates) generically; don't tie examples to a specific domain, language, or test runner.
- **Duplication note:** the canonical conventions live at root (`TERMINOLOGY.md`, `templates/`). Each skill embeds the conventions it needs inline so it stays self-contained when dropped into a project alone; `phase-project-init/assets/` carries copies of the phase-log templates it installs. When you change a convention at root, update the embedded copies in the skills and assets to match.
