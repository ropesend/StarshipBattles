"""
Colonization workflow for strategy scene.
Handles colonize commands, planet validation, and mission queuing.

Extracted from StrategyScene to reduce file size and improve testability.
"""
from game.core.logger import log_debug, log_info, log_warning
from game.strategy.data.fleet import FleetOrder, OrderType
from game.strategy.data.hex_math import pixel_to_hex
from game.strategy.engine.commands import IssueColonizeCommand


class ColonizationSystem:
    """Handles colonization commands and workflows."""

    def __init__(self, scene):
        """
        Initialize colonization system.

        Args:
            scene: StrategyScene instance providing galaxy, session, etc.
        """
        self.scene = scene

    @property
    def galaxy(self):
        return self.scene.galaxy

    @property
    def systems(self):
        return self.scene.systems

    @property
    def turn_engine(self):
        return self.scene.turn_engine

    @property
    def camera(self):
        return self.scene.camera

    @property
    def HEX_SIZE(self):
        return self.scene.HEX_SIZE

    @property
    def session(self):
        return self.scene.session

    def on_colonize_click(self, fleet):
        """
        Handle colonize button/key action.

        Validates colonizable planets at fleet's current location.

        Args:
            fleet: Fleet to issue colonize order to

        Returns:
            dict with result type:
            - {'type': 'prompt', 'planets': list, 'fleet': Fleet} if multiple options
            - {'type': 'success', 'fleet': Fleet} if single planet colonized
            - {'type': 'error', 'message': str} on failure
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
        else:
            # Full scan (rare - fleet in deep space)
            for sys in self.systems:
                loc_local = fleet.location - sys.global_location
                for p in sys.planets:
                    if p.location == loc_local:
                        potential_planets.append(p)

        # Validate with engine
        valid_planets = []
        for p in potential_planets:
            res = self.turn_engine.validate_colonize_order(self.galaxy, fleet, p)
            if res.is_valid:
                valid_planets.append(p)

        if not valid_planets:
            log_debug("No colonizable planets at fleet location (Validation Failed).")
            return None

        if len(valid_planets) == 1:
            return self.issue_colonize_order(fleet, valid_planets[0])
        else:
            # Return context for UI to prompt selection
            return {
                'type': 'prompt',
                'planets': valid_planets,
                'fleet': fleet,
            }

    def issue_colonize_order(self, fleet, planet):
        """
        Issue colonize command to session.

        Args:
            fleet: Fleet to colonize with
            planet: Planet to colonize

        Returns:
            dict with result type and details
        """
        cmd = IssueColonizeCommand(fleet.id, planet.id)
        log_info(f"Issued IssueColonizeCommand for {planet.name}")

        result = self.session.handle_command(cmd)
        if not result.is_valid:
            log_warning(f"Command Failed: {result.message}")
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
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)

        target_system = self._get_system_at_hex(target_hex)
        if not target_system:
            log_debug("No system at target location.")
            return None

        local_hex = target_hex - target_system.global_location
        candidates = [p for p in target_system.planets
                      if p.owner_id is None and p.location == local_hex]

        if not candidates:
            log_debug(f"No colonizable planets at hex {target_hex}.")
            return None

        if len(candidates) == 1:
            return self.queue_colonize_mission(target_hex, candidates[0], fleet)
        else:
            return {
                'type': 'prompt',
                'planets': candidates,
                'target_hex': target_hex,
                'fleet': fleet,
            }

    def queue_colonize_mission(self, target_hex, planet, fleet):
        """
        Queue MOVE + COLONIZE orders for a colonization mission.

        Args:
            target_hex: Destination hex coordinate
            planet: Planet to colonize
            fleet: Fleet to issue orders to

        Returns:
            dict with result type and details
        """
        if not fleet:
            return None

        # Determine start hex (current location or last order target)
        start_hex = fleet.location
        if fleet.orders:
            last = fleet.orders[-1]
            if last.type == OrderType.MOVE:
                start_hex = last.target

        # Calculate path
        from game.strategy.data.pathfinding import find_hybrid_path
        path = find_hybrid_path(self.galaxy, start_hex, target_hex)

        if path:
            # Queue MOVE if not already at target
            if start_hex != target_hex:
                move = FleetOrder(OrderType.MOVE, target_hex)
                fleet.add_order(move)
                if len(fleet.orders) == 1:
                    # Remove start hex from path before assigning
                    if path and path[0] == fleet.location:
                        path = path[1:]
                    fleet.path = path

            # Queue COLONIZE
            col = FleetOrder(OrderType.COLONIZE, planet)
            fleet.add_order(col)

            p_name = planet.name if planet else "Any Planet"
            log_info(f"Mission Queued: Colonize {p_name} at {target_hex}")
            return {'type': 'success', 'fleet': fleet}
        else:
            log_warning("Cannot find path.")
            return {'type': 'error', 'message': 'No path found'}

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
                log_warning("Could not resolve system for planet.")
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
        return get_system_at_hex(self.galaxy, hex_coord)

    def _resolve_planet_global_hex(self, planet):
        """
        Resolve a planet's global hex coordinate.

        Args:
            planet: Planet to resolve

        Returns:
            HexCoord or None
        """
        for sys in self.galaxy.systems.values():
            if planet in sys.planets:
                return sys.global_location + planet.location
        return None
