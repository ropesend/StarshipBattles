# PROTOCOL 03: Closing & Archiving
**Role:** Librarian

**Goal:** Move a confirmed ticket to the permanent archive and clean up the active workspace.

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| ARCHIVE_DIR | Debugging/archived_tickets | Features/archived_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |
| INDEX | Debugging/solved_bugs.md | Features/completed_features.md |

**Procedure:**
1.  **Update Index:** Append an entry to `{INDEX}`.
    * Format: `## [{PREFIX}-ID] [Title]`
    * Content: Date Completed, Brief Summary of Solution/Implementation, and the Key Test Case used.
2.  **Archive Ticket:**
    * **MOVE** the file `{ACTIVE_DIR}/[{PREFIX}-ID].md` to `{ARCHIVE_DIR}/[{PREFIX}-ID].md`.
    * Do not modify the content of the ticket file; preserve the full logs.
3.  **Update Dashboard:**
    * Open `{DASHBOARD}`.
    * Remove the row for this ticket from the queue table.
4.  **Termination:** Confirm the ticket is indexed and the ticket file has been moved to the archive.
