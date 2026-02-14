# Test Coverage Gaps Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Production Files Scanned:** 69
- **Test Files Cross-Referenced:** 101+
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 7 | **Minor:** 7 | **Info:** 2

## Findings

#### CRITICAL: No Direct Tests for Ship Entity Core Methods
**ID:** TCG-SIM-001
**Location:** `game/simulation/entities/ship.py` (production) / `tests/unit/simulation/entities/` (test gap)
**Issue:** The Ship class is 800+ lines with 40+ public methods but has no dedicated `test_ship.py` file. Key untested methods include:
- `die()` - death logic and state transitions
- `update()` - per-tick updates with context handling
- `recalculate_stats()` - stat aggregation pipeline
- `add_component()` / `remove_component()` - component management
- `change_class()` - class migration logic
- `get_missing_requirements()` / `get_validation_warnings()` - validation helpers

Related test files exist for mixins (physics, serialization, loader, formation) but the core Ship class methods are only tested indirectly through integration tests.
**Impact:** Core entity logic has no isolated unit tests. Bugs in death handling, component management, or stat recalculation could go undetected.
**Recommendation:** Create `tests/unit/simulation/entities/test_ship.py` covering:
1. `die()` state transitions and is_alive flag
2. `add_component()` success/failure paths
3. `recalculate_stats()` with various component configurations
4. `update()` with different context scenarios
5. Validation method edge cases
**Effort:** Complex

#### CRITICAL: No Tests for Propulsion Abilities
**ID:** TCG-SIM-002
**Location:** `game/simulation/components/abilities/propulsion.py` (production) / No corresponding test file
**Issue:** Four propulsion ability classes with zero dedicated tests:
- `CombatPropulsion` - thrust calculation
- `ManeuveringThruster` - turn rate calculation
- `StrategicMovement` - movement point calculation
- `WarpJump` - warp capability with tonnage limit

These are core movement abilities. The `STAT_BINDINGS`, `recalculate()`, `sync_data()`, and `get_ui_rows()` methods are all untested.
**Impact:** Movement and propulsion bugs could go undetected. The `WarpJump.can_jump()` method validation is critical for gameplay.
**Recommendation:** Create `tests/unit/simulation/components/abilities/test_propulsion.py` covering:
1. Each class initialization with primitive and dict data
2. `recalculate()` with stat modifiers
3. `sync_data()` state updates
4. `WarpJump.can_jump()` boundary conditions
**Effort:** Medium

#### MAJOR: ResourceConsumption and ResourceGeneration Lack Dedicated Tests
**ID:** TCG-SIM-003
**Location:** `game/simulation/components/abilities/resources.py` (production) / `tests/unit/simulation/components/abilities/test_resource_consumption.py` (partial)
**Issue:** While `test_resource_consumption.py` exists, it only tests basic consumption scenarios. Missing coverage:
- `ResourceConsumption.get_strategic_cost()` method
- `ResourceConsumption` with "strategic_per_hex" trigger type
- `ResourceGeneration` class has no dedicated tests
- `ResourceStorage` `recalculate()` with `CAPACITY_MULT` modifier
- `check_available()` vs `check_and_consume()` difference testing
**Impact:** Strategic map fuel consumption logic may have untested edge cases. Generation rate scaling is untested.
**Recommendation:** Expand test coverage for all three resource ability classes with modifier scenarios.
**Effort:** Medium

#### MAJOR: WeaponFiringSystem Tests Missing Edge Cases
**ID:** TCG-SIM-004
**Location:** `game/simulation/combat/weapon_firing_system.py` (production) / `tests/unit/simulation/combat/test_weapon_firing_system.py` (existing)
**Issue:** WeaponFiringSystem tests exist but miss critical edge cases:
- `_fire_beam_weapon()` with negative damage values
- `_fire_projectile_weapon()` with zero projectile speed
- `_fire_seeker_weapon()` with dead target
- Resource consumption failure mid-burst
- Weapon firing with destroyed component
- Cooldown reset logic on failed fire attempts
**Impact:** Combat firing edge cases could cause crashes or unexpected behavior.
**Recommendation:** Add negative/boundary tests for all fire methods.
**Effort:** Medium

