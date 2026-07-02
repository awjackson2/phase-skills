---
name: phase-audit
description: Use to check the integrity of the phase log and the workflow's git state. Trigger when the user asks to "audit the phases", "check the phase log", "is the phase log healthy", "phase doctor", "validate the phases", "any drift?", or before relying on the log for a release or a recap. Reports drift between plans, logs, the index, design docs, and git (missing logs, broken index links, dangling worktrees, stale design-doc sync, numbering gaps), most-severe first, then offers to fix what's safely fixable via a docs-lane PR. Read-only by default.
---

# Phase Audit

This skill verifies that the artifacts the rest of the workflow trusts are actually consistent: that the index matches the logs, the logs match the files they cite, design docs are in sync, and git has no leftover branches/worktrees. Everything downstream (`phase-recap`, `phase-loop`, `phase-decompose`) assumes these hold — this skill is what guards that assumption.

It is **not a phase** (no plan/log for running it). It is read-only by default; any fixes it applies are a docs-lane change (branch + PR), never a direct commit to the default branch.

It produces a report — the 🩺 banner below.

## Appendability is not a defect

Before listing checks: **never flag later additions to an old theme as drift.** A `3.8.0` logged long after Major 3 "finished", or a `3.4.3` Patch on a months-old Minor, is the workflow working *correctly* (see [TERMINOLOGY.md → Core principle](../../../TERMINOLOGY.md)). Numbering gaps and out-of-numeric-order index lines are expected, not errors. Audit checks *consistency*, not *recency* or *numeric tidiness*.

## What to check

Run these against `development/phase_log/` and git. Order findings most-severe first.

**Integrity (high severity — the log is lying):**
1. **Orphan plan.** A `phase_<NUM>_plan.md` with no matching log, where the index does **not** annotate it as open/partial/planned/abandoned. Either it's an undocumented in-flight phase or a forgotten one. (A plan-with-no-log that the index *does* annotate is fine — that's a known open phase.)
2. **Unlogged-but-merged work.** A phase whose code is on the default branch but has no log / no index entry.
3. **Broken index links.** An index entry whose `[plan]`/`[log]` link points at a file that doesn't exist.
4. **Missing index entry.** A `phase_<NUM>_log.md` that exists but has no line in the index.
5. **Cited file missing.** A log's "Artifacts Produced" (or a plan's Confirmed Starting Point) citing a path that doesn't exist in the repo. Best-effort; report as a warning, since paths may have been moved by later phases.

**Sync (medium severity — curated state is stale):**
6. **Stale design docs.** A `Last synced: Phase X.Y.Z` marker that is behind the latest phase known to have touched that doc. Report each living design doc's marker against the newest index phase; flag suspicious lag rather than asserting staleness you can't prove.
7. **Umbrella vs index.** For any `MAJOR.0.0` umbrella, roadmap items checked off but absent from the index, or shipped (in the index) but still unchecked. (Unchecked-but-shipped is low severity — the checklist is advisory per `phase-loop`.)

**Git hygiene (medium severity — leftovers):**
8. **Dangling worktrees.** `git worktree list` entries for phases that have already merged/wrapped. Phase worktrees live under `.claude/worktrees/`; also flag any phase worktree created **outside** that directory as a convention violation.
9. **Stale phase branches.** `phase-*` branches already merged into the default branch and never deleted, or a `phase-*` branch with no corresponding plan file.
10. **Uncommitted phase work.** A dirty working tree inside a phase worktree (work that should be committed or stashed).

**Scaffolding (low severity):**
11. **Missing templates.** `phase_plan_template.md`, `phase_log_template.md`, or `phase_index.md` absent from `development/phase_log/`.
12. **Numbering note.** List numbering gaps (e.g. no `5.9` between `5.8` and `5.11`) **for the user to confirm are intentional reserved slots** — not as errors. Do not "fix" gaps.

Use read-only git for 8–10 (`git worktree list`, `git branch --merged`, `git status`). This is the one phase skill that reads git — integrity is its whole job.

## Report format

### 🩺 PHASE AUDIT

```
### 🩺 PHASE AUDIT · <N> findings (<H> high · <M> medium · <L> low)

**HIGH**
- <[file:line] one-line finding> — <suggested fix>

**MEDIUM**
- <finding> — <fix>

**LOW / confirm**
- <finding> — <ask / fix>

**Clean:** <checks that passed, one line — e.g. "index links resolve; no dangling worktrees">
```

If everything passes, say so plainly — a clean audit is a valid, useful result.

## Fixing

Audit is read-only until the user opts in. When they do:

- Apply only the **safe, mechanical** fixes: regenerate a missing index entry from an existing log, fix a broken link, remove a dangling worktree, delete a merged branch, refresh an umbrella checkbox, bump a `Last synced` marker after re-syncing the doc.
- Do **not** invent a missing log or plan from nothing — surface the orphan and ask; the human knows whether it shipped.
- Bundle the doc/index fixes into one docs-lane branch (`chore/phase-audit-<date>` or `docs/...`) and open a PR — never commit straight to the default branch. Removing worktrees/branches is local and needs no PR.

## When to trigger

- Explicit: "audit the phases", "phase doctor", "is the log healthy", "any drift".
- Before a recap or release where the log must be trusted.
- After a messy session (interrupted phases, manual git surgery, several branches in flight).
- Periodically on a long-running project.

## What this skill should not do

- Do not treat appendability — late additions to old themes, numbering gaps, non-numeric index order — as drift. Those are correct by design.
- Do not read source code to "verify" a phase's claims; it checks artifact consistency, not implementation correctness (that's `/code-review` or `phase-review`).
- Do not fix anything without the user's go-ahead, and never commit fixes directly to the default branch.
- Do not run as a phase; it needs no plan or log.
