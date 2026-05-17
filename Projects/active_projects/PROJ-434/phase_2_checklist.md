# Phase 2: Migrate remaining UI screens + delete `design_library.py` (deletion gate)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-434 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/ui/screens/workshop_ship_io.py`
- `game/ui/screens/strategy_build_queue_manager.py`
- `game/ui/screens/design_selector_window.py`
- `game/strategy/systems/design_library.py` (delete)
- `tests/unit/ui/screens/test_workshop_ship_io.py`
- `tests/unit/ui/screens/test_strategy_build_queue_manager.py`
- `tests/unit/ui/screens/test_design_selector_window.py`
- (~20 other test files identified by Task 2.1 grep)
- `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/systems/save_load.md` (if they reference `DesignLibrary`)

**Objective:** Migrate the three remaining independent UI screens (`workshop_ship_io.py`, `strategy_build_queue_manager.py`, `design_selector_window.py`) and the ~25 remaining test files. Once `rg -n "DesignLibrary" game tests` returns zero live hits outside `design_library.py` itself, delete the file, remove the `DesignLoadResult` re-export shim, and refresh any docs that still reference the old flow.

---

## Tasks

### Task 2.1: Enumerate remaining call sites [Simple]
**Tests:** none (analysis task)

- [ ] Run `rg -n "DesignLibrary" game tests` and capture every remaining hit. Expected sources: `workshop_ship_io.py`, `strategy_build_queue_manager.py` (4 sites), `design_selector_window.py`, and ~25 test files.
- [ ] Group hits by target: which need `DesignCatalog` (runtime reads / UI views) vs `DesignRepository` (disk writes / scans).
- [ ] Record the table in this checklist's Notes section.

### Task 2.2: Migrate `workshop_ship_io.py` (rich save flow + QA-Obs-3) [Complex]
**File:** `game/ui/screens/workshop_ship_io.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_ship_io.py -q`

- [ ] Write failing tests pinning the rich save flow on `DesignCatalog.save_design(...)`: metadata embedding, overwrite-protection, per-turn cache invalidation visible to the same-empire viewer.
- [ ] Replace `DesignLibrary(save_path, empire.id)` construction with the catalog accessor.
- [ ] Route the workshop save through `DesignCatalog.save_design(ship, name, built_designs)` (Phase 0's orchestration method — it calls the repository write + invalidates the cache).
- [ ] Verify the QA-Obs-3 regression test (added in Phase 0) still passes.
- [ ] Update the test fixture's monkeypatch to point at the catalog.

### Task 2.3: Migrate `strategy_build_queue_manager.py` [Complex]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py -q`

- [ ] Write failing tests for each of the 4 `DesignLibrary(...)` construction sites.
- [ ] Replace each with the empire-keyed catalog lookup. Document any subsystem-boundary nuance (e.g., manager threads its catalog reference into sub-managers).
- [ ] Update test fixtures.
- [ ] Confirm green.

### Task 2.4: Migrate `design_selector_window.py` [Complex]
**File:** `game/ui/screens/design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py -q`

- [ ] Write failing tests for `search_designs`, `filter_designs`, `mark_obsolete` call paths against the catalog/repository.
- [ ] Replace the `design_library`-typed constructor parameter with `design_catalog` (and `design_repository` for `mark_obsolete`).
- [ ] Migrate `search_designs` / `filter_designs` callers onto `DesignCatalog`.
- [ ] Migrate `mark_obsolete` onto `DesignRepository`.
- [ ] Update test fixtures.
- [ ] Confirm green.

### Task 2.5: Migrate remaining test fixtures [Standard]
**Files:** ~20 test files from Task 2.1
**Tests:** focused suites for each migrated file

- [ ] For each test file in Task 2.1's enumeration that has not already been touched, repoint the `DesignLibrary` monkeypatch onto `DesignCatalog` / `DesignRepository` at the new import boundary.
- [ ] Confirm focused tests pass after each migration.

### Task 2.6: Deletion gate [Simple]
**Tests:** `rg -n "DesignLibrary" game tests`

- [ ] Run the grep. Expected: zero live hits in `game/` and `tests/` outside `game/strategy/systems/design_library.py` itself (and its own `tests/unit/strategy/design_library/` directory).
- [ ] If anything else still references `DesignLibrary`, do NOT delete — return to Task 2.5.

### Task 2.7: Delete `design_library.py` + remove the `DesignLoadResult` re-export shim [Standard]
**Files:** `game/strategy/systems/design_library.py`, callers of `DesignLoadResult`
**Tests:** focused suites + sharded.

- [ ] Delete `game/strategy/systems/design_library.py`.
- [ ] Delete `tests/unit/strategy/design_library/` (or empty it of `DesignLibrary`-specific tests; keep any that still apply to the new catalog/repository by moving them to the appropriate test package — note this in `findings_ledger.md`).
- [ ] Update every `from game.strategy.systems.design_library import DesignLoadResult` to import from `game.strategy.systems.design_repository` (PROJ-427's dependency-inversion already moved the canonical home there).
- [ ] Verify the focused suites green.

### Task 2.8: Docs refresh [Standard]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/systems/save_load.md`, others flagged by grep
**Tests:** none

- [ ] Run `rg -n "DesignLibrary" docs`. For each hit, update text to reference `DesignRepository` / `DesignCatalog` instead.
- [ ] If any doc described `DesignLibrary` as the runtime design-lookup mechanism, update it to describe the catalog/repository split.

### Task 2.9: Phase close + final sharded gate [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green.
- [ ] `rg -n "DesignLibrary" game tests docs` returns zero hits (historical mentions in `Projects/active_projects/PROJ-427/*.md` are acceptable — those are immutable history).
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-434 phase_2 --repo .worktrees/phases/PROJ-434/phase_2`.

---

## Notes

Triage table (filled during Task 2.1):

| Caller | Needs | Target |
|--------|-------|--------|
| (filled during implementation) | | |

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `workshop_ship_io.py`, `strategy_build_queue_manager.py`, `design_selector_window.py` all off `DesignLibrary`
- [ ] All test fixtures repointed onto the catalog/repository
- [ ] `game/strategy/systems/design_library.py` deleted
- [ ] `DesignLoadResult` re-export shim removed
- [ ] Docs refreshed
- [ ] `rg -n "DesignLibrary" game tests docs` returns zero live hits
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project execution complete; PROJ-427 Phase 6 deletion gate met"
