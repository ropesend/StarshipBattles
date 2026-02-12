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
