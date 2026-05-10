# Agent 6: Refactor + Builder + Systems + Engine Tests Analysis

## Summary
- Files analyzed: 69/69 (complete)
- Removal candidates found: 4 (files or partial)
- HIGH confidence: 2
- MEDIUM confidence: 5
- LOW confidence: 1

---

## tests/unit/refactor/ Analysis (23 files)

### Overview
All 23 files in this directory were created as part of a large refactoring project (likely PROJ-40 or similar) that introduced:
- StatKey enum and AbilityStatBinding dataclass
- ModifierEffect dataclass and ModifierEffectEvaluator
- STAT_BINDINGS on all ability classes
- V2 modifier JSON schema with formula-based effects
- Pipeline unification (removing duplicate stat application)
- Multi-ability targeted effects
- ModifierIntrospection class

These are NOT "one-time refactoring verification tests." They are the actual TDD tests written as part of building these systems. They test real, current production code and all imports resolve to existing modules. Every test verifies ongoing behavior of the modifier/ability system.

### Assessment: KEEP ALL 23 FILES

The refactor/ directory name is misleading - these are not obsolete refactoring checks but rather the canonical tests for the modifier effect system. They cover:

1. **Core data structures:** StatKey, AbilityStatBinding, ModifierEffect
2. **Formula evaluation:** ModifierEffectEvaluator with edge cases (div/0, overflow, math domain errors)
3. **Ability STAT_BINDINGS:** WeaponAbility, BeamWeaponAbility, ProjectileWeaponAbility, SeekerWeaponAbility, CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump, CrewCapacity, LifeSupportCapacity, CrewRequired, ResourceConsumption, ResourceStorage, ResourceGeneration, ShieldProjection, ShieldRegeneration, VehicleLaunchAbility, defense/marker abilities
4. **Schema validation:** V2 modifier JSON format validation
5. **Integration tests:** Pipeline unification, multi-ability targeting, introspection

**Recommendation:** Consider renaming the directory from `tests/unit/refactor/` to something like `tests/unit/modifiers/` or `tests/unit/simulation/modifier_system/` for clarity. The current name implies these are temporary, but they are permanent tests.

### Potential Issues Found (MEDIUM confidence)

#### 1. Significant overlap between test files
- `test_formula_error_handling.py` and `test_formula_edge_cases.py` both test division by zero with the same formula (`1.0 / param` with param=0). The test in `test_formula_edge_cases.py::TestFormulaDivisionByZero::test_formula_division_by_zero` is a near-duplicate of `test_formula_error_handling.py::TestFormulaErrorHandling::test_division_by_zero_logs_error`.

#### 2. Overlap between formula evaluation tests
- `test_modifier_effect_evaluator.py` tests the same hardened_mount/range_mount formulas as `test_formula_edge_cases.py::TestRealWorldFormulas` and `test_modifier_loader_v2.py::TestModifierFormulaEvaluation`. Three files all test `param ^ 2` with param=2 giving 4, `2 ^ param` with param=2 giving 4, etc.

#### 3. test_seeker_multi_ability.py - Source code inspection test
- `test_seeker_does_not_use_direct_stats_access` uses `inspect.getsource()` to verify implementation details (checking for string patterns in source code). This is brittle and tests implementation rather than behavior.

### Files Confirmed Good (23 total)
- `test_stat_key.py` - Tests StatKey enum (Phase 1 Task 1.1)
- `test_ability_stat_binding.py` - Tests AbilityStatBinding dataclass (Phase 1 Task 1.2)
- `test_modifier_effect.py` - Tests ModifierEffect dataclass (Phase 1 Task 1.3)
- `test_modifier_effect_evaluator.py` - Tests ModifierEffectEvaluator (Phase 1 Task 1.4)
- `test_ability_introspection.py` - Tests Ability base class introspection (Phase 1 Task 1.5)
- `test_modifier_json_schema.py` - Tests V2 modifier JSON schema (Phase 2 Task 2.1)
- `test_modifier_loader_v2.py` - Tests V2 modifier format loading (Phase 2 Task 2.4)
- `test_weapon_ability_bindings.py` - Tests WeaponAbility STAT_BINDINGS (Phase 3 Task 3.1)
- `test_beam_weapon_bindings.py` - Tests BeamWeaponAbility STAT_BINDINGS (Phase 3 Task 3.2)
- `test_projectile_weapon_bindings.py` - Tests ProjectileWeaponAbility STAT_BINDINGS (Phase 3 Task 3.3)
- `test_seeker_weapon_bindings.py` - Tests SeekerWeaponAbility STAT_BINDINGS (Phase 3 Task 3.4)
- `test_propulsion_ability_bindings.py` - Tests propulsion STAT_BINDINGS (Phase 3 Tasks 3.5-3.7)
- `test_crew_resource_bindings.py` - Tests crew/resource ability STAT_BINDINGS (Phase 3 Tasks 3.8-3.10)
- `test_defense_marker_bindings.py` - Tests defense/marker ability STAT_BINDINGS (Phase 3 Task 3.11)
- `test_pipeline_unification.py` - Tests single recalculate path (Phase 4)
- `test_multi_ability_effects.py` - Tests multi-ability targeted effects (Phase 5)
- `test_modifier_introspection.py` - Tests ModifierIntrospection class (Phase 6)
- `test_seeker_multi_ability.py` - Tests SeekerWeaponAbility multi-ability support (Task 8.2)
- `test_formula_error_handling.py` - Tests formula error handling (Task 8.1)
- `test_formula_edge_cases.py` - Tests formula edge cases (Task 9.3)
- `test_formula_validation.py` - Tests formula validation (Task 9.2)
- `test_crew_required_mass_scaling.py` - Tests CrewRequired sqrt-based mass scaling (Task 9.4)
- `test_invalid_operation_handling.py` - Tests invalid operation warnings (Phase 14.1)

