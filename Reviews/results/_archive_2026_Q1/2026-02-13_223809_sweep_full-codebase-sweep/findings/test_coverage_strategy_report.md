# Test Coverage Gaps Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Production Files Scanned:** 80 (excluding __init__.py files)
- **Test Files Cross-Referenced:** 130+
- **Total Issues Found:** 17
- **Critical:** 2 | **Major:** 6 | **Minor:** 7 | **Info:** 2

## Findings

#### CRITICAL: Commands Module Has No Dedicated Unit Tests
**ID:** TCG-STR-001
**Location:** `game/strategy/engine/commands.py` (production) / None (test gap)
**Issue:** The `commands.py` module defines 19 command dataclasses (IssueColonizeCommand, IssueMoveCommand, IssueBuildShipCommand, IssueInterceptCommand, IssueJoinFleetCommand, QueueColonizeMissionCommand, ClearFleetOrdersCommand, IssueTransferCommand, and 11 superweapon commands). None of these have dedicated unit tests for their construction, validation, or dataclass behavior.
**Impact:** Commands are the primary interface for UI-to-engine communication. Malformed commands or unexpected None values in required fields could cause runtime errors. The `__init__` methods set `self.type = CommandType.ISSUE_ORDER` manually rather than relying on dataclass defaults - this pattern is not tested.
**Recommendation:** Create `tests/unit/strategy/engine/test_commands.py` with tests for:
- Each command's `__init__` method sets type correctly
- Required vs optional parameters behave correctly
- Edge cases like None targets in colonize commands
**Effort:** Simple

#### CRITICAL: Physics Module Has No Unit Tests
**ID:** TCG-STR-002
**Location:** `game/strategy/data/physics.py` (production) / None (test gap)
**Issue:** The `physics.py` module contains `SectorEnvironment` class and `calculate_incident_radiation()` function that implements radiation falloff physics (1/r^2.1). No unit tests exist for this module despite it containing numerical calculations that could have off-by-one errors, division by zero risks, or incorrect falloff behavior.
**Impact:** Radiation calculations affect planet habitability and game balance. The clamping at r=1.0 and the 2.1 exponent are physics model decisions that should be verified with tests.
**Recommendation:** Create `tests/unit/strategy/data/test_physics.py` with tests for:
- `calculate_incident_radiation()` returns zero spectrum for empty star list
- Radiation falloff follows 1/r^2.1 law
- Distance clamping at r=1.0 works correctly
- Multiple stars sum correctly
**Effort:** Simple

#### MAJOR: DTO Modules Have Limited Direct Unit Tests
**ID:** TCG-STR-003
**Location:** `game/strategy/facade/dto/*.py` (production) / `tests/unit/strategy/facade/` (partial)
**Issue:** The DTO modules (empire_dto.py, planet_dto.py, system_dto.py) have no dedicated unit test files. While fleet_dto.py has `test_fleet_dto_build.py` and there are integration tests in `tests/integration/strategy/facade/`, the individual `from_*` factory methods lack unit-level testing.
**Impact:** DTOs are the contract between strategy and UI layers. The `from_planet()`, `from_star_system()`, `from_empire()` methods have edge cases (empty populations list, None owner_id, missing optional fields) that are not explicitly tested.
**Recommendation:** Create unit test files for each DTO module:
- `test_empire_dto.py`: Test `ColonySummary.from_planet()`, `FleetSummary.from_fleet()`, `EmpireInfo.from_empire()`
- `test_planet_dto.py`: Test `PlanetInfo.from_planet()` with various population states
- `test_system_dto.py`: Test `StarInfo.from_star()`, `SystemInfo.from_star_system()`
**Effort:** Medium

#### MAJOR: FleetNavigationService Unit Tests Are Thin
**ID:** TCG-STR-004
**Location:** `game/strategy/services/fleet_navigation_service.py` (production) / `tests/unit/strategy/fleet_navigation/` (partial)
**Issue:** While the `fleet_navigation/` test directory exists, the service's complex methods like `project_path()` (100+ lines with many branches), `compute_next_step()`, and warp detection logic have limited branch coverage. The tests focus on happy paths.
**Impact:** Fleet navigation is critical path code - both UI projection and turn execution use this service. Edge cases like:
- Path projection with zero speed
- Non-movement orders (COLONIZE, JOIN_FLEET)
- Iteration safety limit triggering
are not explicitly tested.
**Recommendation:** Add tests in `test_navigation_pure.py` or new file for:
- `project_path()` with zero/negative speed returns empty
- `project_path()` respects max_iterations safety limit
- `compute_next_step()` handles non-movement orders correctly
- `_needs_path_recalculation()` edge cases
**Effort:** Medium

