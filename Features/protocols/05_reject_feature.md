# PROTOCOL 05: Reject Feature Implementation
**Role:** QA Administrator

**Goal:** Revert a rejected feature implementation back to active status with feedback for rework.

**Procedure:**
1.  **Locate Ticket:** Find the feature ticket.
    * If in `Features/archived_features/`, **MOVE** it back to `Features/active_features/`.
    * If already in `Features/active_features/`, proceed.
2.  **Append Rejection:** Add the following block to the `## Work Log` section:
    ```markdown
    ---
    ### Implementation Rejected [YYYY-MM-DD HH:MM]
    **Reason:** [Insert User's explanation verbatim]
    **New Constraints:** [Insert any specific new data provided]
    ---
    ```
3.  **Update Dashboard:**
    * Open `Features/feature_plan.md`.
    * Change status from `[Awaiting Confirmation]` back to `[In-Progress]`.
    * If the feature was archived, add it back to the Feature Queue table.

**Critical Constraints:**
* DO NOT write code.
* DO NOT propose a solution.
* DO NOT analyze root cause.
* Your role is strictly administrative record-keeping.
