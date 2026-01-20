"""
Tests for AbilityLayer and AbilityScope enums and base class extensions.

TDD Phase 1, Step 1.1: Foundation tests for layer/scope system.
"""

import unittest
from unittest.mock import MagicMock


class TestAbilityLayerEnum(unittest.TestCase):
    """Tests for the AbilityLayer Flag enum."""

    def test_ability_layer_enum_values(self):
        """AbilityLayer should have COMBAT, STRATEGIC, and BOTH values."""
        from game.simulation.components.abilities.base import AbilityLayer

        # Check all expected values exist
        self.assertTrue(hasattr(AbilityLayer, 'COMBAT'))
        self.assertTrue(hasattr(AbilityLayer, 'STRATEGIC'))
        self.assertTrue(hasattr(AbilityLayer, 'BOTH'))

    def test_ability_layer_both_combines_flags(self):
        """AbilityLayer.BOTH should combine COMBAT and STRATEGIC flags."""
        from game.simulation.components.abilities.base import AbilityLayer

        # BOTH should include both COMBAT and STRATEGIC
        self.assertTrue(AbilityLayer.COMBAT in AbilityLayer.BOTH)
        self.assertTrue(AbilityLayer.STRATEGIC in AbilityLayer.BOTH)

        # BOTH should equal COMBAT | STRATEGIC
        self.assertEqual(AbilityLayer.BOTH, AbilityLayer.COMBAT | AbilityLayer.STRATEGIC)

    def test_ability_layer_flag_operations(self):
        """AbilityLayer should support bitwise flag operations."""
        from game.simulation.components.abilities.base import AbilityLayer

        # Test bitwise AND
        self.assertTrue(AbilityLayer.COMBAT & AbilityLayer.BOTH)
        self.assertTrue(AbilityLayer.STRATEGIC & AbilityLayer.BOTH)
        self.assertFalse(AbilityLayer.COMBAT & AbilityLayer.STRATEGIC)


class TestAbilityScopeEnum(unittest.TestCase):
    """Tests for the AbilityScope Enum."""

    def test_ability_scope_enum_values(self):
        """AbilityScope should have all expected values."""
        from game.simulation.components.abilities.base import AbilityScope

        expected_scopes = ['SELF', 'SECTOR', 'ALLIED_SECTOR', 'SYSTEM', 'ALLIED_SYSTEM', 'PLANET']

        for scope_name in expected_scopes:
            self.assertTrue(hasattr(AbilityScope, scope_name), f"Missing scope: {scope_name}")

    def test_ability_scope_string_values(self):
        """AbilityScope values should be lowercase strings for JSON compatibility."""
        from game.simulation.components.abilities.base import AbilityScope

        self.assertEqual(AbilityScope.SELF.value, "self")
        self.assertEqual(AbilityScope.SECTOR.value, "sector")
        self.assertEqual(AbilityScope.ALLIED_SECTOR.value, "allied_sector")
        self.assertEqual(AbilityScope.SYSTEM.value, "system")
        self.assertEqual(AbilityScope.ALLIED_SYSTEM.value, "allied_system")
        self.assertEqual(AbilityScope.PLANET.value, "planet")


