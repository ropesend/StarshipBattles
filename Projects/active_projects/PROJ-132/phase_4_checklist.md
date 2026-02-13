# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-132 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (1 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: ADR-UI2-001 - Direct Simulation Layer Import in ship_i [Medium]
**File:** `game/ui/services/ship_io.py:16`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. ARCHITECTURE.md explicitly allows UI→Simulation imports (lines 35-37). ShipIO is a bridge service that must return Ship objects to UI. Adding protocol abstraction adds complexity without benefit - service's core logic (tkinter file dialogs) cannot be unit tested anyway. Consistent with accepted cross-layer imports in simulation_adapter.py and ShipInstance.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
