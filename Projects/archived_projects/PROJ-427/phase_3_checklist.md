# Phase 3: Migrate runtime production to the catalog

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 3`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Complete (Committed)
**Depends on:** Phase 2
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/production_spawner.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/handlers/construction_queue.py`
- `game/strategy/quickstart_builder.py`
- `tests/unit/strategy/engine/test_production_spawner.py`
- `tests/unit/strategy/production_engine/test_spawning.py`
- `tests/integration/strategy/production/test_completion.py`
- `tests/integration/strategy/production/test_fleet_production_e2e.py`
- `tests/integration/strategy/production/test_no_design_disk_read_during_tick.py` (flip from red to green)
- `tests/unit/quickstart/test_quickstart_builder.py`

**Objective:** Migrate every runtime production / construction-queue / quickstart caller from `DesignLibrary` to `DesignCatalog`. Remove `save_path` plumbing from the spawn call chain. Flip the Phase 0 "no design-disk read during production tick" integration test from xfail to expected-pass. The TD-05 source plan's grep gate at the end of this phase MUST show zero `DesignLibrary` or `save_path` matches in the four touched runtime files.

---

## Tasks

### Task 3.1: Failing tests for catalog-based spawn (TDD-first) [Medium]
**Files:** `tests/unit/strategy/engine/test_production_spawner.py`, `tests/unit/strategy/production_engine/test_spawning.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/production_engine/test_spawning.py -v`

- [ ] Assert spawn paths receive a catalog / catalog-provider, not a `save_path`.
- [ ] Assert spawn paths do not invoke any `DesignRepository.load_design_data` / `scan_designs` during the tick.
- [ ] Update the Phase 0 pinning tests (Task 0.1, 0.2) — invert their expectations to match the post-migration shape.
- [ ] **Verify:** all new assertions fail on current code.

### Task 3.2: Migrate `ProductionSpawner` [Medium]
**File:** `game/strategy/engine/production_spawner.py`
**Tests:** Task 3.1 tests

- [ ] Accept a catalog or catalog-provider dependency in the spawner's constructor / helpers.
- [ ] Remove the `DesignLibrary` import.
- [ ] Stop using `save_path` for design lookup.
- [ ] **Verify:** spawn tests pass; `rg -n "DesignLibrary|save_path" game/strategy/engine/production_spawner.py` returns no matches.

### Task 3.3: Migrate `ProductionEngine` [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ tests/integration/strategy/production/ -v`

- [ ] Stop threading `save_path` through spawn helper methods.
- [ ] Engine receives whatever catalog accessor it needs from the session.
- [ ] **Verify:** `rg -n "DesignLibrary|save_path" game/strategy/engine/production_engine.py` returns no matches.

### Task 3.4: Migrate `AddToConstructionQueueCommandHandler` [Medium]
**File:** `game/strategy/engine/handlers/construction_queue.py`
**Tests:** `pytest tests/unit/strategy/engine/handlers/ -v`

- [ ] Validation and cost lookup go through the catalog.
- [ ] **Verify:** `rg -n "DesignLibrary|save_path" game/strategy/engine/handlers/construction_queue.py` returns no matches.

### Task 3.5: Migrate `quickstart_builder.spawn_initial_complexes` [Medium]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_builder.py -v`

- [ ] Initial-complex spawn reads designs through the catalog (populating it from the repository first if quickstart constructs the session).
- [ ] **Verify:** `rg -n "DesignLibrary|save_path" game/strategy/quickstart_builder.py` returns no matches.

### Task 3.6: Flip the no-disk-read integration test [Simple]
**File:** `tests/integration/strategy/production/test_no_design_disk_read_during_tick.py`
**Tests:** `pytest tests/integration/strategy/production/test_no_design_disk_read_during_tick.py -v`

- [ ] Remove the `xfail` marker from Phase 0.
- [ ] **Verify:** the test now passes without `xfail` — a production tick triggers zero `DesignRepository.scan_designs` / `load_design_data` calls.

### Task 3.7: Source-plan grep gate + phase close [Simple]
**Tests:** focused production + integration suites green; sharded suite green.

- [ ] Run the TD-05 grep gate:
  ```bash
  rg -n "DesignLibrary|save_path" game/strategy/engine/production_spawner.py game/strategy/engine/production_engine.py game/strategy/engine/handlers/construction_queue.py game/strategy/quickstart_builder.py
  ```
  Expected output: no matches.
- [ ] `pytest tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/production_engine/test_spawning.py tests/integration/strategy/production/ tests/unit/strategy/engine/handlers/ tests/unit/quickstart/test_quickstart_builder.py -q` is green.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_3 --repo .worktrees/phases/PROJ-427/phase_3`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] Runtime production no longer requires a save-folder path to resolve design JSON during a tick.
- [ ] The "no design-disk read during production tick" integration test passes without `xfail`.
- [ ] The TD-05 grep gate is clean.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after cumulative review.
- [ ] Update plan.md phase table row.
- [ ] Update plan.md Current State to point to Phase 4.
