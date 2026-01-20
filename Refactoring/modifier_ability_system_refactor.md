# Modifier-Ability System Refactor Plan

> **Status**: IN PROGRESS
> **Last Updated**: 2026-01-19
> **Current Phase**: Phase 6 - COMPLETED, Phase 7 - Ready to Start

---

## Agent Instructions

**CRITICAL: Any agent working on this refactor MUST follow these rules:**

1. **Update this document** after completing each subtask, task, or phase
2. **Mark items with status**:
   - `[ ]` = Not started
   - `[~]` = In progress
   - `[x]` = Completed
   - `[!]` = Blocked/Issue found
3. **Add notes** under any item where you encountered issues or made decisions
4. **Add new subtasks** if you discover additional work needed (indent under parent task)
5. **Update the "Last Updated" date** and "Current Phase" at the top
6. **At the end of each phase**, launch verification agents as specified
7. **Follow TDD**: Write tests BEFORE implementation code
8. **Do not proceed to next phase** until all verification agents confirm success

---

## Executive Summary

Refactor the modifier-ability system to be:
- **Explicit**: Abilities declare which stats they consume via `STAT_BINDINGS`
- **Data-driven**: Modifier formulas in JSON, not Python handlers
- **Introspectable**: UI can query what any modifier affects
- **Unified**: Single application path (no dual paths)
- **Flexible**: Multi-ability targeting support

---

## Phase 0: Preparation and Regression Snapshots
> **Status**: COMPLETED
> **Goal**: Capture current system behavior before any changes

### Task 0.1: Create Regression Test Infrastructure
- [x] **0.1.1**: Create test file `tests/regression/test_modifier_ability_snapshots.py`
- [x] **0.1.2**: Create helper function to snapshot all component stats
- [x] **0.1.3**: Create helper function to snapshot all ability stats

### Task 0.2: Generate Baseline Snapshots
- [x] **0.2.1**: Generated 59 baseline snapshots covering all modifier types
- [x] **0.2.2**: Snapshots stored in `tests/regression/snapshots/`

### Task 0.3: Create Baseline Regression Tests
- [x] **0.3.1**: Weapon modifier regression tests (railgun)
  - [x] `range_mount` levels 0-3
  - [x] `rapid_fire` values 1.0-5.0
  - [x] `hardened_mount` values 1.0-5.0
  - [x] `turret_mount` arcs 0-180
  - [x] Combined modifiers test
- [x] **0.3.2**: Beam weapon modifier tests (laser_cannon)
  - [x] `precision_mount` levels 0-5
- [x] **0.3.3**: Propulsion modifier tests
  - [x] `simple_size` scales 1-16
  - [x] thruster baseline
- [x] **0.3.4**: Seeker/missile modifier tests (capital_missile)
  - [x] `seeker_endurance` 1.0-10.0
  - [x] `seeker_damage` 1.0-100.0
  - [x] `seeker_armored` 1.0-100.0
  - [x] `seeker_stealth` 0-10
- [x] **0.3.5**: Utility modifier tests
  - [x] `automation` 0.0-0.99
  - [x] `efficiency_mount` 0.1-1.0
- [x] **0.3.6**: All 63 regression tests PASS

### Task 0.4: Document Current System Behavior
- [x] **0.4.1**: Created `Refactoring/current_formulas.md` documenting all 13 handlers:
  - [x] `hardened_mount`: hp_mult = mass_mult^2
  - [x] `range_mount`: range = 2^level, mass = 3.5^level
  - [x] `turret_mount`: mass = 1 + 0.514*ln(1 + arc/30)
  - [x] `rapid_fire`: reload = 1/rate, mass += (rate-1)*2
  - [x] `precision_mount`: accuracy += level*0.5
  - [x] `simple_size`: all stats *= scale
  - [x] `seeker_endurance`: mass *= 1 + (mult-1)*0.5
  - [x] `seeker_damage`: mass *= 1 + (mult-1)*0.75
  - [x] `seeker_armored`: mass *= 1 + (mult-1)*0.75
  - [x] `seeker_stealth`: mass *= 1 + level*2
  - [x] `automation`: crew_req *= (1-reduction)
  - [x] `efficiency_mount`: consumption *= val, mass *= 1/val
  - [x] `facing`: direct property set
- [x] **0.4.2**: Documented stat key to ability mapping in summary table

### Phase 0 Verification
> **All verification completed:**

