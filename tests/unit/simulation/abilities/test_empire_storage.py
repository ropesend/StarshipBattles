"""
Tests for EmpireStorageAbility - provides storage capacity for empire resource pool.

PROJ-75 Phase 3: TDD tests for EmpireStorageAbility.
"""
import pytest
from unittest.mock import MagicMock


class TestEmpireStorageAbility:
    """Tests for EmpireStorageAbility creation and behavior."""

    def _make_ability(self, resource_type="metals", capacity=10000.0, stats=None):
        """Create an EmpireStorageAbility with given data."""
        from game.simulation.components.abilities.harvester import EmpireStorageAbility

        component = MagicMock()
        component.stats = stats or {}
        component.ability_stats = {}

        data = {
            "resource_type": resource_type,
            "capacity": capacity,
        }
        return EmpireStorageAbility(component, data)

    def test_creation_with_resource_type_and_capacity(self):
        """EmpireStorageAbility stores resource_type and capacity from data."""
        ability = self._make_ability(resource_type="metals", capacity=10000.0)

        assert ability.resource_type == "metals"
        assert ability.capacity == pytest.approx(10000.0)

    def test_creation_defaults(self):
        """EmpireStorageAbility uses defaults when data is missing."""
        from game.simulation.components.abilities.harvester import EmpireStorageAbility

        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}

        ability = EmpireStorageAbility(component, {})

        assert ability.resource_type == ""
        assert ability.capacity == pytest.approx(0.0)

    def test_creation_with_non_dict_data(self):
        """EmpireStorageAbility handles non-dict data gracefully."""
        from game.simulation.components.abilities.harvester import EmpireStorageAbility

        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}

        ability = EmpireStorageAbility(component, True)

        assert ability.resource_type == ""
        assert ability.capacity == pytest.approx(0.0)

    def test_recalculate_applies_storage_mult(self):
        """Recalculate applies storage_mult modifier to base capacity."""
        ability = self._make_ability(capacity=10000.0, stats={"storage_mult": 1.5})

        ability.recalculate()

        assert ability.capacity == pytest.approx(15000.0)

    def test_recalculate_without_modifier(self):
        """Recalculate with no modifier keeps base capacity."""
        ability = self._make_ability(capacity=5000.0)

        ability.recalculate()

        assert ability.capacity == pytest.approx(5000.0)

    def test_get_primary_value_returns_capacity(self):
        """get_primary_value returns the current capacity."""
        ability = self._make_ability(capacity=8000.0)

        assert ability.get_primary_value() == pytest.approx(8000.0)

    def test_get_ui_rows(self):
        """get_ui_rows returns resource type and capacity info."""
        ability = self._make_ability(resource_type="organics", capacity=12000.0)

        rows = ability.get_ui_rows()

        assert len(rows) == 2
        assert rows[0]['label'] == 'Resource Type'
        assert rows[0]['value'] == 'organics'
        assert rows[1]['label'] == 'Storage Capacity'
        assert '12,000' in rows[1]['value'] or '12000' in rows[1]['value']

    def test_different_resource_types(self):
        """EmpireStorageAbility works with all resource types."""
        for rtype in ["metals", "organics", "vapors", "radioactives", "exotics"]:
            ability = self._make_ability(resource_type=rtype, capacity=5000.0)
            assert ability.resource_type == rtype


class TestEmpireStorageAbilityRegistry:
    """Test that EmpireStorageAbility is properly registered."""

    def test_in_registry(self):
        """EmpireStorageAbility is available in ABILITY_REGISTRY."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        assert "EmpireStorage" in ABILITY_REGISTRY

    def test_create_via_registry(self):
        """Can create EmpireStorageAbility via create_ability."""
        from game.simulation.components.abilities import create_ability

        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}

        ability = create_ability("EmpireStorage", component, {
            "resource_type": "metals",
            "capacity": 10000.0,
        })

        assert ability is not None
        assert ability.resource_type == "metals"
        assert ability.capacity == pytest.approx(10000.0)
