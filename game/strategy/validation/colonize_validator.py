"""
ColonizeValidator - Validates COLONIZE orders for fleets.

PROJ-36: Extracted from TurnEngine to centralize validation.
PROJ-55: Added colony pod detection and chain validation.
"""
from typing import Dict, Any, Optional
from game.core.validation import ValidationResult
from game.strategy.services.component_inspector import iterate_design_components


class ColonizeValidator:
    """Validates COLONIZE orders for fleets."""

    @staticmethod
    def validate(
        galaxy,
        fleet,
        target_planet,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate if a fleet can colonize a specific planet.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting to colonize
            target_planet: The Planet object or None for 'Any'
            component_registry: Optional component registry dict for pod lookup.
                               If provided, validates colony pod requirements.

        Returns:
            ValidationResult with error codes:
            - NO_CANDIDATES: No colonizable planets at location
            - ALREADY_OWNED: Target planet is already owned
            - WRONG_LOCATION: Target planet is not at fleet location
            - NO_COLONY_POD: No matching colony pod for planet type
            - COLONY_POD_EXHAUSTED: All matching pods already committed
        """
        # 1. Base Validation: Fleet must exist
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet does not exist."])

        # 2. Get System/Location Context - Use O(1) spatial index
        # Get all planets at the fleet's global hex location
        all_planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        valid_candidates = [p for p in all_planets_at_hex if p.owner_id is None]

        # 3. Check Logic
        if target_planet is None:
            # "Any Planet"
            if not valid_candidates:
                return ValidationResult(is_valid=False, errors=["No colonizable planets at this location."], error_code="NO_CANDIDATES")
            return ValidationResult()

        else:
            # Specific Planet
            if target_planet.owner_id is not None:
                return ValidationResult(is_valid=False, errors=[f"Planet {target_planet.name} is already owned."], error_code="ALREADY_OWNED")

            # Check if planet is in valid candidates (verifies location)
            # We strictly check reference equality or ID equality if we had IDs
            if target_planet not in valid_candidates:
                # Determine detailed reason for better feedback
                # If owner is none (checked above), then it must be location.
                return ValidationResult(is_valid=False, errors=[f"Planet {target_planet.name} is not at fleet location."], error_code="WRONG_LOCATION")

            # 4. Check for colony pod (PROJ-55)
            if component_registry is not None:
                planet_type_str = target_planet.planet_type.name

                # Check if fleet has a matching colony pod
                ship_with_pod = ColonizeValidator.find_ship_with_colony_pod(
                    fleet, planet_type_str, component_registry
                )

                if ship_with_pod is None:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"No ship in fleet has {planet_type_str} colony pod"],
                        error_code="NO_COLONY_POD"
                    )

                # Check chain limits - ensure not over-committed
                available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)
                committed = ColonizeValidator.get_committed_colony_pods(fleet)

                available_count = available.get(planet_type_str, 0)
                committed_count = committed.get(planet_type_str, 0)

                if committed_count >= available_count:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"All {planet_type_str} colony pods already assigned"],
                        error_code="COLONY_POD_EXHAUSTED"
                    )

            return ValidationResult()

    @staticmethod
    def find_ship_with_colony_pod(
        fleet,
        planet_type_str: str,
        component_registry: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Find a ship in the fleet with a colony pod matching the planet type.

        Args:
            fleet: The Fleet object
            planet_type_str: Planet type string (e.g., "ICE_DWARF")
            component_registry: Component registry dict for ability lookup

        Returns:
            The first ship with a matching colony pod, or None if not found.
        """
        for ship in fleet.ships:
            design_data = getattr(ship, 'design_data', {})

            for _comp_entry, _comp_def, abilities in iterate_design_components(
                design_data, component_registry
            ):
                if 'ColonizePlanet' in abilities:
                    ability_data = abilities['ColonizePlanet']
                    # Handle both string shorthand and dict format
                    if isinstance(ability_data, str):
                        pod_planet_type = ability_data
                    elif isinstance(ability_data, dict):
                        pod_planet_type = ability_data.get('planet_type', '')
                    else:
                        continue

                    if pod_planet_type == planet_type_str:
                        return ship

        return None

    @staticmethod
    def get_available_colony_pods(
        fleet,
        component_registry: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Count available colony pods in the fleet by planet type.

        Args:
            fleet: The Fleet object
            component_registry: Component registry dict for ability lookup

        Returns:
            Dict mapping planet type string to count of available pods.
            Example: {"ICE_DWARF": 1, "CONTINENTAL": 2}
        """
        pod_counts: Dict[str, int] = {}

        for ship in fleet.ships:
            design_data = getattr(ship, 'design_data', {})

            for _comp_entry, _comp_def, abilities in iterate_design_components(
                design_data, component_registry
            ):
                if 'ColonizePlanet' in abilities:
                    ability_data = abilities['ColonizePlanet']
                    # Handle both string shorthand and dict format
                    if isinstance(ability_data, str):
                        pod_planet_type = ability_data
                    elif isinstance(ability_data, dict):
                        pod_planet_type = ability_data.get('planet_type', '')
                    else:
                        continue

                    pod_counts[pod_planet_type] = pod_counts.get(pod_planet_type, 0) + 1

        return pod_counts

    @staticmethod
    def get_committed_colony_pods(fleet) -> Dict[str, int]:
        """
        Count colony pods committed to existing COLONIZE orders.

        Args:
            fleet: The Fleet object with orders list

        Returns:
            Dict mapping planet type string to count of committed pods.
            Example: {"ICE_DWARF": 2, "CONTINENTAL": 1}
        """
        from game.strategy.data.fleet import OrderType

        committed: Dict[str, int] = {}

        for order in getattr(fleet, 'orders', []):
            if order.type == OrderType.COLONIZE and order.target is not None:
                # Get planet type from the target planet
                target = order.target
                if hasattr(target, 'planet_type'):
                    planet_type_str = target.planet_type.name
                    committed[planet_type_str] = committed.get(planet_type_str, 0) + 1

        return committed
