# Test Coverage Gaps Sweep: Simulation

## Summary
- **Shard:** Simulation (`game/simulation/`)
- **Production Files Scanned:** 72
- **Test Files Cross-Referenced:** 57 unit + 32 simulation_tests + 0 integration
- **Total Issues Found:** 18
- **Critical:** 4 | **Major:** 6 | **Minor:** 8 | **Info:** 0

## Findings

#### CRITICAL: Registry Loader Service Completely Untested
**ID:** TCG-SIM-001
**Location:** `game/simulation/services/registry_loader.py`
**Issue:** Registry loader function that reloads all registry data from disk has ZERO test coverage. Critical path for loading components, modifiers, and vehicle classes. Used by BuilderScreen and other systems.
**Impact:** Breaking changes to registry loading logic could silently corrupt saved designs, component databases, or vehicle class definitions. No safeguard against file corruption scenarios.
**Recommendation:** Create comprehensive tests covering: successful reload, missing files, corrupted JSON, registry freeze state checks, and state verification after reload.
**Effort:** Medium

#### CRITICAL: Physics Constants Untested
**ID:** TCG-SIM-002
**Location:** `game/simulation/physics_constants.py`
**Issue:** Physics constants (K_SPEED, K_THRUST, K_TURN) define critical formulas for speed/acceleration/turn calculations. Pure constants with no tests.
**Impact:** Any regression or accidental change to these values would silently break ship physics throughout the game. The constants are used in multiple critical paths (ship_stats, ship_physics_mixin).
**Recommendation:** Create parametrized tests that verify physics formulas work correctly with the defined constants. Test inverse mass scaling behavior, unit conversions, and edge cases (mass=0, very large values).
**Effort:** Simple

#### CRITICAL: Battle Configuration Untested
**ID:** TCG-SIM-003
**Location:** `game/simulation/battle_config.py`
**Issue:** BattleConfig and BattleMode enum define battle setup contracts used by BattleController. Configuration is used for mode routing and feature flags but has zero tests.
**Impact:** Configuration serialization/deserialization bugs, invalid mode transitions, or flag logic errors would affect all battle types (manual, test, strategy, hypothetical).
**Recommendation:** Create tests for: dataclass initialization with defaults, all enum modes, configuration validation, boundary values (max_ticks), and feature flag combinations.
**Effort:** Simple

#### CRITICAL: Component Status/Modifier Constants Untested
**ID:** TCG-SIM-004
**Location:** `game/simulation/components/component_constants.py`
**Issue:** ComponentStatus enum and Modifier/ApplicationModifier classes handle critical state tracking and modifier definition loading. No tests for enums, Modifier.create_modifier(), or ApplicationModifier initialization.
**Impact:** Component damage tracking (DAMAGED, NO_CREW, NO_FUEL, NO_AMMO states) has no verification. Modifier value bounds checking (min_val, max_val) not validated. Could allow out-of-range modifier values to be applied.
**Recommendation:** Create tests for: ComponentStatus enum values, Modifier initialization with various JSON formats, create_modifier() factory, evaluate_effects() method, value clamping (min/max bounds).
**Effort:** Simple

#### MAJOR: Modifier Schema Validation Untested
**ID:** TCG-SIM-005
**Location:** `game/simulation/components/modifier_schema.py`
**Issue:** V2 format validation functions (is_v2_format, validate_effect_v2, validate_param_v2, normalize_effect_v2) have no unit tests. Critical for ensuring modifier JSON conforms to schema.
**Impact:** Invalid modifiers could be loaded silently (wrong effect format, missing required fields). UI introspection systems depend on schema assumptions. Phase migration from V1→V2 could have missed edge cases.
**Recommendation:** Create tests for: V1 vs V2 format detection, missing required fields, invalid stat keys, formula syntax validation, parameter bounds, restriction rules validation.
**Effort:** Medium

#### MAJOR: Modifier Effects Evaluation Untested
**ID:** TCG-SIM-006
**Location:** `game/simulation/components/modifier_effects.py`
**Issue:** ModifierEffect dataclass and ModifierEffectEvaluator.evaluate_modifier() method implement core stat modification logic with no unit tests. Formula evaluation and effect targeting not tested.
**Impact:** Modifiers could fail to apply correctly, formula evaluation errors might not be caught, ability-specific targeting could be broken. ModifierEffect.describe() UI output untested.
**Recommendation:** Create tests for: formula evaluation with various operations (multiply, add, set), parameter substitution, error cases (FormulaException), ability-specific targeting, UI description accuracy.
**Effort:** Medium

