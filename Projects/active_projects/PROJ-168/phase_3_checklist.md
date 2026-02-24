# Phase 3: Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-168 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm zero behavioral change across the full test suite

---

## Tasks

### Task 3.1: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 11994+ tests pass (same as baseline)
- [ ] No new warnings related to hex_math
- [ ] No skipped test changes

### Task 3.2: Verify density and region tests specifically [Simple]
**Tests:** `pytest tests/unit/strategy/generation/ -v`

- [ ] All density tests pass with verbose output
- [ ] All region classifier tests pass with verbose output
- [ ] New hex_axial_to_cartesian tests pass: `pytest tests/unit/core/test_hex_math_core.py -v`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — ready for audit"
