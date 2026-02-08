"""Tests for design cost calculation and queue item cost tracking.

PROJ-75 Phase 4: Production resource consumption.

Task 4.1: Design cost calculation tests.
Task 4.3: Queue item cost tracking tests.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.production_engine import ProductionEngine


# --- Helper fixtures ---

def _make_design_data(components_by_layer: dict) -> dict:
    """Create design_data with layers and components.

    Args:
        components_by_layer: Dict of layer_name -> list of component dicts.
            Each component dict should have at minimum 'id' and optionally 'resource_cost'.
    """
    layers = {}
    for layer_name, components in components_by_layer.items():
        layers[layer_name] = {"components": components}
    return {"layers": layers}


class TestDesignCostCalculation:
    """Tests for _calculate_design_cost method."""

    def test_single_component_cost(self):
        """Cost from a single component is returned directly."""
        engine = ProductionEngine()
        design = _make_design_data({
            "CORE": [
                {"id": "bridge", "resource_cost": {"Metals": 80, "Organics": 20}}
            ]
        })

        cost = engine._calculate_design_cost(design)

        assert cost == {"Metals": 80, "Organics": 20}

    def test_multiple_components_summed(self):
        """Costs from multiple components are summed per resource."""
        engine = ProductionEngine()
        design = _make_design_data({
            "CORE": [
                {"id": "bridge", "resource_cost": {"Metals": 80, "Organics": 20}},
                {"id": "railgun", "resource_cost": {"Metals": 150, "Radioactives": 30}},
            ]
        })

        cost = engine._calculate_design_cost(design)

        assert cost == {"Metals": 230, "Organics": 20, "Radioactives": 30}

    def test_missing_resource_cost_defaults_empty(self):
        """Components without resource_cost contribute nothing."""
        engine = ProductionEngine()
        design = _make_design_data({
            "CORE": [
                {"id": "bridge", "resource_cost": {"Metals": 100}},
                {"id": "hull_plating"},  # No resource_cost
            ]
        })

        cost = engine._calculate_design_cost(design)

        assert cost == {"Metals": 100}

    def test_multiple_layers_summed(self):
        """Costs from components across different layers are summed."""
        engine = ProductionEngine()
        design = _make_design_data({
            "CORE": [
                {"id": "bridge", "resource_cost": {"Metals": 80}}
            ],
            "WEAPONS": [
                {"id": "railgun", "resource_cost": {"Metals": 150, "Radioactives": 30}}
            ],
            "ENGINES": [
                {"id": "thruster", "resource_cost": {"Metals": 120, "Radioactives": 40}}
            ]
        })

        cost = engine._calculate_design_cost(design)

        assert cost == {"Metals": 350, "Radioactives": 70}

    def test_empty_design_returns_empty(self):
        """Design with no layers returns empty cost dict."""
        engine = ProductionEngine()
        design = {"layers": {}}

        cost = engine._calculate_design_cost(design)

        assert cost == {}

    def test_cost_cached_in_design_data(self):
        """Calculated cost is cached as total_resource_cost in design_data."""
        engine = ProductionEngine()
        design = _make_design_data({
            "CORE": [
                {"id": "bridge", "resource_cost": {"Metals": 80}}
            ]
        })

        cost = engine._calculate_design_cost(design)

        assert "total_resource_cost" in design
        assert design["total_resource_cost"] == {"Metals": 80}

    def test_cached_cost_returned_on_second_call(self):
        """Second call returns the cached value without recalculating."""
        engine = ProductionEngine()
        design = _make_design_data({
            "CORE": [
                {"id": "bridge", "resource_cost": {"Metals": 80}}
            ]
        })

        # First call calculates and caches
        cost1 = engine._calculate_design_cost(design)
        # Modify layers to verify cache is used
        design["layers"]["CORE"]["components"][0]["resource_cost"]["Metals"] = 999
        cost2 = engine._calculate_design_cost(design)

        assert cost2 == {"Metals": 80}  # Cached value, not 999

    def test_design_with_no_layers_key(self):
        """Design missing layers key returns empty cost."""
        engine = ProductionEngine()
        design = {}

        cost = engine._calculate_design_cost(design)

        assert cost == {}
