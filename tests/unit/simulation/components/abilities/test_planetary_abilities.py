"""Tests for planetary ability classes (PROJ-237)."""

import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.planetary import (
    PlanetaryShieldAbility,
    PlanetaryEnergyGeneratorAbility,
    PlanetaryEnergyStorageAbility,
)
from game.simulation.components.abilities import create_ability


@pytest.fixture
def mock_component():
    """Create a mock component for ability construction."""
    comp = MagicMock()
    comp.id = "test_component"
    return comp


# =============================================================================
# PlanetaryShieldAbility
# =============================================================================

class TestPlanetaryShieldAbility:
    """Tests for PlanetaryShieldAbility."""

    def test_construction_from_dict(self, mock_component):
        data = {
            "energy_drain_rate": 25.0,
            "activation_time": 50,
            "deactivation_time": 10,
            "shield_hp": 100.0,
            "shield_regen": 5.0,
        }
        ability = PlanetaryShieldAbility(mock_component, data)

        assert ability.energy_drain_rate == 25.0
        assert ability.activation_time == 50
        assert ability.deactivation_time == 10
        assert ability.shield_hp == 100.0
        assert ability.shield_regen == 5.0

    def test_construction_partial_data(self, mock_component):
        data = {"energy_drain_rate": 10.0}
        ability = PlanetaryShieldAbility(mock_component, data)

        assert ability.energy_drain_rate == 10.0
        assert ability.activation_time == 1
        assert ability.deactivation_time == 1
        assert ability.shield_hp == 0.0
        assert ability.shield_regen == 0.0

    def test_construction_non_dict(self, mock_component):
        ability = PlanetaryShieldAbility(mock_component, 42)

        assert ability.energy_drain_rate == 0.0
        assert ability.activation_time == 1
        assert ability.deactivation_time == 1

    def test_get_primary_value(self, mock_component):
        data = {"energy_drain_rate": 25.0}
        ability = PlanetaryShieldAbility(mock_component, data)
        assert ability.get_primary_value() == 25.0

    def test_get_ui_rows(self, mock_component):
        data = {"energy_drain_rate": 25.0, "activation_time": 50, "deactivation_time": 10}
        ability = PlanetaryShieldAbility(mock_component, data)
        rows = ability.get_ui_rows()

        assert len(rows) == 3
        assert rows[0]['label'] == 'Energy Drain'
        assert '25.0' in rows[0]['value']
        assert rows[1]['label'] == 'Activation Time'
        assert '50' in rows[1]['value']
        assert rows[2]['label'] == 'Deactivation Time'
        assert '10' in rows[2]['value']

    def test_stat_bindings_empty(self, mock_component):
        ability = PlanetaryShieldAbility(mock_component, {})
        assert ability.STAT_BINDINGS == []


# =============================================================================
# PlanetaryEnergyGeneratorAbility
# =============================================================================

class TestPlanetaryEnergyGeneratorAbility:
    """Tests for PlanetaryEnergyGeneratorAbility."""

    def test_construction_from_dict(self, mock_component):
        data = {"generation_rate": 50.0}
        ability = PlanetaryEnergyGeneratorAbility(mock_component, data)
        assert ability.generation_rate == 50.0

    def test_construction_from_number(self, mock_component):
        ability = PlanetaryEnergyGeneratorAbility(mock_component, 75.0)
        assert ability.generation_rate == 75.0

    def test_construction_empty_dict(self, mock_component):
        ability = PlanetaryEnergyGeneratorAbility(mock_component, {})
        assert ability.generation_rate == 0.0

    def test_get_primary_value(self, mock_component):
        data = {"generation_rate": 50.0}
        ability = PlanetaryEnergyGeneratorAbility(mock_component, data)
        assert ability.get_primary_value() == 50.0

    def test_get_ui_rows(self, mock_component):
        data = {"generation_rate": 50.0}
        ability = PlanetaryEnergyGeneratorAbility(mock_component, data)
        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Generation Rate'
        assert '50.0' in rows[0]['value']

    def test_stat_bindings_empty(self, mock_component):
        ability = PlanetaryEnergyGeneratorAbility(mock_component, {})
        assert ability.STAT_BINDINGS == []


# =============================================================================
# PlanetaryEnergyStorageAbility
# =============================================================================

class TestPlanetaryEnergyStorageAbility:
    """Tests for PlanetaryEnergyStorageAbility."""

    def test_construction_from_dict(self, mock_component):
        data = {"capacity": 5000.0}
        ability = PlanetaryEnergyStorageAbility(mock_component, data)
        assert ability.capacity == 5000.0

    def test_construction_from_number(self, mock_component):
        ability = PlanetaryEnergyStorageAbility(mock_component, 3000)
        assert ability.capacity == 3000.0

    def test_construction_empty_dict(self, mock_component):
        ability = PlanetaryEnergyStorageAbility(mock_component, {})
        assert ability.capacity == 0.0

    def test_get_primary_value(self, mock_component):
        data = {"capacity": 5000.0}
        ability = PlanetaryEnergyStorageAbility(mock_component, data)
        assert ability.get_primary_value() == 5000.0

    def test_get_ui_rows(self, mock_component):
        data = {"capacity": 5000.0}
        ability = PlanetaryEnergyStorageAbility(mock_component, data)
        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Energy Capacity'
        assert '5,000' in rows[0]['value']

    def test_stat_bindings_empty(self, mock_component):
        ability = PlanetaryEnergyStorageAbility(mock_component, {})
        assert ability.STAT_BINDINGS == []


# =============================================================================
# Factory Registration
# =============================================================================

class TestAbilityRegistration:
    """Tests that planetary abilities are properly registered in the factory."""

    def test_create_planetary_shield(self, mock_component):
        data = {"energy_drain_rate": 25.0, "activation_time": 50}
        ability = create_ability("PlanetaryShield", mock_component, data)
        assert ability is not None
        assert isinstance(ability, PlanetaryShieldAbility)
        assert ability.energy_drain_rate == 25.0

    def test_create_planetary_energy_generator(self, mock_component):
        data = {"generation_rate": 50.0}
        ability = create_ability("PlanetaryEnergyGenerator", mock_component, data)
        assert ability is not None
        assert isinstance(ability, PlanetaryEnergyGeneratorAbility)
        assert ability.generation_rate == 50.0

    def test_create_planetary_energy_storage(self, mock_component):
        data = {"capacity": 5000.0}
        ability = create_ability("PlanetaryEnergyStorage", mock_component, data)
        assert ability is not None
        assert isinstance(ability, PlanetaryEnergyStorageAbility)
        assert ability.capacity == 5000.0
