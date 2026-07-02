<!--
PORTABLE PHASE WORKFLOW CHARTER.

Copy everything below the line into any project's CLAUDE.md (fresh or existing) to
make Claude follow the phase-log workflow. It is self-sufficient: it drives the
behavior even if the phase-* skills aren't installed. If they ARE installed, the
"Skills" section says which to use when, and they add the full detail.

Keep this block in sync with TERMINOLOGY.md and the templates/ when conventions change.
-->

---

## Phase Workflow

This project tracks every meaningful development effort as a numbered **phase**. Plans are written before code, logs after, and both live under `development/phase_log/`. Trivial work — single-line fixes, typos, doc tweaks, exploratory reading — needs no phase; anything commit-worthy that spans multiple files or shifts behavior does.

### Phase numbers — `MAJOR.MINOR.PATCH`

Digits only, never a letter suffix (`9.4.1`, not `9.4.1A`). The levels nest:

- **Major** — a milestone / major area of work.
- **Minor** — a feature or self-contained effort. **One branch, one worktree, one PR per Minor.**
- **Patch** — an iteration / fix / sub-step within a Minor. **A commit on the Minor's branch** — no separate branch, worktree, or PR. The first version of a Minor is `MAJOR.MINOR.0`.

Always **capitalize Major / Minor / Patch** when they name a phase. Set a new number by **clustering near the theme it connects to** (notification work near Minor 8.2 → 8.2.1, 8.2.2…), else take the next free Minor; bump Major only for a new milestone.

**Phases are always appendable.** A Major is never "sealed." Related future work is numbered *near its theme* — a new Minor on an old Major, a new Patch on an old Minor — so a change stays close to the history that explains it. There is no closeout/milestone step.

### The phase cycle

Every phase runs the same pipeline, inside a git worktree on its branch:

prompt → discuss/refine → pick the number → cut the `phase-<MAJOR.MINOR>-slug` branch + worktree → write `phase_<NUM>_plan.md` → **🟦 confirm the plan** → **🟩 approve development** → implement → run scoped tests → summarize & confirm → write `phase_<NUM>_log.md` → append to `phase_index.md` → sync any living design docs → commit (one atomic unit) → open the PR when the Minor wraps.

"**Start the phase**" / "**close the phase**" mean the whole opening / closing sequence, not one step.

**Model tip (optional).** Planning benefits from stronger reasoning; implementation doesn't. A natural (optional) point to switch models: a stronger-reasoning model (e.g. `/model opus`) before writing the plan, back to a faster one (e.g. `/model sonnet`) after Development Approval, before implementation starts.

### Where state lives

- `development/phase_log/phase_<NUM>_plan.md` — written before the work (the contract).
- `development/phase_log/phase_<NUM>_log.md` — written after (the immutable history; when it and the plan disagree, the log wins).
- `development/phase_log/phase_index.md` — the timeline, **appended chronologically (bottom = newest), not numeric**. A high number can sit above a lower one logged later.
- Plan/log templates live beside them. A `MAJOR.0.0` plan is an umbrella/roadmap for a milestone.

### Git rules

- **Never develop on the default branch** — it's protected; changes reach it only through merged PRs.
- Cut each Minor's branch + worktree from an up-to-date default branch; **create the worktree under `.claude/worktrees/<branch-name>` — never anywhere else** (keep `.claude/worktrees/` gitignored). Do all work in the worktree. Patches commit onto the Minor's branch.
- Commit with **explicit file lists** (never `git add -A`), a `Phase X.Y.Z:` message, and a `Co-Authored-By:` trailer.
- One PR per Minor (wait for its last planned Patch). After it merges, remove the worktree; delete the branch.
- Doc-only changes (phase log, design docs, this charter) use a short `docs/<topic>` branch + PR — still never a direct commit to the default branch.

### Response modes

When in (or stepping away from) the workflow, open the turn with a labeled banner so the mode is always clear:

- **🟦 Plan Confirmation** — "is the plan right?" (no code yet)
- **🟩 Development Approval** — "shall I start coding?"
- **🏁 Phase Done** — phase complete; summary + what's next
- **🔧 Fix** — a corrective change; classify it as a Patch or as trivial
- **❓ Outside Question** — a work/codebase question outside the current phase's scope
- **💬 Tangent** — discussion unrelated to the phase (current phase paused, untouched)
- **🔁 Loop Progress** — one umbrella iteration finished (when looping)
- **🧭 Phase Recap** — a scoped report of the phases preceding the current one

### Skills (if installed)

- **phase-project-init** — set up a fresh/empty repo for this workflow. **phase-adopt** — retrofit it into an existing repo.
- **phase-decompose** — chunk a large goal into a `MAJOR.0.0` umbrella roadmap. **phase-loop** — run that umbrella to completion by looping cycles (and resume a half-finished effort).
- **phase-tracker** — write a phase's plan/log/index and run one cycle. **phase-recap** — load current state (ambient) or print a scoped recap report.
- **phase-audit** — check the phase log + git state for drift.

If the skills aren't installed, follow this charter directly.
