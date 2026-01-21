# PROTOCOL 03a: Batch Closing & Archiving Features
**Role:** Librarian

**Goal:** Archive multiple confirmed features in a single operation.

**Input:** List of FEAT-IDs (e.g., FEAT-15, FEAT-27, FEAT-30)

**Procedure:**
For EACH feature in the provided list:
1. **Update Index:** Append entry to `Features/completed_features.md`
   - Format: `## [FEAT-ID] [Title]`
   - Content: Date Completed, Brief Summary, Key Test Case
2. **Archive Ticket:** MOVE `active_features/[FEAT-ID].md` to `archived_features/[FEAT-ID].md`
   - Do not modify the content of the ticket file; preserve the full logs.
3. **Update Dashboard:** Remove row from `Features/feature_plan.md` Feature Queue table

**Termination:** Report summary table:
| FEAT-ID | Status |
|---------|--------|
| FEAT-XX | Archived |
| FEAT-YY | Archived |

Confirm total count: "X features archived successfully."
