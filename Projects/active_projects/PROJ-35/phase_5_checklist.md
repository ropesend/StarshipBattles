# Phase 5: Add Consistency Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Guarantee projection matches execution

---

## Tasks

### Task 5.1: Create Consistency Test Suite [Medium]
**File:** `tests/strategy/test_fleet_navigation_consistency.py` (NEW)
**Tests:** `pytest tests/strategy/test_fleet_navigation_consistency.py -v`

```python
class TestProjectionMatchesExecution:
    """Verify UI projections match actual TurnEngine execution."""

    def test_simple_move_consistency(self):
        """MOVE order: projected path matches execution."""

    def test_multi_turn_consistency(self):
        """Multi-turn journey: each step matches."""

    def test_warp_move_consistency(self):
        """Warp jump projection matches execution."""

    def test_intercept_consistency(self):
        """MOVE_TO_FLEET: intercept point matches."""

    def test_chained_orders_consistency(self):
        """Multiple orders: full queue matches."""
```

- [ ] Create test file with fixtures
- [ ] Implement test_simple_move_consistency()
  - Create fleet with MOVE order
  - Project path
  - Execute turns with TurnEngine
  - Compare final positions
- [ ] Implement test_multi_turn_consistency()
  - Longer journey spanning multiple turns
  - Verify each step matches projection
- [ ] Implement test_warp_move_consistency()
  - Fleet with warp capability
  - Path crosses warp points
  - Verify warp segments match
- [ ] Implement test_intercept_consistency()
  - Create chaser and target fleets
  - Chaser has MOVE_TO_FLEET order
  - Verify intercept point calculation consistent
- [ ] Implement test_chained_orders_consistency()
  - Fleet with multiple orders in queue
  - Verify complete queue execution matches projection

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/strategy/test_fleet_navigation_consistency.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
