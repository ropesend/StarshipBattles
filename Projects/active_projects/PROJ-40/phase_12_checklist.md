# Phase 12: UI Layer Remediation (Consolidated)

**Status:** Not Started
**Estimated Effort:** 12-16 hours
**Priority:** Final Phase - Complete all other phases first

## Overview

Consolidated UI layer cross-import violations from Phase 1.3 and Phase 7.
- **37 files** with cross-layer imports
- **124 total imports** (71 top-level + 53 runtime)
- Includes TYPE_CHECKING conversions, DI refactoring, and code quality fixes

---

## Tier 1: Easy Wins (2-3 hours)

### 12.1 strategy_input_handler.py
**Location:** `game/ui/screens/strategy_input_handler.py`
**Violations:** 2 imports (pixel_to_hex, Fleet)
**Approach:** TYPE_CHECKING for Fleet

- [ ] Move Fleet import to TYPE_CHECKING block
- [ ] Use string annotation 'Fleet' in type hints
- [ ] Keep pixel_to_hex as runtime (pure utility function)
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.2 build_queue_screen.py
**Location:** `game/ui/screens/build_queue_screen.py`
**Violations:** 3 imports (Planet, DesignLibrary, SimulationDesignLoader)
**Approach:** TYPE_CHECKING + DI

- [ ] Move Planet to TYPE_CHECKING block
- [ ] Inject DesignLibrary via constructor
- [ ] Inject SimulationDesignLoader via constructor
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.3 fleet_report_filters.py
**Location:** `game/ui/screens/fleet_report_filters.py`
**Violations:** 2 imports
**Approach:** DI pattern

- [ ] Review current imports
- [ ] Apply DI pattern for services
- [ ] Run: `pytest tests/unit/ui/ -v`

---

## Tier 2: Medium Complexity (6-8 hours)

### 12.4 workshop_viewmodel.py
**Location:** `game/ui/screens/workshop_viewmodel.py`
**Violations:** 3 imports (Ship, Component, VehicleDesignService)
**Approach:** TYPE_CHECKING + DI

- [ ] Move Ship, Component to TYPE_CHECKING
- [ ] Inject VehicleDesignService via constructor parameter
- [ ] Update string annotations in type hints
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.5 new_game_setup_screen.py
**Location:** `game/ui/screens/new_game_setup_screen.py`
**Violations:** 3 imports (GameConfig, RaceConfig, RaceLibrary)
**Approach:** DI for RaceLibrary

- [ ] Move RaceConfig to TYPE_CHECKING if type-only
- [ ] Inject RaceLibrary via constructor
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.6 ship_stats_renderer.py
**Location:** `game/ui/panels/ship_stats_renderer.py`
**Violations:** 2 imports (ComponentStatus, StrategyManager)
**Approach:** Constants extraction or DI

- [ ] Consider extracting ComponentStatus to core/constants
- [ ] Inject StrategyManager via constructor
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.7 strategy_scene.py
**Location:** `game/ui/screens/strategy_scene.py`
**Violations:** 5+ imports (StarSystem, Fleet, SaveGameService, etc.)
**Approach:** Mixed TYPE_CHECKING + DI

- [ ] Move data types (StarSystem, Fleet) to TYPE_CHECKING
- [ ] Inject SaveGameService, StrategySessionFacade
- [ ] Keep hex_to_pixel as runtime utility
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.8 battle_scene.py
**Location:** `game/ui/screens/battle_scene.py`
**Violations:** 2 imports (AIController, BattleService)
**Approach:** DI validation

- [ ] Verify BattleOrchestrator pattern
- [ ] Inject BattleService via constructor
- [ ] Run: `pytest tests/unit/ui/ -v`

---

## Tier 3: Hard Cases (4-5 hours)

### 12.9 workshop_screen.py
**Location:** `game/ui/screens/workshop_screen.py`
**Violations:** 5 imports
**Approach:** Extract SharedWorkshopService

- [ ] Create SharedWorkshopService abstraction
- [ ] Consolidate design loading services
- [ ] Inject via constructor
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.10 builder/main.py
**Location:** `game/ui/screens/builder/main.py`
**Violations:** 3 imports (Ship, Component, ShipIO)
**Approach:** Architectural review

- [ ] Document why Ship instantiation may be acceptable
- [ ] If refactoring: Create ShipBuilderService
- [ ] If accepting: Document as architectural exception
- [ ] Run: `pytest tests/unit/ui/ -v`

---

## Remaining Files Summary (27 files)

The following files need review using the same patterns:

