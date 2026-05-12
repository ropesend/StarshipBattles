---
name: claude-gi-continue
description: Autonomous batch — work pending bugs or features until context limit (e.g., /claude-gi-continue bug)
disable-model-invocation: true
argument-hint: bug|feature
---

# Continue (Batch Work)

Loop through pending issues of the given type, working each one to
`status:awaiting-confirmation`, until you hit ~80% context usage.

## Your Role

**Engineer (autonomous batch mode).** Same authority as `/claude-gi-work`.

## Arguments

Parse `$ARGUMENTS` as a single word: `bug` or `feature`.

**Input:** $ARGUMENTS

## Procedure

1. **QUERY** all pending issues of the type (sorted by priority — see
   `/claude-gi-next`).
2. **LOOP**:
   - For each issue, run the full `/claude-gi-work` procedure.
   - After each issue, estimate context usage. Stop the loop when usage
     exceeds ~80% or when there are no more pending issues.
3. **REPORT** at the end:
   - List of issue numbers worked, with their final statuses.
   - Reason for stopping (context exhausted / queue empty / user signal).

## Constraints

- **One issue per loop iteration.** Don't merge changes across issues.
- **Commit after each issue.** Each issue should produce a clean,
  reviewable commit (or sequence) that references the issue number
  (`fix: ... (#NNN)` / `feat: ... (#NNN)`).
- **Same authority limits as `/claude-gi-work`** — no closing issues, no
  `verified` labels.
- **Stop early** if you hit a `status:needs-clarification` situation rather
  than guessing. Move on to the next issue.
