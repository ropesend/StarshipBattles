"""Tests for MassRatioCondition end condition."""

from unittest.mock import MagicMock


def _make_ship(team_id, mass, alive=True, derelict=False):
    ship = MagicMock()
    ship.team_id = team_id
    ship.mass = mass
    ship.is_alive = alive
    ship.is_derelict = derelict
    return ship


class TestMassRatioCondition:

    def test_equal_forces_not_met(self):
        """Equal mass forces should not trigger end."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        cond = MassRatioCondition(threshold=0.10)
        ships = [
            _make_ship(0, 1000), _make_ship(0, 1000),
            _make_ship(1, 1000), _make_ship(1, 1000),
        ]
        assert cond.is_met(ships, 0) is False

    def test_one_side_below_threshold(self):
        """When one side has <10% of the other's mass, battle ends."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        cond = MassRatioCondition(threshold=0.10)
        ships = [
            _make_ship(0, 1000), _make_ship(0, 1000),  # 2000 total
            _make_ship(1, 100),  # 100 = 5% of 2000
        ]
        assert cond.is_met(ships, 0) is True

    def test_just_above_threshold(self):
        """At exactly threshold, battle should NOT end."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        cond = MassRatioCondition(threshold=0.10)
        ships = [
            _make_ship(0, 1000),
            _make_ship(1, 100),  # 100/1000 = 10% = exactly threshold
        ]
        assert cond.is_met(ships, 0) is False

    def test_dead_ships_excluded(self):
        """Dead ships should not count toward fighting mass."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        cond = MassRatioCondition(threshold=0.10)
        ships = [
            _make_ship(0, 1000),
            _make_ship(1, 1000),
            _make_ship(1, 5000, alive=False),  # Dead — excluded
        ]
        assert cond.is_met(ships, 0) is False  # 1000 vs 1000 = 100%

    def test_derelict_ships_excluded(self):
        """Derelict ships should not count toward fighting mass."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        cond = MassRatioCondition(threshold=0.10)
        ships = [
            _make_ship(0, 1000),
            _make_ship(1, 50),
            _make_ship(1, 5000, derelict=True),  # Derelict — excluded
        ]
        assert cond.is_met(ships, 0) is True  # 50/1000 = 5%

    def test_one_side_empty_met(self):
        """If one side has no fighting mass, condition is met."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        cond = MassRatioCondition(threshold=0.10)
        ships = [
            _make_ship(0, 1000),
            _make_ship(1, 500, alive=False),
        ]
        assert cond.is_met(ships, 0) is True

    def test_serialization_round_trip(self):
        """to_dict/from_dict round trip."""
        from game.simulation.systems.battle_end_conditions import MassRatioCondition

        original = MassRatioCondition(threshold=0.15)
        data = original.to_dict()
        restored = MassRatioCondition.from_dict(data)
        assert restored.threshold == 0.15
