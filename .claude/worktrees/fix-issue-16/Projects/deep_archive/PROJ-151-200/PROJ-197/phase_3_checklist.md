# Phase 3: Battle UI Files [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate all battle-related UI files

---

## Tasks

### Task 3.1: Consolidate battle_panels.py [Medium]
**File:** `game/ui/panels/battle_panels.py` (38 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors` for all needed constants

Team colors:
- [x] Line ~118: `(100, 200, 255)` → `TEAM_1_TEXT`
- [x] Line ~123: `(40, 60, 80)` → `TEAM_1_BANNER_BG`
- [x] Line ~131: `(255, 100, 100)` → `TEAM_2_TEXT`
- [x] Line ~136: `(80, 40, 40)` → `TEAM_2_BANNER_BG`
- [x] Line ~506: `(100, 200, 255)` → `TEAM_1_TEXT`
- [x] Line ~508: `(255, 100, 100)` → `TEAM_2_TEXT`
- [x] Line ~510: `(200, 200, 200)` → `TEXT_ITEM`

Panel backgrounds/borders:
- [x] Line ~102: `(20, 25, 35)` → `BG_PANEL_DARK`
- [x] Line ~139: `(30, 30, 50)` → appropriate bg constant
- [x] Line ~141: `(60, 60, 80)` → `BORDER_PANEL`
- [x] Line ~307: `(20, 25, 35)` → `BG_PANEL_DARK`
- [x] Line ~310: `(60, 60, 80)` → `BORDER_PANEL`

Ship status:
- [x] Line ~153: `(200, 200, 200)` → `TEXT_ITEM`
- [x] Line ~155: `(100, 100, 100)` → `TEXT_DIM`
- [x] Line ~157: `(255, 165, 0)` → `STATUS_DERELICT`
- [x] Line ~158: `(40, 40, 40)` → `BAR_BG`

Seeker monitor:
- [x] Line ~321: `(255, 200, 100)` → `SEEKER_TITLE`
- [x] Line ~356: `(50, 255, 50)` → `STATUS_HIT_TEXT`
- [x] Lines ~358, ~362, ~366: `(40, 40, 40)` → `BAR_BG`
- [x] Line ~364: `(255, 50, 50)` → `STATUS_DESTROYED_TEXT`
- [x] Line ~368: `(255, 255, 100)` → `STATUS_ACTIVE_TEXT`
- [x] Line ~370: `(50, 50, 60)` → `STATUS_ACTIVE_BG`

Detail text:
- [x] Lines ~402, ~412, ~423: `(180, 180, 180)` → `TEXT_SECONDARY`
- [x] Line ~429: `(255, 150, 150)` → `DAMAGE_TEXT`
- [x] Line ~436: `(150, 200, 150)` → `TARGET_TEXT`

Buttons:
- [x] Lines ~340-341: clear button tuples → `BTN_DANGER_HOVER`, `BTN_DANGER_BG`, `BTN_DANGER_BORDER`
- [x] Line ~346: `(255, 150, 150)` → `BTN_DANGER_TEXT`
- [x] Lines ~381-383: close X button → appropriate constants
- [x] Lines ~529-531: victory button → `BTN_VICTORY_BG`, `BTN_VICTORY_BORDER`, `WHITE`
- [x] Lines ~557-559: end battle button → `BTN_END_BG`, `BTN_END_BORDER`, `BTN_END_TEXT`
- [x] Verify: `python -c "from game.ui.panels import battle_panels"`
- [x] Run `pytest tests/ --testmon`

**Notes:** All raw tuples replaced with constants from colors.py

### Task 3.2: Consolidate battle_screen.py [Simple]
**File:** `game/ui/screens/battle_screen.py` (~10 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add color imports
- [x] Replace `(10, 10, 20)` → `BG_BATTLE`
- [x] Replace `(255, 200, 50)` → `PROJECTILE_STANDARD`
- [x] Replace `(180, 180, 180)` → `HUD_TEXT`
- [x] Replace speed indicator tuples → `SPEED_PAUSED`, `SPEED_SLOWMO`, `SPEED_FAST`, `TEXT_ITEM`
- [x] Replace `(255, 50, 50)` → `HP_CRITICAL`
- [x] Replace remaining tuples
- [x] Run `pytest tests/ --testmon`

**Notes:** Added HUD_ZOOM_TEXT constant. All tuples replaced.

### Task 3.3: Consolidate battle_ui.py [Simple]
**File:** `game/ui/screens/battle_ui.py` (~15 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add color imports
- [x] Replace debug overlay tuples (target line, weapon range, aim point, firing arc)
- [x] Replace return button tuples → `BTN_RETURN_BG`, `BTN_RETURN_HOVER`, `WHITE`
- [x] Replace test result indicators → `TEST_PASS`, `TEST_FAIL`
- [x] Replace team victory/draw text colors
- [x] Run `pytest tests/ --testmon`

**Notes:** Added new constants: GRID_BG_BATTLE, DEBUG_TARGET_LINE, DEBUG_WEAPON_RANGE, DEBUG_AIM_POINT, DEBUG_FIRING_ARC, TEST_COMPLETE_PASSED/FAILED/NEUTRAL, RESULT_WIN, RESULT_DRAW

### Task 3.4: Consolidate battle_state_viewer.py [Simple]
**File:** `game/ui/screens/battle_state_viewer.py` (~9 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add color imports
- [x] Replace `WHITE` usages
- [x] Replace button bg/hover/border tuples
- [x] Replace diff legend tuples → `DIFF_CHANGED_BG/TEXT`, `DIFF_ADDED_BG/TEXT`, `DIFF_REMOVED_BG/TEXT`
- [x] Run `pytest tests/ --testmon`

**Notes:** Added VIEWER_BTN_BG, VIEWER_BTN_HOVER, VIEWER_BTN_BORDER constants

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Zero raw tuples in all 4 battle files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
