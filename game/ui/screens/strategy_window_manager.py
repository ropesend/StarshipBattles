"""Window lifecycle management for StrategyUI.

PROJ-86: Extracted from strategy_ui.py to reduce god class size.
Handles opening, closing, and tracking of all modal windows in the strategy layer.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import pygame
import pygame_gui
import pygame_gui.elements as ui

from game.ui.screens.fleet_selection_window import FleetSelectionWindow
from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.planet_list_window import PlanetListWindow
from game.ui.screens.star_list_window import StarListWindow
from game.ui.screens.system_selection_window import SystemSelectionWindow
# PROJ-238: OrdersWindow imported locally in open_orders_window()
from game.ui.screens.fleet_report_window import FleetReportWindow
from game.ui.screens.build_queue_list_window import BuildQueueListWindow
from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow
from game.ui.screens.event_log_window import EventLogWindow
from game.ui.screens.empire_panel_window import EmpirePanelWindow

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper


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
        self.star_list_window = None
        self.build_queue_list_window = None
        self.empire_build_queue_window = None
        self.event_log_window = None
        self.fleet_orders_window = None
        self.fleet_report_window = None
        self.transfer_dialog = None
        self.empire_panel_window = None
        self.settings_window = None
        self.move_choice_window = None
        self.cargo_quick_dialog = None
        self.planet_selection_window = None
        self.system_selection_window = None
        self.fleet_selection_window = None

        # Callback map for dynamic prompt buttons
        self.ui_callbacks: dict = {}

        # Confirmation dialog state (PROJ-198)
        self._pending_confirmation_dialog = None
        self._pending_confirmation_callback = None

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

        # PROJ-290: thread the session race_registry so the planet detail
        # panel can render uncolonized-planet habitability for the
        # viewing empire's species.
        race_registry = None
        facade = getattr(self.scene, "facade", None)
        if facade is not None and hasattr(facade, "get_race_registry"):
            race_registry = facade.get_race_registry()

        self.planet_list_window = PlanetListWindow(
            rect,
            self.manager,
            galaxy,
            empire,
            on_close_callback=self._on_planet_list_closed,
            asset_resolver=self._asset_resolver,
            empires=self.scene.session.empires,  # PROJ-198: Pass empires for owner name lookup
            registries=self.scene.session.registries,  # PROJ-211: Pass registries for DI
            on_navigate_callback=self._on_planet_navigate,
            race_registry=race_registry,  # PROJ-290
            facade=facade,  # PROJ-292 H1: enables per-species sub-block on colonized planets
        )

    def _on_planet_list_closed(self) -> None:
        """Callback when planet list window is closed."""
        self.planet_list_window = None

    def _on_planet_navigate(self, global_hex) -> None:
        """Navigate camera to planet's system and close planet list."""
        if self.planet_list_window:
            self.planet_list_window.kill()
        self._navigate_camera_to(global_hex)

    # =========================================================================
    # Star List Window (PROJ-231)
    # =========================================================================

    def open_star_list(self) -> None:
        """Open the Star List Window."""
        if self.star_list_window:
            self.star_list_window.kill()

        w, h = self.width * 0.9, self.height * 0.9
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        galaxy = self.scene.galaxy

        self.star_list_window = StarListWindow(
            rect,
            self.manager,
            galaxy,
            on_close_callback=self._on_star_list_closed,
            on_navigate_callback=self._on_star_navigate,
        )

    def _on_star_list_closed(self) -> None:
        """Callback when star list window is closed."""
        self.star_list_window = None

    def _on_star_navigate(self, global_hex) -> None:
        """Navigate camera to star's system and close star list."""
        if self.star_list_window:
            self.star_list_window.kill()
        self._navigate_camera_to(global_hex)

    # =========================================================================
    # Shared Navigation
    # =========================================================================

    def _navigate_camera_to(self, global_hex) -> None:
        """Center the strategy camera on a hex coordinate.

        Shared by planet and star list navigation callbacks.

        Args:
            global_hex: HexCoord to center the camera on.
        """
        if hasattr(self.scene, '_camera_nav'):
            self.scene._camera_nav.center_on_hex(global_hex)

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

        # PROJ-208 Phase 3: Pass facade for CQRS-compliant command dispatch
        self.empire_build_queue_window = EmpireBuildQueueWindow(
            rect,
            self.manager,
            empire,
            galaxy,
            on_close_callback=self._on_empire_build_queue_closed,
            on_navigate_to_hex=self.scene.on_navigate_to_hex_build,
            session=self.scene.session,
            facade=self.scene.facade,
        )

    def close_empire_build_queue_window(self) -> None:
        """Close the empire build queue window if open."""
        if self.empire_build_queue_window:
            self.empire_build_queue_window.kill()
            self.empire_build_queue_window = None

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

        events = self.scene.facade.get_all_events()

        w, h = int(self.width * 0.7), int(self.height * 0.7)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.event_log_window = EventLogWindow(
            rect,
            self.manager,
            events,
            on_close_callback=self._on_event_log_closed,
            on_navigate_callback=self._on_event_log_navigate,
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
            on_navigate_callback=self._on_event_log_navigate,
        )

    def _on_event_log_navigate(self, location_hex: list) -> None:
        """Navigate camera to event location and close event log.

        Args:
            location_hex: [q, r] hex coordinates to navigate to.
        """
        from game.core.hex_math import HexCoord
        hex_coord = HexCoord(location_hex[0], location_hex[1])

        # Close the event log window
        if self.event_log_window:
            self.event_log_window.kill()

        # Navigate camera to the location
        if hasattr(self.scene, '_camera_nav'):
            self.scene._camera_nav.center_on_hex(hex_coord)

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

        # PROJ-290: pass the session-scoped race_registry so the Treasury
        # tab's Population Upkeep row has its habitability-multiplier dep.
        race_registry = None
        facade = getattr(self.scene, "facade", None)
        if facade is not None and hasattr(facade, "get_race_registry"):
            race_registry = facade.get_race_registry()

        self.empire_panel_window = EmpirePanelWindow(
            rect,
            self.manager,
            empire,
            on_close_callback=self._on_empire_panel_closed,
            registries=self.scene.session.registries,  # PROJ-211: Pass registries for DI
            race_registry=race_registry,
        )

    def _on_empire_panel_closed(self) -> None:
        """Callback when empire panel window is closed."""
        self.empire_panel_window = None

    # =========================================================================
    # Settings Window
    # =========================================================================

    def open_settings(self) -> None:
        """Open the Settings Window."""
        if self.settings_window:
            self.settings_window.kill()

        from game.ui.screens.settings_window import SettingsWindow

        w, h = 500, 200
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.settings_window = SettingsWindow(
            rect,
            self.manager,
            on_close_callback=self._on_settings_closed,
        )

    def _on_settings_closed(self) -> None:
        """Callback when settings window is closed."""
        self.settings_window = None

    # =========================================================================
    # Fleet Orders Window
    # =========================================================================

    def open_orders_window(self, entity, entity_type: str = "fleet") -> None:
        """Open the Orders Window for a fleet or planet.

        PROJ-238: Generalized from fleet-only to any IOrderable entity.

        Args:
            entity: The fleet or planet to show orders for.
            entity_type: "fleet" or "planet".
        """
        if self.fleet_orders_window:
            self.fleet_orders_window.kill()

        w, h = 480, 500
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        if entity_type == "planet":
            def clear_orders_callback(entity_id: int) -> None:
                from game.strategy.engine.commands import ClearPlanetOrdersCommand
                cmd = ClearPlanetOrdersCommand(planet_id=entity_id)
                self.scene.facade.handle_command(cmd)

            def delete_order_callback(entity_id: int, order_index: int) -> None:
                from game.strategy.engine.commands import DeletePlanetOrderCommand
                cmd = DeletePlanetOrderCommand(planet_id=entity_id, order_index=order_index)
                self.scene.facade.handle_command(cmd)

            def reorder_order_callback(entity_id: int, order_index: int, direction: int) -> None:
                pass  # Planet order reordering not yet implemented
        else:
            owner_id = entity.owner_id

            def clear_orders_callback(entity_id: int) -> None:
                from game.strategy.engine.commands import ClearOrdersCommand
                cmd = ClearOrdersCommand(fleet_id=entity_id, empire_id=owner_id)
                self.scene.facade.handle_command(cmd)

            def delete_order_callback(entity_id: int, order_index: int) -> None:
                from game.strategy.engine.commands import DeleteOrderCommand
                cmd = DeleteOrderCommand(fleet_id=entity_id, order_index=order_index, empire_id=owner_id)
                self.scene.facade.handle_command(cmd)

            def reorder_order_callback(entity_id: int, order_index: int, direction: int) -> None:
                from game.strategy.engine.commands import ReorderOrderCommand
                cmd = ReorderOrderCommand(fleet_id=entity_id, order_index=order_index, direction=direction, empire_id=owner_id)
                self.scene.facade.handle_command(cmd)

        def edit_order_callback(entity_id: int, order_index: int, order) -> None:
            self.scene.on_edit_order(entity, order_index, order)

        from game.ui.screens.orders_window import OrdersWindow
        self.fleet_orders_window = OrdersWindow(
            rect, self.manager, entity, entity_type=entity_type,
            input_mapper=self._mapper,
            clear_orders_callback=clear_orders_callback,
            delete_order_callback=delete_order_callback,
            reorder_order_callback=reorder_order_callback,
            edit_order_callback=edit_order_callback,
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

        # PROJ-208 Phase 1: Create callback closure for SplitFleetCommand dispatch
        # PROJ-208 Phase 3: Route through facade (not session) for CQRS consistency
        fleet_owner_id = fleet.owner_id

        def split_fleet_callback(fleet_id: int, ship_instance_ids: list):
            """Dispatch SplitFleetCommand through facade command pipeline."""
            from game.strategy.engine.commands import SplitFleetCommand
            cmd = SplitFleetCommand(fleet_id=fleet_id, ship_instance_ids=ship_instance_ids, empire_id=fleet_owner_id)
            return self.scene.facade.handle_command(cmd)

        empire = self.scene.current_empire
        self.fleet_report_window = FleetReportWindow(
            rect,
            self.manager,
            fleet,
            empire=empire,
            on_close_callback=self._on_fleet_report_closed,
            split_fleet_callback=split_fleet_callback,
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

        win_w, win_h = 940, 700
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
    # Cargo Quick Dialog
    # =========================================================================

    def open_cargo_quick_dialog(self, fleet, hex_coord, direction: str) -> None:
        """Open the quick cargo drop/load dialog.

        PROJ-100: Simplified dialog for D/L quick commands.

        Args:
            fleet: The fleet involved in the transfer.
            hex_coord: The hex coordinate for the transfer.
            direction: 'unload' for dropping cargo, 'load' for loading cargo.
        """
        from game.ui.screens.cargo_quick_dialog import CargoQuickDialog

        win_w, win_h = 500, 450
        win_rect = pygame.Rect(0, 0, win_w, win_h)
        win_rect.center = (self.width // 2, self.height // 2)

        self.cargo_quick_dialog = CargoQuickDialog(
            relative_rect=win_rect,
            manager=self.manager,
            fleet=fleet,
            hex_coord=hex_coord,
            direction=direction,
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
        self.planet_selection_window = PlanetSelectionWindow(rect, self.manager, planets, on_select)

    def open_planet_abilities_window(self, planet) -> None:
        """Open the planet abilities management window."""
        from game.ui.screens.planet_abilities_window import PlanetAbilitiesWindow
        from game.core.registry import get_default_registry_provider

        component_registry = None
        try:
            provider = get_default_registry_provider()
            component_registry = provider.get_components()
        except Exception:
            pass

        width = 540
        height = 300
        x = (self.width - width) / 2
        y = (self.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        self.planet_abilities_window = PlanetAbilitiesWindow(
            rect, self.manager, planet, self.scene.facade, component_registry,
            on_open_editor=self._open_planet_editor,
        )

    def _open_planet_editor(self, editor_type: str, planet) -> None:
        """Open a planet environment editor from the abilities window.

        Args:
            editor_type: One of 'atmosphere', 'gravity', 'water', 'radiation'.
            planet: Planet object.
        """
        from game.ui.screens.strategy_event_router import StrategyEventRouter
        # Delegate to the event router which has all editor opening methods
        router = getattr(self.scene, '_event_router', None)
        if router is None:
            # Build a temporary router if not available on scene
            router = StrategyEventRouter(self.scene.ui)
        editor_map = {
            'atmosphere': router._open_atmosphere_editor,
            'gravity': router._open_gravity_editor,
            'water': router._open_water_editor,
            'radiation': router._open_radiation_shield_editor,
            # PROJ-284 Phase 4: per-colony per-species food allocation.
            'food': router._open_food_allocation_editor,
        }
        opener = editor_map.get(editor_type)
        if opener:
            opener(planet)

    # =========================================================================
    # System Selection Prompt (PROJ-138)
    # =========================================================================

    def open_system_selection(self, systems, current_system, on_selected: Callable) -> None:
        """Open a modal window to select a star system.

        Args:
            systems: List of StarSystem objects to choose from.
            current_system: Current StarSystem (for distance display).
            on_selected: Callback called with selected system name string.
        """
        width = 450
        height = 500
        x = (self.width - width) / 2
        y = (self.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        self.system_selection_window = SystemSelectionWindow(rect, self.manager, systems, current_system, on_selected)

    # =========================================================================
    # Fleet Selection Prompt (FEAT-08)
    # =========================================================================

    def prompt_fleet_selection(self, fleets, on_select: Callable) -> None:
        """Open a modal window to select a fleet to join.

        Args:
            fleets: List of FleetInfo DTOs to choose from.
            on_select: Callback called with the selected FleetInfo.
        """
        width = 450
        height = 400
        x = (self.width - width) / 2
        y = (self.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        self.fleet_selection_window = FleetSelectionWindow(rect, self.manager, fleets, on_select)

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
        self.move_choice_window = win

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

    # =========================================================================
    # Confirmation Dialog (PROJ-198)
    # =========================================================================

    def show_confirmation_dialog(
        self, title: str, message: str, on_confirm, is_warning: bool = False
    ) -> None:
        """Show a confirmation dialog for dangerous actions.

        Uses pygame_gui's UIConfirmationDialog. The on_confirm callback is stored
        and called when UI_CONFIRMATION_DIALOG_CONFIRMED event is received.

        Args:
            title: Dialog window title.
            message: Message to display.
            on_confirm: Callback when user confirms.
            is_warning: If True, indicates a dangerous/irreversible action (for styling).
        """
        import pygame_gui.windows

        dialog_rect = pygame.Rect(0, 0, 400, 200)
        dialog_rect.center = (self.width // 2, self.height // 2)

        dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=dialog_rect,
            action_long_desc=message,
            manager=self.manager,
            window_title=title,
        )
        # Store callback keyed by dialog element for event routing
        self._pending_confirmation_callback = on_confirm
        self._pending_confirmation_dialog = dialog

    def process_confirmation_event(self, event) -> bool:
        """Process UI_CONFIRMATION_DIALOG_CONFIRMED events.

        Called by StrategyEventRouter to route confirmation events.

        Args:
            event: The pygame_gui event.

        Returns:
            True if a confirmation callback was executed, False otherwise.
        """
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if (
                self._pending_confirmation_dialog is not None
                and event.ui_element == self._pending_confirmation_dialog
            ):
                callback = self._pending_confirmation_callback
                self._pending_confirmation_dialog = None
                self._pending_confirmation_callback = None
                if callback:
                    callback()
                return True
        return False

    # =========================================================================
    # Ship Picker (PROJ-198)
    # =========================================================================

    def show_ship_picker(self, ships, ability_name: str, on_selected) -> None:
        """Show ship picker dialog for multi-select.

        PROJ-198: Currently auto-selects all ships for simplicity.
        A full ship picker dialog with individual selection is a future enhancement.

        Args:
            ships: List of ships to pick from.
            ability_name: Ability name (for display/logging).
            on_selected: Callback with list of selected ship IDs.
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"Ship picker ({ability_name}): Auto-selecting all {len(ships)} ships"
        )
        # Auto-select all ships - full picker UI is a future enhancement
        on_selected([s.id for s in ships])
