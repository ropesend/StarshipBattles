"""
Tests for AbilityLayer and AbilityScope enums and base class extensions.

TDD Phase 1, Step 1.1: Foundation tests for layer/scope system.
"""

import pytest
from unittest.mock import MagicMock

from game.core.exceptions import ValidationException


class TestAbilityLayerEnum:
    """Tests for the AbilityLayer Flag enum."""

    def test_ability_layer_enum_values(self):
        """AbilityLayer should have COMBAT, STRATEGIC, and BOTH values."""
        from game.simulation.components.abilities.base import AbilityLayer

        # Check all expected values exist
        assert hasattr(AbilityLayer, 'COMBAT')
        assert hasattr(AbilityLayer, 'STRATEGIC')
        assert hasattr(AbilityLayer, 'BOTH')

    def test_ability_layer_both_combines_flags(self):
        """AbilityLayer.BOTH should combine COMBAT and STRATEGIC flags."""
        from game.simulation.components.abilities.base import AbilityLayer

        # BOTH should include both COMBAT and STRATEGIC
        assert AbilityLayer.COMBAT in AbilityLayer.BOTH
        assert AbilityLayer.STRATEGIC in AbilityLayer.BOTH

        # BOTH should equal COMBAT | STRATEGIC
        assert AbilityLayer.BOTH == AbilityLayer.COMBAT | AbilityLayer.STRATEGIC

    def test_ability_layer_flag_operations(self):
        """AbilityLayer should support bitwise flag operations."""
        from game.simulation.components.abilities.base import AbilityLayer

        # Test bitwise AND
        assert AbilityLayer.COMBAT & AbilityLayer.BOTH
        assert AbilityLayer.STRATEGIC & AbilityLayer.BOTH
        assert not (AbilityLayer.COMBAT & AbilityLayer.STRATEGIC)


class TestAbilityScopeEnum:
    """Tests for the AbilityScope Enum."""

    def test_ability_scope_enum_values(self):
        """AbilityScope should have all expected values."""
        from game.simulation.components.abilities.base import AbilityScope

        expected_scopes = ['SELF', 'SECTOR', 'ALLIED_SECTOR', 'SYSTEM', 'ALLIED_SYSTEM', 'PLANET']

        for scope_name in expected_scopes:
            assert hasattr(AbilityScope, scope_name), f"Missing scope: {scope_name}"

    def test_ability_scope_string_values(self):
        """AbilityScope values should be lowercase strings for JSON compatibility."""
        from game.simulation.components.abilities.base import AbilityScope

        assert AbilityScope.SELF.value == "self"
        assert AbilityScope.SECTOR.value == "sector"
        assert AbilityScope.ALLIED_SECTOR.value == "allied_sector"
        assert AbilityScope.SYSTEM.value == "system"
        assert AbilityScope.ALLIED_SYSTEM.value == "allied_system"
        assert AbilityScope.PLANET.value == "planet"


class TestAbilityBaseClassLayerScope:
    """Tests for layer/scope properties on the Ability base class."""

    @pytest.fixture
    def mock_component(self):
        mock = MagicMock()
        mock.ship = MagicMock()
        return mock

    def test_ability_default_layer_is_combat(self):
        """Ability base class should default to COMBAT layer."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Base Ability class-level default
        assert Ability.layer == AbilityLayer.COMBAT

    def test_ability_default_scope_is_self(self):
        """Ability base class should default to SELF scope."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Base Ability class-level defaults
        assert Ability.default_scope == AbilityScope.SELF
        assert AbilityScope.SELF in Ability.allowed_scopes

    def test_ability_applies_to_layer_combat(self, mock_component):
        """applies_to_layer() should correctly check COMBAT layer."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Create ability instance
        ab = Ability(mock_component, {})

        # Default layer is COMBAT, so should apply to COMBAT
        assert ab.applies_to_layer(AbilityLayer.COMBAT) is True

        # Should not apply to STRATEGIC alone
        assert ab.applies_to_layer(AbilityLayer.STRATEGIC) is False

    def test_ability_applies_to_layer_strategic(self, mock_component):
        """applies_to_layer() should work for STRATEGIC layer abilities."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Create a subclass with STRATEGIC layer
        class StrategicAbility(Ability):
            layer = AbilityLayer.STRATEGIC

        ab = StrategicAbility(mock_component, {})

        assert ab.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ab.applies_to_layer(AbilityLayer.COMBAT) is False

    def test_ability_applies_to_layer_both(self, mock_component):
        """applies_to_layer() should work for BOTH layer abilities."""
        from game.simulation.components.abilities.base import Ability, AbilityLayer

        # Create a subclass with BOTH layers
        class DualLayerAbility(Ability):
            layer = AbilityLayer.BOTH

        ab = DualLayerAbility(mock_component, {})

        assert ab.applies_to_layer(AbilityLayer.COMBAT) is True
        assert ab.applies_to_layer(AbilityLayer.STRATEGIC) is True
        assert ab.applies_to_layer(AbilityLayer.BOTH) is True

    def test_ability_scope_from_json_data(self, mock_component):
        """Ability should read scope from JSON data."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Create subclass that allows multiple scopes
        class FlexibleAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR, AbilityScope.ALLIED_SYSTEM]
            default_scope = AbilityScope.SELF

        # Test with scope in data
        data = {'value': 100, 'scope': 'allied_system'}
        ab = FlexibleAbility(mock_component, data)

        assert ab.scope == AbilityScope.ALLIED_SYSTEM

    def test_ability_scope_uses_default_when_not_specified(self, mock_component):
        """Ability should use default_scope when JSON doesn't specify scope."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Create subclass with custom default
        class DefaultScopeAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.SECTOR]
            default_scope = AbilityScope.SECTOR

        # Data without scope
        data = {'value': 100}
        ab = DefaultScopeAbility(mock_component, data)

        assert ab.scope == AbilityScope.SECTOR

    def test_ability_scope_validation_rejects_invalid(self, mock_component):
        """Ability should reject scope values not in allowed_scopes."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # Create subclass with restricted scopes
        class RestrictedAbility(Ability):
            allowed_scopes = [AbilityScope.SELF]  # Only SELF allowed
            default_scope = AbilityScope.SELF

        # Try to use disallowed scope
        data = {'value': 100, 'scope': 'system'}

        with pytest.raises(ValidationException) as exc_info:
            RestrictedAbility(mock_component, data)

        assert 'does not support scope' in str(exc_info.value)

    def test_ability_scope_handles_primitive_data(self, mock_component):
        """Ability should handle primitive (non-dict) data gracefully."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        # When data is a primitive (e.g., just a number), should use default scope
        ab = Ability(mock_component, 100)

        assert ab.scope == AbilityScope.SELF


class TestAbilityAllowedScopes:
    """Tests for the allowed_scopes class attribute."""

    @pytest.fixture
    def mock_component(self):
        mock = MagicMock()
        mock.ship = MagicMock()
        return mock

    def test_ability_allowed_scopes_is_list(self):
        """allowed_scopes should be a list of AbilityScope values."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        assert isinstance(Ability.allowed_scopes, list)
        for scope in Ability.allowed_scopes:
            assert isinstance(scope, AbilityScope)

    def test_subclass_can_define_custom_allowed_scopes(self):
        """Subclasses should be able to define their own allowed_scopes."""
        from game.simulation.components.abilities.base import Ability, AbilityScope

        class SystemWideAbility(Ability):
            allowed_scopes = [AbilityScope.SELF, AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM]

        assert len(SystemWideAbility.allowed_scopes) == 3
        assert AbilityScope.SYSTEM in SystemWideAbility.allowed_scopes
