"""
Tests for composable battle end conditions system.

TDD tests for the protocol-based end condition system including:
- Leaf conditions: TickLimit, TeamEliminated, TeamIncapacitated, Escape, ShipDestroyed, Never
- Composite conditions: AnyCondition, AllCondition
- Serialization round-trips (to_dict / from_dict)
- IEndCondition protocol conformance
"""
import pytest
from unittest.mock import Mock

import pygame

from game.simulation.systems.battle_end_conditions import (
    IEndCondition,
    TickLimitCondition,
    TeamEliminatedCondition,
    TeamIncapacitatedCondition,
    EscapeCondition,
    ShipDestroyedCondition,
    NeverCondition,
    AnyCondition,
    AllCondition,
    end_condition_from_dict,
)
# ============================================================================
# Test Helpers
# ============================================================================

def _make_ship(team_id=0, is_alive=True, is_derelict=False, name="Ship",
               position=None, thrust=100.0, turn_speed=10.0,
               has_weapons=True, has_engines=True):
    """Create a mock ship for end condition testing."""
    ship = Mock()
    ship.team_id = team_id
    ship.is_alive = is_alive
    ship.is_derelict = is_derelict
    ship.name = name
    ship.position = position or pygame.math.Vector2(0, 0)
    ship.total_thrust = thrust if has_engines else 0.0
    ship.turn_speed = turn_speed if has_engines else 0.0

    # Components for capability check
    if has_weapons:
        weapon = Mock()
        weapon.is_operational = True
        weapon.type = "Weapon"
        ship.get_all_components.return_value = [weapon]
    else:
        ship.get_all_components.return_value = []

    return ship


# ============================================================================
# TickLimitCondition
# ============================================================================

class TestTickLimitCondition:
    """Tests for time-based end condition."""

    def test_not_met_before_limit(self):
        cond = TickLimitCondition(max_ticks=500)
        ships = [_make_ship()]
        assert cond.is_met(ships, tick=499) is False

    def test_met_at_limit(self):
        cond = TickLimitCondition(max_ticks=500)
        ships = [_make_ship()]
        assert cond.is_met(ships, tick=500) is True

    def test_met_past_limit(self):
        cond = TickLimitCondition(max_ticks=500)
        ships = [_make_ship()]
        assert cond.is_met(ships, tick=1000) is True

    def test_description(self):
        cond = TickLimitCondition(max_ticks=500)
        assert "500" in cond.description

    def test_serialization_roundtrip(self):
        cond = TickLimitCondition(max_ticks=500)
        data = cond.to_dict()
        assert data["type"] == "tick_limit"
        assert data["max_ticks"] == 500
        restored = end_condition_from_dict(data)
        assert isinstance(restored, TickLimitCondition)
        assert restored.max_ticks == 500

    def test_protocol_conformance(self):
        cond = TickLimitCondition(max_ticks=100)
        assert isinstance(cond, IEndCondition)


# ============================================================================
# TeamEliminatedCondition
# ============================================================================