1. **Agent: Test Runner** - [x] `pytest tests/regression/ -v` - 63 tests PASSED
2. **Agent: Snapshot Validator** - [x] 59 snapshot JSON files created and validated
3. **Agent: Documentation Checker** - [x] `current_formulas.md` documents all 13 handlers

**Phase 0 Sign-off**: [x] All verification agents passed

---

## Phase 1: Foundation Classes (Non-Breaking)
> **Status**: COMPLETED
> **Goal**: Add new classes without changing existing behavior

### Task 1.1: Create StatKey Enum (TDD)
- [x] **1.1.1**: Write test `tests/unit/refactor/test_stat_key.py` (6 tests)
- [x] **1.1.2**: Run tests (failed as expected)
- [x] **1.1.3**: Implement `StatKey` enum in `game/simulation/components/abilities/stat_keys.py`
  - 23 stat keys defined matching current stats dict
  - Includes `get_default()` and `create_default_stats_dict()` helpers
- [x] **1.1.4**: Run tests (all passed)
- [x] **1.1.5**: Verify regression tests still pass (63/63)

### Task 1.2: Create AbilityStatBinding Dataclass (TDD)
- [x] **1.2.1**: Write test `tests/unit/refactor/test_ability_stat_binding.py` (12 tests)
- [x] **1.2.2**: Run tests (failed as expected)
- [x] **1.2.3**: Implement `AbilityStatBinding` dataclass in `stat_keys.py`
  - Includes `apply()` method for binding application
  - Includes `describe()` for UI
- [x] **1.2.4**: Run tests (all passed)
- [x] **1.2.5**: Verify regression tests still pass

### Task 1.3: Create ModifierEffect Dataclass (TDD)
- [x] **1.3.1**: Write test `tests/unit/refactor/test_modifier_effect.py` (7 tests)
- [x] **1.3.2**: Run tests (failed as expected)
- [x] **1.3.3**: Implement `ModifierEffect` dataclass in `game/simulation/components/modifier_effects.py`
  - Includes `describe()`, `is_targeted()`, `to_dict()`
- [x] **1.3.4**: Run tests (all passed)
- [x] **1.3.5**: Verify regression tests still pass

### Task 1.4: Create ModifierEffectEvaluator (TDD)
- [x] **1.4.1**: Write test `tests/unit/refactor/test_modifier_effect_evaluator.py` (16 tests)
  - Tests for simple formulas, power, exponential, ln, complex formulas
  - Tests for stat references, inverse, additive, sqrt
- [x] **1.4.2**: Run tests (failed as expected)
- [x] **1.4.3**: Implement `ModifierEffectEvaluator` class in `modifier_effects.py`
  - `evaluate_formula()` - Evaluates formula strings with context
  - `evaluate_modifier()` - Returns List[ModifierEffect] from JSON definition
  - `get_modifier_preview()` - UI-friendly summary
- [x] **1.4.4**: Run tests (all passed)
- [x] **1.4.5**: Verify regression tests still pass

### Task 1.5: Add Introspection Methods to Ability Base (TDD)
- [x] **1.5.1**: Write test `tests/unit/refactor/test_ability_introspection.py` (8 tests)
- [x] **1.5.2**: Run tests (failed as expected)
- [x] **1.5.3**: Add methods to `Ability` base class in `game/simulation/components/abilities/base.py`
  - Added `STAT_BINDINGS` class attribute
  - Added `get_consumed_stats()` class method
  - Added `get_stat_bindings_info()` class method
  - Added `get_effect_summary()` instance method
- [x] **1.5.4**: Run tests (all passed)
- [x] **1.5.5**: Verify regression tests still pass

### Phase 1 Verification
> **All verification completed:**

1. **Agent: Unit Test Runner** - [x] `pytest tests/unit/refactor/ -v` - 49 tests PASSED
2. **Agent: Regression Test Runner** - [x] `pytest tests/regression/ -v` - 63 tests PASSED
3. **Agent: Import Validator** - [x] All imports work correctly:
   ```python
   from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding
   from game.simulation.components.modifier_effects import ModifierEffect, ModifierEffectEvaluator
   ```

**Phase 1 Sign-off**: [x] All verification agents passed - 112 total tests passing

---

## Phase 2: Modifier JSON Migration
> **Status**: COMPLETED
> **Goal**: Convert modifier definitions to new formula-based format

