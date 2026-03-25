# PROJ-223: Save/Load Round-Trip Verification Framework

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-223` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-223 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Infrastructure & Helpers | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Leaf Type Round-Trip Coverage | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Compound Type Round-Trip Coverage | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. DI & Reference Integrity | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Full GameSession Round-Trip | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Live State Comparison Harness | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-03-24
**Active Phase:** PROJECT COMPLETE — All 6 phases done
**Last Action:** Completed all 6 phases of PROJ-223 (Save/Load Round-Trip Verification Framework)
**Next Action:** Audit
**Blockers:** None
**Context for Next Agent:**
- All 6 phases complete: Infrastructure, Leaf Types, Compound Types, DI & References, Full Round-Trip, Live Harness
- Final test count: 13,714 passed, 2 skipped (280 new tests from 13,434 baseline)
- Production files modified: `game/core/json_utils.py` (register_serializable decorator), `game/strategy/data/empire.py` (sorted built_ship_designs)
- New test infrastructure: `tests/infrastructure/deep_compare.py`, `tests/infrastructure/state_snapshot.py`, `tests/fixtures/strategy_entities.py`
- 14 new test files in `tests/integration/save_load/`
- deep_compare treats tuples and lists as equivalent (JSON round-trip converts tuples to lists)

## Overview
Build a comprehensive verification framework ensuring all 28 serializable types survive save/load round-trip with full field-level fidelity. Motivated by BUG-107 (missing registries after deserialization). Includes reusable deep-compare utilities, per-type round-trip tests, cross-object reference integrity checks, registry injection validation, and a live state comparison harness for QA sessions.

## Goals
- Prevent BUG-107 class regressions: Ensure all DI-dependent objects receive registries after load
- Field-level fidelity: Verify every serialized field survives `to_dict()` → `from_dict()` round-trip
- Reference integrity: Validate cross-object pointers (fleet→ship, empire→colony, order→target) after load
- Extensibility: Make it trivial to add new serializable types to the verification suite
- Live comparison: Enable QA sessions to snapshot, save/load, and compare game state

## Scope
**In:**
- Deep-compare utility for field-level diff reporting
- Round-trip tests for all 28 serializable types (breadth-first)
- DI registry injection validation across the full deserialization chain
- Cross-object reference integrity tests
- Full GameSession end-to-end save/load verification
- Live state comparison harness
- Light refactoring: optional `@register_serializable` decorator in `json_utils.py`
- Fix non-deterministic set ordering in `Empire.built_ship_designs` serialization

**Out:**
- Changes to the serialization format or save file structure
- Save file migration or backward compatibility code
- Performance optimization of the save/load system itself
- UI changes or user-facing features
- Simulation-layer BattleState serialization (separate concern, tested independently)

## Key Files
| Component | File Path |
|-----------|-----------|
| Triage findings | `Projects/active_projects/PROJ-223/findings/save_load_verification_framework.md` |
| SaveGameService | `game/strategy/systems/save_game_service.py` |
| GameSession | `game/strategy/engine/game_session.py` |
| json_utils (serialization helpers) | `game/core/json_utils.py` |
| validation_helpers | `game/core/validation_helpers.py` |
| FleetOrderSerializer | `game/strategy/data/fleet_order_serializer.py` |
| Existing save/load tests | `tests/integration/save_load/` |
| Test infrastructure | `tests/infrastructure/` |
| Test fixtures | `tests/fixtures/` |
| Root conftest | `tests/conftest.py` |
| Save/load conftest | `tests/integration/save_load/conftest.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/save_load_verification_framework.md](findings/save_load_verification_framework.md) - Original triage document

---

## Phases

### Phase 1: Test Infrastructure & Helpers [Medium]
**Objective:** Build reusable utilities that all subsequent phases depend on.
**Status:** Complete

#### Task 1.1: Create deep comparison utility [Medium]
**File:** `tests/infrastructure/deep_compare.py` (NEW)
**Tests:** `pytest tests/unit/infrastructure/test_deep_compare.py`
- [x] Create `tests/infrastructure/deep_compare.py` with:
  - `ComparisonResult` dataclass (path, expected, actual, message)
  - `deep_compare(original_dict, loaded_dict, ignore_fields=None, float_tolerance=1e-10)` → `List[ComparisonResult]`
  - Handle dict, list, tuple, set, float, None, and primitive types
  - Float comparison with configurable tolerance (default 1e-10)
  - Unordered list comparison option for sets serialized as lists
  - Path tracking for clear diff reporting (e.g., `"galaxy.systems[0].system.planets[2].mass"`)
