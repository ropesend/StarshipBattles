---
name: close-feature
description: Archive a confirmed feature implementation — move ticket to archive and update indexes
disable-model-invocation: true
argument-hint: <feat-number>
---

# Close Feature FEAT-$0

**Protocol:** `Features/protocols/03_close_feature.md`

Read and follow the full protocol file `Features/protocols/03_close_feature.md`.

## Your Role

Adopt the **Librarian** persona.

## Execution

1. **READ** the active ticket `Features/active_features/FEAT-$0.md` to extract the final implementation summary and key test case.

2. **UPDATE INDEX:** Append entry to `Features/completed_features.md`:
   - Format: `## [FEAT-$0] - [Title]`
   - Content: Date Completed, Original Request, Implementation Summary, Test Case, Notes

3. **ARCHIVE TICKET:** MOVE `Features/active_features/FEAT-$0.md` to `Features/archived_features/FEAT-$0.md`
   - Do not modify the content — preserve the full logs.

4. **UPDATE DASHBOARD:** Remove the row for FEAT-$0 from `Features/feature_plan.md`.

5. **CONFIRMATION:** List the 3 specific file paths that were modified/moved to confirm the operation is complete.
