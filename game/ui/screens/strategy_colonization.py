"""
Colonization workflow for strategy scene.
Handles colonize commands, planet validation, and mission queuing.

Extracted from StrategyScreen to reduce file size and improve testability.

Cross-layer imports (acceptable for UI):
- Camera.hex_at_screen: Runtime - coordinate conversion for command targeting
- IssueColonizeCommand, QueueColonizeMissionCommand: Runtime - UI issues commands
- StrategySessionFacade: TYPE_CHECKING - used for type hints only
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
import logging

logger = logging.getLogger(__name__)
from game.core.protocols import is_planet
from game.strategy.engine.commands import IssueColonizeCommand, QueueColonizeMissionCommand

if TYPE_CHECKING:
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade
    from game.ui.renderer.camera import Camera
    from game.strategy.data.star_system import StarSystem
    from game.core.hex_math import HexCoord


class ColonizationSystem:
    """Handles colonization commands and workflows."""

    def __init__(self, scene, facade: 'StrategySessionFacade'):
        """
        Initialize colonization system.

        Args:
            scene: StrategyScreen instance providing camera, systems, hex_size, etc.
            facade: StrategySessionFacade for all engine interactions
        """
        self.scene = scene
        self.facade = facade

    @property
    def camera(self) -> "Camera":
        return self.scene.camera

    @property
    def hex_size(self) -> float:
        return self.scene.hex_size

    def on_colonize_click(self, fleet) -> dict | None:
        """
        Handle colonize button/key action.

        Validates colonizable planets at fleet's current location.
        PROJ-55: Filters by available colony pods.

        Args:
            fleet: Fleet to issue colonize order to

        Returns:
            dict with result type:
            - {'type': 'prompt', 'planets': list, 'fleet': Fleet} if multiple options
            - {'type': 'success', 'fleet': Fleet} if single planet colonized
            - {'type': 'error', 'message': str} on failure
            - {'type': 'no_targets', 'message': str, 'remaining_pods': dict} when no pods
            - None if no fleet or no valid planets
        """
        if not fleet:
            return None

        # Find potential planets at fleet location
        start_sys = self._get_system_at_hex(fleet.location)
        potential_planets = []

        if start_sys:
            loc_local = fleet.location - start_sys.global_location
            for p in start_sys.planets:
                if p.location == loc_local:
                    potential_planets.append(p)

            # PROJ-139: Also check zone registry for multi-hex planets (Dyson
            # Spheres). PROJ-477 Phase 4: live zone objects via scene.world
            # (these are consumed as live domain objects — is_planet protocol
            # check + id round-trip into can_colonize — so NOT the DTO query).
            zone_objects = self.scene.world.zones_at_hex(fleet.location)
            for zone_obj in zone_objects:
                if is_planet(zone_obj) and zone_obj not in potential_planets:
                    potential_planets.append(zone_obj)
        else:
            # Full scan (rare - fleet in deep space)
            for sys in self.scene.world.iter_systems():
                loc_local = fleet.location - sys.global_location
                for p in sys.planets:
                    if p.location == loc_local:
                        potential_planets.append(p)

        # Validate with facade
        valid_planets = []
        for p in potential_planets:
            res = self.facade.validation.can_colonize(fleet.id, p.id)
            if res.is_valid:
                valid_planets.append(p)

        if not valid_planets:
            logger.debug("No colonizable planets at fleet location (Validation Failed).")
            return None

        # Return candidates for UI to open colonize dialog (or planet selection if multiple).
        # Pod availability is checked at execution time, not here — the player may
        # load a pod onto the ship before the fleet arrives at the target planet.
        return {
            'type': 'prompt',
            'planets': valid_planets,
            'fleet': fleet,
        }

    def issue_colonize_order(self, fleet, planet, population_amount=None, cargo_amounts=None) -> dict:
        """
        Issue colonize command via facade.

        Args:
            fleet: Fleet to colonize with
            planet: Planet to colonize
            population_amount: Specific population to drop (None = all)
            cargo_amounts: Dict of resource amounts to drop (None = all)

        Returns:
            dict with result type and details
        """
        cmd = IssueColonizeCommand(
            fleet.id, planet.id,
            population_amount=population_amount,
            cargo_amounts=cargo_amounts,
        )
        logger.info(f"Issued IssueColonizeCommand for {planet.name}")

        result = self.facade.handle_command(cmd)
        if not result.is_valid:
            logger.warning(f"Command Failed: {result.message}")
            return {'type': 'error', 'message': result.message}

        return {'type': 'success', 'fleet': fleet}

    def handle_colonize_designation(self, mx, my, fleet) -> dict | None:
        """
        Handle selecting a planet for colonization with movement.

        Args:
            mx, my: Mouse screen coordinates
            fleet: Fleet to issue mission to

        Returns:
            dict with result type, or None if invalid
        """
        if not fleet:
            return None

        target_hex = self.camera.hex_at_screen(mx, my, self.hex_size)

        target_system = self._get_system_at_hex(target_hex)
        if not target_system:
            logger.debug("No system at target location.")
            return None

        local_hex = target_hex - target_system.global_location
        candidates = [p for p in target_system.planets
                      if p.owner_id is None and p.location == local_hex]

        # PROJ-139: Also check zone registry for multi-hex planets.
        # PROJ-477 Phase 4: live zone objects via scene.world (consumed as live
        # domain objects — is_planet + owner_id + id round-trip).
        for zone_obj in self.scene.world.zones_at_hex(target_hex):
            if is_planet(zone_obj) and zone_obj not in candidates:
                if zone_obj.owner_id is None:
                    candidates.append(zone_obj)

        if not candidates:
            logger.debug(f"No colonizable planets at hex {target_hex}.")
            return None

        # Pod availability checked at execution time — player may load a pod before arrival.
        # Always return prompt so the colonize dialog opens for population/cargo amounts.
        return {
            'type': 'prompt',
            'planets': candidates,
            'target_hex': target_hex,
            'fleet': fleet,
        }

    def queue_colonize_mission(self, target_hex, planet, fleet,
                               population_amount=None, cargo_amounts=None) -> dict | None:
        """
        Queue MOVE + COLONIZE orders for a colonization mission via facade.

        Args:
            target_hex: Destination hex coordinate
            planet: Planet to colonize, or None for "any available planet"
            fleet: Fleet to issue orders to

        Returns:
            dict with result type and details
        """
        if not fleet:
            return None

        # Handle planet=None (colonize any available planet when arriving)
        planet_id = planet.id if planet else None
        cmd = QueueColonizeMissionCommand(
            fleet.id, target_hex, planet_id,
            population_amount=population_amount,
            cargo_amounts=cargo_amounts,
        )
        result = self.facade.handle_command(cmd)

        if result.is_valid:
            p_name = planet.name if planet else "Any Planet"
            logger.info(f"Mission Queued: Colonize {p_name} at {target_hex}")
            return {'type': 'success', 'fleet': fleet}
        else:
            logger.warning(f"Colonize mission failed: {result.message}")
            return {'type': 'error', 'message': result.message}

    def request_colonize_order(self, fleet, planet) -> "dict[str, Any] | None":
        """
        Request colonization order from UI (e.g. detailed panel button).

        Args:
            fleet: Fleet to colonize with
            planet: Planet to colonize (if known), or None for location-based

        Returns:
            dict with result type and details, or None
        """
        if planet:
            # Direct colonize with known planet
            target_hex = self._resolve_planet_global_hex(planet)
            if target_hex:
                return self.queue_colonize_mission(target_hex, planet, fleet)
            else:
                logger.warning("Could not resolve system for planet.")
                return {'type': 'error', 'message': 'Could not resolve planet location'}
        else:
            return self.on_colonize_click(fleet)

    def _get_system_at_hex(self, hex_coord) -> "StarSystem | None":
        """
        Find system at hex coordinate.

        Args:
            hex_coord: HexCoord to search

        Returns:
            StarSystem or None
        """
        # PROJ-477 Phase 4: live system-ownership lookup via scene.world
        # (radius=50 pathfinder semantics). Caller reads the live .planets.
        return self.scene.world.system_at_map_hex(hex_coord)

    def _resolve_planet_global_hex(self, planet) -> "HexCoord | None":
        """
        Resolve a planet's global hex coordinate.

        Args:
            planet: Planet to resolve

        Returns:
            HexCoord or None
        """
        # PROJ-477 Phase 4: iterate live systems through scene.world.
        for sys in self.scene.world.iter_systems():
            if planet in sys.planets:
                return sys.global_location + planet.location
        return None
