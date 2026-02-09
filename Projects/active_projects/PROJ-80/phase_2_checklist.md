# Phase 2: Integrate into BuilderRightPanel

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-80 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Refactor `BuilderRightPanel` to delegate stats display to the shared `DesignStatsPanel`.

---

## Tasks

### Task 2.1: Update StatRow import in right_panel.py [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py`

- [ ] Remove `StatRow` class definition (lines 15-56) from `right_panel.py`
- [ ] Add import: `from game.ui.panels.design_stats_panel import StatRow`
- [ ] Verify tests still pass (StatRow used internally by BuilderRightPanel)

**Notes:**

### Task 2.2: Refactor setup_stats() to use DesignStatsPanel [Medium]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/repro_issues/test_bug_04_display.py`

- [ ] Add import: `from game.ui.panels.design_stats_panel import DesignStatsPanel`
- [ ] Replace `setup_stats()` body (lines 377-496) with:
  ```python
  def setup_stats(self):
      y = self.last_y
      total_h = self.rect.height - y - 10
      if total_h < 100: total_h = 100

      self.stats_panel = DesignStatsPanel(
          manager=self.manager,
          rect=pygame.Rect(0, y, self.rect.width, total_h),
          container=self.panel,
          ship=self.builder.ship,
          show_requirements=True
      )
      # Expose attributes for backward compat with update methods
      self._sync_from_stats_panel()
  ```
- [ ] Add helper method `_sync_from_stats_panel()`:
  ```python
  def _sync_from_stats_panel(self):
      self.rows_map = self.stats_panel.rows_map
      self.current_logistics_keys = self.stats_panel.current_logistics_keys
      self.layer_rows = self.stats_panel.layer_rows
      self.req_box_left = self.stats_panel.req_box_left
      self.req_box_right = self.stats_panel.req_box_right
      self.stats_scroll = self.stats_panel.stats_scroll
  ```
- [ ] Remove old `build_section()` helper, column layout code, layer row creation from `setup_stats()`
- [ ] Remove old `from .stats_config import STATS_CONFIG, get_logistics_rows` import if no longer used directly (check `on_ship_updated` still needs `get_logistics_rows`)
- [ ] Verify: `panel.rows_map` contains expected keys ('mass', 'max_speed', 'shield_regen', etc.)

**Notes:**

### Task 2.3: Refactor update_stats_display() [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/repro_issues/test_bug_04_display.py`

- [ ] Replace `update_stats_display(self, s)` body (lines 558-639) with:
  ```python
  def update_stats_display(self, s):
      self.stats_panel.update_stats(s)
  ```
- [ ] Remove old layer update code, requirements update code, warnings update code
- [ ] Remove now-unused imports (`LayerType` if only used in update_stats_display)

**Notes:**

### Task 2.4: Refactor rebuild_stats() and on_ship_updated() [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py`

- [ ] Replace `rebuild_stats()` body (lines 498-502) with:
  ```python
  def rebuild_stats(self):
      if hasattr(self, 'stats_panel'):
          self.stats_panel.rebuild(self.builder.ship)
          self._sync_from_stats_panel()
      else:
          self.setup_stats()
  ```
- [ ] Simplify `on_ship_updated()` (lines 93-129) to use `needs_rebuild`:
  ```python
  def on_ship_updated(self, ship):
      if hasattr(self, 'stats_panel') and self.stats_panel.needs_rebuild(ship):
          self.stats_panel.rebuild(ship)
          self._sync_from_stats_panel()
      self.stats_panel.update_stats(ship)
  ```
- [ ] Remove old dirty-checking code for logistics keys
- [ ] Remove `from .stats_config import get_logistics_rows` import if no longer used directly

**Notes:**

### Task 2.5: Verify all builder tests pass [Simple]
**Tests:** `pytest tests/unit/ui/ tests/repro_issues/test_bug_04_display.py -v`

- [ ] Run targeted test suite
- [ ] Verify `test_stats_panel_creation_and_update` passes (checks `panel.rows_map` keys)
- [ ] Verify `test_logistics_section` passes (checks `max_fuel` in `panel.rows_map`)
- [ ] Verify `test_bug_04_display` passes
- [ ] Run `pytest tests/ --testmon` for broader regression check

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BuilderRightPanel` delegates all stats to `DesignStatsPanel`
- [ ] `StatRow` class no longer defined in `right_panel.py`
- [ ] All builder tests pass
- [ ] No dead code remains in `right_panel.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
