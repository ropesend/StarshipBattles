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
| 1. Test Infrastructure & Helpers | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Leaf Type Round-Trip Coverage | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Compound Type Round-Trip Coverage | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. DI & Reference Integrity | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Full GameSession Round-Trip | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Live State Comparison Harness | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-03-24 18:45
**Active Phase:** Planning — Awaiting User Approval
**Last Action:** Full plan drafted with 6 phases, all checklists and manifest created
**Next Action:** User approval, then begin Phase 1 implementation
**Blockers:** None
**Context for Next Agent:** Baseline is 13,426 tests, 2 skipped. All swarm findings captured in design.md. 2 production files modified (json_utils.py, empire.py), 23 new test files created across 6 phases.

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
**Status:** Not Started

#### Task 1.1: Create deep comparison utility [Medium]
**File:** `tests/infrastructure/deep_compare.py` (NEW)
**Tests:** `pytest tests/unit/infrastructure/test_deep_compare.py`
- [ ] Create `tests/infrastructure/deep_compare.py` with:
  - `ComparisonResult` dataclass (path, expected, actual, message)
  - `deep_compare(original_dict, loaded_dict, ignore_fields=None, float_tolerance=1e-10)` → `List[ComparisonResult]`
  - Handle dict, list, tuple, set, float, None, and primitive types
  - Float comparison with configurable tolerance (default 1e-10)
  - Unordered list comparison option for sets serialized as lists
  - Path tracking for clear diff reporting (e.g., `"galaxy.systems[0].system.planets[2].mass"`)
- [ ] Create `tests/unit/infrastructure/test_deep_compare.py` with tests for:
  - Identical dicts → empty result
  - Missing key → reports path
  - Extra key → reports path
  - Value difference → reports path + expected/actual
  - Nested dict differences
  - List ordering sensitivity
  - Float tolerance
  - None vs missing key distinction
  - Set-as-list unordered comparison
- [ ] Run tests: `pytest tests/unit/infrastructure/test_deep_compare.py`
**Notes:**

#### Task 1.2: Create strategy entity test factories [Medium]
**File:** `tests/fixtures/strategy_entities.py` (NEW)
**Tests:** `pytest tests/unit/fixtures/test_strategy_entities.py`
- [ ] Create `tests/fixtures/strategy_entities.py` with factory functions:
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
- [ ] Each factory must:
  - Accept keyword overrides for all fields
  - Create fully-populated instances (no None fields unless semantically correct)
  - Accept optional `registries` parameter where DI is needed
  - Return objects that pass their own validation (if any)
- [ ] Create `tests/unit/fixtures/test_strategy_entities.py` to verify each factory produces valid objects
- [ ] Run tests: `pytest tests/unit/fixtures/test_strategy_entities.py`
**Notes:** Follow the `create_test_ship()` pattern from `tests/fixtures/ships.py`

#### Task 1.3: Add @register_serializable decorator to json_utils.py [Simple]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils.py`
- [ ] Add module-level `_SERIALIZABLE_REGISTRY: Dict[str, type] = {}` dict
- [ ] Add `register_serializable(type_name: str = None)` decorator function
  - Stores class reference in `_SERIALIZABLE_REGISTRY` keyed by type_name or cls.__name__
  - Returns class unchanged (no modification)
- [ ] Add `get_serializable_registry() -> Dict[str, type]` function (returns copy)
- [ ] Add tests in existing test file for:
  - Decorator registers class
  - Custom name override works
  - Registry returns all registered classes
  - Decorator doesn't modify class
- [ ] Run tests: `pytest tests/unit/core/test_json_utils.py`
**Notes:** Decorator is optional — not required for serialization to work. Gradual adoption.

#### Task 1.4: Add round-trip assertion helper to save/load conftest [Simple]
**File:** `tests/integration/save_load/conftest.py`
**Tests:** Used by all subsequent phases
- [ ] Add `assert_round_trip_fidelity(original_obj, type_class, ignore_fields=None, registries=None)` helper:
  - Calls `original_obj.to_dict()`
  - Passes through `json.dumps()` → `json.loads()` (validates JSON serializability)
  - Calls `type_class.from_dict(parsed, ...)` with appropriate parameters (registries, galaxy, etc.)
  - Calls `deep_compare()` on original dict vs restored dict
  - Asserts no differences (or only expected differences)
- [ ] Add `assert_field_preserved(original, restored, field_name, tolerance=None)` helper for individual field checks
- [ ] Add fixtures:
  - `populated_planet(fresh_registries)` using factory
  - `populated_fleet(fresh_registries)` using factory
  - `populated_empire(fresh_registries)` using factory
