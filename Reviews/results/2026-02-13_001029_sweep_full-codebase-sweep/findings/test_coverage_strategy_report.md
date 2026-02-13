# Test Coverage Gaps Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Production Files Scanned:** 95
- **Test Files Cross-Referenced:** 134
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 7 | **Minor:** 7 | **Info:** 2

## Findings

#### CRITICAL: No dedicated tests for game/strategy/data/naming.py (NameRegistry)
**ID:** TCG-STR-001
**Location:** `game/strategy/data/naming.py` (production) / No test file
**Issue:** The `NameRegistry` class has no unit test file. This module handles:
- Loading name data from YAML files
- Managing unique name allocation for star systems
- Roman numeral conversion (`to_roman`)
- Tracking used/available names to prevent duplicates
**Impact:** Bugs in name generation could cause duplicate system names, crashes when names exhausted, or incorrect Roman numerals. No tests catch file loading errors or edge cases like empty name files.
**Recommendation:** Create `tests/unit/strategy/data/test_naming.py` with tests for:
- `load_data()` with valid/invalid/missing files
- `get_system_name()` including exhaustion behavior
- `to_roman()` edge cases (0, negative, 4000+)
- Used name deduplication logic
**Effort:** Simple

#### CRITICAL: No dedicated tests for game/strategy/data/physics.py (SectorEnvironment, radiation calculation)
**ID:** TCG-STR-002
**Location:** `game/strategy/data/physics.py` (production) / No test file
**Issue:** The physics module contains critical radiation calculations (`calculate_incident_radiation`) and `SectorEnvironment` class with no unit tests. This affects:
- Planet habitability scoring
- Environmental hazard systems
- Multi-star system radiation falloff (inverse 2.1 power law)
**Impact:** Bugs in radiation calculation could make planets incorrectly habitable/uninhabitable, affecting gameplay balance. The mathematical formula (1/r^2.1) is complex and error-prone without tests.
**Recommendation:** Create `tests/unit/strategy/data/test_physics.py` with tests for:
- `calculate_incident_radiation()` with single/multiple stars
- Distance clamping behavior (r < 1.0)
- Spectrum accumulation across multiple stars
- `SectorEnvironment.calculate_radiation()` integration
**Effort:** Medium

#### MAJOR: No dedicated tests for game/strategy/engine/commands.py (Command dataclasses)
**ID:** TCG-STR-003
**Location:** `game/strategy/engine/commands.py` (production) / No test file
**Issue:** The commands module defines 20+ Command dataclasses used throughout the strategy layer but has no unit tests. Commands include:
- `IssueColonizeCommand`, `IssueMoveCommand`, `IssueBuildShipCommand`
- `IssueTransferCommand` with complex cargo parameters
- Superweapon commands (`IssueImplodePlanetCommand`, `IssueStellerateStarCommand`, etc.)
- Mission commands (`QueueColonizeMissionCommand`, etc.)
**Impact:** Command serialization/construction issues could corrupt save games or cause orders to fail silently. The `Command.name` property and `CommandType` enum are untested.
**Recommendation:** Create `tests/unit/strategy/engine/test_commands.py` with tests for:
- Each command's constructor and field initialization
- `Command.name` property returns class name
- Command type enum values
**Effort:** Simple

#### MAJOR: TurnEngine.validate_colonize_order lacks direct unit tests
**ID:** TCG-STR-004
**Location:** `game/strategy/engine/turn_engine.py::validate_colonize_order` / `tests/unit/strategy/turn_engine/`
**Issue:** `TurnEngine.validate_colonize_order()` delegates to `ColonizeValidator` but has no direct tests verifying the delegation or registry injection. Tests exist for `ColonizeValidator` separately but not the TurnEngine wrapper.
**Impact:** Changes to the delegation pattern or registry handling could break colonization validation without test failures.
**Recommendation:** Add tests in `test_turn_processing.py` verifying:
- `validate_colonize_order()` calls `ColonizeValidator.validate()` with correct args
- Registry injection from `self._registries` works correctly
**Effort:** Simple

