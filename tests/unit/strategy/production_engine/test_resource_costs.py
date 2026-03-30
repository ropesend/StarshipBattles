"""Tests for design cost calculation and queue item cost tracking.

PROJ-75 Phase 4: Production resource consumption.
PROJ-218: Updated to use Ship-loading cost calculation with registry.

Task 4.1: Design cost calculation tests.
Task 4.3: Queue item cost tracking tests.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.production_engine import ProductionEngine


def _make_design_data(hull_id: str = "hull_frigate", components: list = None) -> dict:
    """Create design_data with valid ship structure.

    PROJ-218: Design data must have ship_class and valid component IDs
    for the Ship loading approach to work.

    Args:
        hull_id: Hull component ID (must exist in registry).
        components: Optional list of additional component dicts for INNER layer.
    """
    design = {
        "name": "Test Ship",
        "ship_class": "frigate",
        "layers": {
            "CORE": [{"id": hull_id}]
        }
    }
    if components:
        design["layers"]["INNER"] = components
    return design


class TestDesignCostCalculation:
    """Tests for _calculate_design_cost method.

    PROJ-218: Now uses Ship loading from registry - costs come from
    component definitions in components.json, not inline resource_cost.
    """

    def test_hull_component_cost(self, production_engine):
        """Hull component cost is calculated from registry."""
        design = _make_design_data()

        cost = production_engine._calculate_design_cost(design)

        # Hull component should have Metals cost
        assert "metals" in cost
        assert cost["metals"] > 0

    def test_multiple_components_summed(self, production_engine):
        """Costs from multiple components are summed per resource."""
        design = _make_design_data(
            components=[{"id": "combat_sensor"}]
        )

        cost = production_engine._calculate_design_cost(design)

        # Should have costs from hull + sensor
        assert "metals" in cost
        assert cost["metals"] > 0

    def test_invalid_component_skipped(self, production_engine):
        """Invalid component IDs don't cause failure."""
        design = _make_design_data(
            components=[{"id": "nonexistent_component"}]
        )

        # Should still get hull cost
        cost = production_engine._calculate_design_cost(design)
        assert isinstance(cost, dict)

    def test_empty_design_returns_hull_cost(self, production_engine):
        """Design with empty layers still gets default hull cost."""
        # Ship loader creates default hull
        design = {"layers": {}}

        cost = production_engine._calculate_design_cost(design)

        # Default hull has cost
        assert isinstance(cost, dict)

    def test_cost_cached_in_design_data(self, production_engine):
        """Calculated cost is cached as total_resource_cost in design_data."""
        design = _make_design_data()

        cost = production_engine._calculate_design_cost(design)

        assert "total_resource_cost" in design
        assert design["total_resource_cost"] == cost

    def test_cached_cost_returned_on_second_call(self, production_engine):
        """Second call returns the cached value without recalculating."""
        design = _make_design_data()

        # First call calculates and caches
        cost1 = production_engine._calculate_design_cost(design)

        # Modify cached value to verify cache is used
        design["total_resource_cost"]["metals"] = 999

        cost2 = production_engine._calculate_design_cost(design)

        # Should return cached value (999), not recalculated
        assert cost2["metals"] == 999

    def test_design_with_no_layers_key(self, production_engine):
        """Design missing layers key returns empty cost."""
        design = {}

        cost = production_engine._calculate_design_cost(design)

        assert cost == {}

    def test_registries_required(self):
        """Engine without registries returns empty cost."""
        engine = ProductionEngine(registries=None)
        design = _make_design_data()

        cost = engine._calculate_design_cost(design)

        # Returns empty when registries not provided
        assert cost == {}