class TestTeamEliminatedCondition:
    """Tests for HP-based end condition."""

    def test_not_met_both_teams_alive(self):
        cond = TeamEliminatedCondition()
        ships = [_make_ship(team_id=0), _make_ship(team_id=1)]
        assert cond.is_met(ships, tick=0) is False

    def test_met_team0_eliminated(self):
        cond = TeamEliminatedCondition()
        ships = [
            _make_ship(team_id=0, is_alive=False),
            _make_ship(team_id=1),
        ]
        assert cond.is_met(ships, tick=0) is True

    def test_met_team1_eliminated(self):
        cond = TeamEliminatedCondition()
        ships = [
            _make_ship(team_id=0),
            _make_ship(team_id=1, is_alive=False),
        ]
        assert cond.is_met(ships, tick=0) is True

    def test_check_derelict_false_derelict_counts_alive(self):
        """With check_derelict=False, derelict ships are still 'alive'."""
        cond = TeamEliminatedCondition(check_derelict=False)
        ships = [
            _make_ship(team_id=0, is_derelict=True),
            _make_ship(team_id=1),
        ]
        assert cond.is_met(ships, tick=0) is False

    def test_check_derelict_true_derelict_counts_dead(self):
        """With check_derelict=True, derelict ships count as eliminated."""
        cond = TeamEliminatedCondition(check_derelict=True)
        ships = [
            _make_ship(team_id=0, is_derelict=True),
            _make_ship(team_id=1),
        ]
        assert cond.is_met(ships, tick=0) is True

    def test_empty_ships_not_met(self):
        """No ships means neither team eliminated (edge case)."""
        cond = TeamEliminatedCondition()
        assert cond.is_met([], tick=0) is False

    def test_multiple_ships_per_team(self):
        """Only met when ALL ships on a team are dead."""
        cond = TeamEliminatedCondition()
        ships = [
            _make_ship(team_id=0, is_alive=False),
            _make_ship(team_id=0),  # one still alive
            _make_ship(team_id=1),
        ]
        assert cond.is_met(ships, tick=0) is False

    def test_serialization_roundtrip(self):
        cond = TeamEliminatedCondition(check_derelict=True)
        data = cond.to_dict()
        assert data["type"] == "team_eliminated"
        assert data["check_derelict"] is True
        restored = end_condition_from_dict(data)
        assert isinstance(restored, TeamEliminatedCondition)
        assert restored.check_derelict is True

    def test_serialization_default(self):
        cond = TeamEliminatedCondition()
        data = cond.to_dict()
        restored = end_condition_from_dict(data)
        assert restored.check_derelict is False


# ============================================================================
# TeamIncapacitatedCondition
# ============================================================================

class TestTeamIncapacitatedCondition:
    """Tests for capability-based end condition."""

    def test_not_met_both_capable(self):
        cond = TeamIncapacitatedCondition()
        ships = [
            _make_ship(team_id=0, has_weapons=True),
            _make_ship(team_id=1, has_weapons=True),
        ]
        assert cond.is_met(ships, tick=0) is False

    def test_met_team_no_weapons_no_engines(self):
        cond = TeamIncapacitatedCondition()
        ships = [
            _make_ship(team_id=0, has_weapons=False, has_engines=False),
            _make_ship(team_id=1, has_weapons=True),
        ]
        assert cond.is_met(ships, tick=0) is True

    def test_not_met_team_has_engines_no_weapons(self):
        """Team with engines but no weapons is still capable (can flee)."""
        cond = TeamIncapacitatedCondition()
        ships = [
            _make_ship(team_id=0, has_weapons=False, has_engines=True),
            _make_ship(team_id=1, has_weapons=True),
        ]
        assert cond.is_met(ships, tick=0) is False

    def test_dead_ships_ignored(self):
        """Dead ships don't contribute to capability."""
        cond = TeamIncapacitatedCondition()
        ships = [
            _make_ship(team_id=0, is_alive=False, has_weapons=True),
            _make_ship(team_id=1, has_weapons=True),
        ]
        # Team 0 has no alive ships with capability
        assert cond.is_met(ships, tick=0) is True

    def test_serialization_roundtrip(self):
        cond = TeamIncapacitatedCondition()
        data = cond.to_dict()
        assert data["type"] == "team_incapacitated"
        restored = end_condition_from_dict(data)
        assert isinstance(restored, TeamIncapacitatedCondition)


# ============================================================================
# EscapeCondition
# ============================================================================

