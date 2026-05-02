---
name: claude-gi-batch-close
description: Archive multiple confirmed GitHub issues (e.g., /claude-gi-batch-close 127 128 130). USER-ONLY authority.
disable-model-invocation: true
argument-hint: <issue-number> [<issue-number> ...]
---

# Batch Close GitHub Issues

Close multiple `status:awaiting-confirmation` issues in one go. Counterpart to
`/claude-ticket-batch-close`.

## Your Role

**Librarian (batch).** **User-only** authority — same constraints as
`/claude-gi-close`. Refuse if invoked by an autonomous agent.

## Arguments

Parse `$ARGUMENTS` as a whitespace-separated list of issue numbers.

**Input:** $ARGUMENTS

## Authority

Identical to `/claude-gi-close`, applied to N issues.

## Pre-Flight: Confirm the Caller

If you're an autonomous agent, **stop**. Surface the list of awaiting-
confirmation issues and ask the user to invoke this skill themselves.

## Procedure (user-invoked)

1. **VALIDATE** every issue in the list:
   ```bash
   for n in <numbers>; do
     gh issue view "$n" --json number,state,labels
   done
   ```
   Confirm each is open and has `status:awaiting-confirmation`. Skip any
   that don't qualify, and report which were skipped + why.
2. **CLOSE EACH ISSUE** that qualifies:
   ```bash
   gh issue edit "$n" --add-label "verified"
   gh issue close "$n" --reason completed
   ```
3. **REPORT**:
   - List of closed issue numbers
   - List of skipped issue numbers with reason
   - Any errors encountered

## Constraints

- **Atomic per issue, not per batch.** If a single close fails, continue with
  the rest and report the failure — don't roll everything back.
- **Same `verified`-then-`close` ordering** as `/claude-gi-close`.
