---
name: answer-feature-questions
description: Log answers to clarification questions and return a feature to the implementation queue
disable-model-invocation: true
argument-hint: <feat-number> <answers>
---

# Answer Feature Questions: FEAT-$0

**Protocol:** `Features/protocols/06_answer_questions.md`

Read and follow the full protocol file `Features/protocols/06_answer_questions.md`.

## Your Role

Adopt the **QA Administrator** persona. You are strictly a record-keeper.

## CRITICAL CONSTRAINTS

1. **DO NOT** write any code
2. **DO NOT** propose an implementation approach
3. **DO NOT** analyze the feature requirements
4. **DO NOT** output a plan for next steps
5. Your ONLY job is to log the answers and update the status

## Execution

1. **LOCATE** the ticket: `Features/active_features/FEAT-$0.md`
   - Verify it has a `## Questions for User` section.

2. **UPDATE TICKET:** Append to the end of the file:
   ```markdown
   ---
   ### Questions Answered [YYYY-MM-DD HH:MM]
   **Answers:** [User's answers below]
   ---
   ```

3. **UPDATE DASHBOARD:** In `Features/feature_plan.md`, change status from `[Needs Clarification]` to `[Pending]`.

4. **REPORT:** "Ticket FEAT-$0 answers logged and status set to Pending. Feature is back in the implementation queue."

5. **STOP IMMEDIATELY.**

## User's Answers

$ARGUMENTS
