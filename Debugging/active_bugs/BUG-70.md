# BUG-70: Colonize Order Should Load Population Before Moving

## Description

When I give a ship a colonize order, they should try to load population before they move, this should be an order in the order queue.

## Priority
High

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** When issuing colonize commands (both `IssueColonizeCommand` and `QueueColonizeMissionCommand`), no TRANSFER order was automatically inserted to load passengers before moving/colonizing. The fleet would arrive at the target with empty cargo, resulting in only a 100-unit minimum seed population.

**Changes:**

1. **`game/strategy/engine/game_session.py`**:
   - Added `_find_colony_at_fleet(fleet)` helper method - finds an empire colony in the system where the fleet is currently located
   - Updated `_handle_colonize_command()` - auto-inserts TRANSFER (load passengers, amount=0 for max) order before COLONIZE order when fleet is at a colony with population
   - Updated `_handle_colonize_mission_command()` - auto-inserts TRANSFER order before MOVE + COLONIZE orders

**Order Queue Result:**
- Before: `[MOVE, COLONIZE]`
- After: `[TRANSFER(load passengers), MOVE, COLONIZE]`

The TRANSFER order uses `amount=0` which means "load as much as possible" (up to cargo capacity), ensuring the colony ship carries maximum population to the new world.

**Tests:** All 1510 strategy/gameplay tests pass.
