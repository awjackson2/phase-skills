---
name: phase-loop
description: Use to drive a large multi-step effort to completion by running phase cycles continuously. Trigger when the user hands over a big plan and wants it chunked into phases and executed end-to-end ("loop through this plan", "build this whole thing", "run phase cycles until done", "phase loop"), OR when the user wants to CONTINUE a half-finished effort and complete all remaining phases ("pick up where we left off", "finish the rest of this", "continue from 8.5.1"). Orchestrates phase-tracker and phase-recap: it builds (or recovers) an umbrella plan that chunks the work into Minors and Patches, then loops the phase cycle — recap, plan, implement, log, commit, PR — until every phase ships. Uses Claude's /loop to self-pace across turns and sessions.
---

# Phase Loop

This skill drives a whole effort to completion by running **phase cycles** back-to-back. It does not implement work directly — it **orchestrates** the other phase skills: `phase-recap` to re-ground state at the start of every iteration, and `phase-tracker` to run each phase cycle (plan → approval → implement → log → commit → PR).

It is **not itself a phase**. It is a controller that creates and sequences phases. Terminology (Major / Minor / Patch, the phase cycle) follows [TERMINOLOGY.md](../../../TERMINOLOGY.md).

Two modes:

- **Mode A — Start:** the user hands over a large plan. Build an umbrella plan that chunks it into Minors and Patches, get it approved once, then loop until done.
- **Mode B — Continue:** an effort is half-built (e.g. at Patch 8.5.1). Recover the umbrella, figure out what remains, and loop the remainder to completion.

## The umbrella plan

Every loop is driven by one **umbrella plan** — the `MAJOR.0.0` roadmap plan for the effort (e.g. `phase_8.0.0_plan.md`). Beyond the normal plan sections, it carries a **roadmap checklist**: every Minor and Patch the effort will produce, in order.

```
## Roadmap checklist
- [x] 8.1.0 — Data model + migrations        (shipped)
- [x] 8.1.1 — migration fixups               (shipped)
- [ ] 8.2.0 — API endpoints                  (next)
- [ ] 8.3.0 — Frontend wiring
- [ ] 8.4.0 — Auth + sessions
```

**Where it lives.** The umbrella is a planning doc, not a coding phase. Create it on a docs-lane branch (`docs/<major>-umbrella`) and merge it to the default branch via a quick PR **before** looping, so every later phase branch starts from the same approved roadmap. Do not author it on a feature branch — the checklist would then churn across branches and conflict at merge.

**Progress is read from `phase_index.md`, not the checkboxes.** A phase is "done" when its log exists and it appears in the index. At the start of every iteration the recap derives the remaining work by diffing the roadmap against the index, so the loop never depends on a checkbox being current. Treat the checklist as an **advisory mirror**: refresh its boxes in batches (once at the effort's end, or alongside the next Minor's merge) rather than as a mandatory per-phase edit on the default branch. This keeps the live tracker from generating a stream of one-line commits and cross-branch conflicts.

## Cadence — how much to pause

Confirm the cadence with the user **before** looping. The umbrella-plan approval is the one big gate; the cadence sets how often the loop pauses after that:

- **Autonomous** *(default)* — no per-phase gates. The umbrella approval stands in for each sub-phase's 🟦 plan-confirmation and 🟩 development-approval (the plan file is still written first — plan before code always holds). The loop pauses only on a blocker (see Failure handling).
- **Checkpoint per Minor** — run a Minor's phases autonomously, then pause for approval at each Minor boundary before starting the next feature.
- **Step** — pause at every phase's 🟦 plan confirmation. The loop just sequences; the user approves each one.

State the chosen cadence at the start so the user knows when to expect a pause.

## Mode A: Start from a large plan

1. **Recap first.** Run `phase-recap` (ambient) so numbering and existing work are known. Pick the effort's Major (next free Major for a new milestone, or an existing one the user names).
2. **Chunk the plan with `phase-decompose`.** Defer to that skill to break the goal into tiny, independently-testable Minors (and Patches) against its quality bar — dependency-ordered, risk-tagged, right-sized, with numbering room left to append. It produces the umbrella; do not improvise the chunking here.
3. **The umbrella plan** lives at `development/phase_log/phase_<MAJOR>.0.0_plan.md` with the roadmap checklist, authored on a `docs/<major>-umbrella` branch (by `phase-decompose`).
4. **Confirm the umbrella with the user** (🟦 on the umbrella), confirm the cadence and the branch strategy (below), then **merge the umbrella to the default branch** (docs-lane PR) so every phase branch starts from the approved roadmap. This is the single big approval for autonomous mode.
5. **Enter the loop** (below).

## Mode B: Continue a half-finished effort

