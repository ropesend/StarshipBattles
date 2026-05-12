---
name: codex-starship-qa-observer
description: Triage and review Starship Battles QA Observer sessions. Use for Tools/qa_observer session logs, qa-triage, qa-feedback, converting triage observations to projects, reviewing screenshots/logs, deduplicating against active tickets/projects, and deciding whether observations become bugs, features, projects, or no-ops.
---

# Codex Starship QA Observer

Use this skill for QA Observer session analysis and conversion work.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `Tools/qa_observer/README.md`.
3. Read `AgentCoordination/protocols/ticket_workflow.md` and `Projects/README.md` when creating or cross-referencing GitHub Issues/projects.
4. Read relevant `docs/` files before investigating code paths.

## Session Selection

- If the user gives a session id, use `Tools/qa_observer/session_data/<session_id>/`.
- If no session id is provided, inspect available session directories and use the newest one only when that is clearly the user's intent.
- Primary files are `QA_Session_Log.md`, `triage_summary.md`, `logs/`, screenshots, and `word_timestamps.jsonl` when present.

## Workflows

- Triage a session: inspect the session artifacts, classify each observation as bug, feature, project candidate, or no-op, and write evidence-backed conclusions.
- Review feedback for a session: compare user feedback against the triage summary, update conclusions where evidence supports it, and preserve rejected observations with rationale.
- Convert an accepted triage item into a project: use `Projects/protocols/01_initialize_project.md` and copy referenced images into the new project's findings assets folder.

## Rules

- Investigate code and logs before categorizing an observation.
- Deduplicate against open GitHub Issues using `gh issue list --state open --label "type:bug" --limit 200 --json number,title` and `gh issue list --state open --label "type:feature" --limit 200 --json number,title`, plus active projects.
- Ask for user confirmation before creating new tickets or projects unless the user explicitly requested creation.
- Copy referenced images into the target project findings assets folder when converting triage to a project.
- Never read `docs/_ignore/`.
- Keep triage conclusions grounded in evidence from logs, screenshots, code, and docs.
