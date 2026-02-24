# Phase 4: Ghost Code Cleanup & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-178 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove obsolete comment and verify full test suite passes.

---

## Tasks

### Task 4.1: Remove ghost comment in galaxy.py [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/galaxy/`

- [ ] Delete line 28: `# Planet and PlanetType moved to game.strategy.data.planet`
- [ ] Verify tests pass

**Notes:**

### Task 4.2: Final full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify baseline maintained: 12338+ passed, 0 failures
- [ ] Document final pass count in plan.md Current State

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: 12338+ passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