**Notes:**

#### Task 1.5: Fix Empire.built_ship_designs set ordering [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/ -k empire`
- [ ] In `Empire.to_dict()`, change `list(self.built_ship_designs)` to `sorted(self.built_ship_designs)`
- [ ] Add test: verify `to_dict()` produces deterministic order for `built_ship_designs`
- [ ] Run tests: `pytest tests/ -n 12 --testmon`
**Notes:** Prevents flaky tests from non-deterministic set iteration order.

---

### Phase 2: Leaf Type Round-Trip Coverage [Medium]
**Objective:** Cover all simple (non-nested or minimally-nested) serializable types with field-level round-trip tests.
**Status:** Not Started

#### Task 2.1: Spectrum round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_stars.py`
- [ ] Test `Spectrum.to_dict()` includes all 9 bands
- [ ] Test `Spectrum.from_dict()` restores all 9 bands
- [ ] Test round-trip: `Spectrum → to_dict → JSON → from_dict → compare` (field-level)
- [ ] Test float precision: spectrum values range 1e-47 to 1e-7, verify within tolerance
**Notes:**

#### Task 2.2: Star round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (same file)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_stars.py`
- [ ] Test `Star.to_dict()` includes all fields (name, mass, radius_hexes, temperature, luminosity, spectrum, star_type, color, age, location)
- [ ] Test `Star.from_dict()` restores all fields
- [ ] Test round-trip with float tolerance for physics values
- [ ] Test color tuple→list→tuple conversion (or list preservation)
- [ ] Test HexCoord location round-trip
**Notes:**

#### Task 2.3: StormEffect and Storm round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_storms.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_storms.py`
- [ ] Test `StormEffect.to_dict()` includes all 5 fields (multipliers + rates)
- [ ] Test `StormEffect.from_dict()` with defaults for missing fields
- [ ] Test `Storm.to_dict()` includes all fields (name, type, location, hex_offsets, effects, image_variant, intensity)
- [ ] Test `Storm.from_dict()` restores all fields including nested StormEffect
- [ ] Test hex_offsets list of HexCoords round-trip
**Notes:**

#### Task 2.4: WarpPoint round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`
- [ ] Test `WarpPoint.to_dict()` includes destination_id and location
- [ ] Test `WarpPoint.from_dict()` restores both fields
- [ ] Test round-trip preserves HexCoord location
**Notes:**

#### Task 2.5: SpeciesPopulation round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`
- [ ] Test `SpeciesPopulation.to_dict()` includes race_id, count, happiness
- [ ] Test `SpeciesPopulation.from_dict()` restores all fields
- [ ] Test happiness defaults to 0.5 if missing (backward compat)
**Notes:**

#### Task 2.6: PlanetaryFacility round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (same file)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`
- [ ] Test `PlanetaryFacility.to_dict()` includes all fields (instance_id, design_id, name, design_data, is_operational, construction_queue, resource_levels)
- [ ] Test `PlanetaryFacility.from_dict()` restores all fields
- [ ] Test resource_levels with fuel and energy values
- [ ] Test empty resource_levels (facility with no fuel)
**Notes:** Extends existing coverage in test_resupply_persistence.py with field-level checks.

#### Task 2.7: RaceConfig round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_empire.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_empire.py`
- [ ] Test `RaceConfig.to_dict()` includes all 25+ fields (identity, visuals, environment, aptitudes, descriptions, timestamps)
- [ ] Test `RaceConfig.from_dict()` restores all fields
- [ ] Test atmosphere_preferences include all default gas types after round-trip
- [ ] Test optional fields default correctly when missing
**Notes:**

#### Task 2.8: Event and EventLog round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_events.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_events.py`
- [ ] Test `Event.to_dict()` includes all 6 fields (event_type, category, turn, empire_id, message, details)
- [ ] Test `Event.from_dict()` restores all fields
- [ ] Test `EventLog.to_dict()` includes events array
- [ ] Test `EventLog.from_dict()` restores all events with field-level fidelity
- [ ] Test empty EventLog round-trip
- [ ] Test EventLog with multiple event types
**Notes:**

#### Task 2.9: GameConfig and PlayerConfig round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_config.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_config.py`
- [ ] Test `PlayerConfig.to_dict()` includes all fields (name, theme, color, is_human, optional race_id/flag_id/portrait_id/race_config)
- [ ] Test `PlayerConfig.from_dict()` restores all fields including optional ones
- [ ] Test `GameConfig.to_dict()` includes all fields (asset_base_path, galaxy_radius, system_count, galaxy_type, galaxy_seed, save_name, players)
- [ ] Test `GameConfig.from_dict()` restores all fields including nested PlayerConfigs
- [ ] Test color tuple→list conversion
**Notes:**

