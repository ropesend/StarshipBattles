"""Tests for SimpleMultiplierAbility base class (PROJ-176 Task 3.1)."""

import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.base import (
    SimpleMultiplierAbility,
    Ability,
)


# --- Test Fixture: Minimal subclass with all required class attributes ---

class TestAbility(SimpleMultiplierAbility):
    """Minimal test ability for SimpleMultiplierAbility base class tests."""
    stat_key = 'test_mult'
    value_attr = 'test_value'
    base_attr = 'base_test_value'
    ui_label = 'Test Label'
    ui_format = '{:.1f}'
    ui_color = '#FFFFFF'
    int_result = False


class TestAbilityIntResult(SimpleMultiplierAbility):
    """Test ability with int_result=True for integer casting tests."""
    stat_key = 'int_mult'
    value_attr = 'amount'
    base_attr = '_base_amount'
    ui_label = 'Amount'
    ui_format = '{}'
    ui_color = '#00FF00'
    int_result = True


# --- Test __init_subclass__ validation ---

class TestInitSubclassValidation:
    """Tests for __init_subclass__ validation of required class attributes."""

    def test_init_subclass_missing_stat_key_raises(self):
        """TypeError raised when subclass has empty stat_key."""
        with pytest.raises(TypeError, match="must set class attribute 'stat_key'"):
            class MissingStatKey(SimpleMultiplierAbility):
                stat_key = ''  # Empty string should fail
                value_attr = 'value'
                base_attr = 'base_value'
                ui_label = 'Label'

    def test_init_subclass_missing_value_attr_raises(self):
        """TypeError raised when subclass has empty value_attr."""
        with pytest.raises(TypeError, match="must set class attribute 'value_attr'"):
            class MissingValueAttr(SimpleMultiplierAbility):
                stat_key = 'some_mult'
                value_attr = ''  # Empty string should fail
                base_attr = 'base_value'
                ui_label = 'Label'

    def test_init_subclass_missing_base_attr_raises(self):
        """TypeError raised when subclass has empty base_attr."""
        with pytest.raises(TypeError, match="must set class attribute 'base_attr'"):
            class MissingBaseAttr(SimpleMultiplierAbility):
                stat_key = 'some_mult'
                value_attr = 'value'
                base_attr = ''  # Empty string should fail
                ui_label = 'Label'

    def test_init_subclass_missing_ui_label_raises(self):
        """TypeError raised when subclass has empty ui_label."""
        with pytest.raises(TypeError, match="must set class attribute 'ui_label'"):
            class MissingUILabel(SimpleMultiplierAbility):
                stat_key = 'some_mult'
                value_attr = 'value'
                base_attr = 'base_value'
                ui_label = ''  # Empty string should fail

    def test_init_subclass_valid_attributes_no_error(self):
        """No error when all required attributes are set."""
        # Should not raise any error
        class ValidAbility(SimpleMultiplierAbility):
            stat_key = 'valid_mult'
            value_attr = 'value'
            base_attr = 'base_value'
            ui_label = 'Valid Label'
        # Just verify it exists
        assert ValidAbility.stat_key == 'valid_mult'


# --- Test __init__ ---

class TestInit:
    """Tests for SimpleMultiplierAbility.__init__()."""

    def test_init_sets_base_and_value_from_primitive_data(self):
        """Init with primitive data (int/float) sets both base and value attrs."""
        component = MagicMock()
        ability = TestAbility(component, 100.5)

        assert ability.base_test_value == 100.5
        assert ability.test_value == 100.5

    def test_init_sets_base_and_value_from_dict_data(self):
        """Init with dict data parses 'value' key correctly."""
        component = MagicMock()
        ability = TestAbility(component, {'value': 250.0})

        assert ability.base_test_value == 250.0
        assert ability.test_value == 250.0

    def test_init_int_result_casts_to_int(self):
        """When int_result=True, values are cast to int."""
        component = MagicMock()
        ability = TestAbilityIntResult(component, 42.7)

        assert ability._base_amount == 42  # int cast
        assert ability.amount == 42  # int cast

    def test_init_inherits_from_ability(self):
        """SimpleMultiplierAbility instances are also Ability instances."""
        component = MagicMock()
        ability = TestAbility(component, 100)

        assert isinstance(ability, Ability)
        assert isinstance(ability, SimpleMultiplierAbility)


