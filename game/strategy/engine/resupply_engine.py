"""
ResupplyEngine - Fuel Generation and Fleet Resupply

PROJ-74 Phase 3: Engine for processing fuel generation at planetary facilities
and (future) fleet resupply from facilities.

Responsibilities:
- Process per-tick fuel generation at facilities with fuel synthesizers
- Respect max storage capacity on facilities
- Skip non-operational facilities
- Return ResupplyEvent records for logging/UI

Fits into TurnEngine's _process_tick() as Phase 0a (after resource consumption).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING
import logging

from game.core.constants import ResourceType
from game.core.registry import GameRegistries
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)
from game.strategy.interfaces.engines import IResupplyEngine
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

if TYPE_CHECKING:
    from game.strategy.data.planet import PlanetaryFacility


@dataclass
class ResupplyEvent:
    """Record of a resupply operation."""
    facility_name: str
    fuel_generated: float
    fuel_transferred: float = 0.0
    fleet_id: Optional[int] = None


class ResupplyEngine(IResupplyEngine):
    """
    Engine for processing fuel generation and fleet resupply.

    PROJ-74 Phase 3: Handles fuel generation at planetary facilities.
    Future phases add fleet resupply logic.

    Follows existing engine DI pattern (see ResourceManagementEngine).

    Handles:
    - Scanning facility components for ResourceGeneration with resource="fuel"
    - Spreading per-turn generation over 100 ticks
    - Capping fuel at facility max storage capacity
    - Skipping non-operational facilities
    """

    def __init__(self, *, registries: GameRegistries):
        """Initialize the resupply engine.

        Args:
            registries: GameRegistries container. Required - no fallback.

        Raises:
            ValidationException: If registries is None.
        """
        if registries is None:
            raise ValidationException(
                "registries is required for ResupplyEngine",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "ResupplyEngine", "parameter": "registries"}
            )
        self._registries = registries

    def process_fuel_generation(self, tick: int, empires) -> List[ResupplyEvent]:
        """
        Process fuel generation at all facilities across all empires.

        Each facility with a fuel synthesizer (ResourceGeneration with resource="fuel")
        generates 1/100th of its per-turn output each tick. Fuel is added to the
        facility's resource_levels, capped at max storage capacity.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of ResupplyEvent records for generation that occurred
        """
        events = []

        for empire in empires:
            for colony in empire.colonies:
                for facility in colony.facilities:
                    event = self._process_facility_generation(facility)
                    if event is not None:
                        events.append(event)

        return events

    def _process_facility_generation(self, facility: 'PlanetaryFacility') -> Optional[ResupplyEvent]:
        """
        Process fuel generation for a single facility.

        Args:
            facility: The PlanetaryFacility to process

        Returns:
            ResupplyEvent if fuel was generated, None otherwise
        """
        if not facility.is_operational:
            return None

        # Find total fuel generation rate from all components
        fuel_gen_rate = self._get_fuel_generation_rate(facility)
        if fuel_gen_rate <= 0:
            return None

        # Calculate per-tick generation (spread over 100 ticks)
        tick_generation = fuel_gen_rate / 100.0

        # Add fuel respecting max capacity
        overflow = facility.add_fuel(tick_generation, self._registries)
        actual_generated = tick_generation - overflow

        if actual_generated <= 0:
            return None

        return ResupplyEvent(
            facility_name=facility.name,
            fuel_generated=actual_generated,
        )

    def _get_fuel_generation_rate(self, facility: 'PlanetaryFacility') -> float:
        """
        Calculate total fuel generation rate from facility components.

        Scans all components in the facility's design_data for ResourceGeneration
        abilities with resource type 'fuel' and sums their amounts.

        Args:
            facility: The PlanetaryFacility to inspect

        Returns:
            Total fuel generation rate per turn
        """
        total_rate = 0.0
        registry = self._registries.components

        for layer_data in facility.design_data.get("layers", {}).values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                comp_id = comp.get("id") if isinstance(comp, dict) else comp
                comp_def = registry.get(comp_id)
                if not comp_def:
                    continue

                abilities = getattr(comp_def, 'abilities', {}) or {}
                for gen_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceGeneration'):
                    if gen_data.get('resource') == ResourceType.FUEL:
                        total_rate += gen_data.get('amount', 0.0)

        return total_rate

    def process_fleet_resupply(self, tick: int, empires, galaxy) -> List[ResupplyEvent]:
        """
        Process fuel transfer from facilities to fleets at co-located planets.

        For each fleet, finds planets at the fleet's location. Only the planet
        owner's fleets receive fuel (no allied resupply). Fuel is distributed
        across fleet ships to equalize effective range.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial lookup

        Returns:
            List of ResupplyEvent records for transfers that occurred
        """
        events: List[ResupplyEvent] = []

        for empire in empires:
            for fleet in empire.fleets:
                planets = galaxy.get_planets_at_global_hex(fleet.location)

                for planet in planets:
                    if planet.owner_id != fleet.owner_id:
                        continue  # Owner priority only

                    for facility in planet.facilities:
                        if not facility.is_operational:
                            continue

                        available = facility.get_fuel_storage()
                        if available <= 0:
                            continue

                        distribution = self._calculate_fuel_distribution(
                            fleet, available
                        )
                        if not distribution:
                            continue

                        total_transferred = self._transfer_fuel(
                            distribution, available, facility
                        )

                        if total_transferred > 0:
                            events.append(ResupplyEvent(
                                facility_name=facility.name,
                                fuel_generated=0,
                                fuel_transferred=total_transferred,
                                fleet_id=fleet.id,
                            ))

        return events

    def _calculate_fuel_distribution(
        self, fleet, available_fuel: float
    ) -> Dict:
        """
        Calculate fuel distribution to equalize range across all fleet ships.

        Ships with higher fuel consumption per hex receive proportionally more
        fuel so that all ships can travel the same number of hexes.

        Args:
            fleet: Fleet to distribute fuel to
            available_fuel: Total fuel available from the facility

        Returns:
            Dict mapping ship -> fuel amount to transfer
        """
        ships = [s for s in fleet.ships if s.is_combat_capable()]
        if not ships:
            return {}

        total_cost_per_hex = sum(s.get_all_resource_costs_per_hex().get(ResourceType.FUEL, 0) for s in ships)
        if total_cost_per_hex <= 0:
            return {}

        current_total = sum(s.get_current_resource(ResourceType.FUEL) for s in ships)
        max_range = (available_fuel + current_total) / total_cost_per_hex

        distribution: Dict = {}
        for ship in ships:
            target = ship.get_all_resource_costs_per_hex().get(ResourceType.FUEL, 0) * max_range
            capacity = ship.get_resource_capacity(ResourceType.FUEL)
            target = min(target, capacity)
            deficit = target - ship.get_current_resource(ResourceType.FUEL)
            if deficit > 0:
                distribution[ship] = deficit

        return distribution

    def _transfer_fuel(
        self, distribution: Dict, available: float, facility
    ) -> float:
        """
        Execute fuel transfer from facility to ships.

        Args:
            distribution: Dict mapping ship -> fuel amount
            available: Total fuel available in facility
            facility: PlanetaryFacility to withdraw fuel from

        Returns:
            Total fuel actually transferred
        """
        total_transferred = 0.0

        for ship, amount in distribution.items():
            actual = min(amount, available - total_transferred)
            if actual <= 0:
                break
            transferred = ship.resupply(ResourceType.FUEL, actual)
            total_transferred += transferred

        facility.withdraw_fuel(total_transferred)
        return total_transferred
