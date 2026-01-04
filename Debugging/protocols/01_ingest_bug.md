# PROTOCOL 01: Bug Ingestion
**Role:** Project Manager (No Coding)

**Goal:** parse user input and create distinct tickets for new bugs.

**Procedure:**
1.  **Analyze Queue:** Read `Debugging/debug_plan.md` to identify the next sequential Bug ID (e.g., BUG-06).
2.  **Create Tickets:** For each bug provided by the user:
    * Create a file: `Debugging/active_bugs/[BUG-ID].md`.
    * Paste the *exact, raw* description and image paths into the file.
    * Initialize sections: `## Description`, `## Status (Pending)`, `## Work Log`.
3.  **Update Dashboard:** Append the new bug to the table in `Debugging/debug_plan.md`.
    * Link the "Spec File" column to `active_bugs/[BUG-ID].md`.
4.  **Termination:** List the IDs created and exit.