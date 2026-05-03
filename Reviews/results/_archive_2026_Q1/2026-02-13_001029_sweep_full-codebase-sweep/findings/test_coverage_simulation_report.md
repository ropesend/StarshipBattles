# Test Coverage Gaps Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Production Files Scanned:** 67
- **Test Files Cross-Referenced:** 42
- **Total Issues Found:** 18
- **Critical:** 3 | **Major:** 7 | **Minor:** 6 | **Info:** 2

## Findings

#### CRITICAL: Projectile Entity Has No Unit Tests
**ID:** TCG-SIM-001
**Location:** `game/simulation/entities/projectile.py` (production) / `tests/unit/simulation/entities/test_projectile*.py` (missing)
**Issue:** The `Projectile` class which handles projectile physics, tracking, homing behavior, impact detection, and lifecycle has zero dedicated unit tests. Glob search for `test_projectile*.py` returned no files.
**Impact:** Projectile physics bugs (speed, tracking, collision) would go undetected. Seeker missiles, torpedoes, and other guided munitions are critical combat mechanics. Regression risk is high for any changes to projectile behavior.
**Recommendation:** Create comprehensive unit tests covering:
- Projectile initialization with various weapon ability types
- Movement and physics updates (straight-line and homing)
- Lifetime/endurance expiration
- Impact detection logic
- Stealth level handling
- Target acquisition and retargeting
**Effort:** Medium

#### CRITICAL: ShipStatQuerier Has No Unit Tests
**ID:** TCG-SIM-002
**Location:** `game/simulation/entities/ship_stat_querier.py` (production) / `tests/unit/simulation/entities/test_ship_stat_querier.py` (missing)
**Issue:** `ShipStatQuerier` (extracted in PROJ-88) aggregates critical ship stats like `get_ability_total()`, `get_total_sensor_score()`, `get_total_ecm_score()`, and `max_weapon_range`. No dedicated unit tests exist.
**Impact:** These methods directly affect combat calculations (hit/miss, damage). Stack group aggregation rules (MAX within group, MULTIPLY across groups) are complex and error-prone without tests.
**Recommendation:** Create unit tests covering:
- `get_ability_total()` with various ability types
- Stack group rule verification (MAX within, MULTIPLY across)
- `get_total_ability_value()` with operational_only flag
- `max_weapon_range` calculation including SeekerWeapon endurance fallback
- Edge cases: no components, no abilities, destroyed components
**Effort:** Medium

#### CRITICAL: ShipValidator Rules Have No Unit Tests
**ID:** TCG-SIM-003
**Location:** `game/simulation/validation/ship_validator.py` (production) / `tests/unit/simulation/validation/test_ship_validator*.py` (missing)
**Issue:** All validation rules (LayerConstraintRule, UniqueComponentRule, ExclusiveGroupRule, MountDependencyRule, LayerRestrictionDefinitionRule, MassBudgetRule, ClassRequirementsRule, ResourceDependencyRule, ShipDesignValidator) have zero dedicated unit tests.
**Impact:** Ship design validation is critical for player experience. Invalid designs being allowed or valid designs being rejected would be major bugs. The validation system has 9 distinct rule classes with complex interaction logic.
**Recommendation:** Create comprehensive tests for each rule class:
- Test each rule in isolation with various ship/component configurations
- Test rule interaction via ShipDesignValidator
- Test both validation success and failure paths
- Test warning generation (ResourceDependencyRule)
- Test edge cases: empty ship, max components, boundary values
**Effort:** Complex

#### MAJOR: BattleController Missing Edge Case Tests
**ID:** TCG-SIM-004
**Location:** `game/simulation/battle_controller.py` (production) / `tests/unit/simulation/test_battle_controller.py` (partial coverage)
**Issue:** While BattleController has some test coverage, critical edge cases are untested:
- Reinforcement arrival during active combat
- Multiple simultaneous ship deaths
- Battle pause/resume state transitions
- Very large battles (100+ ships performance)
- Zero-ship edge cases
**Impact:** Battle state corruption under edge conditions could cause crashes or incorrect outcomes.
**Recommendation:** Add edge case tests for battle lifecycle management
**Effort:** Medium

