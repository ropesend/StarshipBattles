# PROJ-15: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project is Phase 2 of an 8-phase Legacy Code Cleanup effort. Phase 1 (PROJ-14) handles deleting dead code. This phase focuses on removing backward compatibility shims and aliases that were introduced during previous refactoring efforts.

**Source Document:** `Projects/legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md`

### Categories of Work

1. **Builder → Workshop Shims** - 5 files that re-export Workshop classes under old Builder names
2. **Method/Property Aliases** - Backward compatibility wrapper methods in Fleet, PathSegment, ShipStats
3. **Singleton Accessor Aliases** - `get_instance` aliases that should use `instance()` pattern
4. **Deprecated Functions** - Functions marked deprecated that should be removed

---

## Swarm Findings Summary

### 1. Builder → Workshop Shim Usages

#### Shim Files to Delete

| File | Type | What It Re-exports |
|------|------|-------------------|
| `game/ui/screens/builder_screen.py` | Wrapper class | `BuilderSceneGUI` → `DesignWorkshopGUI` |
| `game/ui/screens/builder_viewmodel.py` | Pure alias | `BuilderViewModel` → `WorkshopViewModel` |
| `game/ui/screens/builder_data_loader.py` | Pure alias | `BuilderDataLoader` → `WorkshopDataLoader` |
| `game/ui/screens/builder_event_router.py` | Pure alias | `BuilderEventRouter` → `WorkshopEventRouter` |
| `game/simulation/services/ship_builder_service.py` | Pure alias | `ShipBuilderService` → `VehicleDesignService` |

#### Production Code Usages

| File | Line | Import/Usage |
|------|------|--------------|
| `game/app.py` | 18 | `from game.ui.screens.builder_screen import BuilderSceneGUI` |
| `game/app.py` | 118, 150 | Instantiates `BuilderSceneGUI(...)` |
| `game/simulation/services/__init__.py` | 3 | Re-exports `ShipBuilderService`, `ShipBuilderResult` |
| `game/ui/screens/workshop_viewmodel.py` | 14 | `from game.simulation.services import ShipBuilderService, ShipBuilderResult` |

#### Test File Usages (8 files for BuilderSceneGUI)

| File | Import |
|------|--------|
| `tests/unit/builder/test_builder_warning_logic.py` | `BuilderSceneGUI` |
| `tests/unit/builder/test_selection_refinements.py` | `BuilderSceneGUI` |
| `tests/unit/builder/test_builder_structure_features.py` | `BuilderSceneGUI` |
| `tests/unit/builder/test_builder_io_integration.py` | `BuilderSceneGUI` |
| `tests/unit/builder/test_builder_improvements.py` | `BuilderSceneGUI` |
| `tests/unit/builder/test_builder_drag_drop_real.py` | `BuilderSceneGUI` |
| `tests/unit/builder/test_multi_selection_logic.py` | `BuilderSceneGUI` |
| `tests/repro_issues/test_bug_13_clear_removes_hull.py` | `BuilderSceneGUI`, `BuilderViewModel` |
| `tests/unit/builder/test_builder_data_loader.py` | `BuilderDataLoader` (8 imports) |
| `tests/unit/builder/test_builder_viewmodel.py` | `BuilderViewModel` |
| `tests/unit/services/test_ship_builder_service.py` | `ShipBuilderService`, `ShipBuilderResult` |

---

### 2. Method/Property Alias Usages

#### Fleet Warp Aliases (`game/strategy/data/fleet.py`)

| Alias | Canonical | Line | Usages Found |
|-------|-----------|------|--------------|
| `has_energy_for_warp()` | `has_resources_for_warp()` | 350-360 | **0 production, 3 test** (test_fleet.py only) |
| `consume_warp_energy()` | `consume_warp_resources()` | 392-403 | **0 production, 3 test** (test_fleet.py only) |

#### PathSegment Aliases (`game/strategy/engine/fleet_movement.py`)

| Alias | Canonical | Line | Usages Found |
|-------|-----------|------|--------------|
| `.hex` property | `.end` | 43-46 | **0 direct usages** (included in dict for backward compat) |
| `project_path_as_dicts()` | N/A | 307-314 | **1 production** (`pathfinding.py:227`), 5 test |

#### Ship Stats Alias (`game/simulation/entities/ship_stats.py`)

