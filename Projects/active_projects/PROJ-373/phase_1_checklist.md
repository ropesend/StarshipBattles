# Phase 1: Cache `_validate_designs` results

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-373 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Cache validation results in `BuildQueueController` keyed by `(design_id, file_mtime)`. On a repeat call to `_validate_designs` with unchanged designs, every entry is a cache hit and neither `Ship.from_dict` nor `validator.validate` runs. Saves ~2.2s per repeat build-queue open. Cache invalidates correctly when a design's on-disk JSON is modified.

---

## Pre-flight (TDD baseline)

- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count; pin in plan.md Current State
- [ ] Re-read [findings/profile_summary.md](findings/profile_summary.md) for the 2.2s `_validate_designs` line item
- [ ] Re-read `_validate_designs` at [build_queue_controller.py:193-218](../../../game/ui/panels/build_queue_controller.py#L193) and the call site at line 137 (`load_designs_by_category`); confirm there are no other callers (`grep -rn '_validate_designs' game/ tests/`)
- [ ] Identify which `DesignLibrary` method returns the on-disk path for a `design_id` — the cache fingerprint depends on `os.stat(path).st_mtime`. Likely path-resolution helper near `load_design_data`. If no method exists, plan for adding one.

---

## Tasks

### Task 1.1: Add cache miss/hit unit tests (TDD-first) [Simple]
**File:** `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py -v -k validation_cache`

- [ ] Add a test class `TestValidationCache` (or extend the existing test module).
- [ ] Test 1: `test_first_call_validates_each_design` — fresh controller, mocked validator counts calls. `_validate_designs([d1, d2])` invokes `validator.validate` exactly twice; both designs end with `design_valid` set.
- [ ] Test 2: `test_repeat_call_uses_cache` — call `_validate_designs([d1, d2])` twice in a row with same designs. Validator called twice total (not 4×). Both designs still `design_valid`.
- [ ] Test 3: `test_mtime_change_invalidates_one_entry` — call once, change one design's mtime (touch the file or stub the fingerprint helper), call again. Validator called 3× total: 2 for first call, 1 for the changed design on second call.
- [ ] Test 4: `test_validator_exception_does_not_poison_cache` — make validator raise on first call; controller logs and falls through to `design_valid = True` (matching today's behavior). On second call, the validator runs again — no stale cache entry.
- [ ] Test 5: `test_cache_survives_category_switch` — same controller, two `_validate_designs` calls with overlapping design lists from different categories. Validator only called for unique design_ids across both calls.
- [ ] Run the tests; **confirm they fail** on the current code (no cache yet).
- [ ] **Verify:** failures match the expected reasons (e.g., test 2 fails because validator is called 4× not 2×).

**Notes:**

### Task 1.2: Add fingerprint helper [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py -v -k fingerprint`

- [ ] Add private method `_design_fingerprint(self, design_id: str) -> Any` that returns `os.stat(<design_path>).st_mtime_ns` for the design's on-disk JSON.
- [ ] If `DesignLibrary` exposes a `path_for_design(design_id)` (or equivalent) helper, use it. Otherwise, mirror whatever path-resolution pattern `load_design_data` uses internally (read the source first; do NOT replicate path logic if a helper exists).
- [ ] Handle missing-file case: return `None` (or a sentinel) so the cache check treats it as a miss, falls through to validator.
- [ ] Add a focused unit test for the fingerprint helper (mocked filesystem) — same path returns same value, different mtime returns different value, missing file returns `None`.
- [ ] **Verify:** tests pass.

**Notes:** If a path-resolution helper does not exist on `DesignLibrary`, add one as a minimal getter — do not embed path logic into `BuildQueueController`.

### Task 1.3: Add cache attribute and integrate into `_validate_designs` [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py -v -k validation_cache`

- [ ] In `__init__`, add `self._validation_cache: Dict[str, Tuple[Any, bool]] = {}` (design_id → (fingerprint, valid_bool)).
- [ ] In `_validate_designs`:
  - For each design, compute fingerprint via `self._design_fingerprint(d.design_id)`.
  - If `(d.design_id, fingerprint)` is in cache, set `d.design_valid` from the cached value and `continue`.
  - On miss, run the existing load + validate logic. After determining `d.design_valid`, store `self._validation_cache[d.design_id] = (fingerprint, d.design_valid)`.
  - On the load-result-failure branch (existing `if not load_result.success: d.design_valid = False; continue`), still update the cache so we don't re-attempt every call.
  - On the broad `except Exception` branch (existing `d.design_valid = True`), do NOT cache — the failure may be transient. (Confirms test 1.1#4.)
- [ ] **Verify:** Tasks 1.1 tests now pass.

**Notes:** Keep the existing comment on the `except Exception` line (reason: design validation traverses arbitrary registry/save data; queue panel must remain usable on validator failure).

### Task 1.4: Eliminate per-call validator construction [Simple]
**File:** `game/ui/panels/build_queue_controller.py`

- [ ] `_validate_designs` currently constructs `DesignValidator(self._registries)` on every call (line 206). On a cache-hit-only call, the validator is never used — but Python still pays the construction cost.
- [ ] Move validator construction inside the loop, gated by "miss" — only construct when we hit the first miss. (Or: lazy-initialize on the controller instance: `self._validator = self._validator or DesignValidator(...)` and reuse.)
- [ ] **Verify:** golden tests still pass; `_validate_designs` cache-only invocation does not import or construct `DesignValidator`.

**Notes:** Trivial perf nit; included so the cache hit path is fully zero-cost.

### Task 1.5: Add `BuildQueueController.reset_filters()` [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** existing controller tests

- [ ] Add public method `reset_filters(self) -> None` that sets `self.selected_category = "complex"` and `self.selected_role = "Any"`.
- [ ] Do not call `on_queue_changed` from inside `reset_filters` — the caller decides whether to refresh.
- [ ] Add a unit test verifying both attributes are reset.

**Notes:** Phase 2 prerequisite. Adding it here keeps controller changes scoped to one phase.

### Task 1.6: Manual smoke + re-profile [Simple]
**Tests:** Manual + `python Tools/profile_game/profile_game.py`

- [ ] Launch the game; open the build queue 3 times in a row at the same yard.
- [ ] In the resulting pyinstrument HTML, confirm `_validate_designs` cumulative time on the 2nd and 3rd opens is ≪ first open (close to zero).
- [ ] Edit a design (workshop save) → reopen build queue → confirm only the edited design re-validates.
- [ ] Capture before/after numbers and add to plan.md Current State as evidence.
- [ ] **Verify:** Visual behavior unchanged — invalid designs still show as invalid in the UI.

**Notes:**

### Task 1.7: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ baseline + new tests from Tasks 1.1, 1.2, 1.5.
- [ ] **Acceptance:** zero regressions in pass count.

**Notes:**

### Task 1.8: Commit Phase 1 [Simple]

- [ ] `git status --short` to confirm only Phase 1 files are dirty.
- [ ] Commit message: `feat(PROJ-373): Phase 1 — cache _validate_designs results in BuildQueueController`
- [ ] Co-author trailer: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- [ ] Do NOT push.
- [ ] **Verify:** `git show --stat HEAD` shows only in-scope files.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_validate_designs` is cache-aware; mtime invalidation verified
- [ ] `BuildQueueController.reset_filters()` exists (Phase 2 prerequisite)
- [ ] Re-profiled: 2nd-and-later validate calls are ~zero
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
