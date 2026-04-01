"""
Design Cost Calculator - Centralized design cost calculation.

PROJ-204 Phase 1: Consolidates cost calculation logic from multiple modules:
- ProductionEngine._calculate_design_cost()
- DesignMetadata._calculate_construction_cost()

PROJ-218: Fixed to resolve component costs from registry via Ship loading.
The previous implementation looked for inline resource_cost on component entries,
but design files only contain component references. Actual costs live in the
component registry and may include formula-based values and modifier multipliers.
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


logger = logging.getLogger(__name__)


class DesignCostCalculator:
    """Centralized calculator for design resource costs.

    PROJ-218: Calculates costs by loading a Ship object from design data,
    which resolves component costs from the registry, evaluates formula-based
    costs, and applies modifier multipliers. This gives accurate costs that
    match the design report panel.

    Usage:
        total_cost = DesignCostCalculator.calculate_total_cost(design_data, registries)
    """

    @staticmethod
    def calculate_total_cost(
        design_data: Dict[str, Any],
        registries: 'GameRegistries'
    ) -> Dict[str, float]:
        """Calculate total resource cost from a design.

        Order of precedence:
        1. Inline resource_cost on components (for tests with explicit costs,
           and for facilities that have simple cost structures)
        2. Ship loading from registry (for ship designs with ship_class)

        Args:
            design_data: Design data dict containing layers with components.
            registries: GameRegistries for component resolution (optional).

        Returns:
            Dict mapping resource type to total cost amount.
        """
        if not design_data:
            return {}

        # Cache: return previously calculated cost to avoid repeated Ship loading
        cached = design_data.get('total_resource_cost')
        if cached is not None:
            return cached

        # First: Check for inline resource_cost on components
        inline_cost = DesignCostCalculator._calculate_inline_cost(design_data)
        if inline_cost:
            cost = DesignCostCalculator._apply_cost_multiplier(inline_cost, design_data, registries)
            design_data['total_resource_cost'] = cost
            return cost

        # Second: Ship loading from registry (for ship designs only)
        # Only use Ship loading if design has a ship_class (indicates it's a ship design)
        if registries is not None and design_data.get('ship_class'):
            try:
                from game.simulation.services.design_loader import SimulationDesignLoader
                loader = SimulationDesignLoader(registries=registries)
                ship = loader.load_ship_from_design_data(design_data, 0, 0)

                if ship is not None:
                    # Extract construction_cost, stripping zero values
                    cost = {res: amount for res, amount in (ship.construction_cost or {}).items() if amount > 0}
                    cost = DesignCostCalculator._apply_cost_multiplier(cost, design_data, registries)
                    design_data['total_resource_cost'] = cost
                    return cost
            except Exception as e:
                logger.debug(f"Ship loading failed: {e}")

        return {}

    @staticmethod
    def _apply_cost_multiplier(
        base_cost: Dict[str, float],
        design_data: Dict[str, Any],
        registries: 'GameRegistries'
    ) -> Dict[str, float]:
        """Apply vehicle class cost multiplier to base costs.

        Looks up cost_multiplier from vehicleclasses.json via the design's
        ship_class. Default multiplier is 1.0 (no change).

        Args:
            base_cost: Base resource costs before multiplier.
            design_data: Design data with ship_class field.
            registries: GameRegistries for vehicle class lookup.

        Returns:
            Cost dict with multiplier applied.
        """
        multiplier = 1.0
        ship_class = design_data.get('ship_class', '')
        if ship_class and registries is not None:
            class_def = registries.vehicle_classes.get(ship_class, {})
            multiplier = class_def.get('cost_multiplier', 1.0)

        if multiplier == 1.0:
            return base_cost

        return {res: amount * multiplier for res, amount in base_cost.items()}

    @staticmethod
    def _calculate_inline_cost(design_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost from inline resource_cost fields on components.

        This is a fallback for when Ship loading doesn't work (e.g., in tests).

        Args:
            design_data: Design data dict containing layers with components.

        Returns:
            Dict mapping resource type to total cost amount.
        """
        from game.core.patterns.layer_iterator import iter_components

        total_cost: Dict[str, float] = {}

        for component in iter_components(design_data):
            if not isinstance(component, dict):
                continue

            comp_cost = component.get('resource_cost', {})
            for res, amount in comp_cost.items():
                total_cost[res] = total_cost.get(res, 0) + amount

        return total_cost
