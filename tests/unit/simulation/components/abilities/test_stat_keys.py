"""
Unit tests for stat_keys.py.

Tests StatKey enum and AbilityStatBinding class.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestStatKeyEnum:
    """Tests for StatKey enum."""

    def test_all_stat_keys_unique_values(self):
        """No duplicate .value strings."""
        values = [key.value for key in StatKey]
        assert len(values) == len(set(values))

    def test_multiplicative_stat_default_1(self):
        """DAMAGE_MULT defaults to 1.0."""
        default = StatKey.get_default(StatKey.DAMAGE_MULT)
        assert default == 1.0

    def test_additive_stat_default_0(self):
        """MASS_ADD defaults to 0.0."""
        default = StatKey.get_default(StatKey.MASS_ADD)
        assert default == 0.0

    def test_set_stat_default_none(self):
        """ARC_SET defaults to None."""
        default = StatKey.get_default(StatKey.ARC_SET)
        assert default is None

    def test_other_multiplicative_stats_default_1(self):
        """Other multiplicative stats also default to 1.0."""
        mult_stats = [
            StatKey.MASS_MULT, StatKey.HP_MULT, StatKey.RANGE_MULT,
            StatKey.COST_MULT, StatKey.THRUST_MULT, StatKey.TURN_MULT
        ]
        for stat in mult_stats:
            assert StatKey.get_default(stat) == 1.0

    def test_other_additive_stats_default_0(self):
        """Other additive stats also default to 0.0."""
        add_stats = [StatKey.ARC_ADD, StatKey.ACCURACY_ADD, StatKey.PROJECTILE_STEALTH_LEVEL]
        for stat in add_stats:
            assert StatKey.get_default(stat) == 0.0


class TestCreateDefaultStatsDict:
    """Tests for StatKey.create_default_stats_dict."""

    def test_create_default_stats_dict_all_keys(self):
        """Dict has entry for every StatKey."""
        stats = StatKey.create_default_stats_dict()
        for key in StatKey:
            assert key.value in stats

    def test_create_default_stats_dict_has_properties(self):
        """Dict includes 'properties' key."""
        stats = StatKey.create_default_stats_dict()
        assert 'properties' in stats
        assert isinstance(stats['properties'], dict)

    def test_create_default_stats_dict_correct_defaults(self):
        """Dict has correct default values."""
        stats = StatKey.create_default_stats_dict()
        assert stats[StatKey.DAMAGE_MULT.value] == 1.0
        assert stats[StatKey.MASS_ADD.value] == 0.0
        assert stats[StatKey.ARC_SET.value] is None


class TestAbilityStatBindingInit:
    """Tests for AbilityStatBinding initialization."""

    def test_binding_init_basic(self):
        """StatKey, attribute_name, operation stored."""
        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage',
            operation='multiply'
        )
        assert binding.stat_key == StatKey.DAMAGE_MULT
        assert binding.attribute_name == 'damage'
        assert binding.operation == 'multiply'

    def test_binding_invalid_operation_raises(self):
        """ValueError for 'divide'."""
        with pytest.raises(ValueError) as exc_info:
            AbilityStatBinding(
                stat_key=StatKey.DAMAGE_MULT,
                attribute_name='damage',
                operation='divide'
            )
        assert "divide" in str(exc_info.value)

    def test_binding_default_operation_is_multiply(self):
        """Default operation is 'multiply'."""
        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage'
        )
        assert binding.operation == 'multiply'


class TestAbilityStatBindingGetBaseAttribute:
    """Tests for AbilityStatBinding.get_base_attribute_name."""

    def test_binding_get_base_attribute_explicit(self):
        """Returns explicit base_attribute."""
        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage',
            base_attribute='_custom_base'
        )
        assert binding.get_base_attribute_name() == '_custom_base'

    def test_binding_get_base_attribute_auto(self):
        """Returns '_base_{attribute_name}' when not specified."""
        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage'
        )
        assert binding.get_base_attribute_name() == '_base_damage'


class TestAbilityStatBindingApply:
    """Tests for AbilityStatBinding.apply method."""

    def test_binding_apply_multiply(self):
        """base * stat_value set on ability."""
        class DummyAbility:
            _base_damage = 100.0
            damage = 0.0

        ability = DummyAbility()

        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage',
            operation='multiply'
        )

        stats = {StatKey.DAMAGE_MULT.value: 1.5}
        result = binding.apply(ability, stats)

        assert result is True
        assert ability.damage == 150.0

    def test_binding_apply_add(self):
        """base + stat_value set on ability."""
        class DummyAbility:
            _base_accuracy = 0.7
            accuracy = 0.0

        ability = DummyAbility()

        binding = AbilityStatBinding(
            stat_key=StatKey.ACCURACY_ADD,
            attribute_name='accuracy',
            operation='add'
        )

        stats = {StatKey.ACCURACY_ADD.value: 0.1}
        result = binding.apply(ability, stats)

        assert result is True
        assert abs(ability.accuracy - 0.8) < 0.001

    def test_binding_apply_set(self):
        """stat_value directly set on ability."""
        class DummyAbility:
            _base_arc = 45.0
            arc = 0.0

        ability = DummyAbility()

        binding = AbilityStatBinding(
            stat_key=StatKey.ARC_SET,
            attribute_name='arc',
            operation='set'
        )

        stats = {StatKey.ARC_SET.value: 90.0}
        result = binding.apply(ability, stats)

        assert result is True
        assert ability.arc == 90.0

    def test_binding_apply_missing_stat_returns_false(self):
        """Stat not in dict -> False."""
        class DummyAbility:
            _base_damage = 100.0
            damage = 0.0

        ability = DummyAbility()

        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage'
        )

        stats = {}  # Empty stats
        result = binding.apply(ability, stats)

        assert result is False

    def test_binding_apply_missing_base_attr_returns_false(self):
        """No base attr -> False."""
        class DummyAbility:
            damage = 0.0
            # No _base_damage

        ability = DummyAbility()

        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage'
        )

        stats = {StatKey.DAMAGE_MULT.value: 1.5}
        result = binding.apply(ability, stats)

        assert result is False


class TestAbilityStatBindingDescribe:
    """Tests for AbilityStatBinding.describe method."""

    def test_binding_describe_multiply(self):
        """Human-readable description for multiply."""
        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage',
            operation='multiply'
        )
        desc = binding.describe()
        assert "damage" in desc
        assert "multiplied by" in desc
        assert "damage_mult" in desc

    def test_binding_describe_add(self):
        """Human-readable description for add."""
        binding = AbilityStatBinding(
            stat_key=StatKey.ACCURACY_ADD,
            attribute_name='accuracy',
            operation='add'
        )
        desc = binding.describe()
        assert "accuracy" in desc
        assert "increased by" in desc

    def test_binding_describe_set(self):
        """Human-readable description for set."""
        binding = AbilityStatBinding(
            stat_key=StatKey.ARC_SET,
            attribute_name='arc',
            operation='set'
        )
        desc = binding.describe()
        assert "arc" in desc
        assert "set to" in desc
