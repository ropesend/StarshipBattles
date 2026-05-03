# Test Coverage Gaps Sweep: Strategy

## Summary
- **Shard:** Strategy (`game/strategy/`)
- **Production Files Scanned:** 96
- **Test Files Cross-Referenced:** 138 (unit + integration)
- **Total Issues Found:** 15
- **Critical:** 3 | **Major:** 6 | **Minor:** 6 | **Info:** 0

---

## Findings

### CRITICAL: Core Untested Modules

#### CRITICAL: Core Radiation Physics Untested
**ID:** TCG-STR-001
**Location:** `game/strategy/data/physics.py`
**Issue:** Module containing `SectorEnvironment` class and `calculate_incident_radiation()` function has NO corresponding unit test file. Only tested indirectly via integration test (`test_radiation.py`). Core radiation physics calculation lacks unit-level coverage.
**Impact:** Radiation physics is foundational to habitability, planet generation, and environmental effects. Physics bugs would propagate through galaxy generation and planetary mechanics without early detection.
**Recommendation:** Create `tests/unit/strategy/test_physics.py` with unit tests for `SectorEnvironment` initialization, `calculate_radiation()` method, and `calculate_incident_radiation()` function including edge cases (zero distance, multiple stars, falloff verification).
**Effort:** Simple

#### CRITICAL: Major facade for ALL UI-engine communication has NO unit tests
**ID:** TCG-STR-002
**Location:** `game/strategy/facade/strategy_session_facade.py` (450 LOC)
**Issue:** Major facade for ALL UI-engine communication has NO unit tests. Only integration tests exist (`test_facade_init.py`, `test_facade_integration.py`). Public API includes 20+ query and command methods with NO isolated unit coverage.
**Impact:** StrategySessionFacade is the critical boundary between UI and game engine. CQRS pattern implementation, DTO conversion logic, and query delegation are untested in isolation. Bugs in facade would cause UI crashes or logic errors with no unit-level safety net.
**Recommendation:** Create comprehensive `tests/unit/strategy/facade/test_strategy_session_facade.py` with unit tests for: handle_command() success/failure paths, process_turn() delegation, get_fleet/get_system/get_empire queries, path preview calculation, error handling for missing entities.
**Effort:** Complex

#### CRITICAL: Galaxy generation placement and region classification
**ID:** TCG-STR-003  
**Location:** `game/strategy/generation/placement_strategies.py` (211 LOC) + `game/strategy/generation/region_classifier.py` (280 LOC)
**Issue:** Galaxy generation placement and region classification modules have NO unit tests. `RandomPlacementStrategy.sample_location()` and `RegionClassifier` (complex geometry with spiral arm detection, cluster classification, position calculations) lack isolated test coverage.
**Impact:** Galaxy generation is a critical path - placement algorithms determine star distribution quality and region classification affects gameplay balance. Untested algorithms could silently produce malformed galaxies. No regression detection for geometry edge cases.
**Recommendation:** Create `tests/unit/strategy/generation/test_placement_strategies.py` and `test_region_classifier.py` with tests for: placement distance constraints, boundary conditions, cluster detection, spiral arm math, region identification accuracy.
**Effort:** Complex

---

### MAJOR: Large Public Interfaces Without Unit Tests

#### MAJOR: Star, Spectrum, and StarGenerator classes with
**ID:** TCG-STR-004
**Location:** `game/strategy/data/stars.py` (560 LOC)
**Issue:** Star, Spectrum, and StarGenerator classes with serialization/deserialization (`to_dict()`, `from_dict()`) have NO dedicated unit tests. Star generation algorithm (`_generate_mass()`, `_determine_type_and_radius()`) is completely untested.
**Impact:** Star generation is foundational to galaxy generation. Serialization bugs would corrupt save files. Generation algorithm bugs affect star distribution quality. No unit-level validation of constraints (mass ranges, type-temperature mapping).
**Recommendation:** Create `tests/unit/strategy/test_stars.py` testing: Spectrum serialization roundtrip, Star to_dict/from_dict, StarGenerator mass distribution constraints, type determination, spectrum calculation, enum conversions.
**Effort:** Medium

#### MAJOR: Planet naming utility functions including critical
**ID:** TCG-STR-005
**Location:** `game/strategy/data/planet_naming.py` (86 LOC)
**Issue:** Planet naming utility functions including critical `to_roman()` conversion and `assign_body_names()` have NO unit tests. Roman numeral conversion for 1-39 range is untested for correctness and edge cases.
**Impact:** Planet naming affects save data consistency and UI display. Incorrect Roman numerals corrupt planet names permanently. `assign_body_names()` logic for grouping and sorting not verified.
**Recommendation:** Create `tests/unit/strategy/test_planet_naming.py` with tests for: `to_roman()` conversion for 1-39 boundary cases, zero/negative inputs, `assign_body_names()` grouping logic, moon suffix generation, mass-based sorting.
**Effort:** Simple

