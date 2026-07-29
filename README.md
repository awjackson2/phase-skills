<div align="center">

# Phase Skills

**An OKF-native, phase-driven development workflow for Claude Code and ChatGPT/Codex.**

Plan-before-code gates · per-phase tracking · worktree discipline · decomposition · looped execution · audit

[![Skills](https://img.shields.io/badge/skills-7-blue)](#the-skills)
[![SKILL.md](https://img.shields.io/badge/format-SKILL.md-orange)](https://code.claude.com/docs/en/skills)
[![Agents](https://img.shields.io/badge/works%20with-Claude%20%2B%20Codex-6f42c1)](#installation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## What is this?

These are my personal agent-workflow skills, progressively engineered across
real projects. Claude Code and ChatGPT/Codex receive the same workflow:
plan-before-code gates, phase history, worktree discipline, OKF-native
knowledge, and visible agent attribution.

Basically all developments are broken down into three phase types (Majors, Minors, and Patches). Each phase is kept with its own phase_x_plan.md and phase_x_log.md, so it is easy to remeber (or contextualize) what happened during a specific phase of development.

`phase-loop` plans a Major, breaks it into Minors, and lets the active agent
advance phase cycles continuously: create the born-native plan and worktree,
develop, write the log, attribute the commit/PR, and clean up. Every cycle is
documented, reviewable, and revertible.

All new plans, logs, and living design documents are direct Open Knowledge
Format concepts under `development/`. There are no wrapper copies or later
normalization passes.

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

### Claude Code plugin

```
/plugin marketplace add awjackson2/phase-skills
/plugin install phase-workflow@phase-skills
```

This installs the seven workflow skills as a single plugin.

Or copy the seven root skill folders into `.claude/skills/`.

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

### ChatGPT and Codex

The repository includes exact mirrors under `.agents/skills/`. Copy them into
the target project's `.agents/skills/`:

```bash
git clone https://github.com/awjackson2/phase-skills.git /tmp/phase-skills
mkdir -p .agents/skills
cp -r /tmp/phase-skills/.agents/skills/phase-{tracker,recap,decompose,loop,project-init,adopt,audit} .agents/skills/
```

`CLAUDE.md`, `AGENTS.md`, and `AGENT.md` are exact agent-neutral mirrors. The
init/adopt skills install equivalent guidance into projects.

You don't need all seven — `phase-tracker` + `phase-recap` alone give you the core plan/log loop. Add the others as you need setup, decomposition, looping, or auditing.

## Quick start

In a Claude Code or ChatGPT/Codex session with the skills installed:

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

Each Minor runs one cycle: **new worktree + branch + phase plan → implement →
phase log + commit → PR**. Plans are approved before code; logs are written
before the PR. Each numbered plan/log is a direct born-native OKF concept with
complete YAML and a reviewed relationship footer. Living design concepts use
the same Revere-proven direct-authoring shape.

### Response banners

Every workflow turn opens with a labeled banner, so you always know what the
active agent is asking for:

🟦 `PLAN CONFIRMATION` · 🟩 `DEVELOPMENT APPROVAL` · 🏁 `PHASE DONE` · 🔧 `FIX` · ❓ `OUTSIDE QUESTION` · 💬 `TANGENT` · 🔁 `PHASE LOOP` · 🧭 `PHASE RECAP` · 🩺 `PHASE AUDIT`

## Repository layout

```
.agents/skills/phase-*/      exact ChatGPT/Codex mirrors
phase-<name>/SKILL.md        Claude plugin sources (+ phase-amend maintenance)
phase-project-init/assets/   complete OKF + PR scaffold installed into projects
TERMINOLOGY.md               canonical glossary (Major/Minor/Patch, recap scoping, core principles)
OKF.md                       direct-concept + relationship + attribution profile
templates/                   recap + response-banner formats
phase_project.md             portable agent-neutral workflow charter
CLAUDE.md / AGENTS.md / AGENT.md
                             exact authoring-guide mirrors
scripts/validate_repo.py     deterministic mirror and template validation
```

Each skill is self-contained — it embeds every convention it needs, so it works dropped into a project alone. The root docs are the canonical source the skills are kept in sync with.

## License

[MIT](LICENSE)
