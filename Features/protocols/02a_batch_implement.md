# PROTOCOL 02a: Batch Feature Implementation (Autonomous)
**Role:** Senior Software Engineer (Autonomous Mode)

**Goal:** Implement multiple features in sequence without waiting for user input between each one.

**Procedure:**
1.  **Check Context:** Estimate remaining context usage.
    * If context >= 80% full: **STOP** and output a summary.
2.  **Select Feature:** Read `Features/feature_plan.md`, pick the top `[Pending]` feature.
    * If no `[Pending]` features remain: **STOP** and output a summary.
    * Skip any features with status `[Needs Clarification]` — these require user answers first.
3.  **Execute PROTOCOL 02:** Run the full implementation for the selected feature.
    * **Phase 0 — Deep Review:** Before writing any test code, review the feature requirements. If the requirements are NOT clear (ambiguous, vague, or multiple valid interpretations), post questions in the ticket, set `[Needs Clarification]`, and move to the next feature.
    * If feature is marked `[Needs Refactor]`: Skip to next feature.
    * If feature is marked `[Blocked]`: Skip to next feature.
4.  **Loop:** Return to Step 1. Do NOT wait for user confirmation between features.

**Exit Conditions:**
* Context limit reached (80%)
* No pending features remain
* All remaining features are `[Blocked]`, `[Needs Refactor]`, or `[Needs Clarification]`

**Output Format (on exit):**
```
## Batch Implementation Summary

| FEAT-ID | Final Status |
|---------|--------------|
| FEAT-XX | Awaiting Confirmation |
| FEAT-YY | Needs Refactor |
| FEAT-WW | Needs Clarification |
| FEAT-ZZ | Still Pending |

**Features Completed:** X
**Features Skipped (Needs Refactor):** Y
**Features Needing Clarification:** W
**Features Still Pending:** Z
**Exit Reason:** [Context limit / No pending features / All blocked or need input]
```
