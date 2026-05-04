# AGENTS.md — Starship Battles

Compact reference for AI coding agents. See `docs/` for full architecture, patterns, and conventions.

## Non-Negotiable Rules

1. **Strict TDD.** Write (or identify) the failing test first, run it to confirm failure, then implement. No exceptions.
2. **Read docs before coding.** Start at `docs/README.md`, always read `01_ARCHITECTURE.md`, `02_PATTERNS.md`, `03_CONVENTIONS.md`, plus task-specific docs.
3. **Keep code and docs consistent.** Update docs in the same change when behavior/architecture changes.
4. **Root cause fixes only.** No compatibility shims, fallback systems, monkey patches, or duplicate logic.
5. **Never read `docs/_ignore/`.** It is not documentation.
6. **Don't revert unrelated changes.** Check `git status --short` before editing and work around existing changes.

## Commands

```bash
# Full test suite (primary)
python Tools/test_sharded/test_sharded.py

# Incremental tests (changed files only)
pytest tests/ --testmon

# Single test
pytest tests/path/to/test.py -k test_name

# Combat Lab tests
python -m combat_lab.run_tests

# Code shrinkage audit (read-only analysis)
python Tools/audit_shrink/audit_shrink.py   # Phase 1: deterministic tools
# Then /ocode-audit-shrink                         # Phase 2: agents + report
```

## Architecture (Quick Reference)

Layered, bottom-up: **Core / Services / Assets / Engine → Simulation / Research → Strategy / AI → UI**.

- `game/core/` — No dependencies. Registries, validation, protocols, hex math, formula engine.
- `game/services/` — Depends on Core only. Cross-cutting infrastructure, currently LLM provider services.
- `game/assets/` — Depends on Core + Services. Asset managers and generated image derivative tooling.
- `game/engine/` — Depends on Core + Services. Low-level physics, collision detection, spatial indexing.
- `game/simulation/` — Depends on Core + Services + Engine. Combat engine, components, abilities, modifiers, entities.
- `game/research/` — Depends on Core + Services. Tech tree and research mechanics.
- `game/strategy/` — Depends on Core + Services + Engine + Simulation. Galaxy map, fleets, planets, economy, turn engine, facade.
- `game/ai/` — Depends on Core + Services + Engine + Simulation. Behaviors, targeting, spatial navigation.
- `game/ui/` — Depends on all. Pygame screens, panels, widgets, renderer.

Key patterns: Registry, ApplicationContext DI (`game/context.py` manages 10 services), Facade/Delegate, CQRS-lite, two-phase ability aggregation, Habitability Factor Registry (single-source-of-truth for all habitability axes).

## Critical Conventions

- **Python 3.14**. Return-type annotations required on every public function/method (PEP 604 syntax: `int | None`). Dunders exempt.
- **500 LOC ceiling on production files.** When a file approaches 500 lines, split into single-responsibility sub-modules. Test files exempt.
- **Specific exceptions required.** Broad catches (`except Exception`) must carry `# Intentional broad catch: <reason>` on the same line.
- **No save-file migration.** Old saves are disposable. Never write compatibility shims for old save formats.
- **Repo-root discovery for agent tooling.** Agent skills, protocols, daemon prompts, and coordination scripts must resolve the repository root at runtime. Never hardcode machine-specific checkout paths like `c:\Dev\Starship Battles`.
- **Spatial terminology:** A "System" (star system) is ~8000 hexes around a star (radius 50). A "Sector" is a single hex. "System scope" = star-system-wide; "Sector scope" = single-hex. Don't confuse them.
- **Minimum resolution:** 2560x1600. Optimized for 4K (3840x2160).

## Test Infrastructure

