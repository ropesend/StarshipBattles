# FEAT-17: Build queue pause/unpause toggle button

## Description
Add a "Pause Build Queue" button at the bottom-left of the build queue panel
(Build Yards view, per-planet/per-sector). When pressed:
- The queue stops consuming any resources for the affected yard.
- The button label flips to "Unpause Build Queue".
- The currently-progressing item retains its accumulated progress
  (no rollback).
- Pressing Unpause resumes consumption from the saved progress on the next
  turn tick.

The queue's order, contents, and reorder up/down arrows remain operable while
paused.

Reproduced layout in QA Session 20260427_151244 at 15:42:

[![Empty per-yard build queue panel — "Verona I - Planetary Yard"](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_154228.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_154228.png)

## Required changes
- `game/ui/screens/empire_build_queue_window.py` (or per-yard build queue panel
  file) — add the toggle button at bottom-left.
- `game/strategy/` build yard / queue model — add a `paused: bool` flag per
  yard. Resource-consumption tick respects the flag.
- Save/load — serialise the paused flag with the queue state.

## Acceptance
- Toggle button visible and functional on every per-yard build queue panel.
- Paused yard consumes 0 resources per turn while paused.
- Toggle persists across save/load.
- Resuming continues progress from where it left off (no progress reset).

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Implemented (TDD).
  - **Approach:** added `construction_queue_paused: bool = False` field to the three yard-owning entities (`Planet`, `PlanetaryFacility`, `Fleet`). `ProductionEngine.process_construction_tick` now gates each of its three iteration sites (planet base queue / facility queue / fleet yard queue) on the flag; the existing `_process_queue_tick_dynamic` helper is unchanged so the dispatcher/processor separation stays clean. Treasury (`EmpireEconomyCalculator._aggregate_construction_expenses`) and Planet-detail (`PlanetEconomyProjector._project_yard_drain`) skip paused queues so the forecasted next-turn drain matches what `ProductionEngine` will actually consume — `forecast_queue_turn_spend` itself remains a pure function of (queue, build_rate). `BuildQueueSource` gained a derived `is_paused: bool`, populated by `_collect_planet_sources` / `_collect_fleet_sources` from the owning entity at collection time. New `SetBuildQueuePausedCommand` + `SetBuildQueuePausedCommandHandler` follow the PROJ-208 CQRS pattern (sibling to Add/Remove/Reorder). New `BaseCommandHandler._resolve_queue_owner` mirrors `_resolve_queue` but returns the owner (Planet/Facility/Fleet) instead of the list. UI: text-only "Pause Build Queue" / "Unpause Build Queue" toggle button at the bottom-left of the per-yard build queue panel; Empire Build Queue Window gets a read-only "Status" column showing PAUSED.
  - **Decision:** AI controllers do **not** toggle pause — the flag is a player-driven control. No AI code touched; default-False is the only path for AI-built fleets/colonies.
  - **Decision:** flag lives on the yard-owning entity, NOT on `BuildQueueSource` (transient/derived) and NOT per queue item. The currently-progressing item retains its `resources_consumed` while paused; unpausing resumes from saved progress on the next tick (no rollback, no field touched).
  - **Decision:** save/load uses `data.get('construction_queue_paused', False)` so legacy saves (without the key) load with paused=False. No save-version bump per CLAUDE.md "saves are disposable" policy.
  - **Files modified (production):**
    - `game/strategy/data/planet.py` — field + to_dict/from_dict.
    - `game/strategy/data/planetary_facility.py` — field + to_dict/from_dict.
    - `game/strategy/data/fleet.py` — field + to_dict/from_dict.
    - `game/strategy/data/build_queue_source.py` — `is_paused` field on `BuildQueueSource`; populated in `_collect_planet_sources` (base + each facility) and `_collect_fleet_sources`.
    - `game/strategy/engine/production_engine.py` — three pause guards in `process_construction_tick`.
    - `game/strategy/engine/empire_economy_calculator.py` — skip paused queues in `_aggregate_construction_expenses` (planet base / facility / fleet).
    - `game/strategy/services/planet_economy_projector.py` — skip paused `BuildQueueSource` in `_project_yard_drain`.
    - `game/strategy/engine/commands.py` — `SetBuildQueuePausedCommand`.
    - `game/strategy/engine/handlers/construction_queue.py` — `SetBuildQueuePausedCommandHandler`.
    - `game/strategy/engine/handlers/base.py` — `_resolve_queue_owner` static method.
    - `game/strategy/engine/handlers/registry_factory.py` — register the handler.
    - `game/ui/screens/build_queue_panel_factory.py` — `_PAUSE_FOOTER_HEIGHT` + `_pause_button_label` helpers, footer strip + button in `_create_build_queue_panel`, `btn_pause_queue` field on `BuildQueuePanels`.
    - `game/ui/screens/build_queue_screen.py` — `_dispatch_toggle_pause_command`, button event hook, label refresh on selector change + queue display refresh.
    - `game/ui/screens/build_queue_renderer.py` — `refresh_pause_button(active_source)`.
    - `game/ui/screens/empire_build_queue_filter_manager.py` — new `'paused'` column in `DEFAULT_COLUMNS`.
    - `game/ui/screens/empire_build_queue_viewmodel.py` — `'paused'` cell renderer ("PAUSED" / "").
  - **Files modified (tests):**
    - `tests/unit/strategy/production_engine/test_paused_queue.py` (NEW, 6 tests).
    - `tests/unit/strategy/data/test_construction_queue_paused_persistence.py` (NEW, 8 tests — Planet + Fleet round-trip + legacy-save defaults).
    - `tests/unit/strategy/data/test_facility_construction_queue.py` (+4 tests).
    - `tests/unit/strategy/data/test_build_queue_source.py` (+5 propagation tests).
    - `tests/unit/strategy/services/test_planet_economy_projector.py` (+2 paused-yard-drain tests).
    - `tests/unit/strategy/engine/test_empire_economy_calculator.py` (+2 paused-treasury tests; pinned `construction_queue_paused=False` in mock helpers).
    - `tests/unit/strategy/engine/test_set_build_queue_paused_command.py` (NEW, 7 handler tests).
    - `tests/unit/strategy/production_engine/test_tick_consumption.py` (pinned `construction_queue_paused=False` in mock fixture so existing tests stay deterministic).
    - `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` (column-list expectation +1 entry).
    - `tests/unit/ui/screens/test_empire_build_queue_window.py` (column-count 18 → 19).
  - **Files modified (docs):**
    - `docs/systems/production_system.md` — new "Per-Yard Pause Flag (FEAT-17)" subsection, `BuildQueueSource.is_paused` note in Queue Discovery section, `Last verified:` bumped.
    - `docs/systems/strategy_layer.md` — `construction_queue_paused` noted alongside `construction_queue` in the Fleet data-model section (with cross-reference to Planet + PlanetaryFacility), `Last verified:` bumped.
  - **Test results:** Targeted 37/37 paused-feature tests pass; full sharded suite **15802/15802 pass, 0 failed, 0 errors** (52.9s wall, up from 15405 baseline by 397 — those 397 are FEAT-17 + parallel teammate tests landed since baseline).
  - **QA-ticket reproduction:** Pause button at bottom-left of per-yard build queue panel; label flips between "Pause Build Queue" / "Unpause Build Queue"; paused yard consumes 0 resources/turn; queue order/contents/reorder arrows still operable while paused; resume continues from saved `resources_consumed` (no rollback); flag persists across save/load.
  - **Save compatibility:** new field uses `.get(..., False)` defaults — pre-FEAT-17 saves load with paused=False without migration code.
  - **Branch:** `main` (worktree not enabled per coordinator).
  - **Note for FEAT-18 (down-arrow button, will land later):** my edits to `game/ui/screens/build_queue_panel_factory.py` are confined to module-level constants near the top, the `BuildQueuePanels` dataclass (one new `btn_pause_queue` field), `create_all_panels` (one tuple-unpack expansion), and `_create_build_queue_panel` (returns a 6-tuple now instead of 5; `table_panel` height shrunk by `_PAUSE_FOOTER_HEIGHT=50` to make room for the new bottom-of-panel pause button). FEAT-18's down-arrow logic is in `build_queue_queue_data_source.py` + `virtual_table.py` and does not collide. If FEAT-18 changes the actions-column width inside the build queue panel, no interaction with my footer.