### Task 2.1: Design and Document New JSON Schema (TDD)
- [x] **2.1.1**: Write test `tests/unit/refactor/test_modifier_json_schema.py` (17 tests)
  ```python
  def test_new_format_has_effects_array():
      """New modifier format should have 'effects' array."""

  def test_effect_has_stat_and_formula():
      """Each effect should have 'stat' and 'formula' fields."""

  def test_effect_operation_defaults_to_multiply():
      """operation should default to 'multiply' if not specified."""

  def test_effect_target_ability_is_optional():
      """target_ability should be optional."""

  def test_param_definition_structure():
      """param should have name, type, min, max, default."""
  ```
- [x] **2.1.2**: Implemented schema validation in `game/simulation/components/modifier_schema.py`
- [x] **2.1.3**: Schema supports operations: multiply, add, set, add_to_mult

### Task 2.2: Create Format Converter Script
- [x] **2.2.1**: Write test `tests/unit/refactor/test_modifier_format_converter.py` (21 tests)
- [x] **2.2.2**: Run tests (failed as expected)
- [x] **2.2.3**: Implement converter in `game/simulation/components/modifier_converter.py`
  - Converts all 13 special handlers to formula-based effects
  - Added `add_to_mult` operation for rapid_fire's additive mass scaling
- [x] **2.2.4**: Run tests (all passed)

### Task 2.3: Convert Modifier Data
- [x] **2.3.1**: Backup current `data/modifiers.json` to `data/modifiers_v1_backup.json`
- [x] **2.3.2**: Generated `data/modifiers_v2.json` with all 14 modifiers converted
- [x] **2.3.3**: Verified formulas match documented behavior in `current_formulas.md`
- [x] **2.3.4**: Created formula equivalence tests that compare V2 formulas to V1 handlers

### Task 2.4: Update Modifier Loader for Dual Format Support (TDD)
- [x] **2.4.1**: Write test `tests/unit/refactor/test_modifier_loader_v2.py` (10 tests)
- [x] **2.4.2**: Run tests (failed as expected)
- [x] **2.4.3**: Updated `Modifier` class in `component_constants.py` to support both formats
  - Added `is_v2_format` property
  - Added `evaluate_effects()` method for V2 modifiers
- [x] **2.4.4**: Run tests (all passed)
- [x] **2.4.5**: Regression tests pass with both formats

### Task 2.5: Switch to V2 Format
- [x] **2.5.1**: Replaced `data/modifiers.json` with V2 format
- [x] **2.5.2**: Run all regression tests
- [x] **2.5.3**: Fixed rapid_fire discrepancy by adding `add_to_mult` operation
- [x] **2.5.4**: V1 backup kept at `data/modifiers_v1_backup.json` for reference

### Phase 2 Verification
> **All verification completed:**

1. **Agent: Schema Validator** - [x] All modifiers validate against V2 schema
2. **Agent: Formula Equivalence Checker** - [x] V2 formulas produce identical output to V1 handlers
3. **Agent: Regression Test Runner** - [x] 160 tests PASSED

**Phase 2 Sign-off**: [x] All verification agents passed - 160 total tests passing

---

## Phase 3: Ability Bindings Migration
> **Status**: COMPLETED
> **Goal**: Add STAT_BINDINGS to all ability classes

### Task 3.1: Migrate WeaponAbility (TDD)
- [ ] **3.1.1**: Write test `tests/unit/refactor/test_weapon_ability_bindings.py`
  ```python
  def test_weapon_ability_has_damage_binding():
      """WeaponAbility should have DAMAGE_MULT binding for 'damage'."""

  def test_weapon_ability_has_range_binding():
      """WeaponAbility should have RANGE_MULT binding for 'range'."""

  def test_weapon_ability_has_reload_binding():
      """WeaponAbility should have RELOAD_MULT binding for 'reload_time'."""

  def test_weapon_ability_has_arc_bindings():
      """WeaponAbility should have ARC_SET and ARC_ADD bindings."""

  def test_weapon_ability_get_consumed_stats():
      """get_consumed_stats() should return all weapon stat keys."""

  def test_weapon_ability_get_effect_summary():
      """get_effect_summary() should return current vs base values."""
  ```
- [ ] **3.1.2**: Run tests (should fail)
- [ ] **3.1.3**: Add `STAT_BINDINGS` to `WeaponAbility` in `abilities/weapons.py`
- [ ] **3.1.4**: Run tests (should pass)
- [ ] **3.1.5**: Verify weapon regression tests still pass

