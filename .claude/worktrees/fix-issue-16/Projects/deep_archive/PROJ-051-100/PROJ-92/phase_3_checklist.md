# Phase 3: Update documentation & audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-92 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update architecture docs and run final verification.

---

## Tasks

### Task 3.1: Update ARCHITECTURE.md [Simple]
**File:** `docs/architecture/ARCHITECTURE.md`

- [ ] Update any references to `hex_math` living in strategy to reflect its new core location
- [ ] Note in "Intentional Late Imports" section that the `core/protocols.py → strategy/hex_math` violation is resolved

**Notes:**

### Task 3.2: Final audit [Simple]

- [ ] Run `pytest tests/ -n 12 -q` — full pass
- [ ] Verify `grep -r "strategy.data.hex_math" game/ tests/` returns 0 results
- [ ] Verify no `TYPE_CHECKING` remains in the 6 cleaned files

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
