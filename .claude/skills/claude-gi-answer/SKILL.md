---
name: claude-gi-answer
description: Log user answers to clarification questions and re-queue the issue (e.g., /claude-gi-answer 127 <answers>)
disable-model-invocation: true
argument-hint: <issue-number> <answers>
---

# Answer Clarification Questions

Log the user's answers to questions an agent posted, and flip the issue back
to `status:pending` so it can be picked up again.

## Your Role

**Data Entry Clerk.** No analysis.

## Arguments

Parse `$ARGUMENTS`: first token is the issue number; everything after is the
answer text.

**Input:** $ARGUMENTS

## Authority

You may:
- Post a single answer comment
- Atomic flip `status:needs-clarification` → `status:pending`

You **MUST NOT**:
- Start working the issue
- Apply any other label changes

## Procedure

1. **VALIDATE** the issue exists and currently has `status:needs-clarification`.
   If it doesn't, ask the user whether to proceed anyway (the user may have
   meant a different issue).
2. **POST COMMENT** with a timestamp header:
   ```
   ### User Answer [YYYY-MM-DD HH:MM]
   <user text, verbatim>
   ```
   Use `--body-file`:
   ```bash
   gh issue comment <#> --body-file <tempfile.md>
   ```
3. **STATUS TRANSITION** (atomic):
   ```bash
   gh issue edit <#> --remove-label "status:needs-clarification" --add-label "status:pending"
   ```
4. **REPORT**:
   - Comment URL
   - New label state
5. **EXIT.** Do not start working the issue. The user invokes
   `/claude-gi-work <#>` or `/claude-gi-next` to resume work.
