# Phase 6: Migrate UI callers and delete the old `DesignLibrary` shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 6`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Not Started
**Depends on:** Phase 5
**Review Mode:** standard
**Files (planned):**
- `game/ui/screens/workshop_ship_io.py`
- `game/ui/screens/strategy_build_queue_manager.py`
- `game/ui/screens/transfer_controller.py`
- (any other site discovered by `rg -n "DesignLibrary"`)
- `game/strategy/systems/design_library.py` (delete, or reduce to zero-logic alias)
- `docs/01_ARCHITECTURE.md` (edit if flow descriptions change)
- `docs/02_PATTERNS.md` (edit if patterns change)
- `docs/systems/save_load.md` (edit if save-load flow descriptions change)

**Objective:** Migrate every remaining `DesignLibrary(...)` caller to `DesignCatalog` (runtime reads) or `DesignRepository` (disk writes). Pass the deletion gate. Delete `design_library.py` or reduce it to a zero-logic alias that a separate immediate follow-up will remove. Refresh any docs that described runtime design-lookup flow.

---

## Tasks

### Task 6.1: Grep and triage remaining callers [Simple]
**Tests:** none (preparatory).

- [ ] Run `rg -n "DesignLibrary" game tests docs` and capture the full list.
- [ ] For each caller, decide whether it needs `DesignCatalog` (runtime reads / UI views) or `DesignRepository` (disk writes / scans).
- [ ] Record the triage table in this checklist's Notes section below.

### Task 6.2: Migrate UI callers [Medium]
**Files:** every UI caller from Task 6.1
**Tests:** UI screen tests covering the migrated screens; sharded suite.

- [ ] Migrate `workshop_ship_io.py` — workshop save writes go through `DesignRepository`; lookup goes through `DesignCatalog`; on save, refresh the catalog.
- [ ] Migrate `strategy_build_queue_manager.py` — design lookup for build-queue panels goes through `DesignCatalog`.
- [ ] Migrate `transfer_controller.py` — design lookup goes through `DesignCatalog`.
- [ ] Migrate any other site found by Task 6.1.
- [ ] **Verify:** all affected UI tests pass; UI sees newly saved designs through the new catalog path.

### Task 6.3: Deletion gate [Simple]
**Tests:** grep + focused suite.

- [ ] Run `rg -n "DesignLibrary" game tests docs` — expected output: no production or UI caller hits; only `design_library.py` itself (and possibly its own tests) remain.
- [ ] If anything else still references `DesignLibrary`, do NOT delete — return to Task 6.2.

### Task 6.4: Delete or alias `DesignLibrary` [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/design_library/ -v`

- [ ] If clean deletion is possible, delete the file and its test directory.
- [ ] If a zero-logic alias is required for a transient import (record the reason in [`decisions.md`](decisions.md)), reduce the file to a one-line alias and schedule its removal as a separate immediate follow-up.
- [ ] **Verify:** sharded suite green.

### Task 6.5: Docs refresh [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/systems/save_load.md`

- [ ] Update any text that described the old `DesignLibrary` runtime flow.
- [ ] Document the `DesignRepository` / `DesignCatalog` split and the per-empire catalog model.
- [ ] Note that `SaveGameService` is now instance-owned.

### Task 6.6: Phase close [Simple]
**Tests:** all focused suites + sharded suite green.

- [ ] `pytest tests/unit/strategy/design_catalog/ tests/unit/strategy/design_repository/ tests/unit/strategy/save_game_service/ tests/integration/strategy/production/ tests/integration/replay/test_replay_store.py tests/unit/quickstart/test_quickstart_builder.py tests/unit/ui/screens/ -q` is green.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_6 --repo .worktrees/phases/PROJ-427/phase_6`.

---

## Notes

Triage table (filled during Task 6.1):

| Caller | Needs | Target |
|--------|-------|--------|
| (filled during implementation) | | |

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] No live production or UI caller imports `DesignLibrary`.
- [ ] `design_library.py` is deleted (or is a zero-logic alias with an immediate-follow-up plan recorded in [`decisions.md`](decisions.md)).
- [ ] Docs reflect the new repository / catalog split and the instance-owned replay store.
- [ ] Project-level verification checklist in [`plan.md`](plan.md) is fully checked.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after final cumulative review and audit.
- [ ] Update plan.md phase table row.
- [ ] Project enters final-audit gate.
