"""Fleet capability calculator - extracted from Fleet class.

PROJ-87 Phase 4: Encapsulates fleet capability queries like space yards,
warp capability, and build type checking.
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


class FleetCapabilityCalculator:
    """
    Calculates fleet capabilities based on ship composition.

    Handles queries about what the fleet can do:
    - Space shipyard presence
    - Build capabilities by vehicle type
    - Warp point usage capability
    """

    @staticmethod
    def ship_has_spaceyard(ship: 'ShipInstance') -> bool:
        """
        Check if a single ship has a space shipyard component.

        Args:
            ship: The ShipInstance to check.

        Returns:
            True if ship has a component with SpaceShipyard ability.
        """
        design_data = ship.design_data
        for layer_data in design_data.get("layers", {}).values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                if isinstance(comp, dict):
                    if comp.get("id") == "fleet_space_yard":
                        return True
                    if "SpaceShipyard" in comp.get("abilities", {}):
                        return True
        return False

    def __init__(self, fleet: 'Fleet'):
        """
        Initialize calculator with fleet reference.

        Args:
            fleet: The Fleet instance to calculate capabilities for.
        """
        self._fleet = fleet

    @property
    def has_space_shipyard(self) -> bool:
        """
        Check if fleet has an operational space shipyard.

        Returns True if any combat-capable ship has a component with
        SpaceShipyard ability (e.g., fleet_space_yard component).
        """
        return self.space_shipyard_count > 0

    @property
    def space_shipyard_count(self) -> int:
        """Count total fleet space yard components across all combat-capable ships."""
        count = 0
        for ship in self._fleet.get_combat_capable_ships():
            design_data = ship.design_data
            for layer_data in design_data.get("layers", {}).values():
                if not isinstance(layer_data, list):
                    continue
                for comp in layer_data:
                    if isinstance(comp, dict):
                        if comp.get("id") == "fleet_space_yard":
                            count += 1
                        elif "SpaceShipyard" in comp.get("abilities", {}):
                            count += 1
        return count

    def can_build_type(self, vehicle_type: str, galaxy: Any = None) -> bool:
        """
        Check if fleet can build the specified vehicle type.

        Args:
            vehicle_type: Type of vehicle ("ship", "fighter", "satellite", "complex")
            galaxy: Galaxy instance for planet proximity checks (required for complexes)

        Returns:
            True if fleet can build the given vehicle type.
        """
        if not self.has_space_shipyard:
            return False

        vehicle_lower = vehicle_type.lower()

        # Ships, fighters, and satellites can always be built if we have a yard
        if vehicle_lower in ("ship", "fighter", "satellite"):
            return True

        # Complexes require being at the same hex as a planet
        if vehicle_lower == "complex":
            if galaxy is None:
                return False
            # Check if there's a planet at our location
            planets_at_hex = galaxy.get_planets_at_global_hex(self._fleet.location)
            return len(planets_at_hex) > 0

        return False

    def can_use_warp(self) -> bool:
        """
        Check if ALL ships in fleet can use warp points.

        A fleet can only use warp points if every combat-capable ship has
        a WarpJump ability with max_tonnage >= that ship's mass.

        Returns:
            True if all combat-capable ships are warp-capable, False otherwise.
            Returns False if fleet has no combat-capable ships.
        """
        # INTENTIONAL LATE IMPORT: Query operation, service encapsulates warp logic
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        combat_ships = self._fleet.get_combat_capable_ships()
        if not combat_ships:
            return False

        for ship in combat_ships:
            if not ShipStatsCalculator.has_warp_capability(ship):
                return False
        return True

    def get_warp_limiting_ship(self) -> Optional['ShipInstance']:
        """
        Get the ship that prevents the fleet from using warp, if any.

        Returns:
            The first ship without warp capability, or None if all ships are warp-capable.
        """
        # INTENTIONAL LATE IMPORT: Query operation, service encapsulates warp logic
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        for ship in self._fleet.get_combat_capable_ships():
            if not ShipStatsCalculator.has_warp_capability(ship):
                return ship
        return None
