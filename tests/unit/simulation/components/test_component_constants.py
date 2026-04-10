"""
Unit tests for component_constants.py.

Tests ComponentStatus enum, Modifier class, and ApplicationModifier class.
"""
import pytest

from game.simulation.components.component_constants import (
    ComponentStatus, Modifier, ApplicationModifier
)


class TestComponentStatusEnum:
    """Tests for ComponentStatus enum."""

    def test_component_status_all_unique(self):
        """All enum values are distinct."""
        values = [status.value for status in ComponentStatus]
        assert len(values) == len(set(values))


class TestModifierInit:
    """Tests for Modifier class initialization."""

    def test_modifier_init_minimal(self):
        """Modifier({'id': 'test', 'effects': []}) works."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        assert mod.id == 'test'
        assert mod.effects == []

    def test_modifier_init_all_fields(self):
        """Name, description, restrictions, readonly parsed."""
        data = {
            'id': 'test_mod',
            'name': 'Test Modifier',
            'description': 'A test modifier',
            'restrictions': {'allow_abilities': ['WeaponAbility']},
            'readonly': True,
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }
        mod = Modifier(data)
        assert mod.id == 'test_mod'
        assert mod.name == 'Test Modifier'
        assert mod.description == 'A test modifier'
        assert mod.restrictions == {'allow_abilities': ['WeaponAbility']}
        assert mod.readonly is True

    def test_modifier_default_name_is_id(self):
        """name defaults to id when not provided."""
        data = {'id': 'my_modifier', 'effects': []}
        mod = Modifier(data)
        assert mod.name == 'my_modifier'

    def test_modifier_default_description_empty(self):
        """description defaults to empty string."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        assert mod.description == ''

    def test_modifier_default_restrictions_empty(self):
        """restrictions defaults to empty dict."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        assert mod.restrictions == {}

    def test_modifier_default_readonly_false(self):
        """readonly defaults to False."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        assert mod.readonly is False


class TestModifierParams:
    """Tests for Modifier parameter handling."""

    def test_modifier_param_min_max_default(self):
        """min_val, max_val, default_val from param dict."""
        data = {
            'id': 'test',
            'effects': [],
            'param': {'min': 10, 'max': 200, 'default': 50}
        }
        mod = Modifier(data)
        assert mod.min_val == 10
        assert mod.max_val == 200
        assert mod.default_val == 50

    def test_modifier_param_defaults_when_missing(self):
        """min=0, max=100, default=min_val when no param."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        assert mod.min_val == 0
        assert mod.max_val == 100
        assert mod.default_val == 0  # Defaults to min_val

    def test_modifier_param_default_uses_min_when_omitted(self):
        """default_val uses min_val when default not specified."""
        data = {
            'id': 'test',
            'effects': [],
            'param': {'min': 25, 'max': 75}
        }
        mod = Modifier(data)
        assert mod.default_val == 25  # Uses min_val


class TestModifierCreateModifier:
    """Tests for Modifier.create_modifier method."""

    def test_modifier_create_modifier_returns_application(self):
        """Returns ApplicationModifier instance."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        app_mod = mod.create_modifier()
        assert isinstance(app_mod, ApplicationModifier)

    def test_modifier_create_modifier_with_value(self):
        """ApplicationModifier gets specified value."""
        data = {'id': 'test', 'effects': [], 'param': {'default': 50}}
        mod = Modifier(data)
        app_mod = mod.create_modifier(value=75)
        assert app_mod.value == 75

    def test_modifier_create_modifier_default_value(self):
        """ApplicationModifier gets default when no value."""
        data = {'id': 'test', 'effects': [], 'param': {'default': 42}}
        mod = Modifier(data)
        app_mod = mod.create_modifier()
        assert app_mod.value == 42


class TestApplicationModifier:
    """Tests for ApplicationModifier class."""

    def test_application_modifier_stores_definition(self):
        """definition attribute set."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        app_mod = ApplicationModifier(mod, 50)
        assert app_mod.definition is mod

    def test_application_modifier_stores_value(self):
        """value attribute set."""
        data = {'id': 'test', 'effects': []}
        mod = Modifier(data)
        app_mod = ApplicationModifier(mod, 75)
        assert app_mod.value == 75

    def test_application_modifier_default_value(self):
        """Uses mod_def.default_val when value is None."""
        data = {'id': 'test', 'effects': [], 'param': {'default': 33}}
        mod = Modifier(data)
        app_mod = ApplicationModifier(mod, None)
        assert app_mod.value == 33
