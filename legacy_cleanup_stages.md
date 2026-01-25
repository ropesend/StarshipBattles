# Starship Battles - Legacy Code Cleanup Stages

**Created:** 2026-01-25
**Purpose:** Reorganization of legacy_code_audit.md into logical cleanup stages
**Source:** legacy_code_audit.md (comprehensive audit report)

---

## Overview

This document reorganizes all legacy code findings into logical stages. Each stage is designed to:
1. Be completable as a unit
2. Not break work done in previous stages
3. Group related changes together
4. Allow tests to pass between stages

**Total Stages: 12**

---

## STAGE 1: DELETE MARKED FILES AND DIRECTORIES

**Goal:** Remove files already explicitly marked for deletion.

**Risk Level:** Very Low - these are already flagged as safe to delete

### 1.1 Debugging Directory
Delete entire directory: `Debugging/Marked_for_Deletion_2026-01-20/`
| File | Size |
|------|------|
| `inspect_bug_08.py` | 2155 bytes |
| `repro_stats_fix.py` | 1104 bytes |
| `reproduce_logistics.py` | 537 bytes |
| `reproduce_rendering.py` | 616 bytes |
| `test_import_debug.py` | 815 bytes |
| `test_validation_final.py` | 2215 bytes |

### 1.2 Marked for Deletion Directory
Delete entire directory: `Marked_For_Deletion_2026-01-21_07-33/`
| File | Size |
|------|------|
| `test_hightick_debug.py` | 2661 bytes |
| `test_registry_check.py` | 623 bytes |
| `test_tost.py` | 3481 bytes |
| `test_updated_beams.py` | 3188 bytes |
| `verify_ui.py` | 4927 bytes |

### 1.3 Log Files in Root
| File | Size |
|------|------|
| `battle.log` | 420KB |
| `combat_lab.log` | 109KB |
| `collect_log.txt` | 72KB |
| `collect_log_2.txt` | 308KB |
| `crash_log.txt` | 1.7KB |

### 1.4 Test Artifacts
| Directory/File |
|----------------|
| `MagicMock/mock.context.savegame_path/` (Mock design JSON files) |

**Verification:** Run tests after deletion to confirm nothing depended on these files.

---

## STAGE 2: REMOVE DEBUG AND TEMPORARY TOOLS

**Goal:** Clean up debug scripts and obsolete tools from Tools/ directory.

**Risk Level:** Low - these are standalone scripts

### 2.1 Debug Scripts (Safe to Delete)
| File | Purpose |
|------|---------|
| `Tools/debug_automation.py` | Modifier loading test |
| `Tools/debug_devastator.py` | Ship config test |
| `Tools/debug_patch.py` | Mock patching test |
| `Tools/debug_test.py` | Fuel tank clamping |
| `Tools/debug_test_clamping.py` | ResourceRegistry clamping |
| `Tools/debug_ui_import.py` | UI import validation |
| `Tools/reproduce_missile_issue.py` | Missile targeting reproduction |
| `Tools/reproduce_mock_error.py` | Mock pattern validation |
| `Tools/reproduce_seeker.py` | Seeker range calculation |

### 2.2 Visual Test Scripts (Safe to Delete)
| File | Purpose |
|------|---------|
| `Tools/visual_test_beam_weapon.py` | Interactive beam weapon test |
| `Tools/visual_test_sprites.py` | Sprite rendering test |

### 2.3 Superseded/Obsolete Scripts
| File | Status |
|------|--------|
| `Tools/fix_modifiers.py` | Superseded by v2 |
| `Tools/cleanup_pygame.py` | One-time executed |
| `Tools/update_paths.py` | No-op template |

### 2.4 Migration Tools (Review Before Deletion)
These were used for past migrations. Verify migrations are complete before deleting:
| File | Purpose |
|------|---------|
| `Tools/migrate_data.py` | Legacy resource cost migration |
| `Tools/migrate_legacy_components.py` | Phase 6 weapon migration |
| `Tools/refactor_phase2.py` | Core module imports |
| `Tools/refactor_phase3.py` | Additional imports |
| `Tools/refactor_phase4.py` | AI module imports |
| `Tools/refactor_components.py` | Remove 'allowed_layers' |
| `Tools/refactor_fix_json_paths.py` | Fix JSON paths |
| `Tools/refactor_fix_mocks.py` | Update mock paths |
| `Tools/fix_modifiers_v2.py` | Modifier fixes |

