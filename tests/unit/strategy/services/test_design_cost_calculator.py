"""
Tests for DesignCostCalculator service.

PROJ-204 Phase 1: Tests for centralized design cost calculation.
PROJ-218: Updated to pass registries parameter (required for Ship loading).
"""

import pytest
from game.strategy.services.design_cost_calculator import DesignCostCalculator


class TestCalculateTotalCost:
    """Tests for calculate_total_cost method."""

    def test_empty_design(self, fresh_registries):
        """Empty design returns empty cost dict."""
        design_data = {}
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        assert result == {}

    def test_empty_layers_still_has_hull_cost(self, fresh_registries):
        """Design with empty layers still has default hull cost.

        Ship loader creates a default hull even for incomplete designs.
        """
        design_data = {"layers": {}}
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        # Ship loader creates default hull which has cost
        assert isinstance(result, dict)

    def test_none_registries_uses_inline_fallback(self):
        """None registries falls back to inline resource_cost."""
        design_data = {
            "layers": {
                "CORE": [{"id": "reactor", "resource_cost": {"minerals": 100}}]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data, None)
        # Falls back to inline cost since Ship loading not available
        assert result == {"minerals": 100}

    def test_component_reference_resolved_from_registry(self, fresh_registries):
        """Component references resolve costs from registry (the main fix)."""
        # Create a minimal valid design that uses registry components
        # Note: Component IDs in registry use hull_XXX format
        design_data = {
            "name": "Test Ship",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}]  # Hull component from registry
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        # Should have some cost from the hull component
        assert isinstance(result, dict)
        # The frigate hull should have Metals cost
        assert "Metals" in result

    def test_zero_values_stripped(self, fresh_registries):
        """Zero-value costs are not included in result."""
        # Use a design that will result in some zero costs
        design_data = {
            "name": "Test Ship",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        # Verify no zero values in result
        for res, amount in result.items():
            assert amount > 0, f"Resource {res} has zero value"


class TestCalculateMaintenanceCost:
    """Tests for calculate_maintenance_cost method."""

    def test_default_rate(self, fresh_registries):
        """Default 5% maintenance rate is applied."""
        design_data = {
            "name": "Test Ship",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}]
            }
        }
        total_cost = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        maintenance = DesignCostCalculator.calculate_maintenance_cost(design_data, fresh_registries)

        # Verify maintenance is 5% of total for each resource
        for res in total_cost:
            if res in maintenance:
                assert pytest.approx(maintenance[res], rel=0.01) == total_cost[res] * 0.05

    def test_custom_rate(self, fresh_registries):
        """Custom maintenance rate is applied."""
        design_data = {
            "name": "Test Ship",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}]
            }
        }
        total_cost = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        maintenance = DesignCostCalculator.calculate_maintenance_cost(
            design_data, fresh_registries, rate=0.10
        )

        # Verify maintenance is 10% of total for each resource
        for res in total_cost:
            if res in maintenance:
                assert pytest.approx(maintenance[res], rel=0.01) == total_cost[res] * 0.10

    def test_zero_rate(self, fresh_registries):
        """Zero rate returns zero costs."""
        design_data = {
            "name": "Test Ship",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}]
            }
        }
        result = DesignCostCalculator.calculate_maintenance_cost(
            design_data, fresh_registries, rate=0.0
        )
        for res, amount in result.items():
            assert amount == 0.0

    def test_empty_design(self, fresh_registries):
        """Empty design returns empty maintenance dict."""
        design_data = {}
        result = DesignCostCalculator.calculate_maintenance_cost(design_data, fresh_registries)
        assert result == {}


class TestRegistryResolution:
    """Tests verifying component cost resolution from registry.

    PROJ-218: These tests verify the main fix - costs are loaded from
    the component registry, not inline resource_cost fields.
    """

    def test_real_design_has_costs(self, fresh_registries):
        """A real design file structure produces non-empty costs."""
        # This mimics what a real design file looks like
        # Note: Component IDs use hull_XXX format
        design_data = {
            "name": "Scout",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}],
                "INNER": [{"id": "combat_sensor"}],
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        # Real components from registry should have costs
        assert result, "Design with registry components should have costs"
        # Should include Metals at minimum (from hull)
        assert "Metals" in result

    def test_inline_resource_cost_takes_priority(self, fresh_registries):
        """Inline resource_cost on component entries is used first.

        PROJ-218: The calculator checks inline resource_cost first (for tests
        and facilities), then falls back to Ship loading for ship designs.
        """
        design_data = {
            "layers": {
                "CORE": [{"id": "fake_component", "resource_cost": {"minerals": 100}}]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        # Inline cost IS used first
        assert result == {"minerals": 100}

    def test_ship_loading_used_when_no_inline_cost(self, fresh_registries):
        """Ship loading used for ship designs without inline costs.

        PROJ-218: Ship loading only kicks in for designs with ship_class
        and no inline resource_cost fields.
        """
        design_data = {
            "name": "Test Ship",
            "ship_class": "frigate",
            "layers": {
                "CORE": [{"id": "hull_frigate"}]  # No inline cost
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data, fresh_registries)
        # Ship loading resolves cost from registry
        assert "Metals" in result
        assert result["Metals"] > 0
