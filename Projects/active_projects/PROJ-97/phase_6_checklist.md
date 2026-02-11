# Phase 6: Integration Tests & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** End-to-end testing and full verification

---

## Tasks

### Task 6.1: Write integration tests [Medium]
**File:** `tests/integration/strategy/test_production_rates.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_production_rates.py`

- [ ] Test: Build queue item with Metals cost 5500 at rate 3000/turn takes 2 turns
- [ ] Test: After 100 ticks (turn 1), no more than 3000 Metals consumed
- [ ] Test: After 200 ticks (turn 2), all 5500 Metals consumed and item completes
- [ ] Test: Mixed resources with different rates — bottleneck resource determines turns
- [ ] Test: Shipyard with construction_speed_bonus 1.5 multiplies all per-resource rates

**Notes:**

### Task 6.2: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run complete test suite
- [ ] Verify 7595+ tests pass with zero failures
- [ ] Document any new test count

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