#### MAJOR: BattleEngine Missing Tick Processing Edge Case Tests
**ID:** TCG-SIM-005
**Location:** `game/simulation/systems/battle_engine.py` (production) / `tests/unit/simulation/systems/test_battle_engine_tick.py` (partial)
**Issue:** Battle engine tick processing tests exist but miss:
- Tick processing with empty ship lists
- Concurrent ship death during tick
- Mid-tick target invalidation
- Resource depletion during combat tick
- Projectile collision during the same tick as creation
**Impact:** Complex battle scenarios with multiple simultaneous events may have bugs.
**Recommendation:** Add stress tests with edge case scenarios.
**Effort:** Complex

#### MAJOR: FormulaSystem Tests Only Cover Exceptions
**ID:** TCG-SIM-006
**Location:** `game/simulation/formula_system.py` (production) / `tests/unit/simulation/test_formula_exceptions.py` (narrow)
**Issue:** The formula system test file only tests exception handling for missing formulas. Missing:
- Actual formula evaluation with real inputs
- Formula caching behavior
- Formula performance with large input sets
- Formula validation at load time
**Impact:** Formula calculation bugs could affect damage, accuracy, and other critical combat calculations.
**Recommendation:** Create `test_formula_system.py` with actual formula evaluation tests.
**Effort:** Medium

#### MAJOR: No Tests for BattleService Serialization/Deserialization
**ID:** TCG-SIM-007
**Location:** `game/simulation/services/battle_service.py` (production) / `tests/unit/simulation/services/test_battle_service.py` (partial)
**Issue:** BattleService tests exist but serialization roundtrip is not tested:
- `save_battle_state()` / `load_battle_state()` cycle
- Battle continuation after save/load
- Projectile state preservation during save
- Mid-combat saves with active seekers
**Impact:** Save/load during combat could lose state or corrupt game data.
**Recommendation:** Add serialization roundtrip tests for battle state.
**Effort:** Medium

#### MAJOR: No Tests for DesignLoader Error Recovery
**ID:** TCG-SIM-008
**Location:** `game/simulation/services/design_loader.py` (production) / `tests/unit/simulation/services/test_simulation_design_loader.py` (partial)
**Issue:** Design loader tests cover happy path but miss:
- Malformed JSON handling
- Missing required fields
- Invalid component references
- Circular design dependencies
- Version compatibility checks
**Impact:** Corrupt or incompatible design files could crash the game.
**Recommendation:** Add negative tests for malformed design files.
**Effort:** Medium

#### MINOR: CombatEndurance Missing Boundary Tests
**ID:** TCG-SIM-009
**Location:** `game/simulation/entities/combat_endurance.py` (production) / `tests/unit/simulation/entities/test_combat_endurance.py` (existing)
**Issue:** Tests exist but miss boundary conditions:
- Zero endurance initialization
- Negative endurance values (should they clamp?)
- Float precision issues with very small endurance values
- Concurrent endurance modification
**Impact:** Edge cases in endurance calculations could cause unexpected behavior.
**Recommendation:** Add boundary condition tests.
**Effort:** Simple

#### MINOR: ShipStatQuerier Not Directly Tested
**ID:** TCG-SIM-010
**Location:** `game/simulation/entities/ship_stat_querier.py` (production) / No dedicated test file
**Issue:** ShipStatQuerier helper class has no direct tests. It's tested indirectly through Ship tests but:
- Query caching behavior untested
- Invalid stat key handling untested
- Performance with many queries untested
**Impact:** Low - functionality is tested indirectly.
**Recommendation:** Add direct unit tests for caching behavior.
**Effort:** Simple

#### MINOR: ShipValidatorHelper Not Directly Tested
**ID:** TCG-SIM-011
**Location:** `game/simulation/entities/ship_validator_helper.py` (production) / No dedicated test file
**Issue:** Validation helper tested indirectly but missing direct coverage for:
- `get_missing_requirements()` with partial component sets
- `get_validation_warnings()` with edge case configurations
**Impact:** Low - tested through integration tests.
**Recommendation:** Consider adding direct tests for complex validation scenarios.
**Effort:** Simple

#### MINOR: LayerData Entity Has Minimal Tests
**ID:** TCG-SIM-012
**Location:** `game/simulation/entities/layer_data.py` (production) / `tests/unit/simulation/entities/test_layer_data.py` (minimal)
**Issue:** LayerData tests exist but are minimal:
- Only tests basic creation
- No tests for component list operations
- No tests for radius_pct validation
**Impact:** Low - simple data class.
**Recommendation:** Add tests for edge cases if the class becomes more complex.
**Effort:** Simple

