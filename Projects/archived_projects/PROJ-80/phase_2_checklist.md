# Phase 2: Integrate into BuilderRightPanel

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-80 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Refactor `BuilderRightPanel` to delegate stats display to the shared `DesignStatsPanel`.

---

## Tasks

### Task 2.1: Update StatRow import in right_panel.py [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py`

- [x] Remove `StatRow` class definition (lines 15-56) from `right_panel.py`
- [x] Add import: `from game.ui.panels.design_stats_panel import DesignStatsPanel`
- [x] Verify tests still pass (StatRow used internally by BuilderRightPanel)

**Notes:** StatRow now imported from design_stats_panel.py. Also updated design_report_panel.py to import from design_stats_panel.py.

### Task 2.2: Refactor setup_stats() to use DesignStatsPanel [Medium]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/repro_issues/test_bug_04_display.py`

- [x] Add import: `from game.ui.panels.design_stats_panel import DesignStatsPanel`
- [x] Replace `setup_stats()` body with DesignStatsPanel delegation
- [x] Add helper method `_sync_from_stats_panel()`
- [x] Remove old `build_section()` helper, column layout code, layer row creation from `setup_stats()`
- [x] Verify: `panel.rows_map` contains expected keys ('mass', 'max_speed', 'shield_regen', etc.)

**Notes:** setup_stats() now creates DesignStatsPanel and syncs references.

### Task 2.3: Refactor update_stats_display() [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/repro_issues/test_bug_04_display.py`

- [x] Replace `update_stats_display(self, s)` body with delegation to stats_panel.update_stats(s)
- [x] Remove old layer update code, requirements update code, warnings update code

**Notes:** Single line delegation now.

### Task 2.4: Refactor rebuild_stats() and on_ship_updated() [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py`

- [x] Replace `rebuild_stats()` body with stats_panel.rebuild() + _sync_from_stats_panel()
- [x] Simplify `on_ship_updated()` to use `stats_panel.needs_rebuild()`
- [x] Remove old dirty-checking code for logistics keys

**Notes:** on_ship_updated() now uses stats_panel.needs_rebuild() for detection.

### Task 2.5: Verify all builder tests pass [Simple]
**Tests:** `pytest tests/unit/ui/ tests/repro_issues/test_bug_04_display.py -v`

- [x] Run targeted test suite
- [x] Verify `test_stats_panel_creation_and_update` passes (checks `panel.rows_map` keys)
- [x] Verify `test_logistics_section` passes (checks `max_fuel` in `panel.rows_map`)
- [x] Verify `test_bug_04_display` passes
- [x] Run `pytest tests/ --testmon` for broader regression check

**Notes:** Updated test_stats_render.py, test_bug_04_display.py, and test_ui_dynamic_update.py to reload design_stats_panel module.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `BuilderRightPanel` delegates all stats to `DesignStatsPanel`
- [x] `StatRow` class no longer defined in `right_panel.py`
- [x] All builder tests pass
- [x] No dead code remains in `right_panel.py`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
