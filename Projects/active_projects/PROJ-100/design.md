# PROJ-100: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Transfer Flow
1. Player selects a fleet
2. Presses T key
3. `StrategyInputHandler._handle_keydown_mapped()` (line 142-148) immediately calls `scene.ui.open_transfer_dialog(fleet, fleet.location)`
4. `TransferDialog` opens at fleet's current hex, shows dropdowns for source/target/item/amount
5. Dialog issues `IssueTransferCommand` → queued as `FleetOrder(OrderType.TRANSFER)` → executed at end of turn

### Input Mode State Machine
The strategy screen uses an `input_mode` string to track what the next click does:
- `'SELECT'` — default, clicking selects objects
- `'MOVE'` — clicking issues move order (M key)
- `'JOIN'` — clicking selects fleet to join (J key)
- `'COLONIZE_TARGET'` — clicking selects planet to colonize (C key)

**Pattern for each mode:**
1. Key press sets `self.input_mode = 'MODE_NAME'`
2. ESC or right-click cancels back to `'SELECT'`
3. Left-click resolves hex from mouse coordinates, performs action
4. Action resets mode to `'SELECT'`

The T key currently bypasses this pattern — it opens the dialog immediately without entering a mode.

### Transfer Dialog Architecture
- `TransferDialog(UIWindow)` in `game/ui/screens/transfer_dialog.py` (332 lines)
- Constructor: `(relative_rect, manager, source_fleet, hex_coord, scene, input_mapper)`
- Populates from `facade.get_fleets_at_hex()` and `facade.get_planets_at_hex()`
- Source/Target dropdowns built from fleets + colonized planets at hex
- Cargo items: fleet passengers or colony population by species
- Issues `IssueTransferCommand(fleet_id, planet_id, cargo_type, direction, amount, species_id)`
- Current window size: 600x500 (clips some elements)

### Backend (No Changes Needed)
- `IssueTransferCommand` → `TransferCommandHandler.execute()` → validates + creates `FleetOrder(OrderType.TRANSFER, target=params_dict)`
- `FleetOrderProcessor.process_transfer()` → executes at end of turn
- `TransferValidator.validate()` → checks fleet/planet co-location, cargo type, capacity
- Only "passengers" cargo type supported currently

## Swarm Findings Summary

### Architecture
- Input handler (`strategy_input_handler.py`) manages mode state machine and dispatches clicks
- Window manager (`strategy_window_manager.py`) handles window lifecycle (open/close/track)
- Strategy UI (`strategy_ui.py`) delegates window operations to window manager
- Transfer dialog is self-contained — creates its own UI, handles events, dispatches commands

### Key Patterns to Reuse
- **Input mode pattern**: `strategy_input_handler.py:121-140` — M/J/C key handlers set mode, click handlers dispatch
- **Click-to-hex resolution**: `pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)` — used in all click handlers
- **Window manager open method**: `strategy_window_manager.py:284-310` — `open_transfer_dialog()` pattern
- **UIWindow subclass pattern**: `transfer_dialog.py` — `_setup_ui()`, `_populate_initial_data()`, `process_event()`
- **IssueTransferCommand reuse**: `commands.py:112-149` — fleet_id, planet_id, cargo_type, direction, amount, species_id

### Dependencies & Risks
1. **D key binding conflict**: D is bound to `strategy.open_design`. Resolved by standardizing keybindings (screen openers → Shift+Key).
2. **Legacy key handler**: `_handle_keydown_legacy()` has hardcoded T key (line 226-232). Must update alongside mapped handler.
3. **Hex resolution when clicking different hex than fleet's location**: The `TransferDialog._populate_initial_data()` uses `facade.get_fleets_at_hex(self.hex_coord)` — it will show whatever is at the *clicked* hex, which is the desired behavior.
4. **No fleet-to-fleet transfer support**: `IssueTransferCommand` requires `planet_id`. CargoQuickDialog must handle the case where no colony exists at clicked hex.

### Opportunities Discovered
- The keybinding standardization (Shift+Key for menus, plain key for fleet commands) makes the system more intuitive and frees up plain D/L keys for fleet commands.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
