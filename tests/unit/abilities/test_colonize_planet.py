"""
Tests for ColonizePlanet ability.

TDD Phase 1: Tests for the ColonizePlanet ability class.
PROJ-55: Data-Driven Planet-Specific Colonization System
"""

import pytest
from unittest.mock import MagicMock

from game.core.exceptions import ValidationException


# All 11 planet types as defined in the planet system
ALL_PLANET_TYPES = [
    "CONTINENTAL",
    "ARID",
    "PELAGIC",
    "MAGMA",
    "CRYOPLANET",
    "BARREN",
    "JOVIAN",
    "ICE_GIANT",
    "CHTHONIAN",
    "ICE_DWARF",
    "PLANETOID",
]


class TestColonizePlanetAbility:
    """Tests for the ColonizePlanet ability class."""

    @pytest.fixture
    def mock_component(self):
        mock = MagicMock()
        mock.ship = MagicMock()
        mock.stats = {}
        return mock

    def test_colonize_planet_layer_is_strategic(self):
        """ColonizePlanet should have STRATEGIC layer."""
        from game.simulation.components.abilities.colonize import ColonizePlanet
        from game.simulation.components.abilities.base import AbilityLayer

        assert ColonizePlanet.layer == AbilityLayer.STRATEGIC

    def test_colonize_planet_allowed_scopes_is_self_only(self):
        """ColonizePlanet should only allow SELF scope."""
        from game.simulation.components.abilities.colonize import ColonizePlanet
        from game.simulation.components.abilities.base import AbilityScope

        assert ColonizePlanet.allowed_scopes == [AbilityScope.SELF]

    def test_colonize_planet_default_scope_is_self(self):
        """ColonizePlanet should default to SELF scope."""
        from game.simulation.components.abilities.colonize import ColonizePlanet
        from game.simulation.components.abilities.base import AbilityScope

        assert ColonizePlanet.default_scope == AbilityScope.SELF

    def test_colonize_planet_dict_format(self, mock_component):
        """ColonizePlanet should read planet_type from dict format."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        data = {"planet_type": "ICE_DWARF"}
        ability = ColonizePlanet(mock_component, data)

        assert ability is not None
        assert ability.planet_type == "ICE_DWARF"

    def test_colonize_planet_string_shorthand(self, mock_component):
        """ColonizePlanet should read planet_type from string shorthand."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        ability = ColonizePlanet(mock_component, "CONTINENTAL")

        assert ability is not None
        assert ability.planet_type == "CONTINENTAL"

    def test_colonize_planet_ui_display_ice_dwarf(self, mock_component):
        """ColonizePlanet should display formatted planet type in UI."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        ability = ColonizePlanet(mock_component, "ICE_DWARF")
        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Colonizes'
        assert rows[0]['value'] == 'Ice Dwarf'
        assert 'color_hint' in rows[0]

    def test_colonize_planet_ui_display_continental(self, mock_component):
        """ColonizePlanet should display single-word planet types correctly."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        ability = ColonizePlanet(mock_component, "CONTINENTAL")
        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['value'] == 'Continental'

    def test_colonize_planet_ui_display_ice_giant(self, mock_component):
        """ColonizePlanet should display Ice Giant correctly."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        ability = ColonizePlanet(mock_component, "ICE_GIANT")
        rows = ability.get_ui_rows()

        assert rows[0]['value'] == 'Ice Giant'

    @pytest.mark.parametrize("planet_type", ALL_PLANET_TYPES)
    def test_all_11_planet_types_supported(self, mock_component, planet_type):
        """ColonizePlanet should successfully instantiate for all 11 planet types."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        # Should not raise any exception
        ability = ColonizePlanet(mock_component, planet_type)

        assert ability.planet_type == planet_type

    def test_colonize_planet_does_not_apply_to_combat(self, mock_component):
        """ColonizePlanet should NOT apply to COMBAT layer."""
        from game.simulation.components.abilities.colonize import ColonizePlanet
        from game.simulation.components.abilities.base import AbilityLayer

        ability = ColonizePlanet(mock_component, "BARREN")

        assert ability.applies_to_layer(AbilityLayer.COMBAT) is False
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC) is True

    def test_colonize_planet_rejects_invalid_scope(self, mock_component):
        """ColonizePlanet should reject scopes other than SELF."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        data = {"planet_type": "CONTINENTAL", "scope": "planet"}

        with pytest.raises(ValidationException):
            ColonizePlanet(mock_component, data)

    def test_colonize_planet_get_primary_value_returns_zero(self, mock_component):
        """ColonizePlanet.get_primary_value() should return 0 (marker ability)."""
        from game.simulation.components.abilities.colonize import ColonizePlanet

        ability = ColonizePlanet(mock_component, "JOVIAN")

        # Marker ability - no numeric primary value
        assert ability.get_primary_value() == 0.0

    def test_colonize_planet_scope_defaults_to_self(self, mock_component):
        """ColonizePlanet instance scope should be SELF."""
        from game.simulation.components.abilities.colonize import ColonizePlanet
        from game.simulation.components.abilities.base import AbilityScope

        ability = ColonizePlanet(mock_component, "MAGMA")

        assert ability.scope == AbilityScope.SELF


class TestColonizePlanetRegistration:
    """Tests for ColonizePlanet registration in ability system."""

    def test_colonize_planet_in_registry(self):
        """ColonizePlanet should be registered in ABILITY_REGISTRY."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        assert 'ColonizePlanet' in ABILITY_REGISTRY

    def test_create_colonize_planet_via_factory(self):
        """Should be able to create ColonizePlanet via create_ability()."""
        from game.simulation.components.abilities import create_ability
        from game.simulation.components.abilities.colonize import ColonizePlanet

        mock_component = MagicMock()
        ability = create_ability('ColonizePlanet', mock_component, "PELAGIC")

        assert isinstance(ability, ColonizePlanet)
        assert ability.planet_type == "PELAGIC"

    def test_create_colonize_planet_via_factory_dict_format(self):
        """Should be able to create ColonizePlanet via create_ability() with dict."""
        from game.simulation.components.abilities import create_ability
        from game.simulation.components.abilities.colonize import ColonizePlanet

        mock_component = MagicMock()
        data = {"planet_type": "CHTHONIAN"}
        ability = create_ability('ColonizePlanet', mock_component, data)

        assert isinstance(ability, ColonizePlanet)
        assert ability.planet_type == "CHTHONIAN"

    def test_colonize_planet_in_all_exports(self):
        """ColonizePlanet should be in __all__ exports."""
        from game.simulation.components import abilities

        assert 'ColonizePlanet' in abilities.__all__
