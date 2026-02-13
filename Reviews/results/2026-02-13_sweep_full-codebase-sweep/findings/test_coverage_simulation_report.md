# Test Coverage Gaps Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Production Files Scanned:** 71
- **Test Files Cross-Referenced:** 100
- **Total Issues Found:** 18
- **Critical:** 3 | **Major:** 7 | **Minor:** 6 | **Info:** 2

## Findings

#### CRITICAL: No Unit Tests for ship_stats.py (ShipStatsCalculator)
**ID:** TCG-SIM-001
**Location:** `game/simulation/entities/ship_stats.py` (production) / Missing test file
**Issue:** ShipStatsCalculator is a critical class with 547 lines of code containing 5 distinct calculation phases (damage check, resource allocation, stats aggregation, physics/limits, sensor/defense scores). No corresponding unit test file exists at `tests/unit/simulation/entities/test_ship_stats.py`. The class calculates core combat stats: acceleration, max_speed, turn_speed, shields, crew allocation, mass limits, defense scores, and combat endurance.
**Impact:** High regression risk - changes to stat calculation could silently break combat mechanics, ship performance, and game balance. All 5 phases have complex conditional logic with no test coverage.
**Recommendation:** Create comprehensive test suite covering:
1. Phase 1: Damage threshold marking, crew/life support gathering
2. Phase 2: Crew allocation with priority sorting, component deactivation
3. Phase 3: Resource aggregation, thrust/shield/hangar stats
4. Phase 4: Physics formulas (inverse mass scaling), mass budget validation
5. Phase 5: Defense score calculation (size, maneuver, ECM), sensor scores
**Effort:** Complex

#### CRITICAL: No Unit Tests for ship_stat_querier.py
**ID:** TCG-SIM-002
**Location:** `game/simulation/entities/ship_stat_querier.py` (production) / Missing test file
**Issue:** ShipStatQuerier (150 lines) handles polymorphic ability queries including `get_ability_total()`, `get_total_ability_value()`, `get_total_sensor_score()`, `get_total_ecm_score()`, and `max_weapon_range` property. No corresponding test file exists. These methods use complex stack_group rules (MAX within group, MULTIPLY across groups).
**Impact:** Sensor and ECM score calculations directly affect hit/miss resolution. Bugs in stacking rules would cause combat imbalances that are hard to detect.
**Recommendation:** Create tests for:
- `get_ability_total()` with various ability types and stack groups
- `get_total_ability_value()` with operational_only=True/False
- `max_weapon_range` with regular and seeker weapons
- Edge cases: empty components, missing abilities, mixed ability types
**Effort:** Medium

#### CRITICAL: No Unit Tests for ship_validator_helper.py
**ID:** TCG-SIM-003
**Location:** `game/simulation/entities/ship_validator_helper.py` (production) / Missing test file
**Issue:** ShipValidatorHelper (68 lines) handles design validation with `check_validity()`, `get_validation_warnings()`, and `get_missing_requirements()`. No unit tests exist. The class mediates between Ship and centralized ShipValidator.
**Impact:** Invalid ship designs could pass validation, allowing players to create broken ships. Missing validation warnings would confuse players.
**Recommendation:** Create tests covering:
- `check_validity()` returns True for valid designs, False for invalid
- `get_validation_warnings()` returns appropriate soft warnings
- `get_missing_requirements()` returns empty list for valid, error list for invalid
- Integration with ShipValidator for mass budget, required abilities
**Effort:** Simple

#### MAJOR: designs.py Lacks Any Test Coverage
**ID:** TCG-SIM-004
**Location:** `game/simulation/designs.py` (production) / Missing test file
**Issue:** The `designs.py` module (69 lines) contains factory functions `create_brick()` and `create_interceptor()` for creating pre-configured ship designs. No tests verify these designs are valid, properly configured, or even loadable.
**Impact:** Pre-built ship designs could become invalid after component changes, breaking quickstart battles and tutorials.
**Recommendation:** Create tests that:
- Verify each design function creates a valid ship
- Run validation on created ships
- Ensure expected components are present
- Test designs work with current component registry
**Effort:** Simple

#### MAJOR: resource_manager.py (ResourceRegistry) Missing Edge Case Tests
**ID:** TCG-SIM-005
**Location:** `game/simulation/systems/resource_manager.py` (production) / `tests/unit/simulation/systems/test_resource_manager_edge_cases.py` (limited)
**Issue:** ResourceRegistry has 209 lines with complex state management. The existing test file (`test_resource_manager_edge_cases.py`) has only 15 tests. Missing coverage for:
- `register_storage()` called multiple times for same resource
- `register_generation()` with negative rates
- `reset_stats()` preserving current values while zeroing max/regen
- `modify_value()` clamping to bounds
- `set_max_value()` reducing max below current value
- `update()` regeneration tick behavior
**Impact:** Resource bugs could cause ships to have infinite fuel/energy or lose resources unexpectedly.
**Recommendation:** Expand test suite to cover all public methods with boundary conditions (zero, negative, overflow).
**Effort:** Medium

