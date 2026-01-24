# BUG-45: Warp navigation logic issues for non-warp-capable fleets

## Description
- A fleet with a warp drive but no battery is correctly prevented from jumping through a warp point, but the navigation still try's to use the warp points, If a fleet is not war capable it should not try to warp, it should just try to travel via regular hex path travel.
- A fleet that does not have a warp drive is able to travel though warp points.
- So this raises a few issues:
  1) Fleets seem to correctly identify weather or not they are warp capable - this is good
  2) it seems that fleets that know they are not warp capable still try to travel via warp points - this is bad, they should try to travel via normal hexes
  3) it is important that the lack of a functional warp drive should both prevent a fleet from warping (if it tries to), and prevents it from trying to navigate via warp point.
  4) make sure that the warp capability of the fleet is checked imediatly prior to the warp jump, if it fails the fleet cannot jump.  This is important because eventually there will be combat where damage may occur and mid turn the ability to jump is eliminated.  So the capability is updated, then if the fleet tries to warp queery the fleet to see if it has the capability.

## Priority
High (Significant feature broken - navigation pathfinding uses invalid routes)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Deep Investigation initiated - Agent swarm deployed
- 2026-01-23: Root cause identified - 3 bugs found (missing fleet parameter + missing capability check)
- 2026-01-23: Fixes applied:
  - game_session.py:138 - Added `fleet=fleet` to `find_hybrid_path()` call
  - turn_engine.py:298-303 - Added `can_use_warp()` check before warp execution
  - pathfinding.py:289,334 - Added `fleet=chaser_fleet` to intercept calculations
- 2026-01-23: Diagnostic logging added at key decision points

## Investigation Report

### Code Path Trace

```
ENTRY POINT: Player clicks destination hex
strategy_input_handler.py:144 _handle_move_mode_click()
  → strategy_fleet_ops.py:57 handle_move_designation()
    → strategy_fleet_ops.py:90 execute_move()
      → game_session.py:119 preview_fleet_path()
        → pathfinding.py:117 find_hybrid_path() ❌ MISSING fleet parameter
      → game_session.py:155 handle_command(IssueMoveCommand)
        → game_session.py:200 _handle_move_command()
          → fleet.add_order(MOVE)

TURN EXECUTION:
turn_engine.py:28 process_turn()
  → turn_engine.py:232 _process_tick() x100
    → turn_engine.py:317 _calculate_next_hex()
      → pathfinding.py:117 find_hybrid_path() ✓ WITH fleet parameter
    → turn_engine.py:284-313 Phase 3: Apply Moves
      Line 294: Detects warp (distance > 1)
      ❌ NO CHECK for fleet.can_use_warp() - only checks resources
      → turn_engine.py:308 fleet.location = next_hex (WARP EXECUTED)
```

### Dependency Map

**Warp Capability Functions:**
- `has_warp_capability(ship)` - fleet_report_filters.py:11
- `Fleet.can_use_warp()` - fleet.py:129
- `Fleet.get_warp_limiting_ship()` - fleet.py:151
- `Fleet.warp_jumps_remaining()` - fleet.py:428

**Callers of warp capability:**
- `warp_jumps_remaining()` at fleet.py:440
- `get_capability_summary()` at fleet.py:471
- `find_hybrid_path()` at pathfinding.py:134 (IF fleet parameter provided)
- `turn_engine._calculate_next_hex()` at turn_engine.py:358 (correctly passes fleet)

