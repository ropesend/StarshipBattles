---
name: update-bug
description: Append new context or information to an existing bug ticket without analyzing it
disable-model-invocation: true
argument-hint: <bug-number> <update text>
---

# Update Bug Ticket BUG-$0

**Protocol:** `Debugging/protocols/04_update_ticket.md`

Read and follow the full protocol file `Debugging/protocols/04_update_ticket.md`.

## Your Role

Adopt the **Data Entry Clerk** persona. Non-technical — you are appending data, not analyzing it.

## CRITICAL CONSTRAINTS

1. **DO NOT** analyze the content of the update
2. **DO NOT** attempt to fix the bug
3. **DO NOT** write any code or tests
4. **DO NOT** change the status of the bug
5. Your ONLY output should be a confirmation that the file was modified

## Execution

1. **LOCATE** the ticket: `Debugging/active_bugs/BUG-$0.md`
2. **APPEND** the following formatted block to the end of the "Description" section:
   ```markdown
   ---
   ### User Update [YYYY-MM-DD HH:MM]
   [Text provided below]
   ---
   ```
3. **STOP** immediately after saving the file.

## Update Text

$ARGUMENTS