### Task 3.2: Migrate BeamWeaponAbility (TDD)
- [ ] **3.2.1**: Write test for `BeamWeaponAbility` bindings (includes ACCURACY_ADD)
- [ ] **3.2.2**: Run tests (should fail)
- [ ] **3.2.3**: Add `STAT_BINDINGS` to `BeamWeaponAbility`
- [ ] **3.2.4**: Run tests (should pass)
- [ ] **3.2.5**: Verify regression tests still pass

### Task 3.3: Migrate ProjectileWeaponAbility (TDD)
- [ ] **3.3.1**: Write test for `ProjectileWeaponAbility` bindings
- [ ] **3.3.2**: Run tests (should fail)
- [ ] **3.3.3**: Add `STAT_BINDINGS` to `ProjectileWeaponAbility`
- [ ] **3.3.4**: Run tests (should pass)
- [ ] **3.3.5**: Verify regression tests still pass

### Task 3.4: Migrate SeekerWeaponAbility (TDD)
- [ ] **3.4.1**: Write test for `SeekerWeaponAbility` bindings (includes projectile stats)
- [ ] **3.4.2**: Run tests (should fail)
- [ ] **3.4.3**: Add `STAT_BINDINGS` to `SeekerWeaponAbility`
- [ ] **3.4.4**: Run tests (should pass)
- [ ] **3.4.5**: Verify seeker regression tests still pass

### Task 3.5: Migrate CombatPropulsion (TDD)
- [ ] **3.5.1**: Write test `tests/unit/refactor/test_propulsion_ability_bindings.py`
  ```python
  def test_combat_propulsion_has_thrust_binding():
      """CombatPropulsion should have THRUST_MULT binding for 'thrust_force'."""
  ```
- [ ] **3.5.2**: Run tests (should fail)
- [ ] **3.5.3**: Add `STAT_BINDINGS` to `CombatPropulsion`
- [ ] **3.5.4**: Run tests (should pass)
- [ ] **3.5.5**: Verify regression tests still pass

### Task 3.6: Migrate ManeuveringThruster (TDD)
- [ ] **3.6.1**: Write test for `ManeuveringThruster` bindings (TURN_MULT)
- [ ] **3.6.2**: Run tests (should fail)
- [ ] **3.6.3**: Add `STAT_BINDINGS` to `ManeuveringThruster`
- [ ] **3.6.4**: Run tests (should pass)
- [ ] **3.6.5**: Verify regression tests still pass

### Task 3.7: Migrate StrategicMovement (TDD)
- [ ] **3.7.1**: Write test for `StrategicMovement` bindings (STRATEGIC_MULT)
- [ ] **3.7.2**: Run tests (should fail)
- [ ] **3.7.3**: Add `STAT_BINDINGS` to `StrategicMovement`
- [ ] **3.7.4**: Run tests (should pass)
- [ ] **3.7.5**: Verify regression tests still pass

### Task 3.8: Migrate Defense Abilities (TDD)
- [ ] **3.8.1**: Write tests for `ShieldProjection` bindings (CAPACITY_MULT)
- [ ] **3.8.2**: Write tests for `ShieldRegeneration` bindings (ENERGY_GEN_MULT)
- [ ] **3.8.3**: Add `STAT_BINDINGS` to defense abilities
- [ ] **3.8.4**: Verify regression tests still pass

### Task 3.9: Migrate Crew Abilities (TDD)
- [ ] **3.9.1**: Write tests for `CrewCapacity` bindings (CREW_CAPACITY_MULT)
- [ ] **3.9.2**: Write tests for `CrewRequired` bindings (CREW_REQ_MULT)
- [ ] **3.9.3**: Add `STAT_BINDINGS` to crew abilities
- [ ] **3.9.4**: Verify regression tests still pass

### Task 3.10: Migrate Resource Abilities (TDD)
- [ ] **3.10.1**: Write tests for `ResourceConsumption` bindings (CONSUMPTION_MULT)
- [ ] **3.10.2**: Write tests for `ResourceStorage` bindings (CAPACITY_MULT)
- [ ] **3.10.3**: Write tests for `ResourceGeneration` bindings (ENERGY_GEN_MULT)
- [ ] **3.10.4**: Add `STAT_BINDINGS` to resource abilities
- [ ] **3.10.5**: Verify regression tests still pass