**Verification:** Confirm no scripts reference these files.

---

## STAGE 3: REMOVE COMMENTED AND DEAD CODE

**Goal:** Clean up commented-out code blocks, unused imports, and dead code.

**Risk Level:** Low - code is already non-functional

### 3.1 Commented Test Methods
| File | Line | Code |
|------|------|------|
| `simulation_tests/tests/test_example_scenarios.py` | 93 | `# def test_beam_mid_range(self):` |
| `simulation_tests/tests/test_example_scenarios.py` | 97 | `# def test_beam_max_range(self):` |
| `tests/unit/combat/test_pdc.py` | 130-131 | Commented debug print statements |
| `tests/repro_issues/test_bug_09_endurance.py` | 72 | Commented out assertion |

### 3.2 Commented Production Code
| File | Line | Pattern |
|------|------|---------|
| `game/core/logger.py` | 38 | `# ch = logging.StreamHandler(sys.stdout)` |
| `game/core/profiling.py` | 108 | `# logger.debug(f"Profiled {name}...")` |
| `game/simulation/components/component.py` | 31-32 | `# allowed_layers removed in refactor` |
| `game/simulation/entities/ship_physics.py` | 3 | Phase 3 removal comment |
| `game/simulation/entities/ship_physics.py` | 25-38 | Commented physics questions |
| `game/simulation/entities/projectile.py` | 108-114 | Commented alternative calculations |
| `game/simulation/systems/battle_engine.py` | 158 | `# Removed Derelict Warning` |
| `game/ui/screens/workshop_screen.py` | 274, 321 | Commented panel update calls |
| `Tools/process_planet_images.py` | 28-32 | Commented nested loops |

### 3.3 Deprecated Method to Delete
| File | Lines | Method | Note |
|------|-------|--------|------|
| `ui/test_lab_scene.py` | 3657-3741 | `_draw_seed_controls_OLD()` | 85 lines marked as deprecated reference |

### 3.4 Inline Debug Imports to Remove
| File | Lines | Pattern |
|------|-------|---------|
| `ui/test_lab_scene.py` | 1941-1942 | `import traceback; traceback.print_exc()` |
| `ui/test_lab_scene.py` | 2167-2168 | Same pattern |
| `ui/test_lab_scene.py` | 2585-2586 | Same pattern |
| `ui/test_lab_scene.py` | 2718-2719 | Same pattern |

**Verification:** Run full test suite after each file edit.

---

## STAGE 4: REMOVE DEPRECATED SHIM FILES

**Goal:** Update all imports to use new module names, then delete shim files.

**Risk Level:** Medium - requires updating import statements across codebase

### 4.1 Builder → Workshop Shims

**Step A:** Find all imports of these deprecated modules:
- `game/ui/screens/builder_screen.py`
- `game/ui/screens/builder_viewmodel.py`
- `game/ui/screens/builder_data_loader.py`
- `game/ui/screens/builder_event_router.py`

**Step B:** Update imports to use workshop equivalents:
| Old Import | New Import |
|------------|------------|
| `BuilderSceneGUI` | `DesignWorkshopGUI` |
| `BuilderViewModel` | `WorkshopViewModel` |
| `BuilderDataLoader` | `WorkshopDataLoader` |
| `BuilderEventRouter` | `WorkshopEventRouter` |

**Step C:** Delete shim files:
| File | Lines |
|------|-------|
| `game/ui/screens/builder_screen.py` | Entire file (wrapper class) |
| `game/ui/screens/builder_viewmodel.py` | Entire file (re-export only) |
| `game/ui/screens/builder_data_loader.py` | Entire file (re-export only) |
| `game/ui/screens/builder_event_router.py` | Entire file (re-export only) |

### 4.2 ShipBuilderService → VehicleDesignService Shim

**Step A:** Find all imports of `ShipBuilderService`

**Step B:** Update to use `VehicleDesignService`:
| Old Import | New Import |
|------------|------------|
| `ShipBuilderService` | `VehicleDesignService` |
| `ShipBuilderResult` | `DesignResult` |

**Step C:** Delete shim file:
| File |
|------|
| `game/simulation/services/ship_builder_service.py` |

**Verification:** Run tests after each step. All imports must resolve correctly.

---

