---
name: codex-starship-qa-observer
description: Triage and review Starship Battles QA Observer sessions. Use for Tools/qa_observer session logs, qa-triage, qa-feedback, converting triage observations to projects, reviewing screenshots/logs, deduplicating against active tickets/projects, and deciding whether observations become bugs, features, projects, or no-ops.
---

# Codex Starship QA Observer

Use this skill for QA Observer session analysis and conversion work.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `Tools/qa_observer/README.md`.
3. Read `Tracking/README.md` and `Projects/README.md` when creating or cross-referencing tickets/projects.
4. Read relevant `docs/` files before investigating code paths.

## Session Selection

- If the user gives a session id, use `Tools/qa_observer/session_data/<session_id>/`.
- If no session id is provided, inspect available session directories and use the newest one only when that is clearly the user's intent.
- Primary files are `QA_Session_Log.md`, `triage_summary.md`, `logs/`, screenshots, and `word_timestamps.jsonl` when present.

## Workflows

- Triage a session: follow the behavior from `.claude/skills/anti-qa-triage/SKILL.md`, adapted to Codex mechanics.
- Review feedback for a session: follow `.claude/skills/anti-qa-feedback/SKILL.md`, adapted to Codex mechanics.
- Convert an accepted triage item into a project: follow `.claude/skills/anti-triage-to-proj/SKILL.md` and `Projects/protocols/01_initialize_project.md`.

## Rules

- Investigate code and logs before categorizing an observation.
- Deduplicate against `Tracking/debug_plan.md`, `Tracking/feature_plan.md`, active tickets, and active projects.
- Ask for user confirmation before creating new tickets or projects unless the user explicitly requested creation.
- Copy referenced images into the target project findings assets folder when converting triage to a project.
- Never read `docs/_ignore/`.
- Keep triage conclusions grounded in evidence from logs, screenshots, code, and docs.
