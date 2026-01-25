# Phase 2: Remove Shims & Aliases

**Project:** Legacy Code Cleanup
**Phase:** 2 of 8
**Risk Level:** Medium
**Dependencies:** Phase 1 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| **2** | **Remove Shims & Aliases** | **THIS PHASE** |
| 3 | Consolidate Re-exports | Pending |
| 4 | Enforce Layer Boundaries | Pending |
| 5 | Standardize Registry Access | Pending |
| 6 | Type Safety via Protocols | Pending |
| 7 | Standardize Data Formats | Pending |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 2 Objectives

1. Remove deprecated Builder → Workshop shim files
2. Remove ShipBuilderService → VehicleDesignService shim
3. Remove method aliases that exist for backward compatibility
4. Standardize singleton accessor pattern (remove `get_instance` aliases)
5. Remove deprecated functions

---

## Detailed Tasks

### 2.1 Remove Builder → Workshop Shims

These files exist solely to re-export Workshop classes under old Builder names.

**Step A: Find all usages of deprecated imports**

Search for imports of:
- `BuilderSceneGUI`
- `BuilderViewModel`
- `BuilderDataLoader`
- `BuilderEventRouter`

**Step B: Update imports to use Workshop equivalents**

| Old Import | New Import |
|------------|------------|
| `from game.ui.screens.builder_screen import BuilderSceneGUI` | `from game.ui.screens.workshop_screen import DesignWorkshopGUI` |
| `from game.ui.screens.builder_viewmodel import BuilderViewModel` | `from game.ui.screens.workshop_viewmodel import WorkshopViewModel` |
| `from game.ui.screens.builder_data_loader import BuilderDataLoader` | `from game.ui.screens.workshop_data_loader import WorkshopDataLoader` |
| `from game.ui.screens.builder_event_router import BuilderEventRouter` | `from game.ui.screens.workshop_event_router import WorkshopEventRouter` |

**Step C: Delete shim files**

Delete these files after all imports are updated:
- `game/ui/screens/builder_screen.py`
- `game/ui/screens/builder_viewmodel.py`
- `game/ui/screens/builder_data_loader.py`
- `game/ui/screens/builder_event_router.py`

### 2.2 Remove ShipBuilderService Shim

**File:** `game/simulation/services/ship_builder_service.py`

This file re-exports `VehicleDesignService` as `ShipBuilderService`.

**Step A: Find all usages**
```
Search for: from game.simulation.services.ship_builder_service import
Search for: ShipBuilderService
Search for: ShipBuilderResult
```

**Step B: Update imports**

| Old Import | New Import |
|------------|------------|
| `from game.simulation.services.ship_builder_service import ShipBuilderService` | `from game.simulation.services.vehicle_design_service import VehicleDesignService` |
| `from game.simulation.services.ship_builder_service import ShipBuilderResult` | `from game.simulation.services.vehicle_design_service import DesignResult` |

**Step C: Delete shim file**
- Delete `game/simulation/services/ship_builder_service.py`

### 2.3 Remove Method Aliases

#### 2.3.1 Fleet Warp Resource Aliases

**File:** `game/strategy/data/fleet.py`

| Lines | Alias Method | Canonical Method |
|-------|--------------|------------------|
| 350-360 | `has_energy_for_warp()` | `has_resources_for_warp()` |
| 392-403 | `consume_warp_energy()` | `consume_warp_resources()` |

**Steps:**
1. Search for all calls to `has_energy_for_warp()` and `consume_warp_energy()`
2. Update calls to use canonical method names
3. Delete the alias methods from fleet.py

#### 2.3.2 PathSegment Property Alias

**File:** `game/strategy/engine/fleet_movement.py`

| Lines | Alias | Canonical |
|-------|-------|-----------|
| 43-46 | `hex` property | `end` property |
| 48-56 | `to_dict()` includes `'hex': self.end` | Remove duplicate key |
| 307-314 | `project_path_as_dicts()` | Update callers, remove wrapper |

**Steps:**
1. Search for all usages of `.hex` on PathSegment objects
2. Update to use `.end` instead
3. Remove the `hex` property alias
4. Clean up `to_dict()` to not include duplicate key
5. Evaluate `project_path_as_dicts()` - update callers if needed

