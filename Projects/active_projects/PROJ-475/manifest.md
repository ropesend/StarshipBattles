# PROJ-475 File Manifest

> Used by /claude-proj-parallel for conflict detection. Updated if implementation
> discovers additional files. Phase column shows which phase touches each file.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/facade/grouped_namespaces.py` | Production | 1 | Add `FacadeEmpireQueries.race_config`; add `FacadeSessionInfo.save_current_game` |
| `game/strategy/facade/slices/empire_slice.py` | Production | 1 | Back race-config read (empire → race_config/race_id) |
| `game/strategy/facade/slices/event_slice.py` | Production | 1 | Back `save_current_game` (session-meta slice host) |
| `game/strategy/facade/dto/empire_dto.py` | Production | 1 | Optional `EmpireIdentityInfo` DTO and/or `ColonySummary.has_build_yard` |
| `game/strategy/facade/dto/planet_dto.py` | Production | 1 | `PlanetInfo.has_build_yard` projection |
| `game/strategy/facade/dto/fleet_dto.py` (`ShipInfo`) | Production | 1 | `has_spaceyard` per-ship projection (`:127`) |
| `game/ui/screens/fleet_data_source.py` | Production | 2 | `_format_spaceyard` reads `has_spaceyard` via bridge; remove FLEETCAP import + allowlist entry |
| `game/ui/screens/fleet_report_filters.py` | Production | 2 | Filter + sort key via bridge; remove 2 FLEETCAP allowlist entries |
| `game/ui/screens/fleet_report_view_model.py` | Production | 2 | Hold the `instance_id → has_spaceyard` bridge lookup (`set_spaceyard_lookup`/`has_spaceyard`); thread into `_refresh` |
| `game/ui/screens/fleet_report_window.py` | Production | 2 | `_build_spaceyard_lookup` (reads `facade.fleets.get(fleet_id).ships`); pushes into view-model on init + refresh_list |
| `game/ui/screens/strategy_detail_formatter.py` | Production | 2 | Use `has_build_yard`; remove CLUSTER `colony_has_planetary_yard` import + allowlist entry |
| `game/ui/screens/strategy_event_router.py` | Production | 2 | `scene.session.get_empire(...).race_config` → `facade.empires.race_config`; remove 2 Category C allowlist entries |
| `game/ui/screens/strategy_screen_selection.py` | Production | 2 | BUG-125 gate → `screen.active_empire_id`; remove Category C entry |
| `game/ui/screens/strategy_screen_order_editing.py` | Production | 2 | BUG-125 read → `screen.active_empire_id`; remove Category C READ entry (`:66`/`:92` mutator WRITE seams stay) |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | Production | 2 | `c.scene.session.registries` → `c.scene.registries`; remove Category C entry |
| `game/ui/screens/strategy_game_state_manager.py` | Production | 2 | auto-save → `facade.session_meta.save_current_game()`; remove Category E entry |
| `game/ui/screens/strategy_screen_lifecycle.py` | Production | 2 | workshop ctx `game_session` → scalar `save_path`; remove Category E entry |
| `game/ui/screens/transfer_controller.py` | Production | 2 | `session = scene.session` → `facade.facade_state.get_design_catalog_for_empire(viewing_empire_id)`; remove Category E entry |
| `game/ui/screens/strategy_screen_lifecycle.py` (`on_save_game_click:155`) | Production | 2 | manual save → `facade.session_meta.save_current_game()`; drop late `SaveGameService` import (`:150`) |
| `game/app.py` | Production | 2 | Workshop open reads scalar `save_path` from context (was `game_session`) — `:448-486` |
| `game/ui/screens/strategy_screen.py` | Production | 3 | Delete `enemy_empire`/`human_player_ids`/`active_empire` pass-throughs; rewire `active_empire_id`/`current_empire` to `_session`. Getter+setter UNTOUCHED (getter retirement deferred to PROJ-477 — post-flesh B2) |
| `game/ui/screens/strategy_click_dispatcher.py` | Production | 3 | `human_player_ids` consumer → `facade.session_meta.human_player_ids()` |
| `game/ui/screens/strategy_screen_assets.py` | Production | 3 | `active_empire` asset bootstrap → `active_empire_id` / facade |
| `game/strategy/facade/slices/_facade_state.py` | Production | 4 | Rename `session` → `_session`; add slice-internal accessor |
| `game/strategy/facade/slices/system_slice.py` | Production | 4 | `_state.session` → internal accessor |
| `game/strategy/facade/slices/planet_slice.py` | Production | 4 | same |
| `game/strategy/facade/slices/fleet_slice.py` | Production | 4 | same |
| `game/strategy/facade/slices/event_slice.py` | Production | 4 | same |
| `game/strategy/facade/slices/empire_slice.py` | Production | 4 | same |
| `game/strategy/facade/slices/economy_slice.py` | Production | 4 | same (`:67`, `:119` — post-flesh review B1) |
| `game/strategy/facade/slices/command_dispatch_slice.py` | Production | 4 | same |
| `tests/static_guards/test_facade_read_path_session_guard.py` | Test | 2,3,4 | Remove Category C/E allowlist entries as migrated; add pin that `facade_state.session` no longer resolves (Phase 4) |
| `tests/static_guards/test_facade_read_path_imports_guard.py` | Test | 2 | Remove FLEETCAP (3) + CLUSTER (1) allowlist entries |
| `tests/unit/strategy/facade/test_empire_race_config.py` | Test | 1 | NEW — race_config surface (3 cases) |
| `tests/unit/strategy/facade/test_session_meta_save.py` | Test | 1 | NEW — save_current_game surface (2 cases) |
| `tests/unit/strategy/facade/test_planet_has_build_yard.py` | Test | 1 | NEW — has_build_yard DTO field + slice resolution (5 cases) |
| `tests/unit/strategy/facade/test_ship_has_spaceyard.py` | Test | 1 | NEW — has_spaceyard DTO field (3 cases) |
| `game/strategy/facade/slices/planet_slice.py` | Production | 1 | `_project_planet` + `_resolve_has_planetary_yard` resolve build-yard bit with registries |
| `tests/unit/strategy/facade/slices/test_planet_slice.py` | Test | 1 | Updated 2 `from_planet` stubs to accept `**kwargs` (signature gained `has_planetary_yard`) |
| `tests/unit/ui/...` | Test | 2,3 | Reader-migration + pass-through-removal tests |
| `tests/unit/ui/screens/test_strategy_event_router_race_config.py` | Test | 2 | NEW — Task 2.3 race-config via facade (2 cases) |
| `tests/unit/ui/screens/test_fleet_report_spaceyard_bridge.py` | Test | 2 | NEW — Task 2.6 spaceyard bridge (filter/sort/vm/format/import-absence) |
| `tests/unit/ui/screens/test_strategy_detail_formatter_build_yard.py` | Test | 2 | NEW — Task 2.7 Build-Yard gate via facade (3 cases) |
| `tests/unit/ui/screens/test_strategy_screen_selection.py` | Test | 2 | Stub `screen.active_empire_id` for BUG-125 gate |
| `tests/unit/ui/screens/test_strategy_screen_order_editing.py` | Test | 2 | Stub `screen.active_empire_id` for BUG-125 gate |
| `tests/unit/ui/screens/test_transfer_controller.py` | Test | 2 | pod-discovery via `viewing_empire_id` + `get_design_catalog_for_empire` |
| `tests/unit/ui/screens/test_strategy_game_state_manager.py` | Test | 2 | auto-save via `save_current_game()`; fixtures return save triple |
| `tests/unit/ui/screens/test_strategy_screen_lifecycle.py` | Test | 2 | scalar `save_path` ctx; `on_save_game_click` via facade |
| `tests/unit/test_app_create_workshop_context.py` | Test | 2 | gate empire-only; scalar `save_path` |
| `tests/unit/ui/screens/test_viewing_empire_anchor.py` | Test | 2 | scalar `save_path` in workshop ctx |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Test | 2 | spaceyard filter/sort via lookup; `make_mock_ship` sets `instance_id` |
| `tests/unit/ui/screens/test_fleet_data_source.py` | Test | 2 | spaceyard column reads view-model lookup |
| `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py` | Test | 2 | stub `scene.registries` (was `scene.session.registries`) |
| `tests/unit/strategy/engine/test_game_session_projection_boundary.py` | Test | 4 | Keep cache-boundary pin green |

## Conflict notes
- Phase 4 touches 6 facade slice files mechanically; run isolated from other
  facade work (no parallel slice edits).
- `strategy_screen.py` is touched in Phase 3 only (within this project), but is a
  hot file across the repo — coordinate if PROJ-476 runs in parallel.
- The DEFERRED `galaxy`/`empires`/`systems` work (new stub) will touch the renderer
  re-exporters and render modules — explicitly OUT of this manifest.