#### MAJOR: Interface contracts for TurnEngine sub-engines
**ID:** TCG-STR-006
**Location:** `game/strategy/interfaces/engines.py` (470 LOC)
**Issue:** Interface contracts for TurnEngine sub-engines (IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IResourceEngine, etc.) are abstract base classes with NO unit tests verifying interface compliance or documenting expected behavior.
**Impact:** Engine interfaces define contract boundaries between turn processing subsystems. Without unit tests, implementations could violate interface expectations. No regression detection for signature changes. Integration tests alone insufficient for interface validation.
**Recommendation:** Create `tests/unit/strategy/interfaces/test_engines_contracts.py` with tests for: abstract method presence, signature validation, mock implementations confirming interface usage patterns, error condition handling.
**Effort:** Medium

#### MAJOR: QuickstartBuilder factory for creating test games has NO unit tests
**ID:** TCG-STR-007
**Location:** `game/strategy/quickstart_builder.py` (299 LOC)
**Issue:** QuickstartBuilder factory for creating test games has NO unit tests. Public methods `load_test_race()`, `create_quickstart_session()`, fixture directory functions untested in isolation.
**Impact:** QuickstartBuilder is critical for test infrastructure. Bugs prevent test game creation, breaking test setup. No validation that fixtures exist or are properly formatted. Save/load race configurations untested.
**Recommendation:** Create `tests/unit/strategy/test_quickstart_builder.py` with tests for: fixture path resolution, race loading/validation, game session creation, initial complex distribution, homeworld placement.
**Effort:** Medium

#### MAJOR: Configuration classes and loaders for planet
**ID:** TCG-STR-008
**Location:** `game/strategy/data/classification_config.py` + `game/strategy/data/race_point_budget.py` + `game/strategy/data/homeworld_presets.py`
**Issue:** Configuration classes and loaders for planet classification, race budgets, and homeworld presets have NO unit tests. These are data model classes with serialization/validation logic.
**Impact:** Configuration bugs affect game balance and save compatibility. No validation of schema changes. Untested deserialization could silently fail or corrupt data.
**Recommendation:** Create `tests/unit/strategy/data/test_config_classes.py` covering: ClassificationConfig instantiation, RacePointBudget calculations, homeworld_presets loading/application, schema validation.
**Effort:** Simple

---

### MINOR: Shallow Test Coverage - Critical Paths

#### MINOR: FleetNavigationService tests exist in `fleet_navigation/`
**ID:** TCG-STR-009
**Location:** `game/strategy/services/fleet_navigation_service.py` (100+ LOC)
**Issue:** FleetNavigationService tests exist in `fleet_navigation/` subdirectory but are INTEGRATION-focused (mock-heavy, delegation verification). NO pure unit tests for core NavigationState dataclass, NavigationStep creation, or pure path computation algorithms.
**Impact:** Navigation logic is critical turn execution path. While pathfinding functions are tested, the service coordination layer (compute_path, compute_next_step, handle_orders) lacks isolated unit coverage. Mock-heavy tests don't catch algorithm bugs.
**Recommendation:** Enhance `tests/unit/strategy/fleet_navigation/` with pure unit tests for: NavigationState.from_fleet() correctness, path segment calculations, turn projection accuracy, order interpretation (MOVE, INTERCEPT, PATROL).
**Effort:** Medium

#### MINOR: Pathfinding functions are tested but intercept calculation
**ID:** TCG-STR-010
**Location:** `game/strategy/data/pathfinding.py` (447 LOC)
**Issue:** Pathfinding functions are tested but intercept calculation (`calculate_intercept_point()`) uses heavy mocking of `project_fleet_path()`. Real fleet path projection NOT tested end-to-end in pathfinding unit tests.
**Impact:** Intercept logic is critical for chase orders. Mocked tests don't catch integration bugs between pathfinding and navigation service. Path projection accuracy issues hidden.
**Recommendation:** Add tests to `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py` for: unmocked FleetNavigationService integration, end-to-end path projection with real fleet state, chaser speed vs target speed edge cases.
**Effort:** Medium

#### MINOR: ConflictResolutionEngine has unit tests for initialization
**ID:** TCG-STR-011
**Location:** `game/strategy/engine/conflict_resolution_engine.py` (150+ LOC)
**Issue:** ConflictResolutionEngine has unit tests for initialization and seed generation but NO tests for `_resolve_conflicts()` core logic (conflict detection, battle setup, casualty application).
**Impact:** Conflict resolution is critical turn processing step. Core algorithm (`_resolve_conflicts`) untested. Battle orchestration, fleet destruction, damage application NOT verified.
**Recommendation:** Enhance `tests/unit/strategy/conflict_resolution/test_core.py` with tests for: conflict detection at contested hexes, multi-empire detection, battle result application, fleet removal, casualty propagation.
**Effort:** Medium

