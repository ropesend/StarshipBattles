"""
Design Cost Calculator - Centralized design cost calculation.

PROJ-204 Phase 1: Consolidates cost calculation logic from multiple modules:
- ProductionEngine._calculate_design_cost()
- MaintenanceEngine.calculate_maintenance_cost()
- DesignMetadata._calculate_resource_cost()

Uses LayerIterator for consistent layer traversal across all formats.
"""

from typing import Dict, Any

from game.core.patterns.layer_iterator import iter_components


# Standard maintenance rate (5% of build cost per turn)
DEFAULT_MAINTENANCE_RATE = 0.05


class DesignCostCalculator:
    """Centralized calculator for design resource costs.

    Provides static methods for calculating:
    - Total build cost (sum of all component resource_cost values)
    - Maintenance cost (percentage of build cost per turn)

    Uses the 'resource_cost' field on component entries, which is the
    standard field for component costs in design_data.

    Usage:
        total_cost = DesignCostCalculator.calculate_total_cost(design_data)
        maintenance = DesignCostCalculator.calculate_maintenance_cost(design_data)
    """

    @staticmethod
    def calculate_total_cost(design_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate total resource cost from all components in a design.

        Iterates through all layers and components, summing their resource_cost
        fields. Components without resource_cost are skipped.

        Args:
            design_data: Design data dict containing layers with components.

        Returns:
            Dict mapping resource type to total cost amount.
        """
        total_cost: Dict[str, float] = {}

        for component in iter_components(design_data):
            if not isinstance(component, dict):
                continue

            comp_cost = component.get('resource_cost', {})
            for res, amount in comp_cost.items():
                total_cost[res] = total_cost.get(res, 0) + amount

        return total_cost

    @staticmethod
    def calculate_maintenance_cost(
        design_data: Dict[str, Any],
        rate: float = DEFAULT_MAINTENANCE_RATE
    ) -> Dict[str, float]:
        """Calculate maintenance cost from a design's resource costs.

        Maintenance is a percentage of the total build cost.

        Args:
            design_data: Design data dict containing layers with components.
            rate: Maintenance rate to apply (default: 5% = 0.05).

        Returns:
            Dict mapping resource type to maintenance cost amount.
        """
        total_cost = DesignCostCalculator.calculate_total_cost(design_data)

        maintenance: Dict[str, float] = {}
        for res, amount in total_cost.items():
            maintenance[res] = amount * rate

        return maintenance
