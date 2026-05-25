# Phase 2: Tighten `compare_snapshots()` to symmetric key equality

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make `compare_snapshots()` symmetric. After this phase, Phase 1's tests pass and essentially every existing baseline FAILS (which is the expected RED state for Phase 3 to fix).

---

## Tasks

### Task 2.1: Walk the union of key sets in `compare_values()` dict branch [Simple]
**File:** `tests/regression/modifier_ability_snapshots/conftest.py:147-156`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py -v`

- [x] Inside `compare_values()`, change the dict-branch to iterate `sorted(set(expected_val) | set(actual_val))`. Mirror `tests/infrastructure/deep_compare.py:87-88` — sorted union keeps diff ordering deterministic. (Audit F1: PROJ-499 mid-project-review consult, response.md:17.)
- [x] For keys missing from `actual_val`, keep the existing `missing in actual` message.
- [x] For keys missing from `expected_val`, emit a new message of the form `{path}.{key}: unexpected key in actual (value={actual_val[key]!r})`.
- [x] For keys in both, recurse as before.
- [x] Run the Phase 1 test file — confirm all 3 tests now PASS. Capture in notes.
- [x] Do NOT touch `snapshot_full_component()`, `snapshot_component_stats()`, or any other writer helper.

**Notes:**
- Edit: `tests/regression/modifier_ability_snapshots/conftest.py` lines 148-156 (the dict branch of `compare_values()`). Inserted `sorted(set(expected_val) | set(actual_val))` loop with split branches for `missing in actual` (key in expected only) and `unexpected key in actual (value=...)` (key in actual only).
- Phase 1 test file: 3 passed in 1.57s (was 3 failed in 1.81s). All 3 now GREEN.
- Writer helpers untouched.

### Task 2.2: Confirm full modifier-snapshot suite is RED in the expected way [Simple]
**File:** none
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -v`

- [x] Run the full modifier-snapshot suite (`test_utility_modifiers.py` + `test_weapon_modifiers.py`).
- [x] Expect MANY failures — each baseline missing the 4 new keys produces 4 "unexpected key in actual" diffs.
- [x] Capture the failure summary in notes — count of failing tests, sampled diff text.
- [x] Compare against Phase 0's `findings/source_review.md` census: failure counts should match the census expectations. If they don't, investigate before Phase 3.
- [x] Do NOT re-shoot any baselines in this phase.

**Notes:**
- Pytest `tests/regression/modifier_ability_snapshots/test_utility_modifiers.py tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py`: **59 failed, 11 passed in 2.76s.** (Full directory inc. strictness tests: 59 failed, 2212 passed.)
- Failure pattern: every failure emits exactly 4 lines of the form `root.component.stats.{launch_rate_mult|recovery_rate_mult|bay_capacity_mult|shield_bonus_add}: unexpected key in actual (value={1.0|0.0})`. NO other diff content. Matches the Phase 0 census exactly.
- Census predicted 58 stale baselines + 7 fresh + (4 formula-only tests in `TestModifierFormulaVerification` that don't load any baseline) + 1 duplicate-loader test (`test_railgun_no_facing` AND `test_railgun_facing_angles[0]` both load `railgun_facing_0`) = 70 total snapshot-loader tests collected. 59 fail (58 stale + 1 duplicate) + 11 pass (7 fresh + 4 formula-only) = 70. Aligns with census.
- No diff content beyond the 4 expected StatKey additions. No re-baselining done this phase — Phase 3 owns that.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Phase 1 strictness tests now GREEN
- [x] Full modifier-snapshot suite RED in the expected pattern (only `unexpected key in actual` messages)
- [x] Failure pattern matches Phase 0 census
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