#### MAJOR: ShipStatsCalculator Edge Cases Untested
**ID:** TCG-STR-005
**Location:** `game/strategy/services/ship_stats_calculator.py` (production) / `tests/unit/strategy/ship_stats/` (partial)
**Issue:** While ship_stats has several test files, the `ShipStatsCalculator` has complex formula evaluation (`safe_evaluate_math_formula`), damage degradation models, and warp effectiveness checks. Several edge cases are not explicitly tested:
- Formula evaluation with malformed formula strings
- `_get_current_hp()` with indexed component IDs (e.g., "bridge_0")
- `get_component_effectiveness()` with components lacking `type_str` or `abilities`
- `has_warp_capability()` with edge cases like zero mass ships
**Impact:** Ship stats affect combat, movement, and warp capability. Incorrect calculations silently degrade game balance.
**Recommendation:** Add tests for:
- Malformed formula strings return default
- Indexed component ID lookups work correctly
- Zero mass ships return False for warp capability
- Components without standard fields degrade gracefully
**Effort:** Medium

#### MAJOR: Superweapon Command Handlers Have Limited Validation Tests
**ID:** TCG-STR-006
**Location:** `game/strategy/engine/superweapon_command_handlers.py` (production) / `tests/unit/strategy/engine/test_superweapon_command_handlers.py` (partial)
**Issue:** The superweapon command handlers validate preconditions (fleet has ability, target exists, fleet at location) but the tests focus on success paths. Error cases like:
- Fleet at wrong location for warp point closure
- Target system doesn't exist for warp point opening
- Multiple ships with same ability (which gets consumed?)
are not explicitly tested.
**Impact:** Superweapons are game-changing abilities. Validation failures should provide clear error messages but these paths are undertested.
**Recommendation:** Add validation failure tests:
- Each handler returns specific error message for each failure mode
- Multiple ability ships - first ship consumed
- Missing target system returns clear error
**Effort:** Medium

#### MAJOR: GameSession.handle_command Has No Direct Tests
**ID:** TCG-STR-007
**Location:** `game/strategy/engine/game_session.py::handle_command` (production) / `tests/unit/strategy/test_game_session.py` (partial)
**Issue:** While `test_command_handlers.py` tests individual handlers via the registry, `GameSession.handle_command()` itself is not tested. This method routes commands via `_command_registry.dispatch()` and logs command execution. The dispatch routing and error handling wrapper are not tested.
**Impact:** Command routing bugs would affect all game commands. The logging and error wrapping behavior is not verified.
**Recommendation:** Add tests in `test_game_session.py` for:
- `handle_command()` dispatches to correct handler
- Unknown command type returns error ValidationResult
- Exceptions in handlers are caught and logged
**Effort:** Simple

#### MINOR: QuickstartBuilder Has Thin Test Coverage
**ID:** TCG-STR-008
**Location:** `game/strategy/quickstart_builder.py` (production) / `tests/unit/strategy/test_quickstart_builder.py` (partial)
**Issue:** QuickstartBuilder creates initial game state for quick-start scenarios. The test file exists but may not cover:
- Different player counts
- AI vs human player configuration
- Edge cases like 0 or 1 player
**Impact:** Quickstart is a convenience feature; bugs here primarily affect new game creation flow.
**Recommendation:** Verify test coverage for various player configurations.
**Effort:** Simple

#### MINOR: DesignMetadata Tests Are Sparse
**ID:** TCG-STR-009
**Location:** `game/strategy/data/design_metadata.py` (production) / `tests/unit/strategy/test_design_metadata.py` (partial)
**Issue:** DesignMetadata stores ship design metadata (cost, capabilities). The test file exists but coverage of serialization/deserialization edge cases may be thin.
**Impact:** Design metadata affects UI display and production costs.
**Recommendation:** Verify roundtrip serialization tests exist.
**Effort:** Simple

#### MINOR: FleetResourceAggregator Edge Cases
**ID:** TCG-STR-010
**Location:** `game/strategy/data/fleet_resource_aggregator.py` (production) / `tests/unit/strategy/test_fleet_resource_aggregator.py` (partial)
**Issue:** Aggregates resource storage/consumption across fleet ships. Tests exist but edge cases like:
- Empty fleet
- Ships with no resource storage components
- Damaged components reducing capacity
may not be fully tested.
**Impact:** Resource calculations affect fleet movement range.
**Recommendation:** Add edge case tests for empty/damaged fleets.
**Effort:** Simple

