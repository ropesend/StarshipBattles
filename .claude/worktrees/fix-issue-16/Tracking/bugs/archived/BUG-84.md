# BUG-84: Warp Gate Close and Planet Destroyer orders not registering

## Description

When I order a ship with a warp gate close on it to close a warp point, nothing happens, no orders show up, no action is taken, I'm not even sure if it registers the key presses. Same thing for the planet destroyer.

## Priority
High

## Status (Awaiting Confirmation)

## Work Log

### Investigation (2026-02-11)

**Findings:** The entire code pipeline appears correctly wired:
- **Keybindings:** `Ctrl+L` -> `fleet.close_warp_point`, `Ctrl+I` -> `fleet.implode_planet` (in `data/default_keybindings.json`)
- **Input handler:** `_handle_superweapon_action()` sets input mode (e.g., `CLOSE_WARP_TARGET`)
- **Click handler:** `_handle_close_warp_click()` calls `SuperweaponOperations.handle_close_warp_designation()`
- **Operations:** Shows confirmation dialog, issues `QueueCloseWarpPointMissionCommand`
- **Command handler:** `CloseWarpPointMissionCommandHandler` creates `FleetOrder(OrderType.CLOSE_WARP_POINT)`
- **Turn execution:** `SuperweaponOrderProcessor.process_close_warp_point()` executes the order

**Possible causes to investigate:**
1. Runtime: Verify the key presses actually reach `_handle_keydown_mapped()` (add temporary logging)
2. Runtime: Verify `fleet.capabilities.has_ability("CloseWarpPoint")` returns True for the test fleet
3. Runtime: Check if any UI element (pygame_gui) is consuming the Ctrl+L event before it reaches the input handler
4. Component naming: Verify the component JSON defines abilities with exact names "CloseWarpPoint" / "DestroyPlanet"

**Status:** Blocked - needs runtime debugging with actual game session to identify where the flow breaks.

---
### 📝 User Update [2026-03-14]
**Source:** QA Session 20260314_094507

New findings from live gameplay testing:

1. **Partial functionality confirmed:** The close warp point order DOES work, but only if the ship is already in the sector containing the warp point before the order is given. If the ship is elsewhere, the order does not appear in the orders queue. The confirmation dialog appears regardless (see screenshot), but the order is silently dropped if the ship isn't at the target sector.

2. **New issue — wrong-sector execution risk:** The validation should check that the ship is at the correct specific warp point when execution occurs. If move orders are rearranged and the ship ends up at a different sector containing a different warp point, the wrong warp point should NOT be closed.

3. **New issue — fleet destroyed on warp point close:** When a warp point is successfully closed, the fleet containing the ship is lost/destroyed. The fleet should survive the operation.

[![Close Warp Point confirmation dialog](../../tools/qa_observer/session_data/20260314_094507/images/bug_capture_095705.png)](../../tools/qa_observer/session_data/20260314_094507/images/bug_capture_095705.png)

*Close Warp Point confirmation dialog — this dialog appears correctly, but the order only registers if the ship is already at the warp point's sector.*

**Impact on investigation:** Finding #1 narrows the root cause — the order creation pipeline works, but the command handler or validation logic incorrectly requires the ship to already be at the destination sector at order-creation time rather than at execution time.

## Investigation Report