#### Task 2.10: DesignMetadata round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_designs.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_designs.py`
- [ ] Test `DesignMetadata.to_dict()` includes all 12 fields
- [ ] Test `DesignMetadata.from_dict()` restores all fields with correct defaults
- [ ] Test optional fields default correctly when missing
**Notes:**

#### Task 2.11: NodeState round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_research.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_research.py`
- [ ] Test `NodeState.to_dict()` includes current_level, current_chance, rp_allocation
- [ ] Test `NodeState.from_dict()` restores all fields
- [ ] Test defaults: 0, 0.0, 0 for missing fields
**Notes:**

#### Task 2.12: FleetOrder round-trip tests (all 7 target formats) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_orders.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_orders.py`
- [ ] Test HexCoord target (MOVE): `{"q": 5, "r": -3}` → round-trip
- [ ] Test fleet_ref target (MOVE_TO_FLEET): `{"type": "fleet_ref", "id": 42}` → marker dict
- [ ] Test planet_ref target (COLONIZE): `{"type": "planet_ref", "id": 7}` → marker dict
- [ ] Test transfer target (TRANSFER): `{"type": "transfer", "value": {...}}` → round-trip
- [ ] Test warp_params target (OPEN_WARP_POINT): `{"type": "warp_params", "value": {...}}` → round-trip
- [ ] Test ship_id_list target (SELF_DESTRUCT): `{"type": "ship_id_list", "value": [...]}` → round-trip
- [ ] Test execution_progress preservation (> 0 → serialized; 0 → omitted)
- [ ] Test all OrderType enum values round-trip correctly
**Notes:** Fleet/planet refs are NOT fully resolved at this level — that's Phase 4.

#### Task 2.13: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite to verify no regressions
- [ ] Verify all new tests pass
**Notes:**

---

### Phase 3: Compound Type Round-Trip Coverage [Medium]
**Objective:** Cover compound types (those containing nested serializable objects) with field-level round-trip tests.
**Status:** Not Started

#### Task 3.1: Planet round-trip tests (with facilities and populations) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`
- [ ] Test Planet with all 25+ physics/classification fields
- [ ] Test Planet with facilities (nested PlanetaryFacility round-trip)
- [ ] Test Planet with populations (nested SpeciesPopulation round-trip)
- [ ] Test Planet with resources (nested dict round-trip)
- [ ] Test Planet with atmosphere (nested dict round-trip)
- [ ] Test Planet with construction_queue
- [ ] Test owner_id preservation (null and non-null)
- [ ] Test visual fields: image_id, image_rotation, radius_hexes
- [ ] Test PlanetType enum round-trip
**Notes:**

#### Task 3.2: StarSystem round-trip tests (with all children) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`
- [ ] Test StarSystem with stars, warp_points, planets, storms
- [ ] Test region_id optional field (null and non-null)
- [ ] Test global_location HexCoord preservation
- [ ] Test deserialize_list error isolation: corrupt child skipped
**Notes:**

#### Task 3.3: ShipInstance round-trip tests (field-level) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_ships.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py`
- [ ] Test all 15 fields: instance_id, design_id, name, owner_id, design_data, current_hp, component_damage, resource_levels, component_toggles, cargo_contents, is_alive, is_derelict, experience, kills, battles_survived, serial
- [ ] Test design_data (large nested dict) preserved exactly
- [ ] Test resource_levels with multiple resources (fuel, energy, ammo)
- [ ] Test component_toggles with mixed true/false values
- [ ] Test cargo_contents sparse serialization (omitted when empty, included when populated)
- [ ] Test registries parameter passed and stored
**Notes:**

#### Task 3.4: Fleet round-trip tests (with ships and orders) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_fleet.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_fleet.py`
- [ ] Test all core fields: id, owner_id, location, speed, construction_queue
- [ ] Test ships list round-trip (nested ShipInstance preservation)
- [ ] Test orders list round-trip (nested FleetOrder preservation)
- [ ] Test path list round-trip (list of HexCoords)
- [ ] Test fleet with multiple ships and multiple order types
- [ ] Test registries passed to ShipInstance during from_dict
**Notes:**