class TestAbilityBaseClassLayerScope(unittest.TestCase):
    """Tests for layer/scope properties on the Ability base class."""

    def setUp(self):
        self.mock_component = MagicMock()
        self.mock_component.ship = MagicMock()

    def test_ability_default_layer_is_combat(self):
        """Ability base class should default to COMBAT layer."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Base Ability class-level default
        self.assertEqual(Ability.layer, AbilityLayer.COMBAT)

    def test_ability_default_scope_is_self(self):
        """Ability base class should default to SELF scope."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Base Ability class-level defaults
        self.assertEqual(Ability.default_scope, AbilityScope.SELF)
        self.assertIn(AbilityScope.SELF, Ability.allowed_scopes)

    def test_ability_applies_to_layer_combat(self):
        """applies_to_layer() should correctly check COMBAT layer."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Create ability instance
        ab = Ability(self.mock_component, {})

        # Default layer is COMBAT, so should apply to COMBAT
        self.assertTrue(ab.applies_to_layer(AbilityLayer.COMBAT))

        # Should not apply to STRATEGIC alone
        self.assertFalse(ab.applies_to_layer(AbilityLayer.STRATEGIC))

    def test_ability_applies_to_layer_strategic(self):
        """applies_to_layer() should work for STRATEGIC layer abilities."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Create a subclass with STRATEGIC layer
        class StrategicAbility(Ability):
            layer = AbilityLayer.STRATEGIC

        ab = StrategicAbility(self.mock_component, {})

        self.assertTrue(ab.applies_to_layer(AbilityLayer.STRATEGIC))
        self.assertFalse(ab.applies_to_layer(AbilityLayer.COMBAT))

    def test_ability_applies_to_layer_both(self):
        """applies_to_layer() should work for BOTH layer abilities."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Create a subclass with BOTH layers
        class DualLayerAbility(Ability):
            layer = AbilityLayer.BOTH

        ab = DualLayerAbility(self.mock_component, {})

        self.assertTrue(ab.applies_to_layer(AbilityLayer.COMBAT))
        self.assertTrue(ab.applies_to_layer(AbilityLayer.STRATEGIC))
        self.assertTrue(ab.applies_to_layer(AbilityLayer.BOTH))

    def test_ability_scope_from_json_data(self):
        """Ability should read scope from JSON data."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Create subclass that allows multiple scopes
        class FlexibleAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR, AbilityScope.ALLIED_SYSTEM]
            default_scope = AbilityScope.SELF

        # Test with scope in data
        data = {'value': 100, 'scope': 'allied_system'}
        ab = FlexibleAbility(self.mock_component, data)

        self.assertEqual(ab.scope, AbilityScope.ALLIED_SYSTEM)

    def test_ability_scope_uses_default_when_not_specified(self):
        """Ability should use default_scope when JSON doesn't specify scope."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Create subclass with custom default
        class DefaultScopeAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.SECTOR]
            default_scope = AbilityScope.SECTOR

        # Data without scope
        data = {'value': 100}
        ab = DefaultScopeAbility(self.mock_component, data)

        self.assertEqual(ab.scope, AbilityScope.SECTOR)

    def test_ability_scope_validation_rejects_invalid(self):
        """Ability should reject scope values not in allowed_scopes."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Create subclass with restricted scopes
        class RestrictedAbility(Ability):
            allowed_scopes = [AbilityScope.SELF]  # Only SELF allowed
            default_scope = AbilityScope.SELF

        # Try to use disallowed scope
        data = {'value': 100, 'scope': 'system'}

        with self.assertRaises(ValueError) as context:
            RestrictedAbility(self.mock_component, data)

        self.assertIn('does not support scope', str(context.exception))

    def test_ability_scope_handles_primitive_data(self):
        """Ability should handle primitive (non-dict) data gracefully."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # When data is a primitive (e.g., just a number), should use default scope
        ab = Ability(self.mock_component, 100)

        self.assertEqual(ab.scope, AbilityScope.SELF)


class TestAbilityAllowedScopes(unittest.TestCase):
    """Tests for the allowed_scopes class attribute."""

    def setUp(self):
        self.mock_component = MagicMock()
        self.mock_component.ship = MagicMock()

    def test_ability_allowed_scopes_is_list(self):
        """allowed_scopes should be a list of AbilityScope values."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        self.assertIsInstance(Ability.allowed_scopes, list)
        for scope in Ability.allowed_scopes:
            self.assertIsInstance(scope, AbilityScope)

    def test_subclass_can_define_custom_allowed_scopes(self):
        """Subclasses should be able to define their own allowed_scopes."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        class SystemWideAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM]

        self.assertEqual(len(SystemWideAbility.allowed_scopes), 3)
        self.assertIn(AbilityScope.SYSTEM, SystemWideAbility.allowed_scopes)


if __name__ == '__main__':
    unittest.main()
