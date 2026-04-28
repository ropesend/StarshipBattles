"""
System Selection Window - Star system selection dialog for warp point targeting.

Used for selecting a target star system when issuing Open Warp Point orders.
Displays systems alphabetically with hex distances from the current system.
"""
from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UISelectionList, UIButton, UILabel

from game.core.hex_math import hex_distance
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class SystemSelectionWindow(StrategyModalWindow):
    """
    Dialog window for selecting a target star system.

    Displays an alphabetically sorted, scrollable list of star systems
    with their hex distances from the current system. Used by the Open Warp Point
    superweapon order flow.

    PROJ-313: migrated to StrategyModalWindow base class.
    """

    def __init__(
        self,
        rect,
        manager,
        systems,
        current_system,
        on_selection_callback,
        *,
        window_manager: "StrategyWindowManager",
    ):
        """
        Initialize system selection window.

        Args:
            rect: Window position and size rectangle.
            manager: pygame_gui UIManager instance.
            systems: List of StarSystem objects to select from (already filtered by caller).
            current_system: Current StarSystem (for distance calculation).
            on_selection_callback: Called with selected system name (str) on confirm.
            window_manager: PROJ-313 StrategyWindowManager for modal registration.
        """
        super().__init__(
            rect, manager, window_display_title="Select Target System",
            window_manager=window_manager,
        )
        self.systems = systems
        self.current_system = current_system
        self.callback = on_selection_callback

        # Build display_name -> system_name mapping for extraction
        self.display_to_name = {}
        item_list = []

        for system in systems:
            dist = hex_distance(current_system.global_location, system.global_location)
            display_str = f"{system.name} (dist: {dist})"
            self.display_to_name[display_str] = system.name
            item_list.append((system.name, display_str))

        # Sort alphabetically by system name
        item_list.sort(key=lambda x: x[0])

        # Extract just the display strings for the UI
        sorted_display_list = [item[1] for item in item_list]

        # Header label
        self.label = UILabel(
            pygame.Rect(10, 10, rect.width - 20, 30),
            "Select Target System:",
            self.ui_manager,
            container=self
        )

        # Scrollable selection list
        list_height = rect.height - 120  # Room for header, buttons, margins
        self.selection_list = UISelectionList(
            pygame.Rect(10, 45, rect.width - 20, list_height),
            item_list=sorted_display_list,
            manager=self.ui_manager,
            container=self
        )

        # Confirm button (bottom-left)
        self.btn_confirm = UIButton(
            pygame.Rect(10, rect.height - 60, 120, 35),
            "Confirm",
            self.ui_manager,
            container=self
        )

        # Cancel button (bottom-right)
        self.btn_cancel = UIButton(
            pygame.Rect(rect.width - 130, rect.height - 60, 120, 35),
            "Cancel",
            self.ui_manager,
            container=self
        )

    def update(self, time_delta: float) -> None:
        """Process button presses and handle selection confirmation."""
        super().update(time_delta)

        if self.btn_confirm.check_pressed():
            selected_display = self.selection_list.get_single_selection()
            if selected_display:
                # Extract actual system name from display string
                system_name = self.display_to_name.get(selected_display)
                if system_name:
                    self.callback(system_name)
                    self.kill()
            # No selection = do nothing (don't close window)

        if self.btn_cancel.check_pressed():
            # Cancel without calling callback
            self.kill()
