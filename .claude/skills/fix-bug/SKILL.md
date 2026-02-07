---
name: fix-bug
description: Fix a specific bug by ID using the TDD workflow
disable-model-invocation: true
argument-hint: <bug-number>
---

# Fix Bug BUG-$0

**Protocol:** `Debugging/protocols/02_fix_bug.md`

Read and follow the full protocol file `Debugging/protocols/02_fix_bug.md`.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Execution

1. **LOAD** the ticket file: `Debugging/active_bugs/BUG-$0.md`
2. **UPDATE** `Debugging/debug_plan.md`: Set status to `[In-Progress]`.

3. **Phase 1: Reproduction (Red)**
   - Create a test case that fails
   - Update `## Work Log` with the failing test output

4. **Phase 2: The Fix (Green)**
   - Modify code to pass the test
   - Run regression tests to ensure no breaks

5. **Phase 3: Documentation**
   - Append technical approach to `## Work Log`
   - State clearly which files were modified

6. **Phase 4: The Stop Sign**
   - Update `Debugging/debug_plan.md`: Change status to `[Awaiting Confirmation]`
   - **STOP.** Do not update `solved_bugs.md`. Do not move the file.
   - Inform the user: "Bug is fixed locally and passing tests. Status set to Awaiting Confirmation. Please verify."

**CRITICAL:** You do NOT have authority to mark a bug as [Solved] or move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation].
