"""
Isolation unit tests for defense abilities.

Tests ShieldProjection, ShieldRegeneration, ToHitAttackModifier,
ToHitDefenseModifier, and EmissiveArmor abilities.

These are ISOLATION tests - each test focuses on a single method/behavior
without relying on integration with other systems.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.defense import (
    ShieldProjection,
    ShieldRegeneration,
    ToHitAttackModifier,
    ToHitDefenseModifier,
    EmissiveArmor,
)
from game.simulation.components.abilities.stat_keys import StatKey
from game.simulation.components.abilities.ui_colors import (
    HINT_SHIELD_CAP,
    HINT_SHIELD_REGEN,
    HINT_DAMAGE,
    HINT_EVASION,
    HINT_ACCURACY,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_component():
    """Create a mock component with default empty stats."""
    component = MagicMock()
    component.stats = {}
    component.ability_stats = {}
    return component


@pytest.fixture
def mock_component_with_stats():
    """Factory fixture for creating component with specific stats."""
    def _create(stats=None, ability_stats=None):
        component = MagicMock()
        component.stats = stats or {}
        component.ability_stats = ability_stats or {}
        return component
    return _create


# =============================================================================
# ShieldProjection Tests
# =============================================================================

class TestShieldProjection:
    """Tests for ShieldProjection ability class."""

    def test_init_with_numeric_value(self, mock_component):
        """Initialize with a simple numeric value."""
        ability = ShieldProjection(mock_component, 100)

        assert ability.base_capacity == 100.0
        assert ability.capacity == 100.0
        assert ability.component is mock_component

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 250}
        ability = ShieldProjection(mock_component, data)

        assert ability.base_capacity == 250.0
        assert ability.capacity == 250.0

    def test_init_with_dict_missing_value(self, mock_component):
        """Initialize with dict without 'value' key defaults to 0."""
        data = {'other_key': 'ignored'}
        ability = ShieldProjection(mock_component, data)

        assert ability.base_capacity == 0.0
        assert ability.capacity == 0.0

    def test_init_with_float_value(self, mock_component):
        """Initialize with float preserves decimal precision."""
        ability = ShieldProjection(mock_component, 125.5)

        assert ability.base_capacity == 125.5
        assert ability.capacity == 125.5

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = ShieldProjection(mock_component, 0)

        assert ability.base_capacity == 0.0
        assert ability.capacity == 0.0

    def test_recalculate_no_modifier(self, mock_component):
        """recalculate with no modifier keeps base capacity."""
        ability = ShieldProjection(mock_component, 100)

        ability.recalculate()

        assert ability.capacity == 100.0

    def test_recalculate_with_capacity_mult(self, mock_component_with_stats):
        """recalculate applies capacity_mult from component stats."""
        component = mock_component_with_stats(stats={'capacity_mult': 1.5})
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        assert ability.capacity == 150.0

    def test_recalculate_with_doubled_modifier(self, mock_component_with_stats):
        """recalculate with 2x multiplier doubles capacity."""
        component = mock_component_with_stats(stats={'capacity_mult': 2.0})
        ability = ShieldProjection(component, 200)

        ability.recalculate()

        assert ability.capacity == 400.0

    def test_recalculate_with_reduced_modifier(self, mock_component_with_stats):
        """recalculate with <1 multiplier reduces capacity."""
        component = mock_component_with_stats(stats={'capacity_mult': 0.5})
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        assert ability.capacity == 50.0

    def test_recalculate_preserves_base_capacity(self, mock_component_with_stats):
        """recalculate does not modify base_capacity."""
        component = mock_component_with_stats(stats={'capacity_mult': 2.0})
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        assert ability.base_capacity == 100.0
        assert ability.capacity == 200.0

    def test_recalculate_multiple_times(self, mock_component_with_stats):
        """Multiple recalculate calls always use base_capacity."""
        component = mock_component_with_stats(stats={'capacity_mult': 1.5})
        ability = ShieldProjection(component, 100)

        ability.recalculate()
        assert ability.capacity == 150.0

        # Change modifier and recalculate again
        component.stats['capacity_mult'] = 2.0
        ability.recalculate()

        # Should be base * new_mult, not 150 * 2
        assert ability.capacity == 200.0

    def test_get_ui_rows_format(self, mock_component):
        """get_ui_rows returns correct format."""
        ability = ShieldProjection(mock_component, 100)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Shield Cap'
        assert rows[0]['value'] == '100'
        assert rows[0]['color_hint'] == HINT_SHIELD_CAP

    def test_get_ui_rows_rounds_value(self, mock_component):
        """get_ui_rows displays integer for capacity."""
        ability = ShieldProjection(mock_component, 125.7)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '126'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns current capacity."""
        ability = ShieldProjection(mock_component, 100)

        assert ability.get_primary_value() == 100.0
        assert isinstance(ability.get_primary_value(), float)

    def test_get_primary_value_after_recalculate(self, mock_component_with_stats):
        """get_primary_value reflects recalculated capacity."""
        component = mock_component_with_stats(stats={'capacity_mult': 1.5})
        ability = ShieldProjection(component, 100)
        ability.recalculate()

        assert ability.get_primary_value() == 150.0

    def test_stat_bindings_defined(self):
        """STAT_BINDINGS contains both capacity_mult and shield_capacity_mult bindings."""
        assert len(ShieldProjection.STAT_BINDINGS) == 2
        # First binding: capacity_mult
        binding = ShieldProjection.STAT_BINDINGS[0]
        assert binding.stat_key == StatKey.CAPACITY_MULT
        assert binding.attribute_name == 'capacity'
        assert binding.operation == 'multiply'
        # Second binding: shield_capacity_mult
        binding2 = ShieldProjection.STAT_BINDINGS[1]
        assert binding2.stat_key == StatKey.SHIELD_CAPACITY_MULT
        assert binding2.attribute_name == 'capacity'
        assert binding2.operation == 'multiply'

    def test_recalculate_with_shield_capacity_mult(self, mock_component_with_stats):
        """recalculate applies shield_capacity_mult from component stats."""
        component = mock_component_with_stats(stats={'shield_capacity_mult': 0.5})
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        assert ability.capacity == 50.0

    def test_recalculate_with_both_capacity_mults(self, mock_component_with_stats):
        """recalculate applies both capacity_mult and shield_capacity_mult multiplicatively."""
        component = mock_component_with_stats(stats={
            'capacity_mult': 1.5,
            'shield_capacity_mult': 0.5
        })
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        # 100 * 1.5 * 0.5 = 75
        assert ability.capacity == 75.0

    def test_recalculate_shield_capacity_mult_default_no_effect(self, mock_component_with_stats):
        """shield_capacity_mult at default 1.0 has no effect on capacity."""
        component = mock_component_with_stats(stats={'shield_capacity_mult': 1.0})
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        assert ability.capacity == 100.0

    def test_recalculate_both_mults_double_reduction(self, mock_component_with_stats):
        """Both capacity_mult and shield_capacity_mult reducing together stacks."""
        component = mock_component_with_stats(stats={
            'capacity_mult': 0.5,
            'shield_capacity_mult': 0.5
        })
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        # 100 * 0.5 * 0.5 = 25
        assert ability.capacity == 25.0


