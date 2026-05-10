# Phase 1: Replace Detail Panel with DesignReportPanel

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-101 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the right-side ShipDetailPanel (350px) with the shared DesignReportPanel (750px) used in Build Queue and Design Workshop. Fix latent bug.

---

## Tasks

### Task 1.1: Update Layout Constants [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Change `self.detail_width = 350` to `self.detail_width = 750` (line 49)
- [x] Verify: At 2560px min with 90% window (2304px), list gets `2304 - 300 - 750 - 10 = 1244px`

**Notes:** Updated with comment explaining DesignReportPanel

### Task 1.2: Replace ShipDetailPanel Import and Init [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Replace import `from game.ui.panels.ship_detail_panel import ShipDetailPanel` with `from game.ui.panels.design_report_panel import DesignReportPanel` (line 15)
- [x] Add import: `from game.ui.services.design_loader_adapter import DesignLoaderAdapter` (new import)
- [x] In `__init__`, create design loader: `self._design_loader = DesignLoaderAdapter()` (after line 55)
- [x] In `_init_detail_panel()` (line 363-374): Replace ShipDetailPanel creation with:
  ```python
  self.design_report_panel = DesignReportPanel(
      manager=self.ui_manager,
      rect=detail_rect,
      container=self.detail_panel
  )
  ```
  Note: DesignReportPanel does NOT take `on_remove_ship` — removal moves to Phase 4.
- [x] Rename all references from `self.ship_detail_panel` to `self.design_report_panel`

**Notes:** Complete

### Task 1.3: Update Ship Selection to Convert ShipInstance→Ship [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Rewrite `_update_detail_panel()` (line 767-769) to:
  ```python
  def _update_detail_panel(self):
      """Update the detail panel with selected ship info."""
      if self.selected_ship:
          ship_obj = self._design_loader.load_ship_from_design_data(
              self.selected_ship.design_data, 0, 0
          )
          if ship_obj:
              self.design_report_panel.update_design(ship_obj)
          else:
              self.design_report_panel.show_placeholder()
      else:
          self.design_report_panel.show_placeholder()
  ```
- [x] Verify: `DesignLoaderAdapter.load_ship_from_design_data()` accepts `(design_data, width, height)` — check signature in `game/ui/services/design_loader_adapter.py:48`

**Notes:** Complete

### Task 1.4: Update Event Handling [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Remove the ShipDetailPanel event forwarding block (lines 725-728):
  ```python
  # Remove this block:
  if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:
      if self.ship_detail_panel.process_event(event):
          handled = True
  ```
  DesignReportPanel doesn't need process_event forwarding.

**Notes:** Complete

### Task 1.5: Fix _update_sidebar Bug [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] In `_on_remove_ship()` (line 778): Change `self._update_sidebar()` to `self._update_summary()`
- [x] Note: `_on_remove_ship()` will be reworked in Phase 4, but fix the bug now for correctness

**Notes:** Complete

### Task 1.6: Update kill() Method [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] In `kill()` (line 846-854): Change `self.ship_detail_panel` references to `self.design_report_panel`
- [x] Update `hasattr` check: `hasattr(self, 'design_report_panel')`

**Notes:** Complete

### Task 1.7: Run Tests [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite
- [x] All tests pass (baseline 7713)
- [x] No regressions

**Notes:** 7713 passed, 4 warnings

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
