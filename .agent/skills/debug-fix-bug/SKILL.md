---
name: debug-fix-bug
description: Fix a specific bug by ID using the TDD workflow
---

# Fix Bug

**Protocol:** `Debugging/protocols/02_fix_bug.md`

Read and follow the full protocol file `Debugging/protocols/02_fix_bug.md`.

Adopt the **Senior Software Engineer** persona.

## Execution

1. **LOAD** the ticket file: `Debugging/active_bugs/BUG-[ID].md`
2. **UPDATE** `Debugging/debug_plan.md`: Set status to `[In-Progress]`.

3. **Phase 0: Deep Review & Ambiguity Check**
   - Review relevant source code and documentation for the bug area
   - If the correct fix is clearcut: proceed to Phase 1
   - If ambiguous: add `## Questions for User` to the ticket, note uncertainties in `## Work Log`, set status to `[Needs Clarification]`, and **STOP**

4. **Phase 1: Reproduction (Red)**
   - Create a test case that fails
   - Update `## Work Log` with the failing test output

5. **Phase 2: The Fix (Green)**
   - Modify code to pass the test
   - Run regression tests to ensure no breaks

6. **Phase 3: Documentation**
   - Append technical approach to `## Work Log`
   - State clearly which files were modified

7. **Phase 4: The Stop Sign**
   - Update `Debugging/debug_plan.md`: Change status to `[Awaiting Confirmation]`
   - **STOP.** Do not update `solved_bugs.md`. Do not move the file.
   - Inform the user: "Bug is fixed locally and passing tests. Status set to Awaiting Confirmation. Please verify."

**CRITICAL:** You do NOT have authority to mark a bug as [Solved] or move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
