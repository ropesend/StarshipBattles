"""
Tests for StrategicMovement ability.

TDD Phase 2, Step 2.1: Tests for the StrategicMovement ability class.
"""

import unittest
from unittest.mock import MagicMock


class TestStrategicMovementAbility(unittest.TestCase):
    """Tests for the StrategicMovement ability class."""

    def setUp(self):
        self.mock_component = MagicMock()
        self.mock_component.ship = MagicMock()
        self.mock_component.stats = {}

    def test_strategic_movement_layer_is_strategic(self):
        """StrategicMovement should have STRATEGIC layer."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityLayer

        self.assertEqual(StrategicMovement.layer, AbilityLayer.STRATEGIC)

    def test_strategic_movement_allowed_scopes(self):
        """StrategicMovement should allow SELF, ALLIED_SECTOR, and ALLIED_SYSTEM scopes."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityScope

        expected_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR, AbilityScope.ALLIED_SYSTEM]

        for scope in expected_scopes:
            self.assertIn(scope, StrategicMovement.allowed_scopes)

    def test_strategic_movement_default_scope_is_self(self):
        """StrategicMovement should default to SELF scope."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityScope

        self.assertEqual(StrategicMovement.default_scope, AbilityScope.SELF)

    def test_strategic_movement_value_from_simple_data(self):
        """StrategicMovement should read movement points from primitive data."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(self.mock_component, 150)

        self.assertEqual(ab.base_movement_points, 150)
        self.assertEqual(ab.movement_points, 150)

    def test_strategic_movement_value_from_dict_data(self):
        """StrategicMovement should read movement points from dict data."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        data = {'value': 200}
        ab = StrategicMovement(self.mock_component, data)

        self.assertEqual(ab.base_movement_points, 200)
        self.assertEqual(ab.movement_points, 200)

    def test_strategic_movement_scope_from_json(self):
        """StrategicMovement should read scope from JSON data."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityScope

        data = {'value': 100, 'scope': 'allied_system'}
        ab = StrategicMovement(self.mock_component, data)

        self.assertEqual(ab.scope, AbilityScope.ALLIED_SYSTEM)

    def test_strategic_movement_recalculate_with_modifier(self):
        """StrategicMovement should apply strategic_mult modifier on recalculate."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(self.mock_component, 100)

        # Apply modifier
        self.mock_component.stats = {'strategic_mult': 1.5}
        ab.recalculate()

        self.assertEqual(ab.base_movement_points, 100)
        self.assertEqual(ab.movement_points, 150)

    def test_strategic_movement_ui_rows(self):
        """StrategicMovement should provide UI rows for display."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(self.mock_component, 100)
        rows = ab.get_ui_rows()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['label'], 'Strategic Mobility')
        self.assertIn('100', rows[0]['value'])
        self.assertIn('MP', rows[0]['value'])

    def test_strategic_movement_get_primary_value(self):
        """StrategicMovement.get_primary_value() should return movement_points."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        ab = StrategicMovement(self.mock_component, 125)

        self.assertEqual(ab.get_primary_value(), 125)

    def test_strategic_movement_does_not_apply_to_combat(self):
        """StrategicMovement should NOT apply to COMBAT layer."""
        from game.simulation.components.abilities.propulsion import StrategicMovement
        from game.simulation.components.abilities.base import AbilityLayer

        ab = StrategicMovement(self.mock_component, 100)

        self.assertFalse(ab.applies_to_layer(AbilityLayer.COMBAT))
        self.assertTrue(ab.applies_to_layer(AbilityLayer.STRATEGIC))

    def test_strategic_movement_rejects_invalid_scope(self):
        """StrategicMovement should reject invalid scopes like PLANET."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        data = {'value': 100, 'scope': 'planet'}

        with self.assertRaises(ValueError):
            StrategicMovement(self.mock_component, data)


class TestStrategicMovementRegistration(unittest.TestCase):
    """Tests for StrategicMovement registration in ability system."""

    def test_strategic_movement_in_registry(self):
        """StrategicMovement should be registered in ABILITY_REGISTRY."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        self.assertIn('StrategicMovement', ABILITY_REGISTRY)

    def test_create_strategic_movement_via_factory(self):
        """Should be able to create StrategicMovement via create_ability()."""
        from game.simulation.components.abilities import create_ability
        from game.simulation.components.abilities.propulsion import StrategicMovement

        mock_component = MagicMock()
        ab = create_ability('StrategicMovement', mock_component, 100)

        self.assertIsInstance(ab, StrategicMovement)
        self.assertEqual(ab.movement_points, 100)


if __name__ == '__main__':
    unittest.main()