### Code Path Trace
```
UI: Ctrl+L → FleetCommandRouter.handle_superweapon_action() → input_mode='CLOSE_WARP_TARGET'
    → Click → StrategyClickDispatcher._handle_close_warp_click()
    → SuperweaponOperations.handle_close_warp_designation(mx, my, fleet)
      → fleet.capabilities.has_ability("CloseWarpPoint") [UI-level check]
      → _get_warp_point_at_hex(target_hex) [finds warp point]
      → Shows confirmation dialog
      → QueueCloseWarpPointMissionCommand(fleet_id, target_hex, warp_point.destination_id)
        → StrategySessionFacade.handle_command()
          → CommandHandlerRegistry.dispatch()
            → CloseWarpPointMissionCommandHandler.execute()
              → SuperweaponValidator.validate_close_warp_point() ← FAILS HERE if fleet not at warp point
              → _setup_mission_move() [queues MOVE order]
              → FleetOrder(CLOSE_WARP_POINT, target=destination_id)

Execution: TurnEngine tick loop
    → Phase 1.5: ActionExecutionEngine.process_action_ticks()
      → _process_fleet_action_tick() → check execution_progress >= action_time
      → _execute_action() → FleetOrderProcessor.execute_action_order()
        → SuperweaponOrderProcessor.process_close_warp_point()
          → galaxy.remove_warp_link(current_system.name, destination_id)
          → _finalize_superweapon() → fleet.remove_ship(ship) ← CONSUMES SHIP
```

### Dependency Map
**Key files:**
- `game/strategy/validation/superweapon_validator.py:146-188` — validate_close_warp_point()
- `game/strategy/engine/superweapon_command_handlers.py:114-136` — CloseWarpPointCommandHandler
- `game/strategy/engine/superweapon_command_handlers.py:330-358` — CloseWarpPointMissionCommandHandler
- `game/strategy/engine/superweapon_order_processor.py:55-121` — _finalize_superweapon()
- `game/strategy/engine/superweapon_order_processor.py:356-419` — process_close_warp_point()
- `game/strategy/data/galaxy.py:408-441` — remove_warp_link()

### Similar Patterns Found
**COLONIZE** (working correctly):
- `ColonizeValidator` has `skip_chain_check` parameter — skips location check during queueing
- Two-phase validation: loose at queue time, strict at execution time
- `ColonizeCommandHandler` auto-adds MOVE order if fleet not at target

**TRANSFER** (working correctly):
- `TransferValidator` has `skip_location_check` parameter
- Same two-phase validation pattern

**CLOSE_WARP_POINT** (broken):
- `SuperweaponValidator.validate_close_warp_point()` has NO skip parameter
- Checks fleet.location at queue time — fails if fleet not at warp point
- Both direct and mission handlers call the same validator with no skip option

### Documentation Discrepancies
None — code matches docs. `docs/systems/orders_system.md` describes CLOSE_WARP_POINT as an action order correctly.

## User Context

**Reproduction Steps:**
1. Select a fleet with a CloseWarpPoint-capable ship
2. Fleet is NOT at the warp point sector
3. Press Ctrl+L, click on the warp point
4. Confirmation dialog appears, click OK
5. Order does NOT appear in orders queue — silently dropped

**Workaround:** Move fleet to warp point sector first, THEN give close order.

**Expected Behavior:** Order should queue with an auto-MOVE, execute when fleet arrives.

**Fleet destroyed issue:** User tested with single-ship fleet. Ship was consumed by `_finalize_superweapon()`, making fleet empty, which triggered fleet removal.

**Design intent (confirmed by user):**
- Only `stellerate_star` and `self_destruct` should consume the ship
- All other superweapons (close_warp, open_warp, implode_planet, create_dyson_sphere) should NOT consume the ship
- Colony ships are consumed separately (not via superweapon system)

## Hypothesis Log

### Hypothesis 1: Validator checks location at queue time — CONFIRMED
**Theory:** `SuperweaponValidator.validate_close_warp_point()` checks `fleet.location` during command handling, before the fleet has moved. Unlike COLONIZE/TRANSFER validators, it has no `skip_location_check` parameter.
**Evidence For:** Code at superweapon_validator.py:171-186 explicitly checks `fleet.location`. COLONIZE/TRANSFER validators have skip flags; this one doesn't. User confirmed order works when fleet is already at warp point.
**Evidence Against:** None.
**Test:** Compare validator call patterns between COLONIZE and CLOSE_WARP_POINT command handlers.
**Result:** CONFIRMED — root cause of Issue 1.

