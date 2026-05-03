---
name: claude-gi-add
description: Create new bug or feature GitHub issue(s) (e.g., /claude-gi-add bug <descriptions> or /claude-gi-add feature <descriptions>)
disable-model-invocation: true
argument-hint: bug|feature <descriptions>
---

# Add GitHub Issue

Create one or more GitHub issues from the user's raw description(s). This is
the GitHub-Issues counterpart to `/claude-ticket-add`. Both systems run in
parallel; use this one for any new ticket.

## Your Role

**Project Manager.** No coding — data entry only. Translate the user's
description into a clean issue body and apply correct labels.

## Arguments

Parse the first word of `$ARGUMENTS` as the ticket type (`bug` or `feature`).
Everything after is one or more descriptions. If multiple descriptions are
present (separated by clear paragraph breaks or numbered list), create one
issue per description.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| TYPE_LABEL | `type:bug` | `type:feature` |
| TEMPLATE | `bug` (`.github/ISSUE_TEMPLATE/bug.yml`) | `feature` (`.github/ISSUE_TEMPLATE/feature.yml`) |

## Authority

You may:
- Create issues
- Apply `type:*`, `priority:*`, `status:pending` labels
- Post the initial body

You **MUST NOT**:
- Apply the `verified` label (user-only)
- Close any issue (user-only)
- Apply any `status:*` other than `status:pending` at creation time

## Procedure

1. **PARSE** $ARGUMENTS into ticket type + N descriptions.
2. **For each description:**
   - Derive a concise title (≤72 chars) from the first sentence.
   - Build the body using the template's section headings:
     - `## Description` — the user's prose
     - `## Steps to Reproduce` (bugs only) — if the user gave any
     - `## Expected vs Actual` (bugs only) — if extractable
     - `## Acceptance Criteria` — leave a placeholder if the user didn't supply
     - `## Priority` — inferred per the guidelines below
   - Determine priority label:
     - **Bug priority:** `critical` (crashes/blocks core gameplay) | `high` (significant feature broken) | `medium` (minor/visual) | `low` (polish/QoL)
     - **Feature priority:** `critical` (required for release) | `high` (significant impact) | `medium` (nice-to-have) | `low` (minor enhancement)
3. **CREATE** the issue:
   ```bash
   gh issue create \
     --title "<title>" \
     --body-file <tempfile.md> \
     --label "<TYPE_LABEL>" \
     --label "priority:<P>" \
     --label "status:pending"
   ```
   Use `--body-file` (not `--body`) so multi-paragraph bodies don't run into
   shell-quoting trouble. Write the body to a tempfile, create the issue,
   then delete the tempfile.
4. **CAPTURE** the issue number that `gh issue create` prints to stdout.
5. **REPORT** to the user:
   - Each issue number created (one per ticket)
   - The URL of each issue (`gh issue view <#> --json url -q .url`)
   - The labels applied
6. **EXIT.** Do not start any analysis, planning, or implementation. The
   user invokes `/claude-gi-work <#>` separately when ready.

## Notes

- Screenshots and logs referenced in the description: do **not** upload them
  via the issue body at creation time. The user will commit them to
  `tracking-assets/` and add a comment with the link, or invoke
  `/claude-gi-update <#>` later.
- If the description is ambiguous about type (could be a bug or a feature),
  ask the user before creating; do not guess.
