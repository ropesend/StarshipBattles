# PROJ-475: Facade read-path: remaining live strategy-screen + render readers migration (follow-on from PROJ-472)

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
| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-21
**Active Phase:** Stub (deferred tail of PROJ-472)
**Last Action:** Stub created + scoped during PROJ-472 planning; recorded the explicit set of session readers + import-allowlist entries deferred here from PROJ-472 Phase 1 (post-flesh Codex review, 2026-05-21).
**Next Action:** Do NOT start until PROJ-472's two read-path static guards have landed. Then plan phases per UI feature cluster, starting from the "Deferred from PROJ-472 Phase 1" table.
**Blockers:** **GATED on PROJ-472** — both guards (import + session-read) and the build-queue/session-consumer slice must land first; this project migrates the remaining live readers under those guards and tightens the matchers.

## Overview
Follow-on from **PROJ-472**. After 472 lands the policy + guards + build-queue
cluster + the first session-consumer batch, the **live strategy-screen and render
readers** that still bypass the facade remain. THIS project migrates those
remaining live-gameplay UI readers onto facade accessors AND deprecates the two
documented transitional surfaces 472 deliberately left in place:
`StrategyScreen`'s pass-through properties (`galaxy` / `empires` / `systems` /
`active_empire` / `human_player_ids`) and `FacadeSessionState`'s public `session`
attribute. Only after this can the read path honestly be called closed for the
live UI.

## Goals
- Migrate remaining live `game/ui/screens/` + `screens/strategy_render/` +
  `screens/strategy_windows/` readers that bypass the facade onto facade
  accessors (excludes tooling/editor screens — PROJ-476).
- Deprecate the `StrategyScreen` pass-through properties (`strategy_screen.py:160-189`)
  and remove their session-read-guard allowlist entries.
- Reduce/remove the public `FacadeSessionState.session` exposure
  (`_facade_state.py:63-86`) or restrict it to the engine/test seam, keeping the
  documented per-turn cache holder as a performance boundary (`:48-60`).
- Respect render-hot-path caution: no per-frame DTO allocation
  (`strategy_render/hex_outlines.py`, `strategy_render/fleets.py`).

## Scope
**In:** Remaining live strategy-screen / render / strategy-windows readers;
pass-through property + `FacadeSessionState.session` deprecation; guard matcher
tightening. Includes the session readers + import allowlist entries PROJ-472
Phase 1 explicitly deferred here (see "Deferred from PROJ-472 Phase 1" below).
**Out:** Value/config allowlist consolidation (PROJ-474); tooling/editor screens
battle_setup / galaxy_test / race_setup / builder (PROJ-476); anything PROJ-472
already migrated (build-queue cluster, the first session-consumer batch, and
`strategy_render/fleets.py`'s path-projection read — migrated in 472 Phase 1C).

## Deferred from PROJ-472 Phase 1 (allowlisted-with-reason; migrate here)
These sites are verified-present (2026-05-21) but were intentionally left
allowlisted-with-reason by PROJ-472's two guards. PROJ-475 owns migrating them
and removing the corresponding allowlist entries.

**Session READERS deferred from 472 Phase 1C (session-read guard allowlist):**
| Site | Read | Why deferred |
|------|------|--------------|
| `game/ui/screens/strategy_event_router.py:223`, `:368` | `scene.session.get_empire(planet.owner_id)` (race-config lookup) | Needs a facade empire / race-config accessor that does not exist yet |
| `game/ui/screens/strategy_screen_selection.py:93` | `screen.session.active_empire` (BUG-125 gate) | Paired with the `strategy_screen.py` `active_empire` pass-through this project deprecates |
| `game/ui/screens/strategy_screen_order_editing.py:42` | `screen.session.active_empire` (BUG-125 gate) | Same `active_empire` pass-through dependency (`:66`/`:92` are mutator WRITES — separate write-seam allowlist) |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py:62` | `c.scene.session.registries` (registries DI) | Registries-DI seam; migrate alongside the facade registries-accessor rollout |

**Import allowlist deferred from 472 Phase 1B (import guard allowlist):**
| Site | Import | Why deferred |
|------|--------|--------------|
| `game/ui/screens/fleet_data_source.py:241-245` | `FleetCapabilityCalculator` (late import) | Pure per-ship spaceyard capability check; no facade query exists yet |
| `game/ui/screens/fleet_report_filters.py:163`, `:302` | `FleetCapabilityCalculator` (late import) | Same per-ship capability check (filter + sort key) |
| `game/ui/screens/strategy_detail_formatter.py:277` | `colony_has_planetary_yard` from `game.strategy.data.build_queue_source` | Pure read helper `(colony, registries) -> bool`; returns no live ref, but no facade query exists yet. Surfaced by the PROJ-472 end-of-project Codex audit (finding 4) as an orphaned CLUSTER allowlist entry; migrate here when the facade gains a "colony has yard" projection. |

(If a facade per-ship capability query is added, all three
`FleetCapabilityCalculator` sites collapse to it in one change.)

**Bare-session ESCAPE seams deferred from 472 Phase 1D (session-read guard
allowlist, Category E).** PROJ-472 1D hardened the session-read guard to catch
aliased/bare `.session` extraction (Codex audit finding 2). These pre-existing
sites hand the live session object wholesale to a save service or alias it into
a local; they are allowlisted-with-reason and migrate here (save seams) /
PROJ-476 (transfer tooling tail):
| Site | Read | Why deferred |
|------|------|--------------|
| `game/ui/screens/strategy_game_state_manager.py:397` | `SaveGameService.save_game(self._screen.session)` | Save seam; needs a facade save entry point or a session-bound save service |
| `game/ui/screens/strategy_screen_lifecycle.py:51` | `screen.session` in the lifecycle context dict (`game_session`) | Save/context seam; same facade-save dependency |
| `game/ui/screens/transfer_controller.py:160` | `session = scene.session` (alias) for the per-empire design catalog | Transfer tooling tail (PROJ-476 candidate); needs the facade per-empire design-catalog accessor introduced in 472 1C wired here |

## Key Files
| Component | File Path |
|-----------|-----------|
| StrategyScreen pass-through properties (deprecate) | `game/ui/screens/strategy_screen.py:160-189` |
| FacadeSessionState public `session` (restrict) | `game/strategy/facade/slices/_facade_state.py:63-86` |
| Render-hot readers (caution) | `game/ui/screens/strategy_render/hex_outlines.py` (the `fleets.py:85` path-projection read is migrated in PROJ-472 Phase 1C; check `fleets.py` for any OTHER residual readers here) |
| System tree raw-content reader | `game/ui/panels/system_tree_panel.py:177-313`, `:414-640` |
| Session-read + import guards (tighten) | `tests/static_guards/test_facade_read_path_session_guard.py`, `tests/static_guards/test_facade_read_path_imports_guard.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
