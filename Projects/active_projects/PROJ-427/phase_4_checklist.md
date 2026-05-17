# Phase 4: Built-count write-back (deferred, no mid-tick disk writes)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 4`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Not Started
**Depends on:** Phase 3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/systems/design_catalog.py` (edit)
- `game/strategy/systems/design_repository.py` (edit if needed)
- `game/strategy/systems/save_game_service.py` (edit — built-count flush only; replay-store conversion lives in Phase 5)
- `tests/unit/strategy/design_catalog/test_pending_built_count_flush.py` (new)
- `tests/unit/strategy/save_game_service/test_built_count_flush_on_save.py` (new)

**Objective:** Wire the deferred built-count write-back: `DesignCatalog` tracks pending increments in memory during the tick; `SaveGameService` at save time flushes those increments through `DesignRepository`. **No save-schema change.** **No `Empire.designs_built_count` field.** No mid-tick disk write.

This phase does NOT touch the replay store; that conversion is Phase 5.

---

## Tasks

### Task 4.1: Failing tests for deferred flush (TDD-first) [Medium]
**Files:** `tests/unit/strategy/design_catalog/test_pending_built_count_flush.py` (new), `tests/unit/strategy/save_game_service/test_built_count_flush_on_save.py` (new)
**Tests:** `pytest tests/unit/strategy/design_catalog/ tests/unit/strategy/save_game_service/ -v`

- [ ] `test_pending_increment_does_not_call_repository_during_tick` — production spawn records an increment in catalog memory; assert `DesignRepository.increment_built_count` is never called during the tick.
- [ ] `test_save_flushes_pending_increments_through_repository` — running `SaveGameService.save(...)` invokes `DesignRepository.increment_built_count` once per pending entry; catalog's pending dict empties.
- [ ] `test_save_with_no_pending_increments_is_a_noop_on_repository` — guard the empty-flush case.
- [ ] **Verify:** all tests fail.

### Task 4.2: Implement catalog pending-increment + save-time flush [Medium]
**Files:** `game/strategy/systems/design_catalog.py`, `game/strategy/systems/save_game_service.py`, `game/strategy/systems/design_repository.py`
**Tests:** Task 4.1 tests

- [ ] Catalog's pending-increment dict already exists from Phase 2; add a `flush_pending(repository)` (or equivalent) method.
- [ ] `SaveGameService.save(...)` calls `flush_pending(...)` on every owning catalog before writing the save.
- [ ] **No** `Empire.designs_built_count` field. **No** save-format change.
- [ ] **Verify:** Task 4.1 tests pass.

### Task 4.3: Phase close [Simple]
**Tests:** focused suites green; sharded suite green.

- [ ] `pytest tests/unit/strategy/design_catalog/ tests/unit/strategy/save_game_service/ tests/integration/strategy/production/ -q` is green.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_4 --repo .worktrees/phases/PROJ-427/phase_4`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] No mid-tick disk writes for built counts.
- [ ] Save-format is unchanged from before this project started.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after cumulative review.
- [ ] Update plan.md phase table row.
- [ ] Update plan.md Current State to point to Phase 5.
