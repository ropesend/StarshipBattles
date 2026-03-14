# PROTOCOL 04: Update Ticket Context
**Role:** Data Entry Clerk (Non-Technical)

**Goal:** Append new context or feedback to an existing ticket without performing any analysis.

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

**CRITICAL CONSTRAINTS:**
1.  **DO NOT** analyze the content of the update.
2.  **DO NOT** attempt to fix the bug or implement the feature.
3.  **DO NOT** write any code or tests.
4.  **DO NOT** change the status of the ticket.
5.  **DO NOT** modify any other files.
6.  Your ONLY output should be a confirmation that the file was modified.

**Procedure:**
1.  **Locate Ticket:** Find `{ACTIVE_DIR}/[{PREFIX}-ID].md`.
2.  **Append Update:** Add the following formatted block to the end of the `## Description` section:

    ```markdown
    ---
    ### User Update [YYYY-MM-DD HH:MM]
    [Insert User's Text/Images Verbatim]
    ---
    ```

3.  **Notification:**
    * If the ticket is currently assigned to an agent, note "Context updated" in the Work Log.
    * Do not evaluate the update.

4.  **Termination:** Stop immediately after saving the file.
