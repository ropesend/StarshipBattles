"""
Tests for Modifier V1 to V2 Format Converter - Phase 2 Task 2.2

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
import math


class TestModifierFormatConverter:
    """Tests for the V1 to V2 format converter."""

    def test_convert_hardened_mount(self):
        """Should convert hardened_mount to new format with 'param ^ 2' formula."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'type': 'linear',
            'description': 'HP increases as the square of mass multiplier.',
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

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        assert v2_modifier['id'] == 'hardened_mount'
        assert v2_modifier['name'] == 'Hardened'
        assert isinstance(v2_modifier['effects'], list)
        assert len(v2_modifier['effects']) == 3

        # Find the hp_mult effect
        hp_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'hp_mult')
        assert hp_effect['formula'] == 'param ^ 2'

        # Find the mass_mult effect
        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == 'param'

    def test_convert_range_mount(self):
        """Should convert range_mount to new format with '2 ^ param' formula."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'range_mount',
            'name': 'Range Mount',
            'type': 'linear',
            'effects': {
                'special': 'range_mount'
            }
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        range_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'range_mult')
        assert range_effect['formula'] == '2 ^ param'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '3.5 ^ param'

    def test_convert_turret_mount_with_ln(self):
        """Should convert turret_mount with ln formula."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'turret_mount',
            'name': 'Turret Mount',
            'type': 'linear',
            'effects': {
                'special': 'turret_mount',
                'arc_set': True
            }
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert 'ln' in mass_effect['formula']
        assert mass_effect['formula'] == '1.0 + 0.514 * ln(1.0 + param / 30.0)'

        arc_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'arc_set')
        assert arc_effect['formula'] == 'param'
        assert arc_effect['operation'] == 'set'

    def test_convert_rapid_fire(self):
        """Should convert rapid_fire to new format."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'rapid_fire',
            'name': 'Rapid Fire',
            'type': 'linear',
            'effects': {
                'special': 'rapid_fire'
            }
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        reload_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'reload_mult')
        assert reload_effect['formula'] == '1.0 / param'

        # V1 adds to mass_mult: mass_mult += (param - 1.0) * 2.0
        # We use 'add_to_mult' operation to add to existing multiplier
        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '(param - 1.0) * 2.0'
        assert mass_effect['operation'] == 'add_to_mult'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == 'sqrt(param)'

    def test_convert_precision_mount(self):
        """Should convert precision_mount correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'precision_mount',
            'name': 'Precision',
            'effects': {'special': 'precision_mount'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        accuracy_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'accuracy_add')
        assert accuracy_effect['formula'] == 'param * 0.5'
        assert accuracy_effect['operation'] == 'add'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 + param * 0.5'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == '1.5 ^ param'

    def test_convert_simple_size(self):
        """Should convert simple_size with all multipliers."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'simple_size_mount',
            'name': 'Size',
            'effects': {'special': 'simple_size'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        # Should have many effects, all with formula 'param'
        expected_stats = [
            'mass_mult', 'hp_mult', 'damage_mult', 'cost_mult',
            'thrust_mult', 'turn_mult', 'strategic_mult',
            'energy_gen_mult', 'capacity_mult', 'crew_capacity_mult',
            'life_support_capacity_mult', 'consumption_mult'
        ]

        for stat in expected_stats:
            effect = next((e for e in v2_modifier['effects'] if e['stat'] == stat), None)
            assert effect is not None, f"Missing effect for {stat}"
            assert effect['formula'] == 'param'

    def test_convert_seeker_endurance(self):
        """Should convert seeker_endurance correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'seeker_endurance',
            'effects': {'special': 'seeker_endurance'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        endurance_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'endurance_mult')
        assert endurance_effect['formula'] == 'param'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 + (param - 1.0) * 0.5'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == 'param'

    def test_convert_seeker_damage(self):
        """Should convert seeker_damage correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'seeker_damage',
            'effects': {'special': 'seeker_damage'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        damage_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'projectile_damage_mult')
        assert damage_effect['formula'] == 'param'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 + (param - 1.0) * 0.75'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == 'sqrt(param)'

    def test_convert_seeker_armored(self):
        """Should convert seeker_armored correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'seeker_armored',
            'effects': {'special': 'seeker_armored'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        hp_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'projectile_hp_mult')
        assert hp_effect['formula'] == 'param'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 + (param - 1.0) * 0.75'

    def test_convert_seeker_stealth(self):
        """Should convert seeker_stealth correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'seeker_stealth',
            'effects': {'special': 'seeker_stealth'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        stealth_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'projectile_stealth_add')
        assert stealth_effect['formula'] == 'param'
        assert stealth_effect['operation'] == 'add'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 + param * 2.0'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == '2.0 ^ param'

    def test_convert_automation(self):
        """Should convert automation correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'automation',
            'effects': {'special': 'automation'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        crew_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'crew_req_mult')
        assert crew_effect['formula'] == '1.0 - param'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 + param'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == '1.0 + param'

    def test_convert_efficiency_mount(self):
        """Should convert efficiency_mount correctly."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'efficiency_mount',
            'effects': {'special': 'efficiency_mount'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        consumption_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'consumption_mult')
        assert consumption_effect['formula'] == 'param'

        mass_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'mass_mult')
        assert mass_effect['formula'] == '1.0 / param'

        cost_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'cost_mult')
        assert cost_effect['formula'] == '1.0 / param'

    def test_convert_facing(self):
        """Should convert facing to property set."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'facing',
            'effects': {'special': 'facing'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        facing_effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'facing_angle')
        assert facing_effect['formula'] == 'param'
        assert facing_effect['operation'] == 'set'

    def test_convert_preserves_param_definition(self):
        """Should convert param definition to new format."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'test',
            'param_name': 'Level',
            'type': 'linear',
            'min_val': 0,
            'max_val': 5,
            'default_val': 1,
            'effects': {'special': 'hardened_mount'}
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        assert 'param' in v2_modifier
        assert v2_modifier['param']['name'] == 'Level'
        assert v2_modifier['param']['type'] == 'linear'
        assert v2_modifier['param']['min'] == 0
        assert v2_modifier['param']['max'] == 5
        assert v2_modifier['param']['default'] == 1

    def test_convert_preserves_restrictions(self):
        """Should convert restrictions to ability-based format."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'test',
            'effects': {'special': 'hardened_mount'},
            'restrictions': {
                'allow_types': ['BeamWeaponAbility'],
                'deny_types': ['Armor']
            }
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        assert 'restrictions' in v2_modifier
        assert v2_modifier['restrictions']['allow_abilities'] == ['BeamWeaponAbility']
        assert v2_modifier['restrictions']['deny_abilities'] == ['Armor']

    def test_convert_non_special_modifier(self):
        """Should handle modifiers without 'special' handler."""
        from game.simulation.components.modifier_converter import convert_modifier_v1_to_v2

        v1_modifier = {
            'id': 'efficient_engines',
            'name': 'Efficient Engines',
            'type': 'boolean',
            'default_val': True,
            'effects': {
                'consumption_mult': -0.2
            }
        }

        v2_modifier = convert_modifier_v1_to_v2(v1_modifier)

        # Direct effect conversion
        # V1 interpretation: stats['consumption_mult'] *= (1.0 + -0.2) = 0.8
        # V2 formula must produce same result: "1.0 + -0.2" = 0.8
        effect = next(e for e in v2_modifier['effects'] if e['stat'] == 'consumption_mult')
        assert effect['formula'] == '1.0 + -0.2'

    def test_convert_all_modifiers_in_file(self):
        """Should convert all modifiers from current JSON file."""
        from game.simulation.components.modifier_converter import convert_all_modifiers
        import json

        with open('data/modifiers.json', 'r') as f:
            v1_data = json.load(f)

        v2_data = convert_all_modifiers(v1_data)

        assert 'modifiers' in v2_data
        assert len(v2_data['modifiers']) == len(v1_data['modifiers'])

        # Each modifier should be valid V2 format
        from game.simulation.components.modifier_schema import validate_modifier_v2
        for modifier in v2_data['modifiers']:
            assert validate_modifier_v2(modifier), f"Invalid V2 format: {modifier['id']}"


