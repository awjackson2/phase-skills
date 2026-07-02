---
name: phase-recap
description: Use this skill to load context about the project's state from its phase logs before answering or acting on anything substantial. Runs in two modes — an ambient session recap that silently loads general state into working memory, and an explicit scoped recap that prints a clean report of the phases preceding the current one within the current phase's scope. Trigger when the agent lacks current state — start of a session, "catch me up", "what's the state", "summarize the project", "what's in progress / deferred / placeholder" — or when the user asks for a recap at a phase level ("phase recap Major 5", "recap 5.4", "catch me up on 5.3.2"), and BEFORE proposing scope or drafting a phase plan. Reads only from development/phase_log/, never the codebase.
---

# Phase Recap

This is a **context-loading skill**. Its job is to make the agent better-informed about the project's current state by reading the right phase logs, internalizing what matters, and using that knowledge in everything the agent says or does next.

It runs in two modes:

- **Ambient recap** (Mode A) — silent. Loads general project state into working memory at session start or before substantial work. Output to the user is one or two sentences of confirmation.
- **Scoped recap** (Mode B) — explicit. The user asks for a recap *at a phase level* ("phase recap Major 5", "recap 5.4"). This prints a **clean report** of the phases preceding the anchor, within that anchor's scope, using the recap template.

Terminology (Major / Minor / Patch, capitalized) follows [TERMINOLOGY.md](../../../TERMINOLOGY.md): a **Major** contains Minors, a **Minor** contains Patches. The phase workflow that produces the files this skill reads is owned by `phase-tracker`.

## Where state lives

Everything this skill reads is under `development/phase_log/`. The agent does **not** read source code, configs, or git history while running this skill — those are the wrong source of truth for "what's the project state". The phase log is the curated record; trust it.

The canonical entry point is `development/phase_log/phase_index.md` — the chronological table of contents, one line per phase, with status annotations (✓ shipped, partial, abandoned, planned-not-shipped) and a one-sentence summary. Read it first. Always.

Each phase has up to two files:
- `phase_<NUM>_plan.md` — written before the work; describes intended scope
- `phase_<NUM>_log.md` — written after the work; describes what actually shipped

A phase with a plan but no log is one of: in flight, stopped, partial, or abandoned. A phase with both is shipped. A phase with neither doesn't exist yet — gaps are sometimes intentional (reserved slots or skipped numbers).

## When to trigger

Run **ambient recap (Mode A)** when the agent's understanding of state is stale, missing, or wrong:

1. **New session, non-trivial task** — first substantive request where the agent hasn't read the phase log.
2. **Explicit recap request** — "catch me up", "what's the state", "summarize the project", "what's in progress / deferred / placeholder".
3. **Before drafting a phase plan** — so the plan-author knows what's already in flight, deferred, or covered. Especially important for phase numbering — choosing the right `MAJOR.MINOR.PATCH` depends on which open phases exist.
4. **Before answering "is X done? / do we have X? / should we add X?"** — wrong answers without knowing which phases shipped what.

Run **scoped recap (Mode B)** when the user asks for a recap **at a phase level**:

5. **"phase recap Major 5", "recap 5.4", "catch me up on 5.3.2"** — or any request naming a phase level. Print the scoped report (below).

The skill should **not** run for trivial code-reading, single-file questions the user named, or when the agent already recapped recently in the same session.

## Mode B: the scoped recap report

A scoped recap reports the phases preceding the **anchor** (the phase the user named, or the current in-progress phase) **within the anchor's scope**. The level of the anchor sets the scope:

| Anchor | Reports briefs on… |
|---|---|
| **Major N** | every Major up to and including N (one rolled-up brief per Major) |
| **Minor X.Y** | every Minor and Patch under Major X that precedes X.Y |
| **Patch X.Y.Z** | every Patch under Minor X.Y that precedes X.Y.Z (including the base X.Y.0) |

Worked examples:

- Recap at **Major 5** → Major 1, Major 2, Major 3, Major 4, Major 5.
- Recap at **Minor 5.4** → 5.3.2, 5.3.1, 5.3, 5.2, 5.1.1, 5.1.
- Recap at **Patch 5.3.2** → 5.3.1, 5.3.

### Procedure

1. **Read `phase_index.md`** in full to learn the set and status of all phases.
2. **Fix the anchor** — the phase the user named, else the current in-progress phase.
3. **Compute the in-scope set** from the table above. List it **most-recent-first (descending)** — closest context on top.
   - For a **Major** anchor, summarize each Major at a high level: use its `MAJOR.0.0` umbrella/roadmap plan if one exists, otherwise synthesize one brief from that Major's shipped Minors.
   - For **Minor** and **Patch** anchors, one brief per in-scope phase.
