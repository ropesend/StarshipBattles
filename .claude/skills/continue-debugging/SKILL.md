---
name: continue-debugging
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

2. **BEGIN BATCH LOOP:**
   - Check context usage — if >= 80%, EXIT with summary
   - Select highest priority bug
   - Load ticket file: `Debugging/active_bugs/BUG-XX.md`
   - Execute full TDD cycle (Reproduce -> Fix -> Document -> Set `[Awaiting Confirmation]`)
   - If stuck after 3+ attempts, set `[Blocked]` and move to next bug
   - Do NOT wait for user input — proceed to next bug
   - LOOP back to context check

3. **EXIT** when context >= 80% OR no Pending bugs remain.

4. **OUTPUT** batch session summary:
   - Bugs awaiting confirmation (fixed this session)
   - Bugs blocked (need human input)
   - Bugs still pending

**AUTONOMOUS MODE:** Do not stop between bugs. Only stop for context limit or empty queue.

**CRITICAL:** You do NOT have authority to mark bugs as [Solved] or move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation].