## STAGE 5: REMOVE DEPRECATED FUNCTIONS AND METHODS

**Goal:** Remove functions marked as deprecated, update callers to use new methods.

**Risk Level:** Medium - requires finding and updating all call sites

### 5.1 Deprecated Functions with DeprecationWarning
| File | Lines | Function | Replacement |
|------|-------|----------|-------------|
| `game/strategy/engine/turn_engine.py` | 225-236 | `_execute_move_step()` | Use direct implementation |
| `game/ai/strategy_manager.py` | 155 | `load_combat_strategies()` | StrategyManager lazy loading |

### 5.2 Deprecated Methods Kept for Compatibility
| File | Lines | Method | Note |
|------|-------|--------|------|
| `game/strategy/engine/turn_engine.py` | 167-169 | `_spawn_complex` | Kept for backward compatibility |
| `game/strategy/engine/turn_engine.py` | 175-177 | `_spawn_ship` | Kept for backward compatibility |
| `game/strategy/engine/turn_engine.py` | 214-215 | `_calculate_next_hex` | Kept for backward compatibility |

### 5.3 Re-exported Functions (via game/ai/controller.py)
First update callers to import directly, then remove re-exports:
| Re-exported From | Functions |
|------------------|-----------|
| `game/ai/strategy_manager` | `StrategyManager`, `load_combat_strategies`, `get_strategy_names`, `reset_strategy_manager` |
| `game/ai/target_evaluator` | `TargetEvaluator` |

**Verification:** Search for all usages before removal. Run tests after each change.

---

## STAGE 6: CONSOLIDATE RE-EXPORT PATTERNS

**Goal:** Clean up backward compatibility re-exports, update callers to use canonical imports.

**Risk Level:** Medium - requires systematic import updates

### 6.1 Component Module Re-exports
**File:** `game/simulation/components/component.py` (Lines 8-14)
```python
# Re-export from component_constants for backward compatibility
from .component_constants import (
    ComponentStatus, LayerType, Modifier, ApplicationModifier,
)
```
**Action:** Update all callers to import from `component_constants` directly.

### 6.2 Ship Module Re-exports
**File:** `game/simulation/entities/ship.py` (Lines 20-25)
```python
# Re-export from ship_loader for backward compatibility
from .ship_loader import (
    get_or_create_validator, load_vehicle_classes, initialize_ship_data,
)
```
**Action:** Update all callers to import from `ship_loader` directly.

### 6.3 Controller Re-exports
**File:** `game/ai/controller.py` (Lines 9-18)
- Re-exports from `strategy_manager`
- Re-exports `TargetEvaluator`

**Action:** Update all callers to import from source modules.

### 6.4 Planet Module Re-exports
**File:** `game/strategy/data/planet.py` (Line 7-8)
- Re-exports `PLANET_RESOURCES`

**Action:** Update callers to use `game/core/constants.py` directly.

### 6.5 Constants Module Re-exports
**File:** `game/core/constants.py` (Lines 29-33)
```python
WIDTH = DisplayConfig.DEFAULT_WIDTH
HEIGHT = DisplayConfig.DEFAULT_HEIGHT
```
**Action:** Update callers to use `DisplayConfig` directly.

**Verification:** After each file, run tests and search for remaining usages.

---

## STAGE 7: REMOVE METHOD AND PROPERTY ALIASES

**Goal:** Standardize on canonical method/property names.

**Risk Level:** Medium - requires updating all call sites

### 7.1 Singleton Accessor Aliases
| File | Line | Alias | Target | Action |
|------|------|-------|--------|--------|
| `game/core/screenshot_manager.py` | 46-47 | `get_instance` | `instance` | Update callers, remove alias |
| `game/simulation/ship_theme.py` | 43-44 | `get_instance` | `instance` | Update callers, remove alias |
| `game/ui/renderer/sprites.py` | 46 | `get_instance` | `instance` | Update callers, remove alias |

### 7.2 Fleet Warp Resource Aliases
**File:** `game/strategy/data/fleet.py`
| Line | Alias Method | Target Method | Action |
|------|--------------|---------------|--------|
| 350-360 | `has_energy_for_warp()` | `has_resources_for_warp()` | Update callers, remove alias |
| 392-403 | `consume_warp_energy()` | `consume_warp_resources()` | Update callers, remove alias |

