"""
EmpireEconomyCalculator - Aggregates empire-wide production and expense data.

PROJ-99 Phase 1: Pure strategy-layer class that calculates production from
facilities, maintenance from facilities and ships, and provides a snapshot
of the empire economy.

This is a read-only calculation - it doesn't modify any game state.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, TYPE_CHECKING

# TODO: Phase 4 will replace with ResourceCatalog
PLANET_RESOURCE_NAMES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]
from game.core.patterns.layer_iterator import iter_components

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
from game.core.registry import GameRegistries
from game.strategy.engine.maintenance_engine import (
    MAINTENANCE_RATE,
    calculate_maintenance_cost,
)
from game.strategy.engine.harvesting_engine import get_harvester_info
from game.strategy.engine.construction_forecast import forecast_queue_turn_spend


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
    construction_expenses_ships: Dict[str, float] = field(default_factory=dict)
    construction_expenses_complexes: Dict[str, float] = field(default_factory=dict)
    total_expenses: Dict[str, float] = field(default_factory=dict)

    # Treasury state
    net_resources: Dict[str, float] = field(default_factory=dict)
    current_storage: Dict[str, float] = field(default_factory=dict)
    max_storage: Dict[str, float] = field(default_factory=dict)


class EmpireEconomyCalculator:
    """Calculator for empire-wide production and expense aggregation.

    PROJ-211: registries parameter is now required (no global fallback).

    Usage:
        # From GameSession context
        calculator = EmpireEconomyCalculator(registries=session.registries)
        snapshot = calculator.calculate(empire)
        # Access snapshot.colony_production, snapshot.maintenance_expenses, etc.

    Replicates formulas from:
    - HarvestingEngine: base_harvest_rate * planet_quality
    - MaintenanceEngine: 5% of total resource_cost
    """

    # Use shared MAINTENANCE_RATE from maintenance_engine module

    def __init__(self, *, registries: GameRegistries) -> None:
        """Initialize the calculator.

        PROJ-211: registries is now required (no global fallback).

        Args:
            registries: GameRegistries for resolving component
                       abilities from plain component IDs in design_data (required).
        """
        self._registries: GameRegistries = registries

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
        zero_resources = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
        snapshot.ship_production = zero_resources.copy()
        snapshot.trade_production = zero_resources.copy()
        snapshot.tribute_production = zero_resources.copy()
        snapshot.mining_production = zero_resources.copy()

        # Total production = colony production only for now
        snapshot.total_production = snapshot.colony_production.copy()

        # Expense aggregation
        snapshot.maintenance_expenses = self._aggregate_maintenance(empire)

        # Construction expenses split by type
        ships_exp, complexes_exp = self._aggregate_construction_expenses(empire)
        snapshot.construction_expenses_ships = ships_exp
        snapshot.construction_expenses_complexes = complexes_exp

        # Placeholder expense categories (future implementation)
        snapshot.tribute_expenses = zero_resources.copy()

        # Total expenses = sum of all expense categories
        snapshot.total_expenses = {}
        for r in PLANET_RESOURCE_NAMES:
            snapshot.total_expenses[r] = (
                snapshot.tribute_expenses.get(r, 0.0)
                + snapshot.maintenance_expenses.get(r, 0.0)
                + snapshot.construction_expenses_ships.get(r, 0.0)
                + snapshot.construction_expenses_complexes.get(r, 0.0)
            )

        # Net resources per turn
        snapshot.net_resources = {}
        for r in PLANET_RESOURCE_NAMES:
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
        Production = min(base_harvest_rate * quality, remaining_quantity) per harvester.

        Args:
            empire: Empire with colonies attribute.

        Returns:
            Dict mapping resource type to total production per turn.
        """
        totals = {r: 0.0 for r in PLANET_RESOURCE_NAMES}

        for colony in empire.colonies:
            # Track remaining quantity per resource for this colony
            # (multiple harvesters draw from the same deposit)
            remaining_quantity: Dict[str, float] = {}
            for res in PLANET_RESOURCE_NAMES:
                resource_data = colony.resources.get(res, {})
                remaining_quantity[res] = resource_data.get('quantity', 0.0)

            for facility in colony.facilities:
                # Skip non-operational facilities
                if not facility.is_operational:
                    continue

                for comp in iter_components(facility.design_data):
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
                    if quality <= 0:
                        continue

                    # Cap production by remaining planet quantity
                    potential = base_rate * quality
                    available = remaining_quantity.get(resource_type, 0.0)
                    production = min(potential, available)

                    if resource_type in totals:
                        totals[resource_type] += production
                    # Reduce tracked quantity so subsequent harvesters see less
                    remaining_quantity[resource_type] = max(0.0, available - production)

        return totals

    def _aggregate_maintenance(self, empire: 'Empire') -> Dict[str, float]:
        """Calculate total maintenance costs for facilities and ships.

        Maintenance is 5% of the sum of all resource_cost values.

        Args:
            empire: Empire with colonies and fleets.

        Returns:
            Dict mapping resource type to total maintenance cost per turn.
        """
        totals = {r: 0.0 for r in PLANET_RESOURCE_NAMES}

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
        # PROJ-218: Pass registries for Ship-loading cost calculation
        return calculate_maintenance_cost(design_data, self._registries, MAINTENANCE_RATE)

    def _aggregate_construction_expenses(
        self, empire: 'Empire'
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Calculate construction expenses split by ships vs complexes.

        Iterates all construction queues (planet base, facility, fleet),
        forecasts per-turn spend using queue-level distribution, and
        classifies by item type.

        Args:
            empire: Empire with colonies and fleets.

        Returns:
            Tuple of (ships_expenses, complexes_expenses), each a dict
            mapping resource type to total per-turn expense.
        """
        from game.strategy.data.build_queue_source import (
            get_default_production_rates,
            _get_facility_production_rates,
        )
        from game.strategy.data.fleet import Fleet

        ships = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
        complexes = {r: 0.0 for r in PLANET_RESOURCE_NAMES}

        def _accumulate(queue: List[Dict], build_rate: Dict[str, float]) -> None:
            """Forecast spend for a queue and accumulate into ships/complexes."""
            if not queue:
                return
            per_item_spend = forecast_queue_turn_spend(queue, build_rate)
            for i, item in enumerate(queue):
                item_type = item.get("type", "ship")
                target = complexes if item_type == "complex" else ships
                spend = per_item_spend[i]
                for r, amount in spend.items():
                    if r in target:
                        target[r] += amount

        # Planet base queues (complexes only)
        for colony in empire.colonies:
            base_rate = get_default_production_rates("planetary_yard")
            _accumulate(colony.construction_queue, base_rate)

            # Facility queues (shipyards)
            for facility in colony.facilities:
                if facility.construction_queue and facility.is_shipyard:
                    fac_rate = _get_facility_production_rates(facility)
                    _accumulate(facility.construction_queue, fac_rate)

        # Fleet queues
        for fleet in empire.fleets:
            if not fleet.construction_queue:
                continue
            if not hasattr(fleet, 'capabilities') or not fleet.capabilities.has_space_shipyard:
                continue
            yard_count = fleet.capabilities.space_shipyard_count
            base_rate = get_default_production_rates("fleet_space_yard")
            total_rate = {k: v * yard_count for k, v in base_rate.items()}
            _accumulate(fleet.construction_queue, total_rate)

        return ships, complexes
