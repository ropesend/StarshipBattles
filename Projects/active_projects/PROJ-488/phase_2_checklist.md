# Phase 2: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-488 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address 1 VERIFIED + IN-SCOPE finding from the Codex mid-project audit (F1 dead import). See `findings/audit_verification.md`.

---

## Tasks

### Task 2.1: Remove unused EARTH_MASS import (F1) [Simple]
**File:** `tests/unit/strategy/data/test_planet_physics.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_physics.py`

- [x] Line 7: delete `from game.core.constants import EARTH_MASS`. The file's remaining body uses numeric literals (`5.97e24`) directly, not `EARTH_MASS`.
- [x] Verify: `grep -n "EARTH_MASS" tests/unit/strategy/data/test_planet_physics.py` returns no hits.
- [x] Verify: targeted test still passes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row for Phase 2 to `Complete`
- [x] Update plan.md Current State
