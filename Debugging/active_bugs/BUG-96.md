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
Awaiting Confirmation (Deep Investigation fix)

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

---
### ❌ Fix Rejected [2026-03-14 20:35]
**Reason:** The turn calculation is now correct (shows 0.1846 instead of the old hardcoded 1.0). However, the resource columns display incorrect values on the final turn. The first turn showed correct/reasonable per-turn resource amounts, but on the second (final) turn the values were grossly inflated (e.g., 19,245 metals for a ship with a total cost of 3,554 metals). The final turn should display the remaining amount of each resource, not inflated figures.

**New Constraints:**
- The per-turn resource display is correct on the first turn but wrong on subsequent/final turns
- The final turn should show only the remaining resource cost, not the full or inflated amount
- Turn estimate calculation itself is working correctly now

[![Build queue showing inflated resource values on final turn](../../tools/qa_observer/session_data/20260314_202945/images/bug_capture_203430.png)](../../tools/qa_observer/session_data/20260314_202945/images/bug_capture_203430.png)
*Build queue for qs_colony_cryoplanet shows 0.1846 turns remaining but resource values (19245, 1949, 1353, 8009, 8702) far exceed the ship's total build cost*

[![Ship stats showing actual build cost](../../tools/qa_observer/session_data/20260314_202945/images/bug_capture_203517.png)](../../tools/qa_observer/session_data/20260314_202945/images/bug_capture_203517.png)
*Cryoplanet Colony Ship total build cost is only 3554 metals, 360 organics, 250 vapors, 1479 radact, 1607 exotics — far less than the queue display*
---

## Investigation Report

### Code Path Trace
`AddToConstructionQueueCommandHandler.execute()` [command_handlers.py:770] → creates queue item with `total_cost`, `resources_consumed` (zeros), `turns_remaining` (pre-calculated) → `ProductionEngine._process_queue_tick_dynamic()` [production_engine.py:205] → `_apply_resource_consumption()` accumulates `resources_consumed` per tick → `_update_turns_remaining()` updates `turns_remaining` → `BuildQueueRenderer.refresh_queue_display()` [build_queue_renderer.py:170] → **line 220: `per_turn = total_amt / turns`** ← BUG

### Dependency Map
**Callers of buggy display code:** `BuildQueueScreen` triggers `refresh_queue_display()` on queue changes
**Data sources:** Queue item dict contains `total_cost` (constant), `resources_consumed` (accumulated per tick), `turns_remaining` (recalculated per tick)

### Similar Patterns Found
- `ProductionEngine._calculate_tick_expenditure()` [production_engine.py:369-377] correctly uses `remaining_cost = total_cost[res] - resources_consumed[res]` — the display should follow the same pattern
- `EmpireBuildQueueFormatter.get_resource_rate_text()` [empire_build_queue_formatter.py:145-165] uses `cost_per_tick` field (never populated, shows "-")

### Git History Analysis
**Suspect commit:** The BUG-96 fix that pre-calculates `turns_remaining` exposed the renderer's formula. Previously, `turns_remaining` was always 1.0 initially, so `total_cost / 1.0 = total_cost` (wrong but not inflated). Now with correct fractional `turns_remaining`, the same formula produces inflated values.

### Documentation Discrepancies
**Code vs docs mismatches:** None — `docs/systems/production_system.md` correctly documents `remaining_cost = total_cost - resources_consumed` as the production algorithm. The renderer simply wasn't following this documented pattern.

## User Context

**Reproduction Steps:**
1. Queue a ship for construction at a shipyard
2. End turn (first production turn consumes most resources)
3. Observe build queue on the second turn when `turns_remaining < 1.0`

**Expected Behavior:** Resource columns show remaining cost (e.g., 554 metals remaining of 3,554 total)
**Actual Behavior:** Resource columns show `total_cost / turns_remaining` (e.g., 3,554 / 0.1846 = 19,245)

**History:** Bug introduced by the BUG-96 fix that corrected `turns_remaining` from hardcoded 1.0 to accurate pre-calculation
**Consistency:** Always fails when `turns_remaining < 1.0`
**Game State:** Build queue screen, any build context (planet/fleet)
**Known Workarounds:** None

## Hypothesis Log

### Hypothesis 1: Display divides total_cost by turns_remaining instead of using remaining_cost - CONFIRMED
**Theory:** `build_queue_renderer.py:220` calculates `per_turn = total_amt / turns` using the full `total_cost` rather than `total_cost - resources_consumed`. When `turns < 1.0`, this produces values exceeding total cost.
**Evidence For:** Code at line 220 clearly shows `total_amt = total_cost.get(resource, 0)` with no subtraction of consumed resources. Screenshot shows 19,245 metals for a 3,554-metal ship with 0.1846 turns remaining (3554 / 0.1846 ≈ 19,245).
**Evidence Against:** None.
**Test:** Calculate 3554 / 0.1846 = 19,245 — matches screenshot exactly.
**Result:** CONFIRMED. Root cause identified.

- 2026-03-14: **Deep Investigation — Fixed.** Root cause: `build_queue_renderer.py:220` used `total_cost / turns_remaining` for display. When `turns_remaining < 1.0`, this inflated values above total cost. Fix: changed display to show remaining cost (`total_cost - resources_consumed`) instead of a per-turn rate calculation. User confirmed they want remaining cost displayed, not a rate.
  - **Files modified:** `game/ui/screens/build_queue_renderer.py`
  - **Tests:** 1680 UI screen tests passed, 2404 strategy tests passed, 0 failures.