---

## tests/unit/builder/ Analysis (25 files + conftest)

### Overview
The builder directory contains tests for the ship builder/workshop UI, covering component drag-and-drop, validation, save/load (ShipIO), MVVM pattern (WorkshopViewModel/WorkshopContext), multi-selection, bulk operations, fleet composition, and formation editing. Most files are well-structured and test real production code.

### Assessment: KEEP 25 FILES, CLEAN UP 2

#### HIGH Confidence Removal Candidates

##### 1. `test_bulk_add.py` - Two empty/stub test methods
- **File:** `tests/unit/builder/test_bulk_add.py`
- **Issue:** Two out of three test methods are empty stubs containing only `pass`:
  - `test_bulk_add_with_limit` (lines 32-58): Has setup code and extensive comments about what it *should* test, but the entire method body ends with `pass`. Comments reveal the author was unsure how the validator works.
  - `test_bulk_performance_mock` (lines 60-63): Completely empty, just `pass`. Comment says "Verify it runs fast enough?" indicating it was a placeholder idea.
- **Recommendation:** Remove the two empty methods. The remaining `test_bulk_add_success` is a legitimate test and should be kept. **Alternatively**, implement the `test_bulk_add_with_limit` test since the setup code is already there - it just needs to call the method and assert results.
- **Confidence:** HIGH

##### 2. `test_ship_loading.py` - Empty test class
- **File:** `tests/unit/builder/test_ship_loading.py`
- **Issue:** `TestShipExpectedStats` class (line 77-79) is completely empty - just `class TestShipExpectedStats: pass`. It has a docstring ("Test that loaded ships match their expected_stats") but zero test methods.
- **Context:** The file also contains `TestModifierStacking` (4 real tests, all legitimate) and `TestAllShipDesigns` (1 real test, legitimate). Only the empty class needs removal.
- **Recommendation:** Remove the empty `TestShipExpectedStats` class. Its intended purpose is already covered by `TestAllShipDesigns::test_all_ships_match_expected_stats` in the same file, which loads all ship designs and validates their expected_stats.
- **Confidence:** HIGH

### Files Confirmed Good (25 total)
- `conftest.py` - Imports common test fixtures
- `test_formation_editor_logic.py` - Tests FormationCore from tools/formation_editor (standalone tool tests)
- `test_builder_interaction.py` - Tests InteractionController drop delegation
- `test_workshop_context_di.py` - Tests WorkshopContext dependency injection (PROJ-38)
- `test_workshop_viewmodel_di.py` - Tests WorkshopViewModel dependency injection (PROJ-38)
- `test_schematic_cache_key.py` - Tests weapon arc cache key behavior
- `test_builder_data_loader.py` - Tests WorkshopDataLoader (renamed from BuilderDataLoader)
- `test_ship_validator_di.py` - Tests ShipValidator dependency injection (PROJ-50)
- `test_ship_loading.py` - Tests modifier stacking and expected_stats (minus empty class)
- `test_multi_selection_logic.py` - Tests multi-selection in builder
- `test_selection_refinements.py` - Tests selection homogeneity
- `test_requirement_abilities.py` - Tests marker ability validation
- `test_builder_io_integration.py` - Tests WorkshopShipIO save/load flows
- `test_fleet_composition.py` - Tests fleet composition and setup screen
- `test_bulk_add.py` - Tests bulk component addition (minus empty methods)
- `test_builder_validation.py` - Tests builder validation rules
- `test_designs.py` - Tests ship design factory functions
- `test_builder_logic.py` - Tests ship validation logic in builder
- `test_builder_viewmodel.py` - Tests BuilderViewModel MVVM pattern
- `test_builder_ui_sync.py` - Tests UI sync with ship state
- `test_builder_drag_drop_real.py` - Tests drag-and-drop with real builder
- `test_builder_improvements.py` - Tests builder improvements
- `test_builder_structure_features.py` - Tests structure list items and features
- `test_builder_warning_logic.py` - Tests warning dialogs for class/type changes
- `test_layer_targeted_actions.py` - Tests BUG-71 fix for layer-targeted actions
- `test_io_interactive.py` - Tests ShipIO interactive save/load

