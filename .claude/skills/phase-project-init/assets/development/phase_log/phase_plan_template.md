---
type: Phase Plan
title: "Phase X.Y.Z Plan — <Short Descriptive Name>"
description: "Plans the bounded work, evidence, and expected impact for Phase X.Y.Z."
tags:
  - phase-history
  - phase-plan
phase: "X.Y.Z"
phase_status: planned
delivery_status: none
recorded_on: "YYYY-MM-DD"
---

<!--
Phase PLAN template. Copy this file to development/phase_log/phase_<NUM>_plan.md
and fill every section. Written BEFORE any implementation code, confirmed with
the user, then treated as the working contract for the phase. Delete these
comment blocks as you fill the file in. See the phase-tracker skill for the rules.

Replace every placeholder in the front matter, the title, the body, and the
relationship footer. Keep the metadata keys and their order — the plan is a
canonical concept in its own right, so never create a wrapper, a copy, or a
second home for it. This template is the contract; re-check the front matter and
the footer before the phase closes.
-->

# Phase <NUM> — <Short Descriptive Name>

- **Status:** Planned
- **Date drafted:** YYYY-MM-DD

## Purpose

<!-- Why this phase exists — what it proves, de-risks, or unblocks. 2-4 sentences. -->

## Immediate Goal

<!-- Numbered list of concrete, verifiable deliverables. -->

1.
2.

## Confirmed Starting Point

<!-- The relevant current observable state, with real file paths. This is the
baseline the log will compare against — do not skip it. -->

## Scope For This Phase

### In Scope

-

### Explicitly Out Of Scope

<!-- What is intentionally deferred. Be honest; "while we're at it" extensions
belong here unless the user confirmed them into the goal above. -->

-

## Recommended Implementation Direction

<!-- The approach you intend to take and why. -->

## Technical Plan

<!-- The concrete plan, broken out by layer/component when helpful. Reference real
file paths. When stating a rule, follow it with the reasoning. -->

## Test Plan

<!-- The scoped tests this phase's modules need (by file / name / keyword). The
full suite is the PR's CI job, not a step here. -->

## Key Decisions For This Phase

<!-- Calls made up front that later work must respect. -->

## Expected Limitations At End Of Phase

<!-- What will still be gap-shaped when this phase wraps. -->

## What Comes Next

<!-- The likely next phase or follow-up items. -->

## Summary

<!-- Short closing paragraph. -->

## OKF relationships

<!--
Delete rows that do not apply, but keep at least one intended impact. Do not
infer a relationship from phase-number adjacency, filename similarity, or
keyword overlap — link what this work actually touches.
-->

- Builds on: [Phase A.B.C log](phase_A.B.C_log.md) — <the continuity between that outcome and this plan>
- Intended design impact:
  - [Design concept](../design/example.md) — <the current-state concept this phase expects to change>
