"""
Tests for WeaponAbility STAT_BINDINGS - Phase 3 Task 3.1

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestWeaponAbilityStatBindings:
    """Tests for WeaponAbility STAT_BINDINGS declarations."""

    def test_weapon_ability_has_stat_bindings(self):
        """WeaponAbility should have STAT_BINDINGS class attribute."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        assert hasattr(WeaponAbility, 'STAT_BINDINGS')
        assert isinstance(WeaponAbility.STAT_BINDINGS, list)

    def test_weapon_ability_has_damage_binding(self):
        """WeaponAbility should have DAMAGE_MULT binding for 'damage'."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        damage_bindings = [b for b in WeaponAbility.STAT_BINDINGS
                          if b.stat_key == StatKey.DAMAGE_MULT]
        assert len(damage_bindings) == 1

        binding = damage_bindings[0]
        assert binding.attribute_name == 'damage'
        assert binding.operation == 'multiply'

    def test_weapon_ability_has_range_binding(self):
        """WeaponAbility should have RANGE_MULT binding for 'range'."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        range_bindings = [b for b in WeaponAbility.STAT_BINDINGS
                         if b.stat_key == StatKey.RANGE_MULT]
        assert len(range_bindings) == 1

        binding = range_bindings[0]
        assert binding.attribute_name == 'range'
        assert binding.operation == 'multiply'

    def test_weapon_ability_has_reload_binding(self):
        """WeaponAbility should have RELOAD_MULT binding for 'reload_time'."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        reload_bindings = [b for b in WeaponAbility.STAT_BINDINGS
                          if b.stat_key == StatKey.RELOAD_MULT]
        assert len(reload_bindings) == 1

        binding = reload_bindings[0]
        assert binding.attribute_name == 'reload_time'
        assert binding.operation == 'multiply'

    def test_weapon_ability_has_arc_set_binding(self):
        """WeaponAbility should have ARC_SET binding for 'firing_arc'."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        arc_set_bindings = [b for b in WeaponAbility.STAT_BINDINGS
                           if b.stat_key == StatKey.ARC_SET]
        assert len(arc_set_bindings) == 1

        binding = arc_set_bindings[0]
        assert binding.attribute_name == 'firing_arc'
        assert binding.operation == 'set'

    def test_weapon_ability_has_arc_add_binding(self):
        """WeaponAbility should have ARC_ADD binding for 'firing_arc'."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        arc_add_bindings = [b for b in WeaponAbility.STAT_BINDINGS
                           if b.stat_key == StatKey.ARC_ADD]
        assert len(arc_add_bindings) == 1

        binding = arc_add_bindings[0]
        assert binding.attribute_name == 'firing_arc'
        assert binding.operation == 'add'

    def test_weapon_ability_get_consumed_stats(self):
        """get_consumed_stats() should return all weapon stat keys."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        consumed = WeaponAbility.get_consumed_stats()

        assert StatKey.DAMAGE_MULT in consumed
        assert StatKey.RANGE_MULT in consumed
        assert StatKey.RELOAD_MULT in consumed
        assert StatKey.ARC_SET in consumed
        assert StatKey.ARC_ADD in consumed

    def test_weapon_ability_get_stat_bindings_info(self):
        """get_stat_bindings_info() should return binding info for UI."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        info = WeaponAbility.get_stat_bindings_info()

        assert isinstance(info, list)
        assert len(info) >= 5  # At least damage, range, reload, arc_set, arc_add

        # Verify info structure
        for item in info:
            assert 'stat_key' in item
            assert 'attribute' in item
            assert 'operation' in item


class TestWeaponAbilityEffectSummary:
    """Tests for WeaponAbility.get_effect_summary()."""

    def test_effect_summary_with_damage_modifier(self):
        """get_effect_summary() should show damage modification."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        # Create mock component
        class MockComponent:
            def __init__(self):
                self.stats = {'damage_mult': 2.0}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 100, 'range': 500, 'reload': 2.0})

        # Trigger recalculate to apply stats
        ability.recalculate()

        summary = ability.get_effect_summary()

        # Should have damage entry showing 2x multiplier
        damage_entry = next((s for s in summary if s['attribute'] == 'damage'), None)
        assert damage_entry is not None
        assert damage_entry['base'] == 100
        assert damage_entry['current'] == 200
        assert damage_entry['stat_value'] == 2.0
        assert damage_entry['operation'] == 'multiply'

    def test_effect_summary_excludes_unmodified_stats(self):
        """get_effect_summary() should not include stats at default values."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'damage_mult': 1.0}  # Default, should not appear
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 100, 'range': 500, 'reload': 2.0})
        ability.recalculate()

        summary = ability.get_effect_summary()

        # Damage should not appear (multiplier is 1.0)
        damage_entry = next((s for s in summary if s['attribute'] == 'damage'), None)
        assert damage_entry is None

    def test_effect_summary_with_multiple_modifiers(self):
        """get_effect_summary() should show all modified stats."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {
                    'damage_mult': 2.0,
                    'range_mult': 1.5,
                    'reload_mult': 0.5,
                }
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 100, 'range': 1000, 'reload': 2.0})
        ability.recalculate()

        summary = ability.get_effect_summary()

        assert len(summary) == 3

        damage_entry = next((s for s in summary if s['attribute'] == 'damage'), None)
        assert damage_entry['current'] == pytest.approx(200)

        range_entry = next((s for s in summary if s['attribute'] == 'range'), None)
        assert range_entry['current'] == pytest.approx(1500)

        reload_entry = next((s for s in summary if s['attribute'] == 'reload_time'), None)
        assert reload_entry['current'] == pytest.approx(1.0)


