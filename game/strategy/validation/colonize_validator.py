"""
ColonizeValidator - Validates COLONIZE orders for fleets.

PROJ-36: Extracted from TurnEngine to centralize validation.
PROJ-55: Added colony pod detection and chain validation.
PROJ-127: Extracted _iterate_colony_pods helper to reduce duplication.
Phase 2: Colony pods are now cargo items, not ship components.
         Ships are reusable after colonization.
"""
from typing import Dict, Any, Iterator, Optional, Tuple, TYPE_CHECKING
from game.core.validation import ValidationResult
from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy

from game.strategy.data.planet import Planet
from game.core.protocols import is_planet


COLONY_POD_PREFIX = "colony_pod_"


def _iterate_colony_pods_in_cargo(
    fleet: 'Fleet',
) -> Iterator[Tuple[str, str]]:
    """Iterate over colony pods in fleet cargo.

    Scans all ships' cargo_contents for items starting with "colony_pod_".
    Yields (cargo_type, planet_type_str) tuples.

    Args:
        fleet: The Fleet object

    Yields:
        Tuple of (cargo_type string, planet_type string in UPPER_CASE).
        Example: ("colony_pod_continental", "CONTINENTAL")
    """
    for ship in fleet.ships:
        for cargo_type, amount in ship.cargo_contents.items():
            if cargo_type.startswith(COLONY_POD_PREFIX) and amount > 0:
                planet_type = cargo_type[len(COLONY_POD_PREFIX):].upper()
                yield cargo_type, planet_type


