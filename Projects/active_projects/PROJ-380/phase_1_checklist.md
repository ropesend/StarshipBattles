# Phase 1: Dead imports

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-380 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the 1 verified dead import identified by audit `2026-05-07_220215_audit_shrink` and fix the matching stale string annotation.

---

## Tasks

### Task 1.1: Remove dead `IControllableShip` import [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -k controller` (or `pytest tests/ --testmon` once focused tests pass)

- [ ] Remove unused `IControllableShip` import (line 56) from the `if TYPE_CHECKING:` block — symbol does not exist in `game/simulation/interfaces/ai_controller.py` (mypy: `attr-defined` error)
- [ ] Update the stale string annotation `ship: 'IControllableShip'` (line 86) to `ship: 'ShipControllableAdapter'` (already imported at line 69 and is the runtime type passed by callers)
- [ ] Confirm `mypy game/ai/controller.py` no longer reports the `attr-defined` error
- [ ] Verify: focused tests pass; no new mypy/import errors elsewhere; LOC delta ≈ −1 line

**Notes:** Independent verification confirmed the import is unreachable. The string annotation is never resolved at runtime, so updating it is a documentation/static-analysis improvement rather than a behavior change. (DCV-01)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220215_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
