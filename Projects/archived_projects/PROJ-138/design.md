# PROJ-138: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Existing Call Chain (Already Wired)
The entire Open Warp Point flow is already implemented except for the UI dialog:

1. **User clicks hex** → `strategy_superweapons.py:handle_open_warp_designation()` (line 161)
2. **Filters systems** → Excludes current system and already-linked systems (lines 190-199)
3. **Creates callback** → `on_system_selected(system_name: str)` which queues the command (lines 205-214)
4. **Calls picker** → `_show_system_picker(systems, current_system, on_selected)` (line 214)
5. **Discovery check** → `hasattr(self.scene.ui, 'show_system_picker')` (line 388)
6. **Fallback** → Auto-selects first system if no dialog available (lines 392-394)

### Warp Point Placement (Already Correct)
In `superweapon_order_processor.py:261-275`:
- **Near-end:** Fleet's local position within current system
- **Far-end:** `orbit_distance=6` hexes from target system center, direction pointing back to source system
- Uses direction vector normalized and scaled to orbit_distance

### Reference Dialog: PlanetSelectionWindow
`planet_selection_window.py` provides the pattern:
- UIWindow subclass with UISelectionList for scrollable item list
- `get_single_selection()` in `update()` to detect selection changes
- `check_pressed()` on buttons for confirm/cancel
- Callback invoked with selection, then `self.kill()`
- Override `kill()` to clean up child elements

## Swarm Findings Summary

### Architecture
- **Facade/delegate pattern**: StrategyUI delegates all window management to StrategyWindowManager
- **Discovery pattern**: `strategy_superweapons.py` uses `hasattr()` to discover UI methods, with fallbacks for testing without full UI
- **No stored reference needed**: Simple prompt dialogs (like `prompt_planet_selection`) don't need a stored reference — they are fire-and-forget with a callback

### Key Patterns to Reuse
- **PlanetSelectionWindow**: `game/ui/screens/planet_selection_window.py` - Full UIWindow + UISelectionList pattern
- **prompt_planet_selection**: `game/ui/screens/strategy_window_manager.py:381-396` - Centered window creation, no stored reference
- **StrategyUI delegates**: `game/ui/screens/strategy_ui.py:339-389` - One-liner forwarding methods
- **hex_distance**: `game/core/hex_math.py:115` - Grid distance between HexCoord pairs

### Dependencies & Risks
1. **Low risk** - This is purely additive. No existing code is modified except adding new methods to two files.
2. **No breaking changes** - `strategy_superweapons.py` uses `hasattr` discovery; existing tests mock `show_system_picker` independently.
3. **Minimal surface area** - Only 2 files modified (strategy_window_manager.py, strategy_ui.py), 2 files created.

### Opportunities Discovered
- The dialog could later be enhanced with system details (star type, number of planets, etc.) — but that's out of scope for this project.

## Design Decisions

### SystemSelectionWindow Specification
- **Size:** 450w x 500h, centered on screen
- **Layout:** Header label → UISelectionList (scrollable) → Confirm + Cancel buttons at bottom
- **List format:** `"SystemName (dist: N)"` using `hex_distance(current_system.global_location, system.global_location)`
- **Sorting:** Alphabetical by system name
- **Confirm:** Extracts system name from display string, calls `callback(system.name)`, kills window
- **Cancel / X-close:** Kills window, does NOT call callback (order is silently aborted)
- **Name extraction:** Store `{display_string: system.name}` mapping dict to recover actual name from display string

### Why No Stored Window Reference
Following `prompt_planet_selection` pattern — the dialog is a one-shot prompt. The callback handles the result, and the window self-destructs. No need to track it in StrategyWindowManager.

### Why callback(system.name) Returns String
The existing `_show_system_picker` callback signature at `strategy_superweapons.py:205` expects `system_name: str`. The command `QueueOpenWarpPointMissionCommand` takes `(fleet_id, target_hex, system_name)`. Returning the string name keeps the interface simple and matches the existing contract.

See [decisions.md](decisions.md) for the full log with rationale.
