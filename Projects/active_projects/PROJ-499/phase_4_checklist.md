# Phase 4: Negative-test guard (deliberately broken snapshot must fail)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add a permanent regression guard that proves the comparator stays strict. If someone reverts Phase 2's symmetric edit, this test fails immediately.

---

## Tasks

### Task 4.1: Add negative-guard test [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py::test_strictness_negative_guard -v`

- [ ] Add `test_strictness_negative_guard` to the file from Phase 1.
- [ ] Body: load a real baseline (e.g. `railgun_no_modifiers.json`) into memory as `expected`. Construct `actual` by deep-copying `expected` and injecting an extra key like `actual["component"]["stats"]["__strictness_canary__"] = "should fail"`. Call `compare_snapshots(actual, expected)` and assert the returned diff is non-empty AND contains the string `__strictness_canary__`.
- [ ] Add a docstring referencing PROJ-499 and explaining: "If this test fails, someone weakened compare_snapshots() back to asymmetric iteration. Revert that change."
- [ ] Run the test — confirm GREEN under the symmetric comparator.

**Notes:** [Filled during execution]

### Task 4.2: Final sharded green [Simple]
**File:** none
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite. Confirm GREEN.
- [ ] Record final pass count.

**Notes:** [Filled during execution]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Negative-guard test exists and passes
- [ ] Sharded suite GREEN
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