class TestEscapeCondition:
    """Tests for distance-based escape end condition."""

    def test_not_met_ships_inside_radius(self):
        cond = EscapeCondition(escape_radius=5000.0)
        ships = [
            _make_ship(team_id=0, position=pygame.math.Vector2(100, 100)),
            _make_ship(team_id=1, position=pygame.math.Vector2(200, 200)),
        ]
        assert cond.is_met(ships, tick=0) is False

    def test_met_any_ship_outside_radius(self):
        """Default: ANY ship outside radius triggers escape."""
        cond = EscapeCondition(escape_radius=5000.0)
        ships = [
            _make_ship(team_id=0, position=pygame.math.Vector2(6000, 0)),
            _make_ship(team_id=1, position=pygame.math.Vector2(100, 100)),
        ]
        assert cond.is_met(ships, tick=0) is True

    def test_escape_team_filter(self):
        """Only specified team's escape counts."""
        cond = EscapeCondition(escape_radius=5000.0, escape_team=1)
        ships = [
            _make_ship(team_id=0, position=pygame.math.Vector2(6000, 0)),
            _make_ship(team_id=1, position=pygame.math.Vector2(100, 100)),
        ]
        # Team 0 escaped but we only check team 1
        assert cond.is_met(ships, tick=0) is False

    def test_escape_all_ships(self):
        """When escape_all_ships=True, ALL ships must be outside."""
        cond = EscapeCondition(escape_radius=5000.0, escape_all_ships=True)
        ships = [
            _make_ship(team_id=0, position=pygame.math.Vector2(6000, 0)),
            _make_ship(team_id=0, position=pygame.math.Vector2(100, 100)),
        ]
        assert cond.is_met(ships, tick=0) is False

    def test_escape_all_ships_all_outside(self):
        cond = EscapeCondition(escape_radius=5000.0, escape_all_ships=True)
        ships = [
            _make_ship(team_id=0, position=pygame.math.Vector2(6000, 0)),
            _make_ship(team_id=0, position=pygame.math.Vector2(0, 6000)),
        ]
        assert cond.is_met(ships, tick=0) is True

    def test_arena_center_offset(self):
        """Distance measured from arena_center, not origin."""
        center = (1000.0, 1000.0)
        cond = EscapeCondition(escape_radius=500.0, arena_center=center)
        # Ship at (1000, 1000) is at center, distance = 0
        ships = [_make_ship(position=pygame.math.Vector2(1000, 1000))]
        assert cond.is_met(ships, tick=0) is False

        # Ship at (1600, 1000) is 600 from center, > 500 radius
        ships = [_make_ship(position=pygame.math.Vector2(1600, 1000))]
        assert cond.is_met(ships, tick=0) is True

    def test_dead_ships_ignored(self):
        cond = EscapeCondition(escape_radius=5000.0)
        ships = [_make_ship(is_alive=False, position=pygame.math.Vector2(6000, 0))]
        assert cond.is_met(ships, tick=0) is False

    def test_serialization_roundtrip(self):
        cond = EscapeCondition(
            escape_radius=5000.0,
            arena_center=(100.0, 200.0),
            escape_team=1,
            escape_all_ships=True,
        )
        data = cond.to_dict()
        assert data["type"] == "escape"
        assert data["escape_radius"] == 5000.0
        assert data["arena_center"] == [100.0, 200.0]
        restored = end_condition_from_dict(data)
        assert isinstance(restored, EscapeCondition)
        assert restored.escape_radius == 5000.0
        assert restored.arena_center == (100.0, 200.0)
        assert restored.escape_team == 1
        assert restored.escape_all_ships is True


# ============================================================================
# ShipDestroyedCondition
# ============================================================================

class TestShipDestroyedCondition:
    """Tests for flagship/named ship destruction condition."""

    def test_not_met_ship_alive(self):
        cond = ShipDestroyedCondition(ship_name="Flagship")
        ships = [_make_ship(name="Flagship", is_alive=True)]
        assert cond.is_met(ships, tick=0) is False

    def test_met_ship_dead(self):
        cond = ShipDestroyedCondition(ship_name="Flagship")
        ships = [_make_ship(name="Flagship", is_alive=False)]
        assert cond.is_met(ships, tick=0) is True

    def test_ship_not_found_not_met(self):
        """If named ship not in battle, condition never triggers."""
        cond = ShipDestroyedCondition(ship_name="Nonexistent")
        ships = [_make_ship(name="OtherShip")]
        assert cond.is_met(ships, tick=0) is False

    def test_case_sensitive(self):
        cond = ShipDestroyedCondition(ship_name="Flagship")
        ships = [_make_ship(name="flagship", is_alive=False)]
        assert cond.is_met(ships, tick=0) is False

    def test_serialization_roundtrip(self):
        cond = ShipDestroyedCondition(ship_name="USS Enterprise")
        data = cond.to_dict()
        assert data["type"] == "ship_destroyed"
        assert data["ship_name"] == "USS Enterprise"
        restored = end_condition_from_dict(data)
        assert isinstance(restored, ShipDestroyedCondition)
        assert restored.ship_name == "USS Enterprise"