#### MINOR: AstrophysicsLoader, GalaxyLayoutsLoader,
**ID:** TCG-STR-012
**Location:** `game/strategy/generation/loaders/` (3 loader classes)
**Issue:** AstrophysicsLoader, GalaxyLayoutsLoader, SystemBlueprintsLoader ARE tested via `test_astrophysics.py` and `test_system_blueprints.py`, but GalaxyLayoutsLoader `scale_layout_for_radius()` function NOT tested in isolation.
**Impact:** Galaxy layout scaling affects density primitive generation. Unverified scaling math could produce malformed layouts.
**Recommendation:** Add tests to `tests/unit/strategy/generation/test_layout_loader.py` for: scaling field application (sigma, radius, width), position field preservation, primitive parameter correctness.
**Effort:** Simple

---

### MINOR: Error Path Coverage

#### MINOR: BuildQueueSource collection functions are tested but error
**ID:** TCG-STR-013
**Location:** `game/strategy/data/build_queue_source.py` (289 LOC)
**Issue:** BuildQueueSource collection functions are tested but error paths for missing facilities, no shipyards, and production rate loading failures are NOT isolated in unit tests.
**Impact:** Missing error handling for malformed facility data could cause runtime crashes during production queue collection. No graceful degradation for missing production_rates.json.
**Effort:** Simple
**Recommendation:** Add negative test cases to `tests/unit/strategy/data/test_build_queue_source.py` for: missing production_rates.json, invalid facility data, empty empire, no shipyards.

#### MINOR: SimulationBattleResolver implementation has tests but edge
**ID:** TCG-STR-014
**Location:** `game/strategy/adapters/simulation_adapter.py`
**Issue:** SimulationBattleResolver implementation has tests but edge cases around NULL survivors, DI passing, and registries NOT verified.
**Impact:** Battle result application could fail silently if survivor list malformed. Registries not passed to battle engine could cause dependency resolution failures.
**Recommendation:** Enhance `tests/unit/strategy/adapters/test_simulation_adapter.py` with tests for: empty survivor list, registries passing, NULL ship states, battle initialization edge cases.
**Effort:** Simple

#### MINOR: Display formatter has unit tests but edge cases for NULL
**ID:** TCG-STR-015
**Location:** `game/strategy/data/ship_display_formatter.py` (111 LOC)
**Issue:** Display formatter has unit tests but edge cases for NULL ship states, missing stats, and resource calculations NOT fully covered.
**Impact:** UI display crashes on NULL fields or missing calculations. Resource percentage division by zero not tested.
**Recommendation:** Enhance `tests/unit/strategy/test_ship_display_formatter.py` with edge case tests for: NULL HP, zero max_shields, zero resource storage, missing stats calculations.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **TCG-STR-002 (CRITICAL):** `strategy_session_facade.py` - Complete facade for UI/engine boundary with ZERO unit tests. 450 LOC public API untested. **Impact: UI/Engine Corruption Risk**

2. **TCG-STR-003 (CRITICAL):** Galaxy generation placement + region classification - No unit tests for critical galaxy generation algorithms. **Impact: Silent Galaxy Malformation**

3. **TCG-STR-001 (CRITICAL):** `physics.py` - Radiation calculation foundational to habitability, only integration tested. **Impact: Environmental Effects Bugs**

4. **TCG-STR-004 (MAJOR):** `stars.py` - 560 LOC star generation and serialization, zero dedicated unit tests. **Impact: Save File Corruption / Galaxy Quality**

5. **TCG-STR-006 (MAJOR):** `interfaces/engines.py` - Abstract engine interfaces define critical subsystem contracts, no unit verification. **Impact: Interface Violation Risk**

---

## Test Quality Observations

### Strengths
- Pathfinding has excellent unit test coverage with edge cases (basic paths, hybrid paths, intercepts)
- Production engine has deep multi-phase testing (basics, completion, facility queues, tick consumption)
- Galaxy generation density primitives well-tested (geometric, linear, noise, radial, ring, spiral)
- Fleet movement engine has dedicated test subdirectories (basics, batch, warp)

### Weaknesses  
- Data model classes (stars.py, naming.py, configs) lack serialization roundtrip tests
- Facade/interface patterns have integration tests only, no isolated unit validation
- Galaxy generation placement algorithm NOT unit tested (only density maps tested)
- Critical physics calculations (radiation, habitability) scattered between unit and integration with gaps
- Error paths and edge cases for production rates loading, facility detection not isolated

### Systematically Missing
- Unit tests for module-level loader functions (AstrophysicsLoader tested via file existence, not API)
- DTO conversion path testing (FleetInfo.from_fleet, SystemInfo.from_system, etc. untested in isolation)
- QuickstartBuilder test infrastructure (test games can't be created via unit tests)
- Configuration validation (no schema validation tests for ClassificationConfig, RacePointBudget)
