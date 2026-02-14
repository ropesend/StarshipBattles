# Phase 6: Integration & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-139 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full integration testing, serialization round-trips, manual verification.

---

## Tasks

### Task 6.1: Serialization round-trip tests [Medium]
**File:** `tests/unit/strategy/data/test_galaxy.py` (extend or new file)
**Tests:** `pytest tests/unit/strategy/data/`

- [ ] Test: Galaxy with star zones -> to_dict() -> from_dict() -> zone index rebuilt correctly
- [ ] Test: Galaxy with Dyson Sphere -> to_dict() -> from_dict() -> zone index rebuilt correctly
- [ ] Test: Planet with diameter_hexes -> to_dict() -> from_dict() -> diameter_hexes preserved
- [ ] Verify: `pytest tests/unit/strategy/data/` passes

**Notes:**

### Task 6.2: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite - all 11,906+ tests must pass
- [ ] Fix any regressions
- [ ] Verify: 0 failures

**Notes:**

### Task 6.3: Manual gameplay verification [Simple]
**Tests:** Manual

- [ ] Launch game, navigate to a star system with a large star
- [ ] Click hexes around the star - verify star selected from zone hexes
- [ ] Create Dyson Sphere (if possible in test scenario)
- [ ] Verify Dyson Sphere image renders at correct scale (11-hex diameter)
- [ ] Verify clicking any hex in Dyson zone selects it
- [ ] Verify colonization from a zone hex works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