#### MAJOR: Marker Abilities Untested
**ID:** TCG-SIM-007
**Location:** `game/simulation/components/abilities/markers.py`
**Issue:** VehicleLaunchAbility, CommandAndControl, RequiresCommandAndControl, RequiresCombatMovement, StructuralIntegrity classes have zero test coverage. These are used for critical ship system dependencies.
**Impact:** VehicleLaunchAbility capacity calculations could be wrong. Marker validation logic (RequiresXxx checks) could fail to prevent invalid ships. UI display (get_ui_rows) untested.
**Recommendation:** Create tests for: VehicleLaunchAbility fighter launch mechanics (try_launch cooldown), capacity multiplication, all marker abilities initialization and UI text.
**Effort:** Simple

#### MAJOR: Stat Keys and Ability Bindings Untested
**ID:** TCG-SIM-008
**Location:** `game/simulation/components/abilities/stat_keys.py`
**Issue:** StatKey enum and AbilityStatBinding class define modifier-ability contracts with no tests. The apply() method implements stat application logic without unit tests.
**Impact:** Modifier stat application could fail silently. Default values (get_default) might be wrong. AbilityStatBinding.apply() operation logic (multiply/add/set) untested. UI description format untested.
**Recommendation:** Create tests for: all StatKey enum values, get_default() for multiplicative/additive/set stats, AbilityStatBinding.apply() with each operation, base attribute resolution, description format.
**Effort:** Simple

