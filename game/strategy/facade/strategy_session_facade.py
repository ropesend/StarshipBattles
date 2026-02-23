"""Strategy Session Facade.

Provides a strict facade for UI-to-engine communication using CQRS-lite pattern.
All state mutations go through Commands, all reads return immutable DTOs.
"""
from typing import List, Optional, TYPE_CHECKING

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import (
    FleetInfo,
    SystemInfo,
    PlanetInfo,
    EmpireInfo,
    ColonySummary,
    FleetSummary,
)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession
    from game.strategy.engine.commands import Command


class StrategySessionFacade:
    """Facade for UI interaction with the strategy game session.

    This facade provides the single point of access for all UI-to-engine
    communication, implementing a CQRS-lite pattern:
    - Commands (writes): State mutations via handle_command()
    - Queries (reads): Return immutable DTOs, never domain objects

    The UI layer should never access GameSession internals directly.
    All domain objects are converted to DTOs before being returned.

    Attributes:
        _session: The underlying GameSession (private, not for UI access)
    """

    def __init__(self, session: 'GameSession') -> None:
        """Initialize the facade with a GameSession.

        Args:
            session: The GameSession instance to wrap
        """
        self._session = session

    # =========================================================================
    # COMMANDS (Write Path)
    # =========================================================================

    def handle_command(self, command: 'Command') -> ValidationResult:
        """Execute a command against the game session.

        All state mutations should go through this method. The command
        is validated and executed by the underlying GameSession.

        Args:
            command: The command to execute

        Returns:
            ValidationResult indicating success or failure with error details
        """
        return self._session.handle_command(command)

    def process_turn(self) -> None:
        """Process the current turn.

        This advances the game state by one turn, executing all queued
        orders, resolving movement, and processing AI actions.
        """
        self._session.process_turn()

    # =========================================================================
    # QUERIES (Read Path) - Return DTOs only, never domain objects
    # =========================================================================

    # --- Fleet Queries ---

    def _get_fleet_by_id(self, fleet_id: int):
        """Internal helper to get a fleet by ID across all empires.

        Delegates to GameSession._get_fleet_by_id() for O(1) lookup with fallback.

        Args:
            fleet_id: The fleet ID to find

        Returns:
            The Fleet domain object if found, None otherwise
        """
        return self._session._get_fleet_by_id(fleet_id)

    def _get_empire_by_id(self, empire_id: int):
        """Internal helper to get an empire by ID.

        Args:
            empire_id: The empire ID to find

        Returns:
            The Empire domain object if found, None otherwise
        """
        for empire in self._session.empires:
            if empire.id == empire_id:
                return empire
        return None

    def get_fleet(self, fleet_id: int) -> Optional[FleetInfo]:
        """Get fleet information by ID.

        Args:
            fleet_id: The unique fleet identifier

        Returns:
            FleetInfo DTO if found, None otherwise
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return FleetInfo.from_fleet(fleet)

    def get_fleets_at_hex(self, hex_coord: HexCoord) -> List[FleetInfo]:
        """Get all fleets at a specific hex coordinate.

        Args:
            hex_coord: The hex coordinate to query

        Returns:
            List of FleetInfo DTOs for fleets at the hex
        """
        result = []
        for empire in self._session.empires:
            for fleet in empire.fleets:
                if fleet.location == hex_coord:
                    result.append(FleetInfo.from_fleet(fleet))
        return result

    def get_fleet_path_preview(
        self, fleet_id: int, target_hex: HexCoord
    ) -> Optional[List[HexCoord]]:
        """Calculate a path preview for a fleet to a target.

        This is used for UI pathfinding preview without committing
        to a move order.

        Args:
            fleet_id: The fleet to calculate path for
            target_hex: The destination hex

        Returns:
            List of HexCoords representing the path, or None if invalid
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return self._session.preview_fleet_path(fleet, target_hex)

    def get_fleet_path_projection(
        self, fleet_id: int, max_turns: int = 50
    ) -> List[dict]:
        """Get turn-by-turn path projection for a fleet.

        Args:
            fleet_id: The fleet to get projection for
            max_turns: Maximum number of turns to project

        Returns:
            List of dicts with turn-by-turn movement info
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return []
        return self._session.get_fleet_path_projection(fleet, max_turns)

    # --- System Queries ---

    def get_all_systems(self) -> List[SystemInfo]:
        """Get information about all star systems.

        Returns:
            List of SystemInfo DTOs for all systems in the galaxy
        """
        return [
            SystemInfo.from_star_system(system)
            for system in self._session.galaxy.systems.values()
        ]

    def get_system_at_hex(self, hex_coord: HexCoord) -> Optional[SystemInfo]:
        """Get the system at a specific hex coordinate.

        Args:
            hex_coord: The hex coordinate to query (can be global center or any hex in system)

        Returns:
            SystemInfo DTO if a system exists at the hex, None otherwise
        """
        system = self._session.galaxy.get_system_at_location(hex_coord)
        if system is None:
            return None
        return SystemInfo.from_star_system(system)

    def get_system_containing_fleet(self, fleet_id: int) -> Optional[SystemInfo]:
        """Get the system containing (or closest to) the fleet.
        
        This handles cases where the fleet is in empty space within a system's logic bounds
        but not at a specific system object.
        
        Args:
            fleet_id: The fleet to find system for.
            
        Returns:
            SystemInfo DTO if fluidly within a system, None if in deep space.
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None: 
            return None
            
        return self.get_system_near_hex(fleet.location)

    def get_system_near_hex(self, hex_coord: HexCoord, max_dist: int = 8) -> Optional[SystemInfo]:
        """Get the system at or near the given hex coordinate.
        
        This is useful for resolving clicks that might be slightly off a system's strict location,
        or for finding the enclosing system when an entity is in 'empty space' within a system.
        
        Args:
            hex_coord: The hex coordinate to query.
            max_dist: Maximum distance to scan for a system (default 8 hexes).
            
        Returns:
            SystemInfo DTO if a system is found, None otherwise.
        """
        # 1. Try strict lookup first
        system = self._session.galaxy.get_system_at_location(hex_coord)
        if system:
            return SystemInfo.from_star_system(system)
            
        # 2. Proximity check
        from game.core.hex_math import hex_distance
        closest_system = None
        min_dist = max_dist + 1
        
        for sys in self._session.galaxy.systems.values():
            dist = hex_distance(sys.global_location, hex_coord)
            if dist < min_dist:
                min_dist = dist
                closest_system = sys
                
        if closest_system:
            return SystemInfo.from_star_system(closest_system)
            
        return None

    # --- Planet Queries ---

    def _get_planet_by_id(self, planet_id: int):
        """Internal helper to get a planet by ID across all systems.

        Args:
            planet_id: The planet ID to find

        Returns:
            The Planet domain object if found, None otherwise
        """
        for system in self._session.galaxy.systems.values():
            for planet in system.planets:
                if planet.id == planet_id:
                    return planet
        return None

    def get_planet(self, planet_id: int) -> Optional[PlanetInfo]:
        """Get planet information by ID.

        Args:
            planet_id: The unique planet identifier

        Returns:
            PlanetInfo DTO if found, None otherwise
        """
        planet = self._get_planet_by_id(planet_id)
        if planet is None:
            return None
        return PlanetInfo.from_planet(planet)

    def get_planets_at_hex(self, hex_coord: HexCoord) -> List[PlanetInfo]:
        """Get planets whose global position exactly matches the given hex coordinate.

        Only returns planets at the specific hex — not all planets in the system.
        A planet's global position is ``system.global_location + planet.location``.
        Uses radius search to resolve which system owns the hex when a strict
        lookup misses (e.g. clicking an inner hex that isn't the system center).

        Args:
            hex_coord: The exact global hex coordinate to match against planet positions.

        Returns:
            List of PlanetInfo DTOs for planets at this exact hex (may be empty).
        """
        # 1. Try strict lookup first (fast & correct for exact hits)
        system = self._session.galaxy.get_system_at_location(hex_coord)
        
        # 2. If strict failed, try radius/ownership lookup (robust for area clicks)
        if system is None:
            from game.strategy.data.pathfinding import get_system_at_hex
            system = get_system_at_hex(self._session.galaxy, hex_coord, radius=50)
            
        if system is None:
            return []
        
        target_planets = []
        for p in system.planets:
            p_global = system.global_location + p.location
            if p_global == hex_coord:
                target_planets.append(p)
                
        return [PlanetInfo.from_planet(planet) for planet in target_planets]

    # --- Empire Queries ---

    def get_all_empires(self) -> List[EmpireInfo]:
        """Get information about all empires.

        Returns:
            List of EmpireInfo DTOs for all empires
        """
        return [
            EmpireInfo.from_empire(empire)
            for empire in self._session.empires
        ]

    def get_empire(self, empire_id: int) -> Optional[EmpireInfo]:
        """Get empire information by ID.

        Args:
            empire_id: The unique empire identifier

        Returns:
            EmpireInfo DTO if found, None otherwise
        """
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return None
        return EmpireInfo.from_empire(empire)

    def get_empire_colonies(self, empire_id: int) -> List[ColonySummary]:
        """Get colony summaries for an empire.

        Args:
            empire_id: The empire to get colonies for

        Returns:
            List of ColonySummary DTOs for the empire's colonies
        """
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return []
        return [ColonySummary.from_planet(planet) for planet in empire.colonies]

    def get_empire_fleets(self, empire_id: int) -> List[FleetSummary]:
        """Get fleet summaries for an empire.

        Args:
            empire_id: The empire to get fleets for

        Returns:
            List of FleetSummary DTOs for the empire's fleets
        """
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return []
        return [FleetSummary.from_fleet(fleet) for fleet in empire.fleets]

    # --- Game State Queries ---

    def get_human_player_ids(self) -> List[int]:
        """Get the empire IDs of human players.

        Returns:
            List of empire IDs that are controlled by human players
        """
        return list(self._session.human_player_ids)

    def get_turn_number(self) -> int:
        """Get the current turn number.

        Returns:
            The current turn number (1-indexed)
        """
        return self._session.turn_number

    # --- Event Log Queries (PROJ-77) ---

    def get_turn_events(self, turn: int = None) -> List[dict]:
        """Get events for a specific turn (or current turn if None).

        Args:
            turn: The turn number to query. Defaults to current turn.

        Returns:
            List of event dicts (immutable for UI consumption).
        """
        if turn is None:
            turn = self._session.turn_number
        events = self._session.event_log.get_events_for_turn(turn)
        return [e.to_dict() for e in events]

    def get_all_events(self) -> List[dict]:
        """Get all events from the event log.

        Returns:
            List of all event dicts (immutable for UI consumption).
        """
        return [e.to_dict() for e in self._session.event_log.get_all_events()]

    def get_events_by_category(self, category: str) -> List[dict]:
        """Get events filtered by category.

        Args:
            category: Category string or EventCategory enum value to filter by.

        Returns:
            List of matching event dicts (immutable for UI consumption).
        """
        events = self._session.event_log.get_events_by_category(category)
        return [e.to_dict() for e in events]

    # --- Validation Queries ---

    def can_colonize(
        self, fleet_id: int, planet_id: Optional[int]
    ) -> ValidationResult:
        """Check if a fleet can colonize a planet.

        This validates colonization without executing the command.

        Args:
            fleet_id: The fleet to check
            planet_id: The target planet (or None to check current location)

        Returns:
            ValidationResult indicating whether colonization is valid
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        planet = None
        if planet_id is not None:
            planet = self._get_planet_by_id(planet_id)
            if planet is None:
                return ValidationResult(is_valid=False, errors=["Planet not found."])

        return self._session.turn_engine.validate_colonize_order(
            self._session.galaxy, fleet, planet
        )

    def can_move_to(self, fleet_id: int, target_hex: HexCoord) -> ValidationResult:
        """Check if a fleet can move to a target hex.

        This validates movement by checking if a path exists.

        Args:
            fleet_id: The fleet to check
            target_hex: The destination hex

        Returns:
            ValidationResult indicating whether the move is valid
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        path = self._session.preview_fleet_path(fleet, target_hex)
        if path is None:
            return ValidationResult(is_valid=False, errors=["No path to target hex."])

        return ValidationResult()

    # --- Colony Pod Queries (PROJ-55) ---

    def get_fleet_remaining_pods(self, fleet_id: int) -> dict:
        """Get remaining colony pods for a fleet (available minus committed).

        PROJ-55: Used by UI to filter colonizable planets by available pod types.

        Args:
            fleet_id: The fleet to check

        Returns:
            Dict mapping planet type string to count of remaining (uncommitted) pods.
            Example: {"ICE_DWARF": 1, "CONTINENTAL": 0}
            Returns empty dict if fleet not found.
        """
        from game.core.registry import get_default_registry_provider
        from game.strategy.validation.colonize_validator import ColonizeValidator

        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return {}

        # Get component registry
        try:
            provider = get_default_registry_provider()
            component_registry = provider.get_components()
        except (RuntimeError, AttributeError, ImportError):
            # Defensive fallback - return empty dict if registry unavailable
            return {}

        # Calculate available and committed pods
        available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)
        committed = ColonizeValidator.get_committed_colony_pods(fleet)

        # Calculate remaining
        remaining = {}
        for planet_type, count in available.items():
            committed_count = committed.get(planet_type, 0)
            remaining_count = count - committed_count
            if remaining_count > 0:
                remaining[planet_type] = remaining_count

        return remaining