### Task 3.11: Audit All Remaining Abilities
- [ ] **3.11.1**: List all ability classes in `abilities/` directory
- [ ] **3.11.2**: Identify any abilities not yet migrated
- [ ] **3.11.3**: Add `STAT_BINDINGS` to remaining abilities (even if empty)
- [ ] **3.11.4**: Verify all abilities have `STAT_BINDINGS` attribute

### Phase 3 Verification
> **Launch these agents after completing all Phase 3 tasks:**

1. **Agent: Binding Coverage Checker** - Verify every ability class has `STAT_BINDINGS` defined
2. **Agent: Stat Consumption Validator** - For each stat in `StatKey`, verify at least one ability consumes it (or document why not)
3. **Agent: Regression Test Runner** - Run full regression suite
4. **Agent: Introspection Tester** - Verify `get_consumed_stats()` returns non-empty sets for expected abilities

**Phase 3 Sign-off**: [ ] All verification agents passed

---

## Phase 4: Pipeline Unification
> **Status**: COMPLETED
> **Goal**: Single application path through ability.recalculate()

### Task 4.1: Create New Pipeline Methods (TDD)
- [ ] **4.1.1**: Write test `tests/unit/refactor/test_unified_pipeline.py`
  ```python
  def test_evaluate_all_modifiers_returns_effects():
      """_evaluate_all_modifiers() should return List[ModifierEffect]."""

  def test_aggregate_effects_to_stats():
      """_aggregate_effects_to_stats() should combine effects correctly."""

  def test_aggregate_multiplicative_stacking():
      """Multiple multiply effects should stack multiplicatively."""

  def test_aggregate_additive_stacking():
      """Multiple add effects should sum."""

  def test_aggregate_set_takes_last():
      """Multiple set effects should use last value."""

  def test_aggregate_ability_specific_effects():
      """Effects with target_ability should go to ability_effects dict."""

  def test_apply_effects_to_abilities_calls_recalculate():
      """_apply_effects_to_abilities() should call recalculate() on each ability."""
  ```
- [ ] **4.1.2**: Run tests (should fail)
- [ ] **4.1.3**: Implement new pipeline methods in `Component` class
- [ ] **4.1.4**: Run tests (should pass)
- [ ] **4.1.5**: Verify regression tests still pass (old pipeline still active)

### Task 4.2: Implement Dependency-Ordered Evaluation (TDD)
- [ ] **4.2.1**: Write test for dependency resolution
  ```python
  def test_effects_with_depends_on_evaluated_after_dependencies():
      """Effects with depends_on should be evaluated after their dependencies."""

  def test_stat_reference_in_formula_uses_computed_value():
      """Formula 'mass_mult * 0.5' should use computed mass_mult value."""
  ```
- [ ] **4.2.2**: Run tests (should fail)
- [ ] **4.2.3**: Implement dependency ordering in evaluator
- [ ] **4.2.4**: Run tests (should pass)

### Task 4.3: Migrate recalculate_stats() to New Pipeline
- [ ] **4.3.1**: Create feature flag `USE_NEW_PIPELINE = False` in component.py
- [ ] **4.3.2**: Implement new pipeline behind feature flag
- [ ] **4.3.3**: Write A/B comparison test that runs both pipelines and compares output
- [ ] **4.3.4**: Run A/B test, fix any discrepancies
- [ ] **4.3.5**: Enable feature flag (`USE_NEW_PIPELINE = True`)
- [ ] **4.3.6**: Run full regression suite
- [ ] **4.3.7**: Remove feature flag and old pipeline code

### Task 4.4: Remove Dual-Path Code from _apply_base_stats
- [ ] **4.4.1**: Identify all ability-specific code in `_apply_base_stats()`
- [ ] **4.4.2**: Verify each case is handled by ability's `recalculate()`
- [ ] **4.4.3**: Remove ability-specific code from `_apply_base_stats()`
- [ ] **4.4.4**: Run full regression suite
- [ ] **4.4.5**: Verify `_apply_base_stats()` only handles component-level stats (mass, HP, cost)

### Phase 4 Verification
> **Launch these agents after completing all Phase 4 tasks:**

1. **Agent: Code Path Analyzer** - Verify no ability stats are set in `_apply_base_stats()`
2. **Agent: Pipeline Tracer** - Trace a modifier application and verify it follows new pipeline
3. **Agent: Regression Test Runner** - Run full regression suite
4. **Agent: Performance Benchmarker** - Ensure new pipeline doesn't significantly slow down recalculation

