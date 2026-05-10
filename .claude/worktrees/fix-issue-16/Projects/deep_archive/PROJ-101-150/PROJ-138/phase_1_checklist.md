# Phase 1: Create SystemSelectionWindow

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-138 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the SystemSelectionWindow dialog class and its unit tests.

---

## Tasks

### Task 1.1: Create SystemSelectionWindow class [Medium]
**File:** `game/ui/screens/system_selection_window.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_system_selection_window.py`

- [x] Create file `game/ui/screens/system_selection_window.py`
- [x] Import dependencies: `pygame`, `pygame_gui`, `UIWindow`, `UISelectionList`, `UIButton`, `UILabel`, `hex_distance` from `game.core.hex_math`
- [x] Define `SystemSelectionWindow(UIWindow)` class with `__init__(self, rect, manager, systems, current_system, on_selection_callback)`
  - `systems`: list of StarSystem objects (already filtered by caller)
  - `current_system`: current StarSystem (for distance calculation)
  - `on_selection_callback`: called with `system_name: str` on confirm
- [x] In `__init__`: Build `display_name_to_system_name` dict mapping `"Name (dist: N)"` → `system.name`
- [x] In `__init__`: Sort `item_list` alphabetically by system name
- [x] In `__init__`: Create UILabel for header text ("Select Target System")
- [x] In `__init__`: Create UISelectionList with sorted display strings, scrollable
- [x] In `__init__`: Create "Confirm" UIButton (bottom-left)
- [x] In `__init__`: Create "Cancel" UIButton (bottom-right)
- [x] Implement `update(self, time_delta)`:
  - Call `super().update(time_delta)`
  - Check `btn_confirm.check_pressed()` → get selection → look up real name → call callback → `self.kill()`
  - Check `btn_cancel.check_pressed()` → `self.kill()` (no callback)
- [x] Verify: Window layout uses rect 450x500, labels and buttons positioned correctly

**Notes:** Implemented following PlanetSelectionWindow pattern. Button names: btn_confirm, btn_cancel.

### Task 1.2: Write unit tests for SystemSelectionWindow [Medium]
**File:** `tests/unit/ui/screens/test_system_selection_window.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_system_selection_window.py -v`

- [x] Create test file with mock fixtures for systems, current_system, pygame_gui manager
- [x] Test: `test_init_creates_window` — verify window initializes without error
- [x] Test: `test_systems_sorted_alphabetically` — verify list items are alphabetical
- [x] Test: `test_display_format_includes_distance` — verify `"Name (dist: N)"` format
- [x] Test: `test_confirm_calls_callback_with_system_name` — mock selection, verify callback receives actual system name (not display string)
- [x] Test: `test_cancel_does_not_call_callback` — press cancel, verify callback NOT called
- [x] Test: `test_confirm_without_selection_does_nothing` — no selection + confirm = no callback, no crash
- [x] Run tests: `pytest tests/unit/ui/screens/test_system_selection_window.py -v` — all pass

**Notes:** Added test_distance_calculation_correct for extra coverage. 7 tests total, all passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
