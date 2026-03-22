# BUG-98: Build Queue "Next Turn" Resource Columns Show Incorrect Per-Item Values

## Description
The build queue's "next turn" resource columns display incorrect values. Each queued item shows the full build rate (e.g., 3,000 metals/turn) regardless of queue position, rather than the actual amount that will be consumed during the next turn.

The correct behavior should distribute available production across queued items sequentially. For example, with a 3,000 metals/turn build rate and items costing 749 metals each:
- Items 1–4 should show 749 metals each (total 2,996)
- Item 5 should show 4 metals (the remainder)
- Item 6 should show 0 metals

The root cause is in `calculate_per_turn_spend()` (`game/ui/screens/build_queue_helpers.py`), which calculates each item's rate independently assuming it gets the full build rate, with no logic to distribute production across the queue.

Additionally, when a single item will complete partway through the turn, the "next turn" amount should reflect only the resources needed to finish (i.e., the remaining cost), not the full turn's production rate.

### Screenshots

Single qs_escort queued in Shipyard 1. The "next turn" metals column shows 3,000, but the remaining cost is only 749 metals — since it will finish well within one turn, the next-turn value should equal the remaining cost (749):
[![Single item showing 3,000 metals next turn instead of 749 remaining](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_051733.png)](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_051733.png)

Three identical qs_escorts queued. Each shows 3,000 metals next turn, but at 749 metals each, all three should show 749 (total 2,247, well within the 3,000/turn build rate):
[![3 items each incorrectly showing 3,000 metals](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_051921.png)](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_051921.png)

Five qs_escorts queued (6th scrolled off). All show 3,000 metals next turn. The correct values: items 1–4 should show 749 each (2,996 total), item 5 should show 4 (the remaining production capacity), and item 6 should show 0:
[![5 items all showing 3,000 metals — should distribute 749 each across first 4, then remainder](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_052006.png)](../../Tools/qa_observer/session_data/20260322_051459/images/bug_capture_052006.png)

## Priority
Medium

## Status
Awaiting Confirmation

## Investigation Report

### Code Path Trace
```
UI Display Path:
  BuildQueueScreen._refresh_queue_display()
    → BuildQueueRenderer.refresh_queue_display(queue, build_rate)
      → BuildQueueQueueDataSource.set_queue(queue, build_rate)
        → VirtualTable renders rows, calls get_cell_value(row, col) per cell
          → For "met_rate"/"org_rate"/etc columns:
            → calculate_per_turn_spend(item, self._build_rate)  ← BUG: per-item, no queue context
            → Returns formatted value

Production Engine (correct behavior):
  ProductionEngine._process_queue_tick_dynamic(queue, production_rate)
    tick_capacity = 1.0
    while tick_capacity > 0 and queue not empty:
      item = queue[0]  ← Always processes HEAD first
      expenditure = _calculate_tick_expenditure(item, tick_capacity, production_rate)
      tick_capacity -= expenditure.ticks_to_spend  ← CARRIES OVER remaining capacity
      if item complete: queue.pop(0) and continue with remaining capacity
```

### Dependency Map
**Callers of `calculate_per_turn_spend()`:**
- `game/ui/screens/build_queue_queue_data_source.py:142` — `BuildQueueQueueDataSource.get_cell_value()`
- `tests/unit/ui/screens/test_build_queue_helpers.py` — 9 test cases

**Callees:** Pure function, no external dependencies (only dict operations and arithmetic).

**Data flow:**
- `build_rate` comes from `BuildQueueSource.build_rate` → loaded from `data/production_rates.json` via `get_default_production_rates()` in `game/strategy/data/build_queue_source.py`
- Queue items created by `AddToConstructionQueueCommandHandler` in `game/strategy/engine/command_handlers.py:790-796` with `{total_cost, resources_consumed, turns_remaining, design_id, type}`

### Similar Patterns Found
- `ProductionEngine._calculate_tick_expenditure()` (`game/strategy/engine/production_engine.py:347-419`) — Correct per-tick calculation with `tick_capacity` parameter that limits spend to available capacity
- `ProductionEngine._process_queue_tick_dynamic()` (line 240) — Sequential processing loop with carry-over: `tick_capacity -= expenditure.ticks_to_spend`
- `FleetCargoProjector.get_projected_cargo()` (`game/strategy/services/fleet_cargo_projector.py`) — Correct queue-walk projection pattern: iterates orders sequentially, applies deltas to a running total

