# Phase 1: Diagnostic Logging

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-216 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add temporary diagnostic logging to confirm the root cause at runtime.

---

## Tasks

### Task 1.1: Add diagnostic log to click gate [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ -k "event_router" --testmon`

- [ ] Add `import logging; logger = logging.getLogger(__name__)` at top of file if not present
- [ ] Add diagnostic logging inside `handle_click()` method (line 254-274):
  ```python
  def handle_click(self, mx: int, my: int, button: int) -> bool:
      # 1. Check logical sidebar area
      if mx > self.ui.width - self.ui.sidebar_width:
          return True

      # 2. Check if ANY UI element is being hovered
      hovering = self.ui.manager.get_hovering_any_element()
      if hovering:
          logger.debug(f"Click at ({mx},{my}) BLOCKED by UI hover check")
          return True

      return False
  ```
- [ ] Verify no existing tests break

**Notes:**

### Task 1.2: Add diagnostic log to click dispatcher entry [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/strategy/ -k "input_handler" --testmon`

- [ ] Add logging to `handle_click()` method (line 134-147):
  ```python
  def handle_click(self, mx, my, button):
      ui_handled = self.scene.ui.handle_click(mx, my, button)
      if ui_handled:
          logger.debug(f"Click at ({mx},{my}) consumed by UI layer")
          return True
      logger.debug(f"Click at ({mx},{my}) reaching dispatcher, mode={self.input_mode}")
      return self._click_dispatch.dispatch_click(mx, my, button)
  ```
- [ ] Verify no existing tests break

**Notes:**

### Task 1.3: Manual runtime verification [Simple]
**Tests:** Manual test - launch game, open console log, click on map

- [ ] Start new game
- [ ] Select a fleet, press M
- [ ] Click on a destination hex
- [ ] Check console output: confirm "BLOCKED by UI hover check" message appears
- [ ] Document which elements are triggering the false positive

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