1. **Scoped recap.** Run `phase-recap` scoped to the effort's Major to load everything done so far, including any partial phase (a plan with no log).
2. **Recover the umbrella.** If a `MAJOR.0.0` umbrella plan exists, read its roadmap. If it does **not** exist (the effort wasn't loop-driven), reconstruct one: ask the user for the end-goal if it isn't captured, infer the remaining roadmap from the recap, and write the umbrella plan now (docs-lane PR, as in Mode A).
3. **Locate the resume point.** Diff the roadmap against `phase_index.md` for what has shipped, and check for an open/partial phase (a plan with no log). The resume point is: finish the partial phase first if one exists, then the next roadmap item not in the index. (Example: shipped through 8.5.0, partial at 8.5.1 → finish 8.5.1, then continue 8.6.0…)
4. **Confirm the remaining roadmap and cadence** with the user, then **enter the loop**.

## The loop body — one iteration = one phase cycle

Each iteration re-grounds itself so it is resumable across turns and fresh sessions:

1. **Recap.** Run `phase-recap` (scoped to the Major) to reload current state. Do not trust stale context from a previous iteration. Derive remaining work by diffing the umbrella roadmap against `phase_index.md` — the index is the source of truth for what has shipped, not the checklist boxes.
2. **Pick the next phase.** The first roadmap item not yet in the index, or an unfinished partial phase. Determine its number (Minor vs Patch) per `phase-tracker` numbering.
3. **Run the phase cycle** via `phase-tracker`: cut the branch + worktree under `.claude/worktrees/` (new Minor) or continue on the Minor's branch (Patch) → write the plan → (gates per cadence) → implement → run scoped tests → write the log → append to the index → sync design docs → commit → open the PR (or stack — see branch strategy).
4. **Record progress.** The phase's index entry (written by `phase-tracker`) is what marks it done. Refresh the umbrella checkbox only opportunistically — batched with a Minor merge or at the effort's end — never as a separate per-phase commit on the default branch.
5. **Emit loop progress** and decide (the `<done>/<total>` count comes from the index, not the boxes):

```
### 🔁 PHASE LOOP · Major <N> · <done>/<total> phases · cadence: <mode>
**Just shipped:** Phase <NUM> — <name>
**Next:** Phase <NUM> — <name>   <!-- or: none — effort complete -->
```

6. **Continue or stop.** If unchecked items remain, continue to the next iteration. If all boxes are checked, stop the loop and give the final report.

## Driving it with /loop

Run the iterations with Claude's `/loop`, self-paced (no interval), so the loop continues across turns and survives context resets — each iteration rebuilds context via `phase-recap`. The loop's repeated instruction is "advance the umbrella by one phase cycle, then check whether any roadmap items remain." Terminate the loop when the umbrella checklist is fully shipped (or the user stops it). Because every iteration starts with a recap and reads the checklist, a half-finished loop can always be resumed later by re-entering this skill in Mode B.

## Branch strategy

Confirm one at the start:

- **PR per Minor** *(default)* — each Minor opens and merges its own PR (per `phase-tracker`). Best when features are independent and can deploy as they land.
- **Stacked effort** — cut each Minor's branch from the previous Minor's tip and open one consolidated PR at the end (per `phase-tracker`'s "Stacked multi-phase efforts"). Best when the Minors build on each other and should land as a unit.

## Failure handling

The loop is not allowed to barrel past problems:

- **Scoped tests fail** or implementation hits a blocker → stop the loop, surface it (🔧 Fix if it's a quick correction, otherwise a plain pause), and wait for the user. Do not start the next phase on top of a broken one.
- **Ambiguity** the umbrella didn't resolve (a design decision, a missing requirement) → pause and ask, even in autonomous cadence.
- **Scope drift** — if a phase turns out bigger than its roadmap slot, apply `phase-tracker` Mode 3: split it into more Patches/Minors and update the umbrella checklist rather than silently growing the phase.

## Final report

When the checklist is fully shipped, stop and report: the Major and its name, the count of Minors/Patches shipped, the PRs opened/merged (or the consolidated PR), anything deferred to a future Major, and the suggested next step.

## What this skill should not do

- Do not implement work directly or skip `phase-tracker` — every phase still gets its own plan, log, index entry, and commit. The loop sequences phases; it does not bypass the cycle.
- Do not skip the per-iteration `phase-recap` — it is what makes the loop resumable and keeps it from acting on stale state.
- Do not treat the loop controller as a phase (no plan/log for the loop itself; the umbrella `MAJOR.0.0` plan is the closest artifact).
- Do not continue past a failing phase or an unresolved ambiguity.
- Do not invent roadmap scope the user didn't approve — chunk what they gave you; surface anything extra as a proposed addition to the umbrella.
