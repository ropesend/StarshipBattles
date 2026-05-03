---
name: claude-gi-next
description: Pick the highest-priority pending bug or feature and start working it (e.g., /claude-gi-next bug)
disable-model-invocation: true
argument-hint: bug|feature
---

# Work Next GitHub Issue

Find the highest-priority pending issue of the given type and invoke the
work workflow on it. Counterpart to `/claude-ticket-next`.

## Your Role

Same as `/claude-gi-work` (Senior Software Engineer) — this skill just picks
the issue for you.

## Arguments

Parse `$ARGUMENTS` as a single word: `bug` or `feature`.

**Input:** $ARGUMENTS

## Procedure

1. **QUERY** pending issues of the given type:
   ```bash
   gh issue list \
     --label "type:<bug|feature>" \
     --label "status:pending" \
     --limit 100 \
     --json number,title,labels,createdAt
   ```
2. **RANK** by priority (parse the `labels` array). Order:
   - `priority:critical` first
   - `priority:high`
   - `priority:medium`
   - `priority:low`
   - Within a priority bucket, oldest `createdAt` first.
3. **PICK** the top issue. If none exist, report "No pending <type> issues."
   and exit.
4. **REPORT** which issue you're about to work on:
   ```
   Working on #NNN: <title> (priority:<P>, age: <N> days)
   ```
5. **DELEGATE** to the work workflow. Either:
   - Load and follow `.claude/skills/claude-gi-work/SKILL.md`, OR
   - Tell the user you're handing off and the user invokes
     `/claude-gi-work <#>` directly.

In automated/agent contexts, prefer the first option (continue inline).
