"""Fleet capability calculator - extracted from Fleet class.

PROJ-87 Phase 4: Encapsulates fleet capability queries like space yards,
warp capability, and build type checking.

PROJ-212 Phase 3: Added constructor DI for component_registry.
PROJ-211 Task 2.2: Added DI path via ship._registries.components.
Fallback to global retained until Task 2.3 makes DI required.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


def _get_default_component_registry() -> Dict[str, Any]:
    """Get the default component registry for ability lookups.

    PROJ-211 TEMPORARY: This fallback will be removed in Task 2.3
    after all callers are updated to use DI.
    """
    from game.core.registry import get_default_registry_provider
    return get_default_registry_provider().get_components()


def _get_ship_component_registry(ship: 'ShipInstance') -> Optional[Dict[str, Any]]:
    """Get component registry from a ship's stored registries.

    Args:
        ship: ShipInstance that may have _registries set

    Returns:
        The components dict from ship's registries, or None if not available
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
                If None, tries ship._registries.components, then falls back to global.

        Returns:
            True if ship has a component with SpaceShipyard ability.
        """
        from game.strategy.services.component_inspector import ship_has_ability
        # PROJ-211: Prefer explicit registry, then ship's registries, then global fallback
        registry = component_registry
        if registry is None:
            registry = _get_ship_component_registry(ship)
        if registry is None:
            # PROJ-211 TEMPORARY: Fallback removed in Task 2.3
            registry = _get_default_component_registry()
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
        SpaceShipyard ability (e.g., fleet_space_yard component).
        """
        return self.space_shipyard_count > 0

    @property
    def space_shipyard_count(self) -> int:
        """Count total fleet space yard components across all combat-capable ships."""
        from game.strategy.services.component_inspector import count_ability
        registry = self._get_registry()
        count = 0
        for ship in self._fleet.get_combat_capable_ships():
            count += count_ability(ship, 'SpaceShipyard', registry)
        return count

    def _get_registry(self) -> Dict[str, Any]:
        """Get component registry, falling back to global if not injected.

        PROJ-211: Prefers injected registry. Falls back to global temporarily
        until Task 2.3 makes DI required.

        Returns:
            The component registry for ability lookups.
        """
        if self._component_registry is not None:
            return self._component_registry
        # PROJ-211 TEMPORARY: Fallback removed in Task 2.3
        return _get_default_component_registry()

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
        registry = self._get_registry()
        result = []
        for ship in self._fleet.get_combat_capable_ships():
            if check_ability(ship, ability_name, registry):
                result.append(ship)
        return result

    @staticmethod
    def ship_has_ability(
        ship: 'ShipInstance',
        ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a single ship has the specified ability.

        Args:
            ship: The ShipInstance to check.
            ability_name: Name of the ability to check for.
            component_registry: Optional component registry for ability lookups.
                If None, tries ship._registries.components, then falls back to global.

        Returns:
            True if ship has the ability, False otherwise.
        """
        from game.strategy.services.component_inspector import ship_has_ability
        # PROJ-211: Prefer explicit registry, then ship's registries, then global fallback
        registry = component_registry
        if registry is None:
            registry = _get_ship_component_registry(ship)
        if registry is None:
            # PROJ-211 TEMPORARY: Fallback removed in Task 2.3
            registry = _get_default_component_registry()
        return ship_has_ability(ship, ability_name, registry)
