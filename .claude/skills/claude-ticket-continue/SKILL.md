---
name: claude-ticket-continue
description: Autonomously work through multiple tickets in sequence until context limit or queue empty (e.g., /anti-ticket-continue bug or /anti-ticket-continue feature)
disable-model-invocation: true
argument-hint: bug|feature
---

# Continue Working Tickets (Autonomous Batch Mode)

**Protocol:** `Tracking/protocols/02a_batch_work.md`

Read and follow the full protocol file.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Arguments

Parse `$ARGUMENTS` as the ticket type (bug or feature).

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |

## Execution

1. **READ** DASHBOARD to identify all `[Pending]` and `[In-Progress]` tickets.
   - Skip any with status `[Needs Clarification]` — these require user answers first.
2. **READ** `docs/README.md` and relevant docs for areas being modified.

3. **BEGIN BATCH LOOP:**
   - Check context usage — if >= 80%, EXIT with summary
   - Select highest priority pending ticket
   - Load ticket file: `{ACTIVE_DIR}/{PREFIX}-XX.md`
   - Execute full work protocol from `Tracking/protocols/02a_batch_work.md`:
     - Follow **Bug-only** sections if type is Bug (anti-reversion, integrity check)
     - Follow **Feature-only** sections if type is Feature (refactor flag)
   - If stuck after 3+ attempts, set `[Blocked]` and move to next ticket
   - Do NOT wait for user input — proceed to next ticket
   - LOOP back to context check

4. **EXIT** when context >= 80% OR no Pending tickets remain.

5. **OUTPUT** batch session summary.

**AUTONOMOUS MODE:** Do not stop between tickets. Only stop for context limit or empty queue.

**CRITICAL:** Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