### 7.3 PathSegment Property Alias
**File:** `game/strategy/engine/fleet_movement.py`
| Line | Property | Returns | Action |
|------|----------|---------|--------|
| 43-46 | `hex` | `self.end` | Update callers, remove alias |
| 48-56 | `to_dict()` duplicate key | `'hex': self.end` | Remove duplicate key |
| 307-314 | `project_path_as_dicts()` | wrapper | Update callers, remove wrapper |

### 7.4 Ship Stats Alias
**File:** `game/simulation/entities/ship_stats.py`
| Line | Alias | Target | Action |
|------|-------|--------|--------|
| 337-338 | `to_hit_profile` | `total_defense_score` | Update UI callers, remove alias |

### 7.5 ViewModel Property Alias
**File:** `game/ui/screens/workshop_viewmodel.py`
| Line | Alias | Target | Action |
|------|-------|--------|--------|
| 100-102 | `selected_component` | `primary_selection` | Update callers, remove alias |

**Verification:** Search for all usages of old names. Run tests after each change.

---

## STAGE 8: REMOVE ADAPTER AND WRAPPER CLASSES

**Goal:** Transition from adapter pattern to direct usage where appropriate.

**Risk Level:** High - requires careful refactoring of class hierarchies

### 8.1 ShipControllableAdapter
**File:** `game/ai/interfaces/controllable.py` (Lines 160-316)

**Current Pattern:**
- Wraps Ship to implement IControllable
- Uses `__getattr__`/`__setattr__` for legacy attribute access
- Has `ship` property for backward compatibility

**Transition Steps:**
1. Audit all usages of `ShipControllableAdapter`
2. Update consumers to use IControllable interface methods
3. Remove `__getattr__`/`__setattr__` fallback delegation
4. Remove `ship` property
5. Consider whether adapter is still needed or Ship can implement IControllable directly

### 8.2 BuilderSceneGUI Wrapper
**File:** `game/ui/screens/builder_screen.py` (Lines 47-169)

**Status:** This entire file should be deleted in Stage 4.

### 8.3 ModifierLogic Wrapper
**File:** `ui/builder/modifier_logic.py` (Lines 1-70)

**Current Pattern:**
- Wrapper class delegating to ModifierService
- Exposes `MANDATORY_MODIFIERS` for backward compatibility

**Transition Steps:**
1. Update callers to use `ModifierService` directly
2. Update callers to get `MANDATORY_MODIFIERS` from source
3. Delete wrapper file

### 8.4 _ProfilerProxy
**File:** `game/core/profiling.py` (Lines 133-144)

**Current Pattern:**
- Lazy singleton proxy for `PROFILER` global

**Transition Steps:**
1. Update callers to use `Profiler.instance()` directly
2. Remove proxy class
3. Remove `PROFILER` global or keep as simple reference

### 8.5 ShipCombatMixin Facade
**File:** `game/simulation/entities/ship_combat.py`

**Current Pattern:**
- Mixin acts as pass-through to ShipCombatEngine
- All 8 methods delegate to combat_engine

**Note:** This is part of PROJ-12 (God Class Decomposition). May need to coordinate with that project.

**Verification:** Comprehensive testing after each adapter removal.

---

## STAGE 9: STANDARDIZE LEGACY DATA FORMATS

**Goal:** Migrate to single data format, remove dual-format support code.

**Risk Level:** High - requires data migration and format validation

### 9.1 Fleet Ship Format (String vs ShipInstance)
**File:** `game/strategy/data/fleet.py`
| Lines | Pattern |
|-------|---------|
| 50-54 | Ships can be strings (legacy) or ShipInstance |
| 60 | `List[Union[str, 'ShipInstance']]` |
| 93-96 | Speed recalculation guard for string-only fleets |
| 102 | `get_ship_instances()` filters out strings |
| 557-565 | Legacy string preservation in serialization |

**Migration Steps:**
1. Identify all save games with legacy string format
2. Write migration script to convert strings to ShipInstance
3. Remove Union type, use only ShipInstance
4. Remove filtering logic

### 9.2 Production Queue Format (List vs Dict)
**File:** `game/strategy/engine/production_engine.py` (Lines 57-79)
**File:** `game/strategy/data/planet.py` (Lines 140-153)

| Old Format | New Format |
|------------|------------|
| `["Ship Name", 5]` | `{"design_id": "...", "turns_remaining": 5}` |