| Alias | Canonical | Line | Usages Found |
|-------|-----------|------|--------------|
| `to_hit_profile` | `total_defense_score` | 390 | **2 production** (ship_stats.py, ship.py:130), 1 test |

**Note:** `ship.py:130` declares `self.to_hit_profile: float = 1.0` - this is a property definition, not just an alias usage.

---

### 3. Singleton Accessor Alias Usages

| Class | File | Alias Line | Production Usages | Test Usages |
|-------|------|------------|-------------------|-------------|
| `ScreenshotManager` | `game/core/screenshot_manager.py` | 47 | 1 (`workshop_screen.py:88`) | 1 |
| `ShipThemeManager` | `game/simulation/ship_theme.py` | 44 | 2 (`game_renderer.py:42`, `workshop_screen.py:117`) | 7 |
| `SpriteManager` | `game/ui/renderer/sprites.py` | 47 | 2 (`app.py:111`, `workshop_screen.py:114`) | 1 |

**Total:** 5 production calls to `get_instance()`, 9 test calls

---

### 4. Deprecated Function Usages

#### `load_combat_strategies()` (`game/ai/strategy_manager.py:151-171`)

| File | Line | Type | Usage |
|------|------|------|-------|
| `game/ai/controller.py` | 55 | Re-export | Backward compat re-export |
| `game/ui/screens/workshop_data_loader.py` | 104, 168 | **Production call** | Actual function call |
| `simulation_tests/conftest.py` | 96 | Test setup | Function call |
| `tests/infrastructure/session_cache.py` | 65 | Test infra | Function call |
| `conftest.py` | 60 | Test fixture | Mocking |

#### TurnEngine Deprecated Methods

| Method | Lines | Status | Usages |
|--------|-------|--------|--------|
| `_execute_move_step()` | 261-287 | Emits DeprecationWarning | 1 test (`test_advanced_fleet_orders.py:127`) |
| `_calculate_next_hex()` | 250-259 | Backward compat wrapper | 1 internal, 5+ tests |
| `_spawn_ship()` | 211-217 | Backward compat wrapper | Delegates to production_engine |
| `_spawn_complex()` | 203-209 | Backward compat wrapper | Delegates to production_engine |

---

## Key Patterns to Reuse

- **Singleton Pattern**: `instance()` classmethod is the canonical accessor
- **Import Migration**: Update import, verify tests pass, delete shim
- **Test-First Validation**: Run specific test files after each change

---

## Dependencies & Risks

1. **BuilderSceneGUI is a Wrapper Class, not just an alias**
   - It provides a full delegation wrapper around `DesignWorkshopGUI`
   - Need to verify `DesignWorkshopGUI` has compatible interface
   - **Risk: Medium** - May need to update callers if interface differs

2. **`to_hit_profile` is declared in Ship class**
   - `ship.py:130` has `self.to_hit_profile: float = 1.0`
   - This may be intentional defensive property, not just an alias
   - **Risk: Low** - Need to verify this can be safely removed

3. **`load_combat_strategies()` is actively called in production**
   - `workshop_data_loader.py:168` calls this deprecated function
   - **Risk: Medium** - Need to understand lazy loading alternative

4. **`project_path_as_dicts()` is used in production pathfinding**
   - `pathfinding.py:227` calls this
   - **Risk: Low** - Need to update to use canonical method

5. **Test files heavily use deprecated names**
   - 12+ test files need import updates
   - **Risk: Low** - Straightforward find-replace

---

## Opportunities Discovered

1. **Clean separation achieved**: Most shims have very few production usages (1-2 files each)
2. **Test isolation**: Test usages are well-contained in specific test files
3. **Phased approach possible**: Can tackle each category independently
4. **Package-level cleanup**: `services/__init__.py` re-exports can be cleaned up after direct imports updated

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Questions for User

1. **BuilderSceneGUI Wrapper**: The `builder_screen.py` is not just an alias - it's a full wrapper class. Should we:
   - (A) Update callers to use `DesignWorkshopGUI` directly
   - (B) Keep the wrapper for API stability (defer to later phase)

2. **to_hit_profile Property**: `ship.py:130` declares this as a property. Is this intentional game mechanics or legacy cruft?

3. **load_combat_strategies() Replacement**: What should `workshop_data_loader.py` use instead? The docstring says "StrategyManager uses lazy loading" but we need to verify the replacement pattern.

4. **Test File Naming**: Should test files referencing "builder" be renamed to "workshop" as part of this phase, or is that out of scope?
