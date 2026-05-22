# PROJ-477: Facade read-path — delete `galaxy`/`empires`/`systems` StrategyScreen pass-throughs + the `session` getter, behind a scene-owned world-access boundary (deferred tail of PROJ-475)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-477` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-477 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Guard #3 scaffold (ratchet from day one) + session-guard dynamic-`getattr` hardening | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. New cold read surfaces (`facade.systems.by_name`/`of_object`/`at_map_hex`, `facade.spatial.contents_at_hex`) + narrow scene write handle | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Retire the `StrategyScreen.session` GETTER (migrate readers + route writes through the handle; keep SETTER) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate the COLD broad-property consumers + the raw-domain fan-out handoffs onto facade queries / `StrategyWorldAccess` | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Introduce `StrategyWorldAccess` + migrate render-hot stack (`StrategyRenderer` + `strategy_render/*`) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Delete renderer re-exporters + the `galaxy`/`empires`/`systems` pass-throughs; ratchet guard #3 to end-state | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Planned (execution-ready). Pre-flesh + post-flesh Codex consults complete.
**Last Action:** Fleshed to execution-ready + revised per post-flesh review. Pre-flesh consult
(`AgentCoordination/Scratchpad/Consult/proj477_preflesh/advice.md`) confirmed and
EXTENDED the deferred consumer set (stub undercounted — adds `strategy_build_queue_manager`,
`strategy_game_state_manager`, `strategy_screen_assets`, `strategy_screen_selection`,
`strategy_screen.current_empire`, plus the transitive raw-domain fan-out through menu
builders → `build_queue_screen`/`build_queue_controller` and the list windows). Adopted
the **hybrid boundary**: a scene-owned `StrategyWorldAccess` object as the SINGLE raw-domain
seam for render-hot + raw-window handoffs (NO per-frame DTOs), plus narrow cold facade
queries. Guard #3 is added FIRST (Phase 1) and ratcheted down as migrations land.
Post-flesh review (`.../proj477_postflesh/advice.md`) returned BLOCKERS (all addressable
in-plan, NO user-decision blocker) — revised: live-`StarSystem` consumers use
`scene.world` not summary facade queries (B2); added `world.planet_by_id` +
`planet_list_filters`/`star_list_filters` to scope (B3); `superweapons:109` →
`planets_at_exact_hex` not `contents_at_hex` (B5); Phase-5 element-identity test +
Task 5.1 promoted to a hard prerequisite (B1/B4). Verdict on cap: keep WHOLE.
**Next Action:** **Do NOT start until PROJ-475 lands.** Then RE-RUN the consumer
inventory against post-475 live code (the session-getter tail shrinks once PROJ-475
migrates its readers) before executing Phase 1.
**Blockers:** **GATED on PROJ-475** (planned, not executed — `_facade_state.py:65` still
reads `self.session = session`, i.e. the privatization has not landed; the session-guard
Category A allowlist still lists `_session.galaxy/empires/systems`). Confirm scope/cap with
the user (this is a large single project — see Capping).

## Overview
Deferred tail of **PROJ-475**. This project actually CLOSES the facade read-path boundary:
it deletes the three BROAD `StrategyScreen` pass-through properties `galaxy`/`empires`/`systems`
(`game/ui/screens/strategy_screen.py:160-170`), the renderer re-exporters that proxy them
(`strategy_renderer.py:124-134`), and the `StrategyScreen.session` GETTER (`strategy_screen.py:277-292`),
behind a principled access boundary. It adds a THIRD static guard that measures
`scene.galaxy`/`scene.empires`/`scene.systems` (and `r.*`) PROPERTY reads — the current two guards
(`test_facade_read_path_session_guard.py`, `test_facade_read_path_imports_guard.py`) only catch
`.session` chains and `game.strategy.*` imports, NOT property reads.

**The boundary design (hybrid — pre-flesh consult §2):**
- **Render-hot + raw-domain window handoffs:** a scene-owned `StrategyWorldAccess` object,
  constructed by `StrategyScreen`, exposing live, allocation-light traversal
  (`iter_systems()`, `iter_empires()`, `system_by_name()`, `system_for_object()`,
  `system_at_map_hex(hex, radius=50)`, `planets_at_exact_hex()`, `zones_at_hex()`,
  `warp_points_at_hex()`, and accessors for the `global_hex_*` spatial maps). It hands back
  the underlying LIVE collections / O(1) map lookups — **NO per-frame DTO allocation**. This is
  the single seam the renderer (`r`) and the raw-window handoffs read through, replacing
  `r.galaxy`/`r.empires`/`r.systems` and `scene.galaxy`/`scene.empires`/`scene.systems`.
- **Cold callers needing small summaries:** new DTO/scalar facade queries
  (`facade.systems.by_name`, `facade.systems.of_object`, `facade.systems.at_map_hex`,
  `facade.spatial.contents_at_hex`) where projection is acceptable.

