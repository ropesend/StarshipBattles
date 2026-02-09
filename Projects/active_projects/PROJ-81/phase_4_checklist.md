# Phase 4: Queue Item Selection + Design Identity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-81 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clicking a queue item shows that design in the right panel. Add design name/type/class to the right panel. (issues e, f)

---

## Tasks

### Task 4.1: Update design report on queue item click [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test

- [x] In `handle_event()`, after `result = self.drag_handler.handle_mouse_up(...)` (line 1093-1098), when `result is not None`:
  1. Determine the active queue: `self.active_queue_source.construction_queue` or `self.build_context.construction_queue`
  2. Look up `design_id` from `queue[result].get('design_id')`
  3. Call `self.controller.refresh_design_report(design_id)` to update the right panel
- [x] Verify: Click a queue item - right panel updates to show that design's stats

**Notes:** Implemented at line 1111-1116. Uses active_queue already computed for drag handler.

### Task 4.2: Add design identity labels to DesignReportPanel [Medium]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [x] In `__init__()`, after portrait creation (line 60-64), add identity label area:
  - `self.name_label`: UILabel for design name (below portrait, full width, bold/larger)
  - `self.type_class_label`: UILabel for vehicle type + ship class (below name, smaller)
  - Initially hidden or showing empty text
- [x] Shift stats panel positioning down by ~50px in `update_design()` to accommodate identity labels
- [x] In `update_design(ship)`, populate labels:
  - `self.name_label.set_text(ship.name)`
  - `self.type_class_label.set_text(f"{ship.vehicle_type} - {ship.ship_class}")`
- [x] In `show_placeholder()`, clear/hide identity labels
- [x] Verify: Design name, vehicle type, and ship class visible above stats

**Notes:** Added 2 UILabels at identity_y = portrait_h + 15. Stats panel now starts at portrait_h + 15 + 50 = 795px. Updated test_stats_panel_position expected value. Added 2 new tests: test_identity_labels_populated, test_identity_labels_cleared_on_placeholder.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Clicking queue item updates right panel
- [x] Design name, type, class shown in right panel
- [x] Clicking available design still works (doesn't break)
- [x] `pytest tests/ --testmon` passes
- [x] Run full `pytest tests/ -n 12` - all tests pass (4 pre-existing failures in transfer_dialog)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete"
