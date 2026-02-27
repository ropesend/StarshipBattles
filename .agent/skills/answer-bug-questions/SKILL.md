---
name: answer-bug-questions
description: Log answers to clarification questions and return a bug to the fix queue
---

# Answer Bug Questions

**Protocol:** `Debugging/protocols/06_answer_questions.md`

Adopt the **QA Administrator** persona. Strictly record-keeping only.

## Execution

1. **LOCATE**: `Debugging/active_bugs/BUG-[ID].md`. Verify it has a `## Questions for User` section.

2. **LOG ANSWERS**: Append the user's answers to the end of the ticket:
   ```markdown
   ---
   ### Questions Answered [YYYY-MM-DD HH:MM]
   **Answers**: [User's answers]
   ---
   ```

3. **RESET STATUS**: Change status from `[Needs Clarification]` to `[Pending]` in `Debugging/debug_plan.md`.

4. **REPORT**: Confirm answers logged and bug is back in the fix queue.

**CRITICAL**: DO NOT write code, propose fixes, or analyze causes in this step.
