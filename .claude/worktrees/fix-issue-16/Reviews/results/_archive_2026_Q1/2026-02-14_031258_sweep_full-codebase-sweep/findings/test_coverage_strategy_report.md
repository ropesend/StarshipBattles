# Test Coverage Gaps Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Production Files Scanned:** 48 (game/strategy/ and subdirectories)
- **Test Files Cross-Referenced:** 72 (tests/unit/strategy/ and tests/integration/strategy/)
- **Total Issues Found:** 12
- **Critical:** 2 | **Major:** 5 | **Minor:** 4 | **Info:** 1

## Findings

#### CRITICAL: PopulationEngine has no unit tests
**ID:** TCG-STR-001
**Location:** `game/strategy/engine/population_engine.py` (production) / no corresponding test file
**Issue:** The PopulationEngine class, which handles logistic population growth for all species on all colonies, has zero unit test coverage. This is a critical game mechanic that affects colony viability and empire growth.
**Impact:** Population growth bugs could go undetected, leading to broken game balance (runaway growth, population death spirals, or stagnation). The logistic growth formula, aptitude conversion, and edge cases (zero population, negative growth, capacity limits) are untested.
**Recommendation:** Create `tests/unit/strategy/engine/test_population_engine.py` with tests for:
- `_aptitude_to_growth_rate()` conversion at boundary values (1, 50, 100)
- Logistic growth formula correctness
- Zero/negative population handling
- Happiness modifier effects
- Race config lookup fallback logic
- Carrying capacity clamping
**Effort:** Medium

#### CRITICAL: HarvestingEngine has no unit tests
**ID:** TCG-STR-002
**Location:** `game/strategy/engine/harvesting_engine.py` (production) / no corresponding test file
**Issue:** The HarvestingEngine class, which extracts planetary resources into empire pools and calculates storage capacity, has no dedicated unit tests. This engine handles resource harvesting formulas, storage aggregation, and component ability extraction.
**Impact:** Resource extraction bugs could break the economy system. Incorrect harvesting rates, storage capacity calculation errors, or registry lookup failures would go undetected.
**Recommendation:** Create `tests/unit/strategy/engine/test_harvesting_engine.py` with tests for:
- `process_harvesting()` with operational/non-operational facilities
- `recalculate_storage()` with multiple facilities
- `get_harvester_info()` with inline abilities vs registry lookup
- Storage capacity aggregation
- Edge cases: missing resources, zero quality, empty facilities
**Effort:** Medium

#### MAJOR: EmpireEconomyCalculator missing from tests
**ID:** TCG-STR-003
**Location:** `game/strategy/engine/empire_economy_calculator.py` (production) / test file search returned no results
**Issue:** Despite grep finding no test file for `test_empire_economy_calculator`, this module handles critical economy calculations including income, expenses, and budget projections. The lack of direct tests means economy balance relies on integration testing only.
**Impact:** Economy formula bugs could cause game-breaking imbalances (infinite money, instant bankruptcy).
**Recommendation:** Create dedicated unit tests for economy calculation methods, especially edge cases like zero income, maximum expenses, and resource overflow.
**Effort:** Medium

#### MAJOR: physics.py radiation calculation untested
**ID:** TCG-STR-004
**Location:** `game/strategy/data/physics.py` (production) / no test file found for `test_radiation` in strategy tests
**Issue:** The `calculate_incident_radiation()` function and `SectorEnvironment` class have no dedicated unit tests. This physics model calculates radiation falloff using inverse 2.1 power law and affects planet habitability.
**Impact:** Incorrect radiation calculations could affect planet habitability scores, leading to unexpected colony viability issues.
**Recommendation:** Create `tests/unit/strategy/data/test_physics.py` with tests for:
- `calculate_incident_radiation()` at various distances
- Distance clamping (r < 1.0)
- Multiple stars contribution
- Spectrum component aggregation
**Effort:** Simple

#### MAJOR: ResupplyEngine coverage gap
**ID:** TCG-STR-005
**Location:** `game/strategy/engine/resupply_engine.py` (production) / limited test coverage
**Issue:** The ResupplyEngine handles fleet supply replenishment, but grep results show limited dedicated test coverage. Supply mechanics are critical for fleet operations and combat readiness.
**Impact:** Supply bugs could leave fleets stranded or with incorrect supply levels.
**Recommendation:** Verify test coverage and add edge case tests for supply transfer, capacity limits, and partial resupply scenarios.
**Effort:** Simple

