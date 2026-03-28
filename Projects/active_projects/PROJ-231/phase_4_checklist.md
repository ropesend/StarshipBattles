# Phase 4: Strategy Screen Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire the Star List Window into the strategy screen via button, event routing, and window management.

---

## Tasks

### Task 4.1: Add `btn_stars` to Top Bar [Simple]
**File:** `game/ui/screens/strategy_panel_manager.py`
**Tests:** `python -m pytest tests/ --testmon -q`

- [ ] Add `btn_stars: Any = None` to `StrategyWidgets` dataclass (after `btn_planets` at line 69)
- [ ] In top bar button creation (around line 267), insert Stars button after Planets:
  ```python
  widgets.btn_stars = pygame_gui.elements.UIButton(
      relative_rect=pygame.Rect(main_start_x + 1*(btn_w+gap), 5, btn_w, 40),
      text="Stars", manager=manager, container=widgets.top_bar
  )
  ```
- [ ] Shift ALL subsequent button indices right by 1:
  - Empire: index 1 → 2
  - Research: index 2 → 3
  - Design: index 3 → 4
  - Build Yards: index 4 → 5
  - All Queues: index 5 → 6
  - Menu: index 6 → 7
  - Log: index 7 → 8
- [ ] Verify all buttons still fit in top bar at 2560px width

**Notes:**

---

### Task 4.2: Wire `btn_stars` in StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`

- [ ] Add `self.btn_stars = widgets.btn_stars` after `self.btn_planets` (find the widget unpacking section)
- [ ] Add delegation method:
  ```python
  def open_star_list(self):
      """Open the Star List Window."""
      self.window_manager.open_star_list()
  ```

**Notes:**

---

### Task 4.3: Add `open_star_list()` to StrategyWindowManager [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`

- [ ] Add import at top: `from game.ui.screens.star_list_window import StarListWindow`
- [ ] Add `self.star_list_window = None` in `__init__` (after `self.planet_list_window`)
- [ ] Add `open_star_list()` method:
  ```python
  def open_star_list(self) -> None:
      """Open the Star List Window."""
      if self.star_list_window:
          self.star_list_window.kill()
      w, h = self.width * 0.9, self.height * 0.9
      rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)
      galaxy = self.scene.galaxy
      self.star_list_window = StarListWindow(
          rect, self.manager, galaxy,
          on_close_callback=self._on_star_list_closed,
          on_navigate_callback=self._on_star_navigate,
      )
  ```
- [ ] Add `_on_star_list_closed()` callback:
  ```python
  def _on_star_list_closed(self) -> None:
      self.star_list_window = None
  ```
- [ ] Add `_on_star_navigate(global_hex)` callback:
  ```python
  def _on_star_navigate(self, global_hex) -> None:
      if self.star_list_window:
          self.star_list_window.kill()
      if hasattr(self.scene, '_camera_nav'):
          self.scene._camera_nav.center_on_hex(global_hex)
  ```

**Notes:**

---

### Task 4.4: Route `btn_stars` in Event Router [Simple]
**File:** `game/ui/screens/strategy_event_router.py`

- [ ] In `_handle_button_pressed()` (around line 158-159, after `btn_planets` handler):
  ```python
  elif event.ui_element == ui.btn_stars:
      ui.open_star_list()
  ```
- [ ] In `has_modal_open()` (around line 65, after planet_list check):
  ```python
  if wm.star_list_window is not None:
      return True
  ```
- [ ] In `_handle_window_close()` (find the window close section):
  ```python
  elif event.ui_element == wm.star_list_window:
      wm._on_star_list_closed()
  ```
- [ ] In `_is_blocking_ui_element_at()` blocking_windows list (around line 318):
  ```python
  ('star_list_window', wm.star_list_window),
  ```

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `python -m pytest tests/ -n 12`
- [ ] Launch game, strategy screen shows "Stars" button in top bar
- [ ] Clicking "Stars" opens the Star List Window
- [ ] Window closes properly (X button and Navigate both work)
- [ ] No button overlap or layout issues in top bar
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
