---
name: claude-di-triage
description: Triage the shared discovered-issues log — verify entries against current code, recommend disposition (still valid, drifted, already fixed, non-issue), and prune resolved entries (e.g., /claude-di-triage [--severity high] [--category bug]).
disable-model-invocation: true
argument-hint: [--agent X] [--category Y] [--severity Z] [--auto-prune-resolved]
---

# Triage Discovered Issues

Review the shared discovered-issues inbox at
`AgentCoordination/discovered_issues/log.jsonl`, decide which entries are
still actionable, and prune the rest. Surviving entries should be promoted
to GitHub issues (`/claude-gi-add`) or a project (`/claude-gp-add`,
`/claude-proj-start`) per the user's preference.

## Your Role

**Triage analyst.** No coding. For each entry, determine whether the
underlying issue still exists in the current code, decide its disposition,
and act (prune or escalate).

## Input

`$ARGUMENTS` — optional filters that get forwarded to the helper:
`--agent`, `--category`, `--severity`. Plus your own optional flag
`--auto-prune-resolved` (act on `snippet-gone` / `file-gone` without asking).

## Procedure

1. **LOAD** the log with verification:
   ```bash
   python Tools/agent_coordination/triage_discovered_issues.py \
     --format jsonl \
     [filter flags from $ARGUMENTS]
   ```
   Each line is the original entry plus `_verdict`, `_verdict_detail`, and
   (when applicable) `_current_line`.
2. **BUCKET** entries by verdict:
   - `match-exact` / `match-drifted` → likely still valid. Read the
     current code at `_current_line` (or `line`) and confirm the
     description still describes a real issue.
   - `match-elsewhere` → snippet exists but far from the recorded line.
     Read the new location; the original issue may have been moved,
     duplicated, or refactored.
   - `snippet-gone` → file exists but the snippet does not. Almost always
     means the issue was fixed. Confirm by quickly re-reading the file.
   - `file-gone` → file was deleted/renamed. Almost certainly resolved
     (or the path moved — check git history if the issue still seems
     plausible).
3. **DECIDE** per entry:
   - **Resolved / non-issue** → prune (see step 4).
   - **Still valid, minor** → prune and tell the user inline; or, if the
     batch is large, group similar ones.
   - **Still valid, worth tracking** → flag for promotion. Do NOT file
     anything yourself unless the user has asked you to.
4. **PRUNE** in batch:
   ```bash
   python Tools/agent_coordination/triage_discovered_issues.py \
     --prune DI-… DI-… DI-…
   ```
   Git history preserves the removed entries — there is no archive file.
5. **REPORT** a short summary to the user:
   - Total entries inspected.
   - Counts per disposition (resolved / still-valid / needs-decision).
   - For still-valid entries: a one-line description + id + file:line.
   - Recommend next-step skills: `/claude-gi-add bug …` for individual
     bugs, `/claude-gp-add` or `/claude-proj-start` for clustered themes.

## Guardrails

- Do NOT prune `match-exact` / `match-drifted` / `match-elsewhere` entries
  without the user agreeing, unless they invoked `--auto-prune-resolved`
  with intent (which only authorizes `snippet-gone` / `file-gone`).
- Do NOT file GitHub issues without an explicit user instruction. Triage
  surfaces; the user decides.
- Do NOT touch the log file directly — always use the helper.
- If the log is empty: say so and exit.