class TestFormulaEquivalence:
    """Tests to verify V2 formulas produce same output as V1 handlers."""

    def test_hardened_mount_formula_equivalence(self):
        """hardened_mount V2 formulas should produce same values as V1."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        # Test values: 1.0, 2.0, 3.0, 5.0
        test_values = [1.0, 2.0, 3.0, 5.0]

        for val in test_values:
            effects = ModifierEffectEvaluator.evaluate_modifier({
                'id': 'hardened_mount',
                'name': 'Hardened',
                'effects': [
                    {'stat': 'mass_mult', 'formula': 'param'},
                    {'stat': 'hp_mult', 'formula': 'param ^ 2'},
                    {'stat': 'cost_mult', 'formula': 'param'}
                ]
            }, val)

            mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
            hp_effect = next(e for e in effects if e.stat_key == 'hp_mult')
            cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

            # Expected from V1: mass *= val, hp *= val^2, cost *= val
            assert mass_effect.value == pytest.approx(val)
            assert hp_effect.value == pytest.approx(val ** 2)
            assert cost_effect.value == pytest.approx(val)

    def test_range_mount_formula_equivalence(self):
        """range_mount V2 formulas should produce same values as V1."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        test_values = [0, 1, 2, 3]

        for val in test_values:
            effects = ModifierEffectEvaluator.evaluate_modifier({
                'id': 'range_mount',
                'effects': [
                    {'stat': 'range_mult', 'formula': '2 ^ param'},
                    {'stat': 'mass_mult', 'formula': '3.5 ^ param'},
                    {'stat': 'hp_mult', 'formula': '3.5 ^ param'},
                    {'stat': 'cost_mult', 'formula': '3.5 ^ param'}
                ]
            }, val)

            range_effect = next(e for e in effects if e.stat_key == 'range_mult')
            mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')

            # Expected from V1: range *= 2^val, mass *= 3.5^val
            assert range_effect.value == pytest.approx(2 ** val)
            assert mass_effect.value == pytest.approx(3.5 ** val)

    def test_turret_mount_formula_equivalence(self):
        """turret_mount V2 formulas should produce same values as V1."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        test_values = [0, 30, 45, 90, 180]

        for val in test_values:
            effects = ModifierEffectEvaluator.evaluate_modifier({
                'id': 'turret_mount',
                'effects': [
                    {'stat': 'mass_mult', 'formula': '1.0 + 0.514 * ln(1.0 + param / 30.0)'},
                    {'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}
                ]
            }, val)

            mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
            arc_effect = next(e for e in effects if e.stat_key == 'arc_set')

            # Expected from V1
            expected_mass = 1.0 + 0.514 * math.log(1.0 + val / 30.0) if val > 0 else 1.0
            # For val=0, the formula gives 1.0 + 0.514 * ln(1) = 1.0
            assert mass_effect.value == pytest.approx(1.0 + 0.514 * math.log(1.0 + val / 30.0))
            assert arc_effect.value == pytest.approx(val)

    def test_rapid_fire_formula_equivalence(self):
        """rapid_fire V2 formulas should produce same values as V1."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        test_values = [1.0, 2.0, 3.0, 5.0]

        for val in test_values:
            effects = ModifierEffectEvaluator.evaluate_modifier({
                'id': 'rapid_fire',
                'effects': [
                    {'stat': 'reload_mult', 'formula': '1.0 / param'},
                    {'stat': 'mass_add', 'formula': '(param - 1.0) * 2.0', 'operation': 'add'},
                    {'stat': 'cost_mult', 'formula': 'sqrt(param)'}
                ]
            }, val)

            reload_effect = next(e for e in effects if e.stat_key == 'reload_mult')
            mass_effect = next(e for e in effects if e.stat_key == 'mass_add')
            cost_effect = next(e for e in effects if e.stat_key == 'cost_mult')

            # Expected from V1
            assert reload_effect.value == pytest.approx(1.0 / val)
            assert mass_effect.value == pytest.approx((val - 1.0) * 2.0)
            assert cost_effect.value == pytest.approx(math.sqrt(val))
