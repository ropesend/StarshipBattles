# PROJ-267: Test Infrastructure Consolidation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-267` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-267 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Consolidate shared helpers into conftest files | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Consolidate colonize_validator tests | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Relocate misplaced test files | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** Planning Complete
**Last Action:** Plan written with verified file locations and line numbers
**Next Action:** Begin Phase 1 -- consolidate make_colony_ship and MockGalaxy/MockSystem/MockPlanet helpers
**Blockers:** None
**Context for Next Agent:** All duplicate helper locations have been verified via grep. The root `tests/conftest.py` already has a `make_colony_ship_for_planet()` at line 339, and `tests/integration/colonization/conftest.py` has another at line 41. Phase 1 focuses on making all files use a single canonical version. Phase 2 is an independent refactor of one bloated test file. Phase 3 moves files to correct directories (depends on PROJ-263 completing first for the hex math file, which PROJ-263 may delete entirely).

## Overview
The test suite review (`Reviews/results/2026-04-08_test-review/final_report.md`) identified widespread duplication of test helpers -- the same factory functions and mock classes are copy-pasted across dozens of files. This project consolidates shared test infrastructure into conftest files, reduces a bloated test file from 1,247 LOC to ~700 LOC, and relocates test files that are in the wrong directories per the layer architecture.

This is a pure test-infrastructure project. No production code changes. All work is refactoring test helpers, reducing test duplication, and moving test files to correct locations.

## Goals
- Eliminate 7+ independent copies of `make_colony_ship()` by consolidating into shared conftest
- Eliminate 20+ independent copies of `MockGalaxy`/`MockSystem`/`MockPlanet` by extracting into shared conftest
- Eliminate 5+ independent copies of `_make_shipyard()` by making tests use the existing `create_shipyard()` in production conftest
- Eliminate 3 independent copies of `MockGameSession` in save_game_service tests
- Reduce `test_colonize_validator.py` from 1,247 LOC to ~700 LOC by extracting shared fixtures and removing internal duplication
- Move 4 misplaced test files to their correct directories per layer architecture

## Scope
**In:**
- Consolidating duplicate `make_colony_ship()` helpers into conftest files
- Consolidating duplicate `MockGalaxy`/`MockSystem`/`MockPlanet` classes into conftest files
- Consolidating duplicate `_make_shipyard()` helpers -- making tests use existing `create_shipyard()`
- Consolidating duplicate `MockGameSession` into `tests/unit/strategy/save_game_service/conftest.py`
- Refactoring `test_colonize_validator.py` to extract shared fixtures and remove duplicate tests
- Relocating misplaced test files to correct directories

**Out:**
- Deleting duplicate test files (that is PROJ-263)
- Deleting scaffold/trivial tests (that is PROJ-265/PROJ-266)
- Writing new tests to fill coverage gaps (that is PROJ-264)
- Fixing production bugs (that is PROJ-261)
- Changes to production code

## Key Files

### Phase 1: Helper Consolidation

#### make_colony_ship cluster (9 definitions)
| File | Function Name | Line |
|------|--------------|------|
| `tests/conftest.py` | `make_colony_ship_for_planet()` | 339 |
| `tests/integration/colonization/conftest.py` | `make_colony_ship_for_planet()` | 41 |
| `tests/integration/gameplay_loop/test_commands_colonization.py` | `make_colony_ship_for_planet()` | 18 |
| `tests/integration/colonization/test_planet_specific_colonization.py` | `make_colony_ship()` | 104 |
| `tests/integration/strategy/test_colonize_logic.py` | `make_colony_ship()` | 65 |
| `tests/integration/strategy/test_command_handlers.py` | `make_colony_ship()` | 13 |
| `tests/integration/strategy/facade/test_facade_integration.py` | `make_colony_ship_for_planet()` | 19 |
| `tests/unit/strategy/engine/test_colonize_mission_handler.py` | `make_colony_ship()` | 17 |
| `tests/unit/strategy/engine/test_process_colonize_validation.py` | `make_colony_ship()` | 84 |

