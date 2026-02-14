---
name: reject-bug-fix
description: Reject a bug fix and revert status to In-Progress with QA feedback
---

# Reject Bug Fix

**Protocol:** `Debugging/protocols/05_reject_fix.md`

Adopt the **QA Administrator** persona. Strictly record-keeping only.

## Execution

1. **LOCATE**: `Debugging/active_bugs/BUG-[ID].md`. Move back from archive if necessary.

2. **LOG FEEDBACK**: Append the rejection reason and any new data to the end of the ticket:
   ```markdown
   ---
   ### Fix Rejected [YYYY-MM-DD HH:MM]
   **Reason**: [QA feedback]
   ---
   ```

3. **RESET STATUS**: Revert status to `[In-Progress]` in `Debugging/debug_plan.md`.

4. **REPORT**: Confirm the ticket is reverted and details are logged.

**CRITICAL**: DO NOT write code, propose fixes, or analyze causes in this step.
