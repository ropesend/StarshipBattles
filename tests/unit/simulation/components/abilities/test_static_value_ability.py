"""
Tests for StaticValueAbility base class.

StaticValueAbility provides a base for abilities that hold a static value
with no modifier stat bindings. Subclasses configure behavior via class attributes.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.base import StaticValueAbility, Ability
from game.simulation.components.abilities.defense import (
    ToHitAttackModifier,
    ToHitDefenseModifier,
    EmissiveArmor,
)
from game.simulation.components.abilities.ui_colors import (
    HINT_DAMAGE,
    HINT_EVASION,
    HINT_ACCURACY,
)


@pytest.fixture
def mock_component():
    """Create a mock component with default empty stats."""
    component = MagicMock()
    component.stats = {}
    component.ability_stats = {}
    return component


# =============================================================================
# StaticValueAbility Base Class Tests
# =============================================================================

class TestStaticValueAbility:
    """Tests for StaticValueAbility base class behavior."""

    def test_is_subclass_of_ability(self):
        """StaticValueAbility inherits from Ability."""
        assert issubclass(StaticValueAbility, Ability)

    def test_has_empty_stat_bindings(self):
        """StaticValueAbility has empty STAT_BINDINGS."""
        assert StaticValueAbility.STAT_BINDINGS == []

    def test_subclass_requires_ui_label(self):
        """Subclass without ui_label raises TypeError."""
        with pytest.raises(TypeError, match="must set class attribute 'ui_label'"):
            class BadAbility(StaticValueAbility):
                ui_color = '#FFFFFF'
                ui_format = '{}'

    def test_subclass_requires_ui_color(self):
        """Subclass without ui_color raises TypeError."""
        with pytest.raises(TypeError, match="must set class attribute 'ui_color'"):
            class BadAbility(StaticValueAbility):
                ui_label = 'Test'
                ui_format = '{}'

    def test_valid_subclass_creation(self, mock_component):
        """Valid subclass can be instantiated."""
        class TestAbility(StaticValueAbility):
            ui_label = 'Test'
            ui_color = '#FF0000'
            ui_format = '{:.0f}'

        ability = TestAbility(mock_component, 42)
        assert ability.value == 42.0
        assert ability._base_value == 42.0

    def test_init_with_dict(self, mock_component):
        """Init from dict with 'value' key."""
        class TestAbility(StaticValueAbility):
            ui_label = 'Test'
            ui_color = '#FF0000'

        ability = TestAbility(mock_component, {'value': 99})
        assert ability.value == 99.0

    def test_init_with_int_cast(self, mock_component):
        """int_result=True casts to int."""
        class IntAbility(StaticValueAbility):
            ui_label = 'Test'
            ui_color = '#FF0000'
            int_result = True

        ability = IntAbility(mock_component, 7.9)
        assert ability.value == 7
        assert isinstance(ability.value, int)

    def test_recalculate_is_no_op(self, mock_component):
        """recalculate does not change value."""
        class TestAbility(StaticValueAbility):
            ui_label = 'Test'
            ui_color = '#FF0000'

        ability = TestAbility(mock_component, 50)
        ability.recalculate()
        assert ability.value == 50.0

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns float value."""
        class TestAbility(StaticValueAbility):
            ui_label = 'Test'
            ui_color = '#FF0000'

        ability = TestAbility(mock_component, 25)
        assert ability.get_primary_value() == 25.0
        assert isinstance(ability.get_primary_value(), float)

    def test_get_ui_rows_default_format(self, mock_component):
        """get_ui_rows uses default format '{:.1f}'."""
        class TestAbility(StaticValueAbility):
            ui_label = 'Score'
            ui_color = '#00FF00'

        ability = TestAbility(mock_component, 5.0)
        rows = ability.get_ui_rows()
        assert len(rows) == 1
        assert rows[0]['label'] == 'Score'
        assert rows[0]['value'] == '5.0'
        assert rows[0]['color_hint'] == '#00FF00'

    def test_get_ui_rows_custom_format(self, mock_component):
        """get_ui_rows uses custom format string."""
        class TestAbility(StaticValueAbility):
            ui_label = 'HP'
            ui_color = '#FF0000'
            ui_format = '{:.0f}'

        ability = TestAbility(mock_component, 100.7)
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '101'

    def test_get_ui_rows_signed_format(self, mock_component):
        """get_ui_rows with signed format shows +/- sign."""
        class SignedAbility(StaticValueAbility):
            ui_label = 'Bonus'
            ui_color = '#FFFF00'
            ui_format = '{:+.1f}'

        pos = SignedAbility(mock_component, 5)
        assert pos.get_ui_rows()[0]['value'] == '+5.0'

        neg = SignedAbility(mock_component, -3)
        assert neg.get_ui_rows()[0]['value'] == '-3.0'


# =============================================================================
# Concrete Subclass Tests (verify they still work after refactor)
# =============================================================================

class TestToHitAttackModifierIsStaticValue:
    """Verify ToHitAttackModifier uses StaticValueAbility."""

    def test_inherits_from_static_value_ability(self):
        """ToHitAttackModifier is a StaticValueAbility subclass."""
        assert issubclass(ToHitAttackModifier, StaticValueAbility)

    def test_class_attributes(self):
        """ToHitAttackModifier has correct class attributes."""
        assert ToHitAttackModifier.ui_label == 'Targeting'
        assert ToHitAttackModifier.ui_color == HINT_DAMAGE

    def test_positive_value_format(self, mock_component):
        """Positive value shows + sign."""
        ability = ToHitAttackModifier(mock_component, 5)
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '+5.0'

    def test_negative_value_format(self, mock_component):
        """Negative value shows - sign."""
        ability = ToHitAttackModifier(mock_component, -3)
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '-3.0'


class TestToHitDefenseModifierIsStaticValue:
    """Verify ToHitDefenseModifier uses StaticValueAbility."""

    def test_inherits_from_static_value_ability(self):
        """ToHitDefenseModifier is a StaticValueAbility subclass."""
        assert issubclass(ToHitDefenseModifier, StaticValueAbility)

    def test_class_attributes(self):
        """ToHitDefenseModifier has correct class attributes."""
        assert ToHitDefenseModifier.ui_label == 'Evasion'
        assert ToHitDefenseModifier.ui_color == HINT_EVASION

    def test_positive_value_format(self, mock_component):
        """Positive value shows + sign."""
        ability = ToHitDefenseModifier(mock_component, 10)
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '+10.0'


class TestEmissiveArmorIsStaticValue:
    """Verify EmissiveArmor uses StaticValueAbility."""

    def test_inherits_from_static_value_ability(self):
        """EmissiveArmor is a StaticValueAbility subclass."""
        assert issubclass(EmissiveArmor, StaticValueAbility)

    def test_class_attributes(self):
        """EmissiveArmor has correct class attributes."""
        assert EmissiveArmor.ui_label == 'Dmg Ignore'
        assert EmissiveArmor.ui_color == HINT_ACCURACY
        assert EmissiveArmor.int_result is True

    def test_int_cast(self, mock_component):
        """EmissiveArmor casts to int."""
        ability = EmissiveArmor(mock_component, 7.9)
        assert ability.value == 7
        assert isinstance(ability.value, int)

    def test_ui_format(self, mock_component):
        """EmissiveArmor shows integer format."""
        ability = EmissiveArmor(mock_component, 8)
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '8'
