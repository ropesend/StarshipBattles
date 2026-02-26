# Phase 6: Builder, Formation & Remaining Files [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate all remaining ~30 files

---

## Tasks

### Task 6.1: Builder Files [Simple]
**Tests:** `pytest tests/ --testmon`

**weapons_renderer.py** (18 tuples):
- [ ] Replace weapon bar colors → `WEAPON_BAR_BEAM`, `WEAPON_BAR_PROJECTILE`, `WEAPON_BAR_SEEKER`
- [ ] Replace accuracy colors → `WEAPON_ACCURACY_HIGH/MED/LOW`
- [ ] Replace labels → `WEAPON_LABEL`, `WEAPON_RANGE_LABEL`, `WEAPON_ARC`
- [ ] Replace background → `GRID_BG`
- [ ] Handle damage gradient endpoints

**detail_panel.py** (~2 tuples):
- [ ] Replace with appropriate constants

**schematic_view.py** (~2 tuples):
- [ ] Replace with appropriate constants

- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 6.2: Formation Editor [Simple]
**File:** `game/ui/screens/formation/renderer.py` (14 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Replace bg → `GRID_BG`
- [ ] Replace grid → `FORMATION_GRID`
- [ ] Replace axis → `FORMATION_AXIS`
- [ ] Replace arrow colors → `FORMATION_ARROW`, `FORMATION_ARROW_SELECTED`
- [ ] Replace fixed arrow → `FORMATION_FIXED`, `FORMATION_FIXED_SELECTED`
- [ ] Replace `WHITE` and `BLACK`
- [ ] Replace text colors → `TEXT_ITEM`
- [ ] Replace toolbar bg
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 6.3: Build Queue Files [Simple]
**Tests:** `pytest tests/ --testmon`

**build_queue_portraits.py** (17 tuples):
- [ ] Replace vehicle type colors → `VEHICLE_SHIP/FIGHTER/STATION/COMPLEX`
- [ ] Replace resource colors → `RESOURCE_METALS/ORGANICS/VAPORS/RADIOACTIVES/EXOTICS`
- [ ] Replace `WHITE`, `TEXT_DIM`

**build_queue_drag_handler.py** (7 tuples):
- [ ] Replace vehicle type colors → same constants
- [ ] Replace fallback `(100, 100, 100)` → `TEXT_DIM`

**build_queue_renderer.py** (1 tuple):
- [ ] Replace with appropriate constant

- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 6.4: Planet & Galaxy Test Files [Simple]
**Tests:** `pytest tests/ --testmon`

**planet_report_panel.py** (13 tuples):
- [ ] Replace planet type colors → `PLANET_TERRESTRIAL/GAS_GIANT/ICE/ROCKY/OCEANIC`
- [ ] Replace `WHITE`, `BLACK`, `TEXT_ITEM`, `TEXT_DIM`

**galaxy_test/constants.py** (11 tuples):
- [ ] Replace ALL planet colors → `PLANET_CONTINENTAL/ARID/PELAGIC/MAGMA/CRYO/BARREN/JOVIAN/ICE_GIANT/CHTHONIAN/ICE_DWARF/PLANETOID`

**galaxy_test/system_mode.py** (6 tuples):
- [ ] Replace with appropriate constants

**galaxy_test/screen.py** (2 tuples):
- [ ] Replace with appropriate constants

**galaxy_test/galaxy_mode.py** (2 tuples):
- [ ] Replace with appropriate constants

- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 6.5: Strategy & Research Files [Simple]
**Tests:** `pytest tests/ --testmon`

**strategy_screen.py** (1 tuple), **strategy_ui.py** (1 tuple), **fleet_data_source.py** (2 tuples):
- [ ] Replace all with appropriate constants

**research/research_scene.py** (3 tuples), **research/research_renderer.py** (1 tuple):
- [ ] Replace all with appropriate constants

- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 6.6: Design & Misc Files [Simple]
**Tests:** `pytest tests/ --testmon`

**design_image_helper.py** (7 tuples):
- [ ] Replace vehicle type colors → `VEHICLE_SHIP/FIGHTER`, etc.
- [ ] Replace text/border → `TEXT_ITEM`, `TEXT_DIM`

**design_report_panel.py** (4 tuples):
- [ ] Replace `WHITE`, `BLACK`, `TEXT_ITEM`

**keybindings_scene.py** (2), **menu_scene.py** (1), **new_game_setup_screen.py** (1), **workshop_viewmodel.py** (1):
- [ ] Replace all with appropriate constants

- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 6.7: Utility & Component Files [Simple]
**Tests:** `pytest tests/ --testmon`

**utils/pygame_utils.py** (2), **components/table/virtual_table.py** (2):
- [ ] Replace with appropriate constants

**services/battle_ui_service.py** (1), **renderer/sprites.py** (1):
- [ ] Replace with appropriate constants

**renderer/game_renderer.py** (6 tuples):
- [ ] Replace range circle, component, direction colors

**assets/ship_theme_manager.py** (3 tuples):
- [ ] Replace with appropriate constants

- [ ] Run `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All remaining files consolidated
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
