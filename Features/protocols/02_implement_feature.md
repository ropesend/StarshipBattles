# PROTOCOL 02: Feature Implementation (4-Phase with Code Review)
**Role:** Senior Software Engineer

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a feature as [Completed]. You do NOT have the authority to move files to `archived_features/`. Your authority ends at [Awaiting Confirmation], [Needs Refactor], or [Needs Clarification].

**Selection Logic:**
* **If User Specified a Feature ID:** Load that specific ticket.
* **If No ID Specified:** Read `Features/feature_plan.md`, pick the top "Pending" item.

**Execution Steps:**

1.  **Phase 0: Deep Review & Ambiguity Check**
    * Read `Features/active_features/[FEAT-ID].md`.
    * Update `Features/feature_plan.md`: Set status to `[In-Progress]`.
    * **Review** the feature requirements for clarity and completeness.
    * **Assess** whether the requirements are clear enough to implement.

    **Decision Gate:**
    * **If clear:** Proceed to Phase 1 (Analysis).
    * **If ambiguous** (requirements are vague, multiple valid interpretations exist, or acceptance criteria are unclear):
      1. Add a `## Questions for User` section to `active_features/[FEAT-ID].md` with specific questions about the intended behavior.
      2. In the `## Work Log`, note what was reviewed and why the requirements are ambiguous.
      3. Update `Features/feature_plan.md`: Set status to `[Needs Clarification]`.
      4. **STOP.** Do not attempt implementation. Inform the user: "Feature requires clarification before implementation can begin. Questions have been posted in the ticket."

2.  **Phase 1: Analysis (Component Review)**
    * Update `Features/feature_plan.md`: Set status to `[Analysis]`.
    * Identify the component/module where the feature will live.
    * Examine related files in that component (imports, dependencies, existing patterns).
    * Assess: Can this be implemented cleanly without significant refactoring?

    **Decision Point:**
    * **If refactor is recommended:**
      - Update status to `[Needs Refactor]` in `feature_plan.md`.
      - Append refactor report to Work Log (see format below).
      - **STOP.** Inform user: "Feature requires refactoring. See Work Log for details."
    * **If clean implementation is possible:** Continue to Phase 2.

3.  **Phase 2: Test (Red)**
    * Update `Features/feature_plan.md`: Set status to `[In-Progress]`.
    * Create a test case that fails (tests the expected new behavior).
    * Update `active_features/[FEAT-ID].md` `## Work Log` with the failing test details.

4.  **Phase 3: Implementation (Green)**
    * Implement the feature to pass the test.
    * Run regression tests to ensure no breaks.

5.  **Phase 4: Documentation & Gatekeeper**
    * Append your technical approach to `active_features/[FEAT-ID].md` `## Work Log`.
    * State clearly which files were modified.
    * **Update Dashboard:** In `Features/feature_plan.md`, change status to `[Awaiting Confirmation]`.
    * **Action:** STOP. Do not update `completed_features.md`. Do not move the file.
    * **Output:** Inform the user: "Feature is implemented and passing tests. Status set to Awaiting Confirmation. Please verify."

**Refactor Report Format (for Phase 1 when refactor is needed):**
```markdown
---
### Refactor Recommended [YYYY-MM-DD HH:MM]
**Component Reviewed:** [list of files examined]
**Current Structure:** [brief description of existing code architecture]
**Issue:** [why clean implementation isn't feasible]
**Recommendation:** [suggested refactor approach]
**Impact:** [what files/systems would need to change]
---
```

**The Handoff Rule:**
If you run out of context or get stuck, write a summary in the Work Log and ask for a restart.
