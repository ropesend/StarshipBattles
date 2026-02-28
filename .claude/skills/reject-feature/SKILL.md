---
name: reject-feature
description: Reject a feature implementation and revert status to In-Progress with feedback
disable-model-invocation: true
argument-hint: <feat-number> <rejection reason>
---

# Reject Feature Implementation: FEAT-$0

**Protocol:** `Features/protocols/05_reject_feature.md`

Read and follow the full protocol file `Features/protocols/05_reject_feature.md`.

## Your Role

Adopt the **QA Administrator** persona. You are strictly a record-keeper.

## CRITICAL CONSTRAINTS

1. **DO NOT** write any code
2. **DO NOT** propose a solution or new test case
3. **DO NOT** analyze the root cause of the issue
4. **DO NOT** output a plan for next steps
5. Your ONLY job is to update the status and log the text

## Execution

1. **LOCATE** the ticket: `Features/active_features/FEAT-$0.md`
   - If the file was moved to `archived_features/`, MOVE it back to `active_features/` first.

2. **UPDATE TICKET:** Append to the end of the file:
   ```markdown
   ---
   ### Implementation Rejected [YYYY-MM-DD HH:MM]
   **Reason:** [QA feedback below]
   **New Constraints:** [Any specific new data provided]
   ---
   ```

3. **UPDATE DASHBOARD:** In `Features/feature_plan.md`, change status from `[Awaiting Confirmation]` back to `[In-Progress]`.

4. **REPORT:** "Ticket FEAT-$0 has been reverted to In-Progress. Rejection details logged. Ready for a developer agent."

5. **STOP IMMEDIATELY.**

## QA Feedback

$ARGUMENTS
