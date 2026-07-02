<div align="center">

# Phase Skills

**A phase-driven development workflow for Claude Code, packaged as drop-in agent skills.**

Plan-before-code gates · per-phase tracking · worktree discipline · decomposition · looped execution · audit

[![Skills](https://img.shields.io/badge/skills-7-blue)](#the-skills)
[![SKILL.md](https://img.shields.io/badge/format-SKILL.md-orange)](https://code.claude.com/docs/en/skills)
[![Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-d97757)](https://claude.com/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## What is this?

These are my personal Claude Code workflow skills that I have progressivly engineered throughout various coding projects. They help keep my AI coding sessions organized, documented, and linear, which consequentially make my codebase more AI friendly.

Basically all developments are broken down into three phase types (Majors, Minors, and Patches). Each phase is kept with its own phase_x_plan.md and phase_x_log.md, so it is easy to remeber (or contextualize) what happened during a specific phase of development.

Newly, I added 'phase-loop', which is a skill that allows you to plan a Major phase, that gets broken down into Minors, then Claude will continously cycle through "phase cycles" (creating plan docs + dev environment -> develop -> log changes + open PR + destroy dev environment) for each Minor, until your larger Major phase has been complete. This makes it easy to start large scale plans and walk away from your computer with trust that developments will be documented, clean, and revertable. 

The workflow is enforced by seven cooperating skills built around one shared state directory, `development/phase_log/`:

```
setup:   phase-project-init (empty repo)  |  phase-adopt (existing repo)
plan:    phase-decompose  → umbrella MAJOR.0.0 roadmap
run:     phase-loop (big effort, loops the cycle)  |  phase-tracker (single effort)
            └ each cycle: phase-recap (read) → phase-tracker (plan → implement → log → commit → PR)
health:  phase-audit (verify the log + git state anytime)
```

## The skills

| Skill | Role | What it does |
|---|---|---|
| [`phase-tracker`](phase-tracker/SKILL.md) | **Core / writer** | Runs the phase cycle: writes the phase plan before code, gates implementation on your approval, writes the phase log after, maintains the index. |
| [`phase-recap`](phase-recap/SKILL.md) | **Core / reader** | Loads project state from the phase logs — silently at session start, or as an explicit scoped 🧭 recap report. Never reads the codebase. |
| [`phase-decompose`](phase-decompose/SKILL.md) | Planner | Turns a large goal into an umbrella roadmap of small, testable, dependency-ordered phases. |
| [`phase-loop`](phase-loop/SKILL.md) | Orchestrator | Drives a whole effort to completion by looping the phase cycle against the roadmap; resumes half-finished efforts. |
| [`phase-project-init`](phase-project-init/SKILL.md) | Setup (fresh) | Bootstraps an empty repo: git, `development/phase_log/`, templates, conventions. |
| [`phase-adopt`](phase-adopt/SKILL.md) | Setup (existing) | Retrofits the workflow into a repo that already has code and history, with optional git-history backfill. |
| [`phase-audit`](phase-audit/SKILL.md) | Health check | Verifies the phase log against git: orphan plans, broken index links, dangling worktrees, stale docs. Read-only by default. |

An eighth skill, [`phase-amend`](phase-amend/SKILL.md), is a maintenance tool for **this repository only** — it propagates changes to shared conventions across every file that embeds them. Don't install it into your projects.

## Installation

**As a Claude Code plugin (recommended — one command, easy updates):**

```
/plugin marketplace add awjackson2/phase-skills
/plugin install phase-workflow@phase-skills
```

This installs the seven workflow skills as a single plugin.

**Or copy the skill folders directly** into `.claude/skills/` (per project) or `~/.claude/skills/` (everywhere).

Per project:

```bash
git clone https://github.com/awjackson2/phase-skills.git /tmp/phase-skills
mkdir -p .claude/skills
cp -r /tmp/phase-skills/phase-{tracker,recap,decompose,loop,project-init,adopt,audit} .claude/skills/
```

Global (all projects):

```bash
git clone https://github.com/awjackson2/phase-skills.git /tmp/phase-skills
mkdir -p ~/.claude/skills
cp -r /tmp/phase-skills/phase-{tracker,recap,decompose,loop,project-init,adopt,audit} ~/.claude/skills/
```

You don't need all seven — `phase-tracker` + `phase-recap` alone give you the core plan/log loop. Add the others as you need setup, decomposition, looping, or auditing.

## Quick start

In a Claude Code session with the skills installed:

- **Fresh project:** *"Set up the phase workflow here"* → `phase-project-init` scaffolds everything, then hands off to your first phase.
- **Existing repo:** *"Adopt the phase workflow in this repo"* → `phase-adopt` retrofits it via a docs-only PR.
- **Big effort:** *"Break this down and build the whole thing"* → `phase-decompose` writes the roadmap, `phase-loop` executes it phase by phase.
- **Single feature:** *"Let's start a new phase for X"* → `phase-tracker` writes the plan, waits for your approval, then implements and logs.
- **Any time:** *"Catch me up"* (`phase-recap`) or *"Audit the phases"* (`phase-audit`).

## How it works

### Phase numbering

Every phase has a three-part number, `MAJOR.MINOR.PATCH`:

```
Major 5                     ← a milestone / major area of work
├── Minor 5.1               ← a feature (own branch, worktree, PR)
│   └── Patch 5.1.1         ← an iteration / fix (a commit on the Minor's branch)
├── Minor 5.2
└── Minor 5.3
```

A Major is never "sealed" — related future work is always numbered near its theme (`3.8.0` long after Major 3 seemed done), so a change stays physically close to the plans and decisions that explain it.

### The phase cycle

Each Minor runs one cycle: **new worktree + branch + phase plan → implement → phase log + commit → PR**. Plans are approved before code is written; logs are written before the PR opens. All state lives in `development/phase_log/` as plain markdown — `phase_<NUM>_plan.md`, `phase_<NUM>_log.md`, and a chronological `phase_index.md`.

### Response banners

Every workflow turn opens with a labeled banner, so you always know what Claude is asking for:

🟦 `PLAN CONFIRMATION` · 🟩 `DEVELOPMENT APPROVAL` · 🏁 `PHASE DONE` · 🔧 `FIX` · ❓ `OUTSIDE QUESTION` · 💬 `TANGENT` · 🔁 `PHASE LOOP` · 🧭 `PHASE RECAP` · 🩺 `PHASE AUDIT`

## Repository layout

```
phase-<name>/SKILL.md        the seven installable skills (+ phase-amend, repo-maintenance only)
phase-project-init/assets/   the phase-log scaffolding that init installs
TERMINOLOGY.md               canonical glossary (Major/Minor/Patch, recap scoping, core principles)
templates/                   recap + response-banner formats
phase_project.md             portable workflow charter — paste into any project's CLAUDE.md
CLAUDE.md                    authoring guide for this repo
```

Each skill is self-contained — it embeds every convention it needs, so it works dropped into a project alone. The root docs are the canonical source the skills are kept in sync with.

## License

[MIT](LICENSE)
