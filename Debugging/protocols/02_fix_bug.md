# PROTOCOL 02: Bug Resolution (TDD)
**Role:** Senior Software Engineer

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a bug as [Solved]. You do NOT have the authority to move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation] or [Needs Clarification].

**Selection Logic:**
* **If User Specified a Bug ID:** Load that specific ticket.
* **If No ID Specified:** Read `Debugging/debug_plan.md`, pick the top "Pending" item.

**Execution Steps:**

1.  **Context Loading:** * Read `Debugging/active_bugs/[BUG-ID].md`.
    * Update `Debugging/debug_plan.md`: Set status to `[In-Progress]`.

2.  **Phase 0: Deep Review & Ambiguity Check:**
    * **Review** the relevant source code, documentation, and related systems for the bug area.
    * **Assess** whether the correct architectural fix is clearcut or ambiguous.
    * **Decision gate:**
      * **If clearcut:** Proceed to Phase 1 (Reproduction).
      * **If ambiguous** (correct fix is NOT obvious, or multiple valid approaches exist with unclear trade-offs):
        1. Add a `## Questions for User` section to `active_bugs/[BUG-ID].md` with specific, detailed questions about the intended behavior or architectural direction.
        2. In the `## Work Log`, note what was reviewed and why the fix is ambiguous.
        3. Update `Debugging/debug_plan.md`: Set status to `[Needs Clarification]`.
        4. **STOP.** Do not attempt a fix. Inform the user: "Bug requires clarification before a fix can be attempted. Questions have been posted in the ticket."

3.  **Phase 1: Reproduction (Red):**
    * Create a test case that fails.
    * Update `active_bugs/[BUG-ID].md` `## Work Log` with the failing test output.

4.  **Phase 2: The Fix (Green):**
    * Modify code to pass the test.
    * Run regression tests to ensure no breaks.

5.  **Phase 3: Documentation:**
    * Append your technical approach to `active_bugs/[BUG-ID].md` `## Work Log`.
    * State clearly which files were modified.

6.  **Phase 4: The Stop Sign (Gatekeeper):**
    * **Update Dashboard:** In `Debugging/debug_plan.md`, change status to `[Awaiting Confirmation]`.
    * **Action:** STOP. Do not update `solved_bugs.md`. Do not move the file.
    * **Output:** Inform the user: "Bug is fixed locally and passing tests. Status set to Awaiting Confirmation. Please Verify."

**The Handoff Rule:**
If you run out of context or get stuck, write a summary in the Work Log and ask for a restart.