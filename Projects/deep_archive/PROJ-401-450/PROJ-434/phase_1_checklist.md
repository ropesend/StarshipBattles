# Phase 1: Migrate `BuildQueueScreen` + 3 panel collaborators

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-434 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/build_queue_controller.py`
- `game/ui/screens/build_queue_drag_handler.py`
- `game/ui/screens/build_queue_portrait_loader.py`
- `tests/unit/ui/screens/test_build_queue_screen.py`
- `tests/unit/ui/screens/test_build_queue_controller.py`
- `tests/unit/ui/screens/test_build_queue_drag_handler.py`
- `tests/unit/ui/screens/test_build_queue_portrait_loader.py`

**Objective:** Migrate the `BuildQueueScreen` collaborator chain (screen + controller + drag handler + portrait loader) off `DesignLibrary` onto the `DesignCatalog` / `DesignRepository` pair. The four files share `DesignLibrary` state and must migrate atomically — partial migration would orphan one collaborator from the others' state. This phase also proves the migration pattern that Phase 2 will apply to the remaining three independent UI screens.

---

## Tasks

### Task 1.1: Enumerate the migration surface [Simple]
**Tests:** none (analysis task)

- [ ] Run `rg -n "DesignLibrary" game/ui/screens/build_queue_screen.py game/ui/screens/build_queue_controller.py game/ui/screens/build_queue_drag_handler.py game/ui/screens/build_queue_portrait_loader.py`. Record every call site and what method each one calls.
- [ ] Run `rg -n "DesignLibrary" tests/unit/ui/screens/test_build_queue_*`. Record every monkeypatch site.
- [ ] If any of the four production files turns out to share its `DesignLibrary` reference with another file outside this set, surface in `findings_ledger.md` and re-scope before continuing.

### Task 1.2: Migrate `build_queue_screen.py` (entry point) [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py -q`

- [ ] Write a failing test that constructs `BuildQueueScreen` with a catalog reference (not a `DesignLibrary`) and asserts the screen still renders.
- [ ] Replace `DesignLibrary(save_path, empire.id)` construction with `session.services.design_catalogs_by_empire[empire.id]`.
- [ ] Update the screen's constructor signature: replace `design_library` parameter with `design_catalog` (and `design_repository` if any direct repository write is needed).
- [ ] Thread the catalog reference into the three panel collaborators rather than re-constructing per-collaborator.
- [ ] Verify test passes.

### Task 1.3: Migrate `build_queue_controller.py` [Medium]
**File:** `game/ui/screens/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_controller.py -q`

- [ ] Write a failing test pinning each `scan_designs` / `load_design_data` call on the catalog.
- [ ] Replace `DesignLibrary` calls: `scan_designs` → `design_repository.scan_designs(empire_id)` via catalog accessor, `load_design_data` → `design_repository.load_design_data(design_id)`.
- [ ] Update constructor signature parallel to Task 1.2.
- [ ] Verify test passes.

### Task 1.4: Migrate `build_queue_drag_handler.py` [Standard]
**File:** `game/ui/screens/build_queue_drag_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_drag_handler.py -q`

- [ ] Write a failing test for the drag-preview metadata read path on the catalog.
- [ ] Replace `DesignLibrary.load_design_data` callers with `design_catalog.load_design_data` (or the catalog's design-lookup accessor — match whichever the Phase 0 surface exposes).
- [ ] Update constructor signature parallel to Task 1.2.
- [ ] Verify test passes.

### Task 1.5: Migrate `build_queue_portrait_loader.py` [Standard]
**File:** `game/ui/screens/build_queue_portrait_loader.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_portrait_loader.py -q`

- [ ] Write a failing test for the portrait-cache keying through the repository's `get_design_path`.
- [ ] Replace `DesignLibrary.get_design_path` callers with `design_repository.get_design_path`. Cache keying logic is unchanged; only the lookup target moves.
- [ ] Update constructor signature parallel to Task 1.2.
- [ ] Verify test passes.

### Task 1.6: Repoint test fixtures [Standard]
**Files:** `tests/unit/ui/screens/test_build_queue_*.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_*.py -q`

- [ ] Repoint every `DesignLibrary` monkeypatch onto `DesignCatalog` / `DesignRepository` at the appropriate import boundary.
- [ ] Confirm all four files' tests are green.

### Task 1.7: Sharded smoke + caller drift check [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green.
- [ ] `rg -n "DesignLibrary" game/ui/screens/build_queue_*.py` returns zero hits (this family is fully migrated).
- [ ] `rg -n "DesignLibrary" game tests` still returns hits in `workshop_ship_io.py`, `strategy_build_queue_manager.py`, `design_selector_window.py`, and their test files — those land in Phase 2.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-434 phase_1 --repo .worktrees/phases/PROJ-434/phase_1`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BuildQueueScreen` + 3 panel collaborators fully off `DesignLibrary`
- [ ] Their test fixtures repointed onto the catalog/repository
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
