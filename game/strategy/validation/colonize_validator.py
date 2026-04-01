"""
ColonizeValidator - Validates COLONIZE orders for fleets.

PROJ-36: Extracted from TurnEngine to centralize validation.
PROJ-55: Added colony pod detection and chain validation.
Phase 3: Drop pods are constructed items carried in ship.carried_items.
         Colony ships need ColonizePlanet ability for planet type eligibility.
         Drop pods are universal (work on any planet type).
"""
from typing import Dict, Any, Optional, TYPE_CHECKING
from game.core.validation import ValidationResult
from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy

from game.strategy.data.planet import Planet


class ColonizeValidator:
    """Validates COLONIZE orders for fleets.

    Colony ships need:
    1. ColonizePlanet ability matching the target planet type (on a ship component)
    2. A drop pod in carried_items (any ship in fleet)

    Drop pods are universal — any drop pod works on any planet type.
    The colony ship's ColonizePlanet ability determines planet eligibility.
    """

    @staticmethod
    def validate(
        galaxy: 'Galaxy',
        fleet: 'Fleet',
        target_planet: Optional['Planet'],
        component_registry: Optional[Dict[str, Any]] = None,
        skip_chain_check: bool = False
    ) -> ValidationResult:
        """Validate if a fleet can colonize a planet."""
        if not fleet:
            return ValidationResult.error("Fleet does not exist.")

        all_planets_at_hex = list(galaxy.get_planets_at_global_hex(fleet.location))

        # PROJ-139: Check zone registry for multi-hex planets
        zone_objects = galaxy.get_zones_at_global_hex(fleet.location)
        for zone_obj in zone_objects:
            if isinstance(zone_obj, Planet) and zone_obj not in all_planets_at_hex:
                all_planets_at_hex.append(zone_obj)

        valid_candidates = [p for p in all_planets_at_hex if p.owner_id is None]

        if target_planet is None:
            # "Any Planet"
            if not valid_candidates:
                return ValidationResult.error(
                    "No colonizable planets at this location.",
                    code="NO_CANDIDATES"
                )

            # Check fleet has a drop pod
            if not ColonizeValidator.fleet_has_drop_pod(fleet):
                return ValidationResult.error(
                    "No drop pod carried by any ship in fleet.",
                    code="NO_COLONY_POD"
                )

            # Check chain limits
            if not skip_chain_check:
                available = ColonizeValidator.count_drop_pods(fleet)
                committed = ColonizeValidator.count_committed_colonize_orders(fleet)
                if committed >= available:
                    return ValidationResult.error(
                        "All drop pods already assigned to colonize orders.",
                        code="COLONY_POD_EXHAUSTED"
                    )

            return ValidationResult.success()

        else:
            # Specific Planet
            if target_planet.owner_id is not None:
                return ValidationResult.error(
                    f"Planet {target_planet.name} is already owned.",
                    code="ALREADY_OWNED"
                )

            if target_planet not in valid_candidates:
                return ValidationResult.error(
                    f"Planet {target_planet.name} is not at fleet location.",
                    code="WRONG_LOCATION"
                )

            # Check fleet has a drop pod
            if not ColonizeValidator.fleet_has_drop_pod(fleet):
                return ValidationResult.error(
                    "No drop pod carried by any ship in fleet.",
                    code="NO_COLONY_POD"
                )

            # Check chain limits
            if not skip_chain_check:
                available = ColonizeValidator.count_drop_pods(fleet)
                committed = ColonizeValidator.count_committed_colonize_orders(fleet)
                if committed >= available:
                    return ValidationResult.error(
                        "All drop pods already assigned to colonize orders.",
                        code="COLONY_POD_EXHAUSTED"
                    )

            return ValidationResult.success()

    @staticmethod
    def fleet_has_drop_pod(fleet: 'Fleet') -> bool:
        """Check if any ship in the fleet carries a drop pod."""
        for ship in fleet.ships:
            for item in getattr(ship, 'carried_items', []):
                if item.get('vehicle_type') == 'drop_pod':
                    return True
        return False

    @staticmethod
    def count_drop_pods(fleet: 'Fleet') -> int:
        """Count total drop pods across all ships in the fleet."""
        count = 0
        for ship in fleet.ships:
            for item in getattr(ship, 'carried_items', []):
                if item.get('vehicle_type') == 'drop_pod':
                    count += 1
        return count

    @staticmethod
    def find_ship_with_drop_pod(fleet: 'Fleet') -> tuple:
        """Find a ship carrying a drop pod and return (ship, item_index).

        Returns:
            Tuple of (ship, index) or (None, -1) if not found.
        """
        for ship in fleet.ships:
            for i, item in enumerate(getattr(ship, 'carried_items', [])):
                if item.get('vehicle_type') == 'drop_pod':
                    return ship, i
        return None, -1

    @staticmethod
    def count_committed_colonize_orders(fleet: 'Fleet') -> int:
        """Count COLONIZE orders already in the fleet's order queue."""
        count = 0
        for order in fleet.orders:
            if order.type == OrderType.COLONIZE:
                count += 1
        return count

    # Legacy compatibility aliases
    @staticmethod
    def get_available_colony_pods(fleet: 'Fleet', component_registry=None) -> Dict[str, int]:
        """Legacy: returns drop pod count as {'drop_pod': N}."""
        return {'drop_pod': ColonizeValidator.count_drop_pods(fleet)}

    @staticmethod
    def fleet_has_colony_pod(fleet: 'Fleet', planet_type_str: str = None) -> bool:
        """Legacy: check for drop pod (planet type ignored — pods are universal)."""
        return ColonizeValidator.fleet_has_drop_pod(fleet)

    @staticmethod
    def get_committed_colony_pods(fleet: 'Fleet') -> Dict[str, int]:
        """Legacy: returns committed count as {'drop_pod': N}."""
        return {'drop_pod': ColonizeValidator.count_committed_colonize_orders(fleet)}