- [x] Create `tests/unit/infrastructure/test_deep_compare.py` with tests for:
  - Identical dicts → empty result
  - Missing key → reports path
  - Extra key → reports path
  - Value difference → reports path + expected/actual
  - Nested dict differences
  - List ordering sensitivity
  - Float tolerance
  - None vs missing key distinction
  - Set-as-list unordered comparison
- [x] Run tests: `pytest tests/unit/infrastructure/test_deep_compare.py`
**Notes:** 37 tests all passing. Also supports `unordered_lists` and `ignore_fields` parameters.

#### Task 1.2: Create strategy entity test factories [Medium]
**File:** `tests/fixtures/strategy_entities.py` (NEW)
**Tests:** `pytest tests/unit/fixtures/test_strategy_entities.py`
- [x] Create `tests/fixtures/strategy_entities.py` with factory functions:
  - `create_test_spectrum()` → Spectrum with all 9 bands populated
  - `create_test_star(name="TestStar", ...)` → Star with spectrum
  - `create_test_warp_point(destination_id="OtherSystem", ...)` → WarpPoint
  - `create_test_storm(name="TestStorm", ...)` → Storm with StormEffect
  - `create_test_species_population(race_id="test_race", count=1000, ...)` → SpeciesPopulation
  - `create_test_facility(instance_id="fac_1", ...)` → PlanetaryFacility
  - `create_test_planet(name="TestPlanet", has_facilities=True, has_population=True, ...)` → Planet
  - `create_test_star_system(name="TestSystem", num_planets=2, num_stars=1, ...)` → StarSystem
  - `create_test_race_config(race_id="test_race", ...)` → RaceConfig
  - `create_test_fleet_order(order_type=OrderType.MOVE, target=HexCoord(0,0), ...)` → FleetOrder
  - `create_test_ship_instance(name="TestShip", registries=None, ...)` → ShipInstance
  - `create_test_fleet(fleet_id=1, num_ships=2, registries=None, ...)` → Fleet
  - `create_test_empire(empire_id=0, num_fleets=1, galaxy=None, registries=None, ...)` → Empire
  - `create_test_event(event_type="SHIP_BUILT", ...)` → Event
  - `create_test_event_log(num_events=3, ...)` → EventLog
  - `create_test_game_config(num_players=2, ...)` → GameConfig
  - `create_test_design_metadata(design_id="test_design", ...)` → DesignMetadata
- [x] Each factory must:
  - Accept keyword overrides for all fields
  - Create fully-populated instances (no None fields unless semantically correct)
  - Accept optional `registries` parameter where DI is needed
  - Return objects that pass their own validation (if any)
- [x] Create `tests/unit/fixtures/test_strategy_entities.py` to verify each factory produces valid objects
- [x] Run tests: `pytest tests/unit/fixtures/test_strategy_entities.py`
**Notes:** 20 factory functions, 52 tests all passing.

#### Task 1.3: Add @register_serializable decorator to json_utils.py [Simple]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils.py`
- [x] Add module-level `_SERIALIZABLE_REGISTRY: Dict[str, type] = {}` dict
- [x] Add `register_serializable(type_name: str = None)` decorator function
  - Stores class reference in `_SERIALIZABLE_REGISTRY` keyed by type_name or cls.__name__
  - Returns class unchanged (no modification)
- [x] Add `get_serializable_registry() -> Dict[str, type]` function (returns copy)
- [x] Add tests in existing test file for:
  - Decorator registers class
  - Custom name override works
  - Registry returns all registered classes
  - Decorator doesn't modify class
- [x] Run tests: `pytest tests/unit/core/test_json_utils.py`
**Notes:** 5 new tests added. Decorator returns class unchanged. Registry returns copy.

#### Task 1.4: Add round-trip assertion helper to save/load conftest [Simple]
**File:** `tests/integration/save_load/conftest.py`
**Tests:** Used by all subsequent phases
- [x] Add `assert_round_trip_fidelity(original_obj, type_class, ignore_fields=None, registries=None)` helper:
  - Calls `original_obj.to_dict()`
  - Passes through `json.dumps()` → `json.loads()` (validates JSON serializability)
  - Calls `type_class.from_dict(parsed, ...)` with appropriate parameters (registries, galaxy, etc.)
  - Calls `deep_compare()` on original dict vs restored dict
  - Asserts no differences (or only expected differences)
- [x] Add `assert_field_preserved(original, restored, field_name, tolerance=None)` helper for individual field checks
- [x] Add fixtures:
  - `populated_planet(fresh_registries)` using factory
  - `populated_fleet(fresh_registries)` using factory
  - `populated_empire(fresh_registries)` using factory
