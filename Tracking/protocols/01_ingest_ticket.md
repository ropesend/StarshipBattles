# PROTOCOL 01: Ticket Ingestion
**Role:** Project Manager (No Coding)

**Goal:** Parse user input and create distinct tickets for new {TYPE}s.

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| ARCHIVE_DIR | Tracking/bugs/archived | Tracking/features/archived |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |
| INDEX | Tracking/solved_bugs.md | Tracking/completed_features.md |

**Naming Rule:** Each ticket receives a unique sequential ID ({PREFIX}-XX). Never append suffixes (e.g., {PREFIX}-08_ISSUE). If a related issue is found during investigation, create a new ticket with a new ID and reference the related ticket in the Description.

**Procedure:**
1.  **Analyze Queue:** Read `{DASHBOARD}` to identify the next sequential {TYPE} ID (e.g., {PREFIX}-06).
2.  **Create Tickets:** For each ticket provided by the user:
    * Create a file: `{ACTIVE_DIR}/[{PREFIX}-ID].md`.
    * Paste the *exact, raw* description and image paths into the file.
    * Initialize sections: `## Description`, `## Priority`, `## Status (Pending)`, `## Work Log`.
    * Set Priority using the guidelines below.
3.  **Update Dashboard:** Append the new ticket to the table in `{DASHBOARD}`.
    * Link the "Spec File" column to `{ACTIVE_DIR}/[{PREFIX}-ID].md` (use path relative to the dashboard).
4.  **Termination:** List the IDs created and exit.

### Priority Guidelines

**For Bugs** (based on severity):
- **Critical:** Blocks core gameplay or causes crashes
- **High:** Significant feature broken
- **Medium:** Minor feature issue or visual bug
- **Low:** Polish, QoL improvements

**For Features** (based on importance):
- **Critical:** Core functionality required for release
- **High:** Important feature with significant user impact
- **Medium:** Nice-to-have improvement
- **Low:** Polish, minor enhancement
