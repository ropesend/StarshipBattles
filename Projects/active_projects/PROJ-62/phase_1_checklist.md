# Phase 1: Extract Sidebar Builder

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-62 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract the 212-line `_init_sidebar()` method into `planet_list_sidebar.py`

---

## Tasks

### Task 1.1: Create `planet_list_sidebar.py` with `build_sidebar()` [Medium]
**File:** `game/ui/screens/planet_list_sidebar.py` (NEW)
**Tests:** `pytest tests/integration/ui/test_planet_list_window.py tests/repro_issues/`

- [ ] Create new file `game/ui/screens/planet_list_sidebar.py`
- [ ] Add imports: `pygame`, `pygame_gui` elements (UIPanel, UIScrollingContainer, UILabel, UIButton, UITextEntryLine, UIHorizontalSlider, UIDropDownMenu)
- [ ] Define `build_sidebar(manager, sidebar_panel, sidebar_width, rect_height, planet_ranges, columns, preset_manager)` function
- [ ] Move the entire body of `_init_sidebar()` (lines 251-462 of planet_list_window.py) into `build_sidebar()`
- [ ] Replace `self.ui_manager` with `manager` parameter
- [ ] Replace `self.sidebar_width` with `sidebar_width` parameter
- [ ] Replace `self.rect.height` with `rect_height` parameter
- [ ] Replace `self._planet_ranges` with `planet_ranges` parameter
- [ ] Replace `self.columns` with `columns` parameter
- [ ] Replace `self.preset_manager` with `preset_manager` parameter
- [ ] Return dict of all widget references needed by the main window

### Task 1.2: Update `PlanetListWindow` to use `build_sidebar()` [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/integration/ui/test_planet_list_window.py tests/repro_issues/`

- [ ] Add import: `from game.ui.screens.planet_list_sidebar import build_sidebar`
- [ ] Replace `self._init_sidebar()` call (line 105) with call to `build_sidebar()` and unpack returned dict into instance attributes
- [ ] Delete entire `_init_sidebar()` method (lines 251-462)
- [ ] Verify no remaining references to `_init_sidebar`

### Task 1.3: Verify Phase 1 [Simple]
**Tests:** `pytest tests/`

- [ ] Run full test suite - all 6248 tests pass
- [ ] Verify `planet_list_window.py` line count reduced by ~200 lines (target: ~920-940 lines)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
