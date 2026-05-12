# AgentCoordination/legacy_tickets/

**Read-only historical record. Do NOT cite these as current behavior.**

This directory holds the archived ticket files from the retired
`Tracking/` system, preserved as a narrative reference for future-developer
context (refactor history, past bug postmortems, design rationale that
predates the GitHub-Issues migration).

## Contents

| Path | What | Count |
|---|---|---|
| `bugs/` | Archived bug tickets (`BUG-XX.md`) | 135 markdown files |
| `bugs/*_logs/` | Per-ticket log directories nested with their bugs | 2 subdirs (BUG-110, BUG-112) |
| `bug_logs/` | Standalone log directories not nested with their archive | 4 subdirs (BUG-113, BUG-114, BUG-122, BUG-126) |
| `features/` | Archived feature tickets (`FEAT-XX.md`) | 28 markdown files |

Source: previously at `Tracking/bugs/archived/`, `Tracking/bugs/logs/`,
`Tracking/features/archived/`. Moved here on 2026-05-12 as part of the
legacy `Tracking/` system deprecation. See git log around commit
`AgentCoordination/Scratchpad/plans/deprecate_legacy_tracking_system_v2.md`.

## What lives here vs. what doesn't

**Lives here:**
- Ticket bodies (description, reproduction steps, work log, solution notes)
- Per-ticket log evidence captured during bug investigations
- Historical decisions and tradeoffs documented in solution sections

**Does NOT live here:**
- Active or in-flight ticket state — that lives on GitHub Issues
- Project-level multi-phase work — that lives on `Projects/active_projects/` (legacy) or GitHub Issues with `type:project` (`claude-gp-*`)
- Current architectural docs — read `docs/` for those, never these files

## Authoritative warning

Agents reading these files for context **must not** infer current
codebase behavior from them. Many tickets describe fixes that have
since been refactored, replaced, or re-fixed. Always cross-check
material claims against current code (`game/`, `tests/`, `docs/`)
before acting.

## Searching

```bash
# Find tickets mentioning a specific symbol/term:
grep -rln "<term>" AgentCoordination/legacy_tickets/

# Find tickets from a specific date range (filename has no date; use commit history):
git log --all --diff-filter=A --name-only -- 'AgentCoordination/legacy_tickets/bugs/BUG-*.md' \
  | grep BUG-

# For current ticket awareness, use GitHub Issues:
gh issue list --state open --label "type:bug" --limit 50
gh issue list --state closed --label "verified" --label "type:bug" --search "<term>" --limit 50
```

## Maintenance

This directory is **not maintained**. No new files. No edits to existing
files. If you need to record a follow-up insight about a past ticket, open
a new GitHub issue and reference the legacy ticket by filename in the
issue body.
