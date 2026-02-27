"""
Integration tests for defense ability classes.

PROJ-118: Phase 2 - Tasks 2.25-2.27

These tests verify defense ability behavior in integration scenarios:
- Multiple defense abilities on same component
- Defense abilities with modifier stacking
- Cross-ability interactions (shields + armor)
- Component-to-ship stat flow
- Multiple instances contributing to total defense

These complement the isolation tests in test_defense_isolation.py.
"""

import pytest
from unittest.mock import Mock, MagicMock

from game.simulation.components.abilities.defense import (
    ShieldProjection,
    ShieldRegeneration,
    ToHitAttackModifier,
    ToHitDefenseModifier,
    EmissiveArmor,
)
from game.simulation.components.abilities.stat_keys import StatKey


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_component():
    """Create a mock component with default stats."""
    component = Mock()
    component.stats = {}
    component.ability_stats = {}
    return component


@pytest.fixture
def component_with_modifiers():
    """Create a mock component with modifier stat support."""
    def _create(stats=None, ability_stats=None):
        component = Mock()
        component.stats = stats or {}
        component.ability_stats = ability_stats or {}
        return component
    return _create


# =============================================================================
# Multi-Defense Component Tests
# =============================================================================

class TestMultiDefenseComponent:
    """Test multiple defense abilities on the same component."""

    def test_shield_and_regen_on_same_component(self, component_with_modifiers):
        """Shield capacity and regeneration on same component work independently."""
        component = component_with_modifiers(stats={
            'capacity_mult': 1.5,
            'energy_gen_mult': 2.0,
        })

        shield = ShieldProjection(component, 100)
        regen = ShieldRegeneration(component, 10)

        shield.recalculate()
        regen.recalculate()

        assert shield.capacity == 150.0  # 100 * 1.5
        assert regen.rate == 20.0        # 10 * 2.0

    def test_all_defense_types_on_component(self, mock_component):
        """All defense ability types can coexist on same component."""
        shield = ShieldProjection(mock_component, 100)
        regen = ShieldRegeneration(mock_component, 10)
        attack_mod = ToHitAttackModifier(mock_component, 5)
        defense_mod = ToHitDefenseModifier(mock_component, 8)
        armor = EmissiveArmor(mock_component, 3)

        # All should have correct primary values
        assert shield.get_primary_value() == 100.0
        assert regen.get_primary_value() == 10.0
        assert attack_mod.get_primary_value() == 5.0
        assert defense_mod.get_primary_value() == 8.0
        assert armor.get_primary_value() == 3.0


# =============================================================================
# Modifier Stacking Tests
# =============================================================================

class TestDefenseModifierStacking:
    """Test stacking behavior of defense modifiers."""

    def test_shield_capacity_mult_stacking(self, component_with_modifiers):
        """Multiple shield projectors share capacity_mult."""
        component = component_with_modifiers(stats={'capacity_mult': 2.0})

        shield1 = ShieldProjection(component, 100)
        shield2 = ShieldProjection(component, 50)

        shield1.recalculate()
        shield2.recalculate()

        # Both should be affected by the same multiplier
        assert shield1.capacity == 200.0  # 100 * 2.0
        assert shield2.capacity == 100.0  # 50 * 2.0

        # Total capacity contribution
        total_capacity = shield1.capacity + shield2.capacity
        assert total_capacity == 300.0

    def test_regen_rate_mult_stacking(self, component_with_modifiers):
        """Multiple regenerators share energy_gen_mult."""
        component = component_with_modifiers(stats={'energy_gen_mult': 1.5})

        regen1 = ShieldRegeneration(component, 10)
        regen2 = ShieldRegeneration(component, 5)

        regen1.recalculate()
        regen2.recalculate()

        assert regen1.rate == 15.0  # 10 * 1.5
        assert regen2.rate == 7.5   # 5 * 1.5

        # Total regen contribution
        total_regen = regen1.rate + regen2.rate
        assert total_regen == 22.5

    def test_modifier_changes_propagate_on_recalculate(self, component_with_modifiers):
        """Changing modifiers should update defense stats on recalculate."""
        component = component_with_modifiers(stats={'capacity_mult': 1.0})
        shield = ShieldProjection(component, 100)

        # Initial state
        shield.recalculate()
        assert shield.capacity == 100.0

        # Apply modifier
        component.stats['capacity_mult'] = 3.0
        shield.recalculate()
        assert shield.capacity == 300.0

        # Remove modifier
        component.stats['capacity_mult'] = 1.0
        shield.recalculate()
        assert shield.capacity == 100.0