**Migration Steps:**
1. Migrate existing production queues in save games
2. Update `add_production()` to only accept dict format
3. Remove dual-format handling

### 9.3 Ship Stats Legacy Fields
**File:** `game/strategy/services/ship_stats_service.py`
| Lines | Legacy Fields |
|-------|---------------|
| 90-98 | `max_fuel`, `max_energy`, `max_ammo` |
| 100-103 | `strategic_fuel_per_hex` |
| 105-111 | `warp_energy_cost`, `warp_fuel_cost` |
| 214-234 | WarpJump `energy_cost`/`fuel_cost` |

**Migration Steps:**
1. Ensure all ship designs use new format
2. Update all test fixtures
3. Remove legacy field extraction
4. Remove re-export of legacy fields

### 9.4 Design Metadata Layer Format
**File:** `game/strategy/data/design_metadata.py`
| Lines | Old Format | New Format |
|-------|------------|------------|
| 163-169 | `{"components": [...]}` | Direct list `[...]` |
| 88-90 | Top-level `mass` | `expected_stats.mass` |

### 9.5 Build Queue Screen Legacy Handling
**File:** `game/ui/screens/build_queue_screen.py`
| Lines | Pattern |
|-------|---------|
| 476-485 | Dual dict/list format handling |
| 702, 760-761, 770 | Format checks |

### 9.6 Tech Tree Requirement Format
**File:** `game/research/data/tech_tree.py` (Lines 64-70)
| Old Format | New Format |
|------------|------------|
| `level: 5` | `level_range: [5, 10]` |

**Verification:** Test with both old and new save games. Verify all migrations complete.

---

## STAGE 10: CONSOLIDATE DUPLICATE CLASSES AND UTILITIES

**Goal:** Remove duplicate implementations, use single canonical version.

**Risk Level:** Medium - requires choosing canonical implementation

### 10.1 ValidationResult Classes (3 implementations)
| File | Fields | Notes |
|------|--------|-------|
| `game/simulation/validation/base.py` | `is_valid`, `errors[]`, `warnings[]` | Full-featured with `merge()` |
| `game/strategy/engine/turn_engine.py` | `is_valid`, `message`, `error_code` | Dataclass - simplified |
| `game/ui/screens/race_validator.py` | `is_valid`, `message` | Minimal dataclass |

**Recommendation:** Use `game/simulation/validation/base.py` as canonical.
**Migration Steps:**
1. Update turn_engine.py to use canonical class
2. Update race_validator.py to use canonical class
3. Remove duplicate definitions

### 10.2 Color Calculation Functions
| File | Function | Thresholds |
|------|----------|------------|
| `game/ui/panels/ship_detail_panel.py` | `get_damage_color()` | >75% Green, 50-75% Yellow, 1-50% Red |
| `game/ui/panels/ship_stats_renderer.py` | `get_hp_bar_color()` | >50% Green, 20-50% Yellow, <20% Red |

**Recommendation:** Create unified utility, decide on threshold behavior.

### 10.3 Modifier Validation Overlap
| File | Function |
|------|----------|
| `game/simulation/components/modifier_schema.py` | `validate_modifier_v2()` |
| `game/simulation/components/modifier_effects.py` | `validate_modifier_definition()` |

**Action:** Determine if these serve different purposes or should be consolidated.

### 10.4 Ability Shortcut Factories
**File:** `game/simulation/components/abilities/__init__.py` (Lines 82-98)
- Lambda factory shortcuts for FuelStorage, EnergyStorage
- `ABILITY_CLASS_MAP` for instance matching

**Action:** Determine if these are still needed post-migration.

**Verification:** Run tests after each consolidation.

---

## STAGE 11: STANDARDIZE CODE PATTERNS

**Goal:** Apply consistent patterns across codebase.

**Risk Level:** Low to Medium - mostly mechanical changes

### 11.1 Singleton Accessor Pattern
**Standard:** Use `instance()` classmethod, remove `get_instance` aliases

Files to update:
- `game/core/screenshot_manager.py`
- `game/simulation/ship_theme.py`
- `game/ui/renderer/sprites.py`
- `game/ui/renderer/game_renderer.py` (uses `get_instance()`)

### 11.2 Property vs get_* Methods
**Issue:** 150+ `get_*` methods vs sparse `@property` usage