#### MAJOR: battle_controller.py Missing State Transition Tests
**ID:** TCG-SIM-006
**Location:** `game/simulation/battle_controller.py` (production) / `tests/unit/simulation/battle_controller/` (partial)
**Issue:** BattleController tests exist across 7 files but lack comprehensive state transition testing. Missing:
- Pause/resume state transitions
- Time dilation changes during active combat
- Battle end detection with edge cases (simultaneous deaths, retreat scenarios)
- Retreat integration with RetreatManager
**Impact:** State machine bugs could cause battles to become stuck or incorrectly determine winners.
**Recommendation:** Add state machine tests verifying all valid transitions and rejection of invalid transitions.
**Effort:** Medium

#### MAJOR: formula_system.py Edge Cases Not Tested
**ID:** TCG-SIM-007
**Location:** `game/simulation/formula_system.py` (production) / `tests/unit/simulation/test_formula_exceptions.py` (16 tests only)
**Issue:** The formula system evaluates mathematical expressions for component stats. Only exception handling is tested (16 tests). Missing:
- Complex nested expressions
- Edge values (very large numbers, very small numbers)
- Division by zero handling
- Invalid variable references
- Performance with long formulas
**Impact:** Formula evaluation bugs could crash the game or produce incorrect component stats.
**Recommendation:** Add tests for safe_evaluate_math_formula with complex inputs and edge cases.
**Effort:** Simple

#### MAJOR: projectile_manager.py Missing Guidance System Integration Tests
**ID:** TCG-SIM-008
**Location:** `game/simulation/projectile_manager.py` (production) / `tests/unit/simulation/test_projectile_manager.py` (60 tests)
**Issue:** ProjectileManager (60 tests) is well-tested for basic operations, but guidance system integration (seeker missiles, homing behavior) lacks comprehensive tests. The `projectile_guidance/` tests (27 tests) test guidance in isolation but not the full integration path through ProjectileManager.
**Impact:** Seeker missiles could fail to track targets or have incorrect flight paths.
**Recommendation:** Add integration tests verifying:
- Missile guidance updates during `update()` tick
- Target acquisition and loss scenarios
- Guidance system handoff between manager and projectile
**Effort:** Medium

#### MAJOR: battle_state.py Serialization Round-Trip Gaps
**ID:** TCG-SIM-009
**Location:** `game/simulation/battle_state.py` (production) / `tests/unit/simulation/test_battle_state_serialization.py` (55 tests)
**Issue:** While 55 tests exist for battle state serialization, the tests focus on happy paths. Missing:
- Corrupted data handling
- Version migration (old save format to new)
- Partial state recovery
- Maximum battle size stress testing
**Impact:** Save/load bugs could corrupt battles or crash on edge case data.
**Recommendation:** Add adversarial serialization tests with malformed inputs and stress tests.
**Effort:** Medium

#### MAJOR: combat/damage_calculator.py Missing Armor Interaction Tests
**ID:** TCG-SIM-010
**Location:** `game/simulation/combat/damage_calculator.py` (production) / `tests/unit/simulation/combat/test_damage_calculator.py` (47 tests)
**Issue:** DamageCalculator tests (47) cover basic damage flow but lack comprehensive tests for:
- Emissive armor damage reduction with beam weapons
- Crystalline armor damage reduction with kinetic weapons
- Layer penetration order (shields -> armor -> hull)
- Overkill damage propagation
- Zero/negative damage edge cases
**Impact:** Damage calculations are the core of combat - bugs here fundamentally break gameplay balance.
**Recommendation:** Expand armor mechanics tests to cover all armor types and weapon type interactions.
**Effort:** Medium

#### MINOR: components/abilities/weapons.py Tests Split Across Files
**ID:** TCG-SIM-011
**Location:** `game/simulation/components/abilities/weapons.py` (production) / Multiple test files
**Issue:** Weapon ability tests are split between `test_weapons_isolation.py` (77 tests) and `test_weapons_integration.py` (28 tests). While coverage is good, the split organization makes it hard to verify complete coverage. Some specific weapon types (beam, projectile, seeker, PDC) may have gaps between the two files.
**Impact:** Low - tests exist but organization could lead to duplicate effort or missed cases.
**Recommendation:** Consider a test coverage matrix documenting which weapon types and scenarios each file covers.
**Effort:** Simple

