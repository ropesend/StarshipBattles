# Phase 1: Fix Stats Display + Cost Calculation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-81 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the two interconnected data bugs - stats showing "--" and production costs being empty (issues a, b, g)

---

## Tasks

### Task 1.1: Fix DesignStatsPanel not populating values [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [x] In `update_design()` (line 99), after creating `DesignStatsPanel` at line 126-132, add `self._stats_panel.update_stats(ship)` to populate stat values
- [x] This is the same fix as BUG-04 in `game/ui/screens/builder/right_panel.py:57-59`
- [x] Verify: Select a design in Available Designs - right panel should show actual stat values, not "--"

**Notes:**

### Task 1.2: Fix production cost and time calculation [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/ --testmon`

The root cause: `_calculate_build_turns()` (line 170) and `_build_cost_tracking()` (line 191) both use `design.resource_cost` from `DesignMetadata`, but `DesignMetadata._calculate_resource_cost()` reads from raw design JSON which doesn't store cost data. Result: always empty dict, always 1 turn.

**Fix approach:** Load the ship object (same as `refresh_design_report()` does at line 517-539) and use `ship.construction_cost` instead.

- [x] Create a helper method `_get_design_cost(self, design_id: str) -> Dict[str, int]` that:
  1. Loads design data via `self.design_library.load_design_data(design_id)`
  2. Creates ship via `self.design_loader.load_ship_from_design_data(design_data, 0, 0)`
  3. Returns `ship.construction_cost` (already populated by `ShipStatsCalculator.recalculate_stats()`)
  4. Returns `{}` on any error
- [x] Update `_calculate_build_turns()` (line 170) to use `_get_design_cost(design_id)` instead of `design.resource_cost`
- [x] Update `_build_cost_tracking()` (line 191) to use `_get_design_cost(design_id)` instead of `design.resource_cost`
- [x] Verify: Add a design that costs 4500 metals to a shipyard (3000 build rate) - should show 2 turns, not 1
- [x] Verify: Queue items should now have populated `total_cost` dict

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Stats display correctly when design selected (not "--")
- [x] Production time shows correct turns based on cost
- [x] Queue items have total_cost populated
- [x] `pytest tests/ --testmon` passes (7340 passed, 4 pre-existing failures in test_transfer_dialog.py)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
