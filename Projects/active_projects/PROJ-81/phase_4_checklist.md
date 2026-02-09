# Phase 4: Queue Item Selection + Design Identity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-81 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clicking a queue item shows that design in the right panel. Add design name/type/class to the right panel. (issues e, f)

---

## Tasks

### Task 4.1: Update design report on queue item click [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test

- [ ] In `handle_event()`, after `result = self.drag_handler.handle_mouse_up(...)` (line 1093-1098), when `result is not None`:
  1. Determine the active queue: `self.active_queue_source.construction_queue` or `self.build_context.construction_queue`
  2. Look up `design_id` from `queue[result].get('design_id')`
  3. Call `self.controller.refresh_design_report(design_id)` to update the right panel
- [ ] Verify: Click a queue item - right panel updates to show that design's stats

**Code sketch:**
```python
if result is not None:
    self.selected_queue_index = result
    queue = (self.active_queue_source.construction_queue
             if self.active_queue_source else self.build_context.construction_queue)
    if result < len(queue):
        design_id = queue[result].get('design_id')
        if design_id:
            self.controller.refresh_design_report(design_id)
```

**Notes:**

### Task 4.2: Add design identity labels to DesignReportPanel [Medium]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] In `__init__()`, after portrait creation (line 60-64), add identity label area:
  - `self.name_label`: UILabel for design name (below portrait, full width, bold/larger)
  - `self.type_class_label`: UILabel for vehicle type + ship class (below name, smaller)
  - Initially hidden or showing empty text
- [ ] Shift stats panel positioning down by ~50px in `update_design()` to accommodate identity labels
- [ ] In `update_design(ship)`, populate labels:
  - `self.name_label.set_text(ship.name)`
  - `self.type_class_label.set_text(f"{ship.vehicle_type} - {ship.ship_class}")`
- [ ] In `show_placeholder()`, clear/hide identity labels
- [ ] Verify: Design name, vehicle type, and ship class visible above stats

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Clicking queue item updates right panel
- [ ] Design name, type, class shown in right panel
- [ ] Clicking available design still works (doesn't break)
- [ ] `pytest tests/ --testmon` passes
- [ ] Run full `pytest tests/ -n 12` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
