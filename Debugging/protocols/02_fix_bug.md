# PROTOCOL 02: Bug Resolution (TDD)
**Role:** Senior Software Engineer

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a bug as [Solved]. You do NOT have the authority to move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation].

**Selection Logic:**
* **If User Specified a Bug ID:** Load that specific ticket.
* **If No ID Specified:** Read `Debugging/debug_plan.md`, pick the top "Pending" item.

**Execution Steps:**

1.  **Context Loading:** * Read `Debugging/active_bugs/[BUG-ID].md`.
    * Update `Debugging/debug_plan.md`: Set status to `[In-Progress]`.

2.  **Phase 1: Reproduction (Red):**
    * Create a test case that fails.
    * Update `active_bugs/[BUG-ID].md` `## Work Log` with the failing test output.

3.  **Phase 2: The Fix (Green):**
    * Modify code to pass the test.
    * Run regression tests to ensure no breaks.

4.  **Phase 3: Documentation:**
    * Append your technical approach to `active_bugs/[BUG-ID].md` `## Work Log`.
    * State clearly which files were modified.

5.  **Phase 4: The Stop Sign (Gatekeeper):**
    * **Update Dashboard:** In `Debugging/debug_plan.md`, change status to `[Awaiting Confirmation]`.
    * **Action:** STOP. Do not update `solved_bugs.md`. Do not move the file.
    * **Output:** Inform the user: "Bug is fixed locally and passing tests. Status set to Awaiting Confirmation. Please Verify."

**The Handoff Rule:**
If you run out of context or get stuck, write a summary in the Work Log and ask for a restart.