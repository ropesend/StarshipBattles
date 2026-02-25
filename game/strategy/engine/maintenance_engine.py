"""
MaintenanceEngine - Handles per-tick maintenance costs and scuttling.

PROJ-75 Phase 5: Maintenance System.
PROJ-161: Now per-tick only (100 ticks per turn, 1/100th cost each).

Responsibilities:
- Calculate maintenance cost (5% of total build cost per turn, 1/100th per tick)
- Deduct maintenance costs from empire resource pools
- Scuttle (remove) entities that cannot be maintained (immediately on tick failure)
- Clean up empty fleets after ship scuttles
- Return scuttle events for notification/logging

Processing is one-pass: all entities are evaluated against current resources
in order. Resources consumed by earlier entities reduce availability for later ones,
but scuttled entities do NOT return resources (preventing cascade exploitation).

Called by TurnEngine._process_tick() 100 times per turn.
"""

from dataclasses import dataclass
from typing import List, Dict, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet, PlanetaryFacility
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance

logger = logging.getLogger(__name__)


# Shared maintenance rate used by both MaintenanceEngine and EmpireEconomyCalculator
MAINTENANCE_RATE = 0.05  # 5% per turn


def calculate_maintenance_cost(design_data: Dict, rate: float = MAINTENANCE_RATE) -> Dict[str, float]:
    """Calculate maintenance cost from a design's resource costs.

    Maintenance is a percentage of the total build cost, which is
    the sum of resource_cost across all layers and components.

    Handles two layer formats:
    - Dict format: {"CORE": {"components": [...]}}
    - List format: {"HULL": [{"id": "comp_a", ...}]}

    Args:
        design_data: Design data dict containing layers with components.
        rate: Maintenance rate to apply (default: 5% = 0.05).

    Returns:
        Dict mapping resource type to maintenance cost amount.
    """
    total_build_cost: Dict[str, float] = {}

    for layer in design_data.get('layers', {}).values():
        # Handle both formats: dict with "components" key, or direct list
        if isinstance(layer, dict):
            components = layer.get('components', [])
        elif isinstance(layer, list):
            components = layer
        else:
            continue

        for component in components:
            if not isinstance(component, dict):
                continue
            comp_cost = component.get('resource_cost', {})
            for res, amount in comp_cost.items():
                total_build_cost[res] = total_build_cost.get(res, 0) + amount

    # Apply maintenance rate
    maintenance: Dict[str, float] = {}
    for res, amount in total_build_cost.items():
        maintenance[res] = amount * rate

    return maintenance


@dataclass
class ScuttleEvent:
    """Record of an entity being scuttled due to maintenance failure."""
    empire_id: int
    entity_type: str  # "facility" or "ship"
    entity_name: str
    location: str


