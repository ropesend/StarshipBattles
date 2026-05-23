# PROJ-477 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
> **GATED on PROJ-475** — re-verify all line numbers after PROJ-475 lands.

## Files by phase

### Phase 1 — Guard #3 scaffold + session-guard getattr hardening
| File | Type | Notes |
|------|------|-------|
| `tests/static_guards/test_facade_read_path_property_guard.py` | Test (NEW) | AST guard for `scene/r/_screen/screen.galaxy|empires|systems` Load reads under `game/ui/`; full current allowlist; positive-control matcher pin |
| `tests/static_guards/test_facade_read_path_session_guard.py` | Test | Harden matcher for dynamic `getattr(obj,"session")` (`system_tree_panel.py:418-425`) |

### Phase 2 — New cold read surfaces + scene write handle
| File | Type | Notes |
|------|------|-------|
| `game/strategy/facade/slices/system_slice.py` | Production | Add `get_system_by_name`, `get_system_of_object`, `get_system_at_map_hex(hex, radius=50)` |
| `game/strategy/facade/slices/spatial_slice.py` | Production (NEW) | `contents_at_hex(hex)` grouped planet/zone/warp membership (multi-hex aware) |
| `game/strategy/facade/grouped_namespaces.py` | Production | Add `facade.systems.by_name/of_object/at_map_hex`; new `FacadeSpatialQueries` + `facade.spatial` |
| `game/strategy/facade/strategy_session_facade.py` (composer) | Production | Wire `facade.spatial` namespace + the spatial slice |
| `game/ui/screens/strategy_screen.py` | Production | Add narrow `order_writes` scene write handle (set-active-empire / set-path / pop-order) backed by `_session` |
| `tests/unit/strategy/facade/` | Test | Failing-first tests for each new query (semantics: `at_map_hex` radius=50, `contents_at_hex` multi-hex) |

### Phase 3 — Session getter retirement
| File | Type | Notes |
|------|------|-------|
| `game/ui/panels/system_tree_panel.py` | Production | `_get_empire_context` (`:414-426`) → `scene.active_empire_id` + `scene.registries`; drop `getattr(scene,'session')` |
| `game/ui/screens/strategy_game_state_manager.py` | Production | `:164` write → `screen.order_writes.set_active_empire(...)` |
| `game/ui/screens/strategy_screen_order_editing.py` | Production | `:66` set_path / `:92` pop_order → write handle; `:42` read → `screen.active_empire_id` |
| `game/ui/screens/strategy_screen_selection.py` | Production | `:93` read → `screen.active_empire_id` |
| `game/ui/screens/strategy_screen.py` | Production | Getter (`:277-292`) raises `AttributeError`; setter (`:294-311`) kept |
| Session-getter readers (re-scan post-475) | Production | event_router/lifecycle/transfer_controller/empire_panel_ctrl — likely migrated by PROJ-475; verify |
| `tests/` | Test | Pin: getter raises `AttributeError`, setter still swaps; write-handle behavior |