---

## tests/unit/systems/ Analysis (18 files + conftest)

### Overview
The systems directory contains tests for low-level engine systems: spatial grid, physics, collision, formula evaluation, event bus, layer restrictions, logger, persistence (tkinter utils), and application integration. Most files are solid and test real production code.

### Assessment: KEEP 17 FILES, FLAG 1 FOR REMOVAL, FLAG OVERLAPS

#### HIGH Confidence Removal Candidates

##### 1. `test_allowed_layers_removal.py` - Refactoring verification test
- **File:** `tests/unit/systems/test_allowed_layers_removal.py`
- **Issue:** This is a classic one-time refactoring verification test. The file docstring explicitly states: "Test to catch regressions in the layer restriction refactor. Specifically tests that: 1. Components no longer have the deprecated `allowed_layers` attribute."
- **Analysis:** The `TestAllowedLayersRemoval` class (5 tests) checks that `allowed_layers` was removed from Component. This was a one-time migration. The attribute will never re-appear because the code that created it has been deleted. These tests add no ongoing value.
- **However:** The `TestBuilderDropValidation` class (3 tests) in the same file tests that the centralized validator handles component placement correctly. These tests *do* have ongoing value - they verify that weapons are blocked in CORE layer and armor is allowed in ARMOR layer via `vehiclelayers.json` rules.
- **Recommendation:** Remove the `TestAllowedLayersRemoval` class (5 tests). Keep the `TestBuilderDropValidation` class (3 tests) but consider moving it to `tests/unit/builder/test_builder_validation.py` since it tests builder validation behavior.
- **Confidence:** HIGH

#### MEDIUM Confidence Issues

##### 2. `test_spatial.py` and `test_spatial_extended.py` - Significant test overlap
- **Files:** `tests/unit/systems/test_spatial.py` and `tests/unit/systems/test_spatial_extended.py`
- **Issue:** Both files define their own `MockObject` class, their own `pygame_init` fixture, and have overlapping test classes:
  - Both have `TestSpatialGridBasics` testing grid initialization, insert, and clear
  - `test_spatial.py::test_grid_initialization` is functionally identical to `test_spatial_extended.py::test_grid_initialization` (both create SpatialGrid(cell_size=1000) and assert cell_size and empty buckets)
  - `test_spatial.py::test_clear_empties_grid` is functionally identical to `test_spatial_extended.py::test_clear_removes_all`
  - `test_spatial.py::test_insert_single_object` overlaps with `test_spatial_extended.py::test_insert_creates_bucket` (both test that inserting creates a bucket entry)
  - Both have `TestSpatialGridQueries` testing query_radius finding nearby objects and ignoring distant ones
- **Recommendation:** Consolidate into a single file. The `test_spatial_extended.py` file adds `TestSpatialGridCellAssignment` and `TestSpatialGridQueryRadius` classes which test unique scenarios (same-cell grouping, cross-cell queries, negative coordinates). Merge the unique tests from `test_spatial_extended.py` into `test_spatial.py` and delete `test_spatial_extended.py`.
- **Confidence:** MEDIUM

##### 3. `test_collision_system.py` overlaps with engine/collision_edge_cases/test_beam_ramming.py
- **Files:** `tests/unit/systems/test_collision_system.py` and `tests/unit/engine/collision_edge_cases/test_beam_ramming.py`
- **Issue:** Both files test CollisionSystem beam raycasting and ramming with significant overlap:
  - Zero direction vector: `test_collision_system.py::test_beam_weapon_zero_direction_vector` vs `test_beam_ramming.py::test_beam_zero_length_direction`
  - Dead target: `test_collision_system.py::test_beam_weapon_dead_target` vs `test_beam_ramming.py::test_beam_dead_target_no_hit`
  - No target: `test_collision_system.py::test_beam_weapon_no_target` vs `test_beam_ramming.py::test_beam_no_target`
  - Origin inside target: `test_collision_system.py::test_beam_weapon_origin_inside_target` vs `test_beam_ramming.py::test_beam_target_at_origin`
  - Non-kamikaze ramming: `test_collision_system.py::test_ramming_non_kamikaze_ship` vs `test_beam_ramming.py::test_ramming_non_kamikaze_ignored`
  - No target ramming: `test_collision_system.py::test_ramming_no_current_target` vs `test_beam_ramming.py::test_ramming_no_target_ignored`
  - Mutual destruction: `test_collision_system.py::test_ramming_mutual_destruction` vs `test_beam_ramming.py::test_ramming_equal_hp_mutual_destruction`
