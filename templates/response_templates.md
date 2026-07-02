# Phase Response Templates

Consistent formats for each kind of turn in (or around) the phase workflow. **Every one opens with a labeled header banner** naming the response type and the phase it relates to, so the user can tell at a glance what mode we are in and which phase is in play.

Conventions:
- The banner is the first line. Format: `### <emoji> <TYPE> · <phase anchor>`.
- Capitalize **Major / Minor / Patch** per [TERMINOLOGY.md](../TERMINOLOGY.md).
- Keep bodies tight. These are interaction frames, not essays.
- Fill `<…>` placeholders; drop rows that don't apply.

The eight types:

| Type | When | Banner |
|---|---|---|
| Plan Confirmation | Plan written, asking "is the plan right?" | 🟦 PLAN CONFIRMATION |
| Development Approval | Plan locked, asking "shall I start coding?" | 🟩 DEVELOPMENT APPROVAL |
| Phase Done / What's Next | Phase finished, summarizing + proposing next | 🏁 PHASE DONE |
| Fix | A corrective change | 🔧 FIX |
| Outside Question | A work/codebase question outside this phase's scope | ❓ OUTSIDE QUESTION |
| Tangent | Discussion unrelated to the phase | 💬 TANGENT |
| Loop Progress | One iteration of a phase-loop just finished | 🔁 PHASE LOOP |
| Phase Recap | A scoped recap report (see `recap_template.md`) | 🧭 PHASE RECAP |

---

## 🟦 Plan Confirmation

> The plan file is written. We are at the **first gate**: confirm the plan is *correct* before anything else. No code is written yet.

```
### 🟦 PLAN CONFIRMATION · Phase <NUM> — <name>

**Plan file:** development/phase_log/phase_<NUM>_plan.md

**In one paragraph:** <what this phase will do and why>

**In scope:** <bullet / short list>
**Out of scope:** <bullet / short list — what is deliberately deferred>

**Confirm this plan is right, or tell me what to change.** I won't touch code until you approve it.
```

---

## 🟩 Development Approval

> The plan is confirmed. We are at the **second gate**: approval to begin implementation. Branch and worktree are already in place.

```
### 🟩 DEVELOPMENT APPROVAL · Phase <NUM> — <name>

**Plan:** confirmed ✓   **Branch:** phase-<MAJOR.MINOR>-<slug>   **Worktree:** .claude/worktrees/phase-<MAJOR.MINOR>-<slug>

**About to build:**
- <deliverable 1>
- <deliverable 2>

**Approve to start development?** (yes / adjust)
```

---

## 🏁 Phase Done / What's Next

> The work is complete (or explicitly stopped). Summarize what shipped, confirm the close-out steps, and propose the next phase.

```
### 🏁 PHASE DONE · Phase <NUM> — <name> · <Completed | Stopped>

**Shipped:**
- <what now works that didn't before>

**Close-out:** log written ✓ · index updated ✓ · committed ✓ · PR opened <link / pending>
**Scoped tests:** <result, e.g. 412 passed>
**Deferred / limitations:** <what's still gap-shaped, or "none">

**What's next:** <proposed next Minor / Patch and why>

Anything missing before I close this phase?
```

---

## 🔧 Fix

> A corrective change. Decide first whether it's a **Patch** on the current Minor (commit-worthy, gets a number) or **trivial** (no phase). State which.

```
### 🔧 FIX · Phase <NUM> <or: trivial — no phase>

**Problem:** <what's wrong>
**Fix:** <what changed>
**Classification:** <Patch <NUM> on Minor X.Y | trivial, no phase tracking>
**Verified:** <scoped tests / manual check>
```

---

## ❓ Outside Question

> A real question about the project or codebase, but **outside the current phase's execution**. Answer it, then point back to the phase. No phase files change.

```
### ❓ OUTSIDE QUESTION · (current phase: <NUM>)

<the answer>

—
*Outside Phase <NUM>'s scope; nothing in the phase was changed. Back to it whenever you're ready.*
```

---

## 💬 Tangent

> Discussion **unrelated** to the phase (vs. an Outside Question, which is still about the work). The current phase is paused and untouched.

```
### 💬 TANGENT · (paused: Phase <NUM>)

<the discussion>

—
*We're off the phase track — Phase <NUM> is paused and untouched. Say "back to the phase" to resume.*
```

---

## 🔁 Loop Progress

> Used by `phase-loop` after each iteration to show how far the umbrella has progressed and what's next.

```
### 🔁 PHASE LOOP · Major <N> · <done>/<total> phases · cadence: <Autonomous | Checkpoint per Minor | Step>

**Just shipped:** Phase <NUM> — <name>
**Next:** Phase <NUM> — <name>   <!-- or: none — effort complete -->
```
