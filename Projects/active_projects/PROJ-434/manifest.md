# PROJ-434 File Manifest

> Generated from PROJ-427's Phase 6 partial-close findings (2026-05-17). Used by `/proj-parallel` for conflict detection. Updated if implementation discovers additional files.

## Production files

### Phase 0 — API extension (additive only)

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/systems/design_repository.py` | Production | Edit | Add `scan_designs(empire_id)`, `load_design_data(design_id)`, `get_design_path(design_id)`, rich `save_design(ship, name, built_designs)` (overwrite-protection + metadata embedding + on-disk write), `mark_obsolete(design_id)`. Match byte-for-byte the `DesignLibrary` contract for each. |
| `game/strategy/systems/design_catalog.py` | Production | Edit | Add `search_designs(query)`, `filter_designs(predicate)`, `invalidate(design_id)` cache hook. Wire `save_design` orchestration that calls `DesignRepository.save_design` + invalidates the per-turn cache. |
| `game/strategy/facade/slices/_facade_state.py` | Production | Edit | Re-point `designs_by_empire` to resolve through `session.services.design_catalogs_by_empire[empire_id]` rather than constructing a `DesignLibrary`. Preserves the QA-Obs-3 cache contract by going through the catalog's invalidation hook. |

### Phase 1 — `BuildQueueScreen` family migration

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/build_queue_screen.py` | Production | Edit | Replace `DesignLibrary(save_path, empire.id)` construction with `session.services.design_catalogs_by_empire[empire.id]`. Thread the catalog reference into the three panel collaborators below. |
| `game/ui/screens/build_queue_controller.py` | Production | Edit | Migrate `scan_designs` + `load_design_data` calls off `DesignLibrary` onto the catalog/repository. |
| `game/ui/screens/build_queue_drag_handler.py` | Production | Edit | Migrate design-metadata reads (drag previews) off `DesignLibrary` onto the catalog. |
| `game/ui/screens/build_queue_portrait_loader.py` | Production | Edit | Migrate `get_design_path` calls off `DesignLibrary` onto `DesignRepository`. Cache keying unchanged. |

### Phase 2 — Remaining UI screens + deletion

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/workshop_ship_io.py` | Production | Edit | Migrate the rich save flow onto `DesignCatalog.save_design(...)` (which internally calls `DesignRepository.save_design` + invalidates the cache). Preserves QA-Obs-3 cache parity. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | Edit | 4 `DesignLibrary(...)` construction sites — replace each with the empire-keyed catalog lookup. |
| `game/ui/screens/design_selector_window.py` | Production | Edit | Largest UI file in scope (705 LOC). Replace `design_library`-typed constructor parameter with `design_catalog`. Migrate `search_designs`, `filter_designs`, `mark_obsolete` callers. |
| `game/strategy/systems/design_library.py` | Production | Delete | Once `rg -n "DesignLibrary" game tests` returns zero live hits. Also remove the `DesignLoadResult` re-export shim left in the file by PROJ-427's dependency-inversion step. |

## Test files

### Phase 0 — API parity characterization

| File | Type | Action |
|------|------|--------|
| `tests/unit/strategy/design_repository/test_scan_designs.py` | Test (new or extend) | Add coverage matching `DesignLibrary.scan_designs` semantics. |
| `tests/unit/strategy/design_repository/test_save_design.py` | Test (new) | Cover the rich `save_design(ship, name, built_designs)` flow including overwrite-protection. |
| `tests/unit/strategy/design_repository/test_load_design_data.py` | Test (new or extend) | Match `DesignLibrary.load_design_data` semantics. |
| `tests/unit/strategy/design_catalog/test_search_designs.py` | Test (new) | Cover `search_designs(query)` parity with `DesignLibrary.search_designs`. |
| `tests/unit/strategy/design_catalog/test_filter_designs.py` | Test (new) | Cover `filter_designs(predicate)`. |
| `tests/unit/strategy/design_catalog/test_cache_invalidation.py` | Test (new) | QA-Obs-3 regression: workshop save → catalog invalidates → next read picks up the new design. |
| `tests/unit/strategy/facade/test_designs_by_empire_through_catalog.py` | Test (new) | `FacadeSessionState.designs_by_empire` resolves through the catalog. |

### Phase 1 — `BuildQueueScreen` family fixture migration

| File | Type | Action |
|------|------|--------|
| `tests/unit/ui/screens/test_build_queue_screen.py` | Test | Repoint `DesignLibrary` monkeypatch onto the catalog. |
| `tests/unit/ui/screens/test_build_queue_controller.py` | Test | Repoint monkeypatch. |
| `tests/unit/ui/screens/test_build_queue_drag_handler.py` | Test | Repoint monkeypatch. |
| `tests/unit/ui/screens/test_build_queue_portrait_loader.py` | Test | Repoint monkeypatch. |
| (other build-queue family tests discovered by `rg -n "DesignLibrary" tests/unit/ui/screens/`) | Test | Enumerate during Phase 1 Task 1.1. |

### Phase 2 — Remaining UI + production-spawner test fixtures

| File | Type | Action |
|------|------|--------|
| `tests/unit/ui/screens/test_workshop_ship_io.py` | Test | Repoint monkeypatch onto the catalog; cover the rich save flow. |
| `tests/unit/ui/screens/test_strategy_build_queue_manager.py` | Test | Repoint each of the 4 monkeypatch sites. |
| `tests/unit/ui/screens/test_design_selector_window.py` | Test | Repoint monkeypatch; constructor signature changes. |
| `tests/unit/strategy/engine/test_production_spawner.py` | Test | Re-point any remaining `DesignLibrary` module-boundary patches (PROJ-427 Phase 3 already migrated most, but check for stragglers). |
| `tests/unit/strategy/production_engine/test_spawning.py` | Test | Same. |
| `tests/unit/strategy/design_library/*` | Test | Delete (the directory becomes obsolete once `design_library.py` is gone). |
| (~20 other test files identified by `rg -n "DesignLibrary" tests/`) | Test | Enumerate during Phase 2 Task 2.1. |

## Docs

| File | Type | Phase | Action |
|------|------|-------|--------|
| `docs/01_ARCHITECTURE.md` | Docs | 2 | Edit if any text still describes the `DesignLibrary` UI flow. |
| `docs/02_PATTERNS.md` | Docs | 2 | Edit if patterns reference `DesignLibrary`. |
| `docs/systems/save_load.md` | Docs | 2 | Edit if save-load flow references `DesignLibrary`. |
| (any other `docs/` file flagged by `rg -n "DesignLibrary" docs`) | Docs | 2 | Enumerate during Phase 2 Task 2.4. |

## Generated state

| File | Owner | Notes |
|------|-------|-------|
| `Projects/active_projects/PROJ-434/phase_state.json` | Coordinator | Authoritative state; never hand-edit mid-flight. |
| `Projects/active_projects/PROJ-434/findings_ledger.md` | Coordinator | Generated view of `phase_state.json` findings section. |
| `Projects/active_projects/PROJ-434/manifest.md` | Coordinator (this file) | Regenerated by `phase_complete.py` from current SHAs. |
