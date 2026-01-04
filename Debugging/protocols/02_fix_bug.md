# PROTOCOL 02: Bug Resolution (TDD)
**Role:** Senior Software Engineer

**Selection Logic:**
* **If User Specified a Bug ID:** Load that specific ticket.
* **If No ID Specified:** Read `Debugging/debug_plan.md`, pick the top "Pending" item, and mark it "In-Progress".

**Execution Steps:**
1.  **Context Loading:** Read `Debugging/active_bugs/[BUG-ID].md`. This is your Source of Truth.
2.  **Phase 1: Reproduction (TDD):**
    * Create a test case that fails.
    * **CRITICAL:** Update the `## Work Log` in the ticket file with the test name.
3.  **Phase 2: The Fix:**
    * Modify code to pass the test.
    * Run regression tests.
4.  **Phase 3: Update Ticket:**
    * Append your attempts (successful or failed) to the `## Work Log` in `active_bugs/[BUG-ID].md`.
    * **DO NOT** mark as solved in `debug_plan.md` yet. Mark as "Awaiting Confirmation".

**The Handoff Rule:**
If you reach the context limit or get stuck:
1.  Write a summary of your current state into the `## Work Log` of the ticket file.
2.  Stop and ask for a restart.