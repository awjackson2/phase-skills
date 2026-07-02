---
name: phase-decompose
description: Use to turn a large goal into a well-chunked umbrella roadmap before any phase work starts. Trigger when the user hands over a big feature or project and says "break this down", "decompose this", "chunk this into phases", "plan out this whole thing", "make a roadmap", or when phase-loop needs an umbrella to drive. Produces the MAJOR.0.0 umbrella plan — the ordered roadmap of Minors and Patches — applying a quality bar (tiny independently-testable steps, dependency ordering, risk tags, right-sizing) and leaving numbering room so future work can append near its theme. Hands off to phase-loop (multi-phase) or phase-tracker (single Minor).
---

# Phase Decompose

This skill produces the **umbrella plan** (`MAJOR.0.0`) that `phase-loop` consumes: an ordered roadmap that chunks a large goal into the smallest sensible Minors and Patches. Chunk quality is the single biggest determinant of whether a loop succeeds, so this skill exists to apply a real standard to the breakdown rather than improvising it inline.

**Model tip (optional).** This skill is planning-only — a good candidate for a stronger-reasoning model (e.g. `/model opus`) for the whole session, since chunk quality is what determines whether the loop it feeds succeeds.

It is **not a coding phase**. The umbrella it writes is a planning artifact (`MAJOR.0.0`), created on a `docs/<major>-umbrella` branch and merged to the default branch before looping — the same handling `phase-loop` describes. Terminology follows [TERMINOLOGY.md](../../../TERMINOLOGY.md).

## The quality bar

A good roadmap satisfies all of these:

- **Tiny and independently testable.** Each Minor is one shippable feature that can be implemented *and verified on its own*. If a Minor can't be tested without another unshipped Minor, it's mis-cut.
- **Dependency-ordered.** Sequence so every phase builds only on already-shipped phases. Note each Minor's dependencies explicitly; if two are mutually dependent, they're really one Minor (or the seam is wrong).
- **Vertical over horizontal where possible.** Prefer slices that deliver end-to-end value ("user can log in") over horizontal layers ("all the database models") — vertical slices are testable and shippable; horizontal ones aren't until the last one lands. Use judgment; some foundational work is genuinely horizontal.
- **Right-sized.** A Minor that needs many unrelated changes → split. A "Minor" that's a one-line tweak → it's a Patch, or folds into a neighbor.
- **Risk-tagged.** Mark phases that are uncertain, spiky, or exploratory. Sequence high-risk/high-uncertainty work **early** to de-risk the effort, or flag it for a checkpoint in `phase-loop`.
- **Appendable.** Leave numbering room. Do **not** pack the roadmap so densely that related future work has nowhere to land — the whole system depends on later work being able to append near its theme (see [TERMINOLOGY.md → Core principle](../../../TERMINOLOGY.md)). Reserve Minor slots for foreseeable follow-on themes rather than consuming every number now.

## Procedure

1. **Recap first.** Run `phase-recap` (ambient) so existing numbering, shipped work, and reserved slots are known. Decomposition that ignores current state produces colliding numbers.
2. **Capture the goal.** End-goal, hard constraints, and an explicit **definition of done** for the whole effort. Ask if any are unclear — do not invent scope.
3. **Pick the Major.** The next free Major for a new milestone, or — honoring appendability — an existing Major's theme if the work is a continuation. State which and why.
4. **Draft the roadmap.** List the Minors in dependency order, each with: a one-line goal, its dependencies, a risk tag, and any obvious Patches under it. First version of each Minor is `MAJOR.MINOR.0`.
5. **Pressure-test the chunking** against the quality bar above. For each Minor ask: independently shippable? independently testable? right-sized? correctly ordered? Re-cut anything that fails. This is the step that earns the skill its keep — don't skip it.
6. **Write the umbrella** at `development/phase_log/phase_<MAJOR>.0.0_plan.md` (using the plan template) with the roadmap checklist:

   ```
   ## Roadmap checklist
   - [ ] <MAJOR>.1.0 — <feature>            deps: none        risk: low
   - [ ] <MAJOR>.1.1 — <patch on .1>        deps: .1.0        risk: low
   - [ ] <MAJOR>.2.0 — <feature>            deps: .1.0        risk: med
   ```

   Keep the checklist as the **advisory mirror** `phase-loop` expects — progress is read from `phase_index.md`, not the boxes.
7. **Confirm with the user** (🟦 Plan Confirmation on the umbrella) and confirm the Major number, the cadence, and the branch strategy. Merge the umbrella via its docs-lane PR.
8. **Hand off:**
   - Multi-phase effort → `phase-loop` (it reads this umbrella and loops the cycles).
   - A single Minor → `phase-tracker` directly.

## Re-decomposing mid-effort

If an in-flight effort's roadmap turns out wrong (a Minor too big, a missing dependency, a whole branch of work that's now unnecessary), use this skill to **re-chunk the remaining** roadmap: edit the umbrella's checklist (split/merge/reorder/abandon *unstarted* items only), narrate the change, and re-confirm. Never rewrite the numbers of phases that already shipped — append new Minors/Patches instead, per appendability.

## What this skill should not do

- Do not write any plan/log for the concrete phases — that's `phase-tracker`'s job, one phase at a time, at implementation time. This skill only writes the umbrella.
- Do not implement anything. Decomposition is planning.
- Do not pack the roadmap to the last number; leave room to append.
- Do not invent scope or "while we're at it" Minors the user didn't ask for — surface them as candidates, not commitments.
- Do not renumber shipped phases when re-decomposing; only unstarted items may move.
