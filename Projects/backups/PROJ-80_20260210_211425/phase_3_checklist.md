# Phase 3: Integrate into DesignReportPanel + Widen Build Queue

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-80 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Refactor `DesignReportPanel` to use shared `DesignStatsPanel` and widen Build Queue's design report panel to 750px.

---

## Tasks

### Task 3.1: Refactor DesignReportPanel to use DesignStatsPanel [Medium]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_design_report.py`

- [x] Update imports:
  - Remove: `from game.ui.screens.builder.right_panel import StatRow`
  - Remove: `from game.ui.screens.builder.stats_config import STATS_CONFIG, get_construction_rows`
  - Add: `from game.ui.panels.design_stats_panel import DesignStatsPanel`
- [x] Remove methods that are now handled by `DesignStatsPanel`:
  - `_rebuild_stats()` (lines 232-313)
  - `_create_stat_row()` (lines 374-406)
  - `_create_section_header()` (lines 363-372)
  - `_create_layers_section()` (lines 315-361)
- [x] Add `self._stats_panel = None` in `__init__`
- [x] Refactor `update_design(self, ship)` to use DesignStatsPanel
- [x] Update `show_placeholder()` - kill `self._stats_panel` if exists
- [x] Update `kill()` - kill `self._stats_panel` if exists
- [x] Removed stats_container (now handled by DesignStatsPanel internally)
- [x] Removed LayerType import (now handled inside DesignStatsPanel)
- [x] Removed UIScrollingContainer, UILabel imports (no longer needed)

**Notes:** Reduced from 421 lines to 253 lines (-168 lines, -40%)

### Task 3.2: Widen design report panel in Build Queue screen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py tests/integration/ui/test_build_queue_design_report.py`

- [x] In `_create_design_report_panel()` (line 372): change `design_report_width = 400` to `design_report_width = 750`
- [x] In `_create_build_queue_panel()` (line 425): change `design_details_width = 400` to `design_details_width = 750`
- [x] Verify layout math: on 1920px screen:
  - Build queue panel = 1920 - 710 - 750 - 20 = 440px (above 250px minimum, OK)
- [x] Verify `_create_build_queue_panel()` minimum width check still works (line 429: `if panel_width < 250`)

**Notes:** Build Queue now uses 750px wide two-column stats panel matching Design Workshop

### Task 3.3: Verify build queue tests pass [Simple]
**Tests:** `pytest tests/integration/ui/test_build_queue_design_report.py tests/integration/ui/test_build_queue_formatting.py -v`

- [x] Run targeted tests - expect some failures due to dimension changes (portrait, stats container position)
- [x] Note which tests fail for Phase 4 test updates
- [x] Run `pytest tests/ --testmon` for broader regression check

**Notes:**
- 12 tests failing in test_build_queue_design_report.py due to removed stats_container attribute
- Tests expect `stats_container` attribute which is now `_stats_panel.stats_scroll`
- Phase 4 will update these tests to use the new interface

Failing tests to fix in Phase 4:
1. test_stats_container_exists
2. test_stats_container_position
3. test_update_design_displays_ship_name
4. test_update_design_displays_stats
5. test_update_design_updates_portrait
6. test_stat_sections_exist_after_update
7. test_no_requirements_section
8. test_no_warnings_section
9. test_panel_integrates_with_container
10. test_multiple_ship_updates
11. test_show_placeholder_clears_stats
12. test_panel_handles_ship_with_minimal_stats

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `DesignReportPanel` delegates stats to `DesignStatsPanel`
- [x] Build Queue design report panel is 750px wide
- [x] No dead stats code remains in `design_report_panel.py`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