#### MAJOR: Modifier Application Logic Untested
**ID:** TCG-SIM-009
**Location:** `game/simulation/components/modifiers.py`
**Issue:** _apply_effect_to_dict() and apply_modifier_effects() functions implement core modifier logic with no unit tests. V1 handlers were removed but V2 logic not verified.
**Impact:** Modifiers could apply incorrect values (wrong operation types), stats could be corrupted, multiplicative stacking could break. Operation 'multiply'/'add'/'set' logic untested.
**Recommendation:** Create tests for: apply_effect_to_dict with each operation (multiply/add/set), initial state (key exists vs doesn't exist), apply_modifier_effects() with various modifier definitions, error handling.
**Effort:** Simple

#### MINOR: Marker Ability UI Output Not Tested
**ID:** TCG-SIM-010
**Location:** `game/simulation/components/abilities/markers.py:38-41`
**Issue:** get_ui_rows() methods in marker abilities format UI display strings but output format is never verified.
**Impact:** UI could display incorrect/malformed text for hangar capacity, cycle time, command status. No regression protection for UI changes.
**Recommendation:** Add tests validating get_ui_rows() return format and content accuracy.
**Effort:** Simple

#### MINOR: Component Health Manager Edge Cases
**ID:** TCG-SIM-011
**Location:** `game/simulation/components/component_health_manager.py`
**Issue:** While tests exist, edge cases around zero HP, over-healing, and state transitions may not be fully covered.
**Impact:** Component health state could become inconsistent (negative HP, status not updated). Damage threshold detection (>50% for DAMAGED) not verified.
**Recommendation:** Review existing tests for coverage of: zero HP state, healing past max, status transitions, damage threshold calculation edge cases.
**Effort:** Simple

#### MINOR: Resource Manager Edge Cases
**ID:** TCG-SIM-012
**Location:** `game/simulation/systems/resource_manager.py`
**Issue:** Fuel/ammo/energy consumption and generation has tests, but edge cases around max values, min values, and overflow may not be comprehensive.
**Impact:** Resource values could exceed max or go negative. Consumption order (which resource consumed first) not verified.
**Recommendation:** Add parametrized tests for resource limits, simultaneous consumption/generation, resource priority ordering.
**Effort:** Simple

#### MINOR: Ability Aggregator Layer Scope Not Fully Tested
**ID:** TCG-SIM-013
**Location:** `game/simulation/entities/ability_aggregator.py`
**Issue:** While layer scope basics are tested, BOTH layer handling and scope filtering edge cases may not be comprehensive.
**Impact:** Abilities might apply in wrong game layers (COMBAT vs STRATEGIC). Scope filtering (SECTOR, SYSTEM, PLANET) logic untested.
**Recommendation:** Create comprehensive scope/layer combination tests covering all AbilityScope × AbilityLayer permutations.
**Effort:** Simple

#### MINOR: Combat Endurance Calculation Verification
**ID:** TCG-SIM-014
**Location:** `game/simulation/entities/combat_endurance.py`
**Issue:** Endurance calculations exist but may not verify all resource consumption patterns and stacking scenarios.
**Impact:** Endurance estimates could be wrong, affecting AI decisions and UI predictions. Crew vs power vs fuel consumption order not verified.
**Recommendation:** Create scenario-based tests: crew shortage impacts endurance, power shortage, fuel shortage, simultaneous shortages.
**Effort:** Simple

#### MINOR: Hit/Miss Resolution Integration
**ID:** TCG-SIM-015
**Location:** `game/simulation/combat/targeting_system.py` + `game/simulation/combat/damage_calculator.py`
**Issue:** Individual components tested in isolation but integration (targeting → hit/miss → damage) may have gaps.
**Impact:** Hit calculations could use wrong defense values. Accuracy penalties not applied correctly. Range calculations might be off.
**Recommendation:** Add integration tests for: targeting with various defense setups, accuracy formula edge cases, range boundary conditions.
**Effort:** Medium

#### MINOR: Ship Formation Positioning
**ID:** TCG-SIM-016
**Location:** `game/simulation/entities/ship_formation.py`
**Issue:** Formation positioning tests may not cover all edge cases (0 ships, 1 ship, very large formations).
**Impact:** Formation offsets could be incorrect for unusual formation sizes, causing poor AI positioning.
**Recommendation:** Add boundary tests: empty formation, single ship, maximum formation size, scattered positions.
**Effort:** Simple

#### MINOR: Projectile Physics Integration
**ID:** TCG-SIM-017
**Location:** `game/simulation/entities/projectile.py` + `game/simulation/projectile_manager.py`
**Issue:** Projectile creation and update tested separately; collision math (continuous collision detection) integration not fully verified.
**Impact:** Projectiles could miss ships due to CCD math errors. Fast-moving projectiles could phase through targets.
**Recommendation:** Add parametrized tests for projectile speeds (slow/normal/very fast), target velocities, edge collision cases.
**Effort:** Medium

#### MINOR: Ship Stats Calculator Phase Ordering
**ID:** TCG-SIM-018
**Location:** `game/simulation/entities/ship_stats.py:68-90`
**Issue:** Five-phase calculation has interdependencies; tests may not verify correct phase ordering and state between phases.
**Impact:** Crew deactivation (phase 2) might happen before crew is counted (phase 1), breaking ship validity. Phase 4 calculations could use stale values.
**Recommendation:** Add tests that verify: phase 1 resets state correctly, phase 2 crew checks work with phase 1 values, phase 3 uses only active components, phase 4 applies physics with phase 3 results, phase 5 uses final mass.
**Effort:** Medium

## Top 5 Priority Issues

1. **TCG-SIM-001** - Registry Loader Service Completely Untested (CRITICAL)
   - Risk: Silently broken game startup, corrupted designs
   - Effort: Medium
   - Blocks: All systems that use registry reload

2. **TCG-SIM-004** - Component Status/Modifier Constants Untested (CRITICAL)
   - Risk: Component damage state tracking could fail
   - Effort: Simple
   - Blocks: Combat simulation accuracy

3. **TCG-SIM-002** - Physics Constants Untested (CRITICAL)
   - Risk: Silent ship physics regression
   - Effort: Simple
   - Blocks: All movement calculations

4. **TCG-SIM-003** - Battle Configuration Untested (CRITICAL)
   - Risk: Configuration bugs affect all battle modes
   - Effort: Simple
   - Blocks: Battle controller initialization

5. **TCG-SIM-005** - Modifier Schema Validation Untested (MAJOR)
   - Risk: Invalid modifiers loaded silently
   - Effort: Medium
   - Blocks: Modifier system correctness
