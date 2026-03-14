# BUG-84: Warp Gate Close and Planet Destroyer orders not registering

## Description

When I order a ship with a warp gate close on it to close a warp point, nothing happens, no orders show up, no action is taken, I'm not even sure if it registers the key presses. Same thing for the planet destroyer.

## Priority
High

## Status (Blocked)

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
