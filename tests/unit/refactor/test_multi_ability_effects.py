"""
Tests for Phase 5: Multi-Ability Effects

This module tests the ability to target specific abilities with modifier effects,
allowing a single modifier to affect different abilities differently.

Example use case: A power core modifier that boosts weapon damage AND shield capacity
by different amounts, without affecting other abilities that consume those stats.
"""
import pytest


class TestTargetedEffectEvaluation:
    """Tests for ModifierEffect target_ability field handling."""

    def test_modifier_effect_has_target_ability_field(self):
        """ModifierEffect dataclass should have target_ability attribute."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test_mod',
            source_modifier_name='Test Modifier',
            formula_str='1.5',
            param_value=1.0
        )

        assert effect.target_ability == 'WeaponAbility'
        assert effect.is_targeted() == True

    def test_effect_without_target_is_not_targeted(self):
        """Effect with target_ability=None should not be targeted."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability=None,
            source_modifier_id='test_mod',
            source_modifier_name='Test Modifier',
            formula_str='1.5',
            param_value=1.0
        )

        assert effect.is_targeted() == False

    def test_evaluator_parses_target_ability_from_effect(self):
        """ModifierEffectEvaluator should parse target_ability from effect definition."""
        from game.simulation.components.modifier_effects import ModifierEffectEvaluator

        mod_def = {
            'id': 'test_targeted',
            'name': 'Test Targeted Modifier',
            'effects': [
                {
                    'stat': 'damage_mult',
                    'formula': '1.0 + param * 0.1',
                    'target_ability': 'WeaponAbility'
                },
                {
                    'stat': 'capacity_mult',
                    'formula': '1.0 + param * 0.15',
                    'target_ability': 'ShieldProjection'
                },
                {
                    'stat': 'mass_mult',
                    'formula': '1.0 + param * 0.2'
                    # No target_ability = global effect
                }
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        # Should have 3 effects
        assert len(effects) == 3

        # First effect targets WeaponAbility
        damage_effect = next(e for e in effects if e.stat_key == 'damage_mult')
        assert damage_effect.target_ability == 'WeaponAbility'
        assert damage_effect.value == pytest.approx(1.2)  # 1.0 + 2.0 * 0.1

        # Second effect targets ShieldProjection
        capacity_effect = next(e for e in effects if e.stat_key == 'capacity_mult')
        assert capacity_effect.target_ability == 'ShieldProjection'
        assert capacity_effect.value == pytest.approx(1.3)  # 1.0 + 2.0 * 0.15

        # Third effect is global (no target)
        mass_effect = next(e for e in effects if e.stat_key == 'mass_mult')
        assert mass_effect.target_ability is None
        assert mass_effect.value == pytest.approx(1.4)  # 1.0 + 2.0 * 0.2


class TestAbilitySpecificStats:
    """Tests for ability-specific stat dictionaries."""

    def test_component_has_ability_stats_dict(self):
        """Component should have an ability_stats dict for targeted effects."""
        from game.simulation.components.component import create_component

        railgun = create_component('railgun')

        # Component should have ability_stats attribute (initialized in recalculate_stats)
        railgun.recalculate_stats()

        assert hasattr(railgun, 'ability_stats')
        assert isinstance(railgun.ability_stats, dict)

    def test_targeted_effect_goes_to_ability_stats(self):
        """Effects with target_ability should populate ability_stats[ability_name]."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import Modifier
        from game.core.registry import get_modifier_registry

        railgun = create_component('railgun')

        # Create a test modifier with targeted effect
        test_mod_data = {
            'id': 'test_targeted_mod',
            'name': 'Test Targeted',
            'effects': [
                {
                    'stat': 'damage_mult',
                    'formula': '1.5',
                    'target_ability': 'ProjectileWeaponAbility'
                }
            ]
        }

        # Register the test modifier
        mod_registry = get_modifier_registry()
        test_mod_def = Modifier(test_mod_data)
        mod_registry['test_targeted_mod'] = test_mod_def

        # Add the modifier (triggers recalculate_stats)
        railgun.add_modifier('test_targeted_mod', 1.0)

        # Check ability_stats has the targeted effect
        assert 'ProjectileWeaponAbility' in railgun.ability_stats
        assert 'damage_mult' in railgun.ability_stats['ProjectileWeaponAbility']
        assert railgun.ability_stats['ProjectileWeaponAbility']['damage_mult'] == pytest.approx(1.5)

    def test_global_effect_stays_in_stats(self):
        """Effects without target_ability should stay in component.stats."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import Modifier
        from game.core.registry import get_modifier_registry

        railgun = create_component('railgun')

        # Create a test modifier with both targeted and global effects
        test_mod_data = {
            'id': 'test_mixed_mod',
            'name': 'Test Mixed',
            'effects': [
                {
                    'stat': 'damage_mult',
                    'formula': '1.5',
                    'target_ability': 'ProjectileWeaponAbility'
                },
                {
                    'stat': 'mass_mult',
                    'formula': '2.0'
                    # No target = global
                }
            ]
        }

        mod_registry = get_modifier_registry()
        test_mod_def = Modifier(test_mod_data)
        mod_registry['test_mixed_mod'] = test_mod_def

        railgun.add_modifier('test_mixed_mod', 1.0)

        # Global mass_mult should be in stats
        assert railgun.stats['mass_mult'] == pytest.approx(2.0)

        # Targeted damage_mult should NOT be in global stats (stays at 1.0)
        assert railgun.stats['damage_mult'] == pytest.approx(1.0)


class TestAbilityRecalculateWithTargetedStats:
    """Tests for abilities reading from ability_stats."""

    def test_ability_uses_targeted_stat_over_global(self):
        """Ability should use ability_stats[cls_name][stat] if present."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import Modifier
        from game.core.registry import get_modifier_registry

        # Use generator which has simpler formula (no range_to_target)
        generator = create_component('generator')
        if generator is None:
            pytest.skip("generator component not found")

        gen_ab = generator.get_ability('ResourceGeneration')
        if gen_ab is None:
            pytest.skip("generator doesn't have ResourceGeneration")

        # Capture base rate before any modifiers
        base_rate = gen_ab._base_rate
        assert base_rate > 0, f"Generator should have positive base rate, got {base_rate}"

        # Create modifier that targets ResourceGeneration specifically
        test_mod_data = {
            'id': 'gen_boost_targeted',
            'name': 'Generator Boost',
            'effects': [
                {
                    'stat': 'energy_gen_mult',
                    'formula': '2.0',
                    'target_ability': 'ResourceGeneration'
                }
            ]
        }

        mod_registry = get_modifier_registry()
        test_mod_def = Modifier(test_mod_data)
        mod_registry['gen_boost_targeted'] = test_mod_def

        generator.add_modifier('gen_boost_targeted', 1.0)

        # Generation rate should be doubled via targeted effect
        assert gen_ab.rate == pytest.approx(base_rate * 2.0)

        # IMPORTANT: Global energy_gen_mult should stay at 1.0
        assert generator.stats['energy_gen_mult'] == pytest.approx(1.0), \
            "Targeted effect should NOT affect global stats"

    def test_multiple_abilities_same_stat_targeted_differently(self):
        """Different abilities consuming same stat can be targeted independently."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import Modifier
        from game.core.registry import get_modifier_registry

        generator = create_component('generator')
        if generator is None:
            pytest.skip("generator component not found")

        gen = generator.get_ability('ResourceGeneration')
        if gen is None:
            pytest.skip("generator doesn't have ResourceGeneration")

        base_rate = gen._base_rate

        # Create modifier targeting only ResourceGeneration
        test_mod_data = {
            'id': 'gen_boost',
            'name': 'Generator Boost',
            'effects': [
                {
                    'stat': 'energy_gen_mult',
                    'formula': '3.0',
                    'target_ability': 'ResourceGeneration'
                }
            ]
        }

        mod_registry = get_modifier_registry()
        test_mod_def = Modifier(test_mod_data)
        mod_registry['gen_boost'] = test_mod_def

        generator.add_modifier('gen_boost', 1.0)

        # Generation rate should be tripled
        assert gen.rate == pytest.approx(base_rate * 3.0)


class TestMixedGlobalAndTargetedEffects:
    """Tests for modifiers with both global and targeted effects."""

    def test_modifier_with_global_and_targeted_effects(self):
        """A modifier can have both global effects and ability-targeted effects."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import Modifier
        from game.core.registry import get_modifier_registry

        generator = create_component('generator')
        if generator is None:
            pytest.skip("generator component not found")

        gen_ab = generator.get_ability('ResourceGeneration')
        if gen_ab is None:
            pytest.skip("generator doesn't have ResourceGeneration")

        base_rate = gen_ab._base_rate
        base_mass = generator.base_mass

        # Modifier with both global mass effect and targeted energy effect
        test_mod_data = {
            'id': 'heavy_gen_boost',
            'name': 'Heavy Generator Boost',
            'effects': [
                {
                    'stat': 'energy_gen_mult',
                    'formula': '1.5',
                    'target_ability': 'ResourceGeneration'
                },
                {
                    'stat': 'mass_mult',
                    'formula': '2.0'
                    # Global effect - affects component mass
                }
            ]
        }

        mod_registry = get_modifier_registry()
        test_mod_def = Modifier(test_mod_data)
        mod_registry['heavy_gen_boost'] = test_mod_def

        generator.add_modifier('heavy_gen_boost', 1.0)

        # Energy generation should be 1.5x (targeted)
        assert gen_ab.rate == pytest.approx(base_rate * 1.5)

        # Mass should be 2x (global)
        assert generator.mass == pytest.approx(base_mass * 2.0)


class TestEffectDescriptionWithTarget:
    """Tests for UI-friendly effect descriptions with targeting."""

    def test_describe_targeted_effect(self):
        """Targeted effect description should include ability name."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test_mod',
            source_modifier_name='Test',
            formula_str='1.5',
            param_value=1.0
        )

        desc = effect.describe()
        assert 'WeaponAbility' in desc
        assert 'damage_mult' in desc
        assert 'x1.50' in desc

    def test_describe_global_effect(self):
        """Global effect description should not include ability name."""
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key='mass_mult',
            value=2.0,
            operation='multiply',
            target_ability=None,
            source_modifier_id='test_mod',
            source_modifier_name='Test',
            formula_str='2.0',
            param_value=1.0
        )

        desc = effect.describe()
        assert 'mass_mult' in desc
        assert 'x2.00' in desc
        assert '(' not in desc  # No "(on AbilityName)"
