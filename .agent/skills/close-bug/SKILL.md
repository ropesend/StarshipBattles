---
name: close-bug
description: Archive a confirmed bug fix — move ticket to archive and update indexes
---

# Close Bug

**Protocol:** `Debugging/protocols/03_close_bug.md`

Read and follow the full protocol file `Debugging/protocols/03_close_bug.md`.

Adopt the **Librarian** persona.

## Execution

1. **READ** the active ticket `Debugging/active_bugs/BUG-[ID].md` to extract the final "Solution Summary" and key test case.

2. **UPDATE INDEX:** Append entry to `Debugging/solved_bugs.md`:
   - Format: `## BUG-[ID] [Title]`
   - Content: Date Solved, Brief Summary of Solution, Key Test Case

3. **ARCHIVE TICKET:** MOVE `Debugging/active_bugs/BUG-[ID].md` to `Debugging/archived_tickets/BUG-[ID].md`
   - Do not modify the content — preserve the full logs.

4. **UPDATE DASHBOARD:** Remove the row for BUG-[ID] from `Debugging/debug_plan.md`.

5. **CONFIRMATION:** List the 3 specific file paths that were modified/moved to confirm the operation is complete.
