# Phase 2: Introduce `DesignCatalog` and move cache ownership

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 2`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Complete (Committed) — scope-narrowed: absorption only; cache migration + game_session accessor deferred to Phase 6 per the split-execution plan
**Depends on:** Phase 1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/systems/design_catalog.py` (new)
- `game/strategy/facade/slices/_facade_state.py` (edit)
- `game/strategy/engine/game_session.py` (edit)
- `tests/unit/strategy/design_catalog/` (new test package)

**Objective:** Introduce a per-empire `DesignCatalog` that owns in-memory design lookup, per-turn UI cache views, and pending built-count increments. Populate catalogs from `DesignRepository` at session/bootstrap boundaries only — never during a production tick. Move `FacadeSessionState.designs_by_empire` behavior into the catalog. Add `GameSession.get_design_catalog(empire_id)` (or `design_catalogs_by_empire[empire_id]`). `DesignLibrary` is **not** removed in this phase.

---

## Tasks

### Task 2.1: Define `DesignCatalog` unit tests (TDD-first) [Medium]
**File:** `tests/unit/strategy/design_catalog/test_catalog.py` (new)
**Tests:** `pytest tests/unit/strategy/design_catalog/ -v`

- [x] `test_lookup_returns_design_by_id_without_disk_access` — catalog is constructed pre-populated; assert no `DesignRepository` method is called during `lookup`.
- [x] `test_filtered_views_for_ui_per_turn`.
- [x] `test_pending_built_count_increment_does_not_write_to_disk` — increment recorded in memory only.
- [x] `test_refresh_repopulates_from_repository`.
- [x] `test_catalog_is_per_empire` — two empires get distinct catalog instances with distinct contents.
- [x] **Verify:** all 7 tests failed prior to implementation; all green after.

### Task 2.2: Implement `DesignCatalog` [Medium]
**File:** `game/strategy/systems/design_catalog.py` (new)
**Tests:** Task 2.1 tests

- [x] Implement per-empire catalog with `lookup`, list view, `record_built` pending-increment, `repopulate_from(repository)`.
- [x] **No** filesystem call; **no** JSON parsing in `DesignCatalog` itself.
- [x] **Verify:** Task 2.1 tests pass.

### Task 2.3: Migrate `FacadeSessionState.designs_by_empire` into the catalog [Medium]
**File:** `game/strategy/facade/slices/_facade_state.py`
**Tests:** existing facade tests + `tests/unit/strategy/design_catalog/test_facade_state_cache.py` (new)

- [ ] **DEFERRED to Phase 6:** this is a UI-caller migration (the facade-state cache is read by `workshop_ship_io.py` / `strategy_build_queue_manager.py` / `transfer_controller.py`). Per the orchestrator-imposed split-execution scope, Phase 2 in this run absorbs catalogs into `SessionRuntimeServices` only and leaves existing `DesignLibrary` callers untouched. The cache migration moves into Phase 6 alongside the UI-caller deletion gate. Decision logged 2026-05-17 in `decisions.md`.

### Task 2.4: Add `GameSession` accessor [Simple]
**File:** `game/strategy/engine/session/runtime_services.py`, `game/strategy/engine/session/bootstrap.py`, `game/strategy/engine/session/persistence_adapter.py`
**Tests:** `tests/unit/strategy/engine/session/test_bootstrap.py`, `tests/unit/strategy/engine/session/test_runtime_services.py`

- [x] Absorbed directly into `SessionRuntimeServices` per the PROJ-423 cross-plan note (TD-02 has landed). Added two new fields: `design_repository: DesignRepository | None` and `design_catalogs_by_empire: Mapping[int, DesignCatalog]`. Access pattern is `session.services.design_catalogs_by_empire[empire_id]`. No `GameSession.get_design_catalog(...)` method added; the bag access is the canonical surface (consistent with the rest of the wired-services contract).
- [x] Populate catalogs at bootstrap: `SessionBootstrap._build_services` constructs a session-level `DesignRepository`; `SessionBootstrap.new_game_state` and `SessionPersistenceAdapter.rehydrate_state` build per-empire `DesignCatalog` instances after empires are known (using `dataclasses.replace` to re-wrap the frozen services bag). Each catalog is seeded via `repopulate_from(DesignRepository(save_path, empire_id=emp.id))`.
- [x] **Cross-plan absorption:** decision logged in `decisions.md`. PROJ-423 had already landed; the catalog map lives on `SessionRuntimeServices` itself (not on `SessionBootstrapState`).
- [x] **Verify:** new accessor tests pass; anti-drift `test_init_and_from_dict_use_identical_service_classes` extended and green; round-trip remains byte-identical (1821/1821 focused tests green).

### Task 2.5: Phase close [Simple]
**Tests:** `pytest tests/unit/strategy/design_catalog/ tests/unit/strategy/engine/ tests/unit/strategy/facade/ -q`

- [x] Existing production / UI callers still use `DesignLibrary` (no migration in this phase).
- [x] Focused suites green: 1821/1821 across engine/, design_catalog/, design_repository/, design_library/, save_game_service/, facade/. Full sharded-suite gate is deferred to the end of Phase 3-6 execution per the split-execution plan.
- [x] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_2 --repo .worktrees/phases/PROJ-427/phase_2`. _Skipped per split-execution scope; commit recorded on `proj/PROJ-427/main` directly._

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] `DesignCatalog` exists, is per-empire, has no filesystem dependency.
- [ ] `FacadeSessionState.designs_by_empire` UI cache served by catalog.
- [ ] `GameSession.get_design_catalog(empire_id)` exists.
- [ ] No production-spawn or construction-queue caller is migrated yet.
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after cumulative review.
- [ ] Update plan.md phase table row.
- [ ] Update plan.md Current State to point to Phase 3.
