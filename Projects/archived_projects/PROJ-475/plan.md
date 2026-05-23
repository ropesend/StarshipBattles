# PROJ-475: Facade read-path — close the small `.session` reader tail + retire the narrow `StrategyScreen` pass-throughs (follow-on from PROJ-472)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-475` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-475 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. New facade read surfaces (race-config, save, colony-yard, per-ship spaceyard) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate the explicit `.session` reader tail onto facade (remove guard allowlist entries) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Retire the three narrow READ pass-throughs (`enemy_empire` / `human_player_ids` / `active_empire`) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Privatize `FacadeSessionState.session` (rename → `_session`, slice-internal accessor; `_facade_state` + 7 slices) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. End-of-project Codex-audit remediation (build-queue tail deferral pin + defensive-branch coverage + comment retag) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** ALL PHASES COMPLETE (1-5). End-of-project Codex audit done + findings remediated.
**Last Action:** Executed Phases 3 + 4 + 5 (audit remediation). Codex audit: 2 findings VERIFIED
(Finding 1 Medium — build-queue compute_planet_production tail kept allowlisted-with-reason +
pinned, clean migration deferred to PROJ-477; Finding 2 Low — stale import-guard comment retagged),
test-gap notes addressed (3 defensive-branch degrade tests), 1 sub-finding REJECTED for 475
(system_tree_panel string-getattr session = PROJ-477's deferred getter consumer). Both guards GREEN;
full sharded suite GREEN.
- **Phase 3** retired the 3 narrow READ pass-throughs. `enemy_empire` deleted (zero
  consumers). `human_player_ids` external consumers (click_dispatcher, screen_selection,
  game_state_manager x4) → `facade.session_meta.human_player_ids()`; property deleted.
  `active_empire` external consumer (assets `focus_on_player_home`) → resolve live empire
  from raw `screen.empires` bus keyed by `active_empire_id`; property deleted.
  `active_empire_id`/`current_empire` rewired to `_session`. Getter+setter UNTOUCHED.
  Allowlist: `_session.enemy_empire` REMOVED; `_session.human_player_ids` +
  `_session.active_empire` kept as Category-A composition-root self-reads.
- **Phase 4** privatized `FacadeSessionState.session` → `_session` across `_facade_state`
  + 7 slices (slices read `_state._session` directly). Found + fixed a missed external
  reader: `workshop_ship_io.py` `getattr(facade_state,"session")` → public
  `get_design_catalog_for_empire`. Added runtime privatization pin. Cache holder stays
  public (pin green). Both guards GREEN; full sharded suite GREEN.

**HISTORICAL (Phases 1+2):**
- **Phase 1** added the four facade read surfaces: `facade.empires.race_config(empire_id)`
  (raw `RaceConfig`), `facade.session_meta.save_current_game(save_name=None)`,
  `PlanetInfo.has_build_yard` (slice resolves planetary-yard with registries, ORed
  with `has_space_shipyard`), `ShipInfo.has_spaceyard` (calc at projection time).
- **Phase 2** migrated all 7 reader sites + removed their allowlist entries:
  empire_panel_ctrl registries DI; both BUG-125 gates → `screen.active_empire_id`;
  event_router race-config → facade; the three save seams (auto + manual + on_design_click
  scalar save_path handoff via app.py) → `facade.session_meta.save_current_game()`;
  transfer_controller → `facade.facade_state.get_design_catalog_for_empire(viewing_empire_id)`;
  the fleet-report spaceyard bridge (view-model holds `instance_id→has_spaceyard`);
  the colony Build-Yard gate → `facade.planets.get(id).has_build_yard`.
- Allowlists tightened: 4 Category C + 3 Category E session entries, 2 FLEETCAP +
  1 CLUSTER import entries, 2 SaveGameService TAIL import entries — all REMOVED.
  Both read-path guards GREEN. Full sharded suite GREEN.
**Next Action:** Phase 3 — retire the three NARROW READ pass-throughs
(`enemy_empire` DELETE; `human_player_ids` → `facade.session_meta.human_player_ids()`;
`active_empire` DELETE + rewire `active_empire_id`/`current_empire` to `_session`).
**Blockers:** None. (PROJ-472 gate satisfied.)

## Overview
Follow-on from **PROJ-472**, which tightened but did NOT close the strategy facade
READ path. PROJ-472 left two documented transitional surfaces and an explicitly
deferred set of live `.session` readers (allowlisted-with-reason in its two static
guards). THIS project closes the **small, honest** part of that tail:

1. Adds the four new facade read surfaces the deferred readers need.
2. Migrates the explicit `.session`-guard-allowlisted readers onto the facade and
   removes their allowlist entries (Category C + E + the FLEETCAP/CLUSTER import
   entries that now have a facade query).
3. Retires the three NARROW `StrategyScreen` READ pass-throughs that have a small,
   bounded consumer set (`enemy_empire`, `human_player_ids`, `active_empire`). The
   wholesale `StrategyScreen.session` getter is NOT retired here — post-flesh review
   (advice §2) found it still has LIVE production consumers (the `system_tree_panel`
   dynamic `scene.session` resolution `:418-425`, plus the Category B mutator-write
   seams `strategy_game_state_manager.py:164`, `strategy_screen_order_editing.py:66/:92`).
   Retiring it belongs with those (deferred to PROJ-477). The setter stays (split-brain guard).
4. Privatizes `FacadeSessionState.session` (rename to `_session` + a slice-internal
   accessor) so the live session is no longer reachable as a public attribute via
   `facade.facade_state.session`. The cache holder itself stays public (kept-by-design
   performance boundary).

**Honest scope note (do not overclaim).** This project does NOT delete the
`galaxy` / `empires` / `systems` pass-throughs. Those three remain a broad
raw-domain bus feeding the renderer re-exporters (`strategy_renderer.py:124-138`),
render-hot per-frame traversal (`strategy_render/fleets.py`, `hex_outlines.py`,
`systems.py`, `warp_lanes.py`, `planets.py`, `dyson_spheres.py`), context-menu
builders, list/star/build-queue windows, and `system_tree_panel`. Deleting them
is a render/read-model boundary project of a different shape — deferred to a new
stub (see Capping). After PROJ-475 the read path is *more* closed (the live
session is no longer reachable from UI as `.session` / `facade_state.session`),
but the three broad domain pass-throughs persist.

## Capping (READ THIS — orchestrator must confirm scope with user)
The pre-flesh consult (advice §1c, §3, §5) is unambiguous: deleting
`galaxy`/`empires`/`systems` is **too large for one execution pass** and is a
fundamentally different problem (a render/read-model boundary) than "finish the
remaining seven `.session` readers." Capping PROJ-475 to the contained first slice
above; the remainder is pushed to a new further-deferred stub:

- **PROJ-477 (NEW — render/read-model boundary)** — delete `galaxy`/`empires`/`systems`
  pass-throughs; introduce a renderer-only access boundary (NOT per-frame DTO
  churn); migrate context-menu builders, list/star/build-queue windows, and
  `system_tree_panel` off the live galaxy; add a third static guard that measures
  `scene.galaxy`/`scene.empires`/`scene.systems` consumption. **Stub id recorded
  in decisions.md once `create_project.py` runs.**

> **Recommendation:** confirm this cap with the user before executing PROJ-475, so
> the "remaining live readers" expectation is reconciled with the honest split.

## Goals
- Add `facade.empires.race_config(empire_id)` (or `EmpireIdentityInfo` DTO with
  `race_id`/`race_config`) — for `strategy_event_router` race-config reads.
- Add `facade.session_meta.save_current_game(save_name=None)` — the facade owns the
  session and calls `SaveGameService.save_game(session, save_name)` internally, so
  the UI never holds the live session for save.
- Add a colony build-yard projection bit (`has_build_yard` on `PlanetInfo` or
  `ColonySummary`) — for `strategy_detail_formatter`'s Build-Yard button gate.
- Add a per-ship spaceyard projection (`has_spaceyard` on the fleet-report ship DTO)
  — collapses the three `FleetCapabilityCalculator` late-import sites.
- Migrate the deferred `.session` readers; remove their guard allowlist entries.
- Retire `enemy_empire` / `human_player_ids` / `active_empire` pass-throughs.
- (Getter retirement DEFERRED to PROJ-477 per post-flesh review B2 — see Scope.)
- Privatize `FacadeSessionState.session` → `_session` + slice-internal accessor.

## Scope
**In:** The four new facade surfaces; the explicit `.session` reader tail
(event_router, selection, order_editing read, empire_panel_ctrl, save seams,
lifecycle on_design_click handoff, transfer_controller catalog read);
FLEETCAP + colony-yard import allowlist removal; retiring the three narrow READ
pass-throughs (`enemy_empire`/`human_player_ids`/`active_empire`);
`FacadeSessionState.session` privatization; guard allowlist tightening for all of
the above.
**Out (deferred to the NEW stub PROJ-477):** `galaxy`/`empires`/`systems`
pass-through deletion; the `StrategyScreen.session` GETTER retirement (live
consumers: `system_tree_panel` dynamic resolve + Category B mutator WRITE seams —
post-flesh review B2); renderer re-exporters + render modules; context-menu
builders; list/star/build-queue-window raw-galaxy construction; `system_tree_panel`
raw effect walk; the third (property-consumer) static guard. **Out (other projects):** value/config
allowlist consolidation (PROJ-474); tooling/editor screens (PROJ-476);
write-path facade work (already guarded).

## Deferred-from-472 reader set — disposition in PROJ-475 (verified live 2026-05-22)
| Site | Read (verified) | Disposition in 475 |
|------|-----------------|--------------------|
| `strategy_event_router.py:223`, `:368` | `scene.session.get_empire(planet.owner_id)` → `.race_config`/`.race_id` | Phase 2 → new `facade.empires.race_config(empire_id)` |
| `strategy_screen_selection.py:93` | `screen.session.active_empire` (BUG-125 gate, id-compare only) | Phase 2 → `screen.active_empire_id` (rewired off the pass-through in Phase 3) |
| `strategy_screen_order_editing.py:42` | `screen.session.active_empire` (BUG-125 gate, id-compare only) | Phase 2 → `screen.active_empire_id` |
| `strategy_windows/empire_panel_ctrl.py:62` | `c.scene.session.registries` (DI) | Phase 2 → `c.scene.registries` (exists: `facade.session_meta.registries()`) |
| `strategy_game_state_manager.py:397` | `SaveGameService.save_game(self._screen.session)` (auto-save) | Phase 2 → `facade.session_meta.save_current_game()` |
| `strategy_screen_lifecycle.py:51` | `game_session: screen.session` in workshop context dict | Phase 2 → scalar `save_path` handoff (`app.py:448-486` only reads `.save_path`) |
| `transfer_controller.py:160` | `session = scene.session` alias for per-empire catalog | Phase 2 → `facade.facade_state.get_design_catalog_for_empire(viewing_empire_id)` (exists) |
| `fleet_data_source.py:241-245` | `FleetCapabilityCalculator.ship_has_spaceyard(ship)` (import) | Phase 2 → new per-ship `has_spaceyard` projection |
| `fleet_report_filters.py:163`, `:302` | same (filter + sort key) | Phase 2 → same |
| `strategy_detail_formatter.py:277` | `colony_has_planetary_yard(colony, registries)` (import) | Phase 2 → new colony `has_build_yard` projection |
| `strategy_screen_lifecycle.py:155` (manual save, `on_save_game_click`) | `SaveGameService.save_game(screen.session)` | Phase 2 → `facade.session_meta.save_current_game()` (same Category E entry as `:51`) |
| `build_queue_panel_factory.py:18` (`:247` call), `build_queue_screen.py:27` (`:211`,`:321` calls) | `compute_planet_production(...)` on the live build-queue screen | **Owned by PROJ-475** (live build-queue reader; PROJ-474 design.md `:118-119` defers `compute_planet_production` here; NOT PROJ-476 tooling per PROJ-476 post-flesh review Finding 1). Migrate onto a facade production-projection query or allowlist-with-reason if no clean query exists. Re-verify lines at execution. |

## Pass-through disposition (verified live 2026-05-22)
| Property (`strategy_screen.py`) | External consumers | Disposition |
|--------------------------------|--------------------|-------------|
| `enemy_empire` (:184) | **None** (only the property body) | Phase 3 DELETE outright |
| `human_player_ids` (:188) | `strategy_click_dispatcher`, `strategy_game_state_manager`, `strategy_screen_selection` (small) | Phase 3 → `facade.session_meta.human_player_ids()` |
| `active_empire` (:173) | BUG-125 gates (now via `active_empire_id`), `strategy_screen_assets`, `current_empire` (screen-internal) | Phase 3 DELETE; `active_empire_id`/`current_empire` rewired to private `_session` (composition root) |
| `galaxy` (:161) | BROAD (renderer, colonization, superweapons, click, menus, windows) | **DEFERRED to new stub** |
| `empires` (:165) | BROAD (game-state, assets, list windows, render-hot) | **DEFERRED to new stub** |
| `systems` (:169) | MODERATE-BROAD (camera_nav, colonization, superweapons, render) | **DEFERRED to new stub** |
| `session` getter (:277) | LIVE: `system_tree_panel.py:418-425` dynamic resolve; Category B mutator WRITE seams | **DEFERRED to PROJ-477** (retire with system_tree_panel + write-seam cleanup); setter STAYS |

## Key Files
| Component | File Path | Verified refs (2026-05-22) |
|-----------|-----------|----------------------------|
| StrategyScreen narrow pass-throughs + session getter/setter | `game/ui/screens/strategy_screen.py` | `:160-189` pass-throughs, `:225-235` `active_empire_id`, `:191-210` `current_empire`, `:277-311` session getter/setter |
| FacadeSessionState public `session` (privatize) + cache holder (keep) | `game/strategy/facade/slices/_facade_state.py` | `session` `:65`; perf-boundary note `:48-61`; helpers `:108-177` |
| Facade empire queries (add race_config) | `game/strategy/facade/grouped_namespaces.py`, `slices/empire_slice.py` | `FacadeEmpireQueries` `:232-264`; slice `:44-97` |
| Facade session_meta (add save_current_game) | `game/strategy/facade/grouped_namespaces.py` | `FacadeSessionInfo` `:302-336` |
| EmpireInfo DTO (race identity gap) | `game/strategy/facade/dto/empire_dto.py` | `:77-120` |
| PlanetInfo / ColonySummary (colony-yard gap) | `game/strategy/facade/dto/planet_dto.py`, `empire_dto.py:14-42` | `PlanetInfo` `:60-168`; `ColonySummary` `:14-42` |
| Fleet-report ship DTO (per-ship spaceyard gap) | (locate in Phase 1) | `fleet_data_source.py:238-245`, `fleet_report_filters.py:157-165,300-303` |
| SaveGameService (keep engine-internal) | `game/strategy/systems/save_game_service.py` | `save_game(game_session, save_name)` `:93-118` |
| Deferred readers | see table above | — |
| Session-read + import guards (tighten) | `tests/static_guards/test_facade_read_path_session_guard.py`, `test_facade_read_path_imports_guard.py` | allowlists `:67-96` / `:66-222` |

## Related Documents
- [design.md](design.md) — architecture analysis, render-hot rationale, sequencing
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — per-phase file/conflict map
- Pre-flesh consult: `AgentCoordination/Scratchpad/Consult/proj475_preflesh/advice.md`

## Verification
- [ ] All phase checklists complete
- [ ] `python Tools/test_sharded/test_sharded.py` green
- [ ] Both read-path guards green; Category C + E + FLEETCAP/CLUSTER allowlist
      entries for migrated sites REMOVED
- [ ] `enemy_empire` / `human_player_ids` / `active_empire` pass-throughs gone;
      no consumers reference them
- [ ] `facade.facade_state.session` no longer resolves (privatized); slices use the
      internal accessor; cache-boundary pin test still green
- [ ] User verified
