# Phase 4: Setup & Strategy Files [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate setup and strategy screen files

---

## Tasks

### Task 4.1: Consolidate setup_renderer.py [Medium]
**File:** `game/ui/screens/setup_renderer.py` (40 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors` for all needed constants
- [ ] Replace title text `(200, 200, 255)` → `SETUP_TITLE`
- [ ] Replace section labels → `SETUP_LABEL_SHIPS`, `SETUP_LABEL_FORMATIONS`
- [ ] Replace ship item colors → `TEXT_ITEM`, `ITEM_BG`, `ITEM_BORDER`
- [ ] Replace formation item colors → `FORMATION_TEXT`, `FORMATION_BG`, `FORMATION_BORDER`
- [ ] Replace team formation colors → `FORMATION_TEAM_BG`, `FORMATION_TEAM_BORDER`
- [ ] Replace team 1 item colors → `TEAM_1_BG`, `TEAM_1_BORDER`
- [ ] Replace team 2 item colors → `TEAM_2_BG`, `TEAM_2_BORDER`
- [ ] Replace `(255, 255, 255)` → `WHITE`
- [ ] Replace load/save button colors → `BTN_NEUTRAL_BG`, `BTN_NEUTRAL_BORDER`, `BTN_NEUTRAL_TEXT`
- [ ] Replace AI dropdown → `DROPDOWN_BUTTON_BG`, `DROPDOWN_BUTTON_BORDER`, `DROPDOWN_BUTTON_TEXT`
- [ ] Replace begin battle button → `BTN_PRIMARY_BG`, `BTN_PRIMARY_BORDER`, `BTN_DISABLED_BG`, `WHITE`
- [ ] Replace return button → appropriate constants
- [ ] Replace clear all → `BTN_CLEAR_BG`, `BTN_CLEAR_BORDER`, `BTN_CLEAR_TEXT`
- [ ] Replace quick battle → `BTN_QUICK_BG`, `BTN_QUICK_BORDER`, `BTN_QUICK_TEXT`
- [ ] Replace dropdown overlay → `DROPDOWN_BG`, `BTN_NEUTRAL_BORDER`
- [ ] Verify: `python -c "from game.ui.screens import setup_renderer"`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 4.2: Consolidate setup_screen.py [Simple]
**File:** `game/ui/screens/setup_screen.py` (~3 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Replace screen background → `BG_PANEL_DARK`
- [ ] Replace team title colors → `TEAM_1_TEXT`, `TEAM_2_TEXT`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 4.3: Consolidate strategy_renderer.py [Medium]
**File:** `game/ui/screens/strategy_renderer.py` (28 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors`
- [ ] Replace `(255, 255, 255)` (8+ occurrences) → `WHITE`
- [ ] Replace `(50, 50, 100)` (2x) → `WARP_LANE`
- [ ] Replace `(200, 200, 200)` → `STAR_LABEL`
- [ ] Replace movement preview `(0, 255, 0)` → `HP_HEALTHY` (normalize)
- [ ] Replace storm tuples → `STORM_ION/PLASMA/GRAVITATIONAL/RADIATION/DARK_NEBULA`
- [ ] Replace fallback renders → `WARPPOINT_FALLBACK`, `DYSON_FALLBACK`, `PLANET_FALLBACK`
- [ ] Replace fleet selection → `FLEET_SELECTED`
- [ ] Replace paths → `PATH_MOVE`, `PATH_WARP`, `PATH_LABEL`
- [ ] Replace processing → `OVERLAY_PROCESSING`
- [ ] Replace remaining tuples
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 4.4: Consolidate strategy_widgets.py [Medium]
**File:** `game/ui/panels/strategy_widgets.py` (23 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors`
- [ ] Replace graph base colors (bg, border)
- [ ] Replace spectrum bands → `SPECTRUM_GAMMA` through `SPECTRUM_RADIO`
- [ ] Replace gas colors → `GAS_N2` through `GAS_SO2`, `GAS_UNKNOWN`
- [ ] Replace `(255, 255, 255)` → `WHITE`
- [ ] Replace `(200, 200, 200)` → `TEXT_ITEM`
- [ ] Replace `(100, 100, 100)` → `TEXT_DIM`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero raw tuples in all 4 files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
