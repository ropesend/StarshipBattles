"""
Tests for BeamWeaponAbility STAT_BINDINGS - Phase 3 Task 3.2

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestBeamWeaponAbilityStatBindings:
    """Tests for BeamWeaponAbility STAT_BINDINGS declarations."""

    def test_beam_weapon_inherits_weapon_bindings(self):
        """BeamWeaponAbility should inherit all WeaponAbility bindings."""
        from game.simulation.components.abilities.weapons import BeamWeaponAbility, WeaponAbility

        beam_stats = BeamWeaponAbility.get_consumed_stats()
        weapon_stats = WeaponAbility.get_consumed_stats()

        # Beam should consume all weapon stats plus accuracy
        for stat in weapon_stats:
            assert stat in beam_stats

    def test_beam_weapon_has_accuracy_binding(self):
        """BeamWeaponAbility should have ACCURACY_ADD binding for 'base_accuracy'."""
        from game.simulation.components.abilities.weapons import BeamWeaponAbility

        accuracy_bindings = [b for b in BeamWeaponAbility.STAT_BINDINGS
                            if b.stat_key == StatKey.ACCURACY_ADD]
        assert len(accuracy_bindings) == 1

        binding = accuracy_bindings[0]
        assert binding.attribute_name == 'base_accuracy'
        assert binding.operation == 'add'

    def test_beam_weapon_get_consumed_stats_includes_accuracy(self):
        """get_consumed_stats() should include ACCURACY_ADD."""
        from game.simulation.components.abilities.weapons import BeamWeaponAbility

        consumed = BeamWeaponAbility.get_consumed_stats()
        assert StatKey.ACCURACY_ADD in consumed


class TestBeamWeaponAbilityRecalculate:
    """Tests for BeamWeaponAbility.recalculate() with accuracy stats."""

    def test_recalculate_applies_accuracy_add(self):
        """recalculate() should apply accuracy_add from stats."""
        from game.simulation.components.abilities.weapons import BeamWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'accuracy_add': 0.5}
                self.data = {}

        component = MockComponent()
        ability = BeamWeaponAbility(component, {
            'damage': 100,
            'range': 500,
            'reload': 1.0,
            'base_accuracy': 1.0
        })

        assert ability._base_accuracy == 1.0
        ability.recalculate()
        assert ability.base_accuracy == pytest.approx(1.5)

    def test_recalculate_combines_weapon_and_accuracy_stats(self):
        """recalculate() should apply both weapon and accuracy modifiers."""
        from game.simulation.components.abilities.weapons import BeamWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {
                    'damage_mult': 2.0,
                    'accuracy_add': 0.25
                }
                self.data = {}

        component = MockComponent()
        ability = BeamWeaponAbility(component, {
            'damage': 50,
            'range': 500,
            'reload': 1.0,
            'base_accuracy': 0.8
        })

        ability.recalculate()
        assert ability.damage == pytest.approx(100)  # 50 * 2.0
        assert ability.base_accuracy == pytest.approx(1.05)  # 0.8 + 0.25


class TestBeamWeaponAbilityEffectSummary:
    """Tests for BeamWeaponAbility.get_effect_summary() with accuracy."""

    def test_effect_summary_includes_accuracy(self):
        """get_effect_summary() should include accuracy modification."""
        from game.simulation.components.abilities.weapons import BeamWeaponAbility

        class MockComponent:
            def __init__(self):
                self.stats = {'accuracy_add': 0.5}
                self.data = {}

        component = MockComponent()
        ability = BeamWeaponAbility(component, {
            'damage': 100,
            'range': 500,
            'reload': 1.0,
            'base_accuracy': 1.0
        })
        ability.recalculate()

        summary = ability.get_effect_summary()

        accuracy_entry = next((s for s in summary if s['attribute'] == 'base_accuracy'), None)
        assert accuracy_entry is not None
        assert accuracy_entry['base'] == 1.0
        assert accuracy_entry['current'] == pytest.approx(1.5)
        assert accuracy_entry['operation'] == 'add'
