---
name: phase-amend
description: Use this skill in the phase-skills authoring repo whenever the user wants to change a rule, convention, terminology, or format of the phase workflow and have it stay consistent across the whole suite. Trigger on "change the phase rule", "update the numbering convention", "phases should now…", "update the phase skills to…", "propagate this convention", "add/rename a response banner", "the index should…", "make the skills consistent", or any edit to a shared phase convention — even if the user names only one file. A single convention is duplicated across the canonical docs, all the phase-* skills' embedded copies, the template assets, the portable charter, CLAUDE.md, and a memory; editing one by hand silently drifts the rest. This skill maps every place the convention lives, applies the change everywhere, verifies no drift remains, and overrides the installed .claude/skills copies. Prefer it over hand-editing whenever a change touches a shared rule rather than one skill's private wording.
---

# Phase Amend

This is a **maintenance skill for the phase-skills authoring repo itself** — not one of the seven workflow skills that ship into other projects. Its job: apply a change to a shared phase-workflow convention *consistently everywhere it is expressed*.

## Why this exists

The conventions are deliberately **duplicated**. The canonical docs (`TERMINOLOGY.md`, `templates/`, `phase_project.md`) are the source of truth, but every skill also **embeds** the conventions it needs so it stays self-contained when dropped into a project alone. That duplication is a feature — and a liability: change the phase-number grammar in `phase-tracker` only, and `phase-recap`, the charter, `CLAUDE.md`, and the memory now disagree. Nothing at runtime catches that drift; a human reading one skill months later just gets a wrong rule.

So the value of this skill is **not** editing — it's knowing the full *sync surface* for a given convention and hitting all of it in one pass, then proving nothing was missed.

## The sync surface

Where each shared convention lives. Grep to confirm before editing (files shift as the suite grows) — treat this as the starting map, not gospel.

| Convention | Lives in |
|---|---|
| **Phase-number grammar** (`MAJOR.MINOR.PATCH`, digits-only, branch=Minor, Patch=commit) | `TERMINOLOGY.md` (hierarchy), `phase-tracker` (Terminology, Step 1, File-naming, Git rules), `phase-recap` (numbering-signal nuance), `phase-decompose`, `phase-adopt` (numbering origin), `phase_project.md`, `CLAUDE.md`, the plan/log template asset headers |
| **Capitalization** of Major/Minor/Patch | `TERMINOLOGY.md`, every skill, `templates/response_templates.md`, `phase_project.md`, `CLAUDE.md` |
| **Appendability** (never seal a Major; number near the theme) | `TERMINOLOGY.md` (Core principle), `phase-audit` (not-drift), `phase-decompose` (numbering room), `phase-tracker` (clustering), `phase_project.md`, `CLAUDE.md`, **the `phases-always-appendable` memory** (outside the repo — see below) |
| **Index ordering** (chronological, bottom = newest) | `phase-tracker` (Step 3), `phase-recap` (Step 1 + nuance), `phase-audit`, the `phase_index.md` asset, `phase_project.md`, `CLAUDE.md` |
| **Response banners** (the set + count) | `templates/response_templates.md` (catalog), `phase-tracker` (🟦🟩🏁🔧), `phase-recap`/`recap_template.md` (🧭), `phase-loop` (🔁), `phase-audit` (🩺), `phase_project.md` (full list), `CLAUDE.md` (names + count) |
| **The phase cycle** pipeline | `phase-tracker`, `phase_project.md`, `CLAUDE.md` |
| **Git / worktree / PR rules** | `phase-tracker` (Git rules, Mode 2 Step 4), `phase-loop` (branch strategy), `phase-project-init` / `phase-adopt` (docs-lane vs bootstrap), `phase_project.md` |
| **Plan / log section lists** | `phase-tracker` (Mode 1 Step 3, Mode 2 Step 2), the two template assets |
| **Scoped-recap scope rules** | `TERMINOLOGY.md` (table), `phase-recap` (Mode B), `templates/recap_template.md`, `CLAUDE.md` |