4. **Read each in-scope phase's log** (or its plan if no log exists yet) and pull a brief: what shipped + any carry-forward (decisions, limitations, footguns that bear on the current work).
5. **Emit the report** using the template below. This is the one mode that prints a full report to the user.

### Report format

Follows [templates/recap_template.md](../../../templates/recap_template.md):

```
### 🧭 PHASE RECAP · scope: <Major N | Minor X.Y | Patch X.Y.Z>

**Anchored at:** Phase <NUM> — <name> (<status>)
**Showing:** <count> prior phase(s) in scope, most recent first.

---

#### Phase <NUM> — <Name> · <✓ shipped | partial | stopped | abandoned | planned>
- **Shipped:** <one plain sentence>
- **Carry-forward:** <decisions / limitations / footguns affecting current work — or "none">

<!-- one block per in-scope phase, descending -->

---

**Bottom line:** Last shipped before here is Phase <NUM> (<short scope>). Open / partial in scope: <list or "none">.
```

## Mode A: the ambient recap

The agent does not print a report. It reads the right files and internalizes them.

### Step 1: Read phase_index.md in full

Note especially:
- Which phase is at the bottom (most recently shipped). The index is **chronological (log-written) order, appended at the bottom** — *not* numeric — so the last entry is freshest regardless of number. (A high phase number can appear above a lower one logged later.)
- Any entry annotated strikethrough / "ABANDONED" / "Stopped" / "Partial" / "planned, not yet started".
- Iteration patterns (`5.11.0`, `5.11.1`, `5.11.2` — Patches on a still-open Minor, committed on its branch).
- Gaps in the sequence — scan the *numbers* across the whole list, not physical adjacency.

### Step 2: Read the most-recent 3–5 phase logs

Walk backward from the bottom of the index; read the *log* files (not plans). Skim each for the high-value sections: **Major Additions**, **Major Changes**, **Current Limitations**, **Key Decisions**, **What Comes Next**.

### Step 3: Read every open / partial / abandoned phase, regardless of age

For each phase the index marked Partial / Stopped / Planned-not-shipped / Abandoned, read its plan (and log if one exists). These are the project's known loose ends — what will land but hasn't, what stopped partway, what will never ship (don't propose it), and which numbers are reserved.

### Step 4: Read targeted plans on demand

If the user references a specific phase by number, or the recap surfaces something needing depth, read that specific log. Don't pre-read everything just in case.

### Step 5: Retain as working memory, not user output

Internalize five buckets: **Last shipped** (the "you are here" marker), **In flight / open**, **Footguns and invariants** (the "do not break" rules), **Placeholders and unfinished code**, **Backlog and reserved slots**. Then confirm in one or two sentences:

> Loaded the phase log. Most recent shipped is Phase X.Y.Z (`<short scope>`); open items include Phase A.B.C (planned) and the partial Phase D.E.F. Ready for what you need.

That is the entire user-facing output for Mode A.

## Important reading nuances

- **Plans say what was intended; logs say what shipped.** When they conflict, the log wins. Always.
- **"What Comes Next" sections are dated.** A six-month-old phase listing some feature as "next" doesn't make it the next phase today. Cross-reference the current bottom of the index.
- **Memory files are NOT in scope.** Auto-memory (feedback / project context) is separate and orthogonal. This skill doesn't read or overwrite it. Use both together.
- **Abandoned phases are still important to read.** They tell the agent what *not* to propose.
- **Phase numbering is a strong signal.** Numbers cluster by theme: `5.11.0`, `5.11.1`, `5.11.2` are Patches on the 5.11 Minor, on the `phase-5.11` branch. A live `MAJOR.MINOR.PATCH` series means that Minor is still active; the next *new* feature is more likely the next reserved Minor (5.12) than a distant number.
- **Partial phases are open phases.** A "Stopped (partial)" log means the plan covered surfaces that did not ship; treat those as still in scope under the same number unless the log says otherwise.

## What this skill does NOT do

- It does not read source code. The phase log is the contract.
- It does not run `git log` or any shell commands. The index is the timeline.
- It does not write any files. There is no recap artifact saved anywhere.
- In ambient mode it does not dump a long report; in scoped mode the report *is* the deliverable.
- It does not run as part of phase tracking. Use `phase-tracker` for plan/log generation; this skill loads context that *informs* it.
- It is not a phase itself. Running this skill never requires a phase plan or log.
