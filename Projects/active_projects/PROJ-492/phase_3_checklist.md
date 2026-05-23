# Phase 3: HLP-005 setup_tmpdir — Paths.SAVES_DIR standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-492 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement the HLP-005 strategy decision recorded in `decisions.md`: standardize all save-path tests on patching `Paths.SAVES_DIR`; rewrite `test_auto_save.py` to drop `chdir`; consolidate `setup_tmpdir` to the canonical version at `tests/unit/strategy/save_game_service/conftest.py:48`.

**Background:** Per Codex consult, the production save path code uses `Paths.SAVES_DIR` (`game/strategy/systems/save_game_service.py:107-121`). `test_auto_save.py` is the only test that uses cwd-relative save behavior; this is out of step with the production contract.

---

## Tasks

### Task 3.1: Verify canonical setup_tmpdir fixture coverage
**File:** `tests/unit/strategy/save_game_service/conftest.py:48`
**Tests:** none — read-only

- [x] Read the canonical `setup_tmpdir` fixture. Record its signature and behavior.
- [x] Determine whether it can be consumed by `test_auto_save.py` as-is, or needs extension.
- [x] If extension needed, add to Task 3.2.

### Task 3.2: Extend canonical fixture if needed
**File:** `tests/unit/strategy/save_game_service/conftest.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/`

- [x] (Conditional on Task 3.1) Extend canonical with whatever `test_auto_save.py` needs (e.g. configurable subdir, autosave-prefix support).
- [x] Verify existing 75 save_game_service tests still pass.

### Task 3.3: Rewrite test_auto_save.py to Paths.SAVES_DIR
**File:** `tests/unit/strategy/test_auto_save.py` (current chdir setup at lines 26-33)
**Tests:** `pytest tests/unit/strategy/test_auto_save.py`

- [x] Stop using `os.chdir(tmpdir)`.
- [x] Patch `Paths.SAVES_DIR` to `tmpdir` (use `monkeypatch.setattr` or `patch.object`).
- [x] Rewrite each assertion: assert through returned `save_path` and files created at `Paths.SAVES_DIR / <name>`, not cwd-relative paths.
- [x] Verify: tests pass.

### Task 3.4: Migrate test_auto_save.py to canonical setup_tmpdir
**File:** `tests/unit/strategy/test_auto_save.py`
**Tests:** `pytest tests/unit/strategy/test_auto_save.py`

- [x] Delete local tmpdir setup.
- [x] Import canonical `setup_tmpdir` from `tests/unit/strategy/save_game_service/conftest.py`. Note: pytest conftests are auto-discovered up the path; may require relocating fixture or explicit import.
- [x] Verify: tests pass.

### Task 3.5: Verify test_save_selection.py is unchanged
**File:** `tests/unit/ui/test_save_selection.py` (lines 21-33)
**Tests:** `pytest tests/unit/ui/test_save_selection.py`

- [x] Confirm this file already uses `Paths.SAVES_DIR` patching. No change expected.
- [x] If different setup, consider migrating to the canonical fixture as a bonus.

### Task 3.6: Document the production contract in canonical fixture docstring
**File:** `tests/unit/strategy/save_game_service/conftest.py`
**Tests:** none

- [x] Add/update docstring on the canonical `setup_tmpdir`:
  ```
  Patches Paths.SAVES_DIR to a per-test tmpdir. This is the canonical
  save-path test harness; mirrors production save resolution
  (game/strategy/systems/save_game_service.py:107-121). Do not use
  chdir-based variants — the production contract is Paths.SAVES_DIR,
  not cwd. (PROJ-492 decisions.md)
  ```

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `test_auto_save.py` no longer uses `os.chdir`
- [x] Canonical `setup_tmpdir` docstring documents the contract
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-492 ready for audit

_Source: PROJ-479 Phase 6 Task 6.5 + Codex consult finding 6. See [findings/source_review.md](findings/source_review.md)._
