"""
System Selection Window - Star system selection dialog for warp point targeting.

Used for selecting a target star system when issuing Open Warp Point orders.
Displays systems alphabetically with hex distances from the current system.

PROJ-329B Phase 1: Migrated to two-stage construction. Cheap state
(systems, current_system, callback, display mapping, sorted display list)
lives before ``super().__init__``; widget construction is behind
``SystemSelectionUiBuilder`` so tests can swap in a Mock under
``bypass_init``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
from pygame_gui.elements import UISelectionList, UIButton, UILabel

from game.core.hex_math import hex_distance
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class SystemSelectionUiBuilder:
    """Production widget builder. Constructs label, selection list,
    Confirm button, Cancel button.

    Reads ``screen._sorted_display_list`` (built in Stage 1) and writes
    ``screen.label``, ``screen.selection_list``, ``screen.btn_confirm``,
    ``screen.btn_cancel``.
    """

    def build(self, screen: "SystemSelectionWindow") -> None:
        rect = screen.rect

        screen.label = UILabel(
            pygame.Rect(10, 10, rect.width - 20, 30),
            "Select Target System:",
            screen.ui_manager,
            container=screen,
        )

        list_height = rect.height - 120
        screen.selection_list = UISelectionList(
            pygame.Rect(10, 45, rect.width - 20, list_height),
            item_list=screen._sorted_display_list,
            manager=screen.ui_manager,
            container=screen,
        )

        screen.btn_confirm = UIButton(
            pygame.Rect(10, rect.height - 60, 120, 35),
            "Confirm",
            screen.ui_manager,
            container=screen,
        )

        screen.btn_cancel = UIButton(
            pygame.Rect(rect.width - 130, rect.height - 60, 120, 35),
            "Cancel",
            screen.ui_manager,
            container=screen,
        )


class SystemSelectionWindow(StrategyModalWindow):
    """
    Dialog window for selecting a target star system.

    Displays an alphabetically sorted, scrollable list of star systems
    with their hex distances from the current system. Used by the Open Warp Point
    superweapon order flow.

    PROJ-313: migrated to StrategyModalWindow base class.
    PROJ-329B Phase 1: two-stage construction with ``ui_builder`` test seam.
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
        ui_builder: Optional[SystemSelectionUiBuilder] = None,
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
            ui_builder: Optional UI builder override (test seam).
        """
        # ---- Stage 1: cheap state ----
        self.systems = systems
        self.current_system = current_system
        self.callback = on_selection_callback

        # PROJ-347 T4.2 (Pattern §33 widget-ref placeholders): set widget
        # slots populated by the production builder to None up front, so a
        # NullSystemSelectionWindowUiBuilder test can safely call
        # ``update()`` without AttributeError on
        # ``self.btn_confirm.check_pressed()``. The production builder
        # overwrites these in Stage 3.
        self.label = None
        self.selection_list = None
        self.btn_confirm = None
        self.btn_cancel = None

        # Build display_name -> system_name mapping for extraction.
        self.display_to_name: dict[str, str] = {}
        item_list: list[tuple[str, str]] = []

        for system in systems:
            dist = hex_distance(current_system.global_location, system.global_location)
            display_str = f"{system.name} (dist: {dist})"
            self.display_to_name[display_str] = system.name
            item_list.append((system.name, display_str))

        # Sort alphabetically by system name.
        item_list.sort(key=lambda x: x[0])

        # Extract just the display strings for the UI.
        self._sorted_display_list = [item[1] for item in item_list]

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager, window_display_title="Select Target System",
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or SystemSelectionUiBuilder()).build(self)

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
