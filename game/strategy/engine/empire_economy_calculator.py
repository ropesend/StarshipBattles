"""
EmpireEconomyCalculator - Aggregates empire-wide production and expense data.

PROJ-99 Phase 1: Pure strategy-layer class that calculates production from
facilities, maintenance from facilities and ships, and provides a snapshot
of the empire economy.

This is a read-only calculation - it doesn't modify any game state.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

from game.core.constants import PLANET_RESOURCES

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
from game.core.registry import GameRegistries
from game.strategy.engine.maintenance_engine import (
    MAINTENANCE_RATE,
    calculate_maintenance_cost,
)
from game.strategy.engine.harvesting_engine import get_harvester_info


@dataclass
class EmpireEconomySnapshot:
    """Snapshot of empire economic state.

    Contains aggregated production and expense data for the empire.
    All fields are Dict[str, float] mapping resource type to amount.
    Default factory ensures each can be instantiated empty.
    """

    # Production sources
    colony_production: Dict[str, float] = field(default_factory=dict)
    ship_production: Dict[str, float] = field(default_factory=dict)
    trade_production: Dict[str, float] = field(default_factory=dict)
    tribute_production: Dict[str, float] = field(default_factory=dict)
    mining_production: Dict[str, float] = field(default_factory=dict)
    total_production: Dict[str, float] = field(default_factory=dict)

    # Expense categories
    tribute_expenses: Dict[str, float] = field(default_factory=dict)
    maintenance_expenses: Dict[str, float] = field(default_factory=dict)
    construction_expenses: Dict[str, float] = field(default_factory=dict)
    total_expenses: Dict[str, float] = field(default_factory=dict)

    # Treasury state
    net_resources: Dict[str, float] = field(default_factory=dict)
    current_storage: Dict[str, float] = field(default_factory=dict)
    max_storage: Dict[str, float] = field(default_factory=dict)


class EmpireEconomyCalculator:
    """Calculator for empire-wide production and expense aggregation.

    Usage:
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
        )
        calculator = EmpireEconomyCalculator(registries=registries)
        snapshot = calculator.calculate(empire)
        # Access snapshot.colony_production, snapshot.maintenance_expenses, etc.

    Replicates formulas from:
    - HarvestingEngine: base_harvest_rate * planet_quality
    - MaintenanceEngine: 5% of total resource_cost
    """

    # Use shared MAINTENANCE_RATE from maintenance_engine module

    def __init__(self, *, registries: Optional[GameRegistries] = None) -> None:
        """Initialize the calculator.

        Args:
            registries: Optional GameRegistries for resolving component
                       abilities from plain component IDs in design_data.
        """
        self._registries: Optional[GameRegistries] = registries

    def calculate(self, empire: 'Empire') -> EmpireEconomySnapshot:
        """Calculate complete economic snapshot for an empire.

        Args:
            empire: Empire object with colonies, fleets, resource_pool, max_storage.

        Returns:
            EmpireEconomySnapshot with all production and expense data.
        """
        snapshot = EmpireEconomySnapshot()

        # Production aggregation
        snapshot.colony_production = self._aggregate_colony_production(empire)

        # Placeholder production sources (future implementation)
        zero_resources = {r: 0.0 for r in PLANET_RESOURCES}
        snapshot.ship_production = zero_resources.copy()
        snapshot.trade_production = zero_resources.copy()
        snapshot.tribute_production = zero_resources.copy()
        snapshot.mining_production = zero_resources.copy()

        # Total production = colony production only for now
        snapshot.total_production = snapshot.colony_production.copy()

        # Expense aggregation
        snapshot.maintenance_expenses = self._aggregate_maintenance(empire)

        # Placeholder expense categories (future implementation)
        snapshot.tribute_expenses = zero_resources.copy()
        snapshot.construction_expenses = zero_resources.copy()

        # Total expenses = maintenance only for now
        snapshot.total_expenses = snapshot.maintenance_expenses.copy()

        # Net resources per turn
        snapshot.net_resources = {}
        for r in PLANET_RESOURCES:
            prod = snapshot.total_production.get(r, 0.0)
            exp = snapshot.total_expenses.get(r, 0.0)
            snapshot.net_resources[r] = prod - exp

        # Current treasury state
        snapshot.current_storage = empire.resource_pool.copy()
        snapshot.max_storage = empire.max_storage.copy()

        return snapshot

    def _aggregate_colony_production(self, empire: 'Empire') -> Dict[str, float]:
        """Calculate total production from all colony facilities.

        Scans colonies -> facilities -> components for ResourceHarvester abilities.
        Checks inline abilities first, then falls back to registry lookup.
        Production = base_harvest_rate * planet_resource_quality

        Args:
            empire: Empire with colonies attribute.

        Returns:
            Dict mapping resource type to total production per turn.
        """
        totals = {r: 0.0 for r in PLANET_RESOURCES}

        for colony in empire.colonies:
            for facility in colony.facilities:
                # Skip non-operational facilities
                if not facility.is_operational:
                    continue

                design_data = facility.design_data
                layers = design_data.get('layers', {})

                for layer_data in layers.values():
                    # Only handle list-format layers
                    if not isinstance(layer_data, list):
                        continue

                    for comp in layer_data:
                        harvester = get_harvester_info(comp, self._registries)
                        if harvester is None:
                            continue

                        resource_type = harvester.get('resource_type', '')
                        base_rate = harvester.get('base_harvest_rate', 0.0)

                        if not resource_type or base_rate <= 0:
                            continue

                        # Get planet quality for this resource
                        resource_data = colony.resources.get(resource_type, {})
                        quality = resource_data.get('quality', 0.0)

                        # Accumulate production
                        production = base_rate * quality
                        if resource_type in totals:
                            totals[resource_type] += production

        return totals

    def _aggregate_maintenance(self, empire: 'Empire') -> Dict[str, float]:
        """Calculate total maintenance costs for facilities and ships.

        Maintenance is 5% of the sum of all resource_cost values.

        Args:
            empire: Empire with colonies and fleets.

        Returns:
            Dict mapping resource type to total maintenance cost per turn.
        """
        totals = {r: 0.0 for r in PLANET_RESOURCES}

        # Facility maintenance
        for colony in empire.colonies:
            for facility in colony.facilities:
                # Skip non-operational facilities
                if not facility.is_operational:
                    continue

                design_data = facility.design_data
                cost = self._calculate_maintenance_cost(design_data)
                for r, amount in cost.items():
                    if r in totals:
                        totals[r] += amount

        # Ship maintenance
        for fleet in empire.fleets:
            for ship in fleet.ships:
                design_data = ship.design_data
                cost = self._calculate_maintenance_cost(design_data)
                for r, amount in cost.items():
                    if r in totals:
                        totals[r] += amount

        return totals

    def _calculate_maintenance_cost(self, design_data: Dict) -> Dict[str, float]:
        """Calculate maintenance cost from a design's resource costs.

        Delegates to shared calculate_maintenance_cost() function.

        Args:
            design_data: Design data dict containing layers with components.

        Returns:
            Dict mapping resource type to maintenance cost amount.
        """
        return calculate_maintenance_cost(design_data, MAINTENANCE_RATE)