#### 2.3.3 Ship Stats Alias

**File:** `game/simulation/entities/ship_stats.py`

| Line | Alias | Canonical |
|------|-------|-----------|
| 337-338 | `to_hit_profile` | `total_defense_score` |

**Steps:**
1. Search for all usages of `to_hit_profile`
2. Update to use `total_defense_score`
3. Remove the alias assignment

### 2.4 Remove Singleton Aliases

Standardize on `instance()` classmethod pattern. Remove `get_instance` aliases.

#### 2.4.1 Screenshot Manager

**File:** `game/core/screenshot_manager.py`
- Line 46-47: `get_instance = instance`

**Steps:**
1. Search for `ScreenshotManager.get_instance()`
2. Update to `ScreenshotManager.instance()`
3. Remove the alias

#### 2.4.2 Ship Theme

**File:** `game/simulation/ship_theme.py`
- Line 43-44: `get_instance = instance`

**Steps:**
1. Search for `ShipTheme.get_instance()`
2. Update to `ShipTheme.instance()`
3. Remove the alias

#### 2.4.3 Sprites

**File:** `game/ui/renderer/sprites.py`
- Line 46: `get_instance = instance`

**Steps:**
1. Search for `SpriteManager.get_instance()` or similar
2. Update to use `instance()`
3. Remove the alias

**Also check:** `game/ui/renderer/game_renderer.py` (Line 41 uses legacy `get_instance()`)

### 2.5 Remove Deprecated Functions

#### 2.5.1 Strategy Manager

**File:** `game/ai/strategy_manager.py`
- Line 155: `load_combat_strategies()` - marked as deprecated

**Steps:**
1. Search for all calls to `load_combat_strategies()`
2. Remove calls (StrategyManager uses lazy loading)
3. Delete the function

#### 2.5.2 Turn Engine Deprecated Methods

**File:** `game/strategy/engine/turn_engine.py`

| Lines | Method | Status |
|-------|--------|--------|
| 225-236 | `_execute_move_step()` | Emits DeprecationWarning |
| 167-169 | `_spawn_complex` | Kept for backward compatibility |
| 175-177 | `_spawn_ship` | Kept for backward compatibility |
| 214-215 | `_calculate_next_hex` | Kept for backward compatibility |

**Steps:**
1. Search for all usages of these methods
2. Update callers to use current implementations
3. Delete the deprecated methods

---

## Verification Checklist

After completing all tasks:

- [ ] All Builder imports updated to Workshop
- [ ] All 4 builder shim files deleted
- [ ] ShipBuilderService shim deleted
- [ ] Fleet warp aliases removed, callers updated
- [ ] PathSegment `hex` alias removed, callers updated
- [ ] `to_hit_profile` alias removed, callers updated
- [ ] All `get_instance` calls updated to `instance()`
- [ ] Singleton aliases removed
- [ ] Deprecated functions deleted
- [ ] No `DeprecationWarning` emissions during tests
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly

---

## Files Deleted

- `game/ui/screens/builder_screen.py`
- `game/ui/screens/builder_viewmodel.py`
- `game/ui/screens/builder_data_loader.py`
- `game/ui/screens/builder_event_router.py`
- `game/simulation/services/ship_builder_service.py`

## Files Modified

- `game/strategy/data/fleet.py` (remove aliases)
- `game/strategy/engine/fleet_movement.py` (remove alias)
- `game/simulation/entities/ship_stats.py` (remove alias)
- `game/core/screenshot_manager.py` (remove alias)
- `game/simulation/ship_theme.py` (remove alias)
- `game/ui/renderer/sprites.py` (remove alias)
- `game/ui/renderer/game_renderer.py` (update to use `instance()`)
- `game/ai/strategy_manager.py` (remove deprecated function)
- `game/strategy/engine/turn_engine.py` (remove deprecated methods)
- Various files that import from shims (update imports)

---

## Notes for Next Phase

Phase 3 (Consolidate Re-exports) will:
- Update callers to import from canonical module locations
- Remove backward compatibility re-exports from component.py, ship.py, controller.py
- Remove thin adapter/wrapper classes

Ensure all tests pass before proceeding to Phase 3.

---

*End of Phase 2 Plan*
