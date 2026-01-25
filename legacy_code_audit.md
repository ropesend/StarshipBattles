# Starship Battles - Legacy Code Audit Report

**Generated:** 2026-01-25
**Purpose:** Comprehensive identification of aliases, shims, deprecated code, and legacy patterns

---

## Table of Contents
1. [Files Marked for Deletion](#1-files-marked-for-deletion)
2. [Deprecated Shim Files](#2-deprecated-shim-files)
3. [Method/Property Aliases](#3-methodproperty-aliases)
4. [Deprecated Functions](#4-deprecated-functions)
5. [Re-export Patterns](#5-re-export-patterns)
6. [Adapter/Shim Classes](#6-adaptershim-classes)
7. [Legacy Data Format Support](#7-legacy-data-format-support)
8. [Backward Compatibility Tests](#8-backward-compatibility-tests)
9. [Commented/Dead Code](#9-commenteddead-code)
10. [Legacy UI Code](#10-legacy-ui-code)
11. [Architectural Inconsistencies](#11-architectural-inconsistencies)
12. [Hacks and Workarounds](#12-hacks-and-workarounds)

---

## 1. FILES MARKED FOR DELETION

### Directory: `Debugging/Marked_for_Deletion_2026-01-20/`
| File | Size |
|------|------|
| `inspect_bug_08.py` | 2155 bytes |
| `repro_stats_fix.py` | 1104 bytes |
| `reproduce_logistics.py` | 537 bytes |
| `reproduce_rendering.py` | 616 bytes |
| `test_import_debug.py` | 815 bytes |
| `test_validation_final.py` | 2215 bytes |

### Directory: `Marked_For_Deletion_2026-01-21_07-33/`
| File | Size |
|------|------|
| `test_hightick_debug.py` | 2661 bytes |
| `test_registry_check.py` | 623 bytes |
| `test_tost.py` | 3481 bytes |
| `test_updated_beams.py` | 3188 bytes |
| `verify_ui.py` | 4927 bytes |

**Total: 11 files explicitly marked for deletion**

---

## 2. DEPRECATED SHIM FILES

These files exist solely for backward compatibility, re-exporting from new implementations:

### `game/ui/screens/builder_screen.py`
- **Line 2:** `"""DEPRECATED: Use workshop_screen.py instead."""`
- **Lines 33-35:** Import aliases
  ```python
  from game.ui.screens.workshop_event_router import WorkshopEventRouter as BuilderEventRouter
  from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader
  from game.ui.screens.workshop_viewmodel import WorkshopViewModel as BuilderViewModel
  ```
- **Line 169:** Re-exports: `__all__ = ['BuilderSceneGUI', 'BuilderViewModel', 'BuilderEventRouter', 'BuilderDataLoader']`

### `game/ui/screens/builder_viewmodel.py`
- **Line 2:** `"""DEPRECATED: Use workshop_viewmodel.py instead."""`
- **Lines 4-5:**
  ```python
  from game.ui.screens.workshop_viewmodel import WorkshopViewModel as BuilderViewModel
  __all__ = ['BuilderViewModel']
  ```

### `game/ui/screens/builder_data_loader.py`
- **Line 2:** `"""DEPRECATED: Use workshop_data_loader.py instead."""`
- **Lines 4-6:**
  ```python
  from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader, LoadResult
  __all__ = ['BuilderDataLoader', 'LoadResult']
  ```

### `game/ui/screens/builder_event_router.py`
- **Line 2:** `"""DEPRECATED: Use workshop_event_router.py instead."""`
- **Lines 4-5:**
  ```python
  from game.ui.screens.workshop_event_router import WorkshopEventRouter as BuilderEventRouter
  __all__ = ['BuilderEventRouter']
  ```

### `game/simulation/services/ship_builder_service.py`
- **Line 2:** `"""DEPRECATED: Use vehicle_design_service.py instead."""`
- **Lines 4-7:**
  ```python
  from game.simulation.services.vehicle_design_service import (
      VehicleDesignService as ShipBuilderService,
      DesignResult as ShipBuilderResult
  )
  __all__ = ['ShipBuilderService', 'ShipBuilderResult']
  ```

---

## 3. METHOD/PROPERTY ALIASES

### Singleton Accessor Aliases

| File | Line | Alias | Target | Comment |
|------|------|-------|--------|---------|
| `game/core/screenshot_manager.py` | 46-47 | `get_instance` | `instance` | `# Backwards compatibility alias` |
| `game/simulation/ship_theme.py` | 43-44 | `get_instance` | `instance` | `# Backwards compatibility alias` |

### Fleet Warp Resource Aliases

**`game/strategy/data/fleet.py`**

| Line | Alias Method | Target Method | Docstring |
|------|--------------|---------------|-----------|
| 350-360 | `has_energy_for_warp()` | `has_resources_for_warp()` | "This is an alias for has_resources_for_warp() for backward compatibility." |
| 392-403 | `consume_warp_energy()` | `consume_warp_resources()` | "This is an alias for consume_warp_resources() for backward compatibility." |

### PathSegment Property Alias

**`game/strategy/engine/fleet_movement.py`**
| Line | Property | Returns | Docstring |
|------|----------|---------|-----------|
| 43-46 | `hex` | `self.end` | "Alias for end, for backward compatibility." |

### Ship Stats Alias

**`game/simulation/entities/ship_stats.py`**
| Line | Assignment | Comment |
|------|------------|---------|
| 337-338 | `ship.to_hit_profile = ship.total_defense_score` | `# Legacy/Alias for UI until fully refactored` |

### Test Results Alias

**`ui/test_lab_scene.py`**
| Line | Assignment | Comment |
|------|------------|---------|
| 2694 | `scenario.results['ticks'] = tick_count` | `# Alias for consistency with runner` |

---

## 4. DEPRECATED FUNCTIONS

### `game/ai/strategy_manager.py`
| Line | Function | Status |
|------|----------|--------|
| 155 | `load_combat_strategies()` | "NOTE: This function is deprecated. StrategyManager now uses lazy loading." |

### `game/strategy/engine/turn_engine.py`
| Lines | Method | Status |
|-------|--------|--------|
| 225-236 | `_execute_move_step()` | Has `.. deprecated::` docstring, emits `DeprecationWarning` |

### `ui/test_lab_scene.py`
| Line | Method | Status |
|------|--------|--------|
| 3657-3741 | `_draw_seed_controls_OLD()` | "DEPRECATED - Seed controls moved to header. This is kept for reference." |

---

## 5. RE-EXPORT PATTERNS

### `game/simulation/components/component.py`
**Lines 8-14:**
```python
# Re-export from component_constants for backward compatibility
from .component_constants import (
    ComponentStatus,
    LayerType,
    Modifier,
    ApplicationModifier,
)
```

### `game/simulation/entities/ship.py`
**Lines 20-25:**
```python
# Re-export from ship_loader for backward compatibility
from .ship_loader import (
    get_or_create_validator,
    load_vehicle_classes,
    initialize_ship_data,
)
```

### `game/ai/controller.py`
**Lines 9-18:**
```python
# Re-export from strategy_manager for backward compatibility
from game.ai.strategy_manager import (
    StrategyManager,
    load_combat_strategies,
    get_strategy_names,
    reset_strategy_manager,
)

# Re-export TargetEvaluator for backward compatibility
from game.ai.target_evaluator import TargetEvaluator
```

### `game/strategy/data/planet.py`
- Contains comment: `# Re-exported here for backward compatibility`

---

## 6. ADAPTER/SHIM CLASSES

### ShipControllableAdapter

**File:** `game/ai/interfaces/controllable.py`
**Lines:** 160-210

```python
class ShipControllableAdapter(IControllable):
    """
    Adapter that wraps a Ship to implement IControllable.

    This adapter pattern allows the existing Ship class to work with
    the new IControllable interface without modifying Ship directly.
    During the transition period, it also provides backward-compatible
    access to the underlying ship.
    """
```

**Key backward compatibility features:**
| Lines | Feature | Purpose |
|-------|---------|---------|
| 178-181 | `@property ship` | "Access the underlying ship (for backward compatibility)" |
| 183-190 | `__getattr__` | "Fallback attribute access to underlying ship... allows legacy code to access ship attributes during the transition period" |
| 192-197 | `__setattr__` | "Delegate attribute assignment to underlying ship" |

### BuilderSceneGUI Wrapper

**File:** `game/ui/screens/builder_screen.py`
**Lines:** 125-143

```python
def __getattr__(self, name):
    """
    Delegate all attribute access to the wrapped workshop instance.

    This is called only when attribute lookup fails on the instance and class dictionaries.
    """
```

**Pattern:** Wraps `DesignWorkshopGUI` in `_workshop` attribute, delegates all access transparently.

---

## 7. LEGACY DATA FORMAT SUPPORT

### Fleet Legacy Formats

**`game/strategy/data/fleet.py`**

| Lines | Pattern | Description |
|-------|---------|-------------|
| 50, 93-102 | Legacy string ship format | Supports ships as strings instead of ShipInstance objects |
| 565 | Comment | `# Legacy string - keep as is` |
| 725+ | Tests | Tests for mixed legacy and new ship instances |

### Planet Legacy Formats

**`game/strategy/data/planet.py`**

| Lines | Pattern | Description |
|-------|---------|-------------|
| 140-152 | Legacy list format production | `# Legacy: add_production("Colony Ship", 5) -> ["Colony Ship", 5]` |

### Ship Stats Legacy Fields

**`game/strategy/services/ship_stats_service.py`**

| Lines | Pattern | Description |
|-------|---------|-------------|
| 66 | Comment | About legacy fields for backward compatibility |
| 90-105 | Legacy fields | `max_fuel`, `max_energy`, `max_ammo` handling |
| 214-233 | Legacy WarpJump | `energy_cost`/`fuel_cost` support |
| 246 | Comment | About legacy fields for backward compatibility |

### Combat Endurance Legacy

**`game/simulation/entities/combat_endurance.py`**
| Line | Pattern |
|------|---------|
| 68 | `# Fallback to component attribute (Legacy)` |

### Component Migration Tooling

**`Tools/migrate_legacy_components.py`**
| Lines | Purpose |
|-------|---------|
| 4-24 | Script dedicated to migrating legacy weapon attributes into ability dictionaries |

**`Tools/audit_components.py`**
| Lines | Purpose |
|-------|---------|
| 23+ | Audit tracking: `legacy_remaining`, `mismatch`, `missing_ability` |

### Build Queue Legacy Format

**`game/ui/screens/build_queue_screen.py`**
| Lines | Pattern |
|-------|---------|
| 476-482 | `# Handle both dict and legacy list format` |
| 482 | `# Legacy format: ["Ship Name", 5]` |

---

## 8. BACKWARD COMPATIBILITY TESTS

### `game/strategy/data/ship_instance.py`
**Lines 1204-1272:** Test class `TestBackwardCompatibilityLegacyMethods`
- `test_legacy_methods_still_work_get_current_fuel()`
- `test_legacy_methods_still_work_consume_fuel()`
- `test_legacy_methods_still_work_get_current_energy()`
- `test_legacy_methods_still_work_consume_energy()`

### `tests/unit/strategy/test_turn_engine.py`
| Line | Test |
|------|------|
| 481 | `test_legacy_list_format_supported()` |

### `tests/integration/test_resource_system.py`
| Lines | Test Class |
|-------|------------|
| 725-820 | `TestFleetMixedLegacyAndNewShipInstances` |

### `tests/unit/strategy/test_fleet.py`
| Lines | Pattern |
|-------|---------|
| 75, 417-418, 640-641, 845, 857 | Tests for legacy string ships and backward compatibility |

---

## 9. COMMENTED/DEAD CODE

### Commented Test Methods

**`simulation_tests/tests/test_example_scenarios.py`**
| Lines | Code |
|-------|------|
| 93 | `# def test_beam_mid_range(self):` |
| 97 | `# def test_beam_max_range(self):` |

### Commented Logging Setup

**`game/core/logger.py`**
| Line | Code |
|------|------|
| 38 | `# ch = logging.StreamHandler(sys.stdout)` |

### Commented Deprecated Calls

**`Tools/visual_test_sprites.py`**
| Line | Code |
|------|------|
| 35 | `# mgr.load_atlas(atlas_path) # Deprecated` |

**`Tools/visual_test_beam_weapon.py`**
| Line | Comment |
|------|---------|
| 4 | `# Phase 7: Replaced legacy class imports` |

---

## 10. LEGACY UI CODE

### Legacy UI Widgets

**`ui/components.py`**
| Line | Content |
|------|---------|
| 3 | `# --- Legacy UI Widgets ---` |
| 3+ | Old `Button` class and other legacy UI components |

### Legacy Builder Code

**`ui/builder/stats_config.py`**
| Lines | Pattern |
|-------|---------|
| 68-70 | `# Legacy fallback logic from right_panel.py` |
| 355-358 | `# Filter out any hardcoded legacy resource rows if they exist in JSON` with `legacy_keys = ['max_fuel', 'max_energy', 'max_ammo', ...]` |

**`ui/builder/detail_panel.py`**
| Line | Pattern |
|------|---------|
| 197 | `# Skip legacy shims (if they still exist in data)` |

**`ui/builder/layer_panel.py`**
| Line | Pattern |
|------|---------|
| 156 | `# Filter out hull components from OTHER layers (legacy cleanup/safety)` |

---

## 11. ARCHITECTURAL INCONSISTENCIES

### Layer Violations

**`game/ai/target_evaluator.py`**
| Line | Issue |
|------|-------|
| 7 | `from game.simulation.components.component import LayerType` - AI layer imports from Simulation layer |

### Inconsistent String Formatting

**Files using `.format()` style (old):**
- `game/research/systems/research_service.py`
- `game/ui/panels/ship_detail_panel.py`
- `game/ui/screens/planet_list_filters.py`
- `game/core/logger.py`

**Files using f-strings (modern):**
- Most files in `game/simulation/entities/`
- All recent files in `game/simulation/systems/`
- Strategy engine files

### Inconsistent Registry Access Patterns

**Pattern 1: Direct function calls**
- `game/ui/screens/workshop_event_router.py:13` - `get_vehicle_classes()`
- `game/simulation/entities/ship.py:12` - `get_vehicle_classes()`, `get_component_registry()`, `get_modifier_registry()`

**Pattern 2: Service facade**
- `game/simulation/services/data_service.py`
- `game/strategy/services/ship_stats_service.py:18`

**Pattern 3: RegistryManager singleton**
- `game/simulation/services/modifier_service.py:17-20` - `RegistryManager.instance().modifiers`
- `game/ui/screens/builder_screen.py:20`

### Inconsistent Property Access

**Using @property (modern):**
- `game/simulation/entities/ship_combat.py:26-37` - `combat_engine` property

**Using get_* methods (old):**
- `game/simulation/components/component.py` - `get_ability_total()`, `get_primary_value()`
- `game/simulation/entities/ship.py:546-605` - `get_missing_requirements()`, `get_validation_warnings()`, `get_ability_total()`

### Inconsistent Naming Conventions

**ALL_CAPS properties (inconsistent with PEP8):**
| File | Line | Property |
|------|------|----------|
| `game/ui/screens/strategy_renderer.py` | 46 | `HEX_SIZE` |
| `game/ui/screens/strategy_renderer.py` | 58 | `SIDEBAR_WIDTH` |
| `game/ui/screens/strategy_renderer.py` | 62 | `TOP_BAR_HEIGHT` |
| `game/ui/screens/strategy_colonization.py` | 42 | `HEX_SIZE` |
| `game/ui/screens/strategy_fleet_ops.py` | 34 | `HEX_SIZE` |
| `game/ui/screens/strategy_camera_nav.py` | 34 | `HEX_SIZE` |

### Duplicate ValidationResult Classes

| File | Lines | Class |
|------|-------|-------|
| `game/simulation/validation/base.py` | 15-42 | `ValidationResult` (full-featured) |
| `game/strategy/engine/turn_engine.py` | 15-19 | `ValidationResult` (simplified duplicate) |
| `game/simulation/services/battle_service.py` | 18-24 | `BattleResult` (variant) |

### Duplicate Ability Initialization Patterns

**Near-identical `__init__` patterns:**
- `game/simulation/components/abilities/crew.py:14-18` - `CrewCapacity`
- `game/simulation/components/abilities/crew.py:36-40` - `LifeSupportCapacity`
- `game/simulation/components/abilities/resources.py:23-28` - `ResourceConsumption`

---

## 12. HACKS AND WORKAROUNDS

### Code Comments Indicating Hacks

| File | Line | Comment |
|------|------|---------|
| `game/ui/builder/stats_config.py` | 310 | `# Use default arg hack to capture loop variable/list value` |
| `game/ui/screens/planet_list_window.py` | 288 | `# Hack: Store state in button? Or just map it.` |
| `game/ui/screens/battle_scene.py` | 381 | `# Hack to pass state to renderer` |

### Magic Numbers with TODOs

| File | Line | Comment |
|------|------|---------|
| `game/simulation/systems/battle_engine.py` | 302 | `# TODO: Replace magic number with BattleConfig.FIGHTER_LAUNCH_SPEED once added to config` |
| `game/app.py` | 626 | `# TODO: Replace with empire.available_tech or similar` |

---

## SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| Files marked for deletion | 11 |
| Deprecated shim files | 5 |
| Method/property aliases | 7 |
| Deprecated functions | 3 |
| Re-export patterns | 4 files |
| Adapter/shim classes | 2 |
| Legacy data format support locations | 15+ |
| Backward compatibility test classes | 4+ |
| Commented/dead code blocks | 5+ |
| Legacy UI patterns | 4 files |
| Architectural inconsistencies | 6 categories |
| Hacks/workarounds | 5+ |

---

# DETAILED FINDINGS BY AREA

The following sections contain detailed findings from a comprehensive multi-agent review of the entire codebase.

---

## 13. SIMULATION LAYER (`game/simulation/`)

### 13.1 Deprecated Format Migration

#### V1 Modifier Format Deprecation
**File:** `game/simulation/components/modifier_schema.py`
| Line | Pattern |
|------|---------|
| 7 | "V1 format (dict-based effects with 'special' handlers) is no longer supported." |
| 29 | Comment documenting V1 vs V2 format difference |

#### CrystallineArmor Ability (Incomplete)
**File:** `game/simulation/entities/ship_stats.py`
| Line | Pattern |
|------|---------|
| 351 | `ship.crystalline_armor = self._get_ability_total(component_pool, 'CrystallineArmor')` - Ability doesn't exist in registry |

### 13.2 Backward Compatibility Method Aliases

**File:** `game/simulation/ship_theme.py`
| Line | Pattern |
|------|---------|
| 43-44 | `get_instance = instance` - Singleton accessor alias |
| 98-99 | `base_path` parameter deprecated/ignored in favor of ASSET_DIR |

### 13.3 Thin Facade/Shim Layers (PROJ-12)

#### ShipCombatMixin - Facade for ShipCombatEngine
**File:** `game/simulation/entities/ship_combat.py`
| Lines | Pattern |
|-------|---------|
| 1-8 | Header describes maintenance for backward compatibility during PROJ-12 |
| 16-24 | Mixin acts as pass-through wrapper to delegated ShipCombatEngine |
| 39-185 | Every method delegates to self.combat_engine |
| 105-118 | `_find_pdc_target()` - "may be deprecated in future versions" |

#### BattleController.engine Property
**File:** `game/simulation/battle_controller.py`
| Line | Pattern |
|------|---------|
| 617-620 | `engine` property for backward compatibility - service layer now preferred |

#### DataService - Facade Over Registry
**File:** `game/simulation/services/data_service.py`
| Lines | Pattern |
|-------|---------|
| 1-2, 22 | "Facade over data loading operations" |

### 13.4 Property Delegation for Backward Compatibility

**File:** `game/simulation/entities/ship.py`
| Lines | Pattern |
|-------|---------|
| 168-209 | Formation delegation properties (`formation_master`, `formation_offset`, `formation_rotation_mode`, `formation_members`, `formation_active`) all delegate to separate `ShipFormation` class |

### 13.5 Type Migration & Compatibility Support

#### String to Enum Migration
**File:** `game/simulation/systems/battle_engine.py`
| Lines | Pattern |
|-------|---------|
| 252-261 | Normalizes both dict and object attack types, converting string types to Enum |
| 246-271 | Handles both Projectile objects and dict-based attack representations |

#### Multiple Data Type Handling
**File:** `game/simulation/ship_theme.py`
| Lines | Pattern |
|-------|---------|
| 134-138 | Accepts both string and dict formats for image mappings |

### 13.6 Known Issues & Bug Fixes (Tech Debt)

| File | Line | Issue |
|------|------|-------|
| `game/simulation/components/component.py` | 115-128 | Module Identity Drift fallback for isinstance() failure in tests |
| `game/simulation/entities/ability_aggregator.py` | 65-72 | BUG-08: ResourceStorage(fuel) alias to FuelStorage |
| `game/simulation/entities/ship.py` | 417 | BUG-11: Auto-equip default Hull on class change |
| `game/simulation/ship_validator.py` | 141-145 | BUG-12: HullOnly layer restriction handling |

### 13.7 Commented/Removed Code

| File | Line | Pattern |
|------|------|---------|
| `game/simulation/components/component.py` | 31-32 | `# allowed_layers removed in refactor` |
| `game/simulation/entities/ship_physics.py` | 3 | `# Engine, Thruster imports removed - using ability-based checks (Phase 3)` |
| `game/simulation/systems/battle_engine.py` | 158 | `# Removed Derelict Warning` |

### 13.8 TODO/FIXME Incomplete Features

| File | Line | Issue |
|------|------|-------|
| `game/simulation/systems/battle_engine.py` | 302 | Fighter launch speed magic number |
| `game/simulation/battle_controller.py` | 456 | Retreat AI override not implemented |
| `game/simulation/battle_controller.py` | 579 | Projectile restoration not implemented |
| `game/simulation/battle_controller.py` | 709 | Fleet integration placeholder |

### 13.9 Fallback/Legacy Attribute Access

**File:** `game/simulation/entities/combat_endurance.py`
| Line | Pattern |
|------|---------|
| 68-70 | Fallback to component attribute if ability not found |

**File:** `game/simulation/battle_state.py`
Multiple hasattr() checks for optional properties:
- Line 191: `if hasattr(ship, 'resources') and ship.resources:`
- Line 198: `if hasattr(ship, 'current_target') and ship.current_target:`
- Line 211: `if hasattr(ship.velocity, 'x') else (0, 0)`
- Line 295: `if hasattr(ship, 'retreat_status'):`
- Line 382: `if hasattr(proj, 'target') and proj.target:`

### 13.10 Ability Shortcut Factories

**File:** `game/simulation/components/abilities/__init__.py`
| Lines | Pattern |
|-------|---------|
| 82-87 | Shortcut factories for FuelStorage, EnergyStorage (wrap ResourceStorage) |
| 91-98 | Mapping registry for instance matching during refactoring |

---

## 14. STRATEGY LAYER (`game/strategy/`)

### 14.1 Method/Property Aliases

**File:** `game/strategy/data/fleet.py`
| Line | Alias | Target | Docstring |
|------|-------|--------|-----------|
| 350-360 | `has_energy_for_warp()` | `has_resources_for_warp()` | Backward compatibility |
| 392-403 | `consume_warp_energy()` | `consume_warp_resources()` | Backward compatibility |

**File:** `game/strategy/engine/fleet_movement.py`
| Lines | Pattern |
|-------|---------|
| 43-46 | `hex` property alias for `end` |
| 48-56 | `to_dict()` includes duplicate `'hex': self.end` for old code |
| 307-314 | `project_path_as_dicts()` wrapper for backward compatibility |

### 14.2 Shims & Adapter Patterns

**File:** `game/strategy/adapters/simulation_adapter.py`
| Lines | Pattern |
|-------|---------|
| 4-11, 30-36, 38-131 | `SimulationBattleResolver` adapter bridges strategy to simulation layer |

**File:** `game/strategy/data/planet.py`
| Line | Pattern |
|------|---------|
| 7-8 | Re-export of `PLANET_RESOURCES` for backward compatibility |

### 14.3 Deprecated Methods

**File:** `game/strategy/engine/turn_engine.py`
| Lines | Method | Status |
|-------|--------|--------|
| 222-247 | `_execute_move_step()` | DEPRECATED - emits `DeprecationWarning` |
| 164-178 | Delegation methods kept for backward compatibility with tests |

### 14.4 Legacy Data Format Support

#### Fleet Ship Format Migration
**File:** `game/strategy/data/fleet.py`
| Lines | Pattern |
|-------|---------|
| 49-54 | Ships can be strings (legacy) or ShipInstance objects |
| 85-99 | `_trigger_speed_recalculation()` only for ShipInstance objects |
| 101-104 | `get_ship_instances()` filters out legacy strings |

#### Ship Stats Service - Legacy Field Support
**File:** `game/strategy/services/ship_stats_service.py`
| Lines | Pattern |
|-------|---------|
| 66 | Comment about legacy fields |
| 88-130 | Dual field system: new generic + legacy specific (`max_fuel`, `max_energy`, `max_ammo`) |
| 214-234 | Legacy `energy_cost`/`fuel_cost` in WarpJump ability |

#### Production Engine - List/Dict Format
**File:** `game/strategy/engine/production_engine.py`
| Lines | Pattern |
|-------|---------|
| 57-79 | Dual format handling: old `[name, turns]` list vs new dict format |

#### Design Metadata Legacy Fields
**File:** `game/strategy/data/design_metadata.py`
| Lines | Pattern |
|-------|---------|
| 88-90 | Mass location: `expected_stats.mass` or top-level `mass` (legacy) |
| 162-171, 209-215 | Layer format: new list vs old `{"components": [...]}` dict |

#### Planet Construction Queue
**File:** `game/strategy/data/planet.py`
| Lines | Pattern |
|-------|---------|
| 136-153 | `add_production()` supports legacy list and new dict format |

### 14.5 GameSession Legacy Parameters

**File:** `game/strategy/engine/game_session.py`
| Lines | Pattern |
|-------|---------|
| 19-23 | Legacy parameters override config for backward compatibility |
| 53-55 | `player_empire`/`enemy_empire` convenience references |
| 284 | Hardcoded value "per legacy" |

### 14.6 Version/Migration Support

**File:** `game/strategy/systems/save_game_service.py`
| Lines | Pattern |
|-------|---------|
| 25-31 | `MIGRATABLE_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "1.9.0"]` |

### 14.7 Conditional Backward Compat Fields

**File:** `game/strategy/data/empire.py`
| Lines | Pattern |
|-------|---------|
| 89-93 | Optional race fields only included if set |

**File:** `game/strategy/engine/game_config.py`
| Lines | Pattern |
|-------|---------|
| 57-63 | Optional race fields only included if set |

---

## 15. UI LAYER (`game/ui/` and `ui/`)

### 15.1 Backward Compatibility Wrapper Classes

**File:** `game/ui/screens/builder_screen.py`
| Lines | Pattern |
|-------|---------|
| 46-166 | `BuilderSceneGUI` wrapper class delegating to `DesignWorkshopGUI` |
| 65-104 | Proxy properties (`ship`, `template_modifiers`, `selected_components`) |
| 125-143 | `__getattr__` and `__setattr__` for transparent delegation |

**File:** `ui/builder/modifier_logic.py`
| Lines | Pattern |
|-------|---------|
| 1-30 | `ModifierLogic` wrapper delegating to `ModifierService` |
| 14 | `MANDATORY_MODIFIERS` exposed for backward compatibility |

### 15.2 Re-export Shims

| File | Lines | Pattern |
|------|-------|---------|
| `game/ui/screens/builder_viewmodel.py` | 1-8 | Re-exports `WorkshopViewModel` as `BuilderViewModel` |
| `game/ui/screens/builder_data_loader.py` | 1-8 | Re-exports `WorkshopDataLoader` as `BuilderDataLoader` |
| `game/ui/screens/builder_event_router.py` | 1-8 | Re-exports `WorkshopEventRouter` as `BuilderEventRouter` |
| `game/ui/renderer/sprites.py` | 46 | `get_instance = instance` alias |

### 15.3 Property Aliases

**File:** `game/ui/screens/workshop_viewmodel.py`
| Lines | Pattern |
|-------|---------|
| 100-102 | `selected_component` alias for `primary_selection` |

**File:** `game/ui/screens/workshop_screen.py`
| Lines | Pattern |
|-------|---------|
| 355-377 | Proxy properties: `ship`, `selected_components`, `available_components` |

### 15.4 Function Wrappers

**File:** `game/ui/screens/fleet_report_filters.py`
| Lines | Pattern |
|-------|---------|
| 11-29 | `has_warp_capability()` wraps `ShipStatsService.has_warp_capability()` (PROJ-11 migration) |

### 15.5 Removed Features

| File | Line | Pattern |
|------|------|---------|
| `game/ui/screens/builder_screen.py` | 23 | `# PresetManager removed - preset system deprecated` |
| `game/ui/screens/workshop_screen.py` | 512 | Layer panel drawing removed |
| `game/ui/screens/workshop_screen.py` | 526, 668 | Tooltip methods removed |
| `game/ui/screens/workshop_event_router.py` | 431 | Preset deletion removed |

### 15.6 Legacy Data Format Handling

**File:** `game/ui/screens/build_queue_screen.py`
| Lines | Pattern |
|-------|---------|
| 476-485 | Dual dict/list format for construction queue items |
| 702, 760-761, 770 | Multiple checks for dict vs list format |

**File:** `ui/builder/detail_panel.py`
| Lines | Pattern |
|-------|---------|
| 197-199 | Skip legacy shims: `ProjectileWeapon`, `BeamWeapon`, `Armor` |

### 15.7 Legacy Configuration & Fallbacks

**File:** `ui/builder/stats_config.py`
| Lines | Pattern |
|-------|---------|
| 68-70, 78-79, 91-92 | Legacy fallback logic for crew requirements |
| 253-254 | `# Legacy (Mapped to Generics or Keep implementations?)` |
| 357-358 | Filter legacy keys: `['max_fuel', 'max_energy', 'max_ammo', ...]` |

### 15.8 Legacy UI Widgets

**File:** `ui/components.py`
| Lines | Pattern |
|-------|---------|
| 3-102 | Complete legacy UI widget library (`Button`, `Label`, `Slider`) - pre-pygame_gui |

### 15.9 Event Data Format Compatibility

**File:** `game/ui/screens/workshop_event_router.py`
| Lines | Pattern |
|-------|---------|
| 200-206 | Handle new tuple format vs old group_key-only format |
| 223-233 | Fallback layer search for backward compatibility |

### 15.10 Defensive getattr Usage

**File:** `game/ui/panels/ship_stats_renderer.py`
Multiple lines using `getattr(ship, 'attribute', default)` for optional properties:
- Lines 56, 135-136, 149, 175, 307-308, 319, 325, 329, 335

---

## 16. AI & CORE LAYERS (`game/ai/` and `game/core/`)

### 16.1 Re-exports for Backward Compatibility

**File:** `game/ai/controller.py`
| Lines | Pattern |
|-------|---------|
| 9-15 | Re-export from `strategy_manager`: `StrategyManager`, `load_combat_strategies`, `get_strategy_names`, `reset_strategy_manager` |
| 17-18 | Re-export `TargetEvaluator` from `target_evaluator` |

**File:** `game/core/constants.py`
| Lines | Pattern |
|-------|---------|
| 29-33 | `WIDTH = DisplayConfig.DEFAULT_WIDTH`, `HEIGHT = DisplayConfig.DEFAULT_HEIGHT` for backward compatibility |
| 59-60 | `PLANET_RESOURCES` moved from strategy layer to fix dependency |

### 16.2 Deprecated Function

**File:** `game/ai/strategy_manager.py`
| Lines | Pattern |
|-------|---------|
| 151-171 | `load_combat_strategies()` - deprecated, kept for backward compatibility |

### 16.3 Adapter Pattern with Backward Compatibility

**File:** `game/ai/interfaces/controllable.py`
| Lines | Pattern |
|-------|---------|
| 160-196 | `ShipControllableAdapter` - adapter with `__getattr__`/`__setattr__` for legacy attribute access |
| 178-181 | `ship` property for backward compatibility |
| 183-190 | Fallback attribute access during transition period |

### 16.4 Mixed Type Checking (Duplicate Logic)

**File:** `game/ai/controller.py`
| Lines | Pattern |
|-------|---------|
| 72-80, 115-124 | Duplicate missile-checking logic using both string `'missile'` AND enum `AttackType.MISSILE` |

### 16.5 Duplicate Wrapper Methods (Shim Pattern)

**File:** `game/ai/controller.py`
| Lines | Pattern |
|-------|---------|
| 140-154 | `_stat_get_hp_percent`, `_get_hp_percent`, `_stat_is_in_pdc_arc`, `_is_in_pdc_arc` - thin wrappers around `TargetEvaluator` |

### 16.6 Extensive getattr/hasattr Usage

Heavy defensive attribute access throughout:

**File:** `game/ai/behaviors.py`
- Lines 137, 142, 167, 186, 188, 208, 241

**File:** `game/ai/controller.py`
- Lines 47, 65, 77, 98, 107, 120, 193, 205, 246, 277, 306

**File:** `game/ai/target_evaluator.py`
- Lines 70, 77, 85, 89, 112, 116, 131, 136, 170-171

### 16.7 Commented-Out Code

| File | Line | Pattern |
|------|------|---------|
| `game/core/logger.py` | 38 | `# ch = logging.StreamHandler(sys.stdout)` |
| `game/core/profiling.py` | 108 | `# logger.debug(f"Profiled {name}: {duration*1000:.2f}ms")` |

### 16.8 Global Accessor Proxy

**File:** `game/core/profiling.py`
| Lines | Pattern |
|-------|---------|
| 133-144 | `_ProfilerProxy` class - backward compatibility proxy for `PROFILER` global |

### 16.9 Layer Violations

**File:** `game/ai/target_evaluator.py`
| Line | Pattern |
|------|---------|
| 7 | `from game.simulation.components.component import LayerType` - AI imports from Simulation |

---

## 17. TESTS & TOOLS

### 17.1 Test Fixture Aliases

| File | Lines | Pattern |
|------|-------|---------|
| `tests/unit/combat/conftest.py` | 20-22 | `basic_combat_ship = basic_cruiser_ship`, `armed_combat_ship = armed_ship` |
| `tests/unit/entities/conftest.py` | 24 | Alias for backward compatibility with existing tests |
| `tests/unit/strategy/conftest.py` | 257-270 | `legacy_string_fleet()` fixture |

### 17.2 Backward Compatibility Tests

| File | Lines | Test |
|------|-------|------|
| `tests/unit/strategy/test_fleet.py` | 75 | Legacy string ship format |
| `tests/unit/strategy/test_fleet.py` | 417-418, 640-641 | Legacy string ships resource costs |
| `tests/unit/strategy/test_fleet.py` | 817-858 | `test_backward_compat_has_energy_for_warp_wrapper()`, etc. |
| `tests/unit/strategy/test_turn_engine.py` | 481 | `test_legacy_list_format_supported()` |
| `tests/unit/strategy/test_ship_instance_proj08.py` | 1206-1287 | Legacy fuel/energy methods |
| `tests/integration/test_resource_system.py` | 731, 780 | Mixed legacy and new ship instances |
| `tests/unit/entities/test_ship_formation.py` | 144, 158 | Legacy formation attributes |
| `tests/unit/entities/test_ship_stats.py` | 192 | `test_ability_values_match_legacy_attributes()` |
| `tests/unit/strategy/test_save_game_migration.py` | 16, 86-99 | V1 save version migration |
| `tests/unit/ai/test_controllable_interface.py` | 467-494 | `ShipControllableAdapter` backward compatibility |

### 17.3 Obsolete/Deprecated Tests

| File | Lines | Pattern |
|------|-------|---------|
| `tests/unit/combat/test_combat.py` | 151-153 | "Test is obsolete post-Phase 5" |

### 17.4 Commented/Dead Code in Tests

| File | Line | Pattern |
|------|------|---------|
| `tests/repro_issues/test_bug_09_endurance.py` | 72 | Commented out assertion |
| `tests/unit/combat/test_pdc.py` | 130-131 | Commented debug print statements |

### 17.5 Phase-Based Refactoring Comments

Multiple files contain "Phase N" comments documenting refactoring progression:
- `# Phase 7: Removed legacy class imports`
- `# Phase 7: Use ability-based access`
- `# Phase 6 migrated structure`
- `# Phase 5: hull_mass is removed`

### 17.6 Migration Tools

| File | Purpose |
|------|---------|
| `Tools/migrate_data.py` | Migrates legacy component fields to ability dictionaries |
| `Tools/migrate_legacy_components.py` | Comprehensive component refactor migration |
| `Tools/audit_components.py` | Audits components.json for migration consistency |
| `Tools/verify_resources.py` | Validates resource system migration |
| `Tools/refactor_phase2.py` | Module import aliasing |
| `Tools/refactor_phase3.py`, `refactor_phase4.py` | Additional refactoring phases |
| `Tools/fix_modifiers.py`, `fix_modifiers_v2.py` | Modifier handling bug fixes |

### 17.7 Debug/Temporary Files (Candidates for Deletion)

| File | Purpose |
|------|---------|
| `Tools/debug_test.py` | Ad-hoc fuel tank testing |
| `Tools/debug_automation.py` | ModifierLogic automation debug |
| `Tools/debug_devastator.py` | Debugging |
| `Tools/debug_patch.py` | UILabel mocking debug |
| `Tools/debug_test_clamping.py` | Clamping logic debug |
| `Tools/debug_ui_import.py` | UI import issues debug |
| `Tools/visual_test_beam_weapon.py` | Interactive visual test |
| `Tools/visual_test_sprites.py` | Sprite loading visual test |
| `Tools/reproduce_missile_issue.py` | Bug reproduction |
| `Tools/reproduce_mock_error.py` | Mock error reproduction |
| `Tools/reproduce_seeker.py` | Seeker weapon debug |

### 17.8 Bug Reproduction Tests

**Directory:** `tests/repro_issues/` (28 files)
- `test_bug_01_crew_delay.py` through `test_bug_27_ordertype.py`
- Regression tests that could be merged into regular test suites

---

## UPDATED SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| Files marked for deletion | 11 |
| Deprecated shim files | 5 |
| Method/property aliases | 15+ |
| Deprecated functions | 4 |
| Re-export patterns | 10+ files |
| Adapter/shim classes | 5+ |
| Legacy data format support locations | 30+ |
| Backward compatibility test classes | 15+ |
| Commented/dead code blocks | 15+ |
| Legacy UI patterns | 8 files |
| Architectural inconsistencies | 6 categories |
| Hacks/workarounds | 10+ |
| Migration tools | 8 |
| Debug/temporary files | 11+ |
| Bug reproduction tests | 28 |
| getattr/hasattr defensive patterns | 50+ locations |
| TODO/FIXME incomplete features | 10+ |
| Phase-based refactoring markers | 20+ |

---

## 18. RESEARCH LAYER (`game/research/`)

### 18.1 Legacy Data Format Support

**File:** `game/research/data/tech_tree.py`
| Line | Pattern |
|------|---------|
| 64-70 | Backward compatibility shim for requirement definitions - supports both new `level_range` array format and old single `level` integer format |

---

## 19. DATA FILES (`data/`)

### 19.1 Schema Evolution (Modifier Files)

**File:** `data/modifiers_v1_backup.json`
| Location | Pattern |
|----------|---------|
| restrictions | Legacy field names: `deny_types`/`allow_types` instead of `deny_abilities`/`allow_abilities` |
| effects | Legacy structure: direct `special` field instead of structured array with `stat`/`formula` |
| modifier root | Deprecated flattened field structure (`type`, `min_val`, `max_val`, `default_val`) |

**File:** `data/modifiers_v2.json`
| Location | Pattern |
|----------|---------|
| restrictions | Transitional schema: uses new ability names but retains `default` in param |
| effects[].formula | Legacy syntax patterns: `"1.5 ^ param"`, `"sqrt(param)"` instead of standardized operations |

**File:** `data/modifiers.json`
| Location | Pattern |
|----------|---------|
| range_mount/precision_mount | Default value changes from 1 (v2) to 0 (current) - schema migration indicator |

### 19.2 Legacy Documentation Convention

| File | Pattern |
|------|---------|
| `data/combat_strategies.json` | Uses `_comment` field (legacy convention) |
| `data/targeting_policies.json` | Uses `_comment` field (legacy convention) |
| `data/movement_policies.json` | Uses `_comment` field (legacy convention) |

### 19.3 Naming Inconsistency

**File:** `data/components.json`
| Location | Pattern |
|----------|---------|
| component.allowed_vehicle_types | Uses `allowed_vehicle_types` instead of `allowed_types` pattern used in modifiers |

---

## 20. SIMULATION COMPONENTS DEEP AUDIT (`game/simulation/components/`)

### 20.1 Module Identity Drift Fallback

**File:** `game/simulation/components/component.py`
| Line | Pattern |
|------|---------|
| 119-127 | Known issue with isinstance() fallback using `__class__.__name__` MRO traversal for test isolation |
| 31-32 | Commented: `# allowed_layers removed in refactor` |
| 157-167 | `cooldown_timer` property maps abstract interface to concrete ability instance |
| 438 | `getattr(self.ship, 'max_mass_budget', 1000)` uses fallback default |
| 450-507 | Multiple hasattr guards for dynamic property setting |

### 20.2 Weapon Abilities Fallback Patterns

**File:** `game/simulation/components/abilities/weapons.py`
| Line | Pattern |
|------|---------|
| 28-31 | Fallback to component base stats if data is not dict |
| 47-49 | Fallback: `component.data.get('base_range')` |
| 62-64 | Fallback: `component.data.get('base_reload')` |
| 129-147 | Multiple hasattr guards for `_base_*` attributes |
| 224-314 | Extensive getattr with defaults for component attributes |

### 20.3 Base Ability Patterns

**File:** `game/simulation/components/abilities/base.py`
| Line | Pattern |
|------|---------|
| 162-163 | Sentinel pattern: `_NO_DEFAULT = object()` |
| 178-185 | Smart defaults based on key naming convention (`_mult`, `_add` suffixes) |
| 188-281 | Multiple `getattr(self.component, 'ability_stats', {})` patterns |

### 20.4 Modifier Schema Deprecation

**File:** `game/simulation/components/modifier_schema.py`
| Line | Pattern |
|------|---------|
| 29 | "V1 format (deprecated)" in docstring |
| 45-46 | V1 format deprecation comment |

**File:** `game/simulation/components/modifiers.py`
| Line | Pattern |
|------|---------|
| 1-8 | Header: "V1 handler functions were removed in Phase 7 cleanup" |

### 20.5 Resource Abilities

**File:** `game/simulation/components/abilities/resources.py`
| Line | Pattern |
|------|---------|
| 30-40 | `sync_data` supports both dict and primitive formats |

**File:** `game/simulation/components/abilities/propulsion.py`
| Line | Pattern |
|------|---------|
| 16-18 | Primitive shortcut pattern: `"CombatPropulsion": 100` |
| 118-123 | WarpJump primitive shortcut handling |

### 20.6 Ability Registry Shortcuts

**File:** `game/simulation/components/abilities/__init__.py`
| Line | Pattern |
|------|---------|
| 75, 82-87 | Lambda factory shortcuts for backward compatibility |
| 91-98 | `ABILITY_CLASS_MAP` for instance matching during refactoring |

---

## 21. VALIDATION LAYER DUPLICATES

### 21.1 Duplicate ValidationResult Classes

| File | Lines | Fields | Notes |
|------|-------|--------|-------|
| `game/simulation/validation/base.py` | 15-43 | `is_valid`, `errors[]`, `warnings[]` | Full-featured with `merge()` |
| `game/strategy/engine/turn_engine.py` | 15-19 | `is_valid`, `message`, `error_code` | Dataclass - simplified |
| `game/ui/screens/race_validator.py` | 16-25 | `is_valid`, `message` | Dataclass - minimal |

---

## 22. STRATEGY SERVICES LEGACY PATTERNS (`game/strategy/services/`)

### 22.1 Ship Stats Service - Extensive Legacy Support

**File:** `game/strategy/services/ship_stats_service.py`
| Line | Pattern |
|------|---------|
| 66 | Legacy fields documentation |
| 86-130 | Fallback to `expected_stats` for legacy test fixtures |
| 90-98 | Build `resource_storage` from legacy `max_fuel`, `max_energy`, `max_ammo` |
| 100-103 | Build `resource_consumption_per_hex` from legacy `strategic_fuel_per_hex` |
| 105-111 | Build `warp_resource_costs` from legacy `warp_energy_cost`, `warp_fuel_cost` |
| 123-129, 246-252 | Re-export legacy fields for backward compatibility |
| 214-234 | Dual format support for WarpJump ability (old vs new) |
| 292-293 | Dual format: indexed (`bridge_0`) vs base (`bridge`) component IDs |
| 348-354 | Dual format: list vs dict for `layer_components` |
| 442-488 | `has_warp_capability()` relocated facade method |

---

## 23. UI PANELS LEGACY PATTERNS (`game/ui/panels/`)

### 23.1 PROJ-12 Phase 4 Extractions

| File | Lines | Pattern |
|------|-------|---------|
| `race_description_panel.py` | 1-9 | Extracted from RaceSetupScreen god class |
| `race_environment_panel.py` | 1-11 | Extracted from RaceSetupScreen god class |
| `race_flag_gallery.py` | 1-10 | Extracted from RaceSetupScreen god class |
| `race_portrait_gallery.py` | 1-10 | Extracted from RaceSetupScreen god class |
| `race_theme_gallery.py` | 1-10 | Extracted from RaceSetupScreen god class |
| `ship_detail_panel.py` | 1-6 | PROJ-03 Phase 4 wrapper class |

### 23.2 Dynamic Property Aliases

| File | Line | Pattern |
|------|------|---------|
| `race_flag_gallery.py` | 182 | `btn.flag_id = flag_id` - dynamic property on UI object |
| `race_portrait_gallery.py` | 175 | `btn.portrait_id = portrait_id` |
| `race_theme_gallery.py` | 108 | `btn.theme_id = theme_id` |
| `system_tree_panel.py` | 191-293 | `is_group`, `group_key` properties added at runtime |

### 23.3 Bug Workarounds

| File | Line | Pattern |
|------|------|---------|
| `planet_report_panel.py` | 192 | BUG-26: Copy list to avoid mutation during iteration |
| `system_tree_panel.py` | 145 | BUG-26: Copy list to avoid mutation during iteration |

---

## 24. UI RENDERER LEGACY PATTERNS (`game/ui/renderer/`)

### 24.1 Singleton Aliases

**File:** `game/ui/renderer/sprites.py`
| Line | Pattern |
|------|---------|
| 46-47 | `get_instance = instance` - Backwards compatibility alias |
| 52-58 | `reset()` method for testing singleton destruction |
| 74-76 | Fallback to old BMP atlas format |
| 136-140 | Legacy BMP transparency handling comments |

**File:** `game/ui/renderer/game_renderer.py`
| Line | Pattern |
|------|---------|
| 41 | Uses legacy `get_instance()` instead of `instance()` |

---

## 25. UI BUILDER LEGACY PATTERNS (`ui/builder/`)

### 25.1 ModifierLogic Wrapper Class

**File:** `ui/builder/modifier_logic.py`
| Line | Pattern |
|------|---------|
| 2-3, 8, 11 | Wrapper class delegating to ModifierService |
| 14-15 | `MANDATORY_MODIFIERS` exposed for backward compatibility |
| 17-70 | All methods are delegating wrappers |

### 25.2 Stats Config Legacy Handling

**File:** `ui/builder/stats_config.py`
| Line | Pattern |
|------|---------|
| 68-92 | Legacy fallback logic for crew requirements (3 instances) |
| 215-225 | Fallback map with getattr for `potential_*` attributes |
| 253-259 | "Kept for compatibility if JSON not fully migrated yet" |
| 355-358 | Legacy keys filter: `['max_fuel', 'max_energy', 'max_ammo', ...]` |

### 25.3 Detail Panel Legacy Filtering

**File:** `ui/builder/detail_panel.py`
| Line | Pattern |
|------|---------|
| 11-17 | Lazy import pattern to break circular dependencies |
| 86 | `hasattr(selection_data, 'id')` for legacy selection format |
| 197-199 | Skip legacy shims: `ProjectileWeapon`, `BeamWeapon`, `Armor` |

### 25.4 Layer Panel Legacy Cleanup

**File:** `ui/builder/layer_panel.py`
| Line | Pattern |
|------|---------|
| 156-161 | Filter hull components from non-hull layers (legacy cleanup) |

### 25.5 Weapons Panel Defensive Patterns

**File:** `ui/builder/weapons_panel.py`
| Line | Pattern |
|------|---------|
| 232, 261-262, 265, 306-309, 493-505 | Multiple getattr with defaults |
| 265, 309, 505 | `hasattr(ship, 'get_total_sensor_score')` checks |

---

## 26. SIMULATION ENTITIES DEEP AUDIT (`game/simulation/entities/`)

### 26.1 Ship Re-exports

**File:** `game/simulation/entities/ship.py`
| Line | Pattern |
|------|---------|
| 20 | Re-export from ship_loader for backward compatibility |
| 168-214 | Formation delegation properties (7 properties) |

### 26.2 Ship Combat Mixin (PROJ-12 Transition)

**File:** `game/simulation/entities/ship_combat.py`
| Line | Pattern |
|------|---------|
| 2-5 | "Maintained for backward compatibility during PROJ-12 transition" |
| 16-24 | Mixin acts as facade for ShipCombatEngine delegation |
| 39-185 | 8 methods delegate to combat_engine |
| 109-110 | `_find_pdc_target` "may be deprecated in future versions" |

### 26.3 Ship Physics Legacy

**File:** `game/simulation/entities/ship_physics.py`
| Line | Pattern |
|------|---------|
| 3 | `# Engine, Thruster imports removed - using ability-based checks (Phase 3)` |

### 26.4 Ship Stats Alias

**File:** `game/simulation/entities/ship_stats.py`
| Line | Pattern |
|------|---------|
| 337 | `ship.to_hit_profile = ship.total_defense_score` - "Legacy/Alias for UI until fully refactored" |

### 26.5 Combat Endurance Legacy Fallback

**File:** `game/simulation/entities/combat_endurance.py`
| Line | Pattern |
|------|---------|
| 68-70 | "Fallback to component attribute (Legacy)" |

### 26.6 Ability Aggregator Aliasing

**File:** `game/simulation/entities/ability_aggregator.py`
| Line | Pattern |
|------|---------|
| 65-72 | BUG-08 Fix: Alias `ResourceStorage(fuel)` to `FuelStorage` |
| 220-227 | Same aliasing logic repeated |

### 26.7 Projectile Commented Code

**File:** `game/simulation/entities/projectile.py`
| Line | Pattern |
|------|---------|
| 108-114 | Commented alternative calculation methods |
| 138-142 | Complex physics explanation with 5-line comment |

---

## 27. STRATEGY ENGINE DEEP AUDIT (`game/strategy/engine/`)

### 27.1 Turn Engine Backward Compatibility

**File:** `game/strategy/engine/turn_engine.py`
| Line | Pattern |
|------|---------|
| 16-19 | Duplicate ValidationResult dataclass |
| 155 | "PROJ-12 Phase 3: Delegates to ProductionEngine" |
| 167-169 | `_spawn_complex` "kept for backward compatibility" |
| 175-177 | `_spawn_ship` "kept for backward compatibility" |
| 214-215 | `_calculate_next_hex` "kept for backward compatibility" |
| 222-236 | `_execute_move_step()` DEPRECATED with DeprecationWarning |

### 27.2 Game Session Legacy Parameters

**File:** `game/strategy/engine/game_session.py`
| Line | Pattern |
|------|---------|
| 19 | "Allow legacy parameters to override config for backward compatibility" |
| 53-55 | `player_empire`/`enemy_empire` convenience references for backward compatibility |

### 27.3 Fleet Movement Aliases

**File:** `game/strategy/engine/fleet_movement.py`
| Line | Pattern |
|------|---------|
| 44-46 | `hex` property alias for `end` |
| 48-56 | `to_dict()` includes duplicate `'hex': self.end` for old code |
| 309 | `project_path_as_dicts()` wrapper for backward compatibility |

### 27.4 Game Config Optional Fields

**File:** `game/strategy/engine/game_config.py`
| Line | Pattern |
|------|---------|
| 57 | "Only include race fields if set (backwards compatibility)" |

### 27.5 Production Engine Dual Format

**File:** `game/strategy/engine/production_engine.py`
| Line | Pattern |
|------|---------|
| 57-79 | Supports old `[name, turns]` list AND new dict format |

---

## 28. STRATEGY DATA DEEP AUDIT (`game/strategy/data/`)

### 28.1 Fleet Legacy Ship Format

**File:** `game/strategy/data/fleet.py`
| Line | Pattern |
|------|---------|
| 50-53 | Documents both string (legacy) and ShipInstance formats |
| 60 | `ships: List[Union[str, 'ShipInstance']]` |
| 93-96 | Speed recalculation guard for legacy string-only fleets |
| 102 | `get_ship_instances()` filters out legacy strings |
| 354-360 | `has_energy_for_warp()` alias for `has_resources_for_warp()` |
| 396-403 | `consume_warp_energy()` alias for `consume_warp_resources()` |
| 557-565 | Legacy string preservation in serialization |

### 28.2 Planet Legacy Formats

**File:** `game/strategy/data/planet.py`
| Line | Pattern |
|------|---------|
| 7-8 | Re-export `PLANET_RESOURCES` for backward compatibility |
| 115-125 | Handles both list and dict format for layer data |
| 140-153 | `add_production()` supports legacy list AND new dict format |

### 28.3 Design Metadata Legacy Fields

**File:** `game/strategy/data/design_metadata.py`
| Line | Pattern |
|------|---------|
| 88-90 | Mass in `expected_stats` (new) or top-level (legacy) |
| 163-169 | Old format `{"components": [...]}` vs new direct list |
| 210-215 | Same dual format handling |

### 28.4 Empire Optional Fields

**File:** `game/strategy/data/empire.py`
| Line | Pattern |
|------|---------|
| 89-93 | Optional race fields only included if set (backwards compatibility) |

---

## 29. GLOBAL LEGACY KEYWORD SEARCH RESULTS

### 29.1 "backward/backwards" References (60+ locations)

Key files with multiple references:
- `game/ui/screens/builder_screen.py` - 8 references
- `game/strategy/engine/turn_engine.py` - 5 references
- `game/strategy/engine/fleet_movement.py` - 3 references
- `docs/refactoring/workshop_refactoring_plan.md` - 4 references

### 29.2 "legacy" References (100+ locations)

Key files:
- `ui/builder/stats_config.py` - 6 references (legacy_req, legacy_keys)
- `game/strategy/services/ship_stats_service.py` - 8 references
- `game/strategy/data/fleet.py` - 7 references

### 29.3 "deprecated" References (25+ locations)

Key files:
- `game/ui/screens/builder_screen.py` - "preset system deprecated"
- `game/simulation/components/modifier_schema.py` - "V1 format (deprecated)"
- `game/ai/strategy_manager.py` - "This function is deprecated"

### 29.4 "alias" References (40+ locations)

Key files:
- Singleton accessors: `get_instance = instance` in 4 files
- Method aliases in `fleet.py`: 2 warp methods
- Test fixture aliases in conftest files: 4 locations

---

## 30. MIGRATION MARKERS AND PROJECT REFERENCES

### 30.1 Active Projects

| Project | Description | Status |
|---------|-------------|--------|
| PROJ-12 | God Class Decomposition | Active (Phase 8) |
| PROJ-13 | Code Quality & Documentation | Planning |

### 30.2 Phase Markers in Code (20+)

| File | Pattern |
|------|---------|
| `game/simulation/entities/ship_physics.py` | "Phase 3" |
| `game/simulation/components/modifiers.py` | "Phase 7 cleanup" |
| `game/simulation/ship_validator.py` | "Phase 12 refactoring" |

### 30.3 BUG Markers in Code (55 tracked)

Active bugs in code comments:
- BUG-08: Ability aliasing fix
- BUG-11: Hull component auto-equip
- BUG-12: HullOnly restriction
- BUG-19, 22, 23, 24, 25, 26, 27, 29, 45

### 30.4 TODO Markers (6 in source)

| File | Line | TODO |
|------|------|------|
| `game/app.py` | 626 | Replace with empire.available_tech |
| `game/simulation/battle_controller.py` | 456 | Override AI to move toward edge |
| `game/simulation/battle_controller.py` | 579 | Restore projectiles |
| `game/simulation/battle_controller.py` | 709 | Implement Fleet ShipInstance |
| `game/simulation/systems/battle_engine.py` | 302 | Replace magic number |
| `game/strategy/data/fleet.py` | 670 | Restore orders |

---

## 31. RE-EXPORT PATTERNS COMPREHENSIVE LIST

### 31.1 Package `__init__.py` Re-exports (15+ files)

| File | Exports |
|------|---------|
| `game/ui/__init__.py` | sprites, camera, game_renderer, scenes, panels |
| `game/ai/interfaces/__init__.py` | IControllable, ShipControllableAdapter |
| `game/core/__init__.py` | Vector2, clamp, lerp, angle_diff |
| `game/strategy/interfaces/__init__.py` | IBattleResolver, BattleResult |
| `game/strategy/adapters/__init__.py` | SimulationBattleResolver |
| `game/simulation/services/__init__.py` | ModifierService, ShipBuilderService, BattleService, DataService |
| `game/simulation/validation/__init__.py` | ValidationRule, ValidationResult |
| `game/research/data/__init__.py` | TechNode, TechTree, ResearchTracker |
| `game/simulation/components/abilities/__init__.py` | All ability classes (155 lines) |

### 31.2 Deprecated Alias Re-exports (4 files)

| File | Alias | Target |
|------|-------|--------|
| `game/simulation/services/ship_builder_service.py` | ShipBuilderService | VehicleDesignService |
| `game/ui/screens/builder_viewmodel.py` | BuilderViewModel | WorkshopViewModel |
| `game/ui/screens/builder_event_router.py` | BuilderEventRouter | WorkshopEventRouter |
| `game/ui/screens/builder_data_loader.py` | BuilderDataLoader | WorkshopDataLoader |

### 31.3 Controller Re-exports

**File:** `game/ai/controller.py`
| Line | Pattern |
|------|---------|
| 9-15 | Re-exports: StrategyManager, load_combat_strategies, get_strategy_names, reset_strategy_manager |
| 17-18 | Re-exports: TargetEvaluator |

---

## 32. ADAPTER AND WRAPPER PATTERNS

### 32.1 Adapter Classes

**File:** `game/ai/interfaces/controllable.py`
| Class | Lines | Purpose |
|-------|-------|---------|
| ShipControllableAdapter | 160-316 | Wraps Ship to implement IControllable |
| - `__getattr__` | 188 | Fallback delegation to `self._ship` |
| - `__setattr__` | 197 | Intercepts attribute setting |
| - 20 delegation methods | 218-316 | Position, velocity, rotation, etc. |

### 32.2 Wrapper Classes

**File:** `game/ui/screens/builder_screen.py`
| Class | Lines | Purpose |
|-------|-------|---------|
| BuilderSceneGUI | 47-169 | DEPRECATED wrapper for DesignWorkshopGUI |
| - `__getattr__` | 125 | Delegates to `self._workshop` |
| - `__setattr__` | 145 | Intercepts attribute setting |
| - Proxy properties | 65-104 | ship, template_modifiers, selected_components |

### 32.3 Proxy Classes

**File:** `game/core/profiling.py`
| Class | Lines | Purpose |
|-------|-------|---------|
| _ProfilerProxy | 134-141 | Lazy singleton proxy |
| - `__getattr__` | 137 | `getattr(Profiler.instance(), name)` |
| - `__setattr__` | 140 | `setattr(Profiler.instance(), name, value)` |

---

## 33. DEFENSIVE ATTRIBUTE ACCESS PATTERNS (400+ instances)

### 33.1 Critical Areas (Object Initialization Issues)

**File:** `game/app.py` (Lines 629-641)
| Line | Pattern |
|------|---------|
| 629 | `game_session.save_path if hasattr(game_session, 'save_path') else None` |
| 635 | `empire.empire_theme_id if hasattr(empire, 'empire_theme_id') else None` |
| 641 | `empire.built_ship_designs if hasattr(empire, 'built_ship_designs') else set()` |

**File:** `game/simulation/battle_state.py` (Lines 191-382)
| Line | Pattern |
|------|---------|
| 191 | `if hasattr(ship, 'resources') and ship.resources:` |
| 198 | `if hasattr(ship, 'current_target') and ship.current_target:` |
| 211 | `if hasattr(ship.velocity, 'x') else (0, 0)` |
| 295 | `if hasattr(ship, 'retreat_status'):` |
| 382 | `if hasattr(proj, 'target') and proj.target:` |

### 33.2 Type Detection via hasattr (Duck Typing)

**File:** `game/ui/screens/strategy_screen.py` (Lines 446-544)
```
446: if hasattr(obj, 'stars')          # StarSystem
467: elif hasattr(obj, 'color') and hasattr(obj, 'mass')  # Star
481: elif hasattr(obj, 'planet_type')  # Planet
491: elif hasattr(obj, 'calculate_radiation')  # SectorEnvironment
511: elif hasattr(obj, 'ships')        # Fleet
544: elif hasattr(obj, 'destination_id')  # Warp Point
```

### 33.3 UI Element Existence Checks

**File:** `game/ui/screens/workshop_event_router.py` (65+ checks)
| Lines | Pattern |
|-------|---------|
| 65-341 | Excessive hasattr checks for UI elements |

### 33.4 High-Frequency getattr Files

| File | Approximate Count |
|------|-------------------|
| `ui/builder/stats_config.py` | 20+ |
| `ui/builder/weapons_panel.py` | 15+ |
| `game/simulation/components/abilities/weapons.py` | 12+ |
| `game/simulation/battle_state.py` | 10+ |
| `game/ai/behaviors.py` | 8+ |

---

## 34. COMMENTED AND DEAD CODE

### 34.1 Commented Code Blocks

| File | Line | Pattern |
|------|------|---------|
| `Tools/process_planet_images.py` | 28-32 | Commented nested loops |
| `game/ui/screens/workshop_screen.py` | 274, 321 | Commented panel update calls |
| `game/simulation/components/component.py` | 32 | `# allowed_layers removed in refactor` |
| `game/simulation/entities/ship_physics.py` | 25-38 | Commented physics questions |
| `game/simulation/entities/projectile.py` | 108-114 | Commented calculations |
| `tests/unit/combat/test_pdc.py` | 130-131 | Commented debug prints |

### 34.2 Stub/Placeholder Functions

| File | Line | Pattern |
|------|------|---------|
| `game/simulation/battle_controller.py` | 456-457 | Empty pass with TODO |
| `game/simulation/battle_controller.py` | 709-710 | Placeholder with only pass |

### 34.3 Removed Code Markers

| File | Line | Pattern |
|------|------|---------|
| `game/simulation/systems/battle_engine.py` | 158 | `# Removed Derelict Warning` |
| `game/simulation/components/component.py` | 31 | `# allowed_layers removed in refactor` |

---

## 35. NAMING INCONSISTENCIES

### 35.1 get_* Methods vs @property (150+ get_* methods)

Heavy use of `get_*` pattern in:
- `game/ai/interfaces/controllable.py` - 20 methods
- `game/strategy/data/fleet.py` - 15+ methods
- `game/strategy/data/ship_instance.py` - 20+ methods
- `game/simulation/entities/ship.py` - 10+ methods

Sparse @property usage:
- `game/simulation/battle_controller.py` - config, engine, service
- `game/ui/screens/strategy_scene.py` - galaxy, empires
- `game/strategy/data/galaxy.py` - primary_star

### 35.2 ALL_CAPS Instance Properties

| File | Line | Pattern |
|------|------|---------|
| `game/ui/screens/strategy_scene.py` | 67 | `self.HEX_SIZE = 10` |
| `game/ui/screens/strategy_scene.py` | 68 | `self.DETAIL_ZOOM_LEVEL = 3.0` |
| `game/ui/screens/strategy_fleet_ops.py` | 34 | `@property def HEX_SIZE(self)` |

---

## 36. DUPLICATE CODE PATTERNS

### 36.1 ValidationResult Classes (3 implementations)

| File | Fields | Notes |
|------|--------|-------|
| `game/simulation/validation/base.py` | is_valid, errors[], warnings[] | Full-featured |
| `game/strategy/engine/turn_engine.py` | is_valid, message, error_code | Dataclass |
| `game/ui/screens/race_validator.py` | is_valid, message | Minimal dataclass |

### 36.2 Color Calculation Functions

| File | Function | Thresholds |
|------|----------|------------|
| `game/ui/panels/ship_detail_panel.py` | `get_damage_color()` | >75% Green, 50-75% Yellow, 1-50% Red |
| `game/ui/panels/ship_stats_renderer.py` | `get_hp_bar_color()` | >50% Green, 20-50% Yellow, <20% Red |

### 36.3 Modifier Validation Overlap

| File | Function | Purpose |
|------|----------|---------|
| `game/simulation/components/modifier_schema.py` | `validate_modifier_v2()` | Schema validation |
| `game/simulation/components/modifier_effects.py` | `validate_modifier_definition()` | Formula validation |

---

## 37. DEBUG AND TEMPORARY FILES

### 37.1 Directories Marked for Deletion (Still Present)

| Directory | Size | Contents |
|-----------|------|----------|
| `Marked_For_Deletion_2026-01-21_07-33/` | 45MB | Debug logs, test files, temp images |
| `Debugging/Marked_for_Deletion_2026-01-20/` | 6 files | Old debug scripts |

### 37.2 Debug Scripts in Tools/

| File | Size | Purpose |
|------|------|---------|
| `Tools/debug_automation.py` | 1.3K | Modifier automation test |
| `Tools/debug_devastator.py` | 893B | Ship config test |
| `Tools/debug_patch.py` | 763B | Mock patching test |
| `Tools/debug_test.py` | 1.3K | Fuel tank test |
| `Tools/debug_test_clamping.py` | 902B | Clamping test |
| `Tools/debug_ui_import.py` | 401B | UI import test |

### 37.3 Log Files in Root

| File | Size |
|------|------|
| `battle.log` | 420KB |
| `combat_lab.log` | 109KB |
| `collect_log.txt` | 72KB |
| `collect_log_2.txt` | 308KB |
| `crash_log.txt` | 1.7KB |

### 37.4 Test Artifacts

| Directory | Contents |
|-----------|----------|
| `MagicMock/mock.context.savegame_path/` | Mock design JSON files |

---

## FINAL SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| Files marked for deletion | 11 + 45MB directory |
| Deprecated shim files | 5 |
| Method/property aliases | 25+ |
| Deprecated functions | 5 |
| Re-export patterns | 20+ files |
| Adapter/shim classes | 5 |
| Wrapper classes with delegation | 3 |
| Legacy data format support locations | 50+ |
| Backward compatibility test classes | 15+ |
| Commented/dead code blocks | 20+ |
| Legacy UI patterns | 10+ files |
| Architectural inconsistencies | 8 categories |
| Hacks/workarounds | 15+ |
| Migration tools | 8 |
| Debug/temporary files | 20+ |
| Bug reproduction tests | 28 |
| getattr/hasattr defensive patterns | 400+ locations |
| TODO/FIXME incomplete features | 10+ |
| Phase-based refactoring markers | 25+ |
| Duplicate class definitions | 3 (ValidationResult) |
| Duplicate utility functions | 2 (color calculations) |
| ALL_CAPS instance properties | 3 |
| get_* vs @property inconsistency | 150+ methods |

---

## 38. MAIN APPLICATION FILE (`game/app.py`)

### 38.1 GameState Constant Aliases
| Line | Pattern |
|------|---------|
| 45-54 | Aliased constants for backward compatibility: `MENU = GameState.MENU` and similar |

### 38.2 Global Variable Modifications
| Line | Pattern |
|------|---------|
| 74 | `global WIDTH, HEIGHT` |
| 532 | `global WIDTH, HEIGHT` (duplicate) |

### 38.3 Magic Numbers - Resolution Detection
| Line | Pattern |
|------|---------|
| 78-81 | Resolution breakpoints: 3840, 2160, 2560, 1600 |
| 127-136 | Button positioning offsets: 200, 50, -320, -250, -180, -110, -40, +30, +100, +170, +240, +310 |
| 184-185 | Hard-coded window dimensions (650x600) |
| 228 | Hard-coded error dialog dimensions (400x200) |
| 304-305 | Hard-coded window dimensions (600x500) |
| 397-399 | Hard-coded window dimensions (1800x1200) |
| 441 | Magic number: 0.1 for frame time clamp, division by 1000.0 |

### 38.4 Defensive hasattr Patterns (14+ instances)
| Line | Pattern |
|------|---------|
| 155-156 | `hasattr()` for optional cleanup method |
| 160 | `hasattr()` for optional resize handler |
| 180 | `hasattr()` for optional ui manager |
| 300 | `hasattr()` for optional ui manager |
| 499 | Multiple chained `hasattr()` defensive checks |
| 504, 509 | `hasattr()` for optional ui manager |
| 527, 550, 578 | Chained defensive `hasattr()` checks |
| 590 | `hasattr()` for optional scroll handler |
| 616, 653, 668 | Chained defensive `hasattr()` and null checks |
| 629, 632, 641 | Defensive ternary with `hasattr()` |
| 673, 674, 678, 679 | `hasattr()` for optional ui manager |

### 38.5 TODO/Placeholder Code
| Line | Pattern |
|------|---------|
| 625 | "placeholder for now - will be implemented when tech tree exists" |
| 626 | TODO: "Replace with empire.available_tech or similar" |
| 633 | Debug print statement left in |

---

## 39. BATTLE CONTROLLER DEEP AUDIT (`game/simulation/battle_controller.py`)

### 39.1 TODO/FIXME Comments
| Line | Content |
|------|---------|
| 456-457 | `# TODO: Override AI to move toward edge` followed by `pass` stub |
| 579-580 | `# TODO: Restore projectiles` |
| 708-710 | `# TODO: Implement when Fleet uses ShipInstance` with bare `pass` |

### 39.2 hasattr/getattr Defensive Patterns
| Line | Pattern |
|------|---------|
| 473 | `if hasattr(ship, 'retreat_status'):` |
| 799 | `if hasattr(scenario, 'max_ticks')` with fallback to 100000 |

### 39.3 Backward Compatibility Property
| Line | Pattern |
|------|---------|
| 618-620 | `@property engine` with docstring "for backward compatibility" |

### 39.4 Magic Numbers
| Line | Value | Context |
|------|-------|---------|
| 46 | 100000 | BattleConfig.max_ticks default |
| 66 | (0, 0, 100000, 100000) | Default map bounds |
| 75, 364 | 500 | Warp retreat required_ticks |
| 291 | 100 | Progress callback modulo |
| 504 | 500 | Map edge detection threshold |
| 549, 799 | 100000 | max_ticks fallback (duplicate) |
| 917-918 | 20000, 50000, 80000, 2000 | Ship spawn positions |

### 39.5 Incomplete Implementations
| Line | Method | Status |
|------|--------|--------|
| 456-457 | AI retreat navigation | Stub with `pass` |
| 579-580 | Projectile restoration | Not implemented |
| 667-710 | `apply_results_to_fleet()` | Placeholder facade |
| 383-428 | `add_reinforcements()` | Partial implementation |

---

## 40. BATTLE STATE DEFENSIVE PATTERNS (`game/simulation/battle_state.py`)

### 40.1 hasattr() Defensive Patterns
| Line | Pattern |
|------|---------|
| 191-194 | `if hasattr(ship, 'resources') and ship.resources:` |
| 198-200 | `if hasattr(ship, 'current_target') and ship.current_target:` |
| 211 | `if hasattr(ship.velocity, 'x') else (0, 0)` |
| 295 | `if hasattr(ship, 'retreat_status'):` |
| 382-388 | `if hasattr(proj, 'target')` and `if hasattr(proj_type, 'value')` |
| 538, 542 | Duplicate `if hasattr(engine, 'end_condition')` checks |

### 40.2 getattr() with Defaults (16 instances)
| Line | Pattern |
|------|---------|
| 62 | `getattr(component, 'modifiers', [])` |
| 209 | `getattr(ship, 'ai_strategy', 'standard_ranged')` |
| 212 | `getattr(ship, 'angle', 0)` |
| 215-216 | `getattr(ship, 'current_shields', 0)`, `getattr(ship, 'max_shields', 0)` |
| 221-222 | `getattr(ship, 'is_derelict', False)`, `getattr(ship, 'retreat_status', None)` |
| 399 | `getattr(proj, 'max_endurance', proj.endurance or 0)` - cascading fallback |
| 401-406 | Multiple `getattr()` for missile properties |

### 40.3 dict.get() Backward Compatibility (30+ instances)
| Lines | Pattern |
|-------|---------|
| 144-171 | ShipState.from_dict() with `.get()` defaults for optional fields |
| 346-366 | ProjectileState.from_dict() with `.get()` defaults |
| 460-482 | BattleState.from_dict() with version compatibility fields |
| 616-635 | BattleResults.from_dict() with conditional deserialization |

### 40.4 Version Field (Unused)
| Line | Pattern |
|------|---------|
| 414 | `version: str = "1.0"` - hardcoded, no migration logic |

---

## 41. TEST LAB SCENE LEGACY PATTERNS (`ui/test_lab_scene.py`)

### 41.1 Deprecated Method
| Line | Pattern |
|------|---------|
| 3657-3741 | `_draw_seed_controls_OLD()` - "DEPRECATED - Seed controls moved to header. This is kept for reference." (85 lines) |

### 41.2 Inline Debug Imports
| Line | Pattern |
|------|---------|
| 1941-1942 | `import traceback; traceback.print_exc()` in exception handler |
| 2167-2168 | Same pattern |
| 2585-2586 | Same pattern |
| 2718-2719 | Same pattern |

### 41.3 Empty Stub Methods
| Line | Method | Context |
|------|--------|---------|
| 537-539 | `update()` | ShipPanel - empty stub |
| 626-628 | `update()` | TabbedShipPanel - empty stub |

### 41.4 Class Name isinstance Workaround
| Line | Pattern |
|------|---------|
| 1897-1900 | `if rule.__class__.__name__ == 'ExactMatchRule'` - string comparison instead of isinstance |

### 41.5 Broad Exception Handlers
| Lines | Pattern |
|-------|---------|
| 1939, 2165, 2514, 2583, 2715, 2839 | `except Exception as e:` - catch-all handlers |

### 41.6 Results Alias
| Line | Pattern |
|------|---------|
| 2694 | `scenario.results['ticks'] = tick_count` - "Alias for consistency with runner" |

---

## 42. TYPE CHECKING WORKAROUNDS (30+ instances)

### 42.1 `__class__.__name__` String Comparisons
| File | Line | Pattern |
|------|------|---------|
| `game/simulation/entities/ship_stats.py` | 290 | `if ab.__class__.__name__ == 'ResourceConsumption'` |
| `ui/test_lab_scene.py` | 1900 | `if rule.__class__.__name__ == 'ExactMatchRule'` |
| `test_framework/services/metadata_management_service.py` | 60 | Same pattern |
| `game/simulation/entities/ability_aggregator.py` | 44, 200 | `ability_name = ab.__class__.__name__` |
| `game/simulation/entities/combat_endurance.py` | 37 | `ab_cls = ab.__class__.__name__` |
| `game/simulation/entities/combat_endurance.py` | 63 | `if inst.__class__.__name__ in ['WeaponAbility', 'ProjectileWeaponAbility', ...]` |

### 42.2 MRO Traversal Workaround (Documented Known Issue)
| File | Line | Pattern |
|------|------|---------|
| `game/simulation/components/component.py` | 177-186 | Fallback for Module Identity Drift using `cls.__name__` comparison in MRO loop |

### 42.3 Duck Typing with Chained hasattr()
| File | Line | Pattern |
|------|------|---------|
| `game/core/math.py` | 32 | `if hasattr(x, 'x') and hasattr(x, 'y'):` (Vector2 duck typing) |
| `game/ui/screens/strategy_screen.py` | 446-544 | Type discrimination: `hasattr(obj, 'stars')`, `hasattr(obj, 'ships')`, etc. |
| `game/ui/panels/system_tree_panel.py` | 153 | `stars = [x for x in contents if hasattr(x, 'color') and hasattr(x, 'mass')]` |

### 42.4 Type Name Strings for Filtering
| File | Line | Pattern |
|------|------|---------|
| `ui/builder/detail_panel.py` | 198 | `if k in ["ProjectileWeapon", "BeamWeapon", "Armor"]:` |
| `test_framework/scenario.py` | 110 | `if c.type_str in ["Weapon", "ProjectileWeapon", "BeamWeapon", "Shield"]:` |

---

## 43. MAGIC NUMBERS COMPREHENSIVE LIST

### 43.1 Camera & Rendering
| File | Line | Value | Context |
|------|------|-------|---------|
| `game/ui/renderer/camera.py` | 16-18 | 8.0, 0.01, 5.0 | zoom_speed, min_zoom, max_zoom |
| `game/ui/renderer/camera.py` | 80-82 | 1.15 | Zoom multiplier |
| `game/ui/renderer/camera.py` | 119-120 | 500 | Camera fit margin |

### 43.2 Exit Dialog
| File | Line | Values | Context |
|------|------|--------|---------|
| `game/exit_dialog.py` | 32 | 400, 200 | Dialog dimensions |
| `game/exit_dialog.py` | 45-46 | 100, 40, 40 | Button dimensions, spacing |

### 43.3 Battle System
| File | Line | Value | Context |
|------|------|-------|---------|
| `game/simulation/systems/battle_engine.py` | 373 | -10, 10 | Projectile spawn offset range |
| `game/simulation/systems/battle_end_conditions.py` | 57 | 500 | Default max_ticks |
| `game/simulation/entities/ship_stats.py` | 373-374 | 80.0, -2.5 | Baseline diameter, size coefficient |

### 43.4 Weapons
| File | Line | Value | Context |
|------|------|-------|---------|
| `game/simulation/components/abilities/weapons.py` | 76-77 | 360, 0 | Default firing_arc, facing_angle |
| `game/simulation/components/abilities/weapons.py` | 222, 300 | 500 | Default projectile_speed |
| `game/simulation/components/abilities/weapons.py` | 241-242 | 0.001, 1.0 | accuracy_falloff, base_accuracy |
| `game/simulation/components/abilities/weapons.py` | 301-302 | 3.0, 30.0 | Missile endurance, turn_rate |

### 43.5 AI Priority Scores
| File | Line | Value | Context |
|------|------|-------|---------|
| `game/ai/target_evaluator.py` | 123 | 1000 | High priority score |
| `game/ai/target_evaluator.py` | 141 | 2000 | Very high priority (missiles in PDC) |
| `game/ai/target_evaluator.py` | 148 | -999999 | Penalty score |

---

## 44. UNION TYPES INDICATING BACKWARD COMPATIBILITY

| File | Line | Pattern | Purpose |
|------|------|---------|---------|
| `game/core/json_utils.py` | 27, 64, 93 | `Union[str, Path]` | Path type migration |
| `game/strategy/data/fleet.py` | 60, 67, 77 | `Union[str, 'ShipInstance']` | Ship data migration |
| `game/simulation/entities/ship.py` | 30, 34 | `Union[Tuple[int,int,int], List[int]]` | Color format compatibility |
| `game/ui/screens/workshop_data_loader.py` | 44 | `Union[str, List[str]]` | File name resolution |
| `game/simulation/formula_system.py` | 65 | `Union[int, float]` | Numeric return types |
| `game/simulation/entities/ship.py` | 566 | `Union[float, int, bool]` | Ability value types |

---

## 45. TRY/EXCEPT ATTRIBUTEERROR PATTERNS

### 45.1 Delegation Pattern Blocks
| File | Line | Pattern |
|------|------|---------|
| `game/ui/screens/builder_screen.py` | 137 | `try: workshop = object.__getattribute__(self, '_workshop') except AttributeError:` |
| `game/ui/screens/builder_screen.py` | 161 | Same pattern in `__setattr__` |

### 45.2 Nested getattr() Fallback Chains
| File | Line | Pattern |
|------|------|---------|
| `game/ai/target_evaluator.py` | 171 | `getattr(c, 'current_hp', getattr(c, 'max_hp', 0))` |
| `game/ui/panels/ship_stats_renderer.py` | 320 | `getattr(ship.current_target, 'name', getattr(ship.current_target, 'type', 'Target'))` |
| `game/ui/screens/strategy_screen.py` | 584 | `getattr(facility, 'name', getattr(facility, 'design_id', 'Unknown'))` |
| `game/simulation/ship_validator.py` | 303 | `getattr(ab, 'resource_type', getattr(ab, 'resource_name', None))` |

---

## 46. TEST FIXTURE ALIASES

### 46.1 conftest.py Fixture Aliases
| File | Line | Alias | Target |
|------|------|-------|--------|
| `tests/unit/entities/conftest.py` | 24-25 | `basic_ship` | `basic_cruiser_ship` |
| `tests/unit/combat/conftest.py` | 21 | `basic_combat_ship` | `basic_cruiser_ship` |
| `tests/unit/combat/conftest.py` | 22 | `armed_combat_ship` | `armed_ship` |

### 46.2 Legacy Fields in Fixtures
| File | Lines | Pattern |
|------|-------|---------|
| `tests/unit/strategy/conftest.py` | 117-124 | Legacy fields in `ship_stats_with_custom_resources`: `max_fuel`, `max_energy`, `max_ammo`, etc. |
| `tests/unit/strategy/conftest.py` | 257-270 | `legacy_string_fleet` fixture for pre-refactoring format |

---

## 47. TOOLS DIRECTORY COMPLETE AUDIT

### 47.1 Migration Tools (8 files)
| File | Purpose |
|------|---------|
| `migrate_data.py` | Legacy resource cost fields to ResourceConsumption |
| `migrate_legacy_components.py` | Phase 6 weapon attributes migration |
| `refactor_phase2.py` | Core module import restructuring |
| `refactor_phase3.py` | Additional import path updates |
| `refactor_phase4.py` | AI module import refactoring |
| `refactor_components.py` | Remove 'allowed_layers' field |
| `refactor_fix_json_paths.py` | Fix hardcoded JSON paths in tests |
| `refactor_fix_mocks.py` | Update mock patch paths |

### 47.2 Debug Scripts (11 files)
| File | Purpose |
|------|---------|
| `debug_automation.py` | Modifier loading test |
| `debug_devastator.py` | Ship config test |
| `debug_patch.py` | Mock patching test |
| `debug_test.py` | Fuel tank clamping |
| `debug_test_clamping.py` | ResourceRegistry clamping |
| `debug_ui_import.py` | UI import validation |
| `reproduce_missile_issue.py` | Missile targeting reproduction |
| `reproduce_mock_error.py` | Mock pattern validation |
| `reproduce_seeker.py` | Seeker range calculation |
| `visual_test_beam_weapon.py` | Interactive beam weapon test |
| `visual_test_sprites.py` | Sprite rendering test |

### 47.3 Interactive Tools (3 files)
| File | Purpose |
|------|---------|
| `component_graphic_picker.py` (18KB) | Component sprite selection UI |
| `component_manager.py` (36KB) | Component image organization |
| `formation_editor.py` (43KB) | Formation layout editor |

### 47.4 Deprecated/Superseded
| File | Status |
|------|--------|
| `fix_modifiers.py` | Superseded by v2 |
| `fix_modifiers_v2.py` | Improved version |
| `cleanup_pygame.py` | One-time executed |
| `update_paths.py` | No-op template |

---

## 48. DELEGATION PATTERNS

### 48.1 `__getattr__` Delegation
| File | Lines | Purpose |
|------|-------|---------|
| `game/ui/screens/builder_screen.py` | 124-142 | Delegates to `_workshop` |
| `game/core/profiling.py` | 137-138 | `_ProfilerProxy` delegates to `Profiler.instance()` |
| `game/ai/interfaces/controllable.py` | 190-197 | `ShipControllableAdapter` delegates to `_ship` |

### 48.2 `__setattr__` Override
| File | Lines | Purpose |
|------|-------|---------|
| `game/ui/screens/builder_screen.py` | 144-164 | Intercepts for workshop delegation |
| `game/core/profiling.py` | 140-141 | Delegates to Profiler singleton |
| `game/ai/interfaces/controllable.py` | 199-214 | Delegates to underlying ship |

### 48.3 Proxy Properties (Formation Delegation)
| File | Lines | Properties |
|------|-------|------------|
| `game/simulation/entities/ship.py` | 169-215 | `formation_master`, `formation_offset`, `formation_rotation_mode`, `formation_members`, `in_formation` |

---

## 49. LEGACY UI WIDGETS (`ui/components.py`)

### 49.1 Legacy Classes
| Line | Class | Status |
|------|-------|--------|
| 5 | `Button` | **ACTIVELY USED** in game/app.py main menu |
| 36 | `Label` | **NOT NEEDED** - replaced by pygame_gui.UILabel |
| 50 | `Slider` | **NOT NEEDED** - not used in production |

### 49.2 Button Usage Locations
| File | Lines | Usage |
|------|-------|-------|
| `game/app.py` | 127-136 | 10 main menu buttons |
| `ui/test_lab_scene.py` | 52, 153-157, 2321 | Test lab UI buttons |

---

## 50. VERSION CHECKING & FORMAT HANDLING

### 50.1 Save Game Versioning
| File | Line | Pattern |
|------|------|---------|
| `game/strategy/systems/save_game_service.py` | 25 | `SAVE_VERSION = "2.0.0"` |
| `game/strategy/systems/save_game_service.py` | 31 | `MIGRATABLE_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "1.9.0"]` |
| `game/strategy/systems/save_game_service.py` | 380-419 | `_is_compatible_version()`, `_can_migrate_version()` |

### 50.2 Modifier Schema Versioning
| File | Line | Pattern |
|------|------|---------|
| `game/simulation/components/modifier_schema.py` | 20-49 | `is_v2_format()` - V2 (list) vs V1 (dict) |
| `game/simulation/components/modifier_schema.py` | 28-29 | V1 format deprecated |

### 50.3 Disabled Migration Function (BUG-29)
| File | Lines | Pattern |
|------|-------|---------|
| `game/strategy/systems/save_game_service.py` | 75-78 | Commented out `_migrate_temp_designs()` call |
| `game/strategy/systems/save_game_service.py` | 115-147 | Unused function definition |

---

## 51. UI SCREENS HASATTR ANALYSIS

### 51.1 strategy_screen.py (30 hasattr instances)
| Lines | Pattern |
|-------|---------|
| 446-544 | Duck typing: `hasattr(obj, 'stars')`, `hasattr(obj, 'ships')`, `hasattr(obj, 'planet_type')`, etc. |
| 576-605 | Planet ownership/colony checks |
| 631, 647, 654, 676, 679 | Callback method existence checks |
| 686, 690, 715, 721, 728, 733 | Fleet validation checks |

### 51.2 race_setup_screen.py (7 hasattr instances)
| Line | Pattern |
|------|---------|
| 370, 375 | Optional state initialization checks |
| 840, 845 | Cleanup guards for optional elements |
| 1062, 1121, 1191 | Double-check patterns for UI elements |

### 51.3 fleet_report_window.py (10 hasattr instances)
| Lines | Pattern |
|-------|---------|
| 399, 946 | `hasattr(self, 'header_widgets')` cleanup guard |
| 583, 588 | Widget interface duck typing |
| 860, 869 | Event property checks |
| 949, 952 | Button discrimination via hasattr |

### 51.4 planet_list_window.py (14 hasattr instances)
| Line | Pattern |
|------|---------|
| 144 | `hasattr(planet, '_temp_system_ref')` - temporary reference |
| 172, 207, 210, 213 | Optional property checks |
| 688 | `hasattr(planet, 'image')` - optional asset |
| 824, 831, 870, 873 | Button/column reference discrimination |

---

## 52. SIMULATION_TESTS DIRECTORY

### 52.1 Commented Tests
| File | Line | Pattern |
|------|------|---------|
| `simulation_tests/tests/test_example_scenarios.py` | 93 | `# def test_beam_mid_range(self):` |
| `simulation_tests/tests/test_example_scenarios.py` | 97 | `# def test_beam_max_range(self):` |

### 52.2 Skipped Tests
| File | Line | Reason |
|------|------|--------|
| `simulation_tests/tests/test_projectile_weapons.py` | 97 | "Target ship engine configuration issue" |
| `simulation_tests/tests/test_seeker_weapons.py` | 250 | "Requires Point Defense target ships - not yet implemented" |

### 52.3 Missing Import
| File | Line | Issue |
|------|------|-------|
| `simulation_tests/conftest.py` | 61 | `os.environ.get()` called but `import os` missing |

---

## 53. PASS STATEMENT ANALYSIS

### 53.1 Abstract Interface Methods (31+ in IControllable)
| File | Lines | Purpose |
|------|-------|---------|
| `game/ai/interfaces/controllable.py` | 38-159 | ABC abstract methods |
| `game/strategy/interfaces/battle_resolver.py` | 59, 80 | Abstract resolver methods |
| `game/simulation/validation/base.py` | 125, 150 | Abstract validation rules |

### 53.2 Incomplete Implementations
| File | Line | Method |
|------|------|--------|
| `game/simulation/battle_controller.py` | 457 | Retreat AI navigation |
| `game/simulation/battle_controller.py` | 710 | Fleet results application |
| `game/strategy/engine/fleet_movement_engine.py` | 104 | Retry logic placeholder |

### 53.3 Exception Handlers with pass (12+ instances)
| File | Lines |
|------|-------|
| `game/simulation/entities/ability_aggregator.py` | 77 |
| `game/ai/target_evaluator.py` | 153 |
| `game/ai/controller.py` | 332 |
| `game/simulation/components/abilities/defense.py` | 73, 96, 119 |

---

## 54. STRATEGY ADAPTERS (`game/strategy/adapters/`)

### 54.1 Bridge Pattern Implementation
| File | Lines | Pattern |
|------|-------|---------|
| `simulation_adapter.py` | 30-142 | `SimulationBattleResolver(IBattleResolver)` - bridges strategy to simulation |
| `simulation_adapter.py` | 57-59 | Fleet → BattleShip conversion |
| `simulation_adapter.py` | 116-131 | BattleResults → BattleResult conversion |

### 54.2 Translation Layer
| Direction | Method | Purpose |
|-----------|--------|---------|
| Strategy → Simulation | `Fleet.to_battle_ships()` | Converts ShipInstance to Ship |
| Simulation → Strategy | `ShipState.to_ship()` | Reconstructs from state |
| Simulation → Strategy | `Fleet.update_from_battle_results()` | Persists damage state |

### 54.3 Naming Confusion
| Pattern | Issue |
|---------|-------|
| `BattleResult` (strategy) vs `BattleResults` (simulation) | Different classes, potential confusion |

---

## 55. GAME/CORE DIRECTORY AUDIT

### 55.1 Singleton Patterns (4 files)
| File | Lines | Pattern |
|------|-------|---------|
| `logger.py` | 5-15 | Thread-safe `__new__()` singleton |
| `profiling.py` | 30-67 | Double-checked locking |
| `registry.py` | 39-96 | Double-checked locking with freeze() |
| `screenshot_manager.py` | 22-58 | Double-checked locking |

### 55.2 Backward Compatibility Aliases
| File | Line | Pattern |
|------|------|---------|
| `screenshot_manager.py` | 47 | `get_instance = instance` |
| `profiling.py` | 144 | `PROFILER = _ProfilerProxy()` |
| `constants.py` | 32-33 | `WIDTH = DisplayConfig.DEFAULT_WIDTH` |

### 55.3 Non-standard Exception Types
| File | Line | Pattern |
|------|------|---------|
| `logger.py` | 35 | `raise Exception("Profiler is a singleton...")` |
| `profiling.py` | 35 | Same pattern |
| `registry.py` | 50 | Same pattern |
| `screenshot_manager.py` | 27 | Same pattern |

### 55.4 Import Ordering Issues
| File | Line | Issue |
|------|------|-------|
| `constants.py` | 9, 31 | Imports split across file |

---

## 56. CONDITIONAL IMPORTS

### 56.1 Optional Dependencies
| File | Line | Pattern |
|------|------|---------|
| `Tools/resize_components.py` | 5 | Auto-installs PIL if missing |
| `simulation_tests/data/schema_validator.py` | 31 | `JSONSCHEMA_AVAILABLE = False` flag |
| `simulation_tests/scenarios/validation.py` | 484 | Optional scipy.stats |

### 56.2 Dynamic Module Loading
| File | Line | Pattern |
|------|------|---------|
| `test_framework/runner.py` | 220, 238 | `importlib.import_module()` for scenarios |
| `Reviews/scripts/review_to_project.py` | 51-64 | sys.path manipulation |

---

## 57. `__all__` RE-EXPORT PATTERNS

### 57.1 Deprecated Module Aliases
| File | Lines | Pattern |
|------|-------|---------|
| `game/ui/screens/builder_viewmodel.py` | 5-8 | `WorkshopViewModel as BuilderViewModel` |
| `game/ui/screens/builder_event_router.py` | 5-8 | `WorkshopEventRouter as BuilderEventRouter` |
| `game/ui/screens/builder_data_loader.py` | 5-8 | `WorkshopDataLoader as BuilderDataLoader` |

### 57.2 Package-level Consolidation
| File | Exports |
|------|---------|
| `game/core/__init__.py` | `Vector2`, `clamp`, `lerp`, `angle_diff` |
| `game/ai/interfaces/__init__.py` | `IControllable`, `ShipControllableAdapter` |
| `game/strategy/interfaces/__init__.py` | `IBattleResolver`, `BattleResult` |
| `game/simulation/services/__init__.py` | `ModifierService`, `ShipBuilderService`, `BattleService`, etc. |

---

## FINAL UPDATED STATISTICS

| Category | Count |
|----------|-------|
| Files marked for deletion | 11 + 45MB directory |
| Deprecated shim files | 5 |
| Method/property aliases | 30+ |
| Deprecated functions | 6 |
| Re-export patterns | 25+ files |
| Adapter/shim classes | 6 |
| Wrapper classes with delegation | 4 |
| Legacy data format support locations | 60+ |
| Backward compatibility test classes | 20+ |
| Commented/dead code blocks | 25+ |
| Legacy UI patterns | 12+ files |
| Architectural inconsistencies | 10 categories |
| Hacks/workarounds | 20+ |
| Migration tools | 8 |
| Debug/temporary files | 25+ |
| Bug reproduction tests | 28 |
| getattr/hasattr defensive patterns | 500+ locations |
| TODO/FIXME incomplete features | 15+ |
| Phase-based refactoring markers | 30+ |
| Duplicate class definitions | 3 (ValidationResult) |
| Duplicate utility functions | 3 |
| ALL_CAPS instance properties | 3 |
| get_* vs @property inconsistency | 150+ methods |
| Magic numbers without constants | 50+ |
| Union types for compatibility | 6+ |
| Singleton patterns | 4 |
| Abstract pass statements | 35+ |
| __class__.__name__ workarounds | 15+ |
| Skipped/commented tests | 5+ |
| Type discrimination via hasattr | 60+ |

---

*End of Comprehensive Audit Report*
