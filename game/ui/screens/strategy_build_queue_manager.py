"""
StrategyBuildQueueManager - Manages build queue screen operations for StrategyScreen.

Extracted from StrategyScreen as part of PROJ-173 Phase 4 to reduce StrategyScreen
to ~530 lines. Handles all build queue screen creation, closing, and fleet BUILD order
management.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen
    from game.strategy.data.fleet import Fleet
    from game.core.protocols import IFleet

logger = logging.getLogger(__name__)


class StrategyBuildQueueManager:
    """Manages build queue screen creation and lifecycle.

    Handles:
    - Opening build queue for planets (on_build_yard_click)
    - Opening build queue for fleets (on_fleet_build_click)
    - Navigation from empire-wide queue to hex-specific queue
    - Closing build queue and managing fleet BUILD orders
    """

    def __init__(self, screen: "StrategyScreen") -> None:
        """Initialize the build queue manager.

        Args:
            screen: Parent StrategyScreen for accessing session, UI, and state.
        """
        self._screen = screen

    def on_build_yard_click(self) -> None:
        """Open build queue screen for selected planet."""
        # Guard against double-open - if build queue is already open, ignore
        if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
            logger.info("Build queue already open, ignoring click")
            return

        from game.strategy.data.planet import Planet
        if isinstance(self._screen.selected_object, Planet):
            planet = self._screen.selected_object
            if planet.owner_id == self._screen.current_empire.id:
                from game.ui.screens.build_queue_screen import BuildQueueScreen
                from game.strategy.systems.design_library import DesignLibrary
                from game.ui.services.design_loader_adapter import DesignLoaderAdapter

                # Hide main UI
                self._screen.ui.hide_ui()

                # Get planet portrait from asset system
                portrait_surface = self._screen._get_object_asset(planet)

                # PROJ-40: Create dependencies for DI injection
                savegame_path = getattr(self._screen.session, 'save_path', None)
                empire_id = planet.owner_id
                design_library = DesignLibrary(savegame_path, empire_id)
                design_loader = DesignLoaderAdapter()

                # PROJ-69: Calculate hex coord for multi-queue discovery
                parent_sys = self._screen.session.galaxy.get_system_of_planet(planet)
                hex_coord = parent_sys.global_location + planet.location if parent_sys else None

                # Create screen with injected dependencies and hex context
                self._screen.build_queue_screen = BuildQueueScreen(
                    self._screen.ui.manager,
                    planet,
                    self._screen.session,
                    on_close_callback=self._on_build_queue_close,
                    portrait_surface=portrait_surface,
                    design_library=design_library,
                    design_loader=design_loader,
                    hex_coord=hex_coord,
                    galaxy=self._screen.session.galaxy,
                    empire=self._screen.current_empire,
                    input_mapper=self._screen.input_mapper
                )
                logger.info(f"Opened build queue for {planet.name}")

    def _on_build_queue_close(self) -> None:
        """Handle build queue screen closing.

        PROJ-69: Iterates all queue sources from the closing screen and
        manages BUILD orders for any fleet-type sources.
        """
        logger.info("_on_build_queue_close() CALLED")

        # PROJ-69: Handle fleet BUILD orders for all fleet-type queue sources
        queue_sources = getattr(self._screen.build_queue_screen, 'queue_sources', [])
        processed_fleets = set()
        for source in queue_sources:
            if source.context_type == 'fleet':
                fleet: IFleet = source.owner_entity
                fleet_id = fleet.id  # IFleet.id is always present
                if fleet_id not in processed_fleets:
                    processed_fleets.add(fleet_id)
                    self._handle_fleet_build_queue_close(fleet)

        self._screen.build_queue_screen = None

        # Show main UI again
        self._screen.ui.show_ui()

        # Refresh planet details to show updated queue/facilities
        if self._screen.selected_object:
            try:
                logger.info(f"  Refreshing display for selected_object: {self._screen.selected_object}")
                img = self._screen._get_object_asset(self._screen.selected_object)
                self._screen.ui.show_detailed_report(self._screen.selected_object, img)
            except (FileNotFoundError, OSError, pygame.error, AttributeError, KeyError) as e:
                logger.warning(f"Could not refresh planet display after build queue close: {e}")
        logger.info("_on_build_queue_close() FINISHED")

    def _handle_fleet_build_queue_close(self, fleet: "Fleet") -> None:
        """Handle fleet build queue closing - auto-issue BUILD order if items in queue.

        Args:
            fleet: Fleet that was building
        """
        from game.strategy.data.fleet import FleetOrder, OrderType

        if fleet.construction_queue:
            # Check if fleet already has BUILD order
            has_build_order = any(
                order.type == OrderType.BUILD
                for order in fleet.orders
            )
            if not has_build_order:
                logger.info(f"Auto-issuing BUILD order to fleet {fleet.id} ({len(fleet.construction_queue)} items in queue)")
                fleet.orders.insert(0, FleetOrder(OrderType.BUILD))
                fleet.path = []  # Clear movement path
        else:
            # Queue is empty - remove BUILD order if present
            fleet.orders = [o for o in fleet.orders if o.type != OrderType.BUILD]

    def on_navigate_to_hex_build(self, hex_coord, source) -> None:
        """Navigate to the build queue screen for a specific hex and source.

        Called from the empire-wide build queue window (PROJ-76) when the user
        double-clicks a row to navigate to the per-hex build screen.

        Args:
            hex_coord: The HexCoord of the source's location.
            source: BuildQueueSource identifying the entity to open.
        """
        # Guard against double-open
        if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
            logger.info("Build queue already open, ignoring navigate")
            return

        entity = source.owner_entity
        if entity is None:
            logger.warning("on_navigate_to_hex_build: source has no owner_entity")
            return

        # Close the empire build queue window
        self._screen.ui.close_empire_build_queue_window()

        from game.ui.screens.build_queue_screen import BuildQueueScreen
        from game.strategy.systems.design_library import DesignLibrary
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        # Hide main UI
        self._screen.ui.hide_ui()

        # Get portrait from asset system
        portrait_surface = self._screen._get_object_asset(entity)

        # Create dependencies for DI injection
        savegame_path = getattr(self._screen.session, 'save_path', None)
        empire_id = self._screen.current_empire.id
        design_library = DesignLibrary(savegame_path, empire_id)
        design_loader = DesignLoaderAdapter()

        # Create build queue screen with hex context
        self._screen.build_queue_screen = BuildQueueScreen(
            self._screen.ui.manager,
            entity,
            self._screen.session,
            on_close_callback=self._on_build_queue_close,
            portrait_surface=portrait_surface,
            design_library=design_library,
            design_loader=design_loader,
            hex_coord=hex_coord,
            galaxy=self._screen.session.galaxy,
            empire=self._screen.current_empire,
            input_mapper=self._screen.input_mapper
        )
        logger.info(f"Navigated to build queue for {source.display_name} at hex {hex_coord}")

    def on_fleet_build_click(self) -> None:
        """Open build queue screen for selected fleet (PROJ-67: Fleet Space Yards)."""
        # Guard against double-open
        if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
            logger.info("Build queue already open, ignoring click")
            return

        from game.strategy.data.fleet import Fleet
        if isinstance(self._screen.selected_object, Fleet):
            fleet = self._screen.selected_object
            if fleet.owner_id == self._screen.current_empire.id and fleet.has_space_shipyard:
                from game.ui.screens.build_queue_screen import BuildQueueScreen
                from game.strategy.systems.design_library import DesignLibrary
                from game.ui.services.design_loader_adapter import DesignLoaderAdapter

                # Hide main UI
                self._screen.ui.hide_ui()

                # Get fleet portrait from asset system
                portrait_surface = self._screen._get_object_asset(fleet)

                # Create dependencies for DI injection
                savegame_path = getattr(self._screen.session, 'save_path', None)
                empire_id = fleet.owner_id
                design_library = DesignLibrary(savegame_path, empire_id)
                design_loader = DesignLoaderAdapter()

                # PROJ-69: Use fleet.location as hex_coord for multi-queue discovery
                hex_coord = fleet.location

                # Create screen with fleet as build_context and hex context
                self._screen.build_queue_screen = BuildQueueScreen(
                    self._screen.ui.manager,
                    fleet,  # Fleet as build_context
                    self._screen.session,
                    on_close_callback=self._on_build_queue_close,
                    portrait_surface=portrait_surface,
                    design_library=design_library,
                    design_loader=design_loader,
                    hex_coord=hex_coord,
                    galaxy=self._screen.session.galaxy,
                    empire=self._screen.current_empire,
                    input_mapper=self._screen.input_mapper
                )
                logger.info(f"Opened build queue for fleet {fleet.id}")
