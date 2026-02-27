"""
Tests for DesignCostCalculator service.

PROJ-204 Phase 1: Tests for centralized design cost calculation.
"""

import pytest
from game.strategy.services.design_cost_calculator import DesignCostCalculator


class TestCalculateTotalCost:
    """Tests for calculate_total_cost method."""

    def test_empty_design(self):
        """Empty design returns empty cost dict."""
        design_data = {}
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {}

    def test_empty_layers(self):
        """Design with empty layers returns empty cost dict."""
        design_data = {"layers": {}}
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {}

    def test_single_component_resource_cost(self):
        """Single component's resource_cost is summed."""
        design_data = {
            "layers": {
                "CORE": [{"id": "reactor", "resource_cost": {"minerals": 100, "energy": 50}}]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {"minerals": 100, "energy": 50}

    def test_multiple_components_sum(self):
        """Multiple components' costs are summed."""
        design_data = {
            "layers": {
                "CORE": [
                    {"id": "reactor", "resource_cost": {"minerals": 100}},
                    {"id": "bridge", "resource_cost": {"minerals": 50, "crystals": 20}},
                ],
                "INNER": [
                    {"id": "armor", "resource_cost": {"minerals": 200}},
                ],
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {"minerals": 350, "crystals": 20}

    def test_component_without_resource_cost(self):
        """Components without resource_cost are skipped."""
        design_data = {
            "layers": {
                "CORE": [
                    {"id": "sensor"},  # No resource_cost
                    {"id": "reactor", "resource_cost": {"minerals": 100}},
                ]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {"minerals": 100}

    def test_dict_format_layers(self):
        """Dict format layers with 'components' key work."""
        design_data = {
            "layers": {
                "CORE": {"components": [{"id": "reactor", "resource_cost": {"minerals": 100}}]}
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {"minerals": 100}

    def test_string_components_skipped(self):
        """String component entries are skipped (no resource_cost)."""
        design_data = {
            "layers": {
                "CORE": ["reactor_simple", {"id": "reactor", "resource_cost": {"minerals": 100}}]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {"minerals": 100}


class TestCalculateMaintenanceCost:
    """Tests for calculate_maintenance_cost method."""

    def test_default_rate(self):
        """Default 5% maintenance rate is applied."""
        design_data = {
            "layers": {
                "CORE": [{"id": "reactor", "resource_cost": {"minerals": 1000}}]
            }
        }
        result = DesignCostCalculator.calculate_maintenance_cost(design_data)
        assert result == {"minerals": 50.0}  # 5% of 1000

    def test_custom_rate(self):
        """Custom maintenance rate is applied."""
        design_data = {
            "layers": {
                "CORE": [{"id": "reactor", "resource_cost": {"minerals": 1000}}]
            }
        }
        result = DesignCostCalculator.calculate_maintenance_cost(design_data, rate=0.10)
        assert result == {"minerals": 100.0}  # 10% of 1000

    def test_multiple_resources(self):
        """Maintenance rate applied to all resource types."""
        design_data = {
            "layers": {
                "CORE": [{"id": "reactor", "resource_cost": {"minerals": 200, "energy": 100}}]
            }
        }
        result = DesignCostCalculator.calculate_maintenance_cost(design_data, rate=0.05)
        assert result == {"minerals": 10.0, "energy": 5.0}

    def test_zero_rate(self):
        """Zero rate returns zero costs."""
        design_data = {
            "layers": {
                "CORE": [{"id": "reactor", "resource_cost": {"minerals": 1000}}]
            }
        }
        result = DesignCostCalculator.calculate_maintenance_cost(design_data, rate=0.0)
        assert result == {"minerals": 0.0}

    def test_empty_design(self):
        """Empty design returns empty maintenance dict."""
        design_data = {}
        result = DesignCostCalculator.calculate_maintenance_cost(design_data)
        assert result == {}


class TestCostFieldConsistency:
    """Tests verifying consistent handling of 'cost' vs 'resource_cost' fields."""

    def test_resource_cost_field_used(self):
        """The 'resource_cost' field is the standard for design cost."""
        design_data = {
            "layers": {
                "CORE": [{"id": "comp", "resource_cost": {"minerals": 100}}]
            }
        }
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {"minerals": 100}

    def test_cost_field_not_used_by_default(self):
        """The 'cost' field is not used by default (resource_cost is standard)."""
        design_data = {
            "layers": {
                "CORE": [{"id": "comp", "cost": {"minerals": 100}}]
            }
        }
        # cost field is not resource_cost - should return empty
        result = DesignCostCalculator.calculate_total_cost(design_data)
        assert result == {}
