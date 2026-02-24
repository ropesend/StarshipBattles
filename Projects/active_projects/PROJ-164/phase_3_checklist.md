# Phase 3: Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-164 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm zero regressions across full test suite and verify duplication is eliminated.

---

## Tasks

### Task 3.1: Full test suite run [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify same pass count as baseline (7353+ tests)
- [ ] Verify no new warnings related to ability parsing

**Notes:**

### Task 3.2: Verify duplication eliminated [Simple]

- [ ] Run: `grep -rn "val = data if isinstance" game/simulation/components/abilities/` — should only show CrewRequired line 74
- [ ] Verify `_parse_primary_value` is called in `defense.py` (5 uses), `propulsion.py` (6 uses), `crew.py` (2 uses)
- [ ] Read `base.py` helper and confirm docstring, signature, edge case handling

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