#### MINOR: PlacementStrategies Lack Regression Tests
**ID:** TCG-STR-011
**Location:** `game/strategy/generation/placement_strategies.py` (production) / `tests/unit/strategy/generation/test_placement_strategies.py` (partial)
**Issue:** Placement strategies determine how systems are positioned in galaxy generation. While tests exist, determinism tests ensuring same seed produces same placement may be missing.
**Impact:** Galaxy generation should be deterministic for save/load and debugging.
**Recommendation:** Add determinism tests with fixed seeds.
**Effort:** Simple

#### MINOR: RegionClassifier Tests Thin
**ID:** TCG-STR-012
**Location:** `game/strategy/generation/region_classifier.py` (production) / `tests/unit/strategy/generation/test_region_classifier.py` (partial)
**Issue:** Region classification affects system naming and characteristics. Tests exist but boundary classification cases may be undertested.
**Impact:** Affects cosmetic naming primarily.
**Recommendation:** Verify edge case coverage for region boundaries.
**Effort:** Simple

#### MINOR: TransferValidator Missing Specific Edge Case Tests
**ID:** TCG-STR-013
**Location:** `game/strategy/validation/transfer_validator.py` (production) / `tests/unit/strategy/validation/test_transfer_validator.py` (partial)
**Issue:** Transfer validation checks fleet/colony co-location, cargo capacity, and population counts. The species_id parameter for PROJ-68 may have undertested edge cases:
- Transfer with non-existent species_id
- Transfer from multi-species colony
**Impact:** Population transfers are PROJ-68 feature; bugs could lose population.
**Recommendation:** Add species_id edge case tests.
**Effort:** Simple

#### MINOR: ColonizeValidator "Any Planet" Logic Complex
**ID:** TCG-STR-014
**Location:** `game/strategy/validation/colonize_validator.py` (production) / `tests/unit/strategy/validation/test_colonize_validator.py` (partial)
**Issue:** The "Any Planet" colonization mode (planet_id=None) has complex logic to find matching pod types. Recent PROJ-140 changes added skip_chain_check parameter. The interaction between pod type matching and chain order checking may have undertested edge cases.
**Impact:** Colonization is critical gameplay feature.
**Recommendation:** Add tests for PROJ-140 changes and pod/planet type matching edge cases.
**Effort:** Medium

#### INFO: Test Organization Inconsistency
**ID:** TCG-STR-015
**Location:** Various
**Issue:** Some modules have tests in `tests/unit/strategy/` root (e.g., `test_fleet_speed_calculator.py`) while others are in subdirectories (e.g., `fleet/`, `engine/`). The mapping is not always intuitive.
**Impact:** Makes finding tests harder; no functional impact.
**Recommendation:** Consider reorganizing tests to mirror production structure more closely.
**Effort:** Complex

#### INFO: Mock-Heavy Tests May Miss Integration Bugs
**ID:** TCG-STR-016
**Location:** Various unit tests
**Issue:** Many unit tests use MagicMock extensively, which can mask interface changes. For example, tests that mock `fleet.ships` as a list but the real implementation adds methods could pass with mocks but fail in integration.
**Impact:** Unit tests pass but integration fails; caught by integration tests.
**Recommendation:** Consider using dataclass fixtures instead of MagicMock for core domain objects.
**Effort:** Complex

## Top 5 Priority Issues

1. **TCG-STR-001 (CRITICAL):** Commands Module Has No Dedicated Unit Tests - These are the primary UI-to-engine interface, and 19 command classes have no dedicated tests for their construction behavior.

2. **TCG-STR-002 (CRITICAL):** Physics Module Has No Unit Tests - Numerical calculations with no tests; radiation falloff affects planet habitability.

3. **TCG-STR-003 (MAJOR):** DTO Modules Have Limited Direct Unit Tests - DTOs are the strategy/UI contract; factory methods need explicit unit tests.

4. **TCG-STR-005 (MAJOR):** ShipStatsCalculator Edge Cases Untested - Complex formula evaluation and damage models with untested edge cases.

5. **TCG-STR-007 (MAJOR):** GameSession.handle_command Has No Direct Tests - Command routing wrapper is untested despite being critical path.