**Notes:** Helpers added. 41 existing save/load tests still pass.

#### Task 1.5: Fix Empire.built_ship_designs set ordering [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/ -k empire`
- [x] In `Empire.to_dict()`, change `list(self.built_ship_designs)` to `sorted(self.built_ship_designs)`
- [x] Add test: verify `to_dict()` produces deterministic order for `built_ship_designs`
- [x] Run tests: `pytest tests/ -n 12` — 13,530 passed, 2 skipped
**Notes:** 2 new tests in TestEmpireSerializationDeterminism. Full suite green.

---

### Phase 2: Leaf Type Round-Trip Coverage [Medium]
**Objective:** Cover all simple (non-nested or minimally-nested) serializable types with field-level round-trip tests.
**Status:** Complete

#### Task 2.1: Spectrum round-trip tests [Simple]
- [x] Test `Spectrum.to_dict()` includes all 9 bands
- [x] Test `Spectrum.from_dict()` restores all 9 bands
- [x] Test round-trip: `Spectrum → to_dict → JSON → from_dict → compare` (field-level)
- [x] Test float precision: spectrum values range 1e-47 to 1e-7, verify within tolerance
**Notes:** 5 tests in TestSpectrumRoundTrip.

#### Task 2.2: Star round-trip tests [Simple]
- [x] Test all Star fields, color tuple→list conversion, HexCoord location, star_type enum
**Notes:** 7 tests in TestStarRoundTrip.

#### Task 2.3: StormEffect and Storm round-trip tests [Simple]
- [x] Test StormEffect all 5 fields + defaults, Storm all fields + nested effect, hex_offsets
**Notes:** 7 tests across TestStormEffectRoundTrip and TestStormRoundTrip.

#### Task 2.4: WarpPoint round-trip tests [Simple]
- [x] Test destination_id and location round-trip
**Notes:** 3 tests in TestWarpPointRoundTrip.

#### Task 2.5: SpeciesPopulation round-trip tests [Simple]
- [x] Test all 3 fields + happiness default
**Notes:** 4 tests.

#### Task 2.6: PlanetaryFacility round-trip tests [Simple]
- [x] Test all 7 fields + resource_levels variations
**Notes:** 5 tests.

#### Task 2.7: RaceConfig round-trip tests [Simple]
- [x] Test all 25+ fields + atmosphere_preferences + defaults
**Notes:** 5 tests in TestRaceConfigRoundTrip.

#### Task 2.8: Event and EventLog round-trip tests [Simple]
- [x] Test Event 6 fields + EventLog with multiple events + empty log
**Notes:** 9 tests.

#### Task 2.9: GameConfig and PlayerConfig round-trip tests [Simple]
- [x] Test all PlayerConfig/GameConfig fields + color conversion + nested players
**Notes:** 10 tests.

#### Task 2.10: DesignMetadata round-trip tests [Simple]
- [x] Test all 12 fields + optional defaults
**Notes:** 4 tests.

#### Task 2.11: NodeState round-trip tests [Simple]
- [x] Test all 3 fields + defaults for missing
**Notes:** 4 tests.

#### Task 2.12: FleetOrder round-trip tests (all 7 target formats) [Medium]
- [x] Test all 7 target formats + execution_progress + all OrderType enum values
**Notes:** 26 tests (15 + parametrized OrderType).

#### Task 2.13: Run full test suite [Simple]
- [x] Run full test suite: 13,619 passed, 2 skipped — no regressions
**Notes:**

---

### Phase 3: Compound Type Round-Trip Coverage [Medium]
**Objective:** Cover compound types (those containing nested serializable objects) with field-level round-trip tests.
**Status:** Complete

#### Task 3.1: Planet round-trip tests [Medium]
- [x] Test all physics/classification fields, nested facilities/populations, resources, atmosphere, owner_id, visual fields, PlanetType enum
**Notes:** 10 tests in TestPlanetRoundTrip.

#### Task 3.2: StarSystem round-trip tests [Medium]
- [x] Test with stars, warp_points, planets, storms + region_id + global_location
**Notes:** 6 tests. Storm hex_offsets uses ignore+manual check due to frozenset ordering.

#### Task 3.3: ShipInstance round-trip tests [Medium]
- [x] Test all 15 fields + design_data + resource_levels + component_toggles + cargo + registries
**Notes:** 11 tests.

#### Task 3.4: Fleet round-trip tests [Medium]
- [x] Test core fields + nested ships/orders + path + construction_queue + registries
**Notes:** 10 tests.