**Recommendation:** For simple attribute access, prefer `@property`.

High-frequency files to audit:
- `game/ai/interfaces/controllable.py` (20 methods)
- `game/strategy/data/fleet.py` (15+ methods)
- `game/strategy/data/ship_instance.py` (20+ methods)
- `game/simulation/entities/ship.py` (10+ methods)

### 11.3 String Formatting Consistency
**Files using `.format()` (migrate to f-strings):**
- `game/research/systems/research_service.py`
- `game/ui/panels/ship_detail_panel.py`
- `game/ui/screens/planet_list_filters.py`
- `game/core/logger.py`

### 11.4 ALL_CAPS Instance Properties
**Issue:** Instance properties using ALL_CAPS (not class constants)
| File | Line | Property |
|------|------|----------|
| `game/ui/screens/strategy_scene.py` | 67 | `self.HEX_SIZE = 10` |
| `game/ui/screens/strategy_scene.py` | 68 | `self.DETAIL_ZOOM_LEVEL = 3.0` |
| `game/ui/screens/strategy_fleet_ops.py` | 34 | `@property def HEX_SIZE(self)` |

**Recommendation:** Convert to lowercase or make true class constants.

### 11.5 Exception Types
**Issue:** Using generic `Exception` instead of specific types
| File | Line | Pattern |
|------|------|---------|
| `game/core/logger.py` | 35 | `raise Exception("Profiler is a singleton...")` |
| `game/core/profiling.py` | 35 | Same pattern |
| `game/core/registry.py` | 50 | Same pattern |
| `game/core/screenshot_manager.py` | 27 | Same pattern |

**Recommendation:** Use `RuntimeError` or custom exception class.

### 11.6 Broad Exception Handlers
**Files with `except Exception as e:` catch-alls:**
| File | Lines |
|------|-------|
| `ui/test_lab_scene.py` | 1939, 2165, 2514, 2583, 2715, 2839 |

**Recommendation:** Use specific exception types where possible.

**Verification:** Run tests after pattern standardization.

---

## STAGE 12: CLEAN UP TEST INFRASTRUCTURE

**Goal:** Remove test aliases, obsolete tests, and legacy fixtures.

**Risk Level:** Low - test-only changes

### 12.1 Test Fixture Aliases
| File | Line | Alias | Target |
|------|------|-------|--------|
| `tests/unit/entities/conftest.py` | 24-25 | `basic_ship` | `basic_cruiser_ship` |
| `tests/unit/combat/conftest.py` | 21 | `basic_combat_ship` | `basic_cruiser_ship` |
| `tests/unit/combat/conftest.py` | 22 | `armed_combat_ship` | `armed_ship` |

**Action:** Update tests to use canonical fixture names, remove aliases.

### 12.2 Legacy Test Fields
| File | Lines | Pattern |
|------|-------|---------|
| `tests/unit/strategy/conftest.py` | 117-124 | Legacy fields in fixtures |
| `tests/unit/strategy/conftest.py` | 257-270 | `legacy_string_fleet` fixture |

**Action:** After Stage 9 (data format migration), remove legacy fixtures.

### 12.3 Backward Compatibility Tests
These tests validate legacy behavior. Remove after corresponding features are migrated:
| File | Lines | Test |
|------|-------|------|
| `tests/unit/strategy/test_fleet.py` | 75, 417-418, 640-641, 817-858 | Legacy string ships |
| `tests/unit/strategy/test_turn_engine.py` | 481 | `test_legacy_list_format_supported()` |
| `tests/unit/strategy/test_ship_instance_proj08.py` | 1206-1287 | Legacy fuel/energy methods |
| `tests/integration/test_resource_system.py` | 731, 780 | Mixed legacy and new ships |
| `tests/unit/entities/test_ship_formation.py` | 144, 158 | Legacy formation attributes |
| `tests/unit/entities/test_ship_stats.py` | 192 | `test_ability_values_match_legacy_attributes()` |
| `tests/unit/strategy/test_save_game_migration.py` | 16, 86-99 | V1 save version migration |
| `tests/unit/ai/test_controllable_interface.py` | 467-494 | Adapter backward compatibility |

### 12.4 Obsolete Tests
| File | Lines | Pattern |
|------|-------|---------|
| `tests/unit/combat/test_combat.py` | 151-153 | "Test is obsolete post-Phase 5" |

