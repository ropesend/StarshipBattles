"""
Tests for StrategicMovement ability.

TDD Phase 2, Step 2.1: Tests for the StrategicMovement ability class.
"""

import pytest
from unittest.mock import MagicMock


class TestStrategicMovementAbility:
    """Tests for the StrategicMovement ability class."""

    @pytest.fixture
    def mock_component(self):
        mock = MagicMock()
        mock.ship = MagicMock()
        mock.stats = {}
        return mock

    def test_strategic_movement_layer_is_strategic(self):
        """StrategicMovement should have STRATEGIC layer."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityLayer

        assert StrategicMovement.layer == AbilityLayer.STRATEGIC

    def test_strategic_movement_allowed_scopes(self):
        """StrategicMovement should allow SELF, ALLIED_SECTOR, and ALLIED_SYSTEM scopes."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityScope

        expected_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR, AbilityScope.ALLIED_SYSTEM]

        for scope in expected_scopes:
            assert scope in StrategicMovement.allowed_scopes

    def test_strategic_movement_default_scope_is_self(self):
        """StrategicMovement should default to SELF scope."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityScope

        assert StrategicMovement.default_scope == AbilityScope.SELF

    def test_strategic_movement_value_from_simple_data(self, mock_component):
        """StrategicMovement should read movement points from primitive data."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(mock_component, 150)

        assert ab.base_movement_points == 150
        assert ab.movement_points == 150

    def test_strategic_movement_value_from_dict_data(self, mock_component):
        """StrategicMovement should read movement points from dict data."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        data = {'value': 200}
        ab = StrategicMovement(mock_component, data)

        assert ab.base_movement_points == 200
        assert ab.movement_points == 200

    def test_strategic_movement_scope_from_json(self, mock_component):
        """StrategicMovement should read scope from JSON data."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityScope

        data = {'value': 100, 'scope': 'allied_system'}
        ab = StrategicMovement(mock_component, data)

        assert ab.scope == AbilityScope.ALLIED_SYSTEM

    def test_strategic_movement_recalculate_with_modifier(self, mock_component):
        """StrategicMovement should apply strategic_mult modifier on recalculate."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(mock_component, 100)

        # Apply modifier
        mock_component.stats = {'strategic_mult': 1.5}
        ab.recalculate()

        assert ab.base_movement_points == 100
        assert ab.movement_points == 150

    def test_strategic_movement_ui_rows(self, mock_component):
        """StrategicMovement should provide UI rows for display."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(mock_component, 100)
        rows = ab.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Strategic Mobility'
        assert '100' in rows[0]['value']
        assert 'MP' in rows[0]['value']

    def test_strategic_movement_get_primary_value(self, mock_component):
        """StrategicMovement.get_primary_value() should return movement_points."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(mock_component, 125)

        assert ab.get_primary_value() == 125

    def test_strategic_movement_does_not_apply_to_combat(self, mock_component):
        """StrategicMovement should NOT apply to COMBAT layer."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityLayer

        ab = StrategicMovement(mock_component, 100)

        assert ab.applies_to_layer(AbilityLayer.COMBAT) is False
        assert ab.applies_to_layer(AbilityLayer.STRATEGIC) is True

    def test_strategic_movement_rejects_invalid_scope(self, mock_component):
        """StrategicMovement should reject invalid scopes like PLANET."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        data = {'value': 100, 'scope': 'planet'}

        with pytest.raises(ValueError):
            StrategicMovement(mock_component, data)


class TestStrategicMovementRegistration:
    """Tests for StrategicMovement registration in ability system."""

    def test_strategic_movement_in_registry(self):
        """StrategicMovement should be registered in ABILITY_REGISTRY."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        assert 'StrategicMovement' in ABILITY_REGISTRY

    def test_create_strategic_movement_via_factory(self):
        """Should be able to create StrategicMovement via create_ability()."""
        from game.simulation.components.abilities import create_ability
        from game.simulation.components.abilities.propulsion import StrategicMovement

        mock_component = MagicMock()
        ab = create_ability('StrategicMovement', mock_component, 100)

        assert isinstance(ab, StrategicMovement)
        assert ab.movement_points == 100
