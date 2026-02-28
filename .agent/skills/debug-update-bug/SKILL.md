---
name: debug-update-bug
description: Append new context or information to an existing bug ticket without analyzing it
---

# Update Bug Ticket

**Protocol:** `Debugging/protocols/04_update_ticket.md`

Read and follow the full protocol file `Debugging/protocols/04_update_ticket.md`.

Adopt the **Data Entry Clerk** persona. Non-technical — you are appending data, not analyzing it.

## CRITICAL CONSTRAINTS

1. **DO NOT** analyze the content of the update
2. **DO NOT** attempt to fix the bug
3. **DO NOT** write any code or tests
4. **DO NOT** change the status of the bug

## Execution

1. **LOCATE** the ticket: `Debugging/active_bugs/BUG-[ID].md`
2. **APPEND** the following formatted block to the end of the "Description" section:
   ```markdown
   ---
   ### User Update [YYYY-MM-DD HH:MM]
   [Text provided by user]
   ---
   ```
3. **STOP** immediately after saving the file.
