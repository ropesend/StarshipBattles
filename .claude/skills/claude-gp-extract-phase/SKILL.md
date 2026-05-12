---
name: claude-gp-extract-phase
description: Extract a phase from a GP project into its own new GP project. Closes parent's phase sub-issue, renumbers remaining phases. Mandatory blocking codex consult.
disable-model-invocation: true
argument-hint: <parent-gp-number> <phase-number>
---

# Extract Phase from GP Project

Split a phase from an existing GP project into its own project. The
extracted scope becomes a new GP-<n> with its own phases. The parent's
phase sub-issue is closed with a back-reference; remaining phases are
renumbered to keep continuity.

## Your Role

**Senior Software Engineer + Project Manager.** Compose the extracted
project's draft plan with the re-decomposed phases; hand off to Protocol 01.

## Arguments

Parse `$ARGUMENTS`:
- First token: parent GP number (with or without `GP-` prefix)
- Second token: phase number (1-indexed)

**Input:** $ARGUMENTS

## Authority

Same as `/claude-gp-add`, plus:
- Close the extracted phase sub-issue on the parent
- Renumber remaining phase sub-issues on the parent (title + `phase:*` label
  + parent body Quick Status)
- Post back-reference comments on the parent

You **MUST NOT**:
- Close the parent project itself (user-only)
- Extract a phase that's already closed (use `/claude-gp-revise` instead)
- Apply `verified` (user-only)

## Procedure

Follow [Projects/gp_protocols/07_extract_phase_gp.md](../../../Projects/gp_protocols/07_extract_phase_gp.md)
step-by-step:

1. Load parent context (verify parent open, target phase is `pending` or
   `in-progress`)
2. Compose extracted project's draft (Title, Source=`extract`,
   extract_parent_gp=<parent>, re-decomposed phases — refuse if it would
   become a single-phase project)
3. Delegate to Protocol 01 — blocking codex consult applies
4. Update parent:
   - Close the extracted phase sub-issue with back-reference comment
   - Renumber remaining phases (title + label + parent body Quick Status)
   - Post cross-reference comment on parent
5. Report

## Constraints

- **Refuse if extraction would produce a single-phase project.** Extraction
  is for phases that have grown into multi-phase work. A 1-phase result
  means the original phase wasn't actually too big.
- **Refuse if target phase is closed.** Closed phases use `/claude-gp-revise`.
- **Blocking codex consult applies** (via Protocol 01). The consult's
  bundling question becomes "are the extracted sub-phases the right
  decomposition of the original single phase?".
- **Renumbering is atomic** — sub-issue title, `phase:*` label, and parent
  body Quick Status must align after the operation.

## Related skills

- `/claude-gp-revise <gp_number>` — for closed-project gaps
- `/claude-gp-continue <new>` — to start work on the extracted project
