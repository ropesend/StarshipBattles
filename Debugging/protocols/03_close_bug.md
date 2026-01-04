# PROTOCOL 03: Closing & Archiving
**Role:** Librarian

**Goal:** Move a confirmed fix to the permanent archive and clean up the active workspace.

**Procedure:**
1.  **Update Index:** Append an entry to `Debugging/solved_bugs.md`.
    * Format: `## [BUG-ID] [Title]`
    * Content: Date Solved, Brief Summary of Solution, and the Key Test Case used.
2.  **Archive Ticket:**
    * **MOVE** the file `Debugging/active_bugs/[BUG-ID].md` to `Debugging/archived_tickets/[BUG-ID].md`.
    * Do not modify the content of the ticket file; preserve the full logs.
3.  **Update Dashboard:**
    * Open `Debugging/debug_plan.md`.
    * Remove the row for this bug from the "Bug Queue" table.
4.  **Termination:** Confirm the bug is indexed and the ticket file has been moved to the archive.