class MaintenanceEngine:
    """Engine for processing maintenance costs and scuttling.

    Each tick, every operational facility and every ship must pay
    1/100th of their maintenance (5% of build cost per turn). If the
    empire cannot afford the payment, the entity is immediately scuttled.

    PROJ-161: Per-tick only (legacy full-turn method removed).

    Processing order:
    1. Facilities (all colonies, in colony order)
    2. Ships (all fleets, in fleet order)
    3. Empty fleet cleanup

    Usage:
        engine = MaintenanceEngine()
        # Called 100 times per turn:
        events = engine.process_maintenance_tick(tick, empires)
    """

    def __init__(self):
        """Initialize the maintenance engine."""
        pass

    def process_maintenance_tick(self, tick: int, empires: List) -> List[ScuttleEvent]:
        """Process maintenance for one tick (1/100th of turn).

        PROJ-161: Per-tick maintenance spreads costs across 100 ticks.
        Each call deducts 1/100th of the per-turn maintenance cost.
        Entities that cannot pay are immediately scuttled.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.

        Returns:
            List of ScuttleEvent records for scuttled entities.
        """
        events: List[ScuttleEvent] = []
        for empire in empires:
            events.extend(self._process_empire(empire, tick_fraction=0.01))
        return events

    def _process_empire(self, empire: 'Empire', tick_fraction: float = 1.0) -> List[ScuttleEvent]:
        """Process maintenance for a single empire.

        Args:
            empire: Empire to process.
            tick_fraction: Fraction of per-turn cost to charge (1.0 for full turn,
                          0.01 for per-tick operation).

        Returns:
            List of ScuttleEvent records.
        """
        events: List[ScuttleEvent] = []
        fleets_with_scuttles: set = set()

        # Phase 1: Facility maintenance
        for colony in empire.colonies:
            events.extend(self._process_colony_facilities(colony, empire, tick_fraction))

        # Phase 2: Ship maintenance
        for fleet in list(empire.fleets):  # Copy list since we may remove fleets
            fleet_events = self._process_fleet_ships(fleet, empire, tick_fraction)
            if fleet_events:
                fleets_with_scuttles.add(fleet.id)
            events.extend(fleet_events)

        # Phase 3: Clean up fleets emptied by scuttling only
        self._cleanup_empty_fleets(empire, fleets_with_scuttles)

        return events

    def _process_colony_facilities(
        self, colony: 'Planet', empire: 'Empire', tick_fraction: float = 1.0
    ) -> List[ScuttleEvent]:
        """Process maintenance for all facilities on a colony.

        Iterates facilities in order. Pays for each one if possible,
        scuttles those that can't be paid for.

        Args:
            colony: Colony (planet) with facilities.
            empire: Empire that owns the colony.
            tick_fraction: Fraction of per-turn cost to charge.

        Returns:
            List of ScuttleEvent records.
        """
        events: List[ScuttleEvent] = []
        to_scuttle: List = []

        for facility in colony.facilities:
            if not facility.is_operational:
                continue  # Non-operational facilities are free

            cost = self._calculate_maintenance_cost(facility.design_data, tick_fraction)
            if not cost:
                continue  # No cost - free maintenance

            if empire.has_resources(cost):
                # Pay maintenance
                for res, amount in cost.items():
                    empire.consume_resources(res, amount)
            else:
                # Mark for scuttling
                to_scuttle.append(facility)
                events.append(ScuttleEvent(
                    empire_id=empire.id,
                    entity_type="facility",
                    entity_name=facility.name,
                    location=f"Planet {colony.name}",
                ))
                logger.warning(
                    f"Maintenance failure: scuttling {facility.name} "
                    f"on {colony.name} (Empire {empire.id})"
                )

        # Execute scuttles after iteration (don't modify list during iteration)
        for facility in to_scuttle:
            colony.facilities.remove(facility)

        return events

    def _process_fleet_ships(
        self, fleet: 'Fleet', empire: 'Empire', tick_fraction: float = 1.0
    ) -> List[ScuttleEvent]:
        """Process maintenance for all ships in a fleet.

        Args:
            fleet: Fleet containing ships.
            empire: Empire that owns the fleet.
            tick_fraction: Fraction of per-turn cost to charge.

        Returns:
            List of ScuttleEvent records.
        """
        events: List[ScuttleEvent] = []
        to_scuttle: List = []

        for ship in fleet.ships:
            cost = self._calculate_maintenance_cost(ship.design_data, tick_fraction)
            if not cost:
                continue

            if empire.has_resources(cost):
                for res, amount in cost.items():
                    empire.consume_resources(res, amount)
            else:
                to_scuttle.append(ship)
                events.append(ScuttleEvent(
                    empire_id=empire.id,
                    entity_type="ship",
                    entity_name=ship.name,
                    location=f"Fleet {fleet.id}",
                ))
                logger.warning(
                    f"Maintenance failure: scuttling {ship.name} "
                    f"in Fleet {fleet.id} (Empire {empire.id})"
                )

        # Execute scuttles
        for ship in to_scuttle:
            fleet.ships.remove(ship)

        return events

    def _calculate_maintenance_cost(
        self, design_data: Dict, tick_fraction: float = 1.0
    ) -> Dict[str, float]:
        """Calculate maintenance cost from a design's resource costs.

        Delegates to module-level calculate_maintenance_cost() function,
        then applies tick_fraction to spread costs over multiple ticks.

        Args:
            design_data: Design data dict containing layers with components.
            tick_fraction: Fraction of per-turn cost to charge (1.0 for full turn,
                          0.01 for per-tick operation).

        Returns:
            Dict mapping resource type to maintenance cost amount.
        """
        full_cost = calculate_maintenance_cost(design_data, MAINTENANCE_RATE)
        if tick_fraction == 1.0:
            return full_cost
        return {res: amount * tick_fraction for res, amount in full_cost.items()}

    def _cleanup_empty_fleets(self, empire: 'Empire', fleets_with_scuttles: set) -> None:
        """Remove fleets that became empty due to maintenance scuttling.

        Only removes fleets that had ships scuttled AND now have no ships.
        Pre-existing empty fleets (e.g., newly created, waiting for ships)
        are left alone.

        Args:
            empire: Empire to clean up.
            fleets_with_scuttles: Set of fleet IDs that had ships scuttled.
        """
        to_remove = [
            f for f in empire.fleets
            if f.id in fleets_with_scuttles and len(f.ships) == 0
        ]
        for fleet in to_remove:
            empire.remove_fleet(fleet)
            logger.info(f"Removed empty Fleet {fleet.id} (Empire {empire.id})")
