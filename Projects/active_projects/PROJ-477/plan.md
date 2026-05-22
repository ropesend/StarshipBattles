# PROJ-477: Facade read-path: delete galaxy/empires/systems StrategyScreen pass-throughs + renderer/read-model boundary (deferred from PROJ-475)

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
| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Stub (deferred tail of PROJ-475)
**Last Action:** Created during PROJ-475 planning as the capped-out remainder.
PROJ-475 closes the small `.session` reader tail + retires the three NARROW
pass-throughs (`enemy_empire`/`human_player_ids`/`active_empire`) + privatizes
`FacadeSessionState.session`. The THREE BROAD pass-throughs `galaxy`/`empires`/
`systems` were deferred here because they are a different problem shape: a
render/read-model boundary, not "finish the remaining readers."
**Next Action:** Do NOT start until PROJ-475 lands. Then plan the renderer-only
access boundary FIRST (this is the design crux).
**Blockers:** **GATED on PROJ-475.**

## Overview
Deferred tail of **PROJ-475**. Deletes the `galaxy` / `empires` / `systems`
pass-through properties on `StrategyScreen` (`strategy_screen.py:161-170`) and the
renderer re-exporters that proxy them (`strategy_renderer.py:124-138`), migrating
the broad raw-domain consumer base off the live galaxy/empires/systems. This is a
render/read-model boundary project: the render-hot path (`strategy_render/fleets.py`,
`hex_outlines.py`, `systems.py`, `warp_lanes.py`, `planets.py`, `dyson_spheres.py`)
must NOT get per-frame DTO churn — introduce a renderer-only access boundary
instead (pre-flesh consult §3 option i). Adds a THIRD static guard that measures
`scene.galaxy`/`scene.empires`/`scene.systems` consumption (the current two guards
do not).

## Goals
- Introduce a renderer-only access boundary (NOT per-frame DTOs) for the render
  stack's live galaxy/empires/systems traversal.
- Migrate context-menu builders (`strategy_ui.py`, `fleet_menu_items.py`,
  `planet_menu_items.py`), list/star/build-queue windows
  (`list_windows.py`, `planet_list_window.py`, `star_list_window.py`,
  `build_queue_windows.py`, `build_queue_screen.py`), `system_tree_panel`,
  colonization/superweapons/camera-nav/click-dispatch off the live galaxy.
- Add new facade surfaces for: object→system resolution, planets/zones/warp-points
  at hex with membership, all-live-systems iteration (consult §1c/§2).
- Add a third static guard for the pass-through property consumer surface.
- Delete `galaxy`/`empires`/`systems` pass-throughs once consumers are migrated.
- Retire the `StrategyScreen.session` GETTER (`strategy_screen.py:277`) — deferred
  from PROJ-475 because it still has live consumers: `system_tree_panel.py:418-425`
  resolves `scene.session` dynamically (`getattr(..., 'session')`), and the
  Category B mutator WRITE seams (`strategy_game_state_manager.py:164`,
  `strategy_screen_order_editing.py:66/:92`) write through `screen.session.<x>`.
  Migrate `system_tree_panel` off `scene.session`; route the write seams through a
  narrow facade/scene mutator handle; then retire the getter. Keep the SETTER
  (split-brain guard). Tighten the session guard for the bare/dynamic forms.

## Scope
**In:** `galaxy`/`empires`/`systems` pass-through deletion; renderer re-exporters +
render modules; the broad raw-domain consumer base; the renderer access boundary;
new spatial/membership facade queries; the third property-consumer guard.
**Out:** Everything PROJ-475 closes (the `.session` tail, the three narrow
pass-throughs, `FacadeSessionState.session`); tooling/editor screens (PROJ-476);
value/config allowlist (PROJ-474).

## Key Files (verified live 2026-05-22, from PROJ-475 pre-flesh consult)
| Component | File Path |
|-----------|-----------|
| Pass-throughs to delete | `game/ui/screens/strategy_screen.py:161-170` |
| Renderer re-exporters | `game/ui/screens/strategy_renderer.py:124-138` |
| Render-hot traversal | `game/ui/screens/strategy_render/{fleets,hex_outlines,systems,warp_lanes,planets,dyson_spheres}.py` |
| Context-menu builders | `game/ui/screens/strategy_ui.py:197-200,236-237`, `fleet_menu_items.py`, `planet_menu_items.py` |
| List/star/build-queue windows | `strategy_windows/list_windows.py`, `planet_list_window.py`, `star_list_window.py`, `strategy_windows/build_queue_windows.py`, `build_queue_screen.py` |
| System tree raw walk | `game/ui/panels/system_tree_panel.py:414-493` |
| Colonization/superweapons/etc. | `strategy_colonization.py`, `strategy_superweapons.py`, `strategy_camera_nav.py`, `strategy_click_dispatcher.py` |
| New property-consumer guard | `tests/static_guards/` (new) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
