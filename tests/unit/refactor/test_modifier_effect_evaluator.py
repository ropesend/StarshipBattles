"""
Tests for ModifierEffectEvaluator - Phase 1 Task 1.4

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
import math


class TestModifierEffectEvaluator:
    """Tests for the ModifierEffectEvaluator class."""

    def test_evaluate_simple_formula(self):
        """Should evaluate 'param' formula correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('param', {'param': 2.5})
        assert result == 2.5

    def test_evaluate_power_formula(self):
        """Should evaluate 'param ^ 2' formula correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('param ^ 2', {'param': 3.0})
        assert result == 9.0

    def test_evaluate_exponential_formula(self):
        """Should evaluate '2 ^ param' formula correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('2 ^ param', {'param': 3.0})
        assert result == 8.0

    def test_evaluate_ln_formula(self):
        """Should evaluate 'ln(param)' formula correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('ln(param)', {'param': math.e})
        assert result == pytest.approx(1.0)

    def test_evaluate_complex_formula(self):
        """Should evaluate '1.0 + 0.514 * ln(1.0 + param / 30.0)'."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        # turret_mount formula at arc=45
        result = ModifierEffectEvaluator.evaluate_formula(
            '1.0 + 0.514 * ln(1.0 + param / 30.0)',
            {'param': 45.0}
        )
        expected = 1.0 + 0.514 * math.log(1.0 + 45.0 / 30.0)
        assert result == pytest.approx(expected)

    def test_evaluate_linear_formula(self):
        """Should evaluate '1.0 + param * 0.5' correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('1.0 + param * 0.5', {'param': 4.0})
        assert result == 3.0

    def test_evaluate_with_stat_reference(self):
        """Should evaluate '1.0 + (mass_mult - 1.0) * 0.5' with stat context."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula(
            '1.0 + (mass_mult - 1.0) * 0.5',
            {'param': 0, 'mass_mult': 3.0}
        )
        assert result == pytest.approx(2.0)  # 1.0 + (3.0 - 1.0) * 0.5 = 2.0

    def test_evaluate_modifier_returns_effect_list(self):
        """evaluate_modifier() should return List[ModifierEffect]."""
        from game.simulation.components.modifier_effects import (
            ModifierEffectEvaluator, ModifierEffect
        )

        mod_def = {
            'id': 'test_mod',
            'name': 'Test',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param', 'operation': 'multiply'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        assert isinstance(effects, list)
        assert len(effects) == 1
        assert isinstance(effects[0], ModifierEffect)

    def test_evaluate_modifier_hardened_mount(self):
        """Should correctly evaluate hardened_mount formulas."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        mod_def = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param', 'operation': 'multiply'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2', 'operation': 'multiply'},
                {'stat': 'cost_mult', 'formula': 'param', 'operation': 'multiply'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        assert len(effects) == 3

        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
        hp_effect = next(e for e in effects if e.stat_key == 'hp_mult')
        cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

        assert mass_effect.value == 2.0
        assert hp_effect.value == 4.0  # 2^2
        assert cost_effect.value == 2.0

    def test_evaluate_modifier_range_mount(self):
        """Should correctly evaluate range_mount formulas."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        mod_def = {
            'id': 'range_mount',
            'name': 'Range Mount',
            'effects': [
                {'stat': 'range_mult', 'formula': '2 ^ param', 'operation': 'multiply'},
                {'stat': 'mass_mult', 'formula': '3.5 ^ param', 'operation': 'multiply'},
                {'stat': 'hp_mult', 'formula': '3.5 ^ param', 'operation': 'multiply'},
                {'stat': 'cost_mult', 'formula': '3.5 ^ param', 'operation': 'multiply'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        range_effect = next(e for e in effects if e.stat_key == 'range_mult')
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')

        assert range_effect.value == pytest.approx(4.0)  # 2^2
        assert mass_effect.value == pytest.approx(12.25)  # 3.5^2

    def test_evaluate_modifier_preserves_target_ability(self):
        """Should preserve target_ability in ModifierEffect."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        mod_def = {
            'id': 'power_boost',
            'name': 'Power Boost',
            'effects': [
                {
                    'stat': 'damage_mult',
                    'formula': '1.0 + param * 0.1',
                    'operation': 'multiply',
                    'target_ability': 'WeaponAbility'
                },
                {
                    'stat': 'capacity_mult',
                    'formula': '1.0 + param * 0.15',
                    'operation': 'multiply',
                    'target_ability': 'ShieldProjection'
                }
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 3.0)

        damage_effect = next(e for e in effects if e.stat_key == 'damage_mult')
        capacity_effect = next(e for e in effects if e.stat_key == 'capacity_mult')

        assert damage_effect.target_ability == 'WeaponAbility'
        assert damage_effect.value == pytest.approx(1.3)  # 1.0 + 3 * 0.1

        assert capacity_effect.target_ability == 'ShieldProjection'
        assert capacity_effect.value == pytest.approx(1.45)  # 1.0 + 3 * 0.15

    def test_evaluate_modifier_stores_source_info(self):
        """Effect should store source modifier info."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        mod_def = {
            'id': 'my_modifier',
            'name': 'My Modifier',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        assert effects[0].source_modifier_id == 'my_modifier'
        assert effects[0].source_modifier_name == 'My Modifier'
        assert effects[0].param_value == 2.0
        assert effects[0].formula_str == 'param'

    def test_evaluate_inverse_formula(self):
        """Should evaluate '1.0 / param' correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('1.0 / param', {'param': 2.0})
        assert result == 0.5

    def test_evaluate_additive_formula(self):
        """Should evaluate additive formulas like '(param - 1.0) * 2.0'."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        # rapid_fire mass formula
        result = ModifierEffectEvaluator.evaluate_formula('(param - 1.0) * 2.0', {'param': 3.0})
        assert result == 4.0  # (3-1) * 2 = 4

    def test_evaluate_sqrt_formula(self):
        """Should evaluate sqrt(param) correctly."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        result = ModifierEffectEvaluator.evaluate_formula('sqrt(param)', {'param': 9.0})
        assert result == 3.0
