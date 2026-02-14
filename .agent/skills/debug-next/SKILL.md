---
name: debug-next
description: Pick the highest priority pending bug and start reproducing it with TDD
---

# Debug Next Bug

**Protocol:** `Debugging/protocols/02_fix_bug.md`

Adopt the **Senior Software Engineer** persona.

## Execution

1. **SELECT**: Read `Debugging/debug_plan.md` and pick the highest priority `[Pending]` bug.
2. **LOAD**: `Debugging/active_bugs/BUG-XX.md`.
3. **REPRODUCE (RED)**:
   - Create a failing test case.
   - Confirm failure.
   - Log the failure and approach in `## Work Log`.
4. **REPORT**: Inform the user which bug is now under reproduction and share the initial test plan.

**CRITICAL**: You do NOT have authority to move files to `archived_tickets/`. Your authority ends at `[Awaiting Confirmation]`.
