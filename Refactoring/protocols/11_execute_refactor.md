# PROTOCOL 11: Execute Refactor
**Role:** Senior Software Engineer
**Objective:** Execute *only* the current phase.

**Procedure:**
1. **Load Context:** Read `Refactoring/active_refactor.md`.
   * **Safety Check:** If this file is missing, STOP. Return to Protocol 10.

2. **Implementation Loop:**
   * Execute Checklist items for the current phase.
   * **Persistence:** Mark completed items with `[x]`. **NEVER DELETE** completed items.
   * **Immutable Goal:** Do NOT modify the High-Level Goal description.
   * Write new tests as required.
   * Update `Refactoring/active_phase_log.md` with progress.

3. **Test Gauntlet (Goal 4):**
   * **Run ALL tests.**
   * **Triage Failures:** For every failing test, you must explicitly decide:
     * **[FIX]:** Correct the code (or test) if it's a regression.
     * **[DELETE]:** Remove the test if it covers obsolete functionality.
     * **[FLAG]:** Mark as `[KNOWN_ISSUE]` in `active_refactor.md` to be ignored/fixed in a later phase.
     * **CRITICAL:** Do NOT simply revert changes to make tests pass.

4. **Completion:**
   * Checklist Done?
   * Triage Complete? (No unexplained failing tests)
   * **STOP.** Request Protocol 12 (Swarm Review).
