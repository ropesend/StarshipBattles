# PROJ-297 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/core/component_state.py` | Production | NEW — module moved from `game/strategy/data/component_state.py` |
| `game/strategy/data/component_state.py` | Production | DELETE — moved to core (no shim per Migration Policy) |
| `game/simulation/entities/ship_design_stats.py` | Production | EDIT — update import path |
| `game/strategy/data/ship_instance_bridge.py` | Production | EDIT — update import path |
| `game/strategy/data/ship_instance_serializer.py` | Production | EDIT — update import path |
| `game/strategy/data/ship_instance.py` | Production | EDIT — update import path |
| `game/strategy/combat/post_battle_hook.py` | Production | EDIT — update import path |
| `game/simulation/formula_system.py` | Production | DELETE — re-export shim, zero importers |
| `game/core/singleton.py` | Production | DELETE — zero production users |
| `game/core/__init__.py` | Production | EDIT (conditional) — remove `SingletonMeta` re-export if present |
| `tests/unit/core/test_component_state.py` | Test | NEW — TDD coverage of moved module |
| `tests/fixtures/strategy_entities.py` | Test | EDIT — update import path |
| `tests/unit/strategy/fleets/test_ship_instance_components.py` | Test | EDIT — update import path |
| `tests/unit/strategy/combat/test_spec_compiler.py` | Test | EDIT — update import path |
| `tests/unit/strategy/test_ship_instance_damage.py` | Test | EDIT — update import path |
| `tests/unit/strategy/ship_instance/test_cost_queries.py` | Test | EDIT — update import path |
| `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` | Test | EDIT — update import path |
| `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | Test | EDIT — update import path |
| `tests/unit/simulation/systems/test_ship_design_stats.py` | Test | EDIT — update import path |
| `tests/integration/save_load/test_roundtrip_ships.py` | Test | EDIT — update import path |
| `tests/unit/strategy/fleets/test_component_state.py` | Test | MOVE to `tests/unit/core/test_component_state.py` (or merge into the new TDD test file) |
| `tests/integration/strategy/combat/test_damage_persistence.py` | Test | EDIT — update import path |
| `tests/unit/strategy/combat/test_post_battle_hook.py` | Test | EDIT — update import path |
| `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py` | Test | EDIT — update import path |
| `tests/unit/ai/test_ai_protocols.py` | Test | DELETE or REPLACE — stale, fails collection |
| `tests/unit/ai/test_behavior_units.py` | Test | DELETE or REPLACE — stale, fails collection |
| `tests/unit/strategy/engine/test_build_order_command_handler.py` | Test | DELETE or REPLACE — stale, fails collection |
| `CLAUDE.md` | Docs | EDIT — pattern count (line 119), test baseline (line 312) |
| `docs/README.md` | Docs | EDIT — pattern count (lines 17, 66); add `resource_system.md` to reading table + tree |
| `docs/04_SERVICES.md` | Docs | EDIT — remove deprecated `ship_stats_calculator.py` entry; update `component_state.py` import path reference |
| `Reviews/scripts/calculate_agents.py` | Tooling | EDIT — replace bare `except:` at line 94 |
| `Tools/check_orphans/check_orphans.py` | Tooling | EDIT — replace bare `except:` at line 63 |
| `pyproject.toml` | Build | EDIT — add `radon` + `vulture` to dev deps |