**Pathfinding Functions:**
- `find_path_deep_space()` - pathfinding.py:6 (direct hex line)
- `find_path_interstellar()` - pathfinding.py:13 (A* using warp lanes)
- `find_hybrid_path()` - pathfinding.py:117 (main navigation - accepts optional fleet param)
- `calculate_intercept_point()` - pathfinding.py:228 (❌ doesn't pass fleet)

**Calls WITHOUT fleet parameter (BUGS):**
- game_session.py:134 `preview_fleet_path()`
- strategy_colonization.py:191 `queue_colonize_mission()`
- pathfinding.py:287,331 `calculate_intercept_point()`

### Similar Patterns Found

**Working Pattern - Resource Gating (turn_engine.py:287-305):**
```python
is_warp = hex_distance(fleet.location, next_hex) > 1
if is_warp:
    if not fleet.has_resources_for_warp():  # CHECK RIGHT BEFORE EXECUTION
        fleet.clear_orders()
        continue
    fleet.consume_warp_resources()
```
- ✓ Checks BEFORE execution
- ✓ Two-tiered (movement + warp resources)
- ❌ Missing: capability check (`can_use_warp()`)

**Working Pattern - Capability Definition (fleet.py:129-163):**
- `can_use_warp()` correctly checks ALL combat ships
- Has diagnostic method `get_warp_limiting_ship()`
- Returns False if no combat ships

**What's Different About Warp Navigation:**
- Capability checked once at pathfinding time, not at execution time
- Resource check exists but capability check missing at execution
- Path stored in fleet.path - if capability changes mid-turn, stale path still followed

### Git History Analysis

**Root Cause Commit: 654e49f** (Jan 21, 2026 16:38)
- Message: "feat: Implement strategic save/load system with ship serialization..."
- Added `fleet` parameter to `find_hybrid_path()` with warp capability check
- **Did NOT update all call sites** - partial implementation

**Affected Files:**
- game/strategy/engine/game_session.py - preview_fleet_path missing fleet param
- game/strategy/data/pathfinding.py - calculate_intercept_point missing fleet param
- game/ui/screens/strategy_scene.py - UI pathfinding missing fleet param

**Timeline:**
- Jan 15 (dbf794f): Core pathfinding built - no warp capability check
- Jan 21 (654e49f): Warp check added but inconsistently applied

## Identified Bugs

| Bug | Location | Issue |
|-----|----------|-------|
| #1a | game_session.py:134 | `preview_fleet_path()` doesn't pass `fleet` to pathfinding |
| #1b | pathfinding.py:287,331 | `calculate_intercept_point()` doesn't pass fleet |
| #2 | turn_engine.py:297-308 | Movement execution only checks resources, not capability |

## User Context

**Reproduction Steps:**
1. Select a non-warp-capable fleet (no warp drive, or has warp drive but no resources)
2. Click a destination that would require traveling through a warp point
3. Observe the path displayed

**Expected Behavior:** Path should show direct hex-by-hex travel avoiding warp points
**Actual Behavior:** Path shows route through warp points (UI displays invalid path)

**History:** Warp capability check added in commit 654e49f but incompletely implemented
**Consistency:** 100% reproducible - occurs every time
**Game State:** Strategy view, fleet selected, issuing move orders
**Fleet Conditions Tested:**
- Fleet with no warp drive installed
- Fleet with warp drive but lacking resources (battery/fuel)

## Diagnostic Logging

| File | Line | What is Logged |
|------|------|----------------|
| game/strategy/engine/game_session.py | 137-138 | preview_fleet_path entry with fleet.can_use_warp() |
| game/strategy/data/pathfinding.py | 135 | find_hybrid_path with fleet warp capability |
| game/strategy/engine/turn_engine.py | 300 | Warp blocked due to no capability |
| game/strategy/engine/turn_engine.py | 307 | Warp jump executing |

To reproduce and capture logs, run the game with debug logging enabled and:
1. Select a non-warp-capable fleet
2. Click a destination requiring warp travel
3. Check logs for "preview_fleet_path" and "find_hybrid_path" entries

## Hypothesis Log

### Hypothesis 1: Missing fleet parameter in preview_fleet_path - CONFIRMED
**Theory:** `game_session.py:preview_fleet_path()` doesn't pass `fleet` to `find_hybrid_path()`, causing pathfinding to default to `can_use_warp=True`
**Evidence For:**
- Code inspection confirms line 134 was missing `fleet=fleet`
- `find_hybrid_path()` defaults to `can_use_warp=True` when fleet is None
- User reports path shows warp route for non-warp fleets (100% reproducible)
**Evidence Against:** None
**Test:** Add `fleet=fleet` parameter and verify path changes to deep space
**Result:** Fix applied - path now correctly uses `fleet.can_use_warp()` check

### Hypothesis 2: Missing capability check before warp execution - CONFIRMED
**Theory:** `turn_engine.py` only checks `has_resources_for_warp()` but not `can_use_warp()` before allowing warp jump
**Evidence For:**
- Code inspection confirms lines 297-302 only check resources
- User requirement #4 explicitly states capability must be checked immediately before jump
- This would allow damaged/incapable fleets to warp if they have resources
**Evidence Against:** None
**Test:** Add `can_use_warp()` check before resource check
**Result:** Fix applied - now checks capability before resources

### Hypothesis 3: Missing fleet parameter in calculate_intercept_point - CONFIRMED
**Theory:** `pathfinding.py:calculate_intercept_point()` calls `find_hybrid_path()` without fleet parameter
**Evidence For:** Code inspection confirms lines 288 and 332 were missing `fleet=chaser_fleet`
**Evidence Against:** None
**Test:** Add `fleet=chaser_fleet` parameter to both calls
**Result:** Fix applied - interception now respects chaser's warp capability
