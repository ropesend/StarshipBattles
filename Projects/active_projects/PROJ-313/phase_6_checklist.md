# Phase 6: Promote move_choice_window to Named Subclass

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** The `move_choice_window` is currently constructed as an inline `pygame_gui.UIWindow(...)` in `move_choice_dialog.py:48` and tracked via the legacy slot field. Promote it to a named `MoveChoiceWindow(StrategyModalWindow)` subclass so it follows the structural contract uniformly with all other modal windows.

---

## Tasks

### Task 6.1: Create `MoveChoiceWindow` class [Simple]
**File:** `game/ui/screens/strategy_windows/move_choice_dialog.py` (line 48 area)
**Tests:** `pytest tests/unit/ui/screens/strategy_windows/test_move_choice_dialog.py` (or wherever existing tests for this dialog live; search if needed)

- [ ] Locate the inline `pygame_gui.UIWindow(...)` construction at line 48
- [ ] Extract a class definition above the function:
  ```python
  class MoveChoiceWindow(StrategyModalWindow):
      """Modal window prompting the user to choose a move/join action target."""
      pass  # All behaviour lives in the constructor args; no overrides needed.
  ```
  Or, if the inline construction passes title / rect / manager kwargs, replicate them in the new class's `__init__` and accept the same params.
- [ ] Add import for `StrategyModalWindow`
- [ ] Replace the inline `pygame_gui.UIWindow(...)` call with `MoveChoiceWindow(window_manager=..., ...)` passing the existing kwargs plus the new `window_manager` keyword
- [ ] Existing button callbacks (`lambda: (on_move_sector(), win.kill())`) work unchanged — `kill()` now also handles deregistration via the base class
**Notes:**

### Task 6.2: Migrate slot tracking [Simple]
**File:** `game/ui/screens/strategy_window_manager.py` and `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_event_router.py`

- [ ] Delete `move_choice_window: Optional[UIWindow] = None` slot field on `StrategyWindowManager`
- [ ] Delete the slot's clause from `has_modal_open()`
- [ ] Delete the slot's clause from `_is_blocking_ui_element_at()`
- [ ] Delete the `event.ui_element == wm.move_choice_window` branch from `_handle_window_close` (around line 437)
- [ ] Update any direct assignments to `wm.move_choice_window = win` in `move_choice_dialog.py` — they're no longer needed (the base class handles registration)
**Notes:**

### Task 6.3: Phase verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] `MoveChoiceWindow` is a `StrategyModalWindow` subclass and registers itself
- [ ] Router scans no longer reference `move_choice_window`
- [ ] `_handle_window_close` no longer has a branch for it
- [ ] Full sharded suite still 15893 passing
- [ ] Manual smoke: trigger a move-choice scenario in-game (right-click a sector with multiple targets), verify the dialog opens, click an option, verify the dialog closes and `has_modal_open()` returns False
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7 (Migrate untracked editor windows)
