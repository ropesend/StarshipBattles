# Phase 1: Introduce `DesignRepository` (additive, no caller migration)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 1`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Complete (Committed)
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

- [x] `test_locates_save_folder_for_empire` — repository resolves the save-folder path from constructor inputs.
- [x] `test_creates_save_folder_if_missing`.
- [x] `test_scan_designs_returns_design_metadata_list` — explicit shape assertion: list of `DesignMetadata`, matching `DesignLibrary.scan_designs()` today.
- [x] `test_save_design_writes_json_to_correct_path` (split low-level write `save_design_data(design_id, data)` from the rich workshop `save_design` flow; see decisions.md 2026-05-17).
- [x] `test_load_design_data_returns_design_load_result_ok` + `test_load_design_data_returns_not_found_for_missing` (DesignLoadResult shape preserved byte-identically).
- [x] `test_mark_design_obsolete_updates_repository_state`.
- [x] `test_increment_built_count_persists_to_disk`.
- [x] **Verify:** all tests failed prior to implementation; all pass after.

### Task 1.2: Add `game/strategy/systems/design_repository.py` [Medium]
**File:** `game/strategy/systems/design_repository.py` (new)
**Tests:** Task 1.1 tests

- [x] Implement `DesignRepository` with the six methods above.
- [x] Constructor takes the save-folder root and an empire id; key is `(savegame_path, empire_id)` matching `DesignLibrary`. Decision recorded in [`decisions.md`](decisions.md).
- [x] Re-use disk-policy code patterns from `DesignLibrary` by re-implementing them in the repository (per-empire folder, temp-folder fallback, OSError → temp fallback); keep `DesignLibrary` intact as a shim.
- [x] **Verify:** Task 1.1 tests pass (9/9).

### Task 1.3: Phase close [Simple]
**Tests:** `pytest tests/unit/strategy/design_library/ tests/unit/strategy/design_repository/ -q`

- [x] Confirm both `DesignLibrary` and `DesignRepository` test suites are green — 55/55 passed.
- [x] `rg -n "DesignRepository" game tests` — only the new module + test file; zero production callers yet.
- [x] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_1 --repo .worktrees/phases/PROJ-427/phase_1`. _Skipped per split-execution scope; commit recorded on `proj/PROJ-427/main` directly._

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
