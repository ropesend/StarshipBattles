---
name: debug-batch-close
description: Archive multiple confirmed bug fixes in a single operation
---

# Batch Close Bugs

**Protocol:** `Debugging/protocols/03a_batch_close.md`

Adopt the **Librarian** persona.

## Execution

For EACH bug ID provided (e.g. 46 49 50):

1. **READ**: The ticket from `Debugging/active_bugs/BUG-[ID].md`.
2. **UPDATE INDEX**: Append entry to `Debugging/solved_bugs.md` (Date, Summary, Test Case).
3. **ARCHIVE**: MOVE `active_bugs/BUG-[ID].md` to `archived_tickets/BUG-[ID].md`.
4. **UPDATE DASHBOARD**: Remove row from `Debugging/debug_plan.md` Bug Queue table.

## Confirmation

Report a summary table of all archived bugs and the total count.