### Hypothesis 2: _finalize_superweapon() unconditionally consumes ship — CONFIRMED
**Theory:** All superweapons call `_finalize_superweapon()` which always calls `fleet.remove_ship(ship)`, consuming the superweapon ship.
**Evidence For:** Code at superweapon_order_processor.py:92-93 unconditionally removes ship. User confirmed single-ship fleet disappeared.
**Evidence Against:** None.
**Result:** CONFIRMED — root cause of Issue 3. User confirmed only stellerate_star and self_destruct should consume.

## Fix (2026-03-14)

### Root Cause Summary
Three issues, two root causes:

1. **`SuperweaponValidator.validate_close_warp_point()` checked fleet location at queue time** — Unlike COLONIZE/TRANSFER validators which have `skip_location_check` parameters, this validator always required the fleet to be at the warp point before the order could be queued. The confirmation dialog appeared (UI-level check passed), but the command handler's validation rejected the order silently.

2. **`_finalize_superweapon()` unconditionally consumed the ship** — All superweapons shared a common finalization path that always removed the executing ship from the fleet. Per user: only `stellerate_star` and `self_destruct` should consume the ship.

### Changes

**`game/strategy/validation/superweapon_validator.py`:**
- Added `skip_location_check: bool = False` parameter to `validate_close_warp_point()` and `validate_open_warp_point()`
- When `True`, location and warp-point-existence checks are skipped (ability check still enforced)
- Matches the pattern used by COLONIZE (`skip_chain_check`) and TRANSFER (`skip_location_check`)

**`game/strategy/engine/superweapon_command_handlers.py`:**
- `CloseWarpPointMissionCommandHandler` now passes `skip_location_check=True` to validator
- `OpenWarpPointMissionCommandHandler` now passes `skip_location_check=True` to validator
- Direct command handlers (non-mission) unchanged — they require fleet to already be at target

**`game/strategy/engine/superweapon_order_processor.py`:**
- Added `consume_ship: bool = True` parameter to `_finalize_superweapon()`
- Ship is only removed when `consume_ship=True`
- All four non-consuming callers now pass `consume_ship=False`: `process_implode_planet()`, `process_open_warp_point()`, `process_close_warp_point()`, `process_create_dyson_sphere()`
- `process_stellerate_star()` and `process_self_destruct()` have custom finalization (unchanged, still consume)
- Updated module and method docstrings

### Tests
- Updated 4 unit tests: `test_ship_consumed` → `test_ship_not_consumed` for implode, open_warp, close_warp, dyson_sphere
- Updated `TestComponentConsumption` to verify ship preservation
- Updated 3 integration tests: ship assertions changed from `not in` to `in`
- Added 2 new validator tests: `test_skip_location_check_allows_remote_queueing`, `test_skip_location_check_still_checks_ability`
- Full suite: **13,177 passed**, 2 skipped, 0 failures

### Issue 2 Fix: Sector-level validation at execution time

**Problem:** The CLOSE_WARP_POINT order stored only `destination_id` (e.g., "Beta"). At execution time, the processor derived the source system from the fleet's current location. If move orders got rearranged and the fleet ended up at a different sector (even within the same system — a system can have multiple warp points in different sectors), the wrong warp point could be closed.

**Fix:** Changed the order target from a plain string to a dict: `{'destination_id': ..., 'target_hex': {'q': ..., 'r': ...}}`. The target sector (hex coordinate of the warp point) is captured at order creation time. At execution time, `process_close_warp_point()` validates that `fleet.location == expected_hex` before proceeding. If they don't match, the order is canceled with a clear error message. This ensures sector-level precision — the fleet must be at the exact warp point hex, not just in the same system.

**Files changed:**
- `game/strategy/engine/superweapon_command_handlers.py` — both handlers now store dict target with `target_hex`
- `game/strategy/engine/superweapon_order_processor.py` — added sector-level validation at execution time
- `game/strategy/data/order_types.py` — CLOSE_WARP_POINT serialization updated to use `warp_params` format (like OPEN_WARP_POINT)

**Tests:** Added `test_rejects_wrong_sector` — verifies order is canceled and warp link preserved when fleet is at wrong hex. Full suite: **13,178 passed**, 2 skipped.