#### MINOR: ModifierSchema Validation Not Comprehensive
**ID:** TCG-SIM-013
**Location:** `game/simulation/components/modifier_schema.py` (production) / `tests/unit/simulation/components/test_modifier_schema.py` (partial)
**Issue:** Schema validation tests exist but miss:
- Nested modifier validation
- Circular reference detection
- Version migration scenarios
**Impact:** Invalid modifier configurations could pass validation.
**Recommendation:** Add negative tests for malformed schemas.
**Effort:** Simple

#### MINOR: BattleConfig Tests Could Be More Thorough
**ID:** TCG-SIM-014
**Location:** `game/simulation/battle_config.py` (production) / `tests/unit/simulation/test_battle_config.py` (existing)
**Issue:** Battle config tests exist but could test:
- Invalid configuration combinations
- Configuration inheritance/overrides
- Runtime configuration changes
**Impact:** Low - config is mostly static.
**Recommendation:** Add tests if dynamic config becomes needed.
**Effort:** Simple

#### MINOR: PhysicsConstants Could Test Derived Values
**ID:** TCG-SIM-015
**Location:** `game/simulation/physics_constants.py` (production) / `tests/unit/simulation/test_physics_constants.py` (existing)
**Issue:** Tests verify constants exist but don't test:
- Derived calculations using constants
- Constant consistency (e.g., TICK_RATE * TICKS_PER_SECOND == 1)
**Impact:** Low - constants are straightforward.
**Recommendation:** Add consistency check tests.
**Effort:** Simple

#### INFO: Ability Base Class Tests Are Exemplary
**ID:** TCG-SIM-016
**Location:** `game/simulation/components/abilities/base.py` / `tests/unit/simulation/components/abilities/test_ability_base.py`
**Issue:** Not an issue - this is a positive example. The ability base class has comprehensive tests for:
- All STAT_BINDINGS operations
- Scope handling
- Layer assignment
- Recalculation triggers
**Impact:** N/A - good example to follow.
**Recommendation:** Use this as template for other ability tests.
**Effort:** N/A

#### INFO: Damage Calculator Tests Are Comprehensive
**ID:** TCG-SIM-017
**Location:** `game/simulation/combat/damage_calculator.py` / `tests/unit/simulation/combat/test_damage_calculator.py`
**Issue:** Not an issue - positive example. Tests cover:
- All armor types (emissive, crystalline)
- Shield absorption
- Layer damage distribution
- Weighted component selection
- Many edge cases and boundary conditions
**Impact:** N/A - excellent test coverage.
**Recommendation:** Use as model for other combat system tests.
**Effort:** N/A

#### MAJOR: Superweapons Ability Tests Missing Activation Logic
**ID:** TCG-SIM-018
**Location:** `game/simulation/components/abilities/superweapons.py` (production) / `tests/unit/simulation/components/abilities/test_superweapons.py` (partial)
**Issue:** Superweapon tests exist but miss:
- Activation cooldown management
- Area-of-effect damage distribution
- Resource consumption on activation
- Target validation for superweapons
- Charge-up mechanics if applicable
**Impact:** Superweapon bugs could cause balance issues or crashes.
**Recommendation:** Add activation and effect tests.
**Effort:** Medium

## Top 5 Priority Issues

1. **TCG-SIM-001 (CRITICAL):** Ship Entity Core Methods - The Ship class is central to the game and lacks direct unit tests for critical methods like `die()`, `update()`, and component management. This is the highest priority gap.

2. **TCG-SIM-002 (CRITICAL):** Propulsion Abilities - Movement is fundamental to gameplay. Four ability classes with zero tests create significant risk.

3. **TCG-SIM-005 (MAJOR):** BattleEngine Tick Edge Cases - Combat tick processing with concurrent events could have subtle bugs that only manifest in complex battles.

4. **TCG-SIM-007 (MAJOR):** BattleService Save/Load - Save corruption during combat would severely impact player experience.

5. **TCG-SIM-006 (MAJOR):** FormulaSystem Evaluation - Formula calculations affect all combat math. Only testing exceptions misses the actual calculation logic.
