"""
Tests for Propulsion Ability STAT_BINDINGS - Phase 3 Tasks 3.5-3.7

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestCombatPropulsionBindings:
    """Tests for CombatPropulsion STAT_BINDINGS."""

    def test_combat_propulsion_has_thrust_binding(self):
        """CombatPropulsion should have THRUST_MULT binding for 'thrust_force'."""
        from game.simulation.components.abilities.propulsion import CombatPropulsion

        thrust_bindings = [b for b in CombatPropulsion.STAT_BINDINGS
                          if b.stat_key == StatKey.THRUST_MULT]
        assert len(thrust_bindings) == 1

        binding = thrust_bindings[0]
        assert binding.attribute_name == 'thrust_force'
        assert binding.operation == 'multiply'

    def test_combat_propulsion_get_consumed_stats(self):
        """get_consumed_stats() should return THRUST_MULT."""
        from game.simulation.components.abilities.propulsion import CombatPropulsion

        consumed = CombatPropulsion.get_consumed_stats()
        assert StatKey.THRUST_MULT in consumed

    def test_combat_propulsion_recalculate(self):
        """recalculate() should apply thrust_mult."""
        from game.simulation.components.abilities.propulsion import CombatPropulsion

        class MockComponent:
            def __init__(self):
                self.stats = {'thrust_mult': 2.0}

        component = MockComponent()
        ability = CombatPropulsion(component, {'value': 1000})

        ability.recalculate()
        assert ability.thrust_force == pytest.approx(2000)


class TestManeuveringThrusterBindings:
    """Tests for ManeuveringThruster STAT_BINDINGS."""

    def test_maneuvering_thruster_has_turn_binding(self):
        """ManeuveringThruster should have TURN_MULT binding for 'turn_rate'."""
        from game.simulation.components.abilities.propulsion import ManeuveringThruster

        turn_bindings = [b for b in ManeuveringThruster.STAT_BINDINGS
                         if b.stat_key == StatKey.TURN_MULT]
        assert len(turn_bindings) == 1

        binding = turn_bindings[0]
        assert binding.attribute_name == 'turn_rate'
        assert binding.operation == 'multiply'

    def test_maneuvering_thruster_get_consumed_stats(self):
        """get_consumed_stats() should return TURN_MULT."""
        from game.simulation.components.abilities.propulsion import ManeuveringThruster

        consumed = ManeuveringThruster.get_consumed_stats()
        assert StatKey.TURN_MULT in consumed

    def test_maneuvering_thruster_recalculate(self):
        """recalculate() should apply turn_mult."""
        from game.simulation.components.abilities.propulsion import ManeuveringThruster

        class MockComponent:
            def __init__(self):
                self.stats = {'turn_mult': 3.0}

        component = MockComponent()
        ability = ManeuveringThruster(component, {'value': 30})

        ability.recalculate()
        assert ability.turn_rate == pytest.approx(90)


class TestStrategicMovementBindings:
    """Tests for StrategicMovement STAT_BINDINGS."""

    def test_strategic_movement_has_strategic_binding(self):
        """StrategicMovement should have STRATEGIC_MULT binding for 'movement_points'."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        strategic_bindings = [b for b in StrategicMovement.STAT_BINDINGS
                              if b.stat_key == StatKey.STRATEGIC_MULT]
        assert len(strategic_bindings) == 1

        binding = strategic_bindings[0]
        assert binding.attribute_name == 'movement_points'
        assert binding.operation == 'multiply'

    def test_strategic_movement_get_consumed_stats(self):
        """get_consumed_stats() should return STRATEGIC_MULT."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        consumed = StrategicMovement.get_consumed_stats()
        assert StatKey.STRATEGIC_MULT in consumed

    def test_strategic_movement_recalculate(self):
        """recalculate() should apply strategic_mult."""
        from game.simulation.components.abilities.propulsion import StrategicMovement

        class MockComponent:
            def __init__(self):
                self.stats = {'strategic_mult': 4.0}

        component = MockComponent()
        ability = StrategicMovement(component, {'value': 10})

        ability.recalculate()
        assert ability.movement_points == pytest.approx(40)


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