**Why NOT a `facade.render.*` DTO namespace (consult §2):** `facade.systems.all()` /
`facade.empires.all()` allocate DTO lists per call (`grouped_namespaces.py:200-202,240-246`),
and `EmpireInfo.from_empire` rebuilds a `ResourceCatalog.from_json()` tuple per call
(`empire_dto.py:102-110`) — categorically wrong for per-frame use. `FacadeSessionState`
stays a kept-by-design per-turn cache holder (`_facade_state.py:49-61`, pinned by
`test_game_session_projection_boundary.py`), NOT a public raw-domain render API.

## Goals
- Add guard #3 (Phase 1) measuring `scene.galaxy`/`empires`/`systems` (+ `_screen.*`, `r.*`,
  `screen.*` in helper modules) property reads under `game/ui/`, ratcheted down as migrations land.
- Harden the session guard for dynamic `getattr(..., "session")` extraction
  (`system_tree_panel.py:418-425` currently bypasses the AST matcher entirely).
- Add cold read surfaces: `facade.systems.by_name`, `facade.systems.of_object`,
  `facade.systems.at_map_hex(hex, radius=50)` (pathfinder/system-radius semantics — NOT
  `near_hex(max_dist=8)`), `facade.spatial.contents_at_hex` (zones/warp-points/planets at hex
  with multi-hex membership — `at_hex` exact-center alone misses Dyson Spheres).
- Add a narrow scene-owned write handle (`screen.order_writes` / equivalent) for the Category B
  mutator WRITE seams; retire the `StrategyScreen.session` GETTER (keep the SETTER).
- Introduce `StrategyWorldAccess`; migrate `StrategyRenderer` + `strategy_render/*` + the
  raw-domain window handoffs through it (NO per-frame DTOs).
- Delete the `galaxy`/`empires`/`systems` pass-throughs + the renderer re-exporters; ratchet
  guard #3 to its end-state allowlist.

## Scope
**In:** Guard #3 + session-guard `getattr` hardening; the new cold facade surfaces; the scene
write handle; `session` getter retirement; `StrategyWorldAccess`; render-hot + cold + transitive
fan-out consumer migration; deletion of the three broad pass-throughs + renderer re-exporters.
**Out:** Everything PROJ-475 closes (the `.session` tail, the three narrow pass-throughs,
`FacadeSessionState.session` privatization); tooling/editor screens (PROJ-476); value/config
allowlist (PROJ-474). The `galaxy_test/` standalone harness (`galaxy_mode.py`) — it owns its own
`Galaxy`, not a scene pass-through (out of boundary).

## Capping (READ THIS — orchestrator must confirm scope with user)
Pre-flesh consult §8: as a single execution pass this is at the **upper bound** now that the
missed consumers (the transitive fan-out through menu builders, list windows, and the
build-queue manager/screen/controller chain) are included. Two options:

- **(A) Keep PROJ-477 WHOLE (planned here):** feasible *only* by making `StrategyWorldAccess`
  the single raw-domain seam — render migration then becomes mechanical (swap the `r.galaxy`
  source from the scene property to `scene.world`), not a DTO rewrite. Six phases below.
- **(B) Split:** keep guard scaffold + session-getter retirement + cold-consumer migration +
  `StrategyWorldAccess` introduction in PROJ-477; defer the render-hot layer migration
  (`StrategyRenderer` + `strategy_render/*`) and the final property deletion to a NEW stub.

**Recommendation:** plan option (A) but FLAG to the user that if a single agent execution pass
proves too long (esp. the Phase 4 fan-out + Phase 5 render migration), fall back to (B) by
extracting Phases 5-6 to a new stub via `python Projects/scripts/create_project.py`. No further
stub is created pre-emptively — the cut line is documented so an executing agent can split at
the Phase 4/5 boundary if needed. **Confirm A-vs-B with the user before executing.**