#### MAJOR: DamageCalculator Armor Penetration Edge Cases
**ID:** TCG-SIM-005
**Location:** `game/simulation/combat/damage_calculator.py` (production) / `tests/unit/simulation/combat/test_damage_calculator.py` (partial)
**Issue:** While DamageCalculator has 47 test functions, some edge cases are not covered:
- Armor piercing values greater than total armor
- Exactly zero armor remaining
- Multiple concurrent damage events on same tick
- Damage types with zero base damage but additive bonuses
**Impact:** Edge cases in damage calculation could cause exploits or balance issues.
**Recommendation:** Add parametrized tests for boundary conditions
**Effort:** Simple

#### MAJOR: WeaponFiringSystem Missing Multishot Tests
**ID:** TCG-SIM-006
**Location:** `game/simulation/combat/weapon_firing_system.py` (production) / `tests/unit/simulation/combat/test_weapon_firing_system.py` (12 tests)
**Issue:** The weapon firing system has only 12 tests. Missing coverage for:
- Weapons with multiple shots per volley
- Weapons with spread patterns
- Point defense interception logic
- Simultaneous firing from multiple ships
**Impact:** Weapon firing bugs affect core gameplay loop.
**Recommendation:** Add tests for multi-shot weapons and point defense
**Effort:** Medium

#### MAJOR: TargetingSystem Missing AI Priority Tests
**ID:** TCG-SIM-007
**Location:** `game/simulation/combat/targeting_system.py` (production) / `tests/unit/simulation/combat/test_targeting_system.py` (18 tests)
**Issue:** Targeting system has 18 tests but lacks coverage for:
- AI target priority scoring algorithms
- Target switching behavior
- Target out-of-range handling
- Stealth/detection interaction
**Impact:** AI targeting bugs make combat feel unbalanced or unfair.
**Recommendation:** Add AI priority and target selection tests
**Effort:** Medium

#### MAJOR: BattleEngine Tick Processing Incomplete Coverage
**ID:** TCG-SIM-008
**Location:** `game/simulation/systems/battle_engine.py` (production) / `tests/unit/simulation/systems/test_battle_engine_tick.py` (exists)
**Issue:** BattleEngine tick tests exist but don't cover:
- Tick ordering guarantees (movement before firing, etc.)
- Resource consumption timing
- Cooldown timer edge cases (sub-tick precision)
- Component damage during tick (mid-tick death)
**Impact:** Combat timing bugs cause inconsistent behavior.
**Recommendation:** Add tick ordering and timing tests
**Effort:** Medium

#### MAJOR: FormulaSystem Overflow/Underflow Not Tested
**ID:** TCG-SIM-009
**Location:** `game/simulation/formula_system.py` (production) / `tests/unit/simulation/test_formula_exceptions.py` (partial)
**Issue:** Formula exception tests cover syntax errors and division by zero, but not:
- Integer overflow (very large numbers)
- Float precision issues (very small decimals)
- NaN/Infinity propagation
- Deep recursion (nested function calls)
**Impact:** Formula edge cases could cause crashes or incorrect stat calculations.
**Recommendation:** Add boundary value tests for formula evaluation
**Effort:** Simple

#### MAJOR: Design System Serialization Roundtrip Gaps
**ID:** TCG-SIM-010
**Location:** `game/simulation/designs.py` (production) / `tests/unit/simulation/test_designs.py` (if exists)
**Issue:** Ship design serialization needs tests for:
- Roundtrip (save -> load -> save produces identical output)
- Version compatibility (loading older save formats)
- Corrupted data handling (missing fields, wrong types)
- Very large designs (many components)
**Impact:** Save/load bugs cause player data loss.
**Recommendation:** Add roundtrip and corruption handling tests
**Effort:** Medium

#### MINOR: AbilityAggregator Missing Concurrent Modification Tests
**ID:** TCG-SIM-011
**Location:** `game/simulation/entities/ability_aggregator.py` (production) / `tests/unit/simulation/entities/test_ability_aggregator.py` (69 tests)
**Issue:** AbilityAggregator has good coverage but lacks tests for:
- Component removal during iteration
- Concurrent ability activation
- Ability with None values
**Impact:** Edge case bugs in ability aggregation.
**Recommendation:** Add concurrent modification edge cases
**Effort:** Simple