### Phase 4 — Cold consumer + transitive fan-out migration
| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_ui.py` | Production | `:199,237` menu builders → `scene.world.*` (raw) or facade query |
| `game/ui/screens/fleet_menu_items.py`, `planet_menu_items.py` | Production | Take a `world`/facade handle instead of raw `galaxy` |
| `game/ui/screens/strategy_windows/list_windows.py` | Production | `:42,69,103,117` → pass `scene.world` to windows |
| `game/ui/screens/planet_list_window.py`, `star_list_window.py` | Production | Consume `world` handle instead of raw `galaxy`/`empires` (already take `facade_state` for caches) |
| `game/ui/screens/planet_list_filters.py:38-87`, `star_list_filters.py:20-64` | Production | POST-FLESH B3: transitive fan-out — walk `galaxy.systems.values()`; migrate to `world.iter_systems()` |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | Production | `:62` → `scene.world` |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | `:141-142,181-182,211-212,309-317` `_screen.galaxy` → world handle |
| `game/ui/screens/build_queue_screen.py`, `game/ui/panels/build_queue_controller.py` | Production | Consume `world.planets_at_exact_hex` instead of raw `galaxy.get_planets_at_global_hex` |
| `game/ui/screens/strategy_colonization.py` | Production | `:41,83,84,170,171,257,270` → `scene.world` / `facade.spatial` / `facade.systems.at_map_hex` |
| `game/ui/screens/strategy_superweapons.py` | Production | `:74,86,109,213,367` → world / facade |
| `game/ui/screens/strategy_camera_nav.py` | Production | `:45,91,108,112,161` object→system resolution → `scene.world.system_for_object` / `iter_systems` |
| `game/ui/screens/strategy_click_dispatcher.py` | Production | `:560,594,595` → `scene.world` / `facade.spatial.contents_at_hex` |
| `game/ui/screens/strategy_event_router.py` | Production | `:397,401` `get_system_of_object` → `facade.systems.of_object` (may already be migrated by 475) |
| `game/ui/screens/strategy_screen_assets.py` | Production | `:34,50` `screen.systems`/`screen.empires` → `scene.world.iter_*` |
| `game/ui/screens/strategy_screen_selection.py` | Production | `:34,80` `screen.systems` → `scene.world` |
| `game/ui/screens/strategy_game_state_manager.py` | Production | `:144-146,160-164` `_screen.empires` → `scene.world.iter_empires` |
| `game/ui/screens/strategy_fleet_ops.py` | Production | `:66` wrapper-only `scene.empires` → world (or delete wrapper) |
| `game/ui/screens/strategy_screen.py` | Production | `current_empire` (`:201-210`) internal `self.empires` → `self._session.empires` (composition root) |
| `tests/` | Test | Behavior pins for migrated cold consumers |

### Phase 5 — `StrategyWorldAccess` + render migration
| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_world_access.py` | Production (NEW) | Scene-owned live-traversal seam (see design.md); exposed as `scene.world`; includes `planet_by_id` (POST-FLESH B3, for `_resolve_live_yard`) |
| `game/ui/screens/strategy_screen.py` | Production | Construct `StrategyWorldAccess`, expose `scene.world` |
| `game/ui/screens/strategy_renderer.py` | Production | `r.galaxy/empires/systems` source the live data from `scene.world`, not the pass-throughs |
| `game/ui/screens/strategy_render/{fleets,hex_outlines,systems,warp_lanes,planets,dyson_spheres}.py` | Production | Read `r.world.iter_*` / map accessors; iteration shape unchanged (NO per-frame DTOs) |
| `tests/` | Test | Render-shape / no-per-frame-allocation pin; world-access unit tests |

### Phase 6 — Delete pass-throughs + re-exporters; ratchet guard #3
| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_screen.py` | Production | DELETE `galaxy`/`empires`/`systems` properties (`:160-170`); keep pathfinder helpers `:547-555` (now via `_session`/world) |
| `game/ui/screens/strategy_renderer.py` | Production | DELETE `galaxy`/`systems`/`empires` re-exporters (`:124-134`) |
| `tests/static_guards/test_facade_read_path_property_guard.py` | Test | Shrink allowlist to end-state (only `StrategyWorldAccess` internals + screen pathfinder helpers) |

## Conflict map (for /proj-parallel)
- **Phases are SEQUENTIAL — do not parallelize.** Each phase depends on the prior (guard ratchet
  + deletion-after-migration ordering). `strategy_screen.py` is touched in Phases 2, 3, 4, 5, 6 —
  serialize.
- `strategy_game_state_manager.py` touched in Phases 3 (write) + 4 (empires read).
- `strategy_screen_selection.py` / `_order_editing.py` touched in Phase 3.
- The two guard files are isolated to Phases 1 / 6.
