---
type: Knowledge Profile
title: Knowledge Format Profile
description: The metadata, identity, relationship, and validation contract every concept in this project's knowledge bundle must satisfy.
tags: [okf, schema, metadata, provenance, phase-history]
---

# Knowledge Format Profile

This profile is the contract `scripts/okf/manage_bundle.py` enforces. Edit it
and the validator together; a rule that lives only in prose is a rule that
drifts.

## Source hierarchy

1. `development/design/` is the curated current state of the system. A design
   concept describes how something works *now*.
2. `development/phase_log/` is the chronological record of intended and shipped
   change. A log wins over its plan when the two disagree.
3. `scripts/okf/` supplies this schema, the validator, and the generated graph.
   It organizes the layers above without replacing them.

`development/` is the bundle root and holds **only concepts**. Evidence and
analysis — audits, triage notes, scratch research, meeting records — may
support a claim but never become current-state authority, so they live outside
the bundle by construction rather than by exclusion rule. The validator fails on
any unexpected entry in `development/`, which is what keeps the directory
readable without consulting `.okfignore`.

## Required front matter

Every concept carries YAML front matter delimited by `---`:

| Field | Shape | Rule |
|---|---|---|
| `type` | non-empty string | Concept class from the vocabulary below. |
| `title` | non-empty string | Human-readable name, not a filename. |
| `description` | non-empty string | One sentence stating the concept's responsibility. |
| `tags` | non-empty list | Stable discovery terms, lowercase kebab-case where practical. |

Phase records carry four more:

| Field | Shape | Rule |
|---|---|---|
| `phase` | quoted dotted string | Must equal the number in the filename. |
| `phase_status` | controlled | `planned`, `active`, `paused`, `completed`, `stopped`, `abandoned`. |
| `delivery_status` | controlled | `none`, `partial`, `complete`, `unknown`. |
| `recorded_on` | quoted ISO date | Plan draft date, or log completion date. |

Front matter is parsed by a deliberately small stdlib parser: scalars,
inline lists (`[a, b]`), and block lists of `- item`. Keep it boring so it stays
diffable and needs no dependency.

Reserved files are structure, not concepts, and carry no front matter:
`development/index.md`, `development/log.md`, nested `index.md` files, and
`.okfignore`.

## Concept identity

IDs are derived from paths and never stored in front matter:

| Source | ID rule | Example |
|---|---|---|
| Design concept | `design/<stem>` | `design/authentication` |
| Phase plan | `phase_log/phase_<n>_plan` | `phase_log/phase_2.1.0_plan` |
| Phase log | `phase_log/phase_<n>_log` | `phase_log/phase_2.1.0_log` |
| Schema concept | `okf/<stem>` | `okf/profile` |

Moving a file changes its identity and requires updating every link that
pointed at it. Never renumber old phases to make IDs look uniform.

## Concept vocabulary

- `Design Concept` and `Design Template` for the curated design layer;
- `Phase Plan` and `Phase Log` for phase history;
- `Knowledge Profile` for this contract.

Add types as the project grows, and record them here when you do.

## Relationships

Relationships are ordinary relative Markdown links. A link is both navigable
documentation and a graph edge when both endpoints are concepts.

Every phase record ends with exactly one `## OKF relationships` footer, whose
entries use controlled labels:

- **Plans** — `Builds on`, `Superseded by`, `Continued by`,
  `Intended design impact`, `Intended knowledge impact`, `Evidence`.
  At least one *Intended* impact label is required.
- **Logs** — `Plan`, `Builds on`, `Supersedes`, `Superseded by`,
  `Continued by`, `Verified design impact`, `Verified knowledge impact`,
  `Evidence`. At least one *Verified* impact label is required, and the footer
  must link its own plan under `Plan`.

A plan and its log must agree on `phase`, `phase_status`, and
`delivery_status`. Because a log is written after the fact, writing one also
means updating its plan's front-matter status to the reviewed outcome — the
plan's *narrative* still records the state in which it was authored, and that
is intentional.

Do not infer a relationship from phase-number adjacency, filename similarity,
or keyword overlap. Link what the work actually touched.

## What the validator checks

- Required front matter on every concept, and the phase fields on phase records.
- `phase` agreeing with the filename; plan/log pairs agreeing on status.
- Exactly one relationship footer, using only allowed labels, carrying an
  impact label and at least one link; logs linking their plan.
- Broken local links — in full for design concepts, and in the **footer only**
  for phase records. A narrative legitimately references source paths and prior
  states that move or vanish; failing a record for that would turn history into
  a maintenance burden.
- Unexpected entries directly inside `development/`.
- `.okfignore` matching the boundary the validator implements.

Run it at every phase boundary:

```bash
python3 scripts/okf/manage_bundle.py validate
python3 scripts/okf/manage_bundle.py build
```

If your CI skips tests for documentation-only changes, gate the validator on
its own paths (`development/**`, `scripts/okf/**`) rather than on the
code-changed signal — otherwise the one change shape most likely to break the
bundle is the one shape that never checks it.