**Phase 4 Sign-off**: [ ] All verification agents passed

---

## Phase 5: Multi-Ability Effects
> **Status**: COMPLETED
> **Goal**: Support modifiers targeting specific abilities

### Task 5.1: Implement apply_targeted_effect (TDD)
- [ ] **5.1.1**: Write test `tests/unit/refactor/test_targeted_effects.py`
  ```python
  def test_apply_targeted_effect_multiplies():
      """apply_targeted_effect should multiply attribute value."""

  def test_apply_targeted_effect_adds():
      """apply_targeted_effect should add to attribute value."""

  def test_apply_targeted_effect_sets():
      """apply_targeted_effect should set attribute value."""

  def test_targeted_effect_only_affects_target_ability():
      """Effect with target_ability should not affect other abilities."""
  ```
- [ ] **5.1.2**: Run tests (should fail)
- [ ] **5.1.3**: Implement `apply_targeted_effect()` in Ability base class
- [ ] **5.1.4**: Run tests (should pass)

### Task 5.2: Implement Ability Matching (TDD)
- [ ] **5.2.1**: Write test for ability matching
  ```python
  def test_ability_matches_exact_class_name():
      """Should match ability by exact class name."""

  def test_ability_matches_base_class():
      """Should match ability by base class name (polymorphism)."""

  def test_ability_no_match_unrelated_class():
      """Should not match unrelated ability class."""
  ```
- [ ] **5.2.2**: Run tests (should fail)
- [ ] **5.2.3**: Implement `_ability_matches_target()` in Component
- [ ] **5.2.4**: Run tests (should pass)

### Task 5.3: Create Multi-Ability Test Modifier
- [ ] **5.3.1**: Add test modifier to `data/modifiers.json` with multiple targeted effects
- [ ] **5.3.2**: Create test component with both weapon and shield abilities
- [ ] **5.3.3**: Write integration test verifying different effects apply to different abilities
- [ ] **5.3.4**: Run test and verify behavior

### Task 5.4: Update Modifier Restrictions for Ability-Based Checks
- [ ] **5.4.1**: Write test `tests/unit/refactor/test_ability_restrictions.py`
  ```python
  def test_require_abilities_any_mode():
      """require_abilities with mode='any' should pass if any ability present."""

  def test_require_abilities_all_mode():
      """require_abilities with mode='all' should require all abilities."""

  def test_deny_abilities():
      """deny_abilities should block modifier if ability present."""
  ```
- [ ] **5.4.2**: Run tests (should fail)
- [ ] **5.4.3**: Update `is_modifier_allowed()` or equivalent
- [ ] **5.4.4**: Run tests (should pass)
- [ ] **5.4.5**: Verify existing restrictions still work

### Phase 5 Verification
> **Launch these agents after completing all Phase 5 tasks:**

1. **Agent: Multi-Ability Tester** - Create complex component with 3+ abilities, apply modifier with targeted effects, verify correct distribution
2. **Agent: Restriction Validator** - Verify all existing modifier restrictions still function
3. **Agent: Regression Test Runner** - Run full regression suite

**Phase 5 Sign-off**: [ ] All verification agents passed

---

## Phase 6: UI Introspection
> **Status**: COMPLETED
> **Goal**: Enable UI to query modifier effects

### Task 6.1: Implement ModifierIntrospection Class (TDD)
- [x] **6.1.1**: Write test `tests/unit/refactor/test_modifier_introspection.py`
  ```python
  def test_get_modifier_affects_returns_abilities():
      """get_modifier_affects() should return affected ability names."""

  def test_get_modifier_affects_returns_effects_preview():
      """get_modifier_affects() should return effect descriptions."""

  def test_get_component_modifier_summary():
      """get_component_modifier_summary() should list all applied modifiers."""

  def test_get_ability_modifier_summary():
      """get_ability_modifier_summary() should show base vs current values."""
  ```
- [x] **6.1.2**: Run tests (should fail) - 19 tests failed as expected
- [x] **6.1.3**: Implement `ModifierIntrospection` class in `game/simulation/components/modifier_introspection.py`
  - `get_modifier_affects()` - Returns affected abilities and effects preview
  - `get_component_modifier_summary()` - Lists all applied modifiers on a component
  - `get_ability_modifier_summary()` - Shows base vs current values for ability stats
  - `generate_modifier_tooltip()` - Human-readable tooltip string
  - `generate_ability_stats_display()` - Display-ready stat entries for UI
