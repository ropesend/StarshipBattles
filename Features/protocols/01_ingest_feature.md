# PROTOCOL 01: Feature Ingestion
**Role:** Project Manager (No Coding)

**Goal:** Parse user input and create distinct tickets for new feature requests.

**Naming Rule:** Each feature receives a unique sequential ID (FEAT-XX). Never append suffixes. If a related feature is found during investigation, create a new ticket with a new ID and reference the related feature in the Description.

**Procedure:**
1.  **Analyze Queue:** Read `Features/feature_plan.md` to identify the next sequential Feature ID (e.g., FEAT-06).
2.  **Create Tickets:** For each feature provided by the user:
    * Create a file: `Features/active_features/[FEAT-ID].md`.
    * Paste the *exact, raw* description and image paths into the file.
    * Initialize sections: `## Description`, `## Priority`, `## Status (Pending)`, `## Work Log`.
    * Set Priority based on importance:
      - **Critical:** Core functionality required for release
      - **High:** Important feature with significant user impact
      - **Medium:** Nice-to-have improvement
      - **Low:** Polish, minor enhancement
3.  **Update Dashboard:** Append the new feature to the table in `Features/feature_plan.md`.
    * Link the "Spec File" column to `active_features/[FEAT-ID].md`.
4.  **Termination:** List the IDs created and exit.
