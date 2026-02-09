# Phase 3: Integrate into DesignReportPanel + Widen Build Queue

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-80 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Refactor `DesignReportPanel` to use shared `DesignStatsPanel` and widen Build Queue's design report panel to 750px.

---

## Tasks

### Task 3.1: Refactor DesignReportPanel to use DesignStatsPanel [Medium]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_design_report.py`

- [ ] Update imports:
  - Remove: `from game.ui.screens.builder.right_panel import StatRow`
  - Remove: `from game.ui.screens.builder.stats_config import STATS_CONFIG, get_construction_rows`
  - Add: `from game.ui.panels.design_stats_panel import DesignStatsPanel`
- [ ] Remove methods that are now handled by `DesignStatsPanel`:
  - `_rebuild_stats()` (lines 232-313)
  - `_create_stat_row()` (lines 374-406)
  - `_create_section_header()` (lines 363-372)
  - `_create_layers_section()` (lines 315-361)
- [ ] Add `self._stats_panel = None` in `__init__`
- [ ] Refactor `update_design(self, ship)` (lines 112-130):
  ```python
  def update_design(self, ship):
      self.current_ship = ship
      if self.placeholder_text:
          self.placeholder_text.kill()
          self.placeholder_text = None
      self._update_portrait(ship)

      # Kill old stats panel
      if self._stats_panel:
          self._stats_panel.kill()

      # Create stats panel below portrait
      portrait_h = self.portrait_image.relative_rect.height
      stats_y = portrait_h + 20
      stats_w = self.rect.width
      stats_h = self.rect.height - stats_y - 10

      self._stats_panel = DesignStatsPanel(
          manager=self.manager,
          rect=pygame.Rect(0, stats_y, stats_w, stats_h),
          container=self.panel,
          ship=ship,
          show_requirements=False
      )
      self.rows_map = self._stats_panel.rows_map
  ```
- [ ] Update `show_placeholder()` (lines 83-110):
  - Add: kill `self._stats_panel` if it exists
  - Keep existing placeholder text creation logic
- [ ] Update `kill()` (lines 417-420):
  - Add: kill `self._stats_panel` if it exists
- [ ] Remove now-unused `self.rows_map = {}` init from `__init__` (will be set by `_stats_panel`)
- [ ] Remove `LayerType` import if no longer used directly (now handled inside `DesignStatsPanel`)

**Notes:**

### Task 3.2: Widen design report panel in Build Queue screen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py tests/integration/ui/test_build_queue_design_report.py`

- [ ] In `_create_design_report_panel()` (line 372): change `design_report_width = 400` to `design_report_width = 750`
- [ ] In `_create_build_queue_panel()` (line 425): change `design_details_width = 400` to `design_details_width = 750`
- [ ] Verify layout math: on 1920px screen:
  - Build queue panel = 1920 - 710 - 750 - 20 = 440px (above 250px minimum, OK)
- [ ] Verify `_create_build_queue_panel()` minimum width check still works (line 429: `if panel_width < 250`)

**Notes:**

### Task 3.3: Verify build queue tests pass [Simple]
**Tests:** `pytest tests/integration/ui/test_build_queue_design_report.py tests/integration/ui/test_build_queue_formatting.py -v`

- [ ] Run targeted tests - expect some failures due to dimension changes (portrait, stats container position)
- [ ] Note which tests fail for Phase 4 test updates
- [ ] Run `pytest tests/ --testmon` for broader regression check

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `DesignReportPanel` delegates stats to `DesignStatsPanel`
- [ ] Build Queue design report panel is 750px wide
- [ ] No dead stats code remains in `design_report_panel.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