class TestWeaponAbilityRecalculateWithBindings:
    """Tests to verify recalculate() uses the STAT_BINDINGS."""

    def test_recalculate_applies_damage_mult(self):
        """recalculate() should apply damage_mult from stats."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'damage_mult': 3.0}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 50, 'range': 500, 'reload': 1.0})

        assert ability._base_damage == 50
        ability.recalculate()
        assert ability.damage == pytest.approx(150)

    def test_recalculate_applies_range_mult(self):
        """recalculate() should apply range_mult from stats."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'range_mult': 2.0}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 50, 'range': 1000, 'reload': 1.0})

        ability.recalculate()
        assert ability.range == pytest.approx(2000)

    def test_recalculate_applies_reload_mult(self):
        """recalculate() should apply reload_mult from stats."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'reload_mult': 0.5}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 50, 'range': 500, 'reload': 4.0})

        ability.recalculate()
        assert ability.reload_time == pytest.approx(2.0)

    def test_recalculate_arc_set_overrides_base(self):
        """recalculate() should use arc_set to override firing_arc."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'arc_set': 90}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 50, 'range': 500, 'reload': 1.0, 'firing_arc': 30})

        assert ability._base_firing_arc == 30
        ability.recalculate()
        assert ability.firing_arc == 90

    def test_recalculate_arc_add_adds_to_base(self):
        """recalculate() should use arc_add to add to base firing_arc."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'arc_add': 15}  # No arc_set
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 50, 'range': 500, 'reload': 1.0, 'firing_arc': 30})

        ability.recalculate()
        assert ability.firing_arc == pytest.approx(45)

    def test_recalculate_arc_set_takes_priority(self):
        """When both arc_set and arc_add present, arc_set wins."""
        from game.simulation.components.abilities.weapons import WeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'arc_set': 90, 'arc_add': 15}
                self.ability_stats = {}
                self.data = {}

        component = MockComponent()
        ability = WeaponAbility(component, {'damage': 50, 'range': 500, 'reload': 1.0, 'firing_arc': 30})

        ability.recalculate()
        assert ability.firing_arc == 90  # arc_set wins