# --- Test sync_data ---

class TestSyncData:
    """Tests for SimpleMultiplierAbility.sync_data()."""

    def test_sync_data_updates_base_and_value(self):
        """sync_data re-parses data and resets base and value."""
        component = MagicMock()
        ability = TestAbility(component, 100.0)

        # Initial values
        assert ability.base_test_value == 100.0
        assert ability.test_value == 100.0

        # Sync with new data
        ability.sync_data({'value': 200.0})

        assert ability.base_test_value == 200.0
        assert ability.test_value == 200.0

    def test_sync_data_int_result(self):
        """sync_data respects int_result when re-parsing."""
        component = MagicMock()
        ability = TestAbilityIntResult(component, 10)

        ability.sync_data(25.9)

        assert ability._base_amount == 25  # int cast
        assert ability.amount == 25


# --- Test recalculate ---

class TestRecalculate:
    """Tests for SimpleMultiplierAbility.recalculate()."""

    def test_recalculate_applies_multiplier(self):
        """recalculate applies base * stat_multiplier."""
        component = MagicMock()
        component.stats = {'test_mult': 2.0}
        component.ability_stats = {}

        ability = TestAbility(component, 100.0)
        ability.recalculate()

        assert ability.test_value == 200.0
        assert ability.base_test_value == 100.0  # base unchanged

    def test_recalculate_default_multiplier_is_one(self):
        """If stat not present, default multiplier is 1.0."""
        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}

        ability = TestAbility(component, 100.0)
        ability.recalculate()

        assert ability.test_value == 100.0

    def test_recalculate_int_result_casts_to_int(self):
        """When int_result=True, recalculate casts result to int."""
        component = MagicMock()
        component.stats = {'int_mult': 1.5}
        component.ability_stats = {}

        ability = TestAbilityIntResult(component, 10)
        ability.recalculate()

        # 10 * 1.5 = 15 (exact), should be int
        assert ability.amount == 15
        assert isinstance(ability.amount, int)

    def test_recalculate_int_result_truncates(self):
        """int_result truncates (int() behavior, not round)."""
        component = MagicMock()
        component.stats = {'int_mult': 1.7}
        component.ability_stats = {}

        ability = TestAbilityIntResult(component, 10)
        ability.recalculate()

        # 10 * 1.7 = 17.0, should be int(17.0) = 17
        assert ability.amount == 17


# --- Test get_ui_rows ---

class TestGetUIRows:
    """Tests for SimpleMultiplierAbility.get_ui_rows()."""

    def test_get_ui_rows_format(self):
        """get_ui_rows returns formatted row with label, value, color_hint."""
        component = MagicMock()
        ability = TestAbility(component, 123.456)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Test Label'
        assert rows[0]['value'] == '123.5'  # {:.1f} format
        assert rows[0]['color_hint'] == '#FFFFFF'

    def test_get_ui_rows_int_result_format(self):
        """get_ui_rows with int_result uses correct format."""
        component = MagicMock()
        ability = TestAbilityIntResult(component, 42)

        rows = ability.get_ui_rows()

        assert rows[0]['label'] == 'Amount'
        assert rows[0]['value'] == '42'  # {} format for int
        assert rows[0]['color_hint'] == '#00FF00'


# --- Test get_primary_value ---

class TestGetPrimaryValue:
    """Tests for SimpleMultiplierAbility.get_primary_value()."""

    def test_get_primary_value_returns_float(self):
        """get_primary_value returns float of current value."""
        component = MagicMock()
        ability = TestAbility(component, 150.5)

        assert ability.get_primary_value() == 150.5
        assert isinstance(ability.get_primary_value(), float)

    def test_get_primary_value_int_ability_returns_float(self):
        """Even int_result abilities return float from get_primary_value."""
        component = MagicMock()
        ability = TestAbilityIntResult(component, 42)

        assert ability.get_primary_value() == 42.0
        assert isinstance(ability.get_primary_value(), float)
