"""
EmpireEconomyCalculator - Aggregates empire-wide production and expense data.

PROJ-99 Phase 1: Pure strategy-layer class that calculates production from
facilities, maintenance from facilities and ships, and provides a display-ready
snapshot of the empire economy.

This is a read-only calculation - it doesn't modify any game state.
"""

from dataclasses import dataclass, field
from typing import Dict

from game.core.constants import PLANET_RESOURCES


@dataclass
class EmpireEconomySnapshot:
    """Display-ready snapshot of empire economic state.

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
        calculator = EmpireEconomyCalculator(registries=get_default_registries())
        snapshot = calculator.calculate(empire)
        # Access snapshot.colony_production, snapshot.maintenance_expenses, etc.

    Replicates formulas from:
    - HarvestingEngine: base_harvest_rate * planet_quality
    - MaintenanceEngine: 5% of total resource_cost
    """

    MAINTENANCE_RATE = 0.05  # 5% per turn

    def __init__(self, *, registries=None):
        """Initialize the calculator.

        Args:
            registries: Optional GameRegistries for resolving component
                       abilities from plain component IDs in design_data.
        """
        self._registries = registries

    def calculate(self, empire) -> EmpireEconomySnapshot:
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
        resource_pool = getattr(empire, 'resource_pool', {})
        max_storage = getattr(empire, 'max_storage', {})
        snapshot.current_storage = resource_pool.copy()
        snapshot.max_storage = max_storage.copy()

        return snapshot

    def _aggregate_colony_production(self, empire) -> Dict[str, float]:
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

        colonies = getattr(empire, 'colonies', [])
        for colony in colonies:
            facilities = getattr(colony, 'facilities', [])
            for facility in facilities:
                # Skip non-operational facilities
                if not getattr(facility, 'is_operational', True):
                    continue

                design_data = getattr(facility, 'design_data', {})
                layers = design_data.get('layers', {})

                for layer_data in layers.values():
                    # Only handle list-format layers
                    if not isinstance(layer_data, list):
                        continue

                    for comp in layer_data:
                        harvester = self._get_harvester_info(comp)
                        if harvester is None:
                            continue

                        resource_type = harvester.get('resource_type', '')
                        base_rate = harvester.get('base_harvest_rate', 0.0)

                        if not resource_type or base_rate <= 0:
                            continue

                        # Get planet quality for this resource
                        planet_resources = getattr(colony, 'resources', {})
                        resource_data = planet_resources.get(resource_type, {})
                        quality = resource_data.get('quality', 0.0)

                        # Accumulate production
                        production = base_rate * quality
                        if resource_type in totals:
                            totals[resource_type] += production

        return totals

    def _get_harvester_info(self, comp) -> 'Dict[str, any] | None':
        """Extract ResourceHarvester info from a component entry.

        Checks inline abilities first, then falls back to registry lookup.

        Args:
            comp: Component entry from design_data layers (dict or str).

        Returns:
            Dict with 'resource_type' and 'base_harvest_rate', or None.
        """
        if isinstance(comp, dict):
            # Check inline abilities
            abilities = comp.get('abilities', {})
            harvester = abilities.get('ResourceHarvester')
            if isinstance(harvester, dict):
                return harvester
            # Fall back to registry lookup by component ID
            comp_id = comp.get('id')
            if comp_id and self._registries is not None:
                return self._lookup_harvester_in_registry(comp_id)
        elif isinstance(comp, str) and self._registries is not None:
            return self._lookup_harvester_in_registry(comp)
        return None

    def _lookup_harvester_in_registry(self, comp_id: str) -> 'Dict[str, any] | None':
        """Look up harvester ability from the component registry.

        Args:
            comp_id: Component identifier to look up.

        Returns:
            Dict with harvester info or None.
        """
        comp_def = self._registries.components.get(comp_id)
        if comp_def is None:
            return None
        abilities = getattr(comp_def, 'abilities', {}) or {}
        harvester = abilities.get('ResourceHarvester')
        if isinstance(harvester, dict):
            return harvester
        return None

    def _aggregate_maintenance(self, empire) -> Dict[str, float]:
        """Calculate total maintenance costs for facilities and ships.

        Maintenance is 5% of the sum of all resource_cost values.

        Args:
            empire: Empire with colonies and fleets.

        Returns:
            Dict mapping resource type to total maintenance cost per turn.
        """
        totals = {r: 0.0 for r in PLANET_RESOURCES}

        # Facility maintenance
        colonies = getattr(empire, 'colonies', [])
        for colony in colonies:
            facilities = getattr(colony, 'facilities', [])
            for facility in facilities:
                # Skip non-operational facilities
                if not getattr(facility, 'is_operational', True):
                    continue

                design_data = getattr(facility, 'design_data', {})
                cost = self._calculate_maintenance_cost(design_data)
                for r, amount in cost.items():
                    if r in totals:
                        totals[r] += amount

        # Ship maintenance
        fleets = getattr(empire, 'fleets', [])
        for fleet in fleets:
            ships = getattr(fleet, 'ships', [])
            for ship in ships:
                design_data = getattr(ship, 'design_data', {})
                cost = self._calculate_maintenance_cost(design_data)
                for r, amount in cost.items():
                    if r in totals:
                        totals[r] += amount

        return totals

    def _calculate_maintenance_cost(self, design_data: Dict) -> Dict[str, float]:
        """Calculate maintenance cost from a design's resource costs.

        Maintenance is MAINTENANCE_RATE (5%) of the total build cost,
        which is the sum of resource_cost across all layers and components.

        Handles two layer formats:
        - Dict format: {"CORE": {"components": [...]}}
        - List format: {"HULL": [{"id": "comp_a", ...}]}

        Args:
            design_data: Design data dict containing layers with components.

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
            maintenance[res] = amount * self.MAINTENANCE_RATE

        return maintenance