#### MockGalaxy/MockSystem cluster (20+ definitions)
| File | Classes | Line |
|------|---------|------|
| `tests/unit/strategy/engine/test_process_colonize_validation.py` | MockGalaxy, MockSystem | 55, 64 |
| `tests/unit/strategy/engine/test_process_colonize_cargo.py` | MockGalaxy, MockSystem | 73, 80 |
| `tests/integration/colonization/test_planet_specific_colonization.py` | MockGalaxy, MockSystem | 75, 84 |
| `tests/integration/strategy/test_colonize_logic.py` | MockGalaxy, MockSystem | 22, 46 |
| `tests/integration/strategy/test_command_handlers.py` | MockGalaxy | 39 |
| `tests/integration/strategy/test_path_projection.py` | MockGalaxy, MockSystem | 8, 14 |
| `tests/integration/strategy/test_fleet_navigation_consistency.py` | MockGalaxy | 35 |
| `tests/integration/strategy/test_economy_e2e.py` | MockGalaxy | 243 |
| `tests/integration/strategy/test_resupply_system.py` | MockGalaxy | 98 |
| `tests/integration/strategy/transfer/conftest.py` | MockGalaxy, MockSystem | 130, 139 |
| `tests/integration/strategy/turn_engine/conftest.py` | MockGalaxy | 7 |
| `tests/integration/ui/build_queue_screen/conftest.py` | MockGalaxy | 14 |
| `tests/integration/ui/test_build_queue_formatting.py` | MockGalaxy | 16 |
| `tests/integration/ui/test_build_queue_drag_drop.py` | MockGalaxy | 11 |
| `tests/integration/ui/build_queue_screen/test_queue_selector.py` | MockGalaxy | 22 |
| `tests/integration/ui/build_queue_screen/test_portrait_logging.py` | MockGalaxy | 15 |
| `tests/integration/ui/build_queue_screen/test_basics.py` | MockGalaxy | 13 |
| `tests/unit/strategy/engine/test_colonize_population.py` | MockGalaxy | 124 |

#### _make_shipyard cluster (9 definitions)
| File | Function Name | Line |
|------|--------------|------|
| `tests/integration/strategy/production/conftest.py` | `create_shipyard()` | 120 |
| `tests/integration/strategy/production/test_completion.py` | `_make_shipyard()` | 28 |
| `tests/integration/strategy/production/test_queue.py` | `_make_shipyard()` | 29 |
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | `_make_shipyard()` | 79 |
| `tests/unit/strategy/production_engine/test_spawning.py` | `_make_shipyard()` | 14 |
| `tests/unit/strategy/test_engine_event_emission.py` | `_make_shipyard_facility()` | 64 |
| `tests/unit/strategy/data/test_build_queue_source.py` | `_make_shipyard_facility()` | 65 |
| `tests/unit/strategy/data/test_facility_construction_queue.py` | `_make_shipyard_facility()` | 34 |
| `tests/integration/strategy/test_production_rates.py` | `_make_shipyard_facility()` | 25 |

#### MockGameSession cluster (5 definitions)
| File | Line |
|------|------|
| `tests/unit/strategy/save_game_service/conftest.py` | 12 |
| `tests/unit/strategy/save_game_service/test_save_load_ops.py` | 24 |
| `tests/unit/strategy/save_game_service/test_error_handling.py` | 24 |
| `tests/unit/ui/test_save_selection.py` | 15 |
| `tests/unit/strategy/test_auto_save.py` | 15 |

### Phase 2: Colonize Validator Refactor
| File | LOC |
|------|-----|
| `tests/unit/strategy/validation/test_colonize_validator.py` | 1,247 |
| `game/strategy/validation/colonize_validator.py` (source) | 143 |

