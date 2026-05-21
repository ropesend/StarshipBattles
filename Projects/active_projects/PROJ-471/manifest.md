# PROJ-471 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
> **Status legend after scope revision + implementation (2026-05-21):** DONE = implemented + tested; DROPPED/DEFERRED = removed from PROJ-471 scope (see decisions.md); NOT DONE = surviving but not implemented this session.

**Production — DONE**
| `game/simulation/combat/combat_subsystems.py` | Production | NEW (Task 1.2): per-battle `CombatSubsystems` bundle (targeting/damage/firing) |
| `game/simulation/entities/ship_combat_engine.py` | Production | DONE Task 1.2: class-shared subsystems → per-instance via bundle injection |
| `game/simulation/entities/ship_combat_manager.py` | Production | DONE Task 1.2: `set_combat_subsystems` + bundle threading at lazy engine construction |
| `game/simulation/entities/ship.py` | Production | DONE Task 1.2: `set_combat_subsystems` facade |
| `game/simulation/systems/battle_engine.py` | Production | DONE Task 1.2: owns per-battle `combat_subsystems`; injects into ships; ram/mine lookups read the bundle; removed obsolete class-level event-bus wiring |
| `game/simulation/systems/battle_setup.py` | Production | DONE Task 1.2: builds seeded per-battle bundle on engine (was class-attr overwrite). Manifest path corrected from wrong `entities/battle_setup.py` |
| `game/simulation/components/component_loader.py` | Production | DONE Task 2.1 + 4.2: `set_default_cache_manager()`; `reset_component_caches()` clears in place (no ctx divergence) |
| `game/ai/policy_manager.py` | Production | DONE Task 2.2: `set_default_policy_manager()` |
| `game/context.py` | Production | DONE Tasks 2.1/2.2: route cache/policy setters (no raw attr-assign) |
| `game/ui/screens/battle_setup_state.py` | Production | DONE Task 2.8 + 4.1: per-state `itertools.count` fleet-id allocator; `from_dict` advances past loaded ids |
| `game/core/json_utils.py` | Production | DONE Task 2.9: `clear_serializable_registry()` seam |
| `game/ui/screens/transfer_mass_preview.py` | Production | DONE Task 2.10: `_clear_catalog()` invalidation hook |
| `game/simulation/entities/stat_contributors/registry.py` | Production | DONE Task 3.4: `reset_crew_priority_registry()` seam |
| `conftest.py` | Test | DONE Task 3.4: wired `reset_crew_priority_registry()` into pre-test + teardown |

**Production — DROPPED / DEFERRED / NOT DONE**
| `game/core/registry.py` | Production | `_default_provider` Task 1.1 DROPPED (false positive). `_default_manager` dual-pattern Task 2.3 NOT DONE (doc decision) |
| `game/ui/assets/ship_theme_manager.py` | Production | Task 2.4 (15 consumers) NOT DONE |
| `game/assets/asset_manager.py` | Production | Task 2.5 (7 consumers) NOT DONE |
| `game/ui/renderer/sprites.py` | Production | Task 2.6 NOT DONE |
| `game/services/llm/defaults.py`, `.../panel_factory.py` | Production | Tasks 2.7/3.3 NOT DONE |
| `game/strategy/engine/game_initializer.py` | Production | Task 2.11 DEFERRED → PROJ-473 |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | Production | Task 2.12 DEFERRED → PROJ-473 |
| `game/exit_dialog.py` | Production | Task 2.13 NOT DONE (lowest-priority "drop first" MAJOR) |
| `game/ui/services/game_settings.py`, `.../image/defaults.py` | Production | Task 3.1 DROPPED (not dead) |
| `game/core/profiling.py` | Production | Task 3.2 NOT DONE (design-cleanup eval) |

**Tests (new)**
| `tests/unit/simulation/ship_combat_engine/test_subsystem_isolation.py` | Test | Task 1.2 per-instance isolation + bundle injection |
| `tests/unit/simulation/systems/test_battle_combat_subsystems.py` | Test | Task 1.2 + 4.3 per-battle bundle determinism + battle-outcome equivalence |
| `tests/unit/simulation/components/test_cache_manager_setter.py` | Test | Task 2.1 + 4.2 setter + no-ctx-divergence |
| `tests/unit/ai/test_policy_manager_setter.py` | Test | Task 2.2 setter |
| `tests/unit/ui/screens/test_battle_setup_fleet_id_isolation.py` | Test | Task 2.8 + 4.1 fleet-id isolation + no post-load collision |
| `tests/unit/core/test_serializable_registry_seam.py` | Test | Task 2.9 + 4.4 seam + correct cleanup |
| `tests/unit/ui/screens/test_transfer_mass_preview_catalog_seam.py` | Test | Task 2.10 catalog invalidation |
| `tests/unit/simulation/entities/stat_contributors/test_crew_priority_reset_seam.py` | Test | Task 3.4 reset seam |
| `tests/unit/simulation/ship_combat_engine/test_cooldowns.py` | Test | Task 1.2: inverted stale shared-subsystem test |
