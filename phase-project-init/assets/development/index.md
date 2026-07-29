---
okf_version: "0.1"
---

# Development Knowledge

This directory is the knowledge bundle for this project, and it holds nothing
else. Everything inside it is a concept:

- [Design catalog](design/) — the curated current state of the system.
- [Phase history](phase_log/phase_index.md) — the chronological record of
  intended and shipped change.
- [Bundle log](log.md) — material changes to this bundle.

The schema and its validator live in [`scripts/okf/`](../scripts/okf/profile.md),
beside each other rather than inside the bundle they describe.

Evidence and analysis — audits, triage notes, scratch research — live outside
this directory. They may support a claim but never become current-state
authority, so they sit outside the bundle by construction rather than by
exclusion rule.

Validate the bundle with:

```bash
python3 scripts/okf/manage_bundle.py validate
```
