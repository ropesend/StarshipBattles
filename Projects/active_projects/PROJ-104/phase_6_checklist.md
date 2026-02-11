# Phase 6: FormationEditorScreen.handle_event (CC 45 → ≤10)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract per-event-type handlers from the monolithic method

---

## Tasks

### Task 6.1: Extract `_handle_button_pressed(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

- [x] Move button if/elif chain (lines 526-556) into it
- [x] 14 button branches → single method
- [x] Verify tests

**Notes:** Done

### Task 6.2: Extract `_handle_slider_moved(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

- [x] Move slider handling (lines 558-567) into it
- [x] Verify tests

**Notes:** Done

### Task 6.3: Extract `_handle_text_entry(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

- [x] Move text entry handling (lines 569-586) into it
- [x] Verify tests

**Notes:** Done

### Task 6.4: Extract `_handle_mouse_button_down(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

- [x] Move MOUSEBUTTONDOWN handling (lines 602-619) into it
- [x] Includes canvas check, renumber arrow check, right-click pan, left-click delegation
- [x] Verify tests

**Notes:** Done

### Task 6.5: Refactor `handle_event` as dispatcher [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

- [x] `handle_event` becomes: process ui_manager → dispatch by event.type to `_handle_*`
- [x] Also extracted MOUSEWHEEL, KEYDOWN, MOUSEBUTTONUP handlers for CC reduction
- [x] handle_event now ~18 lines, CC = 9
- [x] Verify tests

**Notes:** Done — extracted 7 handlers total

### Task 6.6: Verify CC reduction [Simple]
- [x] Run `radon cc game/ui/screens/formation_editor.py -s -n C` — `handle_event` CC = 9 ≤ 10 ✅
- [x] Run full suite: `pytest tests/ -n 12 -q` — 8167 passed ✅

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `handle_event` CC ≤ 10 confirmed via radon
- [ ] All 8167 tests passing
- [ ] No public API changes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
