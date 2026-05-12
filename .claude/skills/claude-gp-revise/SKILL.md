---
name: claude-gp-revise
description: Revise a closed/awaiting-confirmation GP project by creating a new GP that adds phases addressing user feedback. Mandatory blocking codex consult.
disable-model-invocation: true
argument-hint: <original-gp-number> <feedback description>
---

# Revise GP Project

Add new phases addressing real-world feedback. Always creates a **new**
GP project (`source:revise`) that references the original. The original is
left as-is (closed or `awaiting-confirmation`).

## Your Role

**Senior Software Engineer + Project Manager.** Compose the revision's
draft plan; hand off to Protocol 01.

## Arguments

Parse `$ARGUMENTS`:
- First token: the original GP number (with or without `GP-` prefix)
- Rest: the feedback description

**Input:** $ARGUMENTS

## Authority

Same as `/claude-gp-add`. The original project is touched only for the
back-reference comment in Protocol 06 Step 4.

## Procedure

Follow [Projects/gp_protocols/06_revise_gp_project.md](../../../Projects/gp_protocols/06_revise_gp_project.md)
step-by-step:

1. Load original project context (verify it's `phase:closed` or
   `status:awaiting-confirmation`; refuse if mid-implementation)
2. Compose revision draft (Title, Source=`revise`, Type, Priority, Body,
   Phases, design_md, manifest_md, revise_parent_gp=<original>)
3. Delegate to Protocol 01 — blocking codex consult applies
4. Cross-link: post back-reference comment on the original
5. Report

## Constraints

- **Always a new project.** Never re-opens the original.
- **Blocking codex consult applies** (via Protocol 01).
- **Original's assets stay intact** (archived if archived, present if not).
- **Refuse if original is mid-implementation.** In that case the right
  action is `/claude-gp-continue` discovering new work, not revision.

## Related skills

- `/claude-gp-extract-phase` — for splitting a phase out of an open project
- `/claude-gp-continue <new>` — to start work on the revision's phase 1
