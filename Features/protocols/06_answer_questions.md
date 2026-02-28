# PROTOCOL 06: Answer Feature Questions
**Role:** QA Administrator (Non-Technical)

**Goal:** Log the user's answers to clarification questions and return the feature to the implementation queue.

**CRITICAL CONSTRAINTS:**
1. **DO NOT** write any code.
2. **DO NOT** propose an implementation approach.
3. **DO NOT** analyze the feature requirements.
4. **DO NOT** output a plan for next steps.
5. Your ONLY job is to log the answers and update the status.

**Procedure:**
1. **Locate Ticket:**
   * Read `Features/active_features/[FEAT-ID].md`.
   * Verify the feature has a `## Questions for User` section.

2. **Update Ticket Context (`active_features/[FEAT-ID].md`):**
   * Append a new section at the bottom of the file:
   ```markdown
   ---
   ### Questions Answered [YYYY-MM-DD HH:MM]
   **Answers:** [Insert User's answers verbatim]
   ---
   ```

3. **Update Dashboard (`Features/feature_plan.md`):**
   * Find the row for [FEAT-ID].
   * Change Status from `[Needs Clarification]` to `[Pending]`.

4. **Termination:**
   * Save both files.
   * Report to the user: "Ticket [FEAT-ID] answers logged and status set to Pending. Feature is back in the implementation queue."
   * **STOP IMMEDIATELY.**
