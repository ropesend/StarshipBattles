---
name: ticket-close
description: Archive a confirmed ticket — move to archive and update indexes (e.g., /ticket-close bug 42)
disable-model-invocation: true
argument-hint: bug|feature <number>
---

# Close Ticket

**Protocol:** `Tickets/protocols/03_close_ticket.md`

Read and follow the full protocol file.

## Your Role

Adopt the **Librarian** persona.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type (bug/feature), second word = ticket number.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| ARCHIVE_DIR | Debugging/archived_tickets | Features/archived_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |
| INDEX | Debugging/solved_bugs.md | Features/completed_features.md |

## Execution

1. **READ** the active ticket `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md` to extract the final summary and key test case.
2. **UPDATE INDEX:** Append entry to {INDEX}.
3. **ARCHIVE TICKET:** MOVE `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md` to `{ARCHIVE_DIR}/{PREFIX}-{NUMBER}.md`. Do not modify content.
4. **UPDATE DASHBOARD:** Remove the row from DASHBOARD.
5. **CONFIRMATION:** List the 3 specific file paths that were modified/moved.
