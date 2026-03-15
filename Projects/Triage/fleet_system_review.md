# Fleet System Review and Extensibility Overhaul

## Context
During QA session 20260314_221347, the user attempted to use "Join Fleet" in a sector with multiple fleets. The system silently picked the first fleet with no selection dialog. This revealed that the fleet interaction system has grown organically without a consistent UX pattern for multi-fleet scenarios.

## Screenshots
None captured during this session.

## Code Investigation Findings

### Join Fleet — No Fleet Selection Dialog
- `game/ui/screens/strategy_fleet_ops.py` — `handle_join_designation()` calls `get_fleets_at_hex()` but returns only `fleets[0]`, silently ignoring other fleets at the same hex.
- `game/ui/screens/strategy_click_dispatcher.py` — routes JOIN mode clicks with no choice dialog.
- The MOVE mode already has a `prompt_move_choice()` pattern (line 351 of `strategy_window_manager.py`) for multi-fleet sectors, but JOIN mode doesn't use anything similar.

### Fleet Operations Spread Across Many Files
- **Commands & Handlers:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py` (JoinCommandHandler, SplitFleetCommandHandler)
- **Order Processing:** `game/strategy/engine/fleet_order_processor.py` — `process_join_fleet()` merges fleets when co-located
- **UI — Fleet Ops:** `game/ui/screens/strategy_fleet_ops.py`, `game/ui/screens/strategy_click_dispatcher.py`
- **UI — Fleet Report:** `game/ui/screens/fleet_report_window.py`, `game/ui/screens/fleet_report_sidebar.py`
- **UI — Ship Detail:** `game/ui/panels/ship_detail_panel.py`
- **Data:** `game/strategy/data/fleet.py`, `game/strategy/data/order_types.py`

### Inconsistencies Found
- MOVE mode has a choice dialog for multi-fleet targets; JOIN mode does not.
- Split/remove command results are silently ignored by the UI callback (`strategy_window_manager.py` line 359) — no error feedback to the user.
- Fleet operations don't follow a single consistent pattern for user interaction.

## Scope Notes
This warrants a full project rather than a bug fix or feature because:
1. **System-wide review needed:** Fleet operations span 10+ files across UI, command, and data layers. A piecemeal fix to Join Fleet would leave the same gaps in other operations.
2. **Consistency:** All fleet operations (join, split, transfer, move) should follow the same interaction patterns — selection dialogs, error feedback, confirmation flows.
3. **Extensibility:** Future fleet operations (e.g., transfer ships between fleets, fleet formations, fleet renaming) should be easy to add without duplicating boilerplate.
4. **Error handling:** Command results are currently ignored by UI callbacks, so validation failures are silent. This needs a consistent pattern across all fleet commands.