### Phase 3: Misplaced Test Files
| File | Current Location | Correct Location | LOC |
|------|-----------------|------------------|-----|
| `test_ship_theme_logic.py` | `tests/unit/entities/` | `tests/unit/ui/` | 356 |
| `test_hex_math_strategy.py` | `tests/integration/strategy/` | `tests/unit/core/` (or deleted by PROJ-263) | 97 |
| `test_battle_setup_logic.py` | `tests/unit/combat/` | `tests/unit/ui/screens/` | 103 |
| `test_empire_dto.py` | `tests/integration/strategy/facade/` | `tests/unit/strategy/facade/` | 308 |
| `test_fleet_dto.py` | `tests/integration/strategy/facade/` | `tests/unit/strategy/facade/` | 403 |
| `test_system_dto.py` | `tests/integration/strategy/facade/` | `tests/unit/strategy/facade/` | 432 |

## Dependency Notes

- **PROJ-263 overlap (hex math):** PROJ-263 Phase 3 targets colonization duplicates, and the `test_hex_math_strategy.py` file is flagged as a DUPLICATE in the review. If PROJ-263 deletes it first, Phase 3 Task 3.2 becomes a no-op. Check at execution time.
- **PROJ-263 overlap (colonize_logic):** PROJ-263 Phase 3 may delete or trim `tests/integration/strategy/test_colonize_logic.py`. If that happens before PROJ-267 Phase 1, fewer files need `make_colony_ship()` consolidation. This is not a blocker -- just verify files still exist before modifying.
- **No production code changes:** This project only touches test files and conftest files.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection
- `Reviews/results/2026-04-08_test-review/final_report.md` - Source review that identified all issues

---

## Detailed Analysis

### Phase 1: Consolidate Shared Helpers

#### 1A: make_colony_ship consolidation

There are two naming variants: `make_colony_ship(name, owner_id, pod_type)` and `make_colony_ship_for_planet(planet, owner_id)`. The `_for_planet` variant is the more useful one (derives pod type from planet object). The root `tests/conftest.py` already has `make_colony_ship_for_planet()` at line 339, making it available to all tests.

**Strategy:** Keep the root conftest version as canonical. Files that need the simpler `make_colony_ship(name, owner_id, pod_type)` signature can use a local wrapper or the root conftest can export both variants. Remove all other definitions and update imports.

The `tests/integration/colonization/conftest.py` version at line 41 is nearly identical to the root conftest -- remove it and let tests inherit from root.

#### 1B: MockGalaxy/MockSystem/MockPlanet consolidation

These mock classes appear in 20+ files. Most are simple `MagicMock()`-based or minimal attribute bags. The challenge is that different files have slightly different MockGalaxy implementations:
- Some have `get_planets_at_global_hex()` returning empty list
- Some have `systems` as a dict
- Some have `get_system_at_hex()` returning a MockSystem
- Some are truly minimal (just `systems = {}`)

**Strategy:** Create a shared `tests/helpers/mock_galaxy.py` module (or add to an appropriate conftest) with a configurable MockGalaxy that supports the superset of all usages. Start with the colonization-related files (where MockGalaxy/MockSystem/MockPlanet always appear together) and expand outward.

#### 1C: _make_shipyard consolidation

The `tests/integration/strategy/production/conftest.py` already has `create_shipyard()` at line 120. Five other files define their own `_make_shipyard()` instead of using it. Two variant groups exist:
- `_make_shipyard(instance_id)` -- creates a PlanetaryFacility directly
- `_make_shipyard_facility(instance_id, queue)` -- slightly different signature

**Strategy:** Verify that `create_shipyard()` in the existing conftest covers all use cases. Update tests in `test_completion.py`, `test_queue.py`, `test_tick_consumption.py`, and `test_spawning.py` to use it. For unit tests that need the helper but are outside the production conftest's scope, add a `_make_shipyard` fixture to the appropriate unit test conftest.

#### 1D: MockGameSession consolidation

Three identical copies of `MockGameSession` exist in the save_game_service directory. The conftest already has the canonical version. The other two test files (`test_save_load_ops.py` and `test_error_handling.py`) have copy-pasted it.

