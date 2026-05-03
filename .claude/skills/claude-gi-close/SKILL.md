---
name: claude-gi-close
description: Archive a confirmed GitHub issue — apply verified label and close (e.g., /claude-gi-close 127). USER-ONLY authority.
disable-model-invocation: true
argument-hint: <issue-number>
---

# Close GitHub Issue

Final closure of an issue after the user has verified the fix or feature.
Counterpart to `/claude-ticket-close`.

## Your Role

**Librarian.** This skill exists for the **user only**. Agents may **not**
invoke this skill autonomously, even in batch mode. The architectural
separation between "agent sets awaiting-confirmation" and "user closes" is
the project's primary safeguard against premature closure.

## Arguments

Parse `$ARGUMENTS` as a single issue number.

**Input:** $ARGUMENTS

## Authority

You may (when invoked by the user):
- Apply the `verified` label
- Close the issue

You **MUST NOT** (when invoked by an autonomous agent):
- Run any of the steps below. Refuse and tell the user the issue is ready
  for them to close manually.

## Pre-Flight: Confirm the Caller

If you're an autonomous agent (running in batch / continue mode / background),
**stop immediately** and surface the issue number + status to the user. Do not
execute the close steps. Suggest the user invoke this skill themselves.

## Procedure (user-invoked)

1. **VALIDATE** the issue currently has `status:awaiting-confirmation`. If
   not, ask the user to confirm before proceeding (an issue without
   awaiting-confirmation has not been worked, or has been rejected).
2. **APPLY VERIFIED LABEL**:
   ```bash
   gh issue edit <#> --add-label "verified"
   ```
3. **CLOSE THE ISSUE**:
   ```bash
   gh issue close <#> --reason completed
   ```
4. **REPORT**:
   - Final issue URL
   - Confirmation that closure succeeded
5. **EXIT.**

## Notes

- The `verified` label persists on closed issues; it serves as a marker that
  closure went through the proper flow. If you ever see a closed issue
  without `verified`, it was either closed through an unauthorized path or
  closed before this skill existed.
- If you need to reopen later, `gh issue reopen <#>` restores all labels and
  state intact. You can then strip `verified` and proceed.
