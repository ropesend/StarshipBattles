# Phase 1: Introduce `DesignRepository` (additive, no caller migration)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 1`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Not Started
**Depends on:** Phase 0
**Review Mode:** standard
**Files (planned):**
- `game/strategy/systems/design_repository.py` (new)
- `tests/unit/strategy/design_repository/` (new test package)

**Objective:** Move disk-bound responsibilities out of `DesignLibrary` into a new `DesignRepository` without changing any caller. The repository owns folder location and creation, `scan_designs`, `save_design`, `load_design_data`, `mark_design_obsolete`, and `increment_built_count`. `DesignLoadResult` shape is preserved unchanged. Save-folder and temp-folder policy moves into the repository. No production or UI caller is migrated in this phase — the work is purely additive.

---

## Tasks

### Task 1.1: Define `DesignRepository` unit tests (TDD-first) [Medium]
**File:** `tests/unit/strategy/design_repository/test_repository.py` (new)
**Tests:** `pytest tests/unit/strategy/design_repository/ -v`

- [ ] `test_locates_save_folder_for_empire` — repository resolves the save-folder path from constructor inputs.
- [ ] `test_creates_save_folder_if_missing`.
- [ ] `test_scan_designs_returns_design_load_result_with_unchanged_shape` — explicit shape assertion against today's `DesignLoadResult`.
- [ ] `test_save_design_writes_json_to_correct_path`.
- [ ] `test_load_design_data_returns_dict_for_existing_design`.
- [ ] `test_mark_design_obsolete_updates_repository_state`.
- [ ] `test_increment_built_count_persists_to_disk`.
- [ ] **Verify:** all tests fail — `DesignRepository` does not exist yet.

### Task 1.2: Add `game/strategy/systems/design_repository.py` [Medium]
**File:** `game/strategy/systems/design_repository.py` (new)
**Tests:** Task 1.1 tests

- [ ] Implement `DesignRepository` with the six methods above.
- [ ] Constructor takes the save-folder root and an empire id (or whatever the cleanest accessor key is — record the decision in [`decisions.md`](decisions.md)).
- [ ] Re-use as much disk-policy code from `DesignLibrary` as possible, by extraction; do not delete `DesignLibrary` (it stays as a shim through Phase 5).
- [ ] **Verify:** Task 1.1 tests pass.

### Task 1.3: Phase close [Simple]
**Tests:** `pytest tests/unit/strategy/design_library/ tests/unit/strategy/design_repository/ -q`

- [ ] Confirm both `DesignLibrary` and `DesignRepository` test suites are green (additive change must not break existing callers).
- [ ] `rg -n "DesignRepository" game tests` — confirm zero production callers yet (catalog and migrations come later).
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_1 --repo .worktrees/phases/PROJ-427/phase_1`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] `DesignRepository` exists with the six listed methods.
- [ ] `DesignLoadResult` shape is byte-identical to today (no caller-visible change).
- [ ] No runtime or UI caller imports `DesignRepository` yet.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after cumulative review.
- [ ] Update plan.md phase table row.
- [ ] Update plan.md Current State to point to Phase 2.
