"""Tests for planetary and strategic ability classes (PROJ-237/238)."""

import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.planetary import (
    PlanetaryShieldAbility,
    StrategicResourceGenerationAbility,
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
# StrategicResourceGenerationAbility
# =============================================================================

class TestStrategicResourceGenerationAbility:
    """Tests for StrategicResourceGenerationAbility."""

    def test_construction_from_dict(self, mock_component):
        data = {"resource": "energy", "generation_rate": 25000.0}
        ability = StrategicResourceGenerationAbility(mock_component, data)
        assert ability.resource == "energy"
        assert ability.generation_rate == 25000.0

    def test_construction_empty_dict(self, mock_component):
        ability = StrategicResourceGenerationAbility(mock_component, {})
        assert ability.resource == ""
        assert ability.generation_rate == 0.0

    def test_construction_non_dict(self, mock_component):
        ability = StrategicResourceGenerationAbility(mock_component, 42)
        assert ability.resource == ""
        assert ability.generation_rate == 0.0

    def test_get_primary_value(self, mock_component):
        data = {"resource": "fuel", "generation_rate": 5000.0}
        ability = StrategicResourceGenerationAbility(mock_component, data)
        assert ability.get_primary_value() == 5000.0

    def test_get_ui_rows(self, mock_component):
        data = {"resource": "energy", "generation_rate": 25000.0}
        ability = StrategicResourceGenerationAbility(mock_component, data)
        rows = ability.get_ui_rows()

        assert len(rows) == 2
        assert rows[0]['label'] == 'Resource'
        assert rows[0]['value'] == 'energy'
        assert rows[1]['label'] == 'Strategic Rate'
        assert '25,000' in rows[1]['value']

    def test_stat_bindings_empty(self, mock_component):
        ability = StrategicResourceGenerationAbility(mock_component, {})
        assert ability.STAT_BINDINGS == []

    def test_resource_type_is_required_not_defaulted(self, mock_component):
        """Resource type must be explicitly specified — empty string if missing."""
        ability = StrategicResourceGenerationAbility(mock_component, {"generation_rate": 100})
        assert ability.resource == ""


# =============================================================================
# Factory Registration
# =============================================================================

class TestAbilityRegistration:
    """Tests that abilities are properly registered in the factory."""

    def test_create_planetary_shield(self, mock_component):
        data = {"energy_drain_rate": 25.0, "activation_time": 50}
        ability = create_ability("PlanetaryShield", mock_component, data)
        assert ability is not None
        assert isinstance(ability, PlanetaryShieldAbility)
        assert ability.energy_drain_rate == 25.0

    def test_create_strategic_resource_generation(self, mock_component):
        data = {"resource": "energy", "generation_rate": 25000.0}
        ability = create_ability("StrategicResourceGeneration", mock_component, data)
        assert ability is not None
        assert isinstance(ability, StrategicResourceGenerationAbility)
        assert ability.generation_rate == 25000.0
        assert ability.resource == "energy"
