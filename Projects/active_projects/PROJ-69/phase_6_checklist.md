# Phase 6: Test Updates & Integration Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Comprehensive testing of all changes, update broken tests, add new test coverage.

---

## Tasks

### Task 6.1: Update production engine tests [Medium]
**Files:** `tests/unit/strategy/production_engine/test_basics.py`, `test_completion.py`, `test_spawning.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] Review all existing tests for assumptions about single-queue processing
- [ ] Update test fixtures that create planets with queues:
  - Existing `colony.construction_queue` usage should still work for base queue (complexes)
  - Add facility-level queues to test planets where needed
- [ ] Add test: planet base queue processes complex item
- [ ] Add test: planet base queue skips ship-type item (doesn't process)
- [ ] Add test: shipyard facility queue processes ship item
- [ ] Add test: shipyard facility queue processes complex item
- [ ] Add test: 2 shipyard facilities process 2 items simultaneously in one turn
- [ ] Add test: facility queue completion triggers correct spawner
- [ ] Add test: non-operational shipyard facility queue is skipped
- [ ] Verify: run `pytest tests/unit/strategy/production_engine/ -v` - all pass

**Notes:**

---

### Task 6.2: Update integration tests [Medium]
**Files:** `tests/integration/strategy/production/test_queue.py`, `test_completion.py`, `test_fleet_production_e2e.py`, `test_fleet_save_load.py`
**Tests:** `pytest tests/integration/strategy/production/ -v`

- [ ] Review integration tests for single-queue assumptions
- [ ] Update E2E tests if they rely on `colony.construction_queue` for ship items
- [ ] Add E2E test: planet with 2 shipyards + queued items → process 2 turns → both complete
- [ ] Add E2E test: save game with facility queues → load → queues preserved → process turn → items complete
- [ ] Verify fleet E2E tests still pass unchanged
- [ ] Verify: run `pytest tests/integration/strategy/production/ -v` - all pass

**Notes:**

---

### Task 6.3: Add BuildQueueSource and UI tests [Medium]
**Files:** `tests/unit/strategy/data/test_build_queue_source.py` (if not created in Phase 1), `tests/unit/ui/screens/`
**Tests:** `pytest tests/unit/ -k "build_queue"`

- [ ] Ensure `test_build_queue_source.py` covers all edge cases (created in Phase 1, verify completeness):
  - Empty hex (no planets, no fleets)
  - Planet with no facilities
  - Planet with mixed operational/non-operational facilities
  - Fleet without space yard excluded
  - Multiple planets at same hex
  - Queue source references point to actual queue objects (mutations reflected)
- [ ] Add controller tests for multi-queue add behavior
- [ ] Add test: controller adds to single active queue
- [ ] Add test: controller adds to all selected queues in multi-select
- [ ] Add test: controller respects `can_build_ships`/`can_build_complexes` flags
- [ ] Verify: run all build queue related tests

**Notes:**

---

### Task 6.4: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run `pytest tests/ -n 12` - all pass (expect 6517+ passed)
- [ ] Verify no new test failures beyond known flaky tests (test_stats_render, test_structure_visibility)
- [ ] Manual smoke test:
  - Open game → select planet → click Build Yard
  - Verify queue selector shows correct queues
  - Select single queue → verify contents shown
  - Add item → verify it appears in queue
  - Select multiple queues → verify "Adding to N queues" message
  - Add item in multi-select → verify all selected queues get the item
  - Close and reopen → verify state persists
  - End turn → verify parallel processing works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Manual smoke test completed successfully
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete - All phases done"
