# Phase 2: Tighten `compare_snapshots()` to symmetric key equality

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make `compare_snapshots()` symmetric. After this phase, Phase 1's tests pass and essentially every existing baseline FAILS (which is the expected RED state for Phase 3 to fix).

---

## Tasks

### Task 2.1: Walk the union of key sets in `compare_values()` dict branch [Simple]
**File:** `tests/regression/modifier_ability_snapshots/conftest.py:147-156`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py -v`

- [ ] Inside `compare_values()`, change the dict-branch to iterate `sorted(set(expected_val) | set(actual_val))`. Mirror `tests/infrastructure/deep_compare.py:87-88` — sorted union keeps diff ordering deterministic. (Audit F1: PROJ-499 mid-project-review consult, response.md:17.)
- [ ] For keys missing from `actual_val`, keep the existing `missing in actual` message.
- [ ] For keys missing from `expected_val`, emit a new message of the form `{path}.{key}: unexpected key in actual (value={actual_val[key]!r})`.
- [ ] For keys in both, recurse as before.
- [ ] Run the Phase 1 test file — confirm all 3 tests now PASS. Capture in notes.
- [ ] Do NOT touch `snapshot_full_component()`, `snapshot_component_stats()`, or any other writer helper.

**Notes:** [Filled during execution — include the GREEN test output]

### Task 2.2: Confirm full modifier-snapshot suite is RED in the expected way [Simple]
**File:** none
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -v`

- [ ] Run the full modifier-snapshot suite (`test_utility_modifiers.py` + `test_weapon_modifiers.py`).
- [ ] Expect MANY failures — each baseline missing the 4 new keys produces 4 "unexpected key in actual" diffs.
- [ ] Capture the failure summary in notes — count of failing tests, sampled diff text.
- [ ] Compare against Phase 0's `findings/source_review.md` census: failure counts should match the census expectations. If they don't, investigate before Phase 3.
- [ ] Do NOT re-shoot any baselines in this phase.

**Notes:** [Filled during execution]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Phase 1 strictness tests now GREEN
- [ ] Full modifier-snapshot suite RED in the expected pattern (only `unexpected key in actual` messages)
- [ ] Failure pattern matches Phase 0 census
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