#### MAJOR: SimulationBattleResolver integration tests weak
**ID:** TCG-STR-006
**Location:** `game/strategy/adapters/simulation_adapter.py` (production) / `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py`
**Issue:** The SimulationBattleResolver is the bridge between strategy and simulation layers for combat resolution. While edge case tests exist, there's limited testing of actual battle outcomes and result application to fleets.
**Impact:** Battle resolution bugs could cause incorrect fleet survivor counts, wrong winner determination, or state corruption.
**Recommendation:** Add integration tests that verify full battle flow: fleet setup -> battle resolution -> survivor application -> fleet state update.
**Effort:** Medium

#### MAJOR: FleetNavigationService warp detection edge cases
**ID:** TCG-STR-007
**Location:** `game/strategy/services/fleet_navigation_service.py` (production) / tests exist but gaps identified
**Issue:** While FleetNavigationService has 73 tests across 5 test files, there's no explicit test for warp lane connectivity validation. The service detects warp jumps (distance > 1) but doesn't validate that the warp connection actually exists in the galaxy.
**Impact:** Fleets could theoretically warp to invalid destinations if the pathfinding returns incorrect results.
**Recommendation:** Add tests verifying that `project_path()` and `compute_path()` only use valid warp connections from the galaxy's warp lane data.
**Effort:** Simple

#### MINOR: ConflictResolutionEngine draw handling
**ID:** TCG-STR-008
**Location:** `game/strategy/engine/conflict_resolution_engine.py` (production) / `tests/unit/strategy/conflict_resolution/test_core.py`
**Issue:** The `_resolve_combat_simulated()` method handles draws by comparing survivor counts, but there's no explicit test for the draw case where both teams have equal survivors.
**Impact:** Edge case bug could cause inconsistent winner selection in draw scenarios.
**Recommendation:** Add test case for battle draw with equal survivor counts on both teams.
**Effort:** Simple

#### MINOR: DensityMap edge cases with negative weights
**ID:** TCG-STR-009
**Location:** `game/strategy/generation/density/density_map.py` (production) / `tests/unit/strategy/generation/density/test_density_map.py`
**Issue:** Tests verify that zero weight primitives are ignored, but negative weights are also logged and ignored. No test explicitly verifies negative weight handling.
**Impact:** Low - the code handles it correctly but behavior is undocumented in tests.
**Recommendation:** Add test case for `add_primitive()` with negative weight.
**Effort:** Simple

#### MINOR: QuickstartBuilder scenario validation
**ID:** TCG-STR-010
**Location:** `game/strategy/quickstart_builder.py` (production) / `tests/unit/strategy/test_quickstart_builder.py`
**Issue:** The QuickstartBuilder creates game sessions from presets. Tests exist but don't verify invalid scenario handling (missing keys, corrupt preset data).
**Impact:** Crash on malformed preset files during quickstart.
**Recommendation:** Add negative test cases for invalid/incomplete preset configurations.
**Effort:** Simple

#### MINOR: GameSession from_dict missing fields handling
**ID:** TCG-STR-011
**Location:** `game/strategy/engine/game_session.py` (production) / `tests/unit/strategy/test_game_session_events.py`
**Issue:** Tests verify that missing `event_log` key creates an empty EventLog, but there's no comprehensive test for other missing fields that could exist in old save files.
**Impact:** Potential crashes when loading saves from older versions with missing fields.
**Recommendation:** Add backward compatibility tests for all optional fields in `from_dict()`.
**Effort:** Simple

#### INFO: Test organization could be improved
**ID:** TCG-STR-012
**Location:** `tests/unit/strategy/` (organization)
**Issue:** Test files are well-organized but some subdirectories have inconsistent naming patterns. For example, `turn_engine/` contains tests that could be in `engine/test_turn_engine.py` for consistency with other engine tests.
**Impact:** No functional impact, but minor confusion for developers.
**Recommendation:** Consider consolidating engine tests under `tests/unit/strategy/engine/` for consistency.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-STR-001: PopulationEngine has no unit tests** - CRITICAL. Population growth is a core game mechanic with complex formula that needs verification.

2. **TCG-STR-002: HarvestingEngine has no unit tests** - CRITICAL. Resource harvesting drives the economy and needs explicit coverage.

3. **TCG-STR-003: EmpireEconomyCalculator missing from tests** - MAJOR. Economy calculations affect all strategic decisions.

4. **TCG-STR-004: physics.py radiation calculation untested** - MAJOR. Physics model affects habitability which impacts gameplay.

5. **TCG-STR-006: SimulationBattleResolver integration tests weak** - MAJOR. Combat resolution is the core conflict mechanic.
