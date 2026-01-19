"""
Tests for WarpJump ability.

TDD Phase 3, Step 3.1: Tests for the WarpJump ability class.
"""

import unittest
from unittest.mock import MagicMock


class TestWarpJumpAbility(unittest.TestCase):
    """Tests for the WarpJump ability class."""

    def setUp(self):
        self.mock_component = MagicMock()
        self.mock_component.ship = MagicMock()
        self.mock_component.stats = {}

    def test_warp_jump_layer_is_strategic(self):
        """WarpJump should have STRATEGIC layer."""
        from game.simulation.components.abilities.propulsion import WarpJump
        from game.simulation.components.abilities.base import AbilityLayer

        self.assertEqual(WarpJump.layer, AbilityLayer.STRATEGIC)

    def test_warp_jump_allowed_scopes_only_self(self):
        """WarpJump should only allow SELF scope (affects only the ship it's on)."""
        from game.simulation.components.abilities.propulsion import WarpJump
        from game.simulation.components.abilities.base import AbilityScope

        self.assertEqual(WarpJump.allowed_scopes, [AbilityScope.SELF])
        self.assertEqual(WarpJump.default_scope, AbilityScope.SELF)

    def test_warp_jump_max_tonnage_from_simple_data(self):
        """WarpJump should read max_tonnage from primitive data."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(self.mock_component, 5000)

        self.assertEqual(ab.max_tonnage, 5000)

    def test_warp_jump_max_tonnage_from_dict(self):
        """WarpJump should read max_tonnage from dict data."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 10000}
        ab = WarpJump(self.mock_component, data)

        self.assertEqual(ab.max_tonnage, 10000)

    def test_warp_jump_can_jump_under_limit(self):
        """can_jump() should return True when ship mass <= max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(self.mock_component, {'max_tonnage': 5000})

        self.assertTrue(ab.can_jump(4000))  # Under limit
        self.assertTrue(ab.can_jump(5000))  # At limit

    def test_warp_jump_cannot_jump_over_limit(self):
        """can_jump() should return False when ship mass > max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(self.mock_component, {'max_tonnage': 5000})

        self.assertFalse(ab.can_jump(5001))  # Over limit
        self.assertFalse(ab.can_jump(10000))  # Way over

    def test_warp_jump_ui_rows(self):
        """WarpJump should provide UI rows showing capability and limits."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(self.mock_component, {'max_tonnage': 5000})
        rows = ab.get_ui_rows()

        self.assertGreaterEqual(len(rows), 1)

        # Should indicate warp capability
        labels = [r['label'] for r in rows]
        self.assertTrue(any('Warp' in label for label in labels))

    def test_warp_jump_get_primary_value(self):
        """WarpJump.get_primary_value() should return max_tonnage."""
        from game.simulation.components.abilities.propulsion import WarpJump

        ab = WarpJump(self.mock_component, 7500)

        self.assertEqual(ab.get_primary_value(), 7500)

    def test_warp_jump_does_not_apply_to_combat(self):
        """WarpJump should NOT apply to COMBAT layer."""
        from game.simulation.components.abilities.propulsion import WarpJump
        from game.simulation.components.abilities.base import AbilityLayer

        ab = WarpJump(self.mock_component, 5000)

        self.assertFalse(ab.applies_to_layer(AbilityLayer.COMBAT))
        self.assertTrue(ab.applies_to_layer(AbilityLayer.STRATEGIC))

    def test_warp_jump_rejects_system_scope(self):
        """WarpJump should reject non-SELF scopes."""
        from game.simulation.components.abilities.propulsion import WarpJump

        data = {'max_tonnage': 5000, 'scope': 'system'}

        with self.assertRaises(ValueError):
            WarpJump(self.mock_component, data)


class TestWarpJumpRegistration(unittest.TestCase):
    """Tests for WarpJump registration in ability system."""

    def test_warp_jump_in_registry(self):
        """WarpJump should be registered in ABILITY_REGISTRY."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        self.assertIn('WarpJump', ABILITY_REGISTRY)

    def test_create_warp_jump_via_factory(self):
        """Should be able to create WarpJump via create_ability()."""
        from game.simulation.components.abilities import create_ability
        from game.simulation.components.abilities.propulsion import WarpJump

        mock_component = MagicMock()
        ab = create_ability('WarpJump', mock_component, {'max_tonnage': 8000})

        self.assertIsInstance(ab, WarpJump)
        self.assertEqual(ab.max_tonnage, 8000)


if __name__ == '__main__':
    unittest.main()