# =============================================================================
# ShieldRegeneration Tests
# =============================================================================

class TestShieldRegeneration:
    """Tests for ShieldRegeneration ability class."""

    def test_init_with_numeric_value(self, mock_component):
        """Initialize with a simple numeric value."""
        ability = ShieldRegeneration(mock_component, 10)

        assert ability.base_rate == 10.0
        assert ability.rate == 10.0

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 15}
        ability = ShieldRegeneration(mock_component, data)

        assert ability.base_rate == 15.0
        assert ability.rate == 15.0

    def test_init_with_float_value(self, mock_component):
        """Initialize with float preserves decimal precision."""
        ability = ShieldRegeneration(mock_component, 7.5)

        assert ability.base_rate == 7.5
        assert ability.rate == 7.5

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = ShieldRegeneration(mock_component, 0)

        assert ability.base_rate == 0.0
        assert ability.rate == 0.0

    def test_recalculate_no_modifier(self, mock_component):
        """recalculate with no modifier keeps base rate."""
        ability = ShieldRegeneration(mock_component, 10)

        ability.recalculate()

        assert ability.rate == 10.0

    def test_recalculate_with_energy_gen_mult(self, mock_component_with_stats):
        """recalculate applies energy_gen_mult from component stats."""
        component = mock_component_with_stats(stats={'energy_gen_mult': 1.25})
        ability = ShieldRegeneration(component, 10)

        ability.recalculate()

        assert ability.rate == 12.5

    def test_recalculate_with_doubled_modifier(self, mock_component_with_stats):
        """recalculate with 2x multiplier doubles rate."""
        component = mock_component_with_stats(stats={'energy_gen_mult': 2.0})
        ability = ShieldRegeneration(component, 8)

        ability.recalculate()

        assert ability.rate == 16.0

    def test_recalculate_preserves_base_rate(self, mock_component_with_stats):
        """recalculate does not modify base_rate."""
        component = mock_component_with_stats(stats={'energy_gen_mult': 1.5})
        ability = ShieldRegeneration(component, 10)

        ability.recalculate()

        assert ability.base_rate == 10.0
        assert ability.rate == 15.0

    def test_get_ui_rows_format(self, mock_component):
        """get_ui_rows returns correct format with rate per second."""
        ability = ShieldRegeneration(mock_component, 10)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Regen'
        assert rows[0]['value'] == '10.0/s'
        assert rows[0]['color_hint'] == HINT_SHIELD_REGEN

    def test_get_ui_rows_shows_decimal(self, mock_component):
        """get_ui_rows displays one decimal place."""
        ability = ShieldRegeneration(mock_component, 7.53)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '7.5/s'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns current rate."""
        ability = ShieldRegeneration(mock_component, 12)

        assert ability.get_primary_value() == 12.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_defined(self):
        """STAT_BINDINGS contains energy_gen_mult binding."""
        assert len(ShieldRegeneration.STAT_BINDINGS) == 1
        binding = ShieldRegeneration.STAT_BINDINGS[0]
        assert binding.stat_key == StatKey.ENERGY_GEN_MULT
        assert binding.attribute_name == 'rate'
        assert binding.operation == 'multiply'


# =============================================================================
# ToHitAttackModifier Tests
# =============================================================================

class TestToHitAttackModifier:
    """Tests for ToHitAttackModifier ability class."""

    def test_init_with_positive_value(self, mock_component):
        """Initialize with positive value."""
        ability = ToHitAttackModifier(mock_component, 5)

        assert ability.value == 5.0
        assert ability._base_value == 5.0

    def test_init_with_negative_value(self, mock_component):
        """Initialize with negative value."""
        ability = ToHitAttackModifier(mock_component, -3)

        assert ability.value == -3.0
        assert ability._base_value == -3.0

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = ToHitAttackModifier(mock_component, 0)

        assert ability.value == 0.0
        assert ability._base_value == 0.0

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 10}
        ability = ToHitAttackModifier(mock_component, data)

        assert ability.value == 10.0

    def test_init_with_float_value(self, mock_component):
        """Initialize with float preserves decimal precision."""
        ability = ToHitAttackModifier(mock_component, 2.5)

        assert ability.value == 2.5

    def test_recalculate_is_no_op(self, mock_component):
        """recalculate does not change value (no bindings)."""
        ability = ToHitAttackModifier(mock_component, 5)

        ability.recalculate()

        assert ability.value == 5.0

    def test_get_ui_rows_positive_value(self, mock_component):
        """get_ui_rows shows + sign for positive values."""
        ability = ToHitAttackModifier(mock_component, 5)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Targeting'
        assert rows[0]['value'] == '+5.0'
        assert rows[0]['color_hint'] == HINT_DAMAGE

    def test_get_ui_rows_negative_value(self, mock_component):
        """get_ui_rows shows - sign for negative values."""
        ability = ToHitAttackModifier(mock_component, -3)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '-3.0'

    def test_get_ui_rows_zero_value(self, mock_component):
        """get_ui_rows shows + sign for zero (>= 0 check)."""
        ability = ToHitAttackModifier(mock_component, 0)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '+0.0'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns current value."""
        ability = ToHitAttackModifier(mock_component, 7)

        assert ability.get_primary_value() == 7.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_empty(self):
        """STAT_BINDINGS is empty - no modifier stats consumed."""
        assert len(ToHitAttackModifier.STAT_BINDINGS) == 0


