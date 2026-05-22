# PROJ-475: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Deferred tail of **PROJ-472** (COMPLETE — both read-path guards landed, suite
green). This project closes the small, honest part of the read-path tail and
defers the broad `galaxy`/`empires`/`systems` pass-through deletion to a new stub.
See `Projects/active_projects/PROJ-472/plan.md`, the pre-flesh consult
`AgentCoordination/Scratchpad/Consult/proj475_preflesh/advice.md`, and the
post-flesh consult `.../proj475_postflesh/advice.md`.

## Initial Analysis (verified live 2026-05-22)
PROJ-472's two static guards measure two syntactic surfaces under `game/ui/`:
the `.session`/`._session`/`.facade_state.session` chain (session guard) and
runtime `game.strategy.*` imports (import guard). They do NOT measure the
`StrategyScreen` pass-through *properties* (`scene.galaxy`/`scene.empires`/
`scene.systems`/`scene.active_empire`/`scene.human_player_ids`), because those
reads go through a property, not a `.session` chain. Consequence:

- The `.session`-guard-allowlisted readers are a SMALL tail (~7 sites: Category C
  + E in `test_facade_read_path_session_guard.py:82-96`) plus 3 FLEETCAP + 1
  CLUSTER import-allowlist entries.
- The pass-through PROPERTIES are a BROAD raw-domain bus. `enemy_empire` has zero
  external consumers; `human_player_ids` has a small cluster; `active_empire`'s
  external use is mostly the BUG-125 gate (id-compare only) + asset bootstrap. But
  `galaxy`/`empires`/`systems` feed the renderer re-exporters
  (`strategy_renderer.py:124-138` → `r.galaxy`/`r.empires`/`r.systems`), render-hot
  per-frame domain traversal, context-menu builders, and list/build-queue windows.

So the project splits cleanly: the small tail + the three narrow pass-throughs +
`FacadeSessionState.session` privatization are PROJ-475; the three broad
pass-throughs are a separate render/read-model boundary project.

## New facade surfaces (Phase 1) — what exists vs what must be added
**Already exists, just use it (no new code):**
- `facade.session_meta.registries()` (`grouped_namespaces.py:328-336`) — empire_panel_ctrl DI.
- `facade.session_meta.human_player_ids()` (`:324-326`) — human-player cluster.
- `facade.facade_state.get_design_catalog_for_empire()` (`_facade_state.py:140-157`) — transfer_controller.
- `facade.facade_state.get_fleet_by_id` / `get_empire_by_id` (`:108-120`).
- `StrategyScreen.active_empire_id` (`strategy_screen.py:225-235`) — BUG-125 gates (rewired off the property in Phase 3).
- `facade.session_meta.save_path()` (`:320-322`) — read-only path (not enough for save action).

**Must be added:**
1. **Empire race-config surface** — `facade.empires.race_config(empire_id)` returning
   the live `RaceConfig` (or `None`). Reason: `EmpireInfo` carries no race identity
   (`empire_dto.py:77-120`); `strategy_event_router` needs `empire.race_config` to seed
   the species-ideal button. **Post-flesh review B12:** do NOT force an
   `EmpireIdentityInfo(race_id, race_config)` DTO — `Empire` owns `race_config` directly
   (`empire.py:24-35`) and there is no first-class `Empire.race_id` field; a later caller
   needing the id reads `race_config.race_id`. Returning the `RaceConfig` is acceptable
   here (it is the immutable race-definition value object, not live mutable session
   state); record this allowance in decisions.md.
2. **Save action surface** — `facade.session_meta.save_current_game(save_name=None)`
   returning `(success, message, save_path)`. The facade holds the session and calls
   `SaveGameService.save_game(self._session, save_name)` internally, so the UI never
   holds the live session to save. Reason: `save_game(...)` requires a `GameSession`
   (`save_game_service.py:93-118`).
3. **Colony build-yard projection + a query wiring step** — `has_build_yard: bool` on
   `PlanetInfo`, true when the colony has a planetary yard OR a space shipyard. Reason:
   `strategy_detail_formatter:277` imports `colony_has_planetary_yard` to gate the
   Build-Yard button; `PlanetInfo` exposes only `has_space_shipyard`. **Post-flesh
   review B4 caveat:** `_show_planet_report` renders a live `Planet` domain object
   (`strategy_detail_formatter.py:134,193,241,277`), NOT a `PlanetInfo`. So the field
   alone does not replace the import — Phase 2 must add `facade.planets.get(obj.id)`
   inside `_show_planet_report` and read `has_build_yard` off the DTO result.
