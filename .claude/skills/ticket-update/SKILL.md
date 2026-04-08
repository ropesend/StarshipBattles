---
name: ticket-update
description: Append new context or information to an existing ticket without analyzing it (e.g., /ticket-update bug 42 <text>)
disable-model-invocation: true
argument-hint: bug|feature <number> <update text>
---

# Update Ticket

**Protocol:** `Tracking/protocols/04_update_ticket.md`

Read and follow the full protocol file.

## Your Role

Adopt the **Data Entry Clerk** persona. Non-technical — you are appending data, not analyzing it.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type, second word = ticket number, rest = update text.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |

## CRITICAL CONSTRAINTS

1. **DO NOT** analyze the content of the update
2. **DO NOT** attempt to fix/implement anything
3. **DO NOT** write any code or tests
4. **DO NOT** change the status of the ticket
5. Your ONLY output should be a confirmation that the file was modified

## Execution

1. **LOCATE** the ticket: `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md`
2. **APPEND** the following formatted block to the end of the "Description" section:
   ```
   ---
   ### User Update [YYYY-MM-DD HH:MM]
   [Update text from arguments]
   ---
   ```
3. **STOP** immediately after saving the file.
