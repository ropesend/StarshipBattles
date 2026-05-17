# Phase 5: Convert `SaveGameService` to instance-owned replay-store wiring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 5`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Not Started
**Depends on:** Phase 4
**Review Mode:** standard
**Files (planned):**
- `game/strategy/systems/save_game_service.py`
- `game/app_bootstrap.py`
- all `SaveGameService.` call sites found by grep
- `tests/unit/strategy/save_game_service/test_save_load_ops.py` (extend)
- `tests/unit/strategy/save_game_service/test_error_handling.py` (extend)
- `tests/integration/replay/test_replay_store.py` (extend)

**Objective:** Remove the module-global `_replay_store`, `set_replay_store`, `get_replay_store`. Convert `SaveGameService` to constructor-injected `replay_store` ownership. Wire bootstrap to construct a service instance. **All `SaveGameService` call sites move in this single phase** — no half-static / half-instance period.

---

## Tasks

### Task 5.1: Failing tests for instance-owned replay-store (TDD-first) [Medium]
**File:** `tests/unit/strategy/save_game_service/test_save_load_ops.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/ -v`

- [ ] Construct `SaveGameService(replay_store=spy_store)`.
- [ ] Assert `save(...)`, `load(...)`, `delete(...)` each invoke the corresponding spy notification with the right save root.
- [ ] Add a test that `SaveGameService(replay_store=None)` works (no notifications, no crash).
- [ ] **Verify:** tests fail — current code uses the module-global.

### Task 5.2: Convert `SaveGameService` to instance ownership [Medium]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** Task 5.1 tests

- [ ] Add `replay_store` constructor parameter (keyword-only); store on `self._replay_store`.
- [ ] Convert save / load / delete replay-store notifications to use `self._replay_store`.
- [ ] **Remove** module-level `_replay_store`, `set_replay_store`, `get_replay_store`.
- [ ] **Verify:** Task 5.1 tests pass.

### Task 5.3: Update bootstrap and all call sites [Medium]
**Files:** `game/app_bootstrap.py`, every `SaveGameService.` call site found by grep
**Tests:** `pytest tests/ -q`

- [ ] Bootstrap constructs a single `SaveGameService(replay_store=...)` instance and wires it where the global was previously read.
- [ ] Migrate every test that used `set_replay_store(...)` / `get_replay_store()` to construct service instances directly.
- [ ] **Verify:** sharded suite green.

### Task 5.4: Source-plan grep gate [Simple]
**Tests:** grep + sharded suite.

- [ ] Run the TD-05 grep gate:
  ```bash
  rg -n "_replay_store|set_replay_store|get_replay_store|SaveGameService\." game tests
  ```
  Expected output: zero matches in `game/` for the static names; only legitimate instance-method calls for `SaveGameService.`.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.

### Task 5.5: Phase close [Simple]

- [ ] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_5 --repo .worktrees/phases/PROJ-427/phase_5`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] Module-global `_replay_store`, `set_replay_store`, `get_replay_store` are removed.
- [ ] All call sites construct `SaveGameService` instances with constructor-injected replay store.
- [ ] No half-static / half-instance leftovers.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after cumulative review.
- [ ] Update plan.md phase table row.
- [ ] Update plan.md Current State to point to Phase 6.