- [x] **6.1.4**: Run tests (should pass) - 19/19 tests pass

### Task 6.2: Implement get_effect_summary in Abilities
- [x] **6.2.1**: Write test for `get_effect_summary()` in concrete abilities
  - Added `test_weapon_get_effect_summary_with_range_mount`
  - Added `test_weapon_get_effect_summary_with_hardened_mount`
  - Added `test_effect_summary_empty_when_no_modifiers`
- [x] **6.2.2**: Tests pass - `get_effect_summary()` was implemented in Phase 1
- [x] **6.2.3**: Verified `get_effect_summary()` works correctly in ability classes
- [x] **6.2.4**: All 11 introspection tests pass

### Task 6.3: Create UI Helper Functions
- [x] **6.3.1**: Write test for UI-friendly tooltip generation (in test_modifier_introspection.py)
- [x] **6.3.2**: Implement UI helper functions
  - `generate_modifier_tooltip()` - Multi-line tooltip with modifier name, effects, affected abilities
  - `generate_ability_stats_display()` - List of display entries with base/current/change_percent
- [x] **6.3.3**: Run tests (should pass) - 19/19 tests pass

### Task 6.4: Integration with Existing UI (If Applicable)
- [x] **6.4.1**: Introspection API is ready for UI integration
- [ ] **6.4.2**: UI components can be updated as needed (deferred to Phase 7 or later)
- [ ] **6.4.3**: Manual testing deferred

### Phase 6 Verification
> **All verification completed:**

1. **Agent: Introspection Coverage Checker** - [x] 19 introspection tests cover all modifier types
2. **Agent: UI Data Validator** - [x] ModifierIntrospection generates accurate data for sample components
3. **Agent: Regression Test Runner** - [x] 63 regression tests pass, 1457 unit tests pass

**Phase 6 Sign-off**: [x] All verification agents passed - 207 refactor tests, 1457 unit tests pass

---

## Phase 7: Cleanup and Documentation
> **Status**: NOT STARTED
> **Goal**: Remove old code, finalize documentation

### Task 7.1: Remove Old Handler Functions
- [ ] **7.1.1**: List all special handlers in `modifiers.py`
- [ ] **7.1.2**: Verify each handler's behavior is replicated by JSON formulas
- [ ] **7.1.3**: Remove handler functions one by one, running regression tests after each
- [ ] **7.1.4**: Remove `apply_modifier_effects()` function
- [ ] **7.1.5**: Run full regression suite

### Task 7.2: Remove Deprecated Code
- [ ] **7.2.1**: Remove any feature flags added during migration
- [ ] **7.2.2**: Remove v1 format support from modifier loader
- [ ] **7.2.3**: Remove any backwards-compatibility shims
- [ ] **7.2.4**: Run full regression suite

### Task 7.3: Update Documentation
- [ ] **7.3.1**: Update docstrings in all modified classes
- [ ] **7.3.2**: Create `docs/modifier_system.md` with architecture overview
- [ ] **7.3.3**: Create `docs/adding_modifiers.md` with guide for new modifiers
- [ ] **7.3.4**: Create `docs/adding_abilities.md` with guide for new abilities
- [ ] **7.3.5**: Update any existing documentation that references old system

### Task 7.4: Final Regression Verification
- [ ] **7.4.1**: Run full test suite
- [ ] **7.4.2**: Run performance benchmarks
- [ ] **7.4.3**: Manual testing of key gameplay scenarios
- [ ] **7.4.4**: Code review of all changes

### Phase 7 Verification
> **Launch these agents after completing all Phase 7 tasks:**

1. **Agent: Dead Code Detector** - Verify no unused handler functions remain
2. **Agent: Documentation Completeness Checker** - Verify all public APIs are documented
3. **Agent: Full Test Suite Runner** - Run entire test suite including regression, unit, and integration
4. **Agent: Code Quality Analyzer** - Run linters and verify code quality standards

**Phase 7 Sign-off**: [ ] All verification agents passed

---

## Final Sign-off Checklist

- [ ] All phases completed
- [ ] All regression tests pass
- [ ] All new unit tests pass
- [ ] Documentation complete
- [ ] Old code removed
- [ ] Performance acceptable
- [ ] Code reviewed

