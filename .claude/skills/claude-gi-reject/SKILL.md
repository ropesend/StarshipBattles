---
name: claude-gi-reject
description: Reject a fix and revert the issue to in-progress (e.g., /claude-gi-reject 127 <reason>)
disable-model-invocation: true
argument-hint: <issue-number> <reason>
---

# Reject GitHub Issue Fix

The user smoke-tested an `awaiting-confirmation` fix and found it inadequate.
Log the rejection reason and flip the issue back to `status:in-progress` so
the next work session re-attempts.

## Your Role

**QA Admin.** Record-keeping only.

## Arguments

Parse `$ARGUMENTS`: first token is the issue number; everything after is the
rejection reason.

**Input:** $ARGUMENTS

## Authority

You may:
- Post a rejection comment
- Atomic flip `status:awaiting-confirmation` → `status:in-progress`

You **MUST NOT**:
- Re-investigate or attempt a new fix in this skill
- Apply or remove any other labels

## Procedure

1. **VALIDATE** the issue currently has `status:awaiting-confirmation`. If
   not, ask the user whether to proceed (they may have meant a different
   issue).
2. **POST COMMENT** with a timestamp header:
   ```
   ### Rejection [YYYY-MM-DD HH:MM]
   <user reason, verbatim>
   ```
3. **STATUS TRANSITION** (atomic):
   ```bash
   gh issue edit <#> --remove-label "status:awaiting-confirmation" --add-label "status:in-progress"
   ```
4. **REPORT** comment URL + new label state.
5. **EXIT.** Do not attempt a new fix in this skill. The user invokes
   `/claude-gi-work <#>` or `/claude-gi-deep-dive <#>` to resume work.
