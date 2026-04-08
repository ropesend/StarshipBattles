---
name: ticket-next
description: Pick the highest priority pending ticket and start working on it (e.g., /ticket-next bug or /ticket-next feature)
disable-model-invocation: true
argument-hint: bug|feature
---

# Work Next Ticket

**Protocol:** `Tracking/protocols/02_work_ticket.md`

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

1. **READ** DASHBOARD to identify the highest priority `[Pending]` ticket.
2. **LOAD** the specific ticket file: `{ACTIVE_DIR}/{PREFIX}-XX.md`
3. **READ** relevant `docs/` files for the areas being modified.
4. **EXECUTE** the work protocol from `Tracking/protocols/02_work_ticket.md`:
   - **Bug:** Execute Phase 0 (architectural context + anti-reversion), then Phase 1 (reproduction test). Provide STATUS REPORT of context gathered and reproduction test plan.
   - **Feature:** Execute ALL phases (0-4). Provide STATUS REPORT of approach.

**CRITICAL:** Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
