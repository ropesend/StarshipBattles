# Phase 2: Fix Click Gate

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-216 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the overly broad `get_hovering_any_element()` check with a targeted check that only blocks clicks when actual modal windows or interactive overlays are under the cursor.

---

## Tasks

### Task 2.1: Replace `get_hovering_any_element()` with explicit window check [Medium]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`

- [ ] Replace the current click gate logic (lines 269-272) with explicit modal/window checks:
  ```python
  def handle_click(self, mx: int, my: int, button: int) -> bool:
      # 1. Check logical sidebar area
      if mx > self.ui.width - self.ui.sidebar_width:
          return True

      # 2. Check if mouse is over an active modal/window that should block map clicks
      if self._is_blocking_ui_element_at(mx, my):
          return True

      return False
  ```
- [ ] Add `_is_blocking_ui_element_at()` method to StrategyEventRouter:
  ```python
  def _is_blocking_ui_element_at(self, mx: int, my: int) -> bool:
      """Check if a blocking UI element (modal window, menu panel) is at the given position.

      Only actual interactive overlays should block map clicks - NOT hidden buttons,
      container panels, or decorative elements.
      """
      wm = self.ui.window_manager
      # Check active windows that should block clicks
      blocking_windows = [
          wm.fleet_orders_window,
          wm.planet_list_window,
          wm._pending_confirmation_dialog,
      ]
      for window in blocking_windows:
          if window is not None and window.alive() and window.rect.collidepoint((mx, my)):
              return True

      # Check menu panel
      if self.ui.menu_panel is not None:
          if self.ui.menu_panel.get_abs_rect().collidepoint((mx, my)):
              return True

      # Check top bar and resource bar (they are above the map)
      if hasattr(self.ui, 'top_bar') and self.ui.top_bar.rect.collidepoint((mx, my)):
          return True
      if hasattr(self.ui, 'resource_bar') and self.ui.resource_bar.rect.collidepoint((mx, my)):
          return True

      return False
  ```
- [ ] Verify the method correctly checks all windows that should block
- [ ] Verify attribute names match actual window_manager attributes

**Notes:** Check `strategy_window_manager.py` for the exact attribute names used for windows.

### Task 2.2: Add unit tests for the new click gate [Medium]
**File:** `tests/unit/ui/strategy/test_strategy_event_router.py` (new or existing)
**Tests:** `pytest tests/unit/ui/strategy/ -k "event_router" --testmon`

- [ ] Test: click on map area with no windows open -> returns False (click passes through)
- [ ] Test: click on sidebar area -> returns True (blocked)
- [ ] Test: click on map area with fleet_orders_window open at that position -> returns True
- [ ] Test: click on map area with confirmation dialog open at that position -> returns True
- [ ] Test: click on top_bar area -> returns True (blocked)
- [ ] Test: click on map area with hidden buttons (btn_colonize visible=0) -> returns False (NOT blocked)

**Notes:** Use MagicMock for window_manager and ui elements.

### Task 2.3: Remove or finalize diagnostic logging from Phase 1 [Simple]
**File:** `game/ui/screens/strategy_event_router.py`, `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`

- [ ] Remove the diagnostic `logger.debug` calls added in Phase 1 Tasks 1.1/1.2
- [ ] Or convert to permanent debug-level logging if desired (user decision at implementation time)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
