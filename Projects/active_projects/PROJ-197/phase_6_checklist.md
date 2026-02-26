# Phase 6: Builder, Formation & Remaining Files [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate all remaining ~30 files

---

## Tasks

### Task 6.1: Builder Files [Simple]
**Tests:** `pytest tests/ --testmon`

**weapons_renderer.py** (18 tuples):
- [x] Replace weapon bar colors → `WEAPON_BAR_BEAM`, `WEAPON_BAR_PROJECTILE`, `WEAPON_BAR_SEEKER`
- [x] Replace accuracy colors → `WEAPON_ACCURACY_HIGH/MED/LOW`
- [x] Replace labels → `WEAPON_LABEL`, `WEAPON_RANGE_LABEL`, `WEAPON_ARC`
- [x] Replace background → `GRID_BG`
- [x] Handle damage gradient endpoints (kept as constants in class - explicit gradient values)

**detail_panel.py** (~2 tuples):
- [x] Replace with appropriate constants

**schematic_view.py** (~2 tuples):
- [x] Replace with appropriate constants (local module constants for arc colors)

- [x] Run `pytest tests/ --testmon`

**Notes:** Complete

### Task 6.2: Formation Editor [Simple]
**File:** `game/ui/screens/formation/renderer.py` (14 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Replace bg → `GRID_BG`
- [x] Replace grid → `FORMATION_GRID`
- [x] Replace axis → `FORMATION_AXIS`
- [x] Replace arrow colors → `FORMATION_ARROW`, `FORMATION_ARROW_SELECTED`
- [x] Replace fixed arrow → `FORMATION_FIXED`, `FORMATION_FIXED_SELECTED`
- [x] Replace `WHITE` and `BLACK`
- [x] Replace text colors → `TEXT_ITEM`
- [x] Replace toolbar bg → `BG_MENU`
- [x] Run `pytest tests/ --testmon`

**Notes:** Complete

### Task 6.3: Build Queue Files [Simple]
**Tests:** `pytest tests/ --testmon`

**build_queue_portraits.py** (17 tuples):
- [x] Replace vehicle type colors → `VEHICLE_SHIP/FIGHTER/STATION/COMPLEX`
- [x] Replace resource colors → `RESOURCE_METALS/ORGANICS/VAPORS/RADIOACTIVES/EXOTICS`
- [x] Replace `WHITE`, `TEXT_DIM`

**build_queue_drag_handler.py** (7 tuples):
- [x] Replace vehicle type colors → same constants
- [x] Replace fallback `(100, 100, 100)` → `TEXT_DIM`

**build_queue_renderer.py** (1 tuple):
- [x] Replace with `TEAM_1_TEXT`

- [x] Run `pytest tests/ --testmon`

**Notes:** Complete

### Task 6.4: Planet & Galaxy Test Files [Simple]
**Tests:** `pytest tests/ --testmon`

**planet_report_panel.py** (13 tuples):
- [x] Replace planet type colors → `PLANET_TERRESTRIAL/GAS_GIANT/ICE/ROCKY/OCEANIC`
- [x] Replace `WHITE`, `BLACK`, `TEXT_LIGHT`, `TEXT_DIM`

**galaxy_test/constants.py** (11 tuples):
- [x] Replace ALL planet colors → `PLANET_CONTINENTAL/ARID/PELAGIC/MAGMA/CRYO/BARREN/JOVIAN/ICE_GIANT/CHTHONIAN/ICE_DWARF/PLANETOID`

**galaxy_test/system_mode.py** (6 tuples):
- [x] Replace with `TEXT_LIGHT`, `TEXT_MUTED`, `FLEET_SELECTED`, `GRID_LINE`, `PLANET_TERRESTRIAL`

**galaxy_test/screen.py** (2 tuples):
- [x] Replace with `BG_GALAXY`, `PANEL_BG`

**galaxy_test/galaxy_mode.py** (2 tuples):
- [x] Replace with `WARP_LANE`, `STAR_LABEL`

- [x] Run `pytest tests/ --testmon`

**Notes:** Complete

### Task 6.5: Strategy & Research Files [Simple]
**Tests:** `pytest tests/ --testmon`

**strategy_screen.py** (1 tuple), **strategy_ui.py** (1 tuple), **fleet_data_source.py** (2 tuples):
- [x] Replace all with appropriate constants (`BG_BATTLE`, `WHITE`, `GRID_BG`, `BORDER_LIGHT`)

**research/research_scene.py** (3 tuples), **research/research_renderer.py** (1 tuple):
- [x] Replace all with appropriate constants (`BG_PANEL_DARK`, `BG_GALAXY`, `PANEL_BG`, `TEXT_MUTED`)

- [x] Run `pytest tests/ --testmon`

**Notes:** Complete

### Task 6.6: Design & Misc Files [Simple]
**Tests:** `pytest tests/ --testmon`

**design_image_helper.py** (7 tuples):
- [x] Does not exist in current codebase - removed from scope

**design_report_panel.py** (4 tuples):
- [x] Replace `WHITE`, `BLACK`, `TEXT_ITEM`

**keybindings_scene.py** (2), **menu_scene.py** (1), **new_game_setup_screen.py** (1), **workshop_viewmodel.py** (1):
- [x] Replace all with appropriate constants (`BG_PANEL_DARK`, `WHITE`, `BG_MENU`, `TEXT_ERROR`, `VEHICLE_DEFAULT`)

- [x] Run `pytest tests/ --testmon`

**Notes:** Complete - Added `TEXT_ERROR`, `VEHICLE_DEFAULT` constants

### Task 6.7: Utility & Component Files [Simple]
**Tests:** `pytest tests/ --testmon`

**utils/pygame_utils.py** (2), **components/table/virtual_table.py** (2):
- [x] Replace with appropriate constants (`TEXT_DIM`, `GRID_BG`, `TABLE_SELECTED`, `TABLE_UNSELECTED`)

**services/battle_ui_service.py** (1), **renderer/sprites.py** (0):
- [x] Replace with appropriate constants (`WHITE`). sprites.py had no raw tuples.

**renderer/game_renderer.py** (6 tuples):
- [x] Replace range circle, component, direction colors (`DEBUG_COLLISION`, `DEBUG_DIRECTION`, `OVERLAY_COMPONENT`, `OVERLAY_WEAPON`, `OVERLAY_PROPULSION`, `OVERLAY_ARMOR`)

**assets/ship_theme_manager.py** (3 tuples):
- [x] Replace with appropriate constants (`OVERLAY_FALLBACK`)

- [x] Run `pytest tests/` - 12734 passed

**Notes:** Complete - Added `TABLE_SELECTED`, `TABLE_UNSELECTED`, `DEBUG_COLLISION`, `DEBUG_DIRECTION`, `OVERLAY_COMPONENT`, `OVERLAY_WEAPON`, `OVERLAY_PROPULSION`, `OVERLAY_ARMOR`, `OVERLAY_FALLBACK` constants

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All remaining files consolidated
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
