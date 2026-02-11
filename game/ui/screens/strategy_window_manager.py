"""Window lifecycle management for StrategyUI.

PROJ-86: Extracted from strategy_ui.py to reduce god class size.
Handles opening, closing, and tracking of all modal windows in the strategy layer.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import pygame
import pygame_gui
import pygame_gui.elements as ui

from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.planet_list_window import PlanetListWindow
from game.ui.screens.fleet_orders_window import FleetOrdersWindow
from game.ui.screens.fleet_report_window import FleetReportWindow
from game.ui.screens.build_queue_list_window import BuildQueueListWindow
from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow
from game.ui.screens.event_log_window import EventLogWindow
from game.ui.screens.empire_panel_window import EmpirePanelWindow

if TYPE_CHECKING:
    from game.core.input_mapper import InputMapper


class StrategyWindowManager:
    """Manages modal window lifecycle for the strategy screen.

    Handles opening, closing, and tracking of:
    - Planet list window
    - Build queue list window
    - Empire build queue window
    - Event log window
    - Fleet orders window
    - Fleet report window
    - Transfer dialog
    - Planet selection prompts
    - Move choice prompts

    Attributes:
        planet_list_window: Active planet list window or None.
        build_queue_list_window: Active build queue list window or None.
        empire_build_queue_window: Active empire build queue window or None.
        event_log_window: Active event log window or None.
        fleet_orders_window: Active fleet orders window or None.
        fleet_report_window: Active fleet report window or None.
        transfer_dialog: Active transfer dialog or None.
        ui_callbacks: Dict mapping buttons to callbacks for prompt dialogs.
    """

    def __init__(
        self,
        scene,
        manager: pygame_gui.UIManager,
        width: int,
        height: int,
        input_mapper: Optional["InputMapper"] = None,
        asset_resolver: Optional[Callable] = None,
    ):
        """Initialize the window manager.

        Args:
            scene: Reference to StrategyScreen for current_empire, galaxy, _facade access.
            manager: The pygame_gui UIManager.
            width: Screen width.
            height: Screen height.
            input_mapper: Optional InputMapper for hotkey tooltips.
            asset_resolver: Optional callable for resolving object portraits.
        """
        self.scene = scene
        self.manager = manager
        self.width = width
        self.height = height
        self._mapper = input_mapper
        self._asset_resolver = asset_resolver

        # Window references
        self.planet_list_window = None
        self.build_queue_list_window = None
        self.empire_build_queue_window = None
        self.event_log_window = None
        self.fleet_orders_window = None
        self.fleet_report_window = None
        self.transfer_dialog = None
        self.empire_panel_window = None

        # Callback map for dynamic prompt buttons
        self.ui_callbacks: dict = {}

    def handle_resize(self, width: int, height: int) -> None:
        """Update stored dimensions on resize.

        Args:
            width: New screen width.
            height: New screen height.
        """
        self.width = width
        self.height = height

    # =========================================================================
    # Planet List Window
    # =========================================================================

    def open_planet_list(self) -> None:
        """Open the Planet List Window."""
        w, h = self.width * 0.9, self.height * 0.9
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        empire = self.scene.current_empire
        galaxy = self.scene.galaxy

        self.planet_list_window = PlanetListWindow(
            rect,
            self.manager,
            galaxy,
            empire,
            on_close_callback=self._on_planet_list_closed,
            asset_resolver=self._asset_resolver,
        )

    def _on_planet_list_closed(self) -> None:
        """Callback when planet list window is closed."""
        self.planet_list_window = None

    # =========================================================================
    # Build Queue List Window
    # =========================================================================

    def open_build_queue_list(self) -> None:
        """Open the Build Queue List Window (BUG-67)."""
        if self.build_queue_list_window:
            self.build_queue_list_window.kill()

        empire = self.scene.current_empire

        w, h = 700, 500
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.build_queue_list_window = BuildQueueListWindow(
            rect,
            self.manager,
            empire,
            on_close_callback=self._on_build_queue_list_closed,
            input_mapper=self._mapper,
        )

    def _on_build_queue_list_closed(self) -> None:
        """Callback when build queue list window is closed."""
        self.build_queue_list_window = None

    # =========================================================================
    # Empire Build Queue Window
    # =========================================================================

    def open_empire_build_queue_window(self) -> None:
        """Open the Empire-Wide Build Queue Window (PROJ-76)."""
        if self.empire_build_queue_window:
            self.empire_build_queue_window.kill()

        empire = self.scene.current_empire
        galaxy = self.scene.galaxy

        w, h = int(self.width * 0.9), int(self.height * 0.9)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.empire_build_queue_window = EmpireBuildQueueWindow(
            rect,
            self.manager,
            empire,
            galaxy,
            on_close_callback=self._on_empire_build_queue_closed,
            on_navigate_to_hex=self.scene.on_navigate_to_hex_build,
        )

    def _on_empire_build_queue_closed(self) -> None:
        """Callback when empire build queue window is closed."""
        self.empire_build_queue_window = None

    # =========================================================================
    # Event Log Window
    # =========================================================================

    def open_event_log(self) -> None:
        """Open the Event Log Window showing all events (PROJ-77).

        Fetches all events from the facade and displays them in
        a modal window with filter tabs.
        """
        if self.event_log_window:
            self.event_log_window.kill()

        events = (
            self.scene._facade.get_all_events()
            if hasattr(self.scene, "_facade")
            else []
        )

        w, h = int(self.width * 0.7), int(self.height * 0.7)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.event_log_window = EventLogWindow(
            rect,
            self.manager,
            events,
            on_close_callback=self._on_event_log_closed,
        )

    def open_event_log_with_events(self, events: list) -> None:
        """Open the Event Log Window with a specific event list.

        Used at turn start to show only the current turn's events.

        Args:
            events: List of event dicts to display.
        """
        if self.event_log_window:
            self.event_log_window.kill()

        w, h = int(self.width * 0.7), int(self.height * 0.7)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.event_log_window = EventLogWindow(
            rect,
            self.manager,
            events,
            on_close_callback=self._on_event_log_closed,
        )

    def _on_event_log_closed(self) -> None:
        """Callback when event log window is closed."""
        self.event_log_window = None

    # =========================================================================
    # Empire Panel Window
    # =========================================================================

    def open_empire_panel(self) -> None:
        """Open the Empire Panel Window."""
        if self.empire_panel_window:
            self.empire_panel_window.kill()

        empire = self.scene.current_empire

        w, h = int(self.width * 0.9), int(self.height * 0.9)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.empire_panel_window = EmpirePanelWindow(
            rect,
            self.manager,
            empire,
            on_close_callback=self._on_empire_panel_closed,
        )

    def _on_empire_panel_closed(self) -> None:
        """Callback when empire panel window is closed."""
        self.empire_panel_window = None

    # =========================================================================
    # Fleet Orders Window
    # =========================================================================

    def open_orders_window(self, fleet) -> None:
        """Open the Fleet Orders Window.

        Args:
            fleet: The fleet to show orders for.
        """
        if self.fleet_orders_window:
            self.fleet_orders_window.kill()

        w, h = 400, 500
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.fleet_orders_window = FleetOrdersWindow(
            rect, self.manager, fleet, input_mapper=self._mapper
        )

    # =========================================================================
    # Fleet Report Window
    # =========================================================================

    def open_fleet_report_window(self, fleet) -> None:
        """Open the Fleet Report Window.

        Args:
            fleet: The fleet to show the report for.
        """
        if self.fleet_report_window:
            self.fleet_report_window.kill()

        # Match PlanetListWindow size (90% of screen)
        w, h = self.width * 0.9, self.height * 0.9
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.fleet_report_window = FleetReportWindow(
            rect,
            self.manager,
            fleet,
            on_close_callback=self._on_fleet_report_closed,
        )

    def _on_fleet_report_closed(self) -> None:
        """Callback when fleet report window is closed."""
        self.fleet_report_window = None

    # =========================================================================
    # Transfer Dialog
    # =========================================================================

    def open_transfer_dialog(self, source_fleet, hex_coord) -> None:
        """Open the cargo/population transfer dialog.

        PROJ-68: Hex-aware selection between multiple ships and colonies.

        Args:
            source_fleet: The fleet initiating the transfer.
            hex_coord: The hex coordinate for the transfer context.
        """
        if self.transfer_dialog is not None:
            self.transfer_dialog.kill()
            self.transfer_dialog = None

        from game.ui.screens.transfer_dialog import TransferDialog

        win_w, win_h = 600, 500
        win_rect = pygame.Rect(0, 0, win_w, win_h)
        win_rect.center = (self.width // 2, self.height // 2)

        self.transfer_dialog = TransferDialog(
            relative_rect=win_rect,
            manager=self.manager,
            source_fleet=source_fleet,
            hex_coord=hex_coord,
            scene=self.scene,
            input_mapper=self._mapper,
        )

    # =========================================================================
    # Planet Selection Prompt
    # =========================================================================

    def prompt_planet_selection(self, planets, on_select: Callable) -> None:
        """Open a modal window to select a planet.

        Args:
            planets: List of planets to choose from.
            on_select: Callback called with the selected planet.
        """
        # Large window to fit full planet report (matches strategy UI detail panel)
        width = 950
        height = 650
        x = (self.width - width) / 2
        y = (self.height - height) / 2

        rect = pygame.Rect(x, y, width, height)
        # Use PlanetSelectionWindow (PROJ-54 - now uses PlanetReportPanel internally)
        PlanetSelectionWindow(rect, self.manager, planets, on_select)

    # =========================================================================
    # Move Choice Prompt
    # =========================================================================

    def prompt_move_choice(
        self,
        fleet,
        target_hex,
        on_move_sector: Callable,
        on_intercept_fleet: Callable,
    ) -> None:
        """Dialog to choose between moving to the sector or intercepting the fleet.

        Args:
            fleet: The fleet being ordered.
            target_hex: The target hex coordinate.
            on_move_sector: Callback for static sector move.
            on_intercept_fleet: Callback for dynamic fleet intercept.
        """
        width = 300
        height = 150
        x = (self.width - width) / 2
        y = (self.height - height) / 2
        rect = pygame.Rect(x, y, width, height)

        win = pygame_gui.elements.UIWindow(
            rect=rect, manager=self.manager, window_display_title="Select Move Type"
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 280, 30),
            text="Fleet detected at target.",
            manager=self.manager,
            container=win,
        )

        btn_sector = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 50, 280, 30),
            text="Move to Sector (Static)",
            manager=self.manager,
            container=win,
        )

        btn_intercept = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 90, 280, 30),
            text="Intercept Fleet (Dynamic)",
            manager=self.manager,
            container=win,
        )

        # Store callbacks for button press handling
        self.ui_callbacks[btn_sector] = lambda: (on_move_sector(), win.kill())
        self.ui_callbacks[btn_intercept] = lambda: (on_intercept_fleet(), win.kill())

    def process_ui_callbacks(self, event) -> bool:
        """Process button press events for prompt dialogs.

        Args:
            event: The pygame event.

        Returns:
            True if a callback was executed, False otherwise.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.ui_callbacks:
                self.ui_callbacks[event.ui_element]()
                del self.ui_callbacks[event.ui_element]
                return True
        return False
