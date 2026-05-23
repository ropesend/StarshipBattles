"""
Tests for Propulsion Ability STAT_BINDINGS - Phase 3 Tasks 3.5-3.7

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


def _ability_cls(name):
    """Lazy import helper to keep imports inside parametrized tests cheap."""
    from game.simulation.components.abilities import propulsion as _prop

    return getattr(_prop, name)


@pytest.mark.parametrize(
    "ability_name,stat_key_name,attr_name,base_value,mult_value,expected",
    [
        ("CombatPropulsion", "THRUST_MULT", "thrust_force", 1000, 2.0, 2000),
        ("ManeuveringThruster", "TURN_MULT", "turn_rate", 30, 3.0, 90),
        ("StrategicMovement", "STRATEGIC_MULT", "movement_points", 10, 4.0, 40),
    ],
    ids=["CombatPropulsion", "ManeuveringThruster", "StrategicMovement"],
)
class TestPropulsionAbilityBindings:
    """Parametrized tests for the three propulsion ability STAT_BINDINGS triplets."""

    def test_has_multiply_binding(
        self, ability_name, stat_key_name, attr_name, base_value, mult_value, expected
    ):
        ability_cls = _ability_cls(ability_name)
        stat_key = getattr(StatKey, stat_key_name)
        bindings = [b for b in ability_cls.STAT_BINDINGS if b.stat_key == stat_key]
        assert len(bindings) == 1
        binding = bindings[0]
        assert binding.attribute_name == attr_name
        assert binding.operation == "multiply"

    def test_get_consumed_stats(
        self, ability_name, stat_key_name, attr_name, base_value, mult_value, expected
    ):
        ability_cls = _ability_cls(ability_name)
        stat_key = getattr(StatKey, stat_key_name)
        assert stat_key in ability_cls.get_consumed_stats()

    def test_recalculate_applies_multiplier(
        self, ability_name, stat_key_name, attr_name, base_value, mult_value, expected
    ):
        ability_cls = _ability_cls(ability_name)
        stat_key = getattr(StatKey, stat_key_name)

        class MockComponent:
            def __init__(self):
                # attribute name for stat dict key is the lowercase stat_key
                self.stats = {stat_key.value if hasattr(stat_key, "value") else stat_key_name.lower(): mult_value}
                self.ability_stats = {}

        # build component then patch in the correct dict-key
        component = MockComponent()
        # stat_keys.StatKey values are typically lowercase strings (e.g., "thrust_mult");
        # rebuild stats dict to use the binding's stat_key value:
        component.stats = {stat_key.value: mult_value} if hasattr(stat_key, "value") else {stat_key_name.lower(): mult_value}
        ability = ability_cls(component, {"value": base_value})
        ability.recalculate()
        assert getattr(ability, attr_name) == pytest.approx(expected)


class TestWarpJumpBindings:
    """Tests for WarpJump STAT_BINDINGS (should be empty - no modifier support)."""

    def test_warp_jump_has_empty_bindings(self):
        """WarpJump should have empty STAT_BINDINGS (no modifiers affect it)."""
        from game.simulation.components.abilities.propulsion import WarpJump

        assert hasattr(WarpJump, 'STAT_BINDINGS')
        # WarpJump doesn't consume any stats
        assert len(WarpJump.STAT_BINDINGS) == 0

    def test_warp_jump_get_consumed_stats_empty(self):
        """get_consumed_stats() should return empty set."""
        from game.simulation.components.abilities.propulsion import WarpJump

        consumed = WarpJump.get_consumed_stats()
        assert len(consumed) == 0


class TestPropulsionSyncData:
    """Tests for propulsion ability sync_data consistency (SIM-13)."""

    def test_combat_propulsion_sync_data_updates_thrust(self):
        """CombatPropulsion.sync_data should update base_thrust."""
        from game.simulation.components.abilities.propulsion import CombatPropulsion

        class MockComponent:
            stats = {}

        ability = CombatPropulsion(MockComponent(), {'value': 1000})
        assert ability.base_thrust == 1000

        ability.sync_data({'value': 2000})
        assert ability.base_thrust == 2000
        assert ability.thrust_force == 2000

    def test_maneuvering_thruster_sync_data_updates_turn_rate(self):
        """ManeuveringThruster.sync_data should update base_turn_rate."""
        from game.simulation.components.abilities.propulsion import ManeuveringThruster

        class MockComponent:
            stats = {}

        ability = ManeuveringThruster(MockComponent(), {'value': 30})
        assert ability.base_turn_rate == 30

        ability.sync_data({'value': 60})
        assert ability.base_turn_rate == 60
        assert ability.turn_rate == 60

    def test_strategic_movement_sync_data_updates_movement_points(self):
        """StrategicMovement.sync_data should update base_movement_points."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        class MockComponent:
            stats = {}

        ability = StrategicMovement(MockComponent(), {'value': 10})
        assert ability.base_movement_points == 10

        ability.sync_data({'value': 20})
        assert ability.base_movement_points == 20
        assert ability.movement_points == 20