#### Task 3.5: Empire round-trip tests (with fleets and economy) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_empire.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_empire.py`
- [ ] Test all core fields: id, name, color, theme_path, empire_theme_id
- [ ] Test colony_ids serialization (list of ints, not Planet objects)
- [ ] Test fleets nested round-trip
- [ ] Test built_ship_designs (sorted set→list→set)
- [ ] Test _next_fleet_id counter preservation
- [ ] Test _design_serial_counters dict preservation
- [ ] Test resource_pool and max_storage (economy fields)
- [ ] Test optional fields: flag_id, portrait_id, race_config
- [ ] Test registries passed to Fleet.from_dict()
**Notes:** Colony resolution tested in Phase 4 (requires galaxy).

#### Task 3.6: Galaxy round-trip tests [Medium]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`
- [ ] Test radius preservation
- [ ] Test _next_planet_id counter preservation
- [ ] Test systems array round-trip (coord + StarSystem pairs)
- [ ] Test spatial indexes rebuilt after from_dict (zone registry, warp index, planet registry)
- [ ] Test planet IDs preserved via restore_planet()
**Notes:**

#### Task 3.7: ResearchTracker round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_research.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_research.py`
- [ ] Test ResearchTracker with session_seed, rp_budget, turn_number, auto_spread_enabled
- [ ] Test node_states dict with multiple NodeState entries
- [ ] Test empty ResearchTracker round-trip
**Notes:**

#### Task 3.8: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite to verify no regressions
**Notes:**

---

### Phase 4: DI & Reference Integrity [Medium]
**Objective:** Validate registry injection and cross-object reference resolution survive save/load.
**Status:** Not Started

#### Task 4.1: Registry injection verification [Medium]
**File:** `tests/integration/save_load/test_registry_injection.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_registry_injection.py`
- [ ] Test: After GameSession.from_dict(), all ShipInstance objects have `_registries` set (not None)
- [ ] Test: After load, `ship_instance.get_calculated_stats()` works without error
- [ ] Test: After load, Fleet._component_registry is set (or delegates have registries)
- [ ] Test: Deliberately omit registries in Fleet.from_dict() → verify ShipInstance gets None → verify get_calculated_stats() fails with clear error
- [ ] Test: Verify GameSession._registries is populated after from_dict()
- [ ] Test: Verify TurnEngine receives registries after GameSession.from_dict()
**Notes:** This is the BUG-107 regression guard.

#### Task 4.2: Colony reference integrity [Medium]
**File:** `tests/integration/save_load/test_reference_integrity.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`
- [ ] Test: After save/load, empire.colonies contains actual Planet objects (not IDs)
- [ ] Test: After save/load, each colony planet.owner_id matches empire.id
- [ ] Test: After save/load, colony planets exist in galaxy.get_planet_by_id()
- [ ] Test: Colony count matches between original and loaded empire
- [ ] Test: Colony IDs match between original and loaded (order-insensitive)
**Notes:**

#### Task 4.3: Fleet order reference resolution [Medium]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`
- [ ] Test: MOVE_TO_FLEET order target resolved to actual Fleet object after load
- [ ] Test: JOIN_FLEET order target resolved to actual Fleet object after load
- [ ] Test: COLONIZE order target resolved to actual Planet object after load
- [ ] Test: IMPLODE_PLANET order target resolved to actual Planet object after load
- [ ] Test: Unresolvable fleet_ref (deleted fleet) → order removed with warning
- [ ] Test: Unresolvable planet_ref (deleted planet) → order removed with warning
**Notes:**

#### Task 4.4: Pursuer tracker rebuild [Simple]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`
- [ ] Test: After save/load with MOVE_TO_FLEET order, target fleet's pursuer_tracker includes pursuing fleet
- [ ] Test: After save/load with JOIN_FLEET order, target fleet's pursuer_tracker includes joining fleet
- [ ] Test: Pursuer count matches between original and loaded state
**Notes:**

#### Task 4.5: Fleet registration with galaxy [Simple]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`
- [ ] Test: After save/load, all fleets are registered with galaxy (galaxy.get_fleet_by_id() works)
- [ ] Test: Fleet registration count matches between original and loaded
**Notes:**

#### Task 4.6: Galaxy back-references [Simple]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`
- [ ] Test: After save/load, each empire has galaxy reference set (empire._galaxy is not None)
**Notes:**

#### Task 4.7: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite to verify no regressions
**Notes:**

---

### Phase 5: Full GameSession Round-Trip [Medium]
**Objective:** End-to-end verification with richly-populated game state through SaveGameService.
**Status:** Not Started