class ColonizeValidator:
    """Validates COLONIZE orders for fleets."""

    @staticmethod
    def validate(
        galaxy: 'Galaxy',
        fleet: 'Fleet',
        target_planet: Optional['Planet'],
        component_registry: Optional[Dict[str, Any]] = None,
        skip_chain_check: bool = False
    ) -> ValidationResult:
        """
        Validate if a fleet can colonize a specific planet.

        Phase 2: Colony pod detection is now cargo-based. The component_registry
        parameter is kept for API compatibility but is no longer needed for pod
        detection. Pods are checked via fleet cargo contents.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting to colonize
            target_planet: The Planet object or None for 'Any'
            component_registry: Kept for API compatibility. Not used for pod lookup.
            skip_chain_check: If True, skip chain exhaustion check. Use during
                             execution (we're processing the order, not adding it).

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
            return ValidationResult.error("Fleet does not exist.")

        # 2. Get System/Location Context - Use O(1) spatial index
        # Get all planets at the fleet's global hex location
        all_planets_at_hex = list(galaxy.get_planets_at_global_hex(fleet.location))

        # PROJ-139: Also check zone registry for multi-hex planets (Dyson Spheres)
        # Fleet may be in a planet's zone but not at its center
        zone_objects = galaxy.get_zones_at_global_hex(fleet.location)
        for zone_obj in zone_objects:
            # Check if zone object is a planet
            if isinstance(zone_obj, Planet) and zone_obj not in all_planets_at_hex:
                all_planets_at_hex.append(zone_obj)

        valid_candidates = [p for p in all_planets_at_hex if p.owner_id is None]

        # 3. Check Logic
        if target_planet is None:
            # "Any Planet"
            if not valid_candidates:
                return ValidationResult.error(
                    "No colonizable planets at this location.",
                    code="NO_CANDIDATES"
                )

            # Phase 2: Check if ANY candidate matches available cargo pods
            available = ColonizeValidator.get_available_colony_pods(fleet)

            # Get committed pods by type (skip during execution)
            committed = ColonizeValidator.get_committed_colony_pods(fleet) if not skip_chain_check else {}

            # Check if any valid candidate planet matches an available (uncommitted) pod
            found_match = False
            for candidate in valid_candidates:
                # Duck typing: check for planet_type attribute (works with mocks too)
                if hasattr(candidate, 'planet_type') and candidate.planet_type is not None:
                    planet_type_str = candidate.planet_type.name
                    available_count = available.get(planet_type_str, 0)
                    committed_count = committed.get(planet_type_str, 0)
                    if available_count > committed_count:
                        found_match = True
                        break

            if not found_match:
                return ValidationResult.error(
                    "No matching colony pod for any planet at this location.",
                    code="NO_COLONY_POD"
                )

            return ValidationResult.success()

        else:
            # Specific Planet
            if target_planet.owner_id is not None:
                return ValidationResult.error(
                    f"Planet {target_planet.name} is already owned.",
                    code="ALREADY_OWNED"
                )

            # Check if planet is in valid candidates (verifies location)
            if target_planet not in valid_candidates:
                return ValidationResult.error(
                    f"Planet {target_planet.name} is not at fleet location.",
                    code="WRONG_LOCATION"
                )

            # 4. Check for colony pod in cargo (Phase 2)
            planet_type_str = target_planet.planet_type.name

            if not ColonizeValidator.fleet_has_colony_pod(fleet, planet_type_str):
                return ValidationResult.error(
                    f"No ship in fleet has {planet_type_str} colony pod",
                    code="NO_COLONY_POD"
                )

            # Check chain limits - ensure not over-committed
            if not skip_chain_check:
                available = ColonizeValidator.get_available_colony_pods(fleet)
                committed = ColonizeValidator.get_committed_colony_pods(fleet)

                available_count = available.get(planet_type_str, 0)
                committed_count = committed.get(planet_type_str, 0)

                if committed_count >= available_count:
                    return ValidationResult.error(
                        f"All {planet_type_str} colony pods already assigned",
                        code="COLONY_POD_EXHAUSTED"
                    )

            return ValidationResult.success()

    @staticmethod
    def fleet_has_colony_pod(
        fleet: 'Fleet',
        planet_type_str: str,
    ) -> bool:
        """
        Check if any ship in the fleet has a colony pod matching the planet type
        in its cargo.

        Phase 2: Replaces find_ship_with_colony_pod. Returns bool instead of
        ship reference since ships are no longer consumed.

        Args:
            fleet: The Fleet object
            planet_type_str: Planet type string (e.g., "ICE_DWARF")

        Returns:
            True if the fleet has a matching colony pod in cargo, False otherwise.
        """
        for _cargo_type, pod_planet_type in _iterate_colony_pods_in_cargo(fleet):
            if pod_planet_type == planet_type_str:
                return True
        return False

    @staticmethod
    def get_available_colony_pods(
        fleet: 'Fleet',
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Count available colony pods in the fleet by planet type.

        Phase 2: Reads from fleet cargo instead of component abilities.
        The component_registry parameter is kept for API compatibility but
        is no longer used.

        Args:
            fleet: The Fleet object
            component_registry: Kept for API compatibility. Not used.

        Returns:
            Dict mapping planet type string to count of available pods.
            Example: {"ICE_DWARF": 1, "CONTINENTAL": 2}
        """
        pod_counts: Dict[str, int] = {}

        for _cargo_type, pod_planet_type in _iterate_colony_pods_in_cargo(fleet):
            pod_counts[pod_planet_type] = pod_counts.get(pod_planet_type, 0) + 1

        return pod_counts

    @staticmethod
    def get_committed_colony_pods(fleet: 'Fleet') -> Dict[str, int]:
        """
        Count colony pods committed to existing COLONIZE orders.

        Args:
            fleet: The Fleet object with orders list

        Returns:
            Dict mapping planet type string to count of committed pods.
            Example: {"ICE_DWARF": 2, "CONTINENTAL": 1}
        """
        committed: Dict[str, int] = {}

        for order in fleet.orders:
            if order.type == OrderType.COLONIZE and order.target is not None:
                # Get planet type from the target planet
                target = order.target
                # is_planet() uses duck typing, works with test mocks
                if is_planet(target) and target.planet_type is not None:
                    planet_type_str = target.planet_type.name
                    committed[planet_type_str] = committed.get(planet_type_str, 0) + 1

        return committed
