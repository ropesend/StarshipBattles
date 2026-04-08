---
name: ticket-batch-close
description: Archive multiple confirmed tickets in one operation (e.g., /ticket-batch-close bug 46 49 50)
disable-model-invocation: true
argument-hint: bug|feature <numbers...>
---

# Batch Close Tickets

**Protocol:** `Tracking/protocols/03a_batch_close.md`

Read and follow the full protocol file.

## Your Role

Adopt the **Librarian** persona.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type (bug/feature), remaining words = ticket numbers.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| ARCHIVE_DIR | Tracking/bugs/archived | Tracking/features/archived |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |
| INDEX | Tracking/solved_bugs.md | Tracking/completed_features.md |

## Execution

For EACH ticket number:
1. **READ** the ticket from `{ACTIVE_DIR}/{PREFIX}-XX.md`
2. **UPDATE INDEX:** Append entry to {INDEX}
3. **ARCHIVE TICKET:** MOVE to `{ARCHIVE_DIR}/{PREFIX}-XX.md`. Do not modify content.
4. **UPDATE DASHBOARD:** Remove row from DASHBOARD.

**Report** summary table of all archived tickets and total count.
