# Phase 3: Battle UI Files [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate all battle-related UI files

---

## Tasks

### Task 3.1: Consolidate battle_panels.py [Medium]
**File:** `game/ui/panels/battle_panels.py` (38 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors` for all needed constants

Team colors:
- [ ] Line ~118: `(100, 200, 255)` → `TEAM_1_TEXT`
- [ ] Line ~123: `(40, 60, 80)` → `TEAM_1_BANNER_BG`
- [ ] Line ~131: `(255, 100, 100)` → `TEAM_2_TEXT`
- [ ] Line ~136: `(80, 40, 40)` → `TEAM_2_BANNER_BG`
- [ ] Line ~506: `(100, 200, 255)` → `TEAM_1_TEXT`
- [ ] Line ~508: `(255, 100, 100)` → `TEAM_2_TEXT`
- [ ] Line ~510: `(200, 200, 200)` → `TEXT_ITEM`

Panel backgrounds/borders:
- [ ] Line ~102: `(20, 25, 35)` → `BG_PANEL_DARK`
- [ ] Line ~139: `(30, 30, 50)` → appropriate bg constant
- [ ] Line ~141: `(60, 60, 80)` → `BORDER_PANEL`
- [ ] Line ~307: `(20, 25, 35)` → `BG_PANEL_DARK`
- [ ] Line ~310: `(60, 60, 80)` → `BORDER_PANEL`

Ship status:
- [ ] Line ~153: `(200, 200, 200)` → `TEXT_ITEM`
- [ ] Line ~155: `(100, 100, 100)` → `TEXT_DIM`
- [ ] Line ~157: `(255, 165, 0)` → `STATUS_DERELICT`
- [ ] Line ~158: `(40, 40, 40)` → `BAR_BG`

Seeker monitor:
- [ ] Line ~321: `(255, 200, 100)` → `SEEKER_TITLE`
- [ ] Line ~356: `(50, 255, 50)` → `STATUS_HIT_TEXT`
- [ ] Lines ~358, ~362, ~366: `(40, 40, 40)` → `BAR_BG`
- [ ] Line ~364: `(255, 50, 50)` → `STATUS_DESTROYED_TEXT`
- [ ] Line ~368: `(255, 255, 100)` → `STATUS_ACTIVE_TEXT`
- [ ] Line ~370: `(50, 50, 60)` → `STATUS_ACTIVE_BG`

Detail text:
- [ ] Lines ~402, ~412, ~423: `(180, 180, 180)` → `TEXT_SECONDARY`
- [ ] Line ~429: `(255, 150, 150)` → `DAMAGE_TEXT`
- [ ] Line ~436: `(150, 200, 150)` → `TARGET_TEXT`

Buttons:
- [ ] Lines ~340-341: clear button tuples → `BTN_DANGER_HOVER`, `BTN_DANGER_BG`, `BTN_DANGER_BORDER`
- [ ] Line ~346: `(255, 150, 150)` → `BTN_DANGER_TEXT`
- [ ] Lines ~381-383: close X button → appropriate constants
- [ ] Lines ~529-531: victory button → `BTN_VICTORY_BG`, `BTN_VICTORY_BORDER`, `WHITE`
- [ ] Lines ~557-559: end battle button → `BTN_END_BG`, `BTN_END_BORDER`, `BTN_END_TEXT`
- [ ] Verify: `python -c "from game.ui.panels import battle_panels"`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 3.2: Consolidate battle_screen.py [Simple]
**File:** `game/ui/screens/battle_screen.py` (~10 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add color imports
- [ ] Replace `(10, 10, 20)` → `BG_BATTLE`
- [ ] Replace `(255, 200, 50)` → `PROJECTILE_STANDARD`
- [ ] Replace `(180, 180, 180)` → `HUD_TEXT`
- [ ] Replace speed indicator tuples → `SPEED_PAUSED`, `SPEED_SLOWMO`, `SPEED_FAST`, `TEXT_ITEM`
- [ ] Replace `(255, 50, 50)` → `HP_CRITICAL`
- [ ] Replace remaining tuples
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 3.3: Consolidate battle_ui.py [Simple]
**File:** `game/ui/screens/battle_ui.py` (~15 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add color imports
- [ ] Replace debug overlay tuples (target line, weapon range, aim point, firing arc)
- [ ] Replace return button tuples → `BTN_RETURN_BG`, `BTN_RETURN_HOVER`, `WHITE`
- [ ] Replace test result indicators → `TEST_PASS`, `TEST_FAIL`
- [ ] Replace team victory/draw text colors
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 3.4: Consolidate battle_state_viewer.py [Simple]
**File:** `game/ui/screens/battle_state_viewer.py` (~9 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add color imports
- [ ] Replace `WHITE` usages
- [ ] Replace button bg/hover/border tuples
- [ ] Replace diff legend tuples → `DIFF_CHANGED_BG/TEXT`, `DIFF_ADDED_BG/TEXT`, `DIFF_REMOVED_BG/TEXT`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero raw tuples in all 4 battle files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
