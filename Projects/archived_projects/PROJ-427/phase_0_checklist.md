# Phase 0: Lock current behavior with red tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 0`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Complete (Committed)
**Depends on:** (none — first phase)
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/engine/test_production_spawner.py` (extend)
- `tests/unit/strategy/production_engine/test_spawning.py` (extend)
- `tests/unit/strategy/save_game_service/test_save_load_ops.py` (extend)
- `tests/unit/strategy/design_library/test_scan_designs_caching.py` (extend)
- `tests/integration/strategy/production/test_no_design_disk_read_during_tick.py` (new — initially expected to FAIL on current code; pinned as the explicit no-disk-read guard from the TD-05 risk table)

**Objective:** Add or extend tests that pin the current coupling points before any code changes. The tests must prove the present behavior, not the target behavior: production spawning depends on design lookup, built-count recording, and `save_path` plumbing; `SaveGameService` save/load/delete trigger the module-global replay store; UI design scans reuse per-turn cache state. The new "no design-disk read during a production tick" integration test is added in red form (it is expected to FAIL today because production reads JSON from disk) and is flipped to green by Phase 3.

---

## Tasks

### Task 0.1: Extend production-spawner tests to pin disk + save_path coupling [Simple]
**File:** `tests/unit/strategy/engine/test_production_spawner.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_spawner.py -v`

- [x] Assert `ProductionSpawner` currently imports `DesignLibrary`.
- [x] Assert spawn helpers receive / require `save_path` today.
- [x] Assert a spawn currently triggers a `DesignLibrary(save_path, empire.id)` construction (use a spy or patch).
- [x] **Verify:** tests pass on the current codebase (they are pinning current behavior, not the target).

### Task 0.2: Extend production-engine tests to pin `save_path` threading [Simple]
**File:** `tests/unit/strategy/production_engine/test_spawning.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_spawning.py -v`

- [x] Assert `ProductionEngine` currently threads `save_path` through tick processing.
- [x] **Verify:** test passes on current code.

### Task 0.3: Extend save-game-service tests to pin module-global replay-store [Simple]
**File:** `tests/unit/strategy/save_game_service/test_save_load_ops.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/test_save_load_ops.py -v`

- [x] Assert save / load / delete each notify the replay store currently registered via `set_replay_store(...)`.
- [x] Assert `get_replay_store()` returns the registered instance.
- [x] **Verify:** tests pass on current code.

### Task 0.4: Extend design-library tests to pin per-turn UI cache reuse [Simple]
**File:** `tests/unit/strategy/design_library/test_scan_designs_caching.py`
**Tests:** `pytest tests/unit/strategy/design_library/test_scan_designs_caching.py -v`

- [x] Assert UI design scans reuse per-turn cache state via the current `DesignLibrary` instance.
- [x] **Verify:** test passes on current code.

### Task 0.5: Add the explicit no-disk-read integration test (red) [Medium]
**File:** `tests/integration/strategy/production/test_no_design_disk_read_during_tick.py` (new)
**Tests:** `pytest tests/integration/strategy/production/test_no_design_disk_read_during_tick.py -v`

- [x] Run a production tick with a `DesignLibrary` (or any disk-reading collaborator) whose `scan_designs` / `load_design_data` raise `AssertionError` if invoked.
- [x] Mark the test with `pytest.mark.xfail(strict=True, reason="PROJ-427 Phase 0: current code reads design JSON during the tick; flipped to expected-pass in Phase 3")`.
- [x] **Verify:** test xfails on current code (i.e., it would fail if not xfailed); will be unmarked and assert green in Phase 3.

### Task 0.6: Phase close [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/production/ -q`

- [x] Run focused suites; capture baseline pass count.
- [x] `git status --short` confirms only Phase 0 test files dirty.
- [x] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_0 --repo .worktrees/phases/PROJ-427/phase_0`. _Skipped per split-execution scope; commit recorded on `proj/PROJ-427/main` directly._

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after cumulative review.
- [ ] Update plan.md phase table row.
- [ ] Update plan.md Current State to point to Phase 1.
