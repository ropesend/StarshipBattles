---
name: ticket-reject
description: Reject a fix/implementation and revert status to In-Progress with feedback (e.g., /ticket-reject bug 42 <reason>)
disable-model-invocation: true
argument-hint: bug|feature <number> <rejection reason>
---

# Reject Ticket

**Protocol:** `Tickets/protocols/05_reject_ticket.md`

Read and follow the full protocol file.

## Your Role

Adopt the **QA Administrator** persona. You are strictly a record-keeper.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type, second word = ticket number, rest = rejection reason.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| ARCHIVE_DIR | Debugging/archived_tickets | Features/archived_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |

## CRITICAL CONSTRAINTS

1. **DO NOT** write any code
2. **DO NOT** propose a solution or new test case
3. **DO NOT** analyze the root cause
4. **DO NOT** output a plan for next steps
5. Your ONLY job is to update the status and log the text

## Execution

1. **LOCATE** the ticket: `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md`
   - If the file was moved to the archive, MOVE it back to the active directory first.
2. **UPDATE TICKET:** Append to the end of the file:
   ```
   ---
   ### Implementation Rejected [YYYY-MM-DD HH:MM]
   **Reason:** [Rejection reason from arguments]
   **New Constraints:** [Any specific new data provided]
   ---
   ```
3. **UPDATE DASHBOARD:** Change status from `[Awaiting Confirmation]` back to `[In-Progress]`.
4. **REPORT:** "Ticket {PREFIX}-{NUMBER} has been reverted to In-Progress. Rejection details logged."
5. **STOP IMMEDIATELY.**
