# Codex Adapter

This file is the Codex-specific supplement for Starship Battles. Read it after `AGENTS.md` and before code work in this repository.

## Scope

- Codex-specific skills are repo-local under `.agents/skills/` and are prefixed `codex-`.
- Do not use `.claude/skills/` or `.agent/skills/` as active Codex skills. Read them only when the user asks to compare, migrate, or audit agent setup.
- Keep Codex behavior thin: skills should route to shared project docs and protocols rather than duplicating long workflow text.
- Repo-local Codex configuration lives in `.codex/config.toml`. Local Codex artifacts under `.codex/` remain ignored except that config file.

## Startup Checklist

1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/README.md` and the required docs listed there before code work.
4. Check `git status --short` before editing.
5. If `rg` is blocked or unavailable on Windows, use PowerShell `Get-ChildItem` and `Select-String`.

## Skill Routing

- `$codex-starship-ticket-system`: bug and feature tickets in `Tracking/`.
- `$codex-starship-project-system`: `PROJ-XX` planning, continuation, review, audit, revision, extraction, and closure.
- `$codex-starship-analysis-review`: dead code, complexity, architecture sweeps, and focused reviews.
- `$codex-starship-qa-observer`: QA Observer session triage, feedback, and conversion to projects.
- `$codex-starship-combat-lab`: Combat Lab scenarios, ability tests, simulation fixtures, and validation.
- `$codex-starship-design-assets`: design validation and asset/tool workflows.
- `$codex-ship-theme-creator`: complete Starship Battles ship theme generation.

Use the skill that matches the user request. If no skill matches, follow `AGENTS.md` and the project docs directly.

## Codex Operating Notes

- Prefer repo-local scripts and protocols over ad hoc workflows.
- Use `apply_patch` for manual edits.
- Do not spawn subagents unless the current Codex client supports them and the user has explicitly asked for parallel or delegated work. If a protocol expects parallel agents but that is not available, run the review sequentially and state the limitation.
- For OpenAI API, Codex, or model questions, use the `openaiDeveloperDocs` MCP server configured in `.codex/config.toml` when available.
- After changing Codex skills or config, run the skill validator on changed skill folders.

## Skill Usage Logging

Every time you invoke a `codex-*` skill, call the usage counter once with `--agent codex`:

```bash
python Tools/agent_coordination/log_skill_usage.py --agent codex --skill <full-prefixed-skill-name>
```

The script auto-creates a per-checkout install ID and increments the counter in `AgentCoordination/generated/skill_usage/by_install/<install_id>.json`. See `AGENTS.md §"Skill Usage Logging"` for full context. Counters are advisory only.
