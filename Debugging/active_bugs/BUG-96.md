# BUG-96: Build queue shows 1.0 turns and total cost instead of per-turn resource usage when item first added

## Description

When a ship or other item is first added to a build queue, the "Turns" column always displays 1.0 and the resource columns display the total cost of the item rather than the per-turn resource consumption. Both values are wrong until the first production tick recalculates them.

For example, a ship costing 8,119 Metals at a shipyard producing 3,000 Metals/turn should show ~2.7 turns and ~3,000 Metals/turn. Instead it shows 1.0 turns and 8,119 Metals because the per-turn resource display divides total cost by turns (8119 / 1.0 = 8119).

**Root cause:** In `command_handlers.py` `AddToConstructionQueueCommandHandler.execute()`, the queue item is created with a hardcoded `turns_remaining: 1.0` placeholder. The actual calculation (`max(cost[res] / rate[res])`) is deferred to `ProductionEngine._update_turns_remaining()` which only runs on the first production tick. The fix should pre-calculate the correct turn estimate at queue-add time using the build yard's production rates, so the UI is correct immediately.

### Screenshots

[![Build queue showing 1.0 turns and total costs](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_090212.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_090212.png)
*qs_general_purpose ship shows 1.0 turns and raw total costs (8119, 800, 380, 3989, 4269) instead of per-turn consumption rates*

## Priority
Low

## Status
Awaiting Confirmation

## Work Log
- 2026-03-14: Created from QA Session 20260314_085600.
- 2026-03-14: **Fixed.** Root cause confirmed: `AddToConstructionQueueCommandHandler.execute()` hardcoded `turns_remaining: 1.0`. The UI divides `total_cost / turns_remaining` for per-turn display, so `1.0` turns = showing raw total cost.
  - **Phase 0:** Checked `docs/systems/strategy_layer.md` — no conflicts. Reviewed PROJ-208/209/213 commit history for affected files — fix preserves all refactors.
  - **Phase 1:** Added `test_turns_remaining_precalculated_from_production_rate` — confirmed turns_remaining was 1.0 regardless of cost/rate.
  - **Phase 2:** Added `_get_production_rate()` and `_estimate_turns()` to `AddToConstructionQueueCommandHandler`:
    - `_get_production_rate`: resolves production rate based on entity type (Fleet → fleet_space_yard, Planet facility → facility rates, Planet base → planetary_yard)
    - `_estimate_turns`: computes `max(cost[res] / rate[res])` — same formula ProductionEngine uses on tick 1
  - **Phase 3:** Pre-calculates `turns_remaining` before creating the queue item dict. Falls back to 1.0 if rates unavailable.
  - **Tests:** 4 new tests (precalculated turns, limiting resource, empty cost fallback, zero rate fallback). 74/74 command handler tests pass.
  - **Files modified:** `game/strategy/engine/command_handlers.py`, `tests/unit/strategy/test_command_handlers.py`
- 2026-03-14: **Refactored.** Eliminated duplicated logic from the command handler by extracting two public utilities into `build_queue_source.py`:
  - `estimate_build_turns(total_cost, production_rate)` — single source of truth for the limiting-resource formula `max(cost[res] / rate[res])`. Used by the command handler for initial estimates; matches ProductionEngine's per-tick calculation.
  - `get_production_rate_for_queue(entity, queue_id)` — unified rate resolution using the same helpers as `_collect_planet_sources` / `_collect_fleet_sources`.
  - Deleted `_get_production_rate()` and `_estimate_turns()` from `AddToConstructionQueueCommandHandler` (~55 lines removed).
  - Handler now delegates: `get_production_rate_for_queue(entity, cmd.queue_id)` → `estimate_build_turns(total_cost, rate)`.
  - Formula tests moved to `test_build_queue_source.py` (8 new: TestEstimateBuildTurns). Rate tests added (7 new: TestGetProductionRateForQueue, including consistency check vs `collect_build_queues_at_hex`).
  - Handler test updated to verify delegation via mocks.
  - Updated `docs/systems/production_system.md` to document the pre-calculation path.
  - **Files modified:** `game/strategy/data/build_queue_source.py`, `game/strategy/engine/command_handlers.py`, `tests/unit/strategy/data/test_build_queue_source.py`, `tests/unit/strategy/test_command_handlers.py`, `docs/systems/production_system.md`
  - **Tests:** 13176 passed, 2 skipped, 0 failures (full suite).
