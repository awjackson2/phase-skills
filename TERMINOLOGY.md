# Phase Workflow Terminology

Canonical glossary for the phase workflow. This is the source of truth — every phase skill and every conversation about phases should use these terms exactly. When a skill's wording disagrees with this file, this file wins.

## The phase hierarchy

A phase identifier is the numeric dotted form `MAJOR.MINOR.PATCH` (digits only — never a letter suffix like `5.3.2A`). The three levels nest:

```
Major 5                     ← a milestone / major area of work
├── Minor 5.1               ← a feature / self-contained effort (own branch, worktree, PR)
│   └── Patch 5.1.1         ← an iteration / fix / sub-step (a commit on the Minor's branch)
├── Minor 5.2
└── Minor 5.3
    ├── Patch 5.3.1
    └── Patch 5.3.2
```

- A **Major** contains Minors. A **Minor** contains Patches. The first version of any Minor is `MAJOR.MINOR.0`.

## Core principle — phases are always appendable

The phase log is never "sealed." A Major is **never closed off**. Work that belongs to an existing theme is always **appended near its history** by reusing that theme's numbers — a new Minor on an old Major (`3.8.0` long after Major 3 seemed "done"), or a new Patch on an old Minor (`3.4.3` after `3.4.2` shipped months ago) — rather than being pushed to a distant new number just because a Major looked finished. There is deliberately **no milestone/closeout step** that would freeze a Major, because freezing it would force future related work away from the history that explains it.

This is *why* the numbering clusters by theme (see Step 1 of `phase-tracker`): keeping a change numerically close to its theme keeps it physically close to the plan/log/decisions that motivate it. Appendability is about numbering near the theme; the index still appends chronologically at the bottom, so a freshly-logged `3.8.0` can sit at the bottom of the index while conceptually belonging next to old Major 3 work.

## Core terms

- **Phase** — the generic word for any unit of tracked work. Unqualified, "phase" can mean a Major, a Minor, or a Patch; resolve which from context.

- **Major** — *(noun, always capitalized)* the Major phase — the first digit. A milestone or major area of work. "Major 5" means the phase `5.x.x` and everything under it.

- **Minor** — *(noun, always capitalized)* the Minor phase — the second digit. A feature or self-contained effort within a Major. Each Minor gets its own branch, worktree, and PR. "Minor 5.3" means `5.3.x`.

- **Patch** — *(noun, always capitalized)* the Patch phase — the third digit. An iteration, fix, or sub-step within a Minor, committed onto the Minor's branch (no separate branch/worktree/PR). "Patch 5.3.2".

> **Capitalization rule.** Always capitalize **Major**, **Minor**, and **Patch** when they refer to phases, so it is unambiguous we mean a phase and not an ordinary word ("a minor tweak", "a patch to the file"). Lowercase only when using the everyday English meaning.

## Process terms

- **Phase cycle** — the full pipeline a phase runs through, start to finish: new worktree + branch + phase plan → implement → phase log + commit → PR (or branch stack).

- **Start the phase** — begin the **entire** phase process, not a single step: determine the number → cut the branch → create the worktree under `.claude/worktrees/` → enter them → write the plan → get approval → implement → summarize → write the log → sync docs → commit → PR. When the user says "start the phase," run the whole opening sequence.

- **Close the phase** — complete the **entire** closing process, not a single step: summarize the work → get confirmation → write the log → sync design docs → update the index → commit → open the PR. When the user says "close the phase," run the whole closing sequence.

## Phase recap (scoped)

A **phase recap** loads and reports the phases that precede the current one **within the current phase's scope**. The scope is set by the level the recap is called at:

| Called at… | Reports briefs on… |
|---|---|
| **Major N** | every Major up to and including N — Major 1, Major 2, … Major N (top-level briefs, one per Major) |
| **Minor X.Y** | every Minor and Patch inside Major X that precedes X.Y |
| **Patch X.Y.Z** | every Patch inside Minor X.Y that precedes X.Y.Z (including the base X.Y.0) |

Worked examples:

- Recap at **Major 5** → briefs on Major 1, Major 2, Major 3, Major 4, Major 5.
- Recap at **Minor 5.4** → 5.3.2, 5.3.1, 5.3, 5.2, 5.1.1, 5.1 (all Minors + Patches under Major 5 before 5.4).
- Recap at **Patch 5.3.2** → 5.3.1, 5.3 (all Patches under Minor 5.3 before 5.3.2).

Recaps are reported **most-recent-first (descending)** so the closest context is at the top. The output uses the recap template in [templates/recap_template.md](templates/recap_template.md).

This scoped recap is the *explicit, report-producing* mode of the `phase-recap` skill (the user asks for it by phase level). It is distinct from the ambient session-start recap, which silently loads general state into working memory.

## Response modes

Every assistant turn that is part of (or deliberately steps away from) the phase workflow opens with a labeled header so the user always knows what mode we are in — confirming a plan, asking to start development, closing a phase, fixing, or off on a tangent. The labeled formats live in [templates/response_templates.md](templates/response_templates.md).
