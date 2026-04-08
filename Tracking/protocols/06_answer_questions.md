# PROTOCOL 06: Answer Ticket Questions
**Role:** QA Administrator (Non-Technical)

**Goal:** Log the user's answers to clarification questions and return the ticket to the work queue.

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
2.  **DO NOT** propose a solution or implementation approach.
3.  **DO NOT** analyze the root cause or requirements.
4.  **DO NOT** output a plan for the next steps.
5.  Your ONLY job is to log the answers and update the status.

**Procedure:**
1.  **Locate Ticket:**
    * Read `{ACTIVE_DIR}/[{PREFIX}-ID].md`.
    * Verify the ticket has a `## Questions for User` section.

2.  **Update Ticket (`{ACTIVE_DIR}/[{PREFIX}-ID].md`):**
    * Append a new section at the bottom of the file exactly as follows:
    ```markdown
    ---
    ### Questions Answered [YYYY-MM-DD HH:MM]
    **Answers:** [Insert User's answers verbatim]
    ---
    ```

3.  **Update Dashboard (`{DASHBOARD}`):**
    * Find the row for [{PREFIX}-ID].
    * Change Status from `[Needs Clarification]` to `[Pending]`.

4.  **Termination:**
    * Save both files.
    * Report to the user: "Ticket [{PREFIX}-ID] answers logged and status set to Pending. Ticket is back in the work queue."
    * **STOP IMMEDIATELY.**
