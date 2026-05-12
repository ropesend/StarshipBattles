"""
StrategyBuildQueueManager - Manages build queue screen operations for StrategyScreen.

Extracted from StrategyScreen as part of PROJ-173 Phase 4 to reduce StrategyScreen
to ~530 lines. Handles all build queue screen creation, closing, and fleet BUILD order
management.

PROJ-211: DesignLoaderAdapter now requires registry_provider. Uses lazy initialization.
PROJ-376 Phase 2: Manager constructs ``BuildQueueScreen`` lazily on the first
build-yard click and reuses the same instance for every subsequent open via
``open_for_yard()``. The close callback no longer nulls the slot — callers
that want "currently displayed" semantics use ``is_visible()``.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import pygame

from game.ui.screens.build_queue_screen import BuildQueueScreen
from game.strategy.systems.design_library import DesignLibrary
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
from game.strategy.data.order_types import OrderType

from game.core.protocols import is_planet, is_fleet

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen
    from game.strategy.data.fleet import Fleet
    from game.core.protocols import IFleet
    from game.core.registry import GameRegistries
    from game.core.hex_math import HexCoord

logger = logging.getLogger(__name__)


# PROJ-211: Lazy registries initialization (not available at import time)
_cached_registries = None


def _get_registries() -> 'GameRegistries':
    """Get or create registries for DesignLoaderAdapter."""
    global _cached_registries
    if _cached_registries is None:
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        _cached_registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
            resource_catalog=provider.get_resource_catalog(),
        )
    return _cached_registries


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
        # PROJ-410 Phase 4 Task 4.2: track last-seen active empire id so
        # _open_build_queue can detect player change between opens and
        # invoke cached_screen.on_active_player_changed() to flush stale
        # widget/queue state.
        self._last_active_empire_id: int | None = None

    def _active_theme_id(self) -> str:
        """Resolve the active empire's ``empire_theme_id`` (PROJ-396 MAJ-002).

        Zero-arg supplier passed to ``BuildQueuePortraitLoader`` so the
        loader has no reference to the session.  Returns ``"Federation"``
        when the active empire / theme cannot be resolved (matches the
        prior loader fallback).
        """
        empire = self._screen.current_empire
        theme = getattr(empire, "empire_theme_id", None) if empire else None
        return theme or "Federation"

    def _open_build_queue(
        self,
        yard,
        hex_coord: 'HexCoord',
        portrait_surface: Optional[pygame.Surface],
        design_library: DesignLibrary,
        design_loader: DesignLoaderAdapter,
    ) -> None:
        """Open the build queue overlay for ``yard``.

        PROJ-376 Phase 2: Constructs ``BuildQueueScreen`` lazily on first
        call and reuses the cached instance for every subsequent call via
        ``open_for_yard()``. Re-binds the per-click ``DesignLibrary`` /
        ``DesignLoaderAdapter`` (and the drag handler / portrait loader
        references that hang off them) onto the cached instance so each
        open reflects the manager's current empire context.
        """
        # PROJ-410 Phase 4 Task 4.2: detect active-player change and rebind
        # cached domain context. Use self._screen.current_empire (existing
        # property at strategy_screen.py:192) — no new facade accessor.
        current_empire = self._screen.current_empire
        current_empire_id = current_empire.id if current_empire is not None else None

        if self._screen.build_queue_screen is None:
            # PROJ-382 Phase 1: facade-only construction.
            # PROJ-396 MAJ-002: BuildQueuePortraitLoader no longer takes a
            # session — pass a narrow zero-arg supplier for the active
            # empire's ``empire_theme_id`` instead.
            self._screen.build_queue_screen = BuildQueueScreen(
                self._screen.ui.manager,
                build_context=None,
                on_close_callback=self._on_build_queue_close,
                portrait_surface=portrait_surface,
                design_library=design_library,
                design_loader=design_loader,
                hex_coord=None,
                galaxy=self._screen.galaxy,
                empire=current_empire,
                input_mapper=self._screen.input_mapper,
                facade=self._screen.facade,
                theme_id_supplier=self._active_theme_id,
                initial_yard=None,
            )
        else:
            # Re-bind per-click dependencies onto the cached instance. The
            # manager constructs a fresh ``DesignLibrary`` / ``DesignLoader``
            # per click (the empire context CAN differ — e.g. a
            # navigate-from-empire-queue path uses ``current_empire`` while
            # ``on_build_yard_click`` uses ``planet.owner_id``). The
            # ``portrait_loader`` holds a reference to the library, so it
            # must be rebuilt too. The drag handler's ``design_library``
            # reference is rebound inside ``open_for_yard`` already, but
            # only if the drag handler exists yet — covered by the fact
            # that we only reach this branch after first construction.
            screen = self._screen.build_queue_screen
            # PROJ-410 Phase 4 Task 4.2: if the active empire changed since
            # the last open, flush widget/queue state on the cached screen
            # BEFORE rebinding new context. Without the flush the next
            # open_for_yard would render the prior empire's queues against
            # newly-rebound domain refs.
            if (self._last_active_empire_id is not None
                    and current_empire_id != self._last_active_empire_id):
                screen.on_active_player_changed()
            screen.design_library = design_library
            screen.design_loader = design_loader
            screen.portrait_loader = BuildQueuePortraitLoader(
                design_library, self._active_theme_id
            )

        # PROJ-410 Phase 4 Task 4.2: rebind cached domain context (empire,
        # galaxy, facade) before every open_for_yard(). Without this the
        # cached BuildQueueScreen still queries as the prior empire — the
        # root cause of the missing-yard-selector + cross-player-merged-
        # display symptoms (collect_build_queues_at_hex filters by empire.id
        # at build_queue_source.py:412-416).
        self._screen.build_queue_screen.empire = current_empire
        self._screen.build_queue_screen.galaxy = self._screen.galaxy
        self._screen.build_queue_screen.facade = self._screen.facade

        self._screen.build_queue_screen.open_for_yard(
            yard, hex_coord=hex_coord, portrait_surface=portrait_surface
        )

        # Update last-seen empire id AFTER successful open.
        self._last_active_empire_id = current_empire_id

    def on_build_yard_click(self) -> None:
        """Open build queue screen for selected planet."""
        if is_planet(self._screen.selected_object):
            planet = self._screen.selected_object
            if planet.owner_id == self._screen.current_empire.id:
                # Hide main UI
                self._screen.ui.hide_ui()

                # Get planet portrait from asset system
                portrait_surface = self._screen._get_object_asset(planet)

                # PROJ-40: Create dependencies for DI injection.
                # PROJ-396 MAJ-004: route save_path / galaxy through facade
                # / screen properties instead of reaching into the session.
                savegame_path = self._screen.facade.get_save_path()
                empire_id = planet.owner_id
                # PROJ-411 Phase 1: pass facade_state so scan_designs() reuses
                # the per-turn cache instead of re-globbing 47 JSON files per open.
                design_library = DesignLibrary(
                    savegame_path, empire_id,
                    facade_state=getattr(self._screen.facade, "facade_state", None),
                )
                # PROJ-211: Pass registries explicitly
                design_loader = DesignLoaderAdapter(registry_provider=_get_registries())

                # PROJ-69: Calculate hex coord for multi-queue discovery
                parent_sys = self._screen.galaxy.get_system_of_planet(planet)
                hex_coord = parent_sys.global_location + planet.location if parent_sys else None

                self._open_build_queue(
                    planet, hex_coord, portrait_surface,
                    design_library, design_loader,
                )
                logger.info(f"Opened build queue for {planet.name}")

    def _on_build_queue_close(self) -> None:
        """Handle build queue screen closing.

        PROJ-69: Iterates all queue sources from the closing screen and
        manages BUILD orders for any fleet-type sources.

        PROJ-376 Phase 2: The close-button / Esc handler in
        ``BuildQueueScreen._request_close`` already invoked ``hide()``
        before invoking this callback. The manager does NOT call
        ``hide()`` again and does NOT null the screen slot — the
        instance survives across opens for reuse.
        """
        logger.info("_on_build_queue_close() CALLED")

        # PROJ-69: Handle fleet BUILD orders for all fleet-type queue sources
        queue_sources = self._screen.build_queue_screen.queue_sources
        processed_fleets = set()
        for source in queue_sources:
            if source.context_type == 'fleet':
                fleet: IFleet = source.owner_entity
                fleet_id = fleet.id  # IFleet.id is always present
                if fleet_id not in processed_fleets:
                    processed_fleets.add(fleet_id)
                    self._handle_fleet_build_queue_close(fleet)

        # PROJ-376 Phase 2: do NOT null self._screen.build_queue_screen.
        # The cached instance is reused on the next click via open_for_yard().

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

        PROJ-207 Phase 4: Routes BUILD orders through command pipeline.

        Args:
            fleet: Fleet that was building
        """
        from game.strategy.engine.commands import IssueBuildOrderCommand, RemoveBuildOrderCommand

        if fleet.construction_queue:
            # Check if fleet already has BUILD order
            has_build_order = any(
                order.type == OrderType.BUILD
                for order in fleet.orders
            )
            if not has_build_order:
                logger.info(f"Auto-issuing BUILD order to fleet {fleet.id} ({len(fleet.construction_queue)} items in queue)")
                cmd = IssueBuildOrderCommand(fleet_id=fleet.id)
                self._screen.facade.handle_command(cmd)
        else:
            # Queue is empty - remove BUILD order if present via command pipeline
            cmd = RemoveBuildOrderCommand(fleet_id=fleet.id)
            self._screen.facade.handle_command(cmd)

    def on_navigate_to_hex_build(self, hex_coord, source) -> None:
        """Navigate to the build queue screen for a specific hex and source.

        Called from the empire-wide build queue window (PROJ-76) when the user
        double-clicks a row to navigate to the per-hex build screen.

        Args:
            hex_coord: The HexCoord of the source's location.
            source: BuildQueueSource identifying the entity to open.
        """
        entity = source.owner_entity
        if entity is None:
            logger.warning("on_navigate_to_hex_build: source has no owner_entity")
            return

        # Close the empire build queue window
        self._screen.ui.close_empire_build_queue_window()

        # Hide main UI
        self._screen.ui.hide_ui()

        # Get portrait from asset system
        portrait_surface = self._screen._get_object_asset(entity)

        # Create dependencies for DI injection.
        # PROJ-396 MAJ-004: save_path via facade.
        savegame_path = self._screen.facade.get_save_path()
        empire_id = self._screen.current_empire.id
        # PROJ-411 Phase 1: pass facade_state so scan_designs() reuses
        # the per-turn cache instead of re-globbing 47 JSON files per open.
        design_library = DesignLibrary(
            savegame_path, empire_id,
            facade_state=getattr(self._screen.facade, "facade_state", None),
        )
        # PROJ-211: Pass registries explicitly
        design_loader = DesignLoaderAdapter(registry_provider=_get_registries())

        self._open_build_queue(
            entity, hex_coord, portrait_surface,
            design_library, design_loader,
        )
        logger.info(f"Navigated to build queue for {source.display_name} at hex {hex_coord}")

    def on_fleet_build_click(self) -> None:
        """Open build queue screen for selected fleet (PROJ-67: Fleet Space Yards)."""
        if is_fleet(self._screen.selected_object):
            fleet = self._screen.selected_object
            if fleet.owner_id == self._screen.current_empire.id and fleet.capabilities.has_space_shipyard:
                # Hide main UI
                self._screen.ui.hide_ui()

                # Get fleet portrait from asset system
                portrait_surface = self._screen._get_object_asset(fleet)

                # Create dependencies for DI injection.
                # PROJ-396 MAJ-004: save_path via facade.
                savegame_path = self._screen.facade.get_save_path()
                empire_id = fleet.owner_id
                # PROJ-411 Phase 1: pass facade_state so scan_designs() reuses
                # the per-turn cache instead of re-globbing 47 JSON files per open.
                design_library = DesignLibrary(
                    savegame_path, empire_id,
                    facade_state=getattr(self._screen.facade, "facade_state", None),
                )
                # PROJ-211: Pass registries explicitly
                design_loader = DesignLoaderAdapter(registry_provider=_get_registries())

                # PROJ-69: Use fleet.location as hex_coord for multi-queue discovery
                hex_coord = fleet.location

                self._open_build_queue(
                    fleet, hex_coord, portrait_surface,
                    design_library, design_loader,
                )
                logger.info(f"Opened build queue for fleet {fleet.id}")