#### Task 5.1: Comprehensive GameSession round-trip [Complex]
**File:** `tests/integration/save_load/test_full_roundtrip.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_full_roundtrip.py`
- [ ] Create richly-populated game state:
  - Multiple empires with colonies, fleets, research, economy
  - Fleets with multiple ships, diverse order types, paths
  - Planets with facilities, populations, resources
  - Galaxy with systems, warp points, storms
  - Event log with multiple event types
- [ ] Save via SaveGameService.save_game()
- [ ] Load via SaveGameService.load_game()
- [ ] Deep-compare all fields across the entire game state tree
- [ ] Verify turn processing works after load (process_turn() succeeds)
- [ ] Verify can save again after load (re-save succeeds)
- [ ] Compare re-save JSON with original save JSON (field-level fidelity)
**Notes:** This is the ultimate integration test — if this passes, the entire serialization chain works.

#### Task 5.2: Multi-cycle save/load/play test [Medium]
**File:** `tests/integration/save_load/test_full_roundtrip.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_full_roundtrip.py`
- [ ] Test: Save → Load → Process 3 turns → Save → Load → Verify all fields
- [ ] Test: Verify turn_number increments correctly across save/load cycles
- [ ] Test: Verify events accumulate correctly across cycles
- [ ] Test: Verify fleet movement and order execution work across cycles
**Notes:**

#### Task 5.3: JSON format stability test [Simple]
**File:** `tests/integration/save_load/test_full_roundtrip.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_full_roundtrip.py`
- [ ] Test: `to_dict()` output is fully JSON-serializable (json.dumps succeeds)
- [ ] Test: All dict keys are strings (JSON requirement)
- [ ] Test: No non-serializable objects in output (datetime, HexCoord, enums)
**Notes:**

#### Task 5.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite to verify no regressions
**Notes:**

---

### Phase 6: Live State Comparison Harness [Medium]
**Objective:** Build a harness usable from QA sessions to snapshot, save/load, and compare game state.
**Status:** Not Started

#### Task 6.1: Create state snapshot utility [Medium]
**File:** `tests/infrastructure/state_snapshot.py` (NEW)
**Tests:** `pytest tests/unit/infrastructure/test_state_snapshot.py`
- [ ] Create `snapshot_game_state(game_session) -> dict`:
  - Calls `game_session.to_dict()`
  - Deep-copies the result to avoid mutation
  - Returns the snapshot dict
- [ ] Create `compare_game_states(before: dict, after: dict, ignore_fields=None) -> List[ComparisonResult]`:
  - Uses deep_compare utility from Phase 1
  - Adds expected-difference filtering (spatial indexes, cached stats not in dict)
  - Returns human-readable diff report
- [ ] Create `SaveLoadVerifier` class:
  - `__init__(self, save_service: SaveGameService)`
  - `verify_round_trip(game_session, save_path) -> VerificationReport`:
    1. Snapshot pre-save state
    2. Save via save_service
    3. Load via save_service
    4. Snapshot post-load state
    5. Compare and return report
  - `VerificationReport` dataclass: passed (bool), differences (list), stats (timing, sizes)
- [ ] Write unit tests for snapshot and comparison functions
- [ ] Run tests: `pytest tests/unit/infrastructure/test_state_snapshot.py`
**Notes:**

#### Task 6.2: Create verification integration test [Medium]
**File:** `tests/integration/save_load/test_live_verification.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_live_verification.py`
- [ ] Test: SaveLoadVerifier.verify_round_trip() with minimal game session → passes
- [ ] Test: SaveLoadVerifier.verify_round_trip() with populated game session → passes
- [ ] Test: Introduce deliberate field corruption after save → verification catches it
- [ ] Test: Verification report includes timing and size statistics
**Notes:**

#### Task 6.3: Run full test suite (final verification) [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite: all tests pass
- [ ] Verify total test count increased by expected amount
- [ ] Record final test count
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `pytest tests/` - 13,426 passed, 2 skipped (baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No regressions in existing save/load tests

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] All new round-trip tests pass for all 28 types
- [ ] Registry injection validated for full deserialization chain
- [ ] Cross-object reference integrity validated
- [ ] Live state comparison harness functional
- [ ] Verify changes are consistent with `docs/` — update docs if needed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off (Infrastructure)
- [ ] All Phase 2 tasks checked off (Leaf types)
- [ ] All Phase 3 tasks checked off (Compound types)
- [ ] All Phase 4 tasks checked off (DI & References)
- [ ] All Phase 5 tasks checked off (Full round-trip)
- [ ] All Phase 6 tasks checked off (Live harness)
- [ ] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