# =============================================================================
# Ability-Specific Override Tests
# =============================================================================

class TestAbilitySpecificOverrides:
    """Test ability-specific stat overrides."""

    def test_shield_projection_specific_override(self, component_with_modifiers):
        """ShieldProjection-specific stats override global stats."""
        component = component_with_modifiers(
            stats={'capacity_mult': 2.0},
            ability_stats={'ShieldProjection': {'capacity_mult': 1.5}}
        )

        shield = ShieldProjection(component, 100)
        shield.recalculate()

        # Should use ability-specific 1.5, not global 2.0
        assert shield.capacity == 150.0

    def test_shield_regen_specific_override(self, component_with_modifiers):
        """ShieldRegeneration-specific stats override global stats."""
        component = component_with_modifiers(
            stats={'energy_gen_mult': 3.0},
            ability_stats={'ShieldRegeneration': {'energy_gen_mult': 2.0}}
        )

        regen = ShieldRegeneration(component, 10)
        regen.recalculate()

        # Should use ability-specific 2.0, not global 3.0
        assert regen.rate == 20.0

    def test_mixed_specific_and_global_stats(self, component_with_modifiers):
        """Mix of ability-specific and global stats."""
        component = component_with_modifiers(
            stats={
                'capacity_mult': 2.0,      # Global
                'energy_gen_mult': 1.5,    # Global
            },
            ability_stats={
                'ShieldProjection': {'capacity_mult': 3.0},  # Override
                # ShieldRegeneration uses global energy_gen_mult
            }
        )

        shield = ShieldProjection(component, 100)
        regen = ShieldRegeneration(component, 10)

        shield.recalculate()
        regen.recalculate()

        assert shield.capacity == 300.0  # Uses specific 3.0
        assert regen.rate == 15.0        # Uses global 1.5


# =============================================================================
# To-Hit Modifier Integration Tests
# =============================================================================

class TestToHitModifierIntegration:
    """Integration tests for to-hit modifiers."""

    def test_attack_and_defense_modifiers_combined(self, mock_component):
        """Attack and defense modifiers should both be available."""
        attack_mod = ToHitAttackModifier(mock_component, 10)
        defense_mod = ToHitDefenseModifier(mock_component, 5)

        # Net effect on targeting
        net_targeting = attack_mod.value - defense_mod.value
        assert net_targeting == 5  # +10 attack, -5 defense (opponent's)

    def test_multiple_targeting_modifiers(self, mock_component):
        """Multiple targeting modifiers stack additively."""
        attack1 = ToHitAttackModifier(mock_component, 5)
        attack2 = ToHitAttackModifier(mock_component, 3)

        total_attack_bonus = attack1.value + attack2.value
        assert total_attack_bonus == 8.0

    def test_negative_attack_modifier(self, mock_component):
        """Negative attack modifier (jamming effect)."""
        jammer = ToHitAttackModifier(mock_component, -5)

        assert jammer.value == -5.0
        rows = jammer.get_ui_rows()
        assert rows[0]['value'] == '-5.0'

    def test_negative_defense_modifier(self, mock_component):
        """Negative defense modifier (vulnerability effect)."""
        vulnerability = ToHitDefenseModifier(mock_component, -3)

        assert vulnerability.value == -3.0
        rows = vulnerability.get_ui_rows()
        assert rows[0]['value'] == '-3.0'


# =============================================================================
# Emissive Armor Integration Tests
# =============================================================================

class TestEmissiveArmorIntegration:
    """Integration tests for EmissiveArmor (damage ignore)."""

    def test_multiple_armor_layers(self, mock_component):
        """Multiple armor components stack for total damage ignore."""
        armor1 = EmissiveArmor(mock_component, 5)
        armor2 = EmissiveArmor(mock_component, 3)

        total_ignore = armor1.amount + armor2.amount
        assert total_ignore == 8

    def test_armor_zero_value(self, mock_component):
        """Zero armor provides no damage reduction."""
        armor = EmissiveArmor(mock_component, 0)

        assert armor.amount == 0
        assert armor.get_primary_value() == 0.0

    def test_armor_large_value(self, mock_component):
        """Large armor values should work correctly."""
        armor = EmissiveArmor(mock_component, 1000)

        assert armor.amount == 1000
        assert armor.get_primary_value() == 1000.0


