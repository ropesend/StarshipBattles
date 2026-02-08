# Phase 7: Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire up button and window in strategy UI

---

## Tasks

### Task 7.1: Add "All Queues" button to top bar [Simple]

**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - button visible and clickable

- [ ] Add `self.empire_build_queue_window = None` (after line 46)
- [ ] Add new button after Menu button (around line 253):
  ```python
  self.btn_all_queues = pygame_gui.elements.UIButton(
      relative_rect=pygame.Rect(main_start_x + 5*(btn_w+gap) + btn_w + gap, 5, btn_w, 40),
      text="All Queues",
      manager=self.manager,
      container=self.top_bar
  )
  ```
- [ ] Shift End Turn button position to accommodate new button
- [ ] Update button positioning constants if needed

**Notes:**

---

### Task 7.2: Add button click handler [Simple]

**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - window opens on click

- [ ] Add import: `from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow`
- [ ] Add `open_empire_build_queue_window()` method:
  ```python
  def open_empire_build_queue_window(self):
      if self.empire_build_queue_window:
          self.empire_build_queue_window.kill()

      empire = self.scene.current_empire
      galaxy = self.scene.galaxy
      w, h = int(self.width * 0.9), int(self.height * 0.9)
      rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

      self.empire_build_queue_window = EmpireBuildQueueWindow(
          rect, self.manager, empire, galaxy,
          on_close_callback=self._on_empire_build_queue_closed,
          on_navigate_to_hex=self.scene.on_navigate_to_hex_build
      )
  ```
- [ ] Add close callback: `_on_empire_build_queue_closed()`
- [ ] Add button event handler in `handle_event()` (around line 720)

**Notes:**

---

### Task 7.3: Add modal check [Simple]

**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - prevents input passthrough

- [ ] Update `_has_modal_open()` to check `self.empire_build_queue_window is not None`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Manual test: Button appears in top bar
- [ ] Manual test: Click opens window
- [ ] Manual test: Window closes properly
- [ ] Manual test: Input blocked while window open
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

## Final Verification

After all phases complete:
- [ ] Open window, verify all columns display
- [ ] Toggle column visibility, verify headers update
- [ ] Apply each filter type, verify list updates
- [ ] Click row, verify navigation to hex build screen
- [ ] Ctrl+click multiple rows, verify multi-select
- [ ] Batch add to selected queues, verify items added
- [ ] Run full test suite: `pytest tests/`