# =============================================================================
# ToHitDefenseModifier Tests
# =============================================================================

class TestToHitDefenseModifier:
    """Tests for ToHitDefenseModifier ability class."""

    def test_init_with_positive_value(self, mock_component):
        """Initialize with positive value."""
        ability = ToHitDefenseModifier(mock_component, 8)

        assert ability.value == 8.0
        assert ability._base_value == 8.0

    def test_init_with_negative_value(self, mock_component):
        """Initialize with negative value."""
        ability = ToHitDefenseModifier(mock_component, -5)

        assert ability.value == -5.0
        assert ability._base_value == -5.0

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = ToHitDefenseModifier(mock_component, 0)

        assert ability.value == 0.0

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 12}
        ability = ToHitDefenseModifier(mock_component, data)

        assert ability.value == 12.0

    def test_recalculate_is_no_op(self, mock_component):
        """recalculate does not change value (no bindings)."""
        ability = ToHitDefenseModifier(mock_component, 8)

        ability.recalculate()

        assert ability.value == 8.0

    def test_get_ui_rows_positive_value(self, mock_component):
        """get_ui_rows shows + sign for positive values."""
        ability = ToHitDefenseModifier(mock_component, 10)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Evasion'
        assert rows[0]['value'] == '+10.0'
        assert rows[0]['color_hint'] == HINT_EVASION

    def test_get_ui_rows_negative_value(self, mock_component):
        """get_ui_rows shows - sign for negative values."""
        ability = ToHitDefenseModifier(mock_component, -7)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '-7.0'

    def test_get_ui_rows_zero_value(self, mock_component):
        """get_ui_rows shows + sign for zero."""
        ability = ToHitDefenseModifier(mock_component, 0)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '+0.0'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns current value."""
        ability = ToHitDefenseModifier(mock_component, 15)

        assert ability.get_primary_value() == 15.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_empty(self):
        """STAT_BINDINGS is empty - no modifier stats consumed."""
        assert len(ToHitDefenseModifier.STAT_BINDINGS) == 0


# =============================================================================
# EmissiveArmor Tests
# =============================================================================

class TestEmissiveArmor:
    """Tests for EmissiveArmor ability class."""

    def test_init_with_positive_value(self, mock_component):
        """Initialize with positive value."""
        ability = EmissiveArmor(mock_component, 5)

        assert ability.amount == 5
        assert ability._base_amount == 5

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = EmissiveArmor(mock_component, 0)

        assert ability.amount == 0
        assert ability._base_amount == 0

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 10}
        ability = EmissiveArmor(mock_component, data)

        assert ability.amount == 10

    def test_init_with_float_truncates(self, mock_component):
        """Initialize with float truncates to int."""
        ability = EmissiveArmor(mock_component, 7.9)

        assert ability.amount == 7
        assert isinstance(ability.amount, int)

    def test_init_amount_is_integer(self, mock_component):
        """amount is stored as integer."""
        ability = EmissiveArmor(mock_component, 3)

        assert isinstance(ability.amount, int)
        assert isinstance(ability._base_amount, int)

    def test_recalculate_is_no_op(self, mock_component):
        """recalculate does not change amount (no bindings)."""
        ability = EmissiveArmor(mock_component, 5)

        ability.recalculate()

        assert ability.amount == 5

    def test_get_ui_rows_format(self, mock_component):
        """get_ui_rows returns correct format."""
        ability = EmissiveArmor(mock_component, 8)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Dmg Ignore'
        assert rows[0]['value'] == '8'
        assert rows[0]['color_hint'] == HINT_ACCURACY

    def test_get_ui_rows_zero(self, mock_component):
        """get_ui_rows displays zero correctly."""
        ability = EmissiveArmor(mock_component, 0)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '0'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns amount as float."""
        ability = EmissiveArmor(mock_component, 6)

        assert ability.get_primary_value() == 6.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_empty(self):
        """STAT_BINDINGS is empty - no modifier stats consumed."""
        assert len(EmissiveArmor.STAT_BINDINGS) == 0


