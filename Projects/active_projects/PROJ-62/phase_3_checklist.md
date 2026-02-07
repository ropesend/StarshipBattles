# Phase 3: Extract Virtual Row Renderer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-62 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create `VirtualListRenderer` in `planet_list_renderer.py`

---

## Tasks

### Task 3.1: Create `planet_list_renderer.py` with `VirtualListRenderer` [Medium]
**File:** `game/ui/screens/planet_list_renderer.py` (NEW)
**Tests:** `pytest tests/integration/ui/test_planet_list_window.py tests/performance/benchmark_planet_list.py`

- [ ] Create new file `game/ui/screens/planet_list_renderer.py`
- [ ] Add imports: `pygame`, `pygame_gui.elements` (UIPanel, UILabel, UIImage), `game.assets.asset_manager.AssetManager`
- [ ] Import `get_column_value` from `planet_list_filters`
- [ ] Define `VirtualListRenderer` class:
  - `__init__(self, list_panel, row_height, manager)`:
    - `self.list_panel = list_panel`
    - `self.row_height = row_height`
    - `self.manager = manager`
    - `self.row_pool = []`
    - `self._icon_cache = {}`
    - `self._last_scroll_pct = -1.0`
    - `self._last_filtered_count = -1`
- [ ] Move `_rebuild_row_pool()` (lines 597-653) as `rebuild_row_pool(self, visible_columns)`:
  - Replace `self.list_view_rect` with `self.list_panel.relative_rect`
  - Replace `self.ui_manager` with `self.manager`
  - Replace `self._get_visible_columns()` with `visible_columns` parameter
- [ ] Move `_update_visible_rows()` (lines 655-743) as `update_visible_rows(self, filtered_planets, scroll_bar)`:
  - Replace `self.scroll_bar` with `scroll_bar` parameter
  - Replace `self.filtered_planets` with `filtered_planets` parameter
  - Keep icon cache logic (`self._icon_cache`) inside the class
- [ ] Add `get_clicked_planet_index(self, mouse_pos, list_abs_rect, scroll_bar, total_planets)` method:
  - Extract click-to-index calculation from `process_event()` (lines 792-806)
  - Returns int index or -1 if outside bounds
- [ ] Add `force_update(self)` to reset dirty tracking (sets `self._last_scroll_pct = -1.0`)
- [ ] Add `kill(self)` method to clean up all row pool widgets

### Task 3.2: Update `PlanetListWindow` to use `VirtualListRenderer` [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [ ] Add import: `from game.ui.screens.planet_list_renderer import VirtualListRenderer`
- [ ] In `__init__`, create renderer after list_panel:
  ```python
  self.renderer = VirtualListRenderer(self.list_panel, self.row_height, manager)
  ```
- [ ] Replace `self._rebuild_row_pool()` calls with `self.renderer.rebuild_row_pool(self.column_mgr.get_visible_columns())`
- [ ] Replace `self._update_visible_rows()` calls with `self.renderer.update_visible_rows(self.filtered_planets, self.scroll_bar)`
- [ ] In `refresh_list()`, replace `self._last_scroll_pct = -1.0` with `self.renderer.force_update()`
- [ ] In `process_event()`, replace click calculation block with `self.renderer.get_clicked_planet_index(...)` call
- [ ] Delete `_rebuild_row_pool()` and `_update_visible_rows()` from main class
- [ ] Remove `self.row_pool`, `self._icon_cache`, `self._last_scroll_pct`, `self._last_filtered_count` from `__init__`
- [ ] Update `kill()` to call `self.renderer.kill()`

### Task 3.3: Verify Phase 3 [Simple]
**Tests:** `pytest tests/`

- [ ] Run full test suite - all 6248 tests pass
- [ ] Verify `planet_list_window.py` line count (target: ~595-620 lines)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
