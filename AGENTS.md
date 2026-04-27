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
# Activate venv first
.venv\Scripts\Activate.ps1

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
# Then /audit-shrink                         # Phase 2: agents + report
```

## Architecture (Quick Reference)

Layered, bottom-up: **Core → Simulation → Strategy → UI** (+ AI depends on Simulation and Strategy).

- `game/core/` — No dependencies. Registries, validation, protocols, hex math, formula engine.
- `game/simulation/` — Depends on Core. Combat engine, components, abilities, modifiers, entities.
- `game/strategy/` — Depends on Core + Simulation. Galaxy map, fleets, planets, economy, turn engine, facade.
- `game/ui/` — Depends on all. Pygame screens, panels, widgets, renderer.
- `game/ai/` — Depends on Simulation + Strategy. Behaviors, targeting, spatial navigation.

Key patterns: Registry, ApplicationContext DI (`game/context.py` manages 9 services), Facade/Delegate, CQRS-lite, two-phase ability aggregation, Habitability Factor Registry (single-source-of-truth for all habitability axes).

## Critical Conventions

- **Python 3.13+**. Use `.venv`. Return-type annotations required on every public function/method (PEP 604 syntax: `int | None`). Dunders exempt.
- **500 LOC ceiling on production files.** When a file approaches 500 lines, split into single-responsibility sub-modules. Test files exempt.
- **Specific exceptions required.** Broad catches (`except Exception`) must carry `# Intentional broad catch: <reason>` on the same line.
- **No save-file migration.** Old saves are disposable. Never write compatibility shims for old save formats.
- **Spatial terminology:** A "System" (star system) is ~8000 hexes around a star (radius 50). A "Sector" is a single hex. "System scope" = star-system-wide; "Sector scope" = single-hex. Don't confuse them.
- **Minimum resolution:** 2560x1600. Optimized for 4K (3840x2160).

## Test Infrastructure

- `conftest.py` force-sets `SDL_VIDEODRIVER=dummy` before imports — tests run headless.
- `reset_game_state` fixture (autouse function-scoped) clears singletons, hydrates registries from session cache.
- Session-scoped registries via `session_registries` fixture. Function-scoped variant: `fresh_registries`.
- 15477+ tests baseline. Known flakes: `test_colony_owner_id_matches_empire` (test-isolation) and some `test_fleet_operations.py` resource-accumulation tests. If 1-4 random failures appear in those areas, re-run before triaging.

## Tooling Notes

- **`Tools/test_sharded/`** — Sharded parallel runner. Auto-detects CPU count with greedy load balancing from `.test_durations.json`. This is the canonical full-suite runner.
- **`Tools/audit_shrink/`** — Code shrinkage audit: vulture (dead code), radon (complexity), clone detector (near-duplicate functions), orphan/dependency analysis. See `.opencode/skills/audit-shrink/SKILL.md` for the agent-driven Phase 2 workflow.
- **`requirements-dev.txt`** includes radon, vulture, Pillow, numpy, opencv-python, matplotlib, fastapi, uvicorn, dearpygui, and QA tooling. Runtime-only deps in `requirements.txt`.

## Project Management

- Active projects: `Projects/active_projects/PROJ-XX/`. Protocols: `Projects/protocols/`.
- Tickets: `Tracking/bugs/active/` and `Tracking/features/active/`. Protocols: `Tracking/protocols/`.
- Reviews: `Reviews/protocols/` and `Reviews/results/`. Historical audit reports stored here.
- Archive: `Projects/archived_projects/` and `Projects/deep_archive/` — do not reference as current.
