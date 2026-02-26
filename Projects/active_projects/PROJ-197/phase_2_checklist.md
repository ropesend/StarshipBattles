# Phase 2: Test Lab Renderer Fix [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace all 24 raw color tuples in renderer.py with theme.py or colors.py constants

---

## Tasks

### Task 2.1: Add Missing Constants to theme.py [Simple]
**File:** `game/ui/screens/test_lab/theme.py`
**Tests:** `pytest tests/ --testmon`

Constants needed by renderer.py that don't exist in theme.py yet:

- [ ] Add section `# === Seed Button States ===`
- [ ] Add `SEED_BUTTON_ACTIVE = (40, 80, 120)`
- [ ] Add `SEED_BUTTON_ACTIVE_BORDER = (80, 140, 200)`
- [ ] Add `SEED_BUTTON_ACTIVE_TEXT = (200, 220, 255)`
- [ ] Add `SEED_INPUT_HOVER_BG = (40, 50, 60)`
- [ ] Add `SEED_INPUT_HOVER_BORDER = (80, 100, 120)`
- [ ] Add section `# === Clear Filters Button ===`
- [ ] Add `CLEAR_BUTTON_BG = (60, 50, 50)`
- [ ] Add `CLEAR_BUTTON_HOVER = (80, 60, 60)`
- [ ] Add `CLEAR_BUTTON_BORDER = (120, 80, 80)`
- [ ] Add `CLEAR_BUTTON_TEXT = (255, 180, 180)`
- [ ] Add section `# === Progress Button State ===`
- [ ] Add `BUTTON_PROGRESS_BG = (80, 80, 50)`
- [ ] Add `BUTTON_PROGRESS_BORDER = (150, 150, 80)`
- [ ] Add `BUTTON_PROGRESS_TEXT = (255, 255, 150)`
- [ ] Add section `# === Headless Run Button ===`
- [ ] Add `BUTTON_HEADLESS_BG = (50, 50, 80)`
- [ ] Add `BUTTON_HEADLESS_HOVER = (70, 70, 100)`
- [ ] Add `BUTTON_HEADLESS_BORDER = (100, 100, 150)`
- [ ] Add `BUTTON_HEADLESS_TEXT = (200, 200, 255)`
- [ ] Add section `# === Visual Run Button ===`
- [ ] Add `BUTTON_RUN_BG = (50, 80, 50)`
- [ ] Add `BUTTON_RUN_HOVER = (70, 100, 70)`
- [ ] Add `BUTTON_RUN_BORDER = (100, 150, 100)`
- [ ] Add `BUTTON_RUN_TEXT = (200, 255, 200)`
- [ ] Add `TEXT_VERY_DIM = (120, 120, 120)` — very dim text for ticks/none

**Notes:**

### Task 2.2: Substitute in renderer.py [Simple]
**File:** `game/ui/screens/test_lab/renderer.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `from game.ui.colors import BLACK, TEST_PASS, TEST_FAIL` to imports (if not present)
- [ ] Line ~162: Replace `(40, 80, 120)` → `theme.SEED_BUTTON_ACTIVE`
- [ ] Line ~163: Replace `(80, 140, 200)` → `theme.SEED_BUTTON_ACTIVE_BORDER`
- [ ] Line ~164: Replace `(200, 220, 255)` → `theme.SEED_BUTTON_ACTIVE_TEXT`
- [ ] Line ~221: Replace `(40, 50, 60)` → `theme.SEED_INPUT_HOVER_BG`
- [ ] Line ~222: Replace `(80, 100, 120)` → `theme.SEED_INPUT_HOVER_BORDER`
- [ ] Line ~379: Replace `(80, 60, 60)` → `theme.CLEAR_BUTTON_HOVER`
- [ ] Line ~379: Replace `(60, 50, 50)` → `theme.CLEAR_BUTTON_BG`
- [ ] Line ~381: Replace `(120, 80, 80)` → `theme.CLEAR_BUTTON_BORDER`
- [ ] Line ~382: Replace `(255, 180, 180)` → `theme.CLEAR_BUTTON_TEXT`
- [ ] Line ~427: Replace `(80, 80, 50)` → `theme.BUTTON_PROGRESS_BG`
- [ ] Line ~428: Replace `(150, 150, 80)` → `theme.BUTTON_PROGRESS_BORDER`
- [ ] Line ~429: Replace `(255, 255, 150)` → `theme.BUTTON_PROGRESS_TEXT`
- [ ] Line ~569: Replace `(50, 80, 50)` / `(70, 100, 70)` → `theme.BUTTON_RUN_BG` / `theme.BUTTON_RUN_HOVER`
- [ ] Line ~571: Replace `(100, 150, 100)` → `theme.BUTTON_RUN_BORDER`
- [ ] Line ~572: Replace `(200, 255, 200)` → `theme.BUTTON_RUN_TEXT`
- [ ] Line ~584: Replace `(50, 50, 80)` / `(70, 70, 100)` → `theme.BUTTON_HEADLESS_BG` / `theme.BUTTON_HEADLESS_HOVER`
- [ ] Line ~586: Replace `(100, 100, 150)` → `theme.BUTTON_HEADLESS_BORDER`
- [ ] Line ~587: Replace `(200, 200, 255)` → `theme.BUTTON_HEADLESS_TEXT`
- [ ] Lines ~656, ~708, ~859: Replace `(120, 120, 120)` → `theme.TEXT_VERY_DIM`
- [ ] Line ~934: Replace `(100, 255, 150)` → `TEST_PASS` (normalize)
- [ ] Line ~936: Replace `(255, 100, 100)` → `TEST_FAIL` (normalize)
- [ ] Lines ~1026, ~1030: Replace `(0, 0, 0)` → `BLACK`
- [ ] Verify: `python -c "from game.ui.screens.test_lab import renderer"`

**Notes:**

### Task 2.3: Fix Remaining Test Lab Files [Simple]
**Files:** Other test_lab/ files with small tuple counts
**Tests:** `pytest tests/ --testmon`

- [ ] `test_run_details.py` (~8 tuples): Replace with theme/colors constants
- [ ] `component_dropdown.py` (~3 tuples): Replace with theme constants
- [ ] `json_viewer.py` (~3 tuples): Replace with theme constants
- [ ] `test_run_card.py` (~2 tuples): Replace with theme constants
- [ ] Run `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero raw tuples in test_lab/ files (excluding theme.py definitions)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