# =============================================================================
# UI Row Integration Tests
# =============================================================================

class TestDefenseUIRowIntegration:
    """Integration tests for defense ability UI output."""

    def test_all_defense_ui_rows_format(self, mock_component):
        """All defense abilities should produce valid UI rows."""
        abilities = [
            ShieldProjection(mock_component, 100),
            ShieldRegeneration(mock_component, 10),
            ToHitAttackModifier(mock_component, 5),
            ToHitDefenseModifier(mock_component, 8),
            EmissiveArmor(mock_component, 3),
        ]

        for ability in abilities:
            rows = ability.get_ui_rows()

            assert len(rows) >= 1
            for row in rows:
                assert 'label' in row
                assert 'value' in row
                assert 'color_hint' in row
                assert row['color_hint'].startswith('#')

    def test_ui_rows_reflect_modified_values(self, component_with_modifiers):
        """UI rows should show modified values after recalculate."""
        component = component_with_modifiers(stats={'capacity_mult': 2.0})
        shield = ShieldProjection(component, 100)

        # Before recalculate - shows base
        rows_before = shield.get_ui_rows()
        assert rows_before[0]['value'] == '100'

        # After recalculate - shows modified
        shield.recalculate()
        rows_after = shield.get_ui_rows()
        assert rows_after[0]['value'] == '200'

    def test_regen_ui_shows_rate_per_second(self, mock_component):
        """Shield regen UI should show rate per second."""
        regen = ShieldRegeneration(mock_component, 15.5)

        rows = regen.get_ui_rows()
        assert rows[0]['label'] == 'Regen'
        assert '/s' in rows[0]['value']
        assert '15.5' in rows[0]['value']


# =============================================================================
# Stat Binding Introspection Tests
# =============================================================================

class TestDefenseStatBindingIntrospection:
    """Test stat binding introspection for defense abilities."""

    def test_shield_projection_consumed_stats(self):
        """ShieldProjection should declare capacity_mult and shield_capacity_mult as consumed."""
        consumed = ShieldProjection.get_consumed_stats()

        assert StatKey.CAPACITY_MULT in consumed
        assert StatKey.SHIELD_CAPACITY_MULT in consumed
        assert len(consumed) == 2

    def test_shield_regeneration_consumed_stats(self):
        """ShieldRegeneration should declare energy_gen_mult as consumed."""
        consumed = ShieldRegeneration.get_consumed_stats()

        assert StatKey.ENERGY_GEN_MULT in consumed
        assert len(consumed) == 1

    def test_to_hit_modifiers_no_consumed_stats(self):
        """ToHit modifiers should not consume any stats."""
        assert len(ToHitAttackModifier.get_consumed_stats()) == 0
        assert len(ToHitDefenseModifier.get_consumed_stats()) == 0

    def test_emissive_armor_no_consumed_stats(self):
        """EmissiveArmor should not consume any stats."""
        assert len(EmissiveArmor.get_consumed_stats()) == 0

    def test_get_effect_summary_with_active_modifier(self, component_with_modifiers):
        """get_effect_summary should show active capacity modifier."""
        component = component_with_modifiers(stats={'capacity_mult': 1.5})
        shield = ShieldProjection(component, 100)
        shield.recalculate()

        summary = shield.get_effect_summary()

        assert len(summary) == 1
        assert summary[0]['attribute'] == 'capacity'
        assert summary[0]['base'] == 100.0
        assert summary[0]['current'] == 150.0
        assert summary[0]['stat_value'] == 1.5

    def test_get_effect_summary_no_active_modifiers(self, mock_component):
        """get_effect_summary should be empty when no modifiers active."""
        mock_component.stats = {}
        shield = ShieldProjection(mock_component, 100)
        shield.recalculate()

        summary = shield.get_effect_summary()

        # No modifiers active, so no effects to show
        assert summary == []


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestDefenseEdgeCases:
    """Edge cases for defense abilities."""

    def test_zero_capacity_shield(self, mock_component):
        """Zero-capacity shield should work without errors."""
        shield = ShieldProjection(mock_component, 0)

        assert shield.capacity == 0.0
        assert shield.get_primary_value() == 0.0

        # Zero * any multiplier = zero
        mock_component.stats = {'capacity_mult': 100.0}
        shield.recalculate()
        assert shield.capacity == 0.0

    def test_very_large_capacity(self, mock_component):
        """Very large shield capacity should work correctly."""
        shield = ShieldProjection(mock_component, 1_000_000)

        assert shield.capacity == 1_000_000.0
        assert shield.get_primary_value() == 1_000_000.0

    def test_fractional_capacity(self, mock_component):
        """Fractional shield capacity should be preserved."""
        shield = ShieldProjection(mock_component, 100.5)

        assert shield.capacity == 100.5
        # UI rounds to integer
        rows = shield.get_ui_rows()
        assert rows[0]['value'] == '100' or rows[0]['value'] == '101'

    def test_zero_multiplier(self, component_with_modifiers):
        """Zero multiplier should result in zero capacity."""
        component = component_with_modifiers(stats={'capacity_mult': 0.0})
        shield = ShieldProjection(component, 100)
        shield.recalculate()

        assert shield.capacity == 0.0

    def test_negative_multiplier(self, component_with_modifiers):
        """Negative multiplier results in negative capacity (edge case)."""
        component = component_with_modifiers(stats={'capacity_mult': -1.0})
        shield = ShieldProjection(component, 100)
        shield.recalculate()

        # Implementation does not clamp to zero
        assert shield.capacity == -100.0

    def test_rapid_recalculate_stability(self, component_with_modifiers):
        """Rapid recalculate cycles should be stable."""
        component = component_with_modifiers(stats={'capacity_mult': 1.5})
        shield = ShieldProjection(component, 100)

        for _ in range(100):
            shield.recalculate()

        # Should always equal base * mult
        assert shield.capacity == 150.0
        # Base should never change
        assert shield.base_capacity == 100.0


