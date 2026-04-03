"""Fleet capability calculator - extracted from Fleet class.

PROJ-87 Phase 4: Encapsulates fleet capability queries like space yards,
warp capability, and build type checking.

PROJ-212 Phase 3: Added constructor DI for component_registry.
PROJ-211 Task 5.7: Removed fallback to global registry - now requires
ships have _registries set or explicit registry parameter.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


def _get_ship_component_registry(ship: 'ShipInstance') -> Optional[Dict[str, Any]]:
    """Get component registry from a ship's stored registries.

    Args:
        ship: ShipInstance that should have _registries set via DI

    Returns:
        The components dict from ship's registries, or None if not available

    Note:
        As of PROJ-211, all ShipInstance objects are required to have
        _registries set at creation time. This function returns None only
        for backward compatibility during the transition period.
    """
    if hasattr(ship, '_registries') and ship._registries is not None:
        return ship._registries.components
    return None


class FleetCapabilityCalculator:
    """
    Calculates fleet capabilities based on ship composition.

    Handles queries about what the fleet can do:
    - Space shipyard presence
    - Build capabilities by vehicle type
    - Warp point usage capability
    """

    @staticmethod
    def ship_has_spaceyard(
        ship: 'ShipInstance',
        component_registry: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a single ship has a space shipyard component.

        Args:
            ship: The ShipInstance to check.
            component_registry: Optional component registry for ability lookups.
                If None, uses ship._registries.components (required to be set).

        Returns:
            True if ship has a component with SpaceShipyard ability.

        Raises:
            ValueError: If no registry available (ship has no _registries and
                none passed explicitly).
        """
        from game.strategy.services.component_inspector import ship_has_ability
        registry = component_registry
        if registry is None:
            registry = _get_ship_component_registry(ship)
        if registry is None:
            raise ValueError(
                "FleetCapabilityCalculator.ship_has_spaceyard requires a component "
                "registry. Either pass component_registry explicitly or ensure ship "
                "has _registries set via DI."
            )
        return ship_has_ability(ship, 'SpaceShipyard', registry)

    def __init__(
        self,
        fleet: 'Fleet',
        component_registry: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize calculator with fleet reference.

        Args:
            fleet: The Fleet instance to calculate capabilities for.
            component_registry: Component registry for ability lookups.
                Required for instance methods that need registry access.
        """
        self._fleet = fleet
        self._component_registry = component_registry

    @property
    def has_space_shipyard(self) -> bool:
        """
        Check if fleet has an operational space shipyard.

        Returns True if any combat-capable ship has a component with
        SpaceShipyard ability (e.g., space_shipyard component).
        """
        return self.space_shipyard_count > 0

    @property
    def space_shipyard_count(self) -> int:
        """Count total fleet space yard components across all combat-capable ships."""
        from game.strategy.services.component_inspector import count_ability
        combat_ships = self._fleet.get_combat_capable_ships()
        if not combat_ships:
            return 0
        registry = self._get_registry()
        count = 0
        for ship in combat_ships:
            count += count_ability(ship, 'SpaceShipyard', registry)
        return count

    def _get_registry(self) -> Dict[str, Any]:
        """Get component registry from injection or first ship's registries.

        Returns:
            The component registry for ability lookups.

        Raises:
            ValueError: If no registry available (none injected and fleet
                has no ships with _registries set).
        """
        if self._component_registry is not None:
            return self._component_registry
        # Try to get from first ship's registries
        for ship in self._fleet.get_combat_capable_ships():
            ship_registry = _get_ship_component_registry(ship)
            if ship_registry is not None:
                return ship_registry
        raise ValueError(
            "FleetCapabilityCalculator requires a component registry. Either "
            "pass component_registry to constructor or ensure fleet has ships "
            "with _registries set via DI."
        )

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

    def has_ability(self, ability_name: str) -> bool:
        """
        Check if any combat-capable ship in fleet has the specified ability.

        Args:
            ability_name: Name of the ability to check for (e.g., "DestroyPlanet").

        Returns:
            True if any ship has the ability, False otherwise.
        """
        return len(self.ships_with_ability(ability_name)) > 0

    def ships_with_ability(self, ability_name: str) -> List['ShipInstance']:
        """
        Get all combat-capable ships in fleet that have the specified ability.

        Args:
            ability_name: Name of the ability to check for (e.g., "SelfDestruct").

        Returns:
            List of ShipInstance objects that have the ability.
        """
        from game.strategy.services.component_inspector import ship_has_ability as check_ability
        combat_ships = self._fleet.get_combat_capable_ships()
        if not combat_ships:
            return []
        registry = self._get_registry()
        result = []
        for ship in combat_ships:
            if check_ability(ship, ability_name, registry):
                result.append(ship)
        return result

    def list_abilities(self) -> List[str]:
        """
        Get all unique ability names across all combat-capable ships in the fleet.

        Returns:
            List of unique ability names found on any ship in the fleet.
            Returns empty list if fleet has no combat-capable ships.
        """
        from game.strategy.services.component_inspector import list_ship_abilities

        combat_ships = self._fleet.get_combat_capable_ships()
        if not combat_ships:
            return []

        all_abilities: set = set()
        registry = self._get_registry()
        for ship in combat_ships:
            ship_abilities = list_ship_abilities(ship, registry)
            all_abilities.update(ship_abilities)

        return list(all_abilities)
