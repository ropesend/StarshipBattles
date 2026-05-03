---
name: claude-gi-update
description: Append context to an issue without analysis (e.g., /claude-gi-update 127 <text>)
disable-model-invocation: true
argument-hint: <issue-number> <text>
---

# Update GitHub Issue

Append a new comment to an issue with user-supplied context. Pure data entry —
no analysis, no status changes, no implementation. Counterpart to
`/claude-ticket-update`.

## Your Role

**Data Entry Clerk.** Verbatim transcription only.

## Arguments

Parse `$ARGUMENTS`: first token is the issue number; everything after is the
update text.

**Input:** $ARGUMENTS

## Authority

You may:
- Post a single comment with the supplied text

You **MUST NOT**:
- Modify any labels
- Edit the issue body
- Start any analysis or implementation

## Procedure

1. **VALIDATE** the issue exists:
   ```bash
   gh issue view <#> --json number,state -q .state
   ```
   If state is `CLOSED`, ask the user whether to reopen or attach the update
   to a new issue. Do not proceed silently.
2. **POST COMMENT**:
   - Build a comment body that opens with a timestamp header:
     ```
     ### User Update [YYYY-MM-DD HH:MM]
     <user text, verbatim>
     ```
   - Write to a tempfile, then:
     ```bash
     gh issue comment <#> --body-file <tempfile.md>
     ```
3. **REPORT** the comment URL:
   ```bash
   gh issue view <#> --json url -q .url
   ```
4. **EXIT.** No status changes.
