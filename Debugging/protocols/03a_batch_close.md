# PROTOCOL 03a: Batch Closing & Archiving
**Role:** Librarian

**Goal:** Archive multiple confirmed fixes in a single operation.

**Input:** List of BUG-IDs (e.g., BUG-15, BUG-27, BUG-30)

**Procedure:**
For EACH bug in the provided list:
1. **Update Index:** Append entry to `Debugging/solved_bugs.md`
   - Format: `## [BUG-ID] [Title]`
   - Content: Date Solved, Brief Summary, Key Test Case
2. **Archive Ticket:** MOVE `active_bugs/[BUG-ID].md` to `archived_tickets/[BUG-ID].md`
   - Do not modify the content of the ticket file; preserve the full logs.
3. **Update Dashboard:** Remove row from `debug_plan.md` Bug Queue table

**Termination:** Report summary table:
| BUG-ID | Status |
|--------|--------|
| BUG-XX | Archived |
| BUG-YY | Archived |

Confirm total count: "X bugs archived successfully."
