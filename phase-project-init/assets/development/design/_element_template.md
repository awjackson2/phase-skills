---
type: Design Template
title: Design Concept Template
description: The shape every curated current-state design concept in this project follows.
tags: [design, template, current-state]
---

# Design Concept Template

Copy the fenced block below into `development/design/<name>.md`, remove the
fences, and replace every placeholder. Delete these instructions from the copy.

A design concept describes how something works **now**. It is not a history, a
plan, or a decision record — the phase log holds those. When behavior changes,
update the concept in the same commit as the phase log that changed it, and
stamp `Last synced`.

Add the new concept to [`index.md`](index.md).

```markdown
---
type: Design Concept
title: <Human-readable name>
description: <One sentence stating what this part of the system is responsible for.>
tags: [<area>, <capability>]
---

# <Human-readable name>

Last synced: Phase <X.Y.Z> (<YYYY-MM-DD>)

## Responsibility

<What this element owns, in two or three sentences. Say what it is accountable
for, and name what it deliberately does not do.>

## How it works

<The current mechanism, at the altitude a new contributor needs. Reference real
paths and identifiers so a reader can find the code.>

## Interfaces

<What it exposes, what it depends on, and the shape of each boundary.>

## Constraints and invariants

<Rules that must hold. State the consequence of breaking each one — a rule
without a consequence reads as a preference and gets ignored.>

## Known gaps

<What is missing, deferred, or provisional. Be honest here; this section is the
reason the document stays trustworthy.>

## Phase history

| Phase | Change |
|---|---|
| <X.Y.Z> | <What that phase changed about this element.> |
```