- **Analysis:** The engine/collision_edge_cases/ directory appears to be the newer, more comprehensive version. `test_beam_ramming.py` additionally includes ray-sphere geometry verification tests (TestBeamRaycastingGeometry), hit chance tests, missing HP attribute handling, and integration tests with real Ship objects.
- **Recommendation:** Consolidate by moving any unique tests from `test_collision_system.py` (tangent hit, target behind origin, range limits, no-logger ramming) into `test_beam_ramming.py`, then delete `test_collision_system.py`.
- **Confidence:** MEDIUM

##### 4. `test_main_integration.py` - Very minimal smoke test
- **File:** `tests/unit/systems/test_main_integration.py`
- **Issue:** Contains only 2 tests: `test_import_main` (wraps import in try/except) and `test_game_instantiation` (creates Game instance). The `test_import_main` test catches ImportError but swallows all other exceptions with a print statement, making it a very weak test. The `test_game_instantiation` test actually verifies meaningful things (engine and logger existence, BATTLE_LOG removal).
- **Recommendation:** Keep `test_game_instantiation` but consider strengthening `test_import_main` to not swallow non-import exceptions. This is a low-priority issue.
- **Confidence:** LOW

##### 5. `test_persistence.py` - Misleading name
- **File:** `tests/unit/systems/test_persistence.py`
- **Issue:** File is named `test_persistence.py` but actually tests `tkinter_utils` (specifically `get_tk_root` failure logging). The docstring notes the migration: "PROJ-113: ShipIO moved from game.simulation.systems.persistence to game.ui.services.ship_io."
- **Recommendation:** Rename to `test_tkinter_utils.py` or move to `tests/unit/ui/services/` for clarity. The test itself is valid and should be kept.
- **Confidence:** MEDIUM

### Files Confirmed Good (18 total)
- `conftest.py` - Imports common test fixtures
- `test_spatial.py` - Tests SpatialGrid basics and queries (has overlap, keep as primary)
- `test_spatial_extended.py` - Extended SpatialGrid tests (has overlap, consolidate into test_spatial.py)
- `test_spatial_edge_cases.py` - Tests SpatialGrid query edge cases (unique tests)
- `test_formula_system.py` - Tests formula evaluation security sandbox (important security tests)
- `test_formula_overflow_underflow.py` - Tests formula overflow/underflow/NaN (thorough, 33 tests)
- `test_event_bus.py` - Tests EventBus subscribe/emit/unsubscribe
- `test_dynamic_layers.py` - Tests dynamic layer configuration per ship class
- `test_mount_validation.py` - Tests MountDependencyRule
- `test_layer_restrictions_refactor.py` - Tests LayerRestrictionDefinitionRule
- `test_layer_refinements.py` - Tests layer mass limits
- `test_logger_system.py` - Tests Logger singleton
- `test_physics.py` - Tests PhysicsBody basics
- `test_physics_edge_cases.py` - Tests PhysicsBody edge cases
- `test_collision_system.py` - Tests CollisionSystem (has overlap with engine dir)
- `test_persistence.py` - Tests tkinter utils init logging (misleading name)
- `test_main_integration.py` - Smoke tests for application import/instantiation
- `test_allowed_layers_removal.py` - Partially removable (keep TestBuilderDropValidation)
- `test_arcade_movement.py` - Tests arcade movement with real Ship

---

## tests/unit/engine/ Analysis (3 test files + conftest + __init__)

### Overview
The engine directory contains `collision_edge_cases/` subdirectory with comprehensive tests for the collision system: continuous collision detection (CCD), damage tracking/shot counting, beam raycasting geometry, and ramming edge cases. These are well-organized with shared fixtures in conftest.py.

### Assessment: KEEP ALL 5 FILES

All three test files are well-structured, thorough, and test real production code:

1. **test_ccd.py** (13 tests) - Tests high-velocity collision detection (anti-tunneling), zero/near-zero relative velocity, near-miss scenarios, CCD time clamping, and team/state filtering. No issues found.