#### MINOR: ShipCombatEngine Heat Management Not Tested
**ID:** TCG-SIM-012
**Location:** `game/simulation/entities/ship_combat_engine.py` (production)
**Issue:** Heat management, overheating, and cooling mechanics are not tested if ship_combat_engine is responsible for this logic.
**Impact:** Heat-based gameplay mechanics may have bugs.
**Recommendation:** Verify heat system testing or add if missing
**Effort:** Simple

#### MINOR: ShipFormation Missing Complex Formation Tests
**ID:** TCG-SIM-013
**Location:** `tests/unit/simulation/entities/test_ship_formation.py` (60 tests)
**Issue:** Formation tests exist but may not cover:
- Very large formations (20+ ships)
- Dynamic reformation during combat
- Formation leader death handling
**Impact:** Formation edge cases in large battles.
**Recommendation:** Add stress tests for large formations
**Effort:** Simple

#### MINOR: BattleStateSerializer Version Migration Not Tested
**ID:** TCG-SIM-014
**Location:** `tests/unit/simulation/test_battle_state_serialization.py` (exists)
**Issue:** Serialization tests may not cover version migration if battle state format changes.
**Impact:** Loading older battle states could fail.
**Recommendation:** Add version compatibility tests if applicable
**Effort:** Simple

#### MINOR: PropulsionAbility Strategic Movement Not Tested
**ID:** TCG-SIM-015
**Location:** `game/simulation/components/abilities/propulsion.py` (production)
**Issue:** While CombatPropulsion and ManeuveringThruster may have coverage, StrategicMovement and WarpJump abilities need verification for:
- Movement point calculations
- Warp tonnage limits
- Energy cost consumption
**Impact:** Strategic layer movement bugs.
**Recommendation:** Verify or add strategic ability tests
**Effort:** Simple

#### MINOR: ProjectileManager Missing Batch Update Tests
**ID:** TCG-SIM-016
**Location:** `game/simulation/projectile_manager.py` (production) / `tests/unit/simulation/test_projectile_manager.py` (exists)
**Issue:** ProjectileManager tests exist but may not cover batch update scenarios with hundreds of projectiles.
**Impact:** Performance degradation with many projectiles.
**Recommendation:** Add stress/performance tests
**Effort:** Simple

#### INFO: Test Organization Inconsistency
**ID:** TCG-SIM-017
**Location:** `tests/unit/simulation/` (various)
**Issue:** Some test files are in `tests/unit/simulation/` root while corresponding production code is in subdirectories. Example: `test_projectile_manager.py` is at root but `retreat_manager` is in `managers/`. This inconsistency makes it harder to find test coverage gaps.
**Recommendation:** Consider mirroring production directory structure in tests more consistently.
**Effort:** N/A (organizational)

#### INFO: Simulation Integration Tests Sparse
**ID:** TCG-SIM-018
**Location:** `tests/integration/` and `simulation_tests/`
**Issue:** While unit tests are extensive, integration tests that verify multi-system interactions (e.g., weapon fires -> projectile spawns -> travels -> impacts -> damage calculated -> component destroyed -> ship stats updated) are less common. The `simulation_tests/` directory exists but coverage of full combat flow paths should be verified.
**Recommendation:** Consider adding more end-to-end combat simulation tests that verify entire damage pipelines.
**Effort:** N/A (organizational)

## Top 5 Priority Issues

1. **TCG-SIM-001: Projectile Entity Has No Unit Tests** - The Projectile class handles core combat physics and has zero tests. This is the highest risk gap as projectile behavior affects every ranged weapon in the game.

2. **TCG-SIM-003: ShipValidator Rules Have No Unit Tests** - Ship design validation affects the player's ability to build ships. Invalid validation logic could block valid designs or allow invalid ones, both major UX issues.

3. **TCG-SIM-002: ShipStatQuerier Has No Unit Tests** - Stat aggregation directly affects combat calculations. Stack group rules are complex and bugs here would cause incorrect damage, hit chances, etc.

4. **TCG-SIM-008: BattleEngine Tick Processing Incomplete Coverage** - Tick ordering and timing are fundamental to deterministic combat simulation. Gaps here could cause non-reproducible battle outcomes.

5. **TCG-SIM-010: Design System Serialization Roundtrip Gaps** - Save/load bugs cause player data loss, which is unacceptable. Roundtrip testing is essential for any serialization system.
