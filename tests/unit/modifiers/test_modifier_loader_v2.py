"""
Tests for Modifier Loader V2 Format - Phase 2 Task 2.4

Tests for the V2 modifier format with formula-based effects.
V1 format support was removed in Phase 7 cleanup.
"""
import pytest


class TestModifierLoaderV2:
    """Tests for V2 format modifier loading."""

    def test_modifier_loads_v2_format_correctly(self):
        """Should load V2 format with effects array."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'description': 'HP scales quadratically',
            'param': {
                'name': 'Mass Mult',
                'type': 'linear',
                'min': 1.0,
                'max': 10.0,
                'default': 1.0
            },
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2'},
                {'stat': 'cost_mult', 'formula': 'param'}
            ],
            'restrictions': {
                'deny_abilities': ['Armor']
            }
        }

        mod = Modifier(v2_data)
        assert mod.id == 'hardened_mount'
        assert mod.name == 'Hardened'
        assert mod.min_val == 1.0
        assert mod.max_val == 10.0
        assert mod.default_val == 1.0
        assert isinstance(mod.effects, list)
        assert len(mod.effects) == 3

    def test_modifier_v2_has_effects_list(self):
        """V2 modifier should expose effects as list."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'test',
            'name': 'Test',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2'}
            ]
        }

        mod = Modifier(v2_data)
        assert isinstance(mod.effects, list)
        assert mod.effects[0]['stat'] == 'mass_mult'
        assert mod.effects[0]['formula'] == 'param'

    def test_modifier_v2_evaluate_effects(self):
        """V2 modifier should be able to evaluate effects."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2'}
            ]
        }

        mod = Modifier(v2_data)
        effects = mod.evaluate_effects(2.0)

        assert len(effects) == 2

        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
        hp_effect = next(e for e in effects if e.stat_key == 'hp_mult')

        assert mass_effect.value == pytest.approx(2.0)
        assert hp_effect.value == pytest.approx(4.0)

    def test_load_modifiers_file(self):
        """Should load modifiers.json file correctly.

        Note: modifiers_v2.json was consolidated into modifiers.json in Phase 9 (PROJ-40).
        """
        from game.simulation.components.component import load_modifiers
        from game.core.registry import RegistryManager

        # Clear registry first
        reg = RegistryManager.instance().modifiers
        reg.clear()

        # Load canonical modifiers file (V2 format)
        load_modifiers('data/modifiers.json')

        # Verify some modifiers loaded
        assert 'hardened_mount' in reg
        assert 'range_mount' in reg

        # Verify V2 format
        hardened = reg['hardened_mount']
        assert isinstance(hardened.effects, list)

    def test_v2_modifier_default_param_values(self):
        """V2 modifier should have sensible defaults when param is not specified."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'simple_mod',
            'name': 'Simple',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        }

        mod = Modifier(v2_data)
        assert mod.min_val == 0
        assert mod.max_val == 100
        assert mod.default_val == 0


class TestModifierFormulaEvaluation:
    """Tests for formula evaluation in V2 modifiers."""

    def test_hardened_mount_formula(self):
        """hardened_mount: hp = param^2, mass = param."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2'},
                {'stat': 'cost_mult', 'formula': 'param'}
            ]
        }
        mod = Modifier(v2_data)

        # Test at param = 2.0
        effects = mod.evaluate_effects(2.0)
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
        hp_effect = next(e for e in effects if e.stat_key == 'hp_mult')

        assert mass_effect.value == pytest.approx(2.0)
        assert hp_effect.value == pytest.approx(4.0)  # 2^2 = 4

        # Test at param = 3.0
        effects = mod.evaluate_effects(3.0)
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
        hp_effect = next(e for e in effects if e.stat_key == 'hp_mult')

        assert mass_effect.value == pytest.approx(3.0)
        assert hp_effect.value == pytest.approx(9.0)  # 3^2 = 9

    def test_range_mount_formula(self):
        """range_mount: range = 2^param, mass = 3.5^param."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'range_mount',
            'name': 'Range Mount',
            'effects': [
                {'stat': 'range_mult', 'formula': '2 ^ param'},
                {'stat': 'mass_mult', 'formula': '3.5 ^ param'}
            ]
        }
        mod = Modifier(v2_data)

        # Test at param = 1
        effects = mod.evaluate_effects(1.0)
        range_effect = next(e for e in effects if e.stat_key == 'range_mult')
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')

        assert range_effect.value == pytest.approx(2.0)  # 2^1 = 2
        assert mass_effect.value == pytest.approx(3.5)  # 3.5^1 = 3.5

        # Test at param = 2
        effects = mod.evaluate_effects(2.0)
        range_effect = next(e for e in effects if e.stat_key == 'range_mult')
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')

        assert range_effect.value == pytest.approx(4.0)   # 2^2 = 4
        assert mass_effect.value == pytest.approx(12.25)  # 3.5^2 = 12.25

    def test_turret_mount_logarithmic_formula(self):
        """turret_mount: mass = 1 + 0.514 * ln(1 + param/30)."""
        from game.simulation.components.component_constants import Modifier
        import math

        v2_data = {
            'id': 'turret_mount',
            'name': 'Turret Mount',
            'effects': [
                {'stat': 'mass_mult', 'formula': '1.0 + 0.514 * ln(1.0 + param / 30.0)'}
            ]
        }
        mod = Modifier(v2_data)

        # Test at param = 90
        effects = mod.evaluate_effects(90.0)
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')

        expected = 1.0 + 0.514 * math.log(1.0 + 90.0 / 30.0)
        assert mass_effect.value == pytest.approx(expected)
