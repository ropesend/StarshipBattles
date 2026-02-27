# Phase 4: Setup & Strategy Files [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate setup and strategy screen files

---

## Tasks

### Task 4.1: Consolidate setup_renderer.py [Medium]
**File:** `game/ui/screens/setup_renderer.py` (40 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors` for all needed constants
- [x] Replace title text `(200, 200, 255)` → `SETUP_TITLE`
- [x] Replace section labels → `SETUP_LABEL_SHIPS`, `SETUP_LABEL_FORMATIONS`
- [x] Replace ship item colors → `TEXT_ITEM`, `ITEM_BG`, `ITEM_BORDER`
- [x] Replace formation item colors → `FORMATION_TEXT`, `FORMATION_BG`, `FORMATION_BORDER`
- [x] Replace team formation colors → `FORMATION_TEAM_BG`, `FORMATION_TEAM_BORDER`
- [x] Replace team 1 item colors → `TEAM_1_BG`, `TEAM_1_BORDER`
- [x] Replace team 2 item colors → `TEAM_2_BG`, `TEAM_2_BORDER`
- [x] Replace `(255, 255, 255)` → `WHITE`
- [x] Replace load/save button colors → `BTN_NEUTRAL_BG`, `BTN_NEUTRAL_BORDER`, `BTN_NEUTRAL_TEXT`
- [x] Replace AI dropdown → `DROPDOWN_BUTTON_BG`, `DROPDOWN_BUTTON_BORDER`, `DROPDOWN_BUTTON_TEXT`
- [x] Replace begin battle button → `BTN_PRIMARY_BG`, `BTN_PRIMARY_BORDER`, `BTN_DISABLED_BG`, `WHITE`
- [x] Replace return button → appropriate constants
- [x] Replace clear all → `BTN_CLEAR_BG`, `BTN_CLEAR_BORDER`, `BTN_CLEAR_TEXT`
- [x] Replace quick battle → `BTN_QUICK_BG`, `BTN_QUICK_BORDER`, `BTN_QUICK_TEXT`
- [x] Replace dropdown overlay → `DROPDOWN_BG`, `BTN_NEUTRAL_BORDER`
- [x] Verify: `python -c "from game.ui.screens import setup_renderer"`
- [x] Run `pytest tests/ --testmon`

**Notes:** All ~25 raw tuples replaced with named constants

### Task 4.2: Consolidate setup_screen.py [Simple]
**File:** `game/ui/screens/setup_screen.py` (~3 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Replace screen background → `BG_PANEL_DARK`
- [x] Replace team title colors → `TEAM_1_TEXT`, `TEAM_2_TEXT`
- [x] Run `pytest tests/ --testmon`

**Notes:** All 3 raw tuples replaced

### Task 4.3: Consolidate strategy_renderer.py [Medium]
**File:** `game/ui/screens/strategy_renderer.py` (28 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors`
- [x] Replace `(255, 255, 255)` (8+ occurrences) → `WHITE`
- [x] Replace `(50, 50, 100)` (2x) → `WARP_LANE`
- [x] Replace `(200, 200, 200)` → `STAR_LABEL`
- [x] Replace movement preview `(0, 255, 0)` → `HP_HEALTHY` (normalize)
- [x] Replace storm tuples → `STORM_ION/PLASMA/GRAVITATIONAL/RADIATION/DARK_NEBULA`
- [x] Replace fallback renders → `WARPPOINT_FALLBACK`, `DYSON_FALLBACK`, `PLANET_FALLBACK`
- [x] Replace fleet selection → `FLEET_SELECTED`
- [x] Replace paths → `PATH_MOVE`, `PATH_WARP`, `PATH_LABEL`
- [x] Replace processing → `OVERLAY_PROCESSING`
- [x] Replace remaining tuples
- [x] Run `pytest tests/ --testmon`

**Notes:** All ~25 raw tuples replaced. Storm tints now use + (80,) for RGBA.

### Task 4.4: Consolidate strategy_widgets.py [Medium]
**File:** `game/ui/panels/strategy_widgets.py` (23 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors`
- [x] Replace graph base colors (bg, border)
- [x] Replace spectrum bands → `SPECTRUM_GAMMA` through `SPECTRUM_RADIO`
- [x] Replace gas colors → `GAS_N2` through `GAS_SO2`, `GAS_UNKNOWN`
- [x] Replace `(255, 255, 255)` → `WHITE`
- [x] Replace `(200, 200, 200)` → `TEXT_ITEM`
- [x] Replace `(100, 100, 100)` → `TEXT_DIM`
- [x] Run `pytest tests/ --testmon`

**Notes:** All ~23 raw tuples replaced. BANDS and GAS_COLORS now use named constants.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Zero raw tuples in all 4 files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
