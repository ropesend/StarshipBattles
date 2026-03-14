---
name: debug-next
description: Pick the highest priority pending bug and start reproducing it with TDD
disable-model-invocation: true
---

# Debug Next Bug

**Protocol:** `Debugging/protocols/02_fix_bug.md`

Read and follow the full protocol file `Debugging/protocols/02_fix_bug.md`.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Execution

1. **READ** `Debugging/debug_plan.md` to identify the highest priority `[Pending]` bug.
2. **LOAD** the specific ticket file: `Debugging/active_bugs/BUG-XX.md`

3. **EXECUTE Phase 0: Architectural Context (MANDATORY):**
   - Run `git log --oneline -20 -- <affected_files>` for each file implicated in the bug. Note any PROJ-XX or refactor commits in the last 60 days.
   - Check `Projects/active_projects/` for any active project referencing the affected files. If found, read that project's `design.md`.
   - Review `CLAUDE.md` (Architecture Principles, Key Conventions) for relevant rules.
   - Document findings in `## Work Log` under `### Phase 0: Architectural Context`.
   - **ANTI-REVERSION CHECK:** If code was recently refactored, the fix MUST work within the new architecture. If no forward-fix is apparent, set `[Needs Clarification]` and **STOP**.

4. **EXECUTE Phase 1: Reproduction (Red):**
   - Create a test case that fails
   - Confirm the failure
   - Update the `## Work Log` in the ticket file

5. **STATUS REPORT:** Tell the user which bug you are starting, the architectural context gathered, and the reproduction test plan.

**CRITICAL:** You do NOT have authority to mark a bug as [Solved] or move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation].