### 12.5 Skipped Tests
| File | Line | Reason |
|------|------|--------|
| `simulation_tests/tests/test_projectile_weapons.py` | 97 | "Target ship engine configuration issue" |
| `simulation_tests/tests/test_seeker_weapons.py` | 250 | "Requires Point Defense target ships" |

**Action:** Fix or remove skipped tests.

### 12.6 Bug Reproduction Tests
**Directory:** `tests/repro_issues/` (28 files)

**Action:** Review each test. If bug is fixed and regression test is in main suite, delete reproduction test. Otherwise, merge into appropriate test file.

**Verification:** Run full test suite after cleanup.

---

## DEFERRED ITEMS (Address in Future Projects)

These items require larger architectural decisions or are part of active projects:

### D.1 PROJ-12 Related (God Class Decomposition)
- ShipCombatMixin facade pattern
- Formation delegation properties in Ship
- BattleController.engine backward compatibility property

### D.2 Architectural Decisions Needed
- Layer violations (AI importing from Simulation)
- Registry access pattern standardization (Direct vs Service vs Singleton)
- hasattr/getattr defensive patterns (500+ locations - needs interface definition)
- Duck typing with chained hasattr (type discrimination)

### D.3 Magic Numbers
50+ magic numbers need constants. Create constants as part of feature work:
- Resolution breakpoints in `game/app.py`
- Camera zoom values in `game/ui/renderer/camera.py`
- Battle system values in `game/simulation/systems/`
- AI priority scores in `game/ai/target_evaluator.py`

### D.4 TODO/FIXME Items
| File | Line | TODO |
|------|------|------|
| `game/app.py` | 626 | Replace with empire.available_tech |
| `game/simulation/battle_controller.py` | 456 | Override AI retreat navigation |
| `game/simulation/battle_controller.py` | 579 | Restore projectiles |
| `game/simulation/battle_controller.py` | 709 | Fleet ShipInstance integration |
| `game/simulation/systems/battle_engine.py` | 302 | Replace magic number |
| `game/strategy/data/fleet.py` | 670 | Restore orders |

### D.5 Incomplete Implementations
| File | Lines | Method | Status |
|------|-------|--------|--------|
| `game/simulation/battle_controller.py` | 456-457 | AI retreat navigation | Stub with `pass` |
| `game/simulation/battle_controller.py` | 579-580 | Projectile restoration | Not implemented |
| `game/simulation/battle_controller.py` | 667-710 | `apply_results_to_fleet()` | Placeholder |
| `game/simulation/battle_controller.py` | 383-428 | `add_reinforcements()` | Partial |

### D.6 Legacy UI Widgets
**File:** `ui/components.py`
- `Button` class is actively used in `game/app.py` main menu
- `Label` and `Slider` are unused

**Decision Needed:** Migrate main menu to pygame_gui or keep legacy Button.

### D.7 Version/Schema Migration
- Save game versioning system
- Modifier schema V1 → V2 migration
- Disabled `_migrate_temp_designs()` (BUG-29)

---

## STAGE EXECUTION ORDER

Recommended order (each stage should pass all tests before proceeding):

```
STAGE 1  → DELETE MARKED FILES           [Very Low Risk]
STAGE 2  → REMOVE DEBUG TOOLS            [Low Risk]
STAGE 3  → REMOVE DEAD CODE              [Low Risk]
STAGE 4  → REMOVE DEPRECATED SHIMS       [Medium Risk]
STAGE 5  → REMOVE DEPRECATED FUNCTIONS   [Medium Risk]
STAGE 6  → CONSOLIDATE RE-EXPORTS        [Medium Risk]
STAGE 7  → REMOVE ALIASES                [Medium Risk]
STAGE 8  → REMOVE ADAPTERS               [High Risk]
STAGE 9  → STANDARDIZE DATA FORMATS      [High Risk]
STAGE 10 → CONSOLIDATE DUPLICATES        [Medium Risk]
STAGE 11 → STANDARDIZE PATTERNS          [Low-Medium Risk]
STAGE 12 → CLEAN UP TESTS                [Low Risk]
```

---

## VERIFICATION CHECKLIST

After each stage:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches successfully
- [ ] Manual smoke test of affected features
- [ ] Git commit with descriptive message

---

*End of Cleanup Stages Document*
