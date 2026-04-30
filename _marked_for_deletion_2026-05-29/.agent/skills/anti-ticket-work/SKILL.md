---
name: anti-ticket-work
description: Fix a bug or implement a feature by ticket ID (e.g., /anti-ticket-work bug 42 or /anti-ticket-work feature 7)
disable-model-invocation: true
argument-hint: bug|feature <number>
---

# Work Ticket

**Protocol:** `Tracking/protocols/02_work_ticket.md`

Read and follow the full protocol file.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type (bug/feature), second word = ticket number.

**Input:** $ARGUMENTS

## Configuration

Set these values based on ticket type:

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |
| INDEX | Tracking/solved_bugs.md | Tracking/completed_features.md |

## Execution

1. **LOAD** the ticket file: `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md`
2. **READ** relevant `docs/` files for the areas being modified (see `docs/README.md`).
3. **UPDATE** DASHBOARD: Set status to `[In-Progress]`.
4. **FOLLOW** the full protocol in `Tracking/protocols/02_work_ticket.md`, executing:
   - All shared phases (context, test, implementation, documentation)
   - **Bug-only** phases if type is Bug (anti-reversion, integrity check, documentation discrepancy)
   - **Feature-only** phases if type is Feature (ambiguity check, refactor flag)
5. **SET** status to `[Awaiting Confirmation]` when done.

**CRITICAL:** You do NOT have authority to mark tickets as [Solved]/[Completed] or move files to archives. Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
