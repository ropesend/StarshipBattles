# PROJ-306 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### EDIT
| File | Type | Notes |
|------|------|-------|
| `game/simulation/battle_runner.py` | Production | Delete `_default_ship_builder_from_context()` (~lines 170-220); update `run_battle` / `BattleController.start_from_spec` signatures per chosen pattern |
| `game/simulation/services/registry_loader.py` | Production | Make `registry_provider` required (or context-fetch); delete line-91 fallback call |
| `game/simulation/battle_controller.py` | Production | If `start_from_spec` lives here, update its signature too |
| Caller sites | Production | TBD — Phase 1.1 inventory will enumerate |
| `docs/01_ARCHITECTURE.md` | Docs | Remove/update transitional-fallback mentions |
| `docs/04_SERVICES.md` | Docs | Same |

### NEW
| File | Type | Notes |
|------|------|-------|
| `tests/unit/simulation/test_battle_runner_di.py` | Test | TDD contract for the new ship_builder requirement (NEW or extend) |
| `tests/unit/simulation/services/test_registry_loader.py` | Test | TDD contract for the registry_provider requirement (NEW or extend) |
| `Projects/active_projects/PROJ-306/findings/caller_inventory.md` | Project artifact | Phase 1.1 deliverable |
| `Projects/active_projects/PROJ-306/findings/registry_loader_callers.md` | Project artifact | Phase 2.1 deliverable |

### EXPLICITLY EXCLUDED
- `game/core/protocols.py:38` `TYPE_CHECKING` import of `RaceConfig` — documented unavoidable trade-off; not a violation in practice
