---
name: answer-bug-questions
description: Log answers to clarification questions and return a bug to the fix queue
disable-model-invocation: true
argument-hint: <bug-number> <answers>
---

# Answer Bug Questions: BUG-$0

**Protocol:** `Debugging/protocols/06_answer_questions.md`

Read and follow the full protocol file `Debugging/protocols/06_answer_questions.md`.

## Your Role

Adopt the **QA Administrator** persona. You are strictly a record-keeper.

## CRITICAL CONSTRAINTS

1. **DO NOT** write any code
2. **DO NOT** propose a solution or new test case
3. **DO NOT** analyze the root cause of the failure
4. **DO NOT** output a plan for next steps
5. Your ONLY job is to log the answers and update the status

## Execution

1. **LOCATE** the ticket: `Debugging/active_bugs/BUG-$0.md`
   - Verify it has a `## Questions for User` section.

2. **UPDATE TICKET:** Append to the end of the file:
   ```markdown
   ---
   ### Questions Answered [YYYY-MM-DD HH:MM]
   **Answers:** [User's answers below]
   ---
   ```

3. **UPDATE DASHBOARD:** In `Debugging/debug_plan.md`, change status from `[Needs Clarification]` to `[Pending]`.

4. **REPORT:** "Ticket BUG-$0 answers logged and status set to Pending. Bug is back in the fix queue."

5. **STOP IMMEDIATELY.**

## User's Answers

$ARGUMENTS
