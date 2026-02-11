"""
Unit tests for superweapon abilities.

PROJ-102: Strategic Superweapons and Special Orders - Phase 1
"""

import pytest
from unittest.mock import Mock

from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    create_ability,
)
from game.simulation.components.abilities.base import AbilityLayer, AbilityScope


# Mapping of ability class names to their expected UI values
SUPERWEAPON_ABILITIES = {
    "DestroyPlanet": "Planet Imploder",
    "DestroyStar": "Stellerator",
    "OpenWarpPoint": "Warp Point Creator",
    "CloseWarpPoint": "Warp Point Closer",
    "CreateDysonSphere": "Dyson Sphere Constructor",
    "SelfDestruct": "Self-Destruct Device",
}


@pytest.fixture
def mock_component():
    """Create a mock component for ability testing."""
    component = Mock()
    component.stats = {}
    component.ability_stats = {}
    return component


class TestSuperweaponAbilityInstantiation:
    """Test that all superweapon abilities can be instantiated."""

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_ability_instantiates(self, mock_component, ability_name):
        """Each ability should instantiate without error."""
        ability_class = ABILITY_REGISTRY.get(ability_name)
        assert ability_class is not None, f"{ability_name} not in ABILITY_REGISTRY"

        ability = ability_class(mock_component, True)
        assert ability is not None
        assert ability.component == mock_component

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_ability_via_create_ability(self, mock_component, ability_name):
        """Each ability should be creatable via create_ability factory."""
        ability = create_ability(ability_name, mock_component, True)
        assert ability is not None
        assert ability.component == mock_component


class TestSuperweaponAbilityLayer:
    """Test that all superweapon abilities have strategic layer."""

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_layer_is_strategic(self, mock_component, ability_name):
        """All superweapon abilities should have STRATEGIC layer."""
        ability_class = ABILITY_REGISTRY[ability_name]
        ability = ability_class(mock_component, True)

        assert ability.layer == AbilityLayer.STRATEGIC
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC)
        # Should NOT apply to combat layer
        assert not ability.applies_to_layer(AbilityLayer.COMBAT)


class TestSuperweaponAbilityScope:
    """Test that all superweapon abilities have SELF scope."""

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_allowed_scopes_is_self_only(self, mock_component, ability_name):
        """All superweapon abilities should only allow SELF scope."""
        ability_class = ABILITY_REGISTRY[ability_name]
        assert ability_class.allowed_scopes == [AbilityScope.SELF]

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_default_scope_is_self(self, mock_component, ability_name):
        """All superweapon abilities should default to SELF scope."""
        ability_class = ABILITY_REGISTRY[ability_name]
        ability = ability_class(mock_component, True)

        assert ability.scope == AbilityScope.SELF


class TestSuperweaponAbilityStats:
    """Test that all superweapon abilities are marker abilities with no stats."""

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_stat_bindings_empty(self, mock_component, ability_name):
        """All superweapon abilities should have empty STAT_BINDINGS."""
        ability_class = ABILITY_REGISTRY[ability_name]
        assert ability_class.STAT_BINDINGS == []

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_get_primary_value_returns_zero(self, mock_component, ability_name):
        """All superweapon abilities should return 0.0 for get_primary_value."""
        ability_class = ABILITY_REGISTRY[ability_name]
        ability = ability_class(mock_component, True)

        assert ability.get_primary_value() == 0.0


class TestSuperweaponAbilityUIRows:
    """Test that all superweapon abilities return proper UI rows."""

    @pytest.mark.parametrize("ability_name,expected_value", SUPERWEAPON_ABILITIES.items())
    def test_get_ui_rows_returns_superweapon_row(self, mock_component, ability_name, expected_value):
        """Each ability should return a UI row with correct label and value."""
        ability_class = ABILITY_REGISTRY[ability_name]
        ability = ability_class(mock_component, True)

        ui_rows = ability.get_ui_rows()

        assert len(ui_rows) == 1
        row = ui_rows[0]
        assert row['label'] == 'Superweapon'
        assert row['value'] == expected_value
        assert 'color_hint' in row
        assert row['color_hint'] == '#FF4444'  # Red for superweapons


class TestSuperweaponRegistryPresence:
    """Test that all abilities are properly registered."""

    @pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())
    def test_ability_in_registry(self, ability_name):
        """Each ability should exist in ABILITY_REGISTRY."""
        assert ability_name in ABILITY_REGISTRY

    def test_all_six_abilities_registered(self):
        """All 6 superweapon abilities should be in the registry."""
        for ability_name in SUPERWEAPON_ABILITIES:
            assert ability_name in ABILITY_REGISTRY, f"{ability_name} missing from registry"

        # Verify count
        assert len(SUPERWEAPON_ABILITIES) == 6
