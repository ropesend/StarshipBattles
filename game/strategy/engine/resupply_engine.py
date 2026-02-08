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
from typing import List, Optional, TYPE_CHECKING

from game.core.logger import log_info
from game.core.registry import GameRegistries
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
            TypeError: If registries is None.
        """
        if registries is None:
            raise TypeError("registries is required for ResupplyEngine")
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
                    if gen_data.get('resource') == 'fuel':
                        total_rate += gen_data.get('amount', 0.0)

        return total_rate

    def process_fleet_resupply(self, tick: int, empires, galaxy) -> List[ResupplyEvent]:
        """
        Process fuel transfer from facilities to fleets.

        PROJ-74 Phase 4: Placeholder for fleet resupply logic.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial lookup

        Returns:
            List of ResupplyEvent records for transfers that occurred
        """
        # Phase 4 will implement this
        return []
