"""
Colonization workflow for strategy scene.
Handles colonize commands, planet validation, and mission queuing.

Extracted from StrategyScreen to reduce file size and improve testability.

Cross-layer imports (acceptable for UI):
- pixel_to_hex: Runtime - coordinate conversion for command targeting
- IssueColonizeCommand, QueueColonizeMissionCommand: Runtime - UI issues commands
- StrategySessionFacade: TYPE_CHECKING - used for type hints only
"""
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)
from game.core.hex_math import pixel_to_hex
from game.core.protocols import is_planet
from game.strategy.engine.commands import IssueColonizeCommand, QueueColonizeMissionCommand

if TYPE_CHECKING:
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade


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
    def systems(self):
        return self.scene.systems

    @property
    def camera(self):
        return self.scene.camera

    @property
    def hex_size(self):
        return self.scene.hex_size

    def on_colonize_click(self, fleet):
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

            # PROJ-139: Also check zone registry for multi-hex planets (Dyson Spheres)
            if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
                zone_lookup = getattr(self.scene.galaxy, 'get_zones_at_global_hex', None)
                if zone_lookup and callable(zone_lookup):
                    zone_objects = zone_lookup(fleet.location)
                    if isinstance(zone_objects, list):
                        for zone_obj in zone_objects:
                            if is_planet(zone_obj) and zone_obj not in potential_planets:
                                potential_planets.append(zone_obj)
        else:
            # Full scan (rare - fleet in deep space)
            for sys in self.systems:
                loc_local = fleet.location - sys.global_location
                for p in sys.planets:
                    if p.location == loc_local:
                        potential_planets.append(p)

        # Validate with facade
        valid_planets = []
        for p in potential_planets:
            res = self.facade.can_colonize(fleet.id, p.id)
            if res.is_valid:
                valid_planets.append(p)

        if not valid_planets:
            logger.debug("No colonizable planets at fleet location (Validation Failed).")
            return None

        # PROJ-55: Filter by available colony pods
        remaining_pods = self.facade.get_fleet_remaining_pods(fleet.id)

        # If no remaining pods, return informative message
        if not remaining_pods:
            logger.debug("No colony pods available in fleet.")
            return {
                'type': 'no_targets',
                'message': 'No colony pods in fleet',
                'remaining_pods': remaining_pods,
            }

        # Filter planets by available pod types
        pod_filtered_planets = []
        for p in valid_planets:
            planet_type_str = p.planet_type.name
            if planet_type_str in remaining_pods:
                pod_filtered_planets.append(p)

        # If no planets match available pods
        if not pod_filtered_planets:
            pod_types = ", ".join(remaining_pods.keys())
            logger.debug(f"No colonizable planets for available pods ({pod_types}).")
            return {
                'type': 'no_targets',
                'message': f'No colonizable planets for available pods ({pod_types})',
                'remaining_pods': remaining_pods,
            }

        if len(pod_filtered_planets) == 1:
            return self.issue_colonize_order(fleet, pod_filtered_planets[0])
        else:
            # Return context for UI to prompt selection
            return {
                'type': 'prompt',
                'planets': pod_filtered_planets,
                'fleet': fleet,
            }

    def issue_colonize_order(self, fleet, planet):
        """
        Issue colonize command via facade.

        Args:
            fleet: Fleet to colonize with
            planet: Planet to colonize

        Returns:
            dict with result type and details
        """
        cmd = IssueColonizeCommand(fleet.id, planet.id)
        logger.info(f"Issued IssueColonizeCommand for {planet.name}")

        result = self.facade.handle_command(cmd)
        if not result.is_valid:
            logger.warning(f"Command Failed: {result.message}")
            return {'type': 'error', 'message': result.message}

        return {'type': 'success', 'fleet': fleet}

    def handle_colonize_designation(self, mx, my, fleet):
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

        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)

        target_system = self._get_system_at_hex(target_hex)
        if not target_system:
            logger.debug("No system at target location.")
            return None

        local_hex = target_hex - target_system.global_location
        candidates = [p for p in target_system.planets
                      if p.owner_id is None and p.location == local_hex]

        # PROJ-139: Also check zone registry for multi-hex planets
        if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
            zone_lookup = getattr(self.scene.galaxy, 'get_zones_at_global_hex', None)
            if zone_lookup and callable(zone_lookup):
                zone_objects = zone_lookup(target_hex)
                if isinstance(zone_objects, list):
                    for zone_obj in zone_objects:
                        if is_planet(zone_obj) and zone_obj not in candidates:
                            if zone_obj.owner_id is None:
                                candidates.append(zone_obj)

        if not candidates:
            logger.debug(f"No colonizable planets at hex {target_hex}.")
            return None

        # PROJ-140: Filter by available colony pods (same pattern as on_colonize_click)
        remaining_pods = self.facade.get_fleet_remaining_pods(fleet.id)

        # If no remaining pods, return informative message
        if not remaining_pods:
            logger.debug("No colony pods available in fleet for designation.")
            return {
                'type': 'no_targets',
                'message': 'No colony pods in fleet',
                'remaining_pods': remaining_pods,
            }

        # Filter candidates by available pod types
        pod_filtered = [p for p in candidates if p.planet_type.name in remaining_pods]

        # If no candidates match available pods
        if not pod_filtered:
            pod_types = ", ".join(remaining_pods.keys())
            logger.debug(f"No colonizable planets for available pods ({pod_types}) at designation.")
            return {
                'type': 'no_targets',
                'message': f'No colonizable planets for available pods ({pod_types})',
                'remaining_pods': remaining_pods,
            }

        if len(pod_filtered) == 1:
            return self.queue_colonize_mission(target_hex, pod_filtered[0], fleet)
        else:
            return {
                'type': 'prompt',
                'planets': pod_filtered,
                'target_hex': target_hex,
                'fleet': fleet,
            }

    def queue_colonize_mission(self, target_hex, planet, fleet):
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
        cmd = QueueColonizeMissionCommand(fleet.id, target_hex, planet_id)
        result = self.facade.handle_command(cmd)

        if result.is_valid:
            p_name = planet.name if planet else "Any Planet"
            logger.info(f"Mission Queued: Colonize {p_name} at {target_hex}")
            return {'type': 'success', 'fleet': fleet}
        else:
            logger.warning(f"Colonize mission failed: {result.message}")
            return {'type': 'error', 'message': result.message}

    def request_colonize_order(self, fleet, planet):
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

    def _get_system_at_hex(self, hex_coord):
        """
        Find system at hex coordinate.

        Args:
            hex_coord: HexCoord to search

        Returns:
            StarSystem or None
        """
        from game.strategy.data.pathfinding import get_system_at_hex
        # Access galaxy through scene (read-only for internal lookups)
        return get_system_at_hex(self.scene.galaxy, hex_coord)

    def _resolve_planet_global_hex(self, planet):
        """
        Resolve a planet's global hex coordinate.

        Args:
            planet: Planet to resolve

        Returns:
            HexCoord or None
        """
        # Access galaxy through scene (read-only for internal lookups)
        for sys in self.scene.galaxy.systems.values():
            if planet in sys.planets:
                return sys.global_location + planet.location
        return None
