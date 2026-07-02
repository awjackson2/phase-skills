<!--
SCOPED PHASE RECAP template — used by the phase-recap skill to produce a clean,
consistent report of the phases preceding the current one, within the current
phase's scope. See TERMINOLOGY.md → "Phase recap (scoped)" for the scope rules.

Fill the placeholders and delete these comments. List entries MOST-RECENT-FIRST
(descending). Keep each brief to a few lines — this is a scan-able report, not a
re-print of the logs.

Scope selector:
  • Recap at Major N    → one brief per Major, 1 … N.
  • Recap at Minor X.Y  → every Minor + Patch under Major X before X.Y.
  • Recap at Patch X.Y.Z→ every Patch under Minor X.Y before X.Y.Z.
-->

### 🧭 PHASE RECAP · scope: <Major N | Minor X.Y | Patch X.Y.Z>

**Anchored at:** Phase <NUM> — <current phase name> (<status: in progress / planned / etc.>)
**Showing:** <count> prior phase(s) in scope, most recent first.

---

#### Phase <NUM> — <Name> · <✓ shipped | partial | stopped | abandoned | planned>
- **Shipped:** <one plain sentence on what this phase delivered>
- **Carry-forward:** <decisions, limitations, or footguns that affect the current work — or "none">

#### Phase <NUM> — <Name> · <status>
- **Shipped:** <…>
- **Carry-forward:** <…>

<!-- repeat one block per in-scope phase, descending -->

---

**Bottom line:** Last shipped before here is Phase <NUM> (<short scope>). Open / partial in scope: <list, or "none">. <One sentence on what this means for the current phase.>