2. **test_damage_tracking.py** (4 tests) - Tests damage calculation with source weapon formulas, base damage fallback, and shot hit tracking with accumulation. No issues found.

3. **test_beam_ramming.py** (18 tests) - Tests beam raycasting edge cases (zero direction, target at origin, dead target, no target, hit chance zero), ray-sphere geometry verification with distance calculations, ramming edge cases (non-kamikaze, no target, dead target, equal HP, zero radius, missing HP attribute), and integration tests with real Ship objects. Particularly thorough.

#### MEDIUM Confidence Issues

##### 1. Overlap with `tests/unit/systems/test_collision_system.py`
- **Issue:** As noted in the systems analysis above, there is significant overlap between `test_beam_ramming.py` and `tests/unit/systems/test_collision_system.py`. At least 7 test scenarios are duplicated.
- **Recommendation:** The engine/collision_edge_cases/ directory is the more comprehensive and better-organized version. Consolidate unique tests from `test_collision_system.py` into this directory and remove the systems file.
- **Confidence:** MEDIUM

### Files Confirmed Good (5 total)
- `__init__.py` - Empty package init
- `conftest.py` - Shared fixtures (projectile_manager, collision_system, mock_grid, mock_target_ship, mock_projectile)
- `test_ccd.py` - CCD and projectile collision tests (13 tests)
- `test_damage_tracking.py` - Damage calculation and shot tracking (4 tests)
- `test_beam_ramming.py` - Beam raycasting and ramming edge cases (18 tests)

---

## Cross-Directory Issues

### 1. Collision System Test Duplication (MEDIUM confidence)
Tests for `CollisionSystem` exist in two locations:
- `tests/unit/systems/test_collision_system.py` - 13 tests (beam raycasting + ramming)
- `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` - 18 tests (beam raycasting + ramming + geometry + integration)

At least 7 test scenarios are functionally duplicated. The engine directory version is more comprehensive and better organized. **Recommendation:** Consolidate into the engine directory.

### 2. Spatial Grid Test Duplication (MEDIUM confidence)
Tests for `SpatialGrid` exist in three files:
- `tests/unit/systems/test_spatial.py` - 9 tests (basics + queries)
- `tests/unit/systems/test_spatial_extended.py` - 9 tests (basics + queries + cell assignment + cross-cell)
- `tests/unit/systems/test_spatial_edge_cases.py` - Additional edge case tests

At least 3 test scenarios are functionally duplicated between `test_spatial.py` and `test_spatial_extended.py`. **Recommendation:** Consolidate the first two files into one.

---

## Actionable Summary

### Remove (HIGH confidence)
| File | What to Remove | Tests Removed |
|------|---------------|---------------|
| `tests/unit/builder/test_bulk_add.py` | Two empty `pass` methods: `test_bulk_add_with_limit`, `test_bulk_performance_mock` | 2 stubs |
| `tests/unit/builder/test_ship_loading.py` | Empty `TestShipExpectedStats` class | 0 (class had no tests) |
| `tests/unit/systems/test_allowed_layers_removal.py` | `TestAllowedLayersRemoval` class (5 tests). Keep `TestBuilderDropValidation` (3 tests) | 5 |

### Consolidate (MEDIUM confidence)
| Source File | Target File | Reason |
|-------------|-------------|--------|
| `tests/unit/systems/test_spatial_extended.py` | `tests/unit/systems/test_spatial.py` | Merge unique tests, delete duplicates |
| `tests/unit/systems/test_collision_system.py` | `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` | Merge unique tests, delete duplicates |

### Rename/Move (MEDIUM confidence)
| File | Recommended Action |
|------|-------------------|
| `tests/unit/refactor/` directory | Rename to `tests/unit/modifiers/` - current name implies temporary tests |
| `tests/unit/systems/test_persistence.py` | Rename to `test_tkinter_utils.py` or move to `tests/unit/ui/services/` |
| `tests/unit/systems/test_allowed_layers_removal.py` `TestBuilderDropValidation` | Move to `tests/unit/builder/test_builder_validation.py` |

### Clean Up (MEDIUM confidence)
| File | Issue |
|------|-------|
| `tests/unit/refactor/test_formula_error_handling.py` + `test_formula_edge_cases.py` | Deduplicate division-by-zero tests |
| `tests/unit/refactor/test_modifier_effect_evaluator.py` + `test_formula_edge_cases.py` + `test_modifier_loader_v2.py` | Triple-tested formula evaluations (param^2, 2^param) |
| `tests/unit/refactor/test_seeker_multi_ability.py` | Replace `inspect.getsource()` test with behavior-based test |