# =============================================================================
# Edge Case Tests (Cross-class)
# =============================================================================

class TestDefenseAbilitiesEdgeCases:
    """Edge case tests across all defense abilities."""

    def test_shield_projection_large_value(self, mock_component):
        """ShieldProjection handles very large values."""
        ability = ShieldProjection(mock_component, 1_000_000)

        assert ability.capacity == 1_000_000.0

    def test_shield_projection_small_decimal(self, mock_component):
        """ShieldProjection handles very small decimals."""
        ability = ShieldProjection(mock_component, 0.001)

        assert ability.capacity == 0.001

    def test_shield_regen_large_multiplier(self, mock_component_with_stats):
        """ShieldRegeneration handles large multipliers."""
        component = mock_component_with_stats(stats={'energy_gen_mult': 100.0})
        ability = ShieldRegeneration(component, 10)

        ability.recalculate()

        assert ability.rate == 1000.0

    def test_shield_projection_zero_multiplier(self, mock_component_with_stats):
        """ShieldProjection handles zero multiplier."""
        component = mock_component_with_stats(stats={'capacity_mult': 0.0})
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        assert ability.capacity == 0.0

    def test_emissive_armor_negative_value(self, mock_component):
        """EmissiveArmor handles negative value (edge case)."""
        ability = EmissiveArmor(mock_component, -5)

        # Implementation stores as int, doesn't validate
        assert ability.amount == -5

    def test_to_hit_attack_very_large_bonus(self, mock_component):
        """ToHitAttackModifier handles very large bonus."""
        ability = ToHitAttackModifier(mock_component, 999)

        assert ability.value == 999.0
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '+999.0'

    def test_to_hit_defense_very_large_penalty(self, mock_component):
        """ToHitDefenseModifier handles very large penalty."""
        ability = ToHitDefenseModifier(mock_component, -999)

        assert ability.value == -999.0
        rows = ability.get_ui_rows()
        assert rows[0]['value'] == '-999.0'

    def test_ability_specific_stats_override(self, mock_component_with_stats):
        """Ability-specific stats override global stats."""
        # Global says 2.0, but ability-specific says 1.5
        component = mock_component_with_stats(
            stats={'capacity_mult': 2.0},
            ability_stats={'ShieldProjection': {'capacity_mult': 1.5}}
        )
        ability = ShieldProjection(component, 100)

        ability.recalculate()

        # Should use ability-specific 1.5, not global 2.0
        assert ability.capacity == 150.0
