"""Strategy screen selection + colonization helper (PROJ-330).

Extracted from ``strategy_screen.py`` as part of the LOC decomposition.
Owns:

- ``on_ui_selection``: routes a UI-list selection through type guards,
  updates ``selected_object`` / ``selected_fleet`` / ``last_selected_system``,
  and refreshes the detail panel.
- ``on_colonize_click`` / ``_on_colonize_planet_selected`` /
  ``request_colonize_order``: the player-driven colonization flow.

Each helper takes the screen as a parameter; no new MVVM seam.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.protocols import is_fleet, is_planet, is_star_system, is_warp_point

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen


def on_ui_selection(screen: "StrategyScreen", obj) -> None:
    """Called when user selects an item in the UI list."""
    screen.selected_object = obj

    # Track last selected system - PROJ-40: protocol type guard
    if is_star_system(obj):
        screen.last_selected_system = obj
    elif is_planet(obj) or is_warp_point(obj):
        # Planets and warp points have location - find their containing system
        parent_sys = next(
            (s for s in screen.systems if obj in s.planets or obj in s.warp_points),
            None,
        )
        if parent_sys:
            screen.last_selected_system = parent_sys

    # Update fleet selection - PROJ-40: protocol type guard
    current_player_id = screen.facade.session_meta.human_player_ids()[screen.current_player_index]
    if is_fleet(obj) and obj.owner_id == current_player_id:
        screen.selected_fleet = obj
    elif not is_fleet(obj):
        screen.selected_fleet = None

    # Update UI
    img = screen._get_object_asset(obj)
    screen.ui.show_detailed_report(obj, img)

    # If TransferDialog is open, update its selection
    if screen.ui.window_manager.transfer_dialog:
        screen.ui.window_manager.transfer_dialog.handle_external_selection(obj)


def on_colonize_click(screen: "StrategyScreen") -> None:
    """Handle colonize action — always opens load transfer dialog first.

    Flow:
      1. Open transfer dialog to load cargo/population.
      2. Input mode enters COLONIZE_TARGET (handled by fleet_command_router).
      3. Player clicks destination → drop dialog → colonize + TRANSFER queued.
    """
    fleet = screen.selected_fleet
    if not fleet:
        return

    screen.ui.open_transfer_dialog(fleet, fleet.location)
    # Input mode is set to COLONIZE_TARGET by the fleet_command_router
    # regardless of whether the load dialog was opened.


def on_colonize_planet_selected(screen: "StrategyScreen", planet) -> None:
    """Handle planet selection — issue colonize command, then open drop dialog."""
    fleet = screen.selected_fleet
    result = screen._colonization.issue_colonize_order(fleet, planet)
    if result and result.get("type") == "success":
        # Find planet's global hex for the drop transfer dialog
        planet_global_hex = None
        for sys in screen.systems:
            if planet in sys.planets:
                planet_global_hex = sys.global_location + planet.location
                break
        if planet_global_hex:
            screen.ui.open_transfer_dialog(fleet, planet_global_hex)
        screen.on_ui_selection(fleet)


def request_colonize_order(screen: "StrategyScreen", fleet, planet=None) -> None:
    """Handle colonize request from UI."""
    # BUG-125: gate against active empire — never select an opponent's
    # fleet for command issuance. PROJ-475: id-compare via the scene's
    # active_empire_id accessor (off the direct .session read).
    active_id = screen.active_empire_id
    if active_id is not None and fleet.owner_id != active_id:
        return
    screen.selected_fleet = fleet
    result = screen._colonization.request_colonize_order(fleet, planet)
    if result and result.get("type") == "success":
        screen.on_ui_selection(fleet)
