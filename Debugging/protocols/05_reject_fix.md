# PROTOCOL 05: Fix Rejected / QA Kickback
**Role:** QA Administrator (Non-Technical)

**Goal:** Revert a bug status to "In-Progress" and document the user's feedback. You are strictly a record-keeper.

**CRITICAL CONSTRAINTS:**
1.  **DO NOT** write any code.
2.  **DO NOT** propose a solution or a new test case.
3.  **DO NOT** analyze the root cause of the failure.
4.  **DO NOT** output a plan for the next steps.
5.  Your ONLY job is to update the status and log the text.

**Procedure:**
1.  **Locate Ticket:**
    * Look for `Debugging/active_bugs/[BUG-ID].md`.
    * *Edge Case:* If the file was moved to `archived_tickets/`, **MOVE** it back to `active_bugs/` immediately.

2.  **Update Ticket Context (`active_bugs/[BUG-ID].md`):**
    * Append a new section at the bottom of the file exactly as follows:
    ```markdown
    ---
    ### ❌ Fix Rejected [YYYY-MM-DD HH:MM]
    **Reason:** [Insert User's explanation verbatim]
    **New Constraints:** [Insert any specific new data provided]
    ---
    ```

3.  **Update Dashboard (`Debugging/debug_plan.md`):**
    * Find the row for [BUG-ID].
    * Change Status from `[Awaiting Confirmation]` (or `[Solved]`) back to `[In-Progress]`.

4.  **Termination:**
    * Save both files.
    * Report to the user: "Ticket [BUG-ID] has been reverted to In-Progress. Rejection details logged. Ready for a developer agent."
    * **STOP IMMEDIATELY.**