### Simulation Layer (14 files):
- [ ] hud/panels.py
- [ ] panels/design_report_panel.py
- [ ] panels/ship_detail_panel.py
- [ ] renderer/game_renderer.py
- [ ] renderer/renderer.py
- [ ] builder/detail_panel.py
- [ ] builder/layer_panel.py
- [ ] builder/legacy_components.py
- [ ] builder/modifier_logic.py
- [ ] builder/right_panel.py
- [ ] builder/schematic_view.py
- [ ] builder/stats_config.py
- [ ] setup.py / setup_data_io.py / setup_screen.py
- [ ] workshop_event_router.py

### Strategy Layer (16 files):
- [ ] design_selector_window.py
- [ ] fleet_orders_window.py
- [ ] race_setup_screen.py
- [ ] strategy_camera_nav.py
- [ ] strategy_colonization.py
- [ ] strategy_detail_fmt.py
- [ ] strategy_fleet_ops.py
- [ ] strategy_renderer.py
- [ ] strategy_screen.py
- [ ] (remaining strategy imports)

### AI Layer (7 files):
- [ ] orchestration/battle_orchestrator.py
- [ ] setup_renderer.py
- [ ] (remaining AI imports)

---

## Phase 7 Tasks (Moved Here)

### 12.11 FormationEditor Type Hints (NEW-UI-005)
**Location:** `game/ui/screens/formation_editor.py`
**Effort:** Medium

- [ ] Add type hints to 42 methods
- [ ] Focus on public API
- [ ] Run mypy if available

---

### 12.12 Bare Exception Fixes (NEW-UI-008)
**Location:** `game/ui/screens/formation_editor.py:525,533`
**Effort:** Simple

- [ ] Replace `except:` with `except ValueError as e:`
- [ ] Add logging for debugging
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.13 Fragile Path Construction (NEW-UI-009)
**Location:** `game/ui/screens/test_lab.py:38`
**Effort:** Simple

- [ ] Replace nested `os.path.dirname()` with pathlib
- [ ] Use `Path(__file__).parents[4]` or similar
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.14 tkinter Exception Handling (NEW-UI-011)
**Location:** `game/ui/screens/builder/main.py:34-39`
**Effort:** Simple

- [ ] Replace bare `except:` with `except tk.TclError as e:`
- [ ] Add logging for debugging
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.15 UI Layout Constants (NEW-UI-012)
**Location:** Multiple files (837 instances)
**Effort:** Medium (partial implementation)

- [ ] Create `game/ui/config.py` with UILayoutConfig dataclass
- [ ] Migrate 10-20 most-used constants as proof of concept
- [ ] Document pattern for future migrations
- [ ] Run: `pytest tests/unit/ui/ -v`

---

### 12.16 RaceSetupScreen Planning (NEW-UI-014)
**Location:** `game/ui/screens/race_setup_screen.py` (1,227 lines)
**Effort:** Medium (planning only)

- [ ] Document current responsibilities (1,227 lines, 36 methods)
- [ ] Identify extraction candidates:
  - [ ] `TabManager` class
  - [ ] `ColorPickerPanel` class
- [ ] Add decomposition plan to `decisions.md`
- [ ] Extract ONE component as proof of concept

---

### 12.17 ComponentRef Pattern (NEW-UI-015)
**Location:** Multiple builder files
**Effort:** Simple

- [ ] Create `ComponentRef` dataclass with explicit fields
- [ ] Define standard pattern for component references
- [ ] Document usage in builder README or comments
- [ ] Update 2-3 files to use new pattern as example

---

### 12.18 Schematic Cache Key (NEW-UI-016)
**Location:** `game/ui/screens/builder/schematic_view.py:123-176`
**Effort:** Medium

- [ ] Include weapon stats in cache key, not just ID
- [ ] Or invalidate cache when weapon is modified
- [ ] Add test for cache invalidation on modifier change
- [ ] Run: `pytest tests/unit/ui/ -v`

---

## Verification

- [ ] Run all UI tests: `pytest tests/unit/ui/ -v`
- [ ] Manual verification of UI screens
- [ ] Verify no circular imports: `python -c "import game.ui"`
- [ ] Test key workflows: builder, workshop, strategy scene

---

## Notes

- Complete Phases 1-6 and 8-11 before starting this phase
- This phase can be split into multiple sessions
- Tier 1 tasks are quick wins - start there
- Tier 3 tasks may require architectural decisions - document in `decisions.md`
- Consider creating PROJ-4X for remaining work if scope exceeds estimate