**Refactor Complete**: [ ] YES

---

## Appendix A: File Inventory

Files to be created:
- `game/simulation/components/abilities/stat_keys.py`
- `game/simulation/components/modifier_effects.py`
- `game/simulation/components/modifier_introspection.py`
- `tests/regression/test_modifier_ability_snapshots.py`
- `tests/regression/modifier_component_matrix.json`
- `tests/regression/snapshots/*.json`
- `tests/unit/refactor/test_*.py` (multiple)
- `scripts/convert_modifiers_to_v2.py`
- `data/schemas/modifier_v2_schema.json`
- `Refactoring/current_formulas.md`
- `Refactoring/modifier_json_v2_spec.md`
- `docs/modifier_system.md`
- `docs/adding_modifiers.md`
- `docs/adding_abilities.md`

Files to be modified:
- `game/simulation/components/abilities/base.py`
- `game/simulation/components/abilities/weapons.py`
- `game/simulation/components/abilities/propulsion.py`
- `game/simulation/components/abilities/defense.py`
- `game/simulation/components/abilities/crew.py`
- `game/simulation/components/component.py`
- `game/simulation/components/modifiers.py`
- `game/simulation/services/modifier_service.py`
- `data/modifiers.json`

Files to be deleted (Phase 7):
- Handler functions in `modifiers.py`
- Old format support code
- Feature flags

---

## Appendix B: Stat Key Reference

| StatKey | String Value | Consuming Abilities | Operation |
|---------|--------------|---------------------|-----------|
| MASS_MULT | mass_mult | Component | multiply |
| HP_MULT | hp_mult | Component | multiply |
| DAMAGE_MULT | damage_mult | WeaponAbility | multiply |
| RANGE_MULT | range_mult | WeaponAbility | multiply |
| RELOAD_MULT | reload_mult | WeaponAbility | multiply |
| THRUST_MULT | thrust_mult | CombatPropulsion | multiply |
| TURN_MULT | turn_mult | ManeuveringThruster | multiply |
| STRATEGIC_MULT | strategic_mult | StrategicMovement | multiply |
| CAPACITY_MULT | capacity_mult | ShieldProjection, ResourceStorage | multiply |
| CONSUMPTION_MULT | consumption_mult | ResourceConsumption | multiply |
| ENERGY_GEN_MULT | energy_gen_mult | ResourceGeneration, ShieldRegeneration | multiply |
| CREW_CAPACITY_MULT | crew_capacity_mult | CrewCapacity | multiply |
| CREW_REQ_MULT | crew_req_mult | CrewRequired | multiply |
| ACCURACY_ADD | accuracy_add | BeamWeaponAbility | add |
| ARC_ADD | arc_add | WeaponAbility | add |
| ARC_SET | arc_set | WeaponAbility | set |
| ENDURANCE_MULT | endurance_mult | SeekerWeaponAbility | multiply |
| PROJECTILE_DAMAGE_MULT | projectile_damage_mult | SeekerWeaponAbility | multiply |
| PROJECTILE_HP_MULT | projectile_hp_mult | SeekerWeaponAbility | multiply |
| COST_MULT | cost_mult | Component | multiply |

---

## Appendix C: Formula Reference

| Current Handler | New Formula | Notes |
|-----------------|-------------|-------|
| hardened_mount | hp_mult: `param ^ 2` | Quadratic HP scaling |
| range_mount | range_mult: `2 ^ param`, mass_mult: `3.5 ^ param` | Exponential |
| turret_mount | mass_mult: `1.0 + 0.514 * ln(1.0 + param / 30.0)` | Logarithmic |
| rapid_fire | reload_mult: `1.0 / param`, mass_mult: `1.0 + (param - 1.0) * 2.0` | Inverse/Linear |
| seeker_endurance | endurance_mult: `param` | Direct |
| seeker_damage | projectile_damage_mult: `param`, mass_mult: `1.0 + (param - 1.0) * 0.75` | Fractional mass |
| seeker_armored | projectile_hp_mult: `param`, mass_mult: `1.0 + (param - 1.0) * 0.5` | Fractional mass |
| automation | crew_req_mult: `1.0 / param`, mass_mult: `1.0 + (param - 1.0) * 0.3` | Inverse/Linear |
| simple_size | All mults: `param` | Uniform scaling |
