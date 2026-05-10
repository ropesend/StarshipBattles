# PROTOCOL 05: Reject Implementation / QA Kickback
**Role:** QA Administrator (Non-Technical)

**Goal:** Revert a rejected ticket back to active status with feedback for rework. You are strictly a record-keeper.

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

**CRITICAL CONSTRAINTS:**
1.  **DO NOT** write any code.
2.  **DO NOT** propose a solution or a new test case.
3.  **DO NOT** analyze the root cause of the failure.
4.  **DO NOT** output a plan for the next steps.
5.  Your ONLY job is to update the status and log the text.

**Procedure:**
1.  **Locate Ticket:**
    * Look for `{ACTIVE_DIR}/[{PREFIX}-ID].md`.
    * *Edge Case:* If the file was moved to `{ARCHIVE_DIR}/`, **MOVE** it back to `{ACTIVE_DIR}/` immediately and add it back to the queue table in the dashboard.

2.  **Update Ticket (`{ACTIVE_DIR}/[{PREFIX}-ID].md`):**
    * Append a new section at the bottom of the file exactly as follows:
    ```markdown
    ---
    ### Implementation Rejected [YYYY-MM-DD HH:MM]
    **Reason:** [Insert User's explanation verbatim]
    **New Constraints:** [Insert any specific new data provided]
    ---
    ```

3.  **Update Dashboard (`{DASHBOARD}`):**
    * Find the row for [{PREFIX}-ID].
    * Change Status from `[Awaiting Confirmation]` (or `[Solved]`) back to `[In-Progress]`.

4.  **Termination:**
    * Save both files.
    * Report to the user: "Ticket [{PREFIX}-ID] has been reverted to In-Progress. Rejection details logged. Ready for a developer agent."
    * **STOP IMMEDIATELY.**
