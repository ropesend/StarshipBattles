# PROTOCOL 03: Closing & Archiving Feature
**Role:** Librarian

**Goal:** Move a confirmed feature to the permanent archive and clean up the active workspace.

**Procedure:**
1.  **Update Index:** Append an entry to `Features/completed_features.md`.
    * Format: `## [FEAT-ID] [Title]`
    * Content: Date Completed, Brief Summary of Implementation, and the Key Test Case used.
2.  **Archive Ticket:**
    * **MOVE** the file `Features/active_features/[FEAT-ID].md` to `Features/archived_features/[FEAT-ID].md`.
    * Do not modify the content of the ticket file; preserve the full logs.
3.  **Update Dashboard:**
    * Open `Features/feature_plan.md`.
    * Remove the row for this feature from the "Feature Queue" table.
4.  **Termination:** Confirm the feature is indexed and the ticket file has been moved to the archive.