# ============================================================================
# NeverCondition
# ============================================================================

class TestNeverCondition:
    """Tests for manual/never-end condition."""

    def test_never_met(self):
        cond = NeverCondition()
        ships = [_make_ship()]
        assert cond.is_met(ships, tick=0) is False
        assert cond.is_met(ships, tick=999999) is False
        assert cond.is_met([], tick=0) is False

    def test_serialization_roundtrip(self):
        cond = NeverCondition()
        data = cond.to_dict()
        assert data["type"] == "never"
        restored = end_condition_from_dict(data)
        assert isinstance(restored, NeverCondition)


# ============================================================================
# AnyCondition (OR composite)
# ============================================================================

class TestAnyCondition:
    """Tests for OR-composite end condition."""

    def test_met_when_any_child_met(self):
        cond = AnyCondition([
            TickLimitCondition(max_ticks=100),
            TeamEliminatedCondition(),
        ])
        ships = [_make_ship(team_id=0), _make_ship(team_id=1)]
        # Tick limit met
        assert cond.is_met(ships, tick=100) is True

    def test_not_met_when_no_child_met(self):
        cond = AnyCondition([
            TickLimitCondition(max_ticks=100),
            TeamEliminatedCondition(),
        ])
        ships = [_make_ship(team_id=0), _make_ship(team_id=1)]
        assert cond.is_met(ships, tick=50) is False

    def test_met_when_second_child_met(self):
        cond = AnyCondition([
            TickLimitCondition(max_ticks=1000),
            TeamEliminatedCondition(),
        ])
        ships = [
            _make_ship(team_id=0, is_alive=False),
            _make_ship(team_id=1),
        ]
        assert cond.is_met(ships, tick=50) is True

    def test_empty_conditions_not_met(self):
        cond = AnyCondition([])
        assert cond.is_met([], tick=0) is False

    def test_serialization_roundtrip(self):
        cond = AnyCondition([
            TickLimitCondition(max_ticks=500),
            TeamEliminatedCondition(check_derelict=True),
        ])
        data = cond.to_dict()
        assert data["type"] == "any"
        assert len(data["conditions"]) == 2
        restored = end_condition_from_dict(data)
        assert isinstance(restored, AnyCondition)
        assert len(restored.conditions) == 2
        assert isinstance(restored.conditions[0], TickLimitCondition)
        assert isinstance(restored.conditions[1], TeamEliminatedCondition)

    def test_description(self):
        cond = AnyCondition([
            TickLimitCondition(max_ticks=500),
            TeamEliminatedCondition(),
        ])
        desc = cond.description
        assert "OR" in desc or "or" in desc


# ============================================================================
# AllCondition (AND composite)
# ============================================================================

class TestAllCondition:
    """Tests for AND-composite end condition."""

    def test_not_met_when_only_one_child_met(self):
        cond = AllCondition([
            TickLimitCondition(max_ticks=100),
            TeamEliminatedCondition(),
        ])
        ships = [_make_ship(team_id=0), _make_ship(team_id=1)]
        # Only tick limit met
        assert cond.is_met(ships, tick=100) is False

    def test_met_when_all_children_met(self):
        cond = AllCondition([
            TickLimitCondition(max_ticks=100),
            TeamEliminatedCondition(),
        ])
        ships = [
            _make_ship(team_id=0, is_alive=False),
            _make_ship(team_id=1),
        ]
        assert cond.is_met(ships, tick=100) is True

    def test_empty_conditions_met(self):
        """All([]) is vacuously true."""
        cond = AllCondition([])
        assert cond.is_met([], tick=0) is True

    def test_serialization_roundtrip(self):
        cond = AllCondition([
            TickLimitCondition(max_ticks=500),
            ShipDestroyedCondition(ship_name="Boss"),
        ])
        data = cond.to_dict()
        assert data["type"] == "all"
        restored = end_condition_from_dict(data)
        assert isinstance(restored, AllCondition)
        assert len(restored.conditions) == 2


# ============================================================================
# Nested Composites
# ============================================================================