4. **Per-ship spaceyard projection + a consumer BRIDGE** — add `has_spaceyard: bool`
   to `ShipInfo` (`fleet_dto.py:127`, built by `FleetInfo.from_fleet` via
   `fleet_slice.py:60`). **Post-flesh review B3 caveat:** the fleet report does NOT
   consume `ShipInfo` today — it runs on raw `ShipInstance` lists
   (`fleet_report_window.py:185,238`, `fleet_report_view_model.py:49,152`,
   `fleet_data_source.py:115,238`, `fleet_report_filters.py:157,300`). So the field
   alone is not enough; Phase 2 must add the bridge: read `facade.fleets.get(fleet_id)`
   and build an `instance_id → has_spaceyard` lookup the report rows consult, replacing
   the three `FleetCapabilityCalculator.ship_has_spaceyard(ship)` calls. (The
   spaceyard calc still runs once per ship at projection time, in the facade layer.)

## Render-hot path — DECISION (consult §3)
Render-hot traversal is the deferred boundary, NOT touched here. Rationale:
`hex_outlines` reads `galaxy.state.global_hex_*` spatial maps and every empire's
fleets per frame; `fleets`/`systems`/`warp_lanes` walk live `galaxy.systems`. A
blanket DTO rewrite would allocate per-frame or require a much fatter cached
projection than the facade exposes. `EmpireInfo.from_empire` even rebuilds a
`ResourceCatalog.from_json()` per call (`empire_dto.py:104`) — categorically not
per-frame safe. The eventual end-state (consult §3 option i) is a renderer-only
access boundary, owned by the new stub — not per-frame DTOs (option ii rejected as
primary).

## FacadeSessionState.session privatization — DESIGN NUANCE (Phase 4)
The pre-flesh consult recommended "remove public `FacadeSessionState.session`."
Verified caveat: the facade's OWN slices read `_state.session.galaxy` /
`.empires` / `.registries` / `.turn_engine` etc. extensively across **7 slices**:
`system_slice`, `planet_slice`, `fleet_slice`, `event_slice`, `empire_slice`,
`economy_slice` (`:67`, `:119` — flagged by post-flesh review B1), and
`command_dispatch_slice`, plus `_facade_state`'s own helpers. So `session` cannot
be deleted — it must be **renamed `session` → `_session`** with a slice-internal
read path, removing only the PUBLIC reachability via `facade.facade_state.session`.
No UI runtime code reads `facade_state.session` today (the four remaining hits are
docstring/comment residue; the live reads were migrated in PROJ-472 1C). The
**cache holder stays public** — UI legitimately reads `facade_state.planets_for_empire_cache`
/ `stars_cache_new` (the kept-by-design performance boundary, pinned by
`test_game_session_projection_boundary.py`). Phase 4 is mechanical but touches ~6
slice files; pin it with a test asserting `facade.facade_state.session` raises
`AttributeError` while the slices still function.

## Dependencies & Risks
1. **Pass-through deprecation is behavioral.** Removing a property breaks any
   missed consumer at import/attr time. Mitigation: per-property (consult §4 order:
   `enemy_empire` → `human_player_ids` → `active_empire`); migrate all consumers
   first, run the suite, then delete the property; a removed property surfaces as an
   `AttributeError` in tests immediately.
2. **`active_empire_id` / `current_empire` are screen-internal.** They currently
   read the public `active_empire` property; rewire them to the private `_session`
   (the screen is the composition root and owns the only legitimate handle) so
   deleting the public `active_empire` does not break the screen's own helpers.
3. **Keep BOTH the `session` getter and setter (post-flesh review B2).** The setter
   rebuilds the facade in lockstep to avoid split-brain (`strategy_screen.py:294-311`);
   tests swap via `screen.session = mock`. The GETTER is NOT retired in PROJ-475 — it
   still has live production consumers (`system_tree_panel.py:418-425` dynamic
   `getattr(scene,'session')`, plus the Category B mutator WRITE seams). Its retirement
   + those callers move to PROJ-477.
4. **`human_player_ids` semantics must not change** to fix UI turn/view issues
   (`docs/systems/strategy_layer.md:193`). Read-only projection only.
5. **transfer_controller anchor** — when migrated, use `viewing_empire_id`
   (the documented "whose data" anchor, `strategy_screen.py:247-266`), not the
   active-turn empire (consult §6).
6. **Determinism/save-compat: projection-only**, as PROJ-472. New queries are
   read-only; `save_current_game` serializes the same session SaveGameService
   already serializes — no schema change. Keep save/load suites in scope when
   touching save seams (`docs/systems/save_load.md`).
7. **Don't remove `FacadeSessionState`** — only privatize `.session`; the helper
   surface (`get_fleet_by_id`/`get_empire_by_id`/`get_design_catalog_for_empire`/
   `get_designs_for_empire`) and caches stay.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
