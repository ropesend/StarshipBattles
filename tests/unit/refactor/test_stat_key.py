"""
Tests for StatKey enum - Phase 1 Task 1.1

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest


class TestStatKeyEnum:
    """Tests for the StatKey enumeration."""

    def test_stat_key_enum_exists(self):
        """StatKey enum should be importable."""
        from game.simulation.components.abilities.stat_keys import StatKey
        assert StatKey is not None

    def test_stat_key_has_all_current_stats(self):
        """StatKey enum should have all stats from current stats dict in component.py."""
        from game.simulation.components.abilities.stat_keys import StatKey

        # All stats that currently exist in _calculate_modifier_stats()
        required_stats = [
            'MASS_MULT',
            'HP_MULT',
            'DAMAGE_MULT',
            'RANGE_MULT',
            'COST_MULT',
            'THRUST_MULT',
            'TURN_MULT',
            'STRATEGIC_MULT',
            'ENERGY_GEN_MULT',
            'CAPACITY_MULT',
            'CREW_CAPACITY_MULT',
            'LIFE_SUPPORT_CAPACITY_MULT',
            'CONSUMPTION_MULT',
            'MASS_ADD',
            'ARC_ADD',
            'ACCURACY_ADD',
            'ARC_SET',
            'RELOAD_MULT',
            'ENDURANCE_MULT',
            'PROJECTILE_HP_MULT',
            'PROJECTILE_DAMAGE_MULT',
            'PROJECTILE_STEALTH_LEVEL',
            'CREW_REQ_MULT',
        ]

        for stat_name in required_stats:
            assert hasattr(StatKey, stat_name), f"StatKey missing: {stat_name}"

    def test_stat_key_value_matches_string(self):
        """StatKey enum values should match the string keys used in stats dict."""
        from game.simulation.components.abilities.stat_keys import StatKey

        # Check that enum values are the lowercase string versions
        assert StatKey.DAMAGE_MULT.value == 'damage_mult'
        assert StatKey.MASS_MULT.value == 'mass_mult'
        assert StatKey.HP_MULT.value == 'hp_mult'
        assert StatKey.RANGE_MULT.value == 'range_mult'
        assert StatKey.RELOAD_MULT.value == 'reload_mult'
        assert StatKey.THRUST_MULT.value == 'thrust_mult'
        assert StatKey.TURN_MULT.value == 'turn_mult'
        assert StatKey.STRATEGIC_MULT.value == 'strategic_mult'
        assert StatKey.ACCURACY_ADD.value == 'accuracy_add'
        assert StatKey.ARC_ADD.value == 'arc_add'
        assert StatKey.ARC_SET.value == 'arc_set'

    def test_stat_key_can_be_used_as_dict_key(self):
        """StatKey enum members should be usable as dictionary keys."""
        from game.simulation.components.abilities.stat_keys import StatKey

        stats = {
            StatKey.DAMAGE_MULT: 1.5,
            StatKey.RANGE_MULT: 2.0,
        }

        assert stats[StatKey.DAMAGE_MULT] == 1.5
        assert stats[StatKey.RANGE_MULT] == 2.0

    def test_stat_key_value_can_index_stats_dict(self):
        """StatKey.value should work with existing stats dictionaries."""
        from game.simulation.components.abilities.stat_keys import StatKey

        # Simulate existing stats dict format
        stats = {
            'damage_mult': 1.5,
            'range_mult': 2.0,
        }

        assert stats.get(StatKey.DAMAGE_MULT.value) == 1.5
        assert stats.get(StatKey.RANGE_MULT.value) == 2.0

    def test_stat_key_iteration(self):
        """Should be able to iterate over all StatKey members."""
        from game.simulation.components.abilities.stat_keys import StatKey

        stat_keys = list(StatKey)
        assert len(stat_keys) >= 23  # At least 23 stats defined

        # All should have string values
        for key in stat_keys:
            assert isinstance(key.value, str)