class TestNestedComposites:
    """Tests for deeply nested composite conditions."""

    def test_any_containing_all(self):
        """AnyCondition containing an AllCondition."""
        cond = AnyCondition([
            AllCondition([
                TickLimitCondition(max_ticks=100),
                ShipDestroyedCondition(ship_name="Boss"),
            ]),
            TeamEliminatedCondition(),
        ])
        # Neither child met
        ships = [_make_ship(name="Boss"), _make_ship(team_id=1)]
        assert cond.is_met(ships, tick=50) is False

        # TeamEliminated met (second child of Any)
        ships = [_make_ship(team_id=0, is_alive=False), _make_ship(team_id=1)]
        assert cond.is_met(ships, tick=50) is True

        # All met: tick >= 100 AND Boss dead (first child of Any)
        ships = [_make_ship(name="Boss", is_alive=False), _make_ship(team_id=1)]
        assert cond.is_met(ships, tick=100) is True

    def test_nested_serialization_roundtrip(self):
        cond = AnyCondition([
            AllCondition([
                TickLimitCondition(max_ticks=100),
                ShipDestroyedCondition(ship_name="Boss"),
            ]),
            TeamEliminatedCondition(),
        ])
        data = cond.to_dict()
        restored = end_condition_from_dict(data)
        # Verify structure
        assert isinstance(restored, AnyCondition)
        assert isinstance(restored.conditions[0], AllCondition)
        inner = restored.conditions[0]
        assert isinstance(inner.conditions[0], TickLimitCondition)
        assert isinstance(inner.conditions[1], ShipDestroyedCondition)
        assert inner.conditions[1].ship_name == "Boss"


# ============================================================================
# Deserialization Edge Cases
# ============================================================================

class TestDeserialization:
    """Tests for end_condition_from_dict edge cases."""

    def test_unknown_type_raises(self):
        with pytest.raises(KeyError):
            end_condition_from_dict({"type": "nonexistent"})

    def test_missing_type_raises(self):
        with pytest.raises(KeyError):
            end_condition_from_dict({"max_ticks": 500})


# ============================================================================
# Protocol Conformance
# ============================================================================

class TestProtocolConformance:
    """All condition classes implement IEndCondition."""

    @pytest.mark.parametrize("cls,kwargs", [
        (TickLimitCondition, {"max_ticks": 100}),
        (TeamEliminatedCondition, {}),
        (TeamIncapacitatedCondition, {}),
        (EscapeCondition, {"escape_radius": 5000.0}),
        (ShipDestroyedCondition, {"ship_name": "Test"}),
        (NeverCondition, {}),
        (AnyCondition, {"conditions": []}),
        (AllCondition, {"conditions": []}),
    ])
    def test_isinstance_check(self, cls, kwargs):
        cond = cls(**kwargs)
        assert isinstance(cond, IEndCondition)

    @pytest.mark.parametrize("cls,kwargs", [
        (TickLimitCondition, {"max_ticks": 100}),
        (TeamEliminatedCondition, {}),
        (TeamIncapacitatedCondition, {}),
        (EscapeCondition, {"escape_radius": 5000.0}),
        (ShipDestroyedCondition, {"ship_name": "Test"}),
        (NeverCondition, {}),
        (AnyCondition, {"conditions": []}),
        (AllCondition, {"conditions": []}),
    ])
    def test_has_description(self, cls, kwargs):
        cond = cls(**kwargs)
        assert isinstance(cond.description, str)
        assert len(cond.description) > 0

    @pytest.mark.parametrize("cls,kwargs", [
        (TickLimitCondition, {"max_ticks": 100}),
        (TeamEliminatedCondition, {}),
        (TeamIncapacitatedCondition, {}),
        (EscapeCondition, {"escape_radius": 5000.0}),
        (ShipDestroyedCondition, {"ship_name": "Test"}),
        (NeverCondition, {}),
        (AnyCondition, {"conditions": []}),
        (AllCondition, {"conditions": []}),
    ])
    def test_to_dict_has_type(self, cls, kwargs):
        cond = cls(**kwargs)
        data = cond.to_dict()
        assert "type" in data
