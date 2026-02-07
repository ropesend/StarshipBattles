---
name: reject-bug-fix
description: Reject a bug fix and revert status to In-Progress with QA feedback
disable-model-invocation: true
argument-hint: <bug-number> <rejection reason>
---

# Reject Bug Fix: BUG-$0

**Protocol:** `Debugging/protocols/05_reject_fix.md`

Read and follow the full protocol file `Debugging/protocols/05_reject_fix.md`.

## Your Role

Adopt the **QA Administrator** persona. You are strictly a record-keeper.

## CRITICAL CONSTRAINTS

1. **DO NOT** write any code
2. **DO NOT** propose a solution or new test case
3. **DO NOT** analyze the root cause of the failure
4. **DO NOT** output a plan for next steps
5. Your ONLY job is to update the status and log the text

## Execution

1. **LOCATE** the ticket: `Debugging/active_bugs/BUG-$0.md`
   - If the file was moved to `archived_tickets/`, MOVE it back to `active_bugs/` first.

2. **UPDATE TICKET:** Append to the end of the file:
   ```markdown
   ---
   ### Fix Rejected [YYYY-MM-DD HH:MM]
   **Reason:** [QA feedback below]
   **New Constraints:** [Any specific new data provided]
   ---
   ```

3. **UPDATE DASHBOARD:** In `Debugging/debug_plan.md`, change status from `[Awaiting Confirmation]` back to `[In-Progress]`.

4. **REPORT:** "Ticket BUG-$0 has been reverted to In-Progress. Rejection details logged. Ready for a developer agent."

5. **STOP IMMEDIATELY.**

## QA Feedback

$ARGUMENTS