### Git History Analysis
- `f97622fa` (2026-03-14): PROJ-221 Phase 2 — Introduced `calculate_per_turn_spend()` with the limiting-resource formula for single-item isolation
- `6aee5516` (2026-03-01): Introduced per-tick resource consumption in ProductionEngine
- `795d6fa5`: PROJ-209 Phase 2 — Extracted `_calculate_tick_expenditure()` from ProductionEngine
- No previous attempts to implement queue-wide distribution found

### Documentation Discrepancies
**Code vs docs mismatches:** The `calculate_per_turn_spend()` docstring claims "This matches the proportional calculation in ProductionEngine._calculate_tick_expenditure()" — this is misleading. It matches the *per-item proportional formula* but not the *queue-wide distribution* behavior.
**Docs last updated:** 2026-03-14 (production_system.md)
**Code last updated:** 2026-03-14 (build_queue_helpers.py)

## Hypothesis Log

### Hypothesis 1: Architectural Mismatch — No Queue-Wide Distribution Logic - CONFIRMED
**Theory:** `calculate_per_turn_spend()` was designed as a per-item formatter, but the "next turn" columns require queue-wide forecasting. The function calculates each item's spend assuming it gets the full build rate, with no awareness of queue position or items ahead of it.
**Evidence For:**
- Function signature `(queue_item, build_rate)` — receives single item, not queue
- Called per-cell in `get_cell_value()` with no queue index or prior-consumption context
- ProductionEngine uses `tick_capacity` carry-over (line 286: `tick_capacity -= expenditure.ticks_to_spend`) — this concept is absent from the UI
- Bug report shows all items displaying 3,000 metals regardless of position
**Evidence Against:** None
**Test:** Compare function output for 5 identical 749-metals items vs. ProductionEngine behavior
**Result:** Function returns 749 for ALL items. Engine returns 749 for items 1-4, 4 for item 5, 0 for item 6.

### Root Cause Summary
The fix requires replacing the per-item `calculate_per_turn_spend()` call with a **queue-level distribution function** that:
1. Takes the **full queue** and **build_rate** as input
2. Walks items sequentially, tracking remaining capacity (starting at 1.0 turn)
3. For each item: calculates how much capacity it consumes (using the limiting-resource formula), deducts from remaining capacity, and records the per-turn spend
4. Items that exceed remaining capacity get partial or zero spend
5. Returns a list of per-item spend dicts, indexed by queue position

The `BuildQueueQueueDataSource` would call this once per `set_queue()` and cache the results, then `get_cell_value()` would look up the pre-computed value by row index.

## User Context

**Reproduction Steps:**
1. Open the build queue for any planet with a shipyard
2. Queue multiple identical cheap items (e.g., qs_escort at 749 metals each)
3. Observe the "Met/t" column — all items show the full build rate (e.g., 3,000)

**Expected Behavior:** Production distributed sequentially — items 1-4 show 749 each, item 5 shows 4, item 6 shows 0 (for a 3,000/turn rate)
**Actual Behavior:** Every item shows 3,000 (the full build rate) regardless of queue position

**History:** Not sure — may have always been this way since PROJ-221 introduced the columns
**Consistency:** Always fails — every queue with multiple items shows incorrect values
**Game State:** Any planet build queue with 2+ items
**Known Workarounds:** None

**Scope decisions:**
- Do NOT account for empire resource pool limits — just show build-rate distribution
- Fix per-planet queue only — empire-wide build queue is a separate concern

## Work Log
- 2026-03-22: Created from QA Session 20260322_051459.
- 2026-03-22: Deep Investigation — Root cause confirmed as architectural mismatch. `calculate_per_turn_spend()` processes items in isolation; needs queue-wide sequential distribution matching ProductionEngine's carry-over logic.
- 2026-03-22: User interview complete. Scope: per-planet queue only, no resource pool caps.
- 2026-03-22: Fix implemented via TDD. Added `calculate_queue_turn_spend()` in `build_queue_helpers.py` — distributes production sequentially across queue with carry-over. Updated `BuildQueueQueueDataSource` to pre-compute distribution on `set_queue()` and cache results. Updated data source test. 58/58 tests pass, 1786/1786 UI screen tests pass.