#### MINOR: components/abilities/defense.py Tests Lack Stacking Rule Tests
**ID:** TCG-SIM-012
**Location:** `game/simulation/components/abilities/defense.py` (production) / `tests/unit/simulation/components/abilities/test_defense_*.py`
**Issue:** Defense ability tests (103 tests across isolation and integration) lack explicit tests for stack_group rules. Defense abilities like ShieldProjection, Armor, EmissiveArmor have stacking rules that should be verified.
**Impact:** Defense stacking bugs could make ships invulnerable or too fragile.
**Recommendation:** Add explicit stacking rule tests for each defense ability type.
**Effort:** Simple

#### MINOR: components/abilities/propulsion.py Missing Turn Rate Limit Tests
**ID:** TCG-SIM-013
**Location:** `game/simulation/components/abilities/propulsion.py` (production) / Limited test coverage
**Issue:** ManeuveringThruster and CombatPropulsion abilities lack tests for:
- Maximum turn rate clamping
- Thrust contribution at various power levels
- Strategic movement point calculations
**Impact:** Ships could have unrealistic turning speeds or movement rates.
**Recommendation:** Add boundary condition tests for propulsion ability values.
**Effort:** Simple

#### MINOR: services/design_loader.py Has No Tests
**ID:** TCG-SIM-014
**Location:** `game/simulation/services/design_loader.py` (production) / Missing test file
**Issue:** DesignLoader service loads ship designs from files. No unit tests exist. While `test_simulation_design_loader.py` exists with 8 tests, it may not cover all DesignLoader functionality.
**Impact:** Design loading bugs could cause ship designs to fail silently.
**Recommendation:** Verify test coverage or add missing tests for DesignLoader methods.
**Effort:** Simple

#### MINOR: interfaces/ai_controller.py Interface Tests Shallow
**ID:** TCG-SIM-015
**Location:** `game/simulation/interfaces/ai_controller.py` (production) / `tests/unit/simulation/interfaces/test_ai_controller_interface.py` (8 tests)
**Issue:** AIController interface tests (8) only verify interface contracts. Missing tests for:
- Mock implementations adhering to interface
- Error handling for invalid implementations
- Thread safety considerations
**Impact:** Low - interface testing is naturally limited but could be more robust.
**Recommendation:** Add negative tests verifying interface enforcement.
**Effort:** Simple

#### MINOR: validation/ship_validator.py Missing Complex Validation Scenarios
**ID:** TCG-SIM-016
**Location:** `game/simulation/validation/ship_validator.py` (production) / `tests/unit/simulation/validation/test_ship_validator_rules.py` (50 tests)
**Issue:** ShipValidator tests (50) cover individual rules but lack tests for:
- Multiple simultaneous validation failures
- Validation order independence
- Custom rule registration
- Performance with many components
**Impact:** Complex invalid designs might pass validation or produce confusing error messages.
**Recommendation:** Add tests for multi-rule failure scenarios and validation consistency.
**Effort:** Simple

#### INFO: Test Organization Could Use Consolidation
**ID:** TCG-SIM-017
**Location:** Multiple test directories
**Issue:** Simulation tests are spread across `tests/unit/simulation/` (75 files), `tests/integration/` (strategy-focused), and `simulation_tests/` (scenario-based). The `simulation_tests/` directory provides excellent scenario coverage but is separate from unit tests.
**Impact:** None - this is organizational feedback.
**Recommendation:** Document test organization in a README or consolidate scenario tests into integration test structure.
**Effort:** N/A

#### INFO: No Performance/Load Tests for Simulation Tick
**ID:** TCG-SIM-018
**Location:** `game/simulation/systems/battle_engine.py`
**Issue:** No performance tests exist for battle simulation with many ships (100+), projectiles (1000+), or extended durations (10000+ ticks). The existing tests mock most dependencies.
**Impact:** Performance regressions could go unnoticed until gameplay.
**Recommendation:** Consider adding benchmark tests for simulation tick processing.
**Effort:** N/A

## Top 5 Priority Issues

1. **TCG-SIM-001 (CRITICAL)**: ShipStatsCalculator has zero test coverage despite being the central stat calculation system. This is the highest priority gap - all ship stats flow through this calculator.

2. **TCG-SIM-002 (CRITICAL)**: ShipStatQuerier handles ability aggregation with complex stacking rules but has no tests. Bugs here would affect combat balance calculations.

3. **TCG-SIM-010 (MAJOR)**: DamageCalculator lacks armor interaction tests. Damage is core to combat - comprehensive tests for all armor types and weapon interactions are essential.

4. **TCG-SIM-005 (MAJOR)**: ResourceRegistry edge cases (negative values, regeneration ticks, capacity changes) need better coverage to prevent resource bugs.

5. **TCG-SIM-003 (CRITICAL)**: ShipValidatorHelper has no tests. Ship design validation is player-facing and needs verification.