**Strategy:** Delete `MockGameSession` from `test_save_load_ops.py` and `test_error_handling.py`. They already import from conftest implicitly via pytest. The two files outside this directory (`test_save_selection.py`, `test_auto_save.py`) have their own MockGameSession that may differ slightly -- evaluate whether they can share or need to stay local.

### Phase 2: Colonize Validator Test Refactor

**File:** `tests/unit/strategy/validation/test_colonize_validator.py` (1,247 LOC)
**Source:** `game/strategy/validation/colonize_validator.py` (143 LOC)
**Ratio:** 8.7:1 test-to-source

The file has 8 test classes with significant internal duplication:
- `MockPlanetType(Enum)` is redefined 16 times across individual test methods
- `mock_component_registry` fixture is defined 3 times (lines 410, 777, 918)
- `_make_planet()` helper is defined 2 times (lines 781, 922)
- `_make_ship_with_pod()` helper is defined 1 time but its logic is reimplemented in multiple test methods

**Strategy:**
1. Extract `MockPlanetType` to module level (one definition, 16 removals)
2. Extract `mock_component_registry` to a module-level fixture
3. Extract `_make_planet()` and `_make_ship_with_pod()` to module-level helpers
4. Identify semantically duplicate tests (multiple tests asserting the same behavior with trivially different setups)
5. Consolidate without losing edge case coverage
6. Run with `--cov=game/strategy/validation/colonize_validator` to verify no coverage loss

### Phase 3: Relocate Misplaced Test Files

1. **test_ship_theme_logic.py** (356 LOC) -- imports `game.ui.assets.ShipThemeManager`. This is UI layer code, not entity code. Move from `tests/unit/entities/` to `tests/unit/ui/`.

2. **test_hex_math_strategy.py** (97 LOC) -- pure unit tests for `HexCoord` (core layer). Currently in `tests/integration/strategy/`. Should be in `tests/unit/core/`. However, PROJ-263 lists this as a DUPLICATE to delete. **Check at execution time** -- if PROJ-263 has already deleted it, skip this task.

3. **test_battle_setup_logic.py** (103 LOC) -- imports `game.ui.screens.battle_screen.BattleScreen`. This tests UI layer code, not simulation combat. Move from `tests/unit/combat/` to `tests/unit/ui/screens/`.

4. **DTO test files** (3 files, 1,143 LOC total) -- `test_empire_dto.py`, `test_fleet_dto.py`, `test_system_dto.py` in `tests/integration/strategy/facade/`. These test frozen dataclass creation with zero cross-layer behavior (no I/O, no integration). Move from `tests/integration/strategy/facade/` to `tests/unit/strategy/facade/`.

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-09 | Use root `tests/conftest.py` as canonical location for `make_colony_ship_for_planet()` | Already exists there at line 339; available to all tests without explicit imports |
| 2026-04-09 | Create `tests/helpers/mock_galaxy.py` for MockGalaxy/MockSystem/MockPlanet | Too many variants for a conftest fixture; a shared module with configurable classes is cleaner |
| 2026-04-09 | Update production tests to use existing `create_shipyard()` rather than creating new shared version | Avoids creating yet another helper when one already exists in the right conftest |
| 2026-04-09 | Phase 3 depends on PROJ-263 for hex_math_strategy.py | PROJ-263 may delete it entirely as a duplicate; check at execution time |
| 2026-04-09 | Move DTO tests to unit/ not just relocate within integration/ | They test frozen dataclass creation -- pure unit tests with no integration behavior |

---

## Verification

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` -- all tests pass (baseline)
- [ ] Note test count for comparison (should remain the same -- no tests added or removed)

### After Each Phase
- [ ] Run affected test files -- all pass
- [ ] Run `pytest tests/ --testmon` -- no regressions

### Final Verification
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify test count is unchanged (this project consolidates helpers, not tests)
- [ ] Verify no new test failures

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (full suite)
- [ ] Test count unchanged
- [ ] No docs need updating (test-only changes)
- [ ] User verified
