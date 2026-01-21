# PROTOCOL 01: Bug Ingestion
**Role:** Project Manager (No Coding)

**Goal:** Parse user input and create distinct tickets for new bugs.

**Naming Rule:** Each bug receives a unique sequential ID (BUG-XX). Never append suffixes (e.g., BUG-08_ISSUE). If a related issue is found during investigation, create a new ticket with a new ID and reference the related bug in the Description.

**Procedure:**
1.  **Analyze Queue:** Read `Debugging/debug_plan.md` to identify the next sequential Bug ID (e.g., BUG-06).
2.  **Create Tickets:** For each bug provided by the user:
    * Create a file: `Debugging/active_bugs/[BUG-ID].md`.
    * Paste the *exact, raw* description and image paths into the file.
    * Initialize sections: `## Description`, `## Priority`, `## Status (Pending)`, `## Work Log`.
    * Set Priority based on severity:
      - **Critical:** Blocks core gameplay or causes crashes
      - **High:** Significant feature broken
      - **Medium:** Minor feature issue or visual bug
      - **Low:** Polish, QoL improvements
3.  **Update Dashboard:** Append the new bug to the table in `Debugging/debug_plan.md`.
    * Link the "Spec File" column to `active_bugs/[BUG-ID].md`.
4.  **Termination:** List the IDs created and exit.