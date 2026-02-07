---
name: close-bug
description: Archive a confirmed bug fix — move ticket to archive and update indexes
disable-model-invocation: true
argument-hint: <bug-number>
---

# Close Bug BUG-$0

**Protocol:** `Debugging/protocols/03_close_bug.md`

Read and follow the full protocol file `Debugging/protocols/03_close_bug.md`.

## Your Role

Adopt the **Librarian** persona.

## Execution

1. **READ** the active ticket `Debugging/active_bugs/BUG-$0.md` to extract the final "Solution Summary" and key test case.

2. **UPDATE INDEX:** Append entry to `Debugging/solved_bugs.md`:
   - Format: `## BUG-$0 [Title]`
   - Content: Date Solved, Brief Summary of Solution, Key Test Case

3. **ARCHIVE TICKET:** MOVE `Debugging/active_bugs/BUG-$0.md` to `Debugging/archived_tickets/BUG-$0.md`
   - Do not modify the content — preserve the full logs.

4. **UPDATE DASHBOARD:** Remove the row for BUG-$0 from `Debugging/debug_plan.md`.

5. **CONFIRMATION:** List the 3 specific file paths that were modified/moved to confirm the operation is complete.