#### Task 3.5: Empire round-trip tests [Medium]
- [x] Test core fields + nested fleets + colony_ids + economy + optional fields + registries
**Notes:** 12 tests. Colony resolution tested in Phase 4.

#### Task 3.6: Galaxy round-trip tests [Medium]
- [x] Test radius + _next_planet_id + systems + spatial indexes rebuilt
**Notes:** 5 tests.

#### Task 3.7: ResearchTracker round-trip tests [Simple]
- [x] Test all fields + node_states + empty tracker
**Notes:** 3 tests.

#### Task 3.8: Run full test suite [Simple]
- [x] 13,673 passed, 2 skipped — no regressions
**Notes:**

---

### Phase 4: DI & Reference Integrity [Medium]
**Objective:** Validate registry injection and cross-object reference resolution survive save/load.
**Status:** Complete

#### Task 4.1: Registry injection verification [Medium]
- [x] Test all ShipInstance _registries + get_calculated_stats + GameSession._registries + TurnEngine
**Notes:** 5 tests. BUG-107 regression guard.

#### Task 4.2: Colony reference integrity [Medium]
- [x] Test colonies are Planet objects + owner_id + galaxy lookup + count
**Notes:** 4 tests.

#### Task 4.3: Fleet order reference resolution [Medium]
- [x] Test MOVE_TO_FLEET/COLONIZE resolved + unresolvable removed
**Notes:** 3 tests.

#### Task 4.4: Pursuer tracker rebuild [Simple]
- [x] Test pursuers registered after load
**Notes:** 1 test.

#### Task 4.5: Fleet registration with galaxy [Simple]
- [x] Test all fleets registered + count matches
**Notes:** 2 tests.

#### Task 4.6: Galaxy back-references [Simple]
- [x] Test empires have galaxy reference
**Notes:** 1 test.

#### Task 4.7: Run full test suite [Simple]
- [x] 13,689 passed, 2 skipped — no regressions
**Notes:**

---

### Phase 5: Full GameSession Round-Trip [Medium]
**Objective:** End-to-end verification with richly-populated game state through SaveGameService.
**Status:** Complete

#### Task 5.1: Comprehensive GameSession round-trip [Complex]
- [x] Create rich game state, save/load via SaveGameService, deep-compare, process_turn, re-save
**Notes:** 5 tests in TestComprehensiveGameSessionRoundTrip.

#### Task 5.2: Multi-cycle save/load/play test [Medium]
- [x] Save → Load → 3 turns → Save → Load → Verify + turn_number + events
**Notes:** 3 tests in TestMultiCycleSaveLoadPlay.

#### Task 5.3: JSON format stability test [Simple]
- [x] JSON-serializable + all string keys + no non-serializable objects
**Notes:** 3 tests in TestJsonFormatStability.

#### Task 5.4: Run full test suite [Simple]
- [x] All tests pass
**Notes:**

---

### Phase 6: Live State Comparison Harness [Medium]
**Objective:** Build a harness usable from QA sessions to snapshot, save/load, and compare game state.
**Status:** Complete

#### Task 6.1: Create state snapshot utility [Medium]
- [x] snapshot_game_state, compare_game_states, SaveLoadVerifier, VerificationReport
**Notes:** Auto-ignores save_path and storm hex_offsets.

#### Task 6.2: Create verification integration test [Medium]
- [x] Minimal + populated sessions pass, corruption detected, timing/size stats
**Notes:** 10 tests across unit and integration.

#### Task 6.3: Run full test suite (final verification) [Simple]
- [x] 13,714 passed, 2 skipped. 280 new tests from baseline.
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `pytest tests/` - 13,426 passed, 2 skipped (baseline)

### After Each Phase
- [x] Run `pytest tests/ -n 12` - all affected tests pass
- [x] No regressions in existing save/load tests

### Final Verification
- [x] Run full test suite: `pytest tests/ -n 12` — 13,714 passed, 2 skipped
- [x] All new round-trip tests pass for all 28 types
- [x] Registry injection validated for full deserialization chain
- [x] Cross-object reference integrity validated
- [x] Live state comparison harness functional
- [x] Verify changes are consistent with `docs/` — no doc changes needed (only added optional decorator + minor sort fix)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] All Phase 1 tasks checked off (Infrastructure)
- [x] All Phase 2 tasks checked off (Leaf types)
- [x] All Phase 3 tasks checked off (Compound types)
- [x] All Phase 4 tasks checked off (DI & References)
- [x] All Phase 5 tasks checked off (Full round-trip)
- [x] All Phase 6 tasks checked off (Live harness)
- [x] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
