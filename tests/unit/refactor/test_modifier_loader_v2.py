"""
Tests for Modifier Loader V2 Support - Phase 2 Task 2.4

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest


class TestModifierLoaderV2:
    """Tests for V2 format modifier loading."""

    def test_modifier_detects_v2_format(self):
        """Modifier class should detect V2 format by presence of 'effects' array."""
        from game.simulation.components.component_constants import Modifier

        v2_data = {
            'id': 'test_mod',
            'name': 'Test',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'}
            ],
            'param': {
                'name': 'Level',
                'type': 'linear',
                'min': 0,
                'max': 5,
                'default': 1
            }
        }

        mod = Modifier(v2_data)
        assert mod.is_v2_format is True

    def test_modifier_detects_v1_format(self):
        """Modifier class should detect V1 format (effects is dict with 'special')."""
        from game.simulation.components.component_constants import Modifier

        v1_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'type': 'linear',
            'effects': {
                'special': 'hardened_mount'
            },
            'min_val': 1.0,
            'max_val': 10.0,
            'default_val': 1.0
        }

        mod = Modifier(v1_data)
        assert mod.is_v2_format is False

    def test_modifier_loads_v1_format_correctly(self):
        """Should still load old V1 format correctly."""
        from game.simulation.components.component_constants import Modifier

        v1_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'type': 'linear',
            'param_name': 'Mass Mult',
            'min_val': 1.0,
            'max_val': 10.0,
            'default_val': 1.0,
            'effects': {
                'special': 'hardened_mount'
            },
            'restrictions': {
                'deny_types': ['Armor']
            }
        }

        mod = Modifier(v1_data)
        assert mod.id == 'hardened_mount'
        assert mod.name == 'Hardened'
        assert mod.min_val == 1.0
        assert mod.max_val == 10.0
        assert mod.default_val == 1.0
        assert mod.effects['special'] == 'hardened_mount'

    def test_modifier_loads_v2_format_correctly(self):
        """Should load new V2 format with effects array."""
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
        assert mod.param_name == 'Mass Mult'
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

    def test_modifier_v1_evaluate_effects_returns_none(self):
        """V1 modifier evaluate_effects should return None (uses old path)."""
        from game.simulation.components.component_constants import Modifier

        v1_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'type': 'linear',
            'effects': {'special': 'hardened_mount'}
        }

        mod = Modifier(v1_data)
        effects = mod.evaluate_effects(2.0)

        # V1 modifiers don't support formula evaluation
        assert effects is None

    def test_load_v2_modifiers_file(self):
        """Should load modifiers_v2.json file correctly."""
        from game.simulation.components.component import load_modifiers
        from game.core.registry import get_modifier_registry

        # Clear registry first
        reg = get_modifier_registry()
        reg.clear()

        # Load V2 format
        load_modifiers('data/modifiers_v2.json')

        # Verify some modifiers loaded
        assert 'hardened_mount' in reg
        assert 'range_mount' in reg

        # Verify V2 format detected
        hardened = reg['hardened_mount']
        assert hardened.is_v2_format is True
        assert isinstance(hardened.effects, list)


class TestModifierEvaluationEquivalence:
    """Tests to verify V2 evaluation matches V1 handler output."""

    def test_hardened_mount_v2_matches_v1(self):
        """V2 hardened_mount formulas should produce same results as V1 handler."""
        from game.simulation.components.component_constants import Modifier
        from game.simulation.components.modifiers import ModifierEffects

        # V2 modifier
        v2_data = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2'},
                {'stat': 'cost_mult', 'formula': 'param'}
            ]
        }
        v2_mod = Modifier(v2_data)

        # Test various param values
        for val in [1.0, 2.0, 3.0, 5.0]:
            # V2 evaluation
            v2_effects = v2_mod.evaluate_effects(val)
            v2_mass = next(e for e in v2_effects if e.stat_key == 'mass_mult').value
            v2_hp = next(e for e in v2_effects if e.stat_key == 'hp_mult').value
            v2_cost = next(e for e in v2_effects if e.stat_key == 'cost_mult').value

            # V1 handler evaluation - call handler directly
            v1_stats = {
                'mass_mult': 1.0,
                'hp_mult': 1.0,
                'cost_mult': 1.0
            }
            ModifierEffects.hardened_mount(val, v1_stats)

            assert v2_mass == pytest.approx(v1_stats['mass_mult']), f"mass_mult mismatch at val={val}"
            assert v2_hp == pytest.approx(v1_stats['hp_mult']), f"hp_mult mismatch at val={val}"
            assert v2_cost == pytest.approx(v1_stats['cost_mult']), f"cost_mult mismatch at val={val}"

    def test_range_mount_v2_matches_v1(self):
        """V2 range_mount formulas should produce same results as V1 handler."""
        from game.simulation.components.component_constants import Modifier
        from game.simulation.components.modifiers import ModifierEffects

        v2_data = {
            'id': 'range_mount',
            'name': 'Range Mount',
            'effects': [
                {'stat': 'range_mult', 'formula': '2 ^ param'},
                {'stat': 'mass_mult', 'formula': '3.5 ^ param'},
                {'stat': 'hp_mult', 'formula': '3.5 ^ param'},
                {'stat': 'cost_mult', 'formula': '3.5 ^ param'}
            ]
        }
        v2_mod = Modifier(v2_data)

        for val in [0, 1, 2, 3]:
            v2_effects = v2_mod.evaluate_effects(float(val))
            v2_range = next(e for e in v2_effects if e.stat_key == 'range_mult').value
            v2_mass = next(e for e in v2_effects if e.stat_key == 'mass_mult').value

            # V1 handler evaluation - call handler directly
            v1_stats = {
                'range_mult': 1.0,
                'mass_mult': 1.0,
                'hp_mult': 1.0,
                'cost_mult': 1.0
            }
            ModifierEffects.range_mount(val, v1_stats)

            assert v2_range == pytest.approx(v1_stats['range_mult']), f"range_mult mismatch at val={val}"
            assert v2_mass == pytest.approx(v1_stats['mass_mult']), f"mass_mult mismatch at val={val}"
