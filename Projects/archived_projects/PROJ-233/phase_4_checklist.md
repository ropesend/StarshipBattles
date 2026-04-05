# Phase 4: Clean Up `process_construction_tick`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the 30-line design-discussion comment, extract fleet rate helper, and move deferred import to top-level.

---

## Tasks

### Task 4.1: Replace 30-line comment with concise summary [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ tests/unit/strategy/engine/ -v`

- [ ] Replace the 30-line comment block (lines 163-192 in original, adjust for earlier edits) with:
  ```python
  # Fleet yards share one queue; multiple yards multiply build speed.
  ```
- [ ] Verify: No behavioral change, just comment cleanup

**Notes:**

### Task 4.2: Move deferred import to top-level [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] Move `from game.strategy.data.build_queue_source import get_default_production_rates, _get_facility_production_rates` from inside `process_construction_tick()` (line 131 area) to the top-of-file imports section
- [ ] Verify: Import succeeds (no circular import), all tests pass

**Notes:**

### Task 4.3: Extract fleet rate resolution helper [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ tests/integration/strategy/production/ -v`

- [ ] Add helper method to `ProductionEngine`:
  ```python
  def _resolve_fleet_production_rate(self, fleet) -> Dict[str, float]:
      """Calculate combined production rate for a fleet's space yards."""
      yard_count = fleet.capabilities.space_shipyard_count
      base_rate = get_default_production_rates("fleet_space_yard")
      return {k: v * yard_count for k, v in base_rate.items()}
  ```
- [ ] Update `process_construction_tick()` fleet section to call the helper:
  ```python
  # OLD:
  yard_count = fleet.capabilities.space_shipyard_count
  base_rate = get_default_production_rates("fleet_space_yard")
  total_rate = {k: v * yard_count for k, v in base_rate.items()}

  # NEW:
  total_rate = self._resolve_fleet_production_rate(fleet)
  ```
- [ ] Verify: `process_construction_tick` is now ~45 lines (down from 77)
- [ ] Run tests: All pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