#### MAJOR: FleetOrder.to_dict() serialization has weak test coverage
**ID:** TCG-STR-005
**Location:** `game/strategy/data/fleet.py::FleetOrder.to_dict` / `tests/unit/strategy/fleet/test_serialization.py`
**Issue:** `FleetOrder.to_dict()` handles 7+ different target types (planet_ref, fleet_ref, transfer, warp_params, ship_id_list, raw) but the serialization tests don't cover all branches, especially:
- `IMPLODE_PLANET` with planet target
- `SELF_DESTRUCT` with ship_id_list
- `OPEN_WARP_POINT` with warp_params dict
**Impact:** Save/load could corrupt superweapon orders introduced in PROJ-102.
**Recommendation:** Add parametrized tests for all order types in `test_serialization.py`
**Effort:** Medium

#### MAJOR: QuickstartBuilder has no comprehensive test coverage
**ID:** TCG-STR-006
**Location:** `game/strategy/quickstart_builder.py` / `tests/unit/quickstart/`
**Issue:** `QuickstartBuilder` has tests for design/race loading but critical methods are untested:
- `build_1p_config()` and `build_2p_config()` return value verification
- `copy_quickstart_designs()` file operations
- `spawn_initial_complexes()` facility creation
- Fallback behavior when fixtures are missing
**Impact:** Quickstart flow could break without CI catching it. Save folder setup and initial facility spawning are untested.
**Recommendation:** Add tests for all builder methods with file system mocking
**Effort:** Medium

#### MAJOR: StrategySessionFacade has incomplete query coverage
**ID:** TCG-STR-007
**Location:** `game/strategy/facade/strategy_session_facade.py` / `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Issue:** Several facade queries lack dedicated tests:
- `get_fleet_remaining_pods()` (PROJ-55 colony pod queries)
- `can_move_to()` validation method
- Event log queries (`get_turn_events()`, `get_all_events()`, `get_events_by_category()`)
**Impact:** UI could receive incorrect data from untested query paths.
**Recommendation:** Extend facade tests to cover all public query methods
**Effort:** Medium

#### MAJOR: GameInitializer._setup_initial_scenario lacks edge case tests
**ID:** TCG-STR-008
**Location:** `game/strategy/engine/game_initializer.py::_setup_initial_scenario` / `tests/unit/strategy/engine/test_game_initializer.py`
**Issue:** Tests cover basic homeworld assignment but miss:
- Systems with no planets (empty system handling)
- More than 4 empires (distribution algorithm)
- `_adjust_homeworld_to_race()` with missing/None homeworld_type
- Atmosphere building with no positive gas preferences
**Impact:** Edge cases in galaxy setup could crash or produce incorrect starting conditions.
**Recommendation:** Add edge case tests for scenario setup
**Effort:** Simple

#### MAJOR: ShipStatsCalculator.has_warp_capability lacks integration tests
**ID:** TCG-STR-009
**Location:** `game/strategy/services/ship_stats_calculator.py::has_warp_capability` / `tests/unit/strategy/ship_stats/`
**Issue:** The static method `has_warp_capability()` has unit tests but no integration tests verifying it works with real component configurations. Tests use mocked `get_calculated_stats()` return values.
**Impact:** Real component configurations with warp drives may not be correctly identified as warp-capable.
**Recommendation:** Add integration tests using real ship designs from fixtures
**Effort:** Medium

#### MINOR: DensityMap.from_config() lacks test coverage
**ID:** TCG-STR-010
**Location:** `game/strategy/generation/density/density_map.py::from_config` / `tests/unit/strategy/generation/density/test_density_map.py`
**Issue:** The `from_config()` factory method is used in production but has minimal direct tests. Most tests use `add_primitive()` directly.
**Impact:** Config parsing bugs could cause incorrect galaxy density fields.
**Recommendation:** Add tests for `from_config()` with various primitive configurations
**Effort:** Simple

#### MINOR: RegionClassifier._classify_spiral edge cases
**ID:** TCG-STR-011
**Location:** `game/strategy/generation/region_classifier.py::_classify_spiral` / `tests/unit/strategy/generation/test_region_classifier.py`
**Issue:** The spiral classification has complex math (logarithmic spiral calculation) but edge cases aren't tested:
- `pitch_angle` = 0 (circular arms)
- Very high arm counts (8+)
- Points at exact arm boundaries
**Impact:** Region classification could fail at mathematical edge cases.
**Recommendation:** Add parametrized edge case tests for spiral classification
**Effort:** Simple

#### MINOR: calculate_habitability has no negative tolerance tests
**ID:** TCG-STR-012
**Location:** `game/strategy/formulas/habitability.py` / `tests/unit/strategy/formulas/test_habitability.py`
**Issue:** Tests verify positive tolerance values but don't test behavior with:
- Negative tolerance values (should be clamped or error)
- Extremely large tolerance values (>1000)
**Impact:** Invalid race configurations could cause unexpected habitability scores.
**Recommendation:** Add boundary tests for tolerance parameters
**Effort:** Simple

#### MINOR: EmpireEconomyCalculator doesn't test design without layers
**ID:** TCG-STR-013
**Location:** `game/strategy/engine/empire_economy_calculator.py` / `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Issue:** Tests cover dict-format and list-format layers but not designs completely missing `layers` key.
**Impact:** Malformed designs could cause KeyError.
**Recommendation:** Add test for facility with `design_data = {}` (no layers)
**Effort:** Simple

