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
from game.strategy.systems.design_catalog import DesignCatalog
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
from game.strategy.data.order_types import OrderType

from game.core.protocols import is_planet, is_fleet

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen
    from game.core.hex_math import HexCoord

logger = logging.getLogger(__name__)


# PROJ-420: Lazy registries cache lives in game.core.registry_cache —
# single source of truth shared across ship_io, strategy_build_queue_manager,
# and setup_data_io.
from game.core.registry_cache import get_cached_registries


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

    def _design_catalog_for_empire(self, empire_id: int) -> DesignCatalog:
        """Resolve the per-empire ``DesignCatalog`` from the facade.

        PROJ-434 Phase 2: replaces the previous
        ``DesignLibrary(savegame_path, empire_id, facade_state=...)`` (legacy)
        construction. The catalog is bootstrapped per-empire and holds
        a reference to its disk-bound ``DesignRepository`` (see
        ``SessionBootstrap`` / ``PersistenceAdapter``), so writes
        through ``catalog.save_design`` still hit the per-empire
        designs folder. The QA-Obs-3 cache contract is preserved
        because every read in the BuildQueue family routes through
        the same catalog instance — workshop saves invalidate the
        in-memory list view via ``catalog.upsert_design`` and the
        next ``catalog.scan_designs()`` sees the new entry.

        PROJ-472 Phase 1C: route through
        ``facade.facade_state.get_design_catalog_for_empire`` rather than
        reaching ``facade_state.session.services.design_catalogs_by_empire``.
        The accessor returns the same per-empire ``DesignCatalog`` object,
        so the QA-Obs-3 cache contract above is unchanged. A ``KeyError``
        (no catalog for the empire) is preserved as before.
        """
        catalog = self._screen.facade.facade_state.get_design_catalog_for_empire(
            empire_id
        )
        if catalog is None:
            raise KeyError(empire_id)
        return catalog

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
        design_catalog: DesignCatalog,
        design_loader: DesignLoaderAdapter,
    ) -> None:
        """Open the build queue overlay for ``yard``.

        PROJ-376 Phase 2: Constructs ``BuildQueueScreen`` lazily on first
        call and reuses the cached instance for every subsequent call via
        ``open_for_yard()``. Re-binds the per-click ``DesignCatalog`` /
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
                on_close_callback=self._on_build_queue_close,
                portrait_surface=portrait_surface,
                design_catalog=design_catalog,
                design_loader=design_loader,
                hex_coord=None,
                world=self._screen.world,
                empire=current_empire,
                input_mapper=self._screen.input_mapper,
                facade=self._screen.facade,
                theme_id_supplier=self._active_theme_id,
                initial_yard=None,
            )
        else:
            # Re-bind per-click dependencies onto the cached instance. The
            # manager resolves a per-empire ``DesignCatalog`` per click; the
            # empire context CAN differ (e.g. a navigate-from-empire-queue
            # path uses ``current_empire`` while ``on_build_yard_click``
            # uses ``planet.owner_id``). The ``portrait_loader`` holds a
            # reference to the catalog, so it must be rebuilt too. The
            # drag handler's ``design_catalog`` reference is rebound inside
            # ``open_for_yard`` already, but only if the drag handler
            # exists yet — covered by the fact that we only reach this
            # branch after first construction.
            screen = self._screen.build_queue_screen
            # PROJ-410 Phase 4 Task 4.2: if the active empire changed since
            # the last open, flush widget/queue state on the cached screen
            # BEFORE rebinding new context. Without the flush the next
            # open_for_yard would render the prior empire's queues against
            # newly-rebound domain refs.
            if (self._last_active_empire_id is not None
                    and current_empire_id != self._last_active_empire_id):
                screen.on_active_player_changed()
            screen.design_catalog = design_catalog
            screen.design_loader = design_loader
            screen.portrait_loader = BuildQueuePortraitLoader(
                design_catalog, self._active_theme_id
            )

        # PROJ-410 Phase 4 Task 4.2: rebind cached domain context (empire,
        # galaxy, facade) before every open_for_yard(). Without this the
        # cached BuildQueueScreen still queries as the prior empire — the
        # root cause of the missing-yard-selector + cross-player-merged-
        # display symptoms (collect_build_queues_at_hex filters by empire.id
        # at build_queue_source.py:412-416).
        self._screen.build_queue_screen.empire = current_empire
        self._screen.build_queue_screen.world = self._screen.world
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

                # PROJ-434 Phase 2: resolve the per-empire DesignCatalog
                # from the live session (PROJ-427 bootstrap binds one per
                # empire). Replaces the previous DesignLibrary construction.
                empire_id = planet.owner_id
                design_catalog = self._design_catalog_for_empire(empire_id)
                # PROJ-211: Pass registries explicitly
                design_loader = DesignLoaderAdapter(registry_provider=get_cached_registries())

                # PROJ-69: Calculate hex coord for multi-queue discovery.
                # PROJ-477 Phase 4: live system via scene.world.
                parent_sys = self._screen.world.system_for_object(planet)
                hex_coord = parent_sys.global_location + planet.location if parent_sys else None

                self._open_build_queue(
                    planet, hex_coord, portrait_surface,
                    design_catalog, design_loader,
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

        # PROJ-69: Handle fleet BUILD orders for all fleet-type queue sources.
        # PROJ-472 Phase 1B: queue sources are ``BuildQueueSourceDTO`` — read
        # the fleet id off ``entity_id`` and inspect BUILD-order state via the
        # facade fleet query, never a live fleet object.
        queue_sources = self._screen.build_queue_screen.queue_sources
        processed_fleets = set()
        for source in queue_sources:
            if source.context_type == 'fleet':
                fleet_id = source.entity_id
                if fleet_id not in processed_fleets:
                    processed_fleets.add(fleet_id)
                    self._handle_fleet_build_queue_close(fleet_id)

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

    def _handle_fleet_build_queue_close(self, fleet_id: int) -> None:
        """Handle fleet build queue closing - auto-issue BUILD order if items in queue.

        PROJ-207 Phase 4: Routes BUILD orders through command pipeline.
        PROJ-472 Phase 1B: BUILD-order state is read from the facade fleet
        query (``facade.fleets.get(fleet_id)`` → ``FleetInfo``), not a live
        fleet object. Commands stay id-based.

        Args:
            fleet_id: Id of the fleet that was building.
        """
        from game.strategy.engine.commands import IssueBuildOrderCommand, RemoveBuildOrderCommand

        info = self._screen.facade.fleets.get(fleet_id)
        if info is None:
            logger.warning(
                "Fleet build-queue close: fleet id %s not found via facade", fleet_id
            )
            return

        if info.construction_queue_size > 0:
            # Check if fleet already has BUILD order
            has_build_order = any(
                order.order_type == OrderType.BUILD.name
                for order in info.orders
            )
            if not has_build_order:
                logger.info(
                    f"Auto-issuing BUILD order to fleet {fleet_id} "
                    f"({info.construction_queue_size} items in queue)"
                )
                cmd = IssueBuildOrderCommand(fleet_id=fleet_id)
                self._screen.facade.handle_command(cmd)
        else:
            # Queue is empty - remove BUILD order if present via command pipeline
            cmd = RemoveBuildOrderCommand(fleet_id=fleet_id)
            self._screen.facade.handle_command(cmd)

    def _resolve_live_yard(self, source) -> object | None:
        """Resolve the live yard (Planet or Fleet) for a build-queue DTO.

        PROJ-472 Phase 1B: the per-hex BuildQueueScreen's ``build_context``
        must be a live domain object, but the empire-window navigation
        callback now provides only a ``BuildQueueSourceDTO``. Resolve by id:
        planets via the galaxy registry, fleets via the session lookup.
        """
        if source.context_type == "planet":
            planet_id = source.planet_id if source.planet_id is not None else source.entity_id
            # PROJ-477 Phase 4 (POST-FLESH B3): live planet-by-id via scene.world.
            return self._screen.world.planet_by_id(planet_id)
        if source.context_type == "fleet":
            # PROJ-472 1C: resolve the live fleet via the facade-state id
            # lookup (cache-owning) rather than reaching
            # ``facade_state.session._get_fleet_by_id`` directly.
            return self._screen.facade.facade_state.get_fleet_by_id(
                source.entity_id
            )
        return None

    def on_navigate_to_hex_build(self, hex_coord, source) -> None:
        """Navigate to the build queue screen for a specific hex and source.

        Called from the empire-wide build queue window (PROJ-76) when the user
        double-clicks a row to navigate to the per-hex build screen.

        Args:
            hex_coord: The HexCoord of the source's location.
            source: ``BuildQueueSourceDTO`` identifying the entity to open.

        PROJ-472 Phase 1B: the empire-window callback now hands a
        ``BuildQueueSourceDTO`` (DTO scalars), not a live ``BuildQueueSource``.
        The per-hex build screen still needs a LIVE yard object as its
        ``build_context``, so resolve it by id here (planet via galaxy,
        fleet via session) from the DTO's ``context_type`` / ``entity_id``.
        """
        entity = self._resolve_live_yard(source)
        if entity is None:
            logger.warning(
                "on_navigate_to_hex_build: could not resolve live yard for "
                "%s id=%s", source.context_type, source.entity_id,
            )
            return

        # Close the empire build queue window
        self._screen.ui.close_empire_build_queue_window()

        # Hide main UI
        self._screen.ui.hide_ui()

        # Get portrait from asset system
        portrait_surface = self._screen._get_object_asset(entity)

        # PROJ-434 Phase 2: per-empire DesignCatalog via session services.
        empire_id = self._screen.current_empire.id
        design_catalog = self._design_catalog_for_empire(empire_id)
        # PROJ-211: Pass registries explicitly
        design_loader = DesignLoaderAdapter(registry_provider=get_cached_registries())

        self._open_build_queue(
            entity, hex_coord, portrait_surface,
            design_catalog, design_loader,
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

                # PROJ-434 Phase 2: per-empire DesignCatalog via session services.
                empire_id = fleet.owner_id
                design_catalog = self._design_catalog_for_empire(empire_id)
                # PROJ-211: Pass registries explicitly
                design_loader = DesignLoaderAdapter(registry_provider=get_cached_registries())

                # PROJ-69: Use fleet.location as hex_coord for multi-queue discovery
                hex_coord = fleet.location

                self._open_build_queue(
                    fleet, hex_coord, portrait_surface,
                    design_catalog, design_loader,
                )
                logger.info(f"Opened build queue for fleet {fleet.id}")
