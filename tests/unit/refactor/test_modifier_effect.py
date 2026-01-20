"""
Tests for ModifierEffect dataclass - Phase 1 Task 1.3

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest


class TestModifierEffect:
    """Tests for the ModifierEffect dataclass."""

    def test_modifier_effect_creation(self):
        """ModifierEffect should store all required fields."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability=None,
            source_modifier_id='hardened_mount',
            source_modifier_name='Hardened',
            formula_str='param',
            param_value=1.5
        )

        assert effect.stat_key == 'damage_mult'
        assert effect.value == 1.5
        assert effect.operation == 'multiply'
        assert effect.target_ability is None
        assert effect.source_modifier_id == 'hardened_mount'
        assert effect.source_modifier_name == 'Hardened'
        assert effect.formula_str == 'param'
        assert effect.param_value == 1.5

    def test_modifier_effect_with_target_ability(self):
        """ModifierEffect should support target_ability for multi-ability modifiers."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.3,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='power_boost',
            source_modifier_name='Power Boost',
            formula_str='1.0 + param * 0.1',
            param_value=3.0
        )

        assert effect.target_ability == 'WeaponAbility'

    def test_modifier_effect_describe_multiply(self):
        """describe() should return 'damage_mult x1.50' for multiply."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )

        desc = effect.describe()
        assert 'damage_mult' in desc
        assert 'x' in desc or '*' in desc  # Multiplication symbol
        assert '1.50' in desc or '1.5' in desc

    def test_modifier_effect_describe_add(self):
        """describe() should return 'accuracy_add +0.50' for add."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='accuracy_add',
            value=0.5,
            operation='add',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param * 0.5',
            param_value=1.0
        )

        desc = effect.describe()
        assert 'accuracy_add' in desc
        assert '+' in desc
        assert '0.50' in desc or '0.5' in desc

    def test_modifier_effect_describe_set(self):
        """describe() should return 'arc_set =90.00' for set."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='arc_set',
            value=90.0,
            operation='set',
            target_ability=None,
            source_modifier_id='turret',
            source_modifier_name='Turret',
            formula_str='param',
            param_value=90.0
        )

        desc = effect.describe()
        assert 'arc_set' in desc
        assert '=' in desc
        assert '90' in desc

    def test_modifier_effect_describe_with_target(self):
        """describe() should include target ability when present."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )

        desc = effect.describe()
        assert 'WeaponAbility' in desc or 'damage_mult' in desc

    def test_modifier_effect_is_targeted(self):
        """is_targeted() should return True if target_ability is set."""
        from game.simulation.components.modifier_effects import ModifierEffect

        targeted = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )

        untargeted = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )

        assert targeted.is_targeted() is True
        assert untargeted.is_targeted() is False
