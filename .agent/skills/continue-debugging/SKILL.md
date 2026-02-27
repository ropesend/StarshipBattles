---
name: continue-debugging
description: Autonomously fix multiple bugs in sequence until context limit or queue empty
---

# Continue Debugging (Autonomous Batch Mode)

**Protocol:** `Debugging/protocols/02a_batch_fix.md`

Adopt the **Senior Software Engineer** persona.

## Execution

1. **IDENTIFY**: Read `Debugging/debug_plan.md` for all `[Pending]` and `[In-Progress]` bugs.
   - Skip any bugs with status `[Needs Clarification]` — these require user answers first.

2. **BATCH LOOP**:
   - Check context usage — if approaching limit, EXIT with summary.
   - Select highest priority bug.
   - **Phase 0 — Deep Review:** Before writing any test code, review relevant source code and documentation. If the correct fix is NOT clearcut, post questions in the ticket, set `[Needs Clarification]`, and move to the next bug.
   - If clearcut, load ticket file and execute full TDD cycle.
   - If stuck after 3 attempts, mark as `[Blocked]` and move to next.
   - Proceed autonomously to the next bug without waiting for input.

3. **EXIT**: Stop when the context window is full or the queue is empty.

4. **SUMMARY**: Report bugs fixed (Awaiting Confirmation), bugs needing clarification (questions posted), bugs blocked, and bugs remaining.

**CRITICAL**: You do NOT have authority to move files to `archived_tickets/`. Your authority ends at `[Awaiting Confirmation]` or `[Needs Clarification]`.