## Key Files (verified live 2026-05-22)
| Component | File Path | Verified refs |
|-----------|-----------|---------------|
| Broad pass-throughs to delete | `game/ui/screens/strategy_screen.py` | `galaxy`/`empires`/`systems` `:160-170`; `current_empire` internal reader `:201-210`; `session` getter `:277-292` + setter `:294-311`; pathfinder helpers `:547-555` |
| Renderer re-exporters | `game/ui/screens/strategy_renderer.py` | `:124-134` (`galaxy`/`systems`/`empires`); ctor `:79-85`; per-frame `draw()` `:226-249` |
| Render-hot traversal | `game/ui/screens/strategy_render/{fleets,hex_outlines,systems,warp_lanes,planets,dyson_spheres}.py` | fleets `:16-20`; hex_outlines `:30-86`; systems `:28-58,96-102`; warp_lanes `:23-54`; planets `:33-54`; dyson_spheres `:42-45,92-113` |
| Cold: context-menu builders | `strategy_ui.py:197-200,236-237` → `fleet_menu_items.py:89-142`, `planet_menu_items.py:59-97` | raw `galaxy` passed in + traversed |
| Cold: list windows | `strategy_windows/list_windows.py:41-74,100-123` → `planet_list_window.py:90-111,383-389`, `star_list_window.py:188-200,507-523` | raw `galaxy`/`empires` stored as `self.galaxy`/`self.empires` |
| Cold: build-queue chain | `strategy_windows/build_queue_windows.py:59-82`, `strategy_build_queue_manager.py:141-142,181-182,211-212,309-317` → `build_queue_screen.py:111,237,357` → `build_queue_controller.py:104-107,456-460,491-493,553-554` | raw `galaxy` threaded + `get_planets_at_global_hex` |
| Cold: colonization/superweapons/nav/click/events | `strategy_colonization.py:40-41,83-88,170-176,257,270-272`, `strategy_superweapons.py:72-86,109-110,213-221,362-367`, `strategy_camera_nav.py:44-45,91-93,108-113,160-163`, `strategy_click_dispatcher.py:560-563,594-598`, `strategy_event_router.py:397-401` | systems/galaxy traversal + spatial queries |
| Cold: assets/selection/state-manager/fleet-ops | `strategy_screen_assets.py:29-51`, `strategy_screen_selection.py:33-35,80-83`, `strategy_game_state_manager.py:144-146,160-164`, `strategy_fleet_ops.py:65-66` | `screen.systems`/`screen.empires` |
| Session getter readers (live, pre-475) | `strategy_event_router.py:223,368`, `strategy_game_state_manager.py:164,397`, `strategy_screen_selection.py:93`, `strategy_screen_order_editing.py:42,66,92`, `strategy_screen_lifecycle.py:49-53,155`, `transfer_controller.py:159-176`, `strategy_windows/empire_panel_ctrl.py:51-63`, `system_tree_panel.py:414-426` | re-scan AFTER PROJ-475 lands |
| Category B WRITE seams | `strategy_game_state_manager.py:164` (set active empire), `strategy_screen_order_editing.py:66` (set_path), `:92` (pop_order) | route through scene write handle |
| Existing facade surfaces (reuse) | `grouped_namespaces.py` | `facade.systems.all()` `:200-202`, `at_hex()` `:208-210`, `near_hex()` `:216-220`; `facade.planets.at_hex()` `:175-177`; `scene.active_empire_id` `strategy_screen.py:225-235`; `scene.registries` `:213-222` |
| New cold query slices | `game/strategy/facade/slices/system_slice.py`, new `spatial` slice | add `by_name`/`of_object`/`at_map_hex`; `contents_at_hex` |
| `StrategyWorldAccess` (NEW) | `game/ui/screens/` (new module, e.g. `strategy_world_access.py`) | scene-owned live-traversal seam |
| Guards | `tests/static_guards/test_facade_read_path_property_guard.py` (NEW); `test_facade_read_path_session_guard.py` (harden `getattr`) | mirror existing guard structure |
| Domain methods consumed | `galaxy.py:130-180` (`get_system_by_name`/`get_system_of_object`/`get_planets_at_global_hex`/`get_zones_at_global_hex`), `galaxy_pathfinding_service.py:113-128` (`get_system_at_hex` radius=50), `galaxy.state.global_hex_*` | — |

## Related Documents
- [design.md](design.md) — render-hot hazards, boundary design, semantic-drift risks, sequencing
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — per-phase file/conflict map
- Pre-flesh consult: `AgentCoordination/Scratchpad/Consult/proj477_preflesh/advice.md`
- Post-flesh consult: `AgentCoordination/Scratchpad/Consult/proj477_postflesh/advice.md`

## Verification
- [ ] All phase checklists complete
- [ ] `python Tools/test_sharded/test_sharded.py` green
- [ ] All THREE read-path guards green; guard #3 ratcheted to end-state (only `StrategyWorldAccess`
      internals + the screen's own pathfinder helpers allowlisted)
- [ ] `scene.galaxy` / `scene.empires` / `scene.systems` pass-throughs gone; `r.galaxy`/etc.
      re-exporters gone; no consumer references them
- [ ] `StrategyScreen.session` getter raises `AttributeError` (setter still works for test swap)
- [ ] Render-perf: no per-frame DTO allocation introduced (render reads `scene.world` live
      collections); spot-check `draw_systems`/`draw_fleets`/`hex_outlines` unchanged in shape
- [ ] No system/hex-ownership SEMANTIC drift (`at_map_hex` radius=50 ≠ `near_hex` max_dist=8;
      `contents_at_hex` preserves multi-hex zone membership)
- [ ] User verified
