---
name: claude-di-log
description: Record a cross-task discovered issue in the shared log without derailing the current task (e.g., /claude-di-log file:line category — description). Used when an agent notices an unrelated issue while working on something else.
disable-model-invocation: true
argument-hint: <file>:<line> <category> — <description> [| suggested: <fix>]
---

# Log Discovered Issue

Record one out-of-scope issue you noticed while working on a different task.
The log is shared across all agents and lives at
`AgentCoordination/discovered_issues/log.jsonl`.

This skill is for **drive-by findings only**. If the issue is part of what you
are already working on, just fix it — do not log.

## Your Role

**Inbox clerk.** Capture the finding cleanly, then return to the task at hand.
Do NOT investigate further, file a GitHub issue, or fix the issue here.

## Input

`$ARGUMENTS` — the user (or you, mid-task) supplies a free-form description
that should contain at minimum: a file path, a line number, a category, and
a description. The user may use shorthand like `path/to/file.py:42 bug — ...`.

## Procedure

1. **PARSE** the input into the helper's required fields:
   - `--file` (repo-relative path)
   - `--line` (int)
   - `--category` — one of `bug`, `security`, `perf`, `test-gap`,
     `dead-code`, `doc`, `convention`, `tech-debt`. If unclear, default
     to `bug`.
   - `--severity` — `low` | `medium` | `high`; default `medium`.
   - `--description` — durable explanation. Quote the problem precisely
     enough that a future reader does not need to re-discover the issue.
   - `--suggested-action` (optional) — only include if you have a concrete
     recommendation.
   - `--symbol` (optional) — the enclosing function/class name.
   - `--source-task` — what you were doing when you noticed this. Use the
     active issue/project ID if you have one (e.g., `PROJ-437 Phase 3`,
     `GH#142`, or a short phrase like `combat refactor`).
2. **CHECK** that the file exists and the line number is sensible before
   calling the helper. The helper will fail loudly otherwise.
3. **RUN** the helper:
   ```bash
   python Tools/agent_coordination/log_discovered_issue.py \
     --agent claude \
     --source-task "<your current task>" \
     --file "<repo/relative/path>" \
     --line <N> \
     --category <cat> \
     --severity <sev> \
     --description "<…>" \
     --suggested-action "<…optional…>" \
     --symbol "<…optional…>"
   ```
4. **REPORT** the returned id (e.g., `DI-2026-05-18-007`) back to the user
   in one short line, and return to whatever you were doing.

## Guardrails

- Do NOT log something you are about to change in the current task — fix it.
- Do NOT log subjective style preferences.
- Do NOT log speculative refactors with no concrete problem.
- Do NOT investigate further. If the finding warrants investigation,
  surface it to the user as "worth a deeper look" *and* log it.
- Skim `AgentCoordination/discovered_issues/log.jsonl` first only if you
  suspect a duplicate is already recorded for the same file+line. Do not
  read the whole file unless it is small.
