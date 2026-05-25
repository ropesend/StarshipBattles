# Phase 4: Negative-test guard (deliberately broken snapshot must fail)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add a permanent regression guard that proves the comparator stays strict. If someone reverts Phase 2's symmetric edit, this test fails immediately.

---

## Tasks

### Task 4.1: Add negative-guard test [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py::test_strictness_negative_guard -v`

- [x] Add `test_strictness_negative_guard` to the file from Phase 1.
- [x] Body: load a real baseline (e.g. `railgun_no_modifiers.json`) into memory as `expected`. Construct `actual` by deep-copying `expected` and injecting an extra key like `actual["component"]["stats"]["__strictness_canary__"] = "should fail"`. Call `compare_snapshots(actual, expected)` and assert the returned diff is non-empty AND contains the string `__strictness_canary__`.
- [x] Add a docstring referencing PROJ-499 and explaining: "If this test fails, someone weakened compare_snapshots() back to asymmetric iteration. Revert that change."
- [x] Run the test — confirm GREEN under the symmetric comparator.

**Notes:**
- Added `test_strictness_negative_guard` to `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py`.
- Per orchestrator constraint #5, test covers BOTH directions: (a) extra key in `actual` (the PROJ-489 regression direction), (b) extra key in `expected` (a stale-baseline carrying a removed key — the missing-in-actual branch). Both directions assert the diff fires AND names the canary.
- Loads `railgun_no_modifiers.json`, deep-copies, injects `__strictness_canary__` then `__missing_canary__`. Real-baseline based, so the test exercises the same call path as production usage.
- Docstring explicitly references PROJ-499 and instructs reverter to undo their change.
- Test GREEN: **4 passed in 1.66s** (3 Phase-1 tests + this new guard).

### Task 4.2: Final sharded green [Simple]
**File:** none
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite. Confirm GREEN.
- [x] Record final pass count.

**Notes:**
- Sharded suite GREEN: **26874 tests | 26873 passed | 0 failed | 0 errors | 1 skipped** (152.0s, 12 shards).
- Net test delta from start (Phase 0 baseline 26870/26869) is +4 tests: the 3 Phase-1 strictness tests + the new Phase-4 negative guard. Zero regressions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Negative-guard test exists and passes
- [x] Sharded suite GREEN
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
