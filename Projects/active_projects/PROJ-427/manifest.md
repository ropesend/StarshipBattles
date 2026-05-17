# PROJ-427 File Manifest

> Generated from the TD-05 source plan's File Touch Map plus the per-phase task lists. Updated by the coordinator (this protocol) when implementation discovers additional files.

## Production files

| File | Type | Phase | Action | Notes |
|------|------|-------|--------|-------|
| `game/strategy/systems/design_repository.py` | Production (new) | 1 | Add | Filesystem + JSON persistence: folder locate/create, `scan_designs`, `save_design`, `load_design_data`, `mark_design_obsolete`, `increment_built_count`. Preserves `DesignLoadResult` shape. |
| `game/strategy/systems/design_catalog.py` | Production (new) | 2 | Add | In-memory per-empire lookup, per-turn UI cache, pending built-count increments, explicit `refresh()` / `repopulate_from(repository)`. No filesystem access. |
| `game/strategy/facade/slices/_facade_state.py` | Production | 2 | Edit | Move `designs_by_empire` UI cache behavior into `DesignCatalog`. |
| `game/strategy/engine/game_session.py` | Production | 2 | Edit | Add `get_design_catalog(empire_id)` (or `design_catalogs_by_empire[empire_id]`). If PROJ-423 ships later, this accessor migrates into `SessionRuntimeServices`. |
| `game/strategy/engine/production_spawner.py` | Production | 3 | Edit | Drop `DesignLibrary` import; accept catalog/catalog-provider dependency; stop using `save_path`. |
| `game/strategy/engine/production_engine.py` | Production | 3 | Edit | Stop threading `save_path` through tick processing. |
| `game/strategy/engine/handlers/construction_queue.py` | Production | 3 | Edit | Validation and cost lookup go through the catalog. |
| `game/strategy/quickstart_builder.py` | Production | 3 | Edit | Initial-complex spawn populates/reads through the catalog. |
| `game/strategy/systems/save_game_service.py` | Production | 4, 5 | Edit | Phase 4: flush pending built-count increments through `DesignRepository` at save time. Phase 5: instance-owned replay-store wiring; remove `_replay_store`, `set_replay_store`, `get_replay_store`. |
| `game/app_bootstrap.py` | Production | 5 | Edit | Construct `SaveGameService` instance with constructor-injected replay store; drop the module-global registration call. |
| `game/ui/screens/workshop_ship_io.py` | Production | 6 | Edit | UI caller migration: catalog for runtime reads; repository for disk writes. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | 6 | Edit | UI caller migration. |
| `game/ui/screens/transfer_controller.py` | Production | 6 | Edit | UI caller migration. |
| (any other site found by `rg -n "DesignLibrary"`) | Production | 6 | Edit | Discovered during Phase 6 grep step; recorded back here when discovered. |
| `game/strategy/systems/design_library.py` | Production | 6 | Delete (or zero-logic alias) | Deletion only when `rg -n "DesignLibrary" game tests docs` shows no remaining callers. |

## Test files (extended in Phase 0; gated per phase thereafter)

| File | Type | Phase | Action |
|------|------|-------|--------|
| `tests/unit/strategy/design_library/test_basics.py` | Test | 0 | Extend (lock current coupling) |
| `tests/unit/strategy/design_library/test_scan_designs_caching.py` | Test | 0 | Extend (per-turn UI cache state) |
| `tests/unit/strategy/design_library/test_design_load_result.py` | Test | 0 | Extend |
| `tests/unit/strategy/save_game_service/test_save_load_ops.py` | Test | 0, 5 | Extend (replay-store hooks today; instance ownership in Phase 5) |
| `tests/unit/strategy/save_game_service/test_error_handling.py` | Test | 5 | Extend |
| `tests/unit/strategy/engine/test_production_spawner.py` | Test | 0, 3 | Extend (current coupling first; catalog-based spawn after migration) |
| `tests/unit/strategy/production_engine/test_spawning.py` | Test | 0, 3 | Extend |
| `tests/integration/strategy/production/test_completion.py` | Test | 3 | Extend |
| `tests/integration/strategy/production/test_fleet_production_e2e.py` | Test | 3 | Extend |
| `tests/integration/strategy/production/test_no_design_disk_read_during_tick.py` | Test (new) | 3 | Add (explicit no-disk-read guard) |
| `tests/integration/replay/test_replay_store.py` | Test | 5 | Extend |
| `tests/unit/quickstart/test_quickstart_builder.py` | Test | 3 | Extend |
| `tests/unit/strategy/design_repository/` | Test package (new) | 1 | Add |
| `tests/unit/strategy/design_catalog/` | Test package (new) | 2, 4 | Add (Phase 2 lookup + UI views; Phase 4 pending-increment flush) |

## Docs

| File | Type | Phase | Action |
|------|------|-------|--------|
| `docs/01_ARCHITECTURE.md` | Docs | 6 | Edit if runtime flow descriptions change |
| `docs/02_PATTERNS.md` | Docs | 6 | Edit if patterns change |
| `docs/systems/save_load.md` | Docs | 6 | Edit if save-load flow descriptions change |

## Generated state

| File | Owner | Notes |
|------|-------|-------|
| `Projects/active_projects/PROJ-427/phase_state.json` | Coordinator | Authoritative state; never hand-edit mid-flight. |
| `Projects/active_projects/PROJ-427/findings_ledger.md` | Coordinator | Generated view of `phase_state.json` findings section. |
| `Projects/active_projects/PROJ-427/manifest.md` | Coordinator (this file) | Regenerated by `phase_complete.py` from current SHAs. |
