---
name: debug-batch-close
description: Archive multiple confirmed bug fixes in a single operation
disable-model-invocation: true
argument-hint: <bug-numbers, e.g. 46 49 50>
---

# Batch Close Bugs

**Protocol:** `Debugging/protocols/03a_batch_close.md`

Read and follow the full protocol file `Debugging/protocols/03a_batch_close.md`.

## Your Role

Adopt the **Librarian** persona.

## Targets

Bug IDs to close: $ARGUMENTS

## Execution

For EACH bug ID listed above:

1. **READ** the ticket from `Debugging/active_bugs/BUG-XX.md`
2. **UPDATE INDEX:** Append entry to `Debugging/solved_bugs.md`
   - Format: `## BUG-XX [Title]`
   - Content: Date Solved, Brief Summary, Key Test Case
3. **ARCHIVE TICKET:** MOVE `active_bugs/BUG-XX.md` to `archived_tickets/BUG-XX.md`
   - Do not modify content — preserve full logs.
4. **UPDATE DASHBOARD:** Remove row from `Debugging/debug_plan.md` Bug Queue table.

## Confirmation

Report summary table of all archived bugs and total count.
