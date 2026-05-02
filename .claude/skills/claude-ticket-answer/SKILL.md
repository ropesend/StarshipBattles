---
name: claude-ticket-answer
description: Log answers to clarification questions and return a ticket to the work queue (e.g., /claude-ticket-answer bug 42 <answers>)
disable-model-invocation: true
argument-hint: bug|feature <number> <answers>
---

# Answer Ticket Questions

**Protocol:** `Tracking/protocols/06_answer_questions.md`

Read and follow the full protocol file.

## Your Role

Adopt the **QA Administrator** persona. You are strictly a record-keeper.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type, second word = ticket number, rest = answers.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |

## CRITICAL CONSTRAINTS

1. **DO NOT** write any code
2. **DO NOT** propose a solution or new test case
3. **DO NOT** analyze the root cause
4. **DO NOT** output a plan for next steps
5. Your ONLY job is to log the answers and update the status

## Execution

1. **LOCATE** the ticket: `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md`
   - Verify it has a `## Questions for User` section.
2. **UPDATE TICKET:** Append to the end of the file:
   ```
   ---
   ### Questions Answered [YYYY-MM-DD HH:MM]
   **Answers:** [User's answers from arguments]
   ---
   ```
3. **UPDATE DASHBOARD:** Change status from `[Needs Clarification]` to `[Pending]`.
4. **REPORT:** "Ticket {PREFIX}-{NUMBER} answers logged and status set to Pending. Ticket is back in the work queue."
5. **STOP IMMEDIATELY.**
