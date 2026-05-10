# Phase 3: Delete `_capture_baseline.py` + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-379 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** lightweight
**Files (planned):**
- `tests/fixtures/saves/_capture_baseline.py` (DELETE)

**Objective:** Delete the old capture script. Its `_normalize_image_fields`, double-seed pattern, and best-effort docstring are all superseded by `_build_galaxy_fixture.py`. Verify no other code imports or references it.

---

## Tasks

### Task 3.1: Grep for references [Simple]
**File:** N/A — verification only
**Tests:** N/A

- [x] Run `Grep` over `tests/`, `Tools/`, `docs/`, `Projects/active_projects/`, and `game/` for the literal string `_capture_baseline`. Expected matches:
  - `tests/fixtures/saves/_capture_baseline.py` itself (the file being deleted)
  - References in PROJ-377 `decisions.md` and PROJ-379 docs (these document the historical script — leave them; they correctly describe the past)
  - Possibly a docstring in `tests/integration/strategy/test_save_round_trip.py` mentioning the old capture script — update to reference `_build_galaxy_fixture.py` if found
- [x] If any production code or live test imports `_capture_baseline`, STOP — surface to user. Should not happen; PROJ-377 design constrained the script to standalone.

**Notes:**

### Task 3.2: Delete the file [Simple]
**File:** `tests/fixtures/saves/_capture_baseline.py`
**Tests:** N/A

- [x] `git rm tests/fixtures/saves/_capture_baseline.py`.
- [x] **Verify:** `git status --short` shows the deletion staged.
- [x] **Verify:** `ls tests/fixtures/saves/` shows only `_build_galaxy_fixture.py`, `galaxy_proj372_baseline.json`, `galaxy_proj372_populated.json`.

**Notes:**

### Task 3.3: Update any stale docstring references [Simple]
**File:** `tests/integration/strategy/test_save_round_trip.py` (potentially)
**Tests:** `pytest tests/integration/strategy/test_save_round_trip.py -v --override-ini="addopts="`

- [x] If the module docstring at the top of `test_save_round_trip.py` references `_capture_baseline.py`, replace with a reference to `_build_galaxy_fixture.py` and PROJ-379.
- [x] If any other docstrings in `tests/` mention the old script, update similarly.
- [x] **Verify:** focused test run passes.

**Notes:**

### Task 3.4: Run sharded suite + commit Phase 3 [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded green; pass count unchanged from Phase 2 close.
- [x] `git status --short` confirms only `_capture_baseline.py` deletion (and any docstring update).
- [x] Commit message: `PROJ-379 phase 3: delete _capture_baseline.py (superseded by _build_galaxy_fixture.py)`.
- [x] **Verify:** `git log -1 --stat`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] `_capture_baseline.py` no longer exists.
- [x] `Grep` for `_capture_baseline` over `tests/` + `Tools/` + `game/` returns zero matches outside of historical doc references in `Projects/active_projects/`.
- [x] Sharded suite green.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 4.