- `conftest.py` force-sets `SDL_VIDEODRIVER=dummy` before imports — tests run headless.
- `reset_game_state` fixture (autouse function-scoped) clears singletons, hydrates registries from session cache.
- Session-scoped registries via `session_registries` fixture. Function-scoped variant: `fresh_registries`.
- Repo-wide test baseline lives in `AgentCoordination/generated/test_baseline.json`. Known flakes: `test_colony_owner_id_matches_empire` (test-isolation) and some `test_fleet_operations.py` resource-accumulation tests. If 1-4 random failures appear in those areas, re-run before triaging.

## Tooling Notes

- **`Tools/test_sharded/`** — Sharded parallel runner. Auto-detects CPU count with greedy load balancing from `.test_durations.json`. This is the canonical full-suite runner.
- **`Tools/audit_shrink/`** — Code shrinkage audit: vulture (dead code), radon (complexity), clone detector (near-duplicate functions), orphan/dependency analysis. See `.opencode/skills/ocode-audit-shrink/SKILL.md` for the agent-driven Phase 2 workflow.
- **`requirements-dev.txt`** includes radon, vulture, Pillow, numpy, opencv-python, matplotlib, fastapi, uvicorn, dearpygui, and QA tooling. Runtime-only deps in `requirements.txt`.

## Project Management

- Active projects: `Projects/active_projects/PROJ-XX/`. Protocols: `Projects/protocols/`.
- Tickets (legacy, parallel): `Tracking/bugs/active/` and `Tracking/features/active/`. Protocols: `Tracking/protocols/`. Skills: `/claude-ticket-*`.
- Tickets (GitHub Issues, parallel): https://github.com/ropesend/StarshipBattles/issues. Skills: `/claude-gi-*`. New tickets should go here unless the legacy system is more convenient. Both systems run side-by-side; legacy will be sunset on user signal.
- Reviews: `Reviews/protocols/` and `Reviews/results/`. Historical audit reports stored here.
- Archive: `Projects/archived_projects/` and `Projects/deep_archive/` — do not reference as current.
- Scratchpad: `AgentCoordination/Scratchpad/` (gitignored) — transient agent files. Subdirs: `plans/`, `reviews/`, `reports/`, `handoffs/`, `tmp/`. **Do not write transient files outside the repo.** Persist-worthy artifacts go in tracked dirs (`Projects/`, `docs/`, `Reviews/results/`). Full rules: `AgentCoordination/SCRATCHPAD.md`.

## Skill Usage Logging

**Claude Code logs ALL skill invocations automatically** (prefixed `claude-*` and
builtins like `loop`, `simplify`, `review`) via the `UserPromptExpansion` and
`PreToolUse(Skill)` hooks wired in `.claude/settings.json` →
`Tools/agent_coordination/claude_skill_usage_hook.py`. No manual call required.

Other agents call the script explicitly because their hook surfaces are
narrower (Codex has no skill event; OpenCode's plugin hooks don't expose a
skill-invoked event in the declarative config; Antigravity is lower
priority):

```bash
python Tools/agent_coordination/log_skill_usage.py --agent <claude|anti|ocode|codex> --skill <full-prefixed-skill-name>
```

Examples:
- Codex invoking `$codex-starship-project-system` → `python Tools/agent_coordination/log_skill_usage.py --agent codex --skill codex-starship-project-system`
- OpenCode invoking `/ocode-audit-shrink` → `python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-audit-shrink`
- Antigravity invoking an `anti-*` skill → `python Tools/agent_coordination/log_skill_usage.py --agent anti --skill <name>`
- Claude Code (manual override or testing) → same script with `--agent claude`.

Counters are **advisory only** and identify cleanup candidates; they never authorize automatic deletion. Counter data is per-checkout (a UUID install ID is auto-generated on first call); the aggregated `summary.json` is the artifact a human reviews for cross-checkout totals.

Each logging invocation updates the per-install counter at
`AgentCoordination/generated/skill_usage/by_install/<install_id>.json` (tracked,
no cross-checkout conflicts because filenames are UUIDs) and rewrites the
aggregated `AgentCoordination/generated/skill_usage/summary.json` (**gitignored**;
purely derived from the per-install files, regenerated on every skill use).