#### MINOR: Component inspector service lacks edge case tests
**ID:** TCG-STR-014
**Location:** `game/strategy/services/component_inspector.py` / `tests/unit/strategy/test_component_inspector.py`
**Issue:** `ship_has_ability()` and `count_ability()` are tested but edge cases missing:
- Ship with None design_data
- Component with abilities as list instead of dict
**Impact:** Defensive checks may not handle all real-world data shapes.
**Recommendation:** Add defensive edge case tests
**Effort:** Simple

#### MINOR: Fleet.trigger_speed_recalculation has no unit test
**ID:** TCG-STR-015
**Location:** `game/strategy/data/fleet.py::trigger_speed_recalculation` / `tests/unit/strategy/fleet/`
**Issue:** The method is called indirectly via `add_ship()`/`remove_ship()` but the delegation to `FleetSpeedCalculator.update_fleet_speed()` has no direct test.
**Impact:** Speed recalculation delegation could break silently.
**Recommendation:** Add direct test for `trigger_speed_recalculation()` method
**Effort:** Simple

#### MINOR: Transfer order validator edge cases
**ID:** TCG-STR-016
**Location:** `game/strategy/validation/transfer_validator.py` / `tests/unit/strategy/validation/test_transfer_validator.py`
**Issue:** Tests exist but don't cover:
- Transfer amount = 0 ("all") behavior
- Invalid direction values (not "load" or "unload")
- Species_id parameter validation
**Impact:** Invalid transfer parameters could cause runtime errors.
**Recommendation:** Add edge case tests for transfer validation
**Effort:** Simple

#### INFO: Test fixtures use hardcoded component IDs
**ID:** TCG-STR-017
**Location:** Multiple test files
**Issue:** Tests hardcode component IDs like "fleet_space_yard", "laser", "metal_harvester" which could desync from actual component registry.
**Impact:** Tests could pass with fake IDs even if registry changes break production.
**Recommendation:** Consider using a test fixture that validates IDs exist in registry
**Effort:** Complex

#### INFO: Heavy mocking in TurnEngine tests
**ID:** TCG-STR-018
**Location:** `tests/unit/strategy/turn_engine/`
**Issue:** TurnEngine tests mock most sub-engines (movement_engine, conflict_engine, resource_engine, etc.) which validates orchestration but not real integration.
**Impact:** Individual engine integration bugs could be missed.
**Recommendation:** Add integration tests in `tests/integration/strategy/turn_engine/` that use real engines
**Effort:** Medium

## Top 5 Priority Issues

1. **TCG-STR-001 (CRITICAL)**: `naming.py` - No tests for NameRegistry which handles unique star system name generation. Simple to write, high impact for galaxy generation reliability.

2. **TCG-STR-002 (CRITICAL)**: `physics.py` - No tests for radiation calculation which affects planet habitability. Complex mathematical formula with no verification.

3. **TCG-STR-003 (MAJOR)**: `commands.py` - 20+ Command dataclasses with no unit tests. These are the foundation of the command pattern used throughout the strategy layer.

4. **TCG-STR-005 (MAJOR)**: `FleetOrder.to_dict()` - Superweapon order serialization paths (PROJ-102) have no test coverage, risking save game corruption.

5. **TCG-STR-006 (MAJOR)**: `QuickstartBuilder` - File operations and facility spawning are untested, risking quickstart flow breakage.
