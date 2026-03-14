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
Pending

## Work Log
- 2026-03-14: Created from QA Session 20260314_085600.
