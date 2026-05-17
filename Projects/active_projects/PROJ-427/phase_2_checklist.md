# Phase 2: Introduce `DesignCatalog` and move cache ownership

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-427 2`
> 2. Only proceed if output shows PASSED.
> 3. Update plan.md phase table AND Current State.

**Status:** Not Started
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

- [ ] `test_lookup_returns_design_by_id_without_disk_access` — catalog is constructed pre-populated; assert no `DesignRepository` method is called during `lookup`.
- [ ] `test_filtered_views_for_ui_per_turn`.
- [ ] `test_pending_built_count_increment_does_not_write_to_disk` — increment recorded in memory only.
- [ ] `test_refresh_repopulates_from_repository`.
- [ ] `test_catalog_is_per_empire` — two empires get distinct catalog instances with distinct contents.
- [ ] **Verify:** all tests fail — `DesignCatalog` does not exist yet.

### Task 2.2: Implement `DesignCatalog` [Medium]
**File:** `game/strategy/systems/design_catalog.py` (new)
**Tests:** Task 2.1 tests

- [ ] Implement per-empire catalog with `lookup`, filtered/list views, pending-increment dict, `refresh()` / `repopulate_from(repository)`.
- [ ] **No** filesystem call; **no** JSON parsing.
- [ ] **Verify:** Task 2.1 tests pass.

### Task 2.3: Migrate `FacadeSessionState.designs_by_empire` into the catalog [Medium]
**File:** `game/strategy/facade/slices/_facade_state.py`
**Tests:** existing facade tests + `tests/unit/strategy/design_catalog/test_facade_state_cache.py` (new)

- [ ] `designs_by_empire` becomes a view backed by the per-empire catalog rather than a private dict on the facade state.
- [ ] Cache invalidation responsibility moves with the data.
- [ ] **Verify:** existing facade-state tests pass; new cache-equivalence test green.

### Task 2.4: Add `GameSession` accessor [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `tests/unit/strategy/engine/test_game_session_catalog_accessor.py` (new)

- [ ] Add `get_design_catalog(empire_id)` (or `design_catalogs_by_empire[empire_id]`) — match whatever naming convention is least invasive to the current `GameSession` surface; record the choice in [`decisions.md`](decisions.md).
- [ ] Populate catalogs at bootstrap by calling `DesignRepository.scan_designs(...)` and seeding each empire's catalog.
- [ ] **Cross-plan note:** if PROJ-423 (TD-02) has landed before this phase, the accessor goes into `SessionRuntimeServices` (or `SessionBootstrapState` for the per-empire catalog map) per the TD-02 cross-plan note. If PROJ-423 has not landed, the accessor lives directly on `GameSession`; the absorption happens later in PROJ-423.
- [ ] **Verify:** new accessor test passes; `GameSession` from-dict / to-dict round-trip remains byte-identical.

### Task 2.5: Phase close [Simple]
**Tests:** `pytest tests/unit/strategy/design_catalog/ tests/unit/strategy/engine/ tests/unit/strategy/facade/ -q`

- [ ] Existing production / UI callers still use `DesignLibrary` (no migration in this phase).
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-427 phase_2 --repo .worktrees/phases/PROJ-427/phase_2`.

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