Two locations are easy to forget because they aren't plain repo `.md` files:

- **The memory** at `~/.claude/projects/-home-aksel-Documents-phase-skills/memory/` (e.g. `phases-always-appendable.md` + the `MEMORY.md` pointer). A principle change must update the memory too, or a future session recalls the old rule.
- **The installed copies** at `.claude/skills/<name>/`. These are the *real* skills the harness loads; the root dirs are the working versions. Edits to root do nothing until the installed copy is overridden (final step).

## Procedure

### 1. Pin down the change

State it as **from → to**, and *why*. A rule change often implies more than its sentence: changing the numbering grammar ripples into file-naming, branch names, and every worked example. Enumerate the ripples before editing, so the propagation is complete rather than literal.

### 2. Locate every occurrence

Grep the whole repo for the old form **and** the concept, not just the exact string — conventions are paraphrased differently per file (the banners appear as a table row in one place, a bullet list in another, a count in a third). Cross-check against the sync-surface table. Include the memory dir.

### 3. Apply canonical-first

Edit in this order so the source of truth leads and the copies conform to it:

1. **Canonical** — `TERMINOLOGY.md`, `templates/`, `phase_project.md`.
2. **Embedded copies** — each affected skill, matching the canonical wording (adapted to that skill's voice; the *rule* must match, the prose needn't be identical).
3. **Assets** — the plan/log/index templates under `phase-project-init/assets/`.
4. **`CLAUDE.md`** — the invariants list, repo contents, architecture notes.
5. **Memory** — update the relevant memory file and `MEMORY.md`.

Preserve each file's voice and altitude; this is not a find-and-replace. When a skill *explains why* a rule holds, update the reasoning too, not just the statement.

### 4. Verify no drift

Prove the change landed everywhere and the old form is gone:

- `grep` the repo (and memory dir) for the **old** form — expect zero hits outside `revere_portal_CLAUDE.md` (the frozen reference artifact — never edit it).
- Check the **cross-file invariants** that must agree exactly:
  - Banner set + count identical across `response_templates.md`, `phase_project.md`, and `CLAUDE.md`.
  - Phase-number grammar and examples identical across `TERMINOLOGY.md`, `phase-tracker`, `phase_project.md`, `CLAUDE.md`.
  - Appendability present in `TERMINOLOGY.md`, `phase-audit`, `phase-decompose`, the memory, `CLAUDE.md`.
  - Index "bottom = newest" wording consistent across `phase-tracker`, `phase-recap`, the `phase_index.md` asset, `phase_project.md`, `CLAUDE.md`.
- If the change added/removed a skill or banner, re-count **everywhere a count is stated in prose** — e.g. the "…labeled response modes" line and the "…skills" line in `CLAUDE.md` and the template headers. These spelled-out numbers are the most common drift: they read fine in isolation but silently contradict the list they head.

### 5. Override the installed copies

The harness loads `.claude/skills/<name>/`, not the working dirs. Push the changed working skills in and reload:

```bash
cd /home/aksel/Documents/phase_skills
for s in <changed-skill-dirs>; do rm -rf ".claude/skills/$s" && cp -R "$s" ".claude/skills/$s"; done
```

Then run `/reload-skills`. (Only the skills you changed need overriding; canonical docs and the charter aren't loaded as skills.)

### 6. Report

List what changed, grouped by convention, and name every file touched (including memory + installed copies). Flag anything you *chose not to* change and why — e.g. an intentional wording difference — so the user can spot an accidental omission.

## What this skill should not do

- Do not edit `revere_portal_CLAUDE.md` — it is a frozen reference artifact and its old conventions are intentional.
- Do not treat propagation as literal find-and-replace — follow the concept through each file's own phrasing and reasoning.
- Do not stop at the canonical docs; the embedded skill copies are what make a skill self-contained, so they must match.
- Do not forget the two non-obvious locations: the memory and the installed `.claude/skills/` copies.
- Do not run as a phase; amending the suite is repo maintenance, not tracked phase work.
