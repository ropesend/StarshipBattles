---
name: debug-continue
description: Autonomously fix multiple bugs in sequence until context limit or queue empty
disable-model-invocation: true
---

# Continue Debugging (Autonomous Batch Mode)

**Protocol:** `Debugging/protocols/02a_batch_fix.md`

Read and follow the full protocol file `Debugging/protocols/02a_batch_fix.md`.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Execution

1. **READ** `Debugging/debug_plan.md` to identify all `[Pending]` and `[In-Progress]` bugs.
   - Skip any bugs with status `[Needs Clarification]` — these require user answers first.

2. **BEGIN BATCH LOOP:**
   - Check context usage — if >= 80%, EXIT with summary
   - Select highest priority bug
   - Load ticket file: `Debugging/active_bugs/BUG-XX.md`
   - **Phase 0 — Architectural Context (MANDATORY):**
     - Run `git log --oneline -20 -- <affected_files>` to check for recent refactors or PROJ-XX commits (last 60 days).
     - Check `Projects/active_projects/` for active projects touching this code. If found, read that project's `design.md`.
     - Review `CLAUDE.md` architecture principles for relevant constraints.
     - Document findings in Work Log under `### Phase 0: Architectural Context`.
     - **ANTI-REVERSION RULE:** If code was recently refactored, the fix MUST preserve the refactor. If no forward-fix is apparent, set `[Needs Clarification]` and move to next bug.
   - If clearcut, execute full TDD cycle (Phase 1: Reproduce → Phase 2: Fix → Phase 2.5: Integrity Check → Phase 3: Document → Phase 4: Set `[Awaiting Confirmation]`)
   - **Phase 2.5 — Post-Fix Integrity Check:** After fix passes tests, verify it doesn't revert recent refactors (`git diff` review), maintains layer boundaries, and follows CLAUDE.md conventions. If reversion detected, set `[Needs Clarification]` and move to next bug.
   - If stuck after 3+ attempts, set `[Blocked]` and move to next bug
   - Do NOT wait for user input — proceed to next bug
   - LOOP back to context check

3. **EXIT** when context >= 80% OR no Pending bugs remain.

4. **OUTPUT** batch session summary:
   - Bugs awaiting confirmation (fixed this session)
   - Bugs needing clarification (questions posted)
   - Bugs blocked (need human input)
   - Bugs still pending

**A skipped bug is better than a reverted refactor.**

**AUTONOMOUS MODE:** Do not stop between bugs. Only stop for context limit or empty queue.

**CRITICAL:** You do NOT have authority to mark bugs as [Solved] or move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