# =============================================================================
# Value Initialization Tests
# =============================================================================

class TestDefenseValueInitialization:
    """Test various initialization scenarios for defense abilities."""

    def test_shield_projection_dict_value(self, mock_component):
        """ShieldProjection initializes from dict with 'value' key."""
        data = {'value': 250}
        shield = ShieldProjection(mock_component, data)

        assert shield.base_capacity == 250.0
        assert shield.capacity == 250.0

    def test_shield_projection_numeric_value(self, mock_component):
        """ShieldProjection initializes from numeric value."""
        shield = ShieldProjection(mock_component, 150)

        assert shield.base_capacity == 150.0
        assert shield.capacity == 150.0

    def test_shield_regen_dict_value(self, mock_component):
        """ShieldRegeneration initializes from dict with 'value' key."""
        data = {'value': 20}
        regen = ShieldRegeneration(mock_component, data)

        assert regen.base_rate == 20.0
        assert regen.rate == 20.0

    def test_to_hit_modifier_dict_value(self, mock_component):
        """ToHitModifiers initialize from dict with 'value' key."""
        attack_data = {'value': 7}
        defense_data = {'value': 4}

        attack = ToHitAttackModifier(mock_component, attack_data)
        defense = ToHitDefenseModifier(mock_component, defense_data)

        assert attack.value == 7.0
        assert defense.value == 4.0

    def test_emissive_armor_dict_value(self, mock_component):
        """EmissiveArmor initializes from dict with 'value' key."""
        data = {'value': 6}
        armor = EmissiveArmor(mock_component, data)

        assert armor.amount == 6

    def test_missing_value_key_defaults_to_zero(self, mock_component):
        """Missing 'value' key in dict defaults to zero."""
        data = {'other_key': 'ignored'}

        shield = ShieldProjection(mock_component, data)
        regen = ShieldRegeneration(mock_component, data)
        attack = ToHitAttackModifier(mock_component, data)
        defense = ToHitDefenseModifier(mock_component, data)
        armor = EmissiveArmor(mock_component, data)

        assert shield.capacity == 0.0
        assert regen.rate == 0.0
        assert attack.value == 0.0
        assert defense.value == 0.0
        assert armor.amount == 0
