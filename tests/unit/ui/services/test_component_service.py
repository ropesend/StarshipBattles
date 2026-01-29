"""Unit tests for ComponentService.

PROJ-43: Tests for the ComponentService facade that decouples UI from simulation.
"""
from unittest.mock import MagicMock, patch
import pytest

from game.ui.services.component_service import ComponentService


class TestComponentService:
    """Tests for ComponentService class."""

    def test_get_all_components_returns_list(self):
        """Test get_all_components returns component list from registry."""
        # Create mock registry provider
        mock_provider = MagicMock()
        mock_components = {
            'engine_1': MagicMock(name='engine_1'),
            'weapon_1': MagicMock(name='weapon_1'),
        }
        mock_provider.get_components.return_value = mock_components

        service = ComponentService(registry_provider=mock_provider)
        result = service.get_all_components()

        assert len(result) == 2
        mock_provider.get_components.assert_called_once()

    def test_get_modifier_registry_returns_dict(self):
        """Test get_modifier_registry returns modifier dict from registry."""
        mock_provider = MagicMock()
        mock_modifiers = {
            'size_mod': MagicMock(),
            'damage_mod': MagicMock(),
        }
        mock_provider.get_modifiers.return_value = mock_modifiers

        service = ComponentService(registry_provider=mock_provider)
        result = service.get_modifier_registry()

        assert result == mock_modifiers
        mock_provider.get_modifiers.assert_called_once()

    def test_get_modifier_definition_returns_definition(self):
        """Test get_modifier_definition returns specific modifier def."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.name = 'Size Mount'
        mock_provider.get_modifiers.return_value = {
            'size_mod': mock_mod_def,
        }

        service = ComponentService(registry_provider=mock_provider)
        result = service.get_modifier_definition('size_mod')

        assert result == mock_mod_def

    def test_get_modifier_definition_returns_none_for_missing(self):
        """Test get_modifier_definition returns None for unknown modifier."""
        mock_provider = MagicMock()
        mock_provider.get_modifiers.return_value = {}

        service = ComponentService(registry_provider=mock_provider)
        result = service.get_modifier_definition('nonexistent')

        assert result is None

    def test_is_modifier_allowed_no_restrictions(self):
        """Test modifier with no restrictions is always allowed."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.restrictions = None
        mock_provider.get_modifiers.return_value = {'test_mod': mock_mod_def}

        mock_component = MagicMock()
        mock_component.type_str = 'weapon'

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('test_mod', mock_component)

        assert result is True

    def test_is_modifier_allowed_with_allow_types_allowed(self):
        """Test modifier allowed when component type is in allow_types."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.restrictions = {'allow_types': ['weapon', 'engine']}
        mock_provider.get_modifiers.return_value = {'test_mod': mock_mod_def}

        mock_component = MagicMock()
        mock_component.type_str = 'weapon'

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('test_mod', mock_component)

        assert result is True

    def test_is_modifier_allowed_with_allow_types_denied(self):
        """Test modifier denied when component type not in allow_types."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.restrictions = {'allow_types': ['weapon', 'engine']}
        mock_provider.get_modifiers.return_value = {'test_mod': mock_mod_def}

        mock_component = MagicMock()
        mock_component.type_str = 'sensor'

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('test_mod', mock_component)

        assert result is False

    def test_is_modifier_allowed_with_deny_types(self):
        """Test modifier denied when component type is in deny_types."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.restrictions = {'deny_types': ['sensor']}
        mock_provider.get_modifiers.return_value = {'test_mod': mock_mod_def}

        mock_component = MagicMock()
        mock_component.type_str = 'sensor'

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('test_mod', mock_component)

        assert result is False

    def test_is_modifier_allowed_with_allow_abilities_present(self):
        """Test modifier allowed when component has required ability."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.restrictions = {'allow_abilities': ['WeaponAbility']}
        mock_provider.get_modifiers.return_value = {'test_mod': mock_mod_def}

        mock_component = MagicMock()
        mock_component.type_str = 'weapon'
        mock_component.abilities = {'WeaponAbility': {}}
        mock_component.data = {'abilities': {}}

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('test_mod', mock_component)

        assert result is True

    def test_is_modifier_allowed_with_allow_abilities_missing(self):
        """Test modifier denied when component lacks required ability."""
        mock_provider = MagicMock()
        mock_mod_def = MagicMock()
        mock_mod_def.restrictions = {'allow_abilities': ['WeaponAbility']}
        mock_provider.get_modifiers.return_value = {'test_mod': mock_mod_def}

        mock_component = MagicMock()
        mock_component.type_str = 'sensor'
        mock_component.abilities = {}
        mock_component.data = {'abilities': {}}

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('test_mod', mock_component)

        assert result is False

    def test_is_modifier_allowed_unknown_modifier(self):
        """Test is_modifier_allowed returns False for unknown modifier."""
        mock_provider = MagicMock()
        mock_provider.get_modifiers.return_value = {}

        mock_component = MagicMock()

        service = ComponentService(registry_provider=mock_provider)
        result = service.is_modifier_allowed('nonexistent', mock_component)

        assert result is False

    def test_service_uses_default_registries_when_none_provided(self):
        """Test service falls back to default registries when none injected."""
        with patch('game.ui.services.component_service.get_default_registries') as mock_get:
            mock_registries = MagicMock()
            mock_registries.get_components.return_value = {}
            mock_get.return_value = mock_registries

            service = ComponentService()
            service.get_all_components()

            mock_get.assert_called()
