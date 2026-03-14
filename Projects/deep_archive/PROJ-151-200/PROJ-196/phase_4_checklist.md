# Phase 4: Test Lab Theme Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace inline color tuples in all 9 Test Lab files with `theme.*` constants.

---

## Tasks

### Task 4.1: Update renderer.py to use theme [Medium]
**File:** `game/ui/screens/test_lab/renderer.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace 8 class-level constants (lines 31-38):
  - `BG_COLOR = (20, 20, 25)` → `BG_COLOR = theme.BG_PRIMARY`
  - `PANEL_BG = (25, 25, 30)` → `PANEL_BG = theme.BG_PANEL`
  - `BORDER_COLOR = (80, 80, 90)` → `BORDER_COLOR = theme.BORDER`
  - `TEXT_COLOR = (220, 220, 220)` → `TEXT_COLOR = theme.TEXT`
  - `HEADER_COLOR = (100, 200, 255)` → `HEADER_COLOR = theme.TEXT_HEADER`
  - `SELECTED_COLOR = (0, 100, 200)` → `SELECTED_COLOR = theme.SELECTED_BG`
  - `HOVER_COLOR = (150, 150, 150)` → `HOVER_COLOR = theme.TEXT_DIM`
  - `CATEGORY_BG = (35, 35, 40)` → `CATEGORY_BG = theme.BG_CATEGORY`
- [x] Replace inline tuples matching theme constants throughout methods
- [x] Run tests

**Notes:** Migrated ~40 inline color tuples to theme constants including seed colors, tag filter colors, status colors, section header colors, buttons, scrollbars, and more.

---

### Task 4.2: Update test_run_details.py to use theme [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace instance color attributes (lines 23-30):
  - `self.bg_color = (30, 30, 35)` → `theme.BG_CONTENT`
  - `self.border_color = (80, 80, 90)` → `theme.BORDER`
  - `self.text_color = (220, 220, 220)` → `theme.TEXT`
  - `self.header_color = (150, 200, 255)` → `theme.TEXT_HEADER`
  - `self.button_color` → `theme.BUTTON_BLUE`
  - `self.button_hover_color` → `theme.BUTTON_BLUE_HOVER`
- [x] Replace inline tuples: `(140, 140, 160)` → `theme.TEXT_LABEL`, `(180, 200, 255)` → `theme.TEXT_EXPECTED`, etc.
- [x] Run tests

**Notes:** Migrated ~20 inline color tuples.

---

### Task 4.3: Update test_run_card.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/test_run_card.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace instance color attributes:
  - `self.bg_color = (35, 35, 40)` → `theme.BG_CATEGORY`
  - `self.text_color = (220, 220, 220)` → `theme.TEXT`
  - `self.border_color = (100, 100, 120)` → `theme.BORDER_ACTIVE`
  - `self.border_selected_color = (100, 150, 255)` → `theme.SELECTED_BORDER`
- [x] Replace inline `(140, 140, 160)` → `theme.TEXT_LABEL`, `(180, 200, 255)` → `theme.TEXT_EXPECTED`
- [x] Run tests

**Notes:** Migrated ~12 inline color tuples.

---

### Task 4.4: Update ship_panels.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/ship_panels.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace 7 instance color attributes:
  - `self.bg_color` → `theme.BG_CONTENT`
  - `self.border_color` → `theme.BORDER`
  - `self.header_color` → `theme.TEXT_HEADER`
  - `self.tab_color` → `theme.TAB_NORMAL`
  - `self.tab_selected_color` → `theme.TAB_SELECTED`
  - `self.tab_hover_color` → `theme.TAB_HOVER`
  - `self.text_color` → `theme.TEXT`
- [x] Run tests

**Notes:**

---

### Task 4.5: Update json_viewer.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/json_viewer.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace instance colors:
  - `self.bg_color = (30, 30, 35)` → `theme.BG_CONTENT`
  - `self.text_color = (220, 220, 220)` → `theme.TEXT`
  - `self.title_color = (255, 255, 255)` → `theme.TEXT_WHITE`
  - `self.border_color = (100, 100, 120)` → `theme.BORDER_ACTIVE`
- [x] Run tests

**Notes:**

---

### Task 4.6: Update results_panel.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/results_panel.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace instance colors:
  - `self.bg_color` → `theme.BG_CONTENT`
  - `self.border_color` → `theme.BORDER_ACTIVE`
  - `self.title_color` → `theme.TEXT_WHITE`
  - `self.button_color` → `theme.BUTTON_BLUE`
  - `self.button_hover_color` → `theme.BUTTON_BLUE_HOVER`
- [x] Replace inline scrollbar color → `theme.SCROLLBAR_THUMB`
- [x] Run tests

**Notes:**

---

### Task 4.7: Update component_dropdown.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/component_dropdown.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace: `self.text_color` → `theme.TEXT_WHITE`, `self.border_color` → `theme.BORDER_ACTIVE`
- [x] Run tests

**Notes:** `self.bg_color = (50, 50, 60)` is unique to dropdown — replaced with theme.TAG_NORMAL_BG.

---

### Task 4.8: Update dialogs.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/dialogs.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace inline colors:
  - `(30, 30, 35)` → `theme.BG_CONTENT`
  - `(100, 100, 120)` → `theme.BORDER_ACTIVE`
  - `(220, 220, 220)` → `theme.TEXT`
  - `(150, 200, 255)` → `theme.TEXT_HEADER`
  - `(255, 100, 100)` → `theme.STATUS_FAIL`
  - `(100, 255, 150)` → `theme.SECTION_OUTCOME`
- [x] Run tests

**Notes:**

---

### Task 4.9: Update screen.py to use theme [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -v`

- [x] Add `from game.ui.screens.test_lab import theme`
- [x] Replace `_render_progress` colors:
  - `(40, 40, 45)` → `theme.BG_OVERLAY`
  - `(100, 100, 120)` → `theme.BORDER_ACTIVE`
  - `(255, 255, 255)` → `theme.TEXT_WHITE`
  - `(200, 200, 200)` → `theme.TEXT_MUTED`
  - `(150, 150, 150)` → `theme.TEXT_DIM`
  - `(20, 20, 25)` → `theme.BG_PRIMARY`
- [x] Run tests

**Notes:**

---

### Task 4.10: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All 12,734 tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
