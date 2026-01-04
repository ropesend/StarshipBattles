# PROTOCOL 05: Fix Rejected / QA Kickback
**Role:** Quality Assurance Lead

**Goal:** Revert a bug status to "In-Progress" and document why the previous fix attempt failed.

**Procedure:**
1.  **Locate Ticket:**
    * Look for `Debugging/active_bugs/[BUG-ID].md`.
    * *Edge Case:* If the file was prematurely moved to `archived_tickets/`, **MOVE** it back to `active_bugs/` immediately.

2.  **Update Ticket Context (`active_bugs/[BUG-ID].md`):**
    * Append a new section at the bottom of the file (do not overwrite previous logs):
    ```markdown
    ---
    ### ❌ Fix Rejected [YYYY-MM-DD HH:MM]
    **Reason:** [Insert User's explanation of the failure/partial success]
    **New Constraints:** [Insert any specific new data provided]
    ---
    ```

3.  **Update Dashboard (`Debugging/debug_plan.md`):**
    * Find the row for [BUG-ID].
    * Change Status from `[Awaiting Confirmation]` (or `[Solved]`) back to `[In-Progress]`.
    * **Crucial:** In the "Attempt Log" or notes, mark the last attempt as **FAILED**.

4.  **Immediate Next Step:**
    * The agent must now analyze the new feedback.
    * **Action:** Propose a new "Red Phase" test case that reproduces the *remaining* part of the issue described by the user.

**Constraint:** Do not argue with the feedback. If the user says it is broken, treat it as broken.