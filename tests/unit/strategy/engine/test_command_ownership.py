# -*- coding: utf-8 -*-
"""Tests for command ownership validation.

BUG-125: replaces the prior fleet-ID-collision contract (PROJ-34) which
validated that the UI-supplied `cmd.empire_id` matched the fleet's owner
— a tautology after the UI was found to set
`empire_id=fleet.owner_id`. The DTO field has been removed (Q5=DROP);
identity is session context. `_resolve_player_fleet` is the canonical
authorization helper, gating against `session.active_empire.id`.
"""
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.engine.command_handlers import BaseCommandHandler
from game.strategy.engine.commands import (
    IssueColonizeCommand,
    IssueMoveCommand,
    SplitFleetCommand,
)


def _make_session_with_fleet(fleet_id, owner_id, active_empire_id=None):
    """Create a mock session with one fleet in the galaxy registry.

    `active_empire_id` defaults to the fleet owner so authorization
    succeeds; pass a different value to simulate the rotated hot-seat
    case where the active empire is not the fleet owner.
    """
    if active_empire_id is None:
        active_empire_id = owner_id

    fleet = Fleet(fleet_id=fleet_id, owner_id=owner_id, location=HexCoord(0, 0))
    ship = MagicMock()
    ship.instance_id = "ship_1"
    ship.name = "Test Ship"
    ship.is_combat_capable = MagicMock(return_value=True)
    ship.get_calculated_stats = MagicMock(return_value={'strategic_movement': 5.0})
    fleet.ships.append(ship)

    session = MagicMock()
    session._get_fleet_by_id = MagicMock(return_value=fleet)
    session.active_empire = MagicMock()
    session.active_empire.id = active_empire_id
    return session, fleet


class TestResolvePlayerFleet:
    """BaseCommandHandler._resolve_player_fleet authorizes against the
    active empire."""

    def test_active_empire_owns_fleet_succeeds(self):
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0, active_empire_id=0)
        result_fleet, error = BaseCommandHandler._resolve_player_fleet(session, 1)
        assert result_fleet is fleet
        assert error is None

    def test_active_empire_differs_from_fleet_owner_returns_error(self):
        """Hot-seat: active empire is empire_1, fleet belongs to empire_0
        — authorization must reject."""
        session, _fleet = _make_session_with_fleet(fleet_id=1, owner_id=0, active_empire_id=1)
        result_fleet, error = BaseCommandHandler._resolve_player_fleet(session, 1)
        assert result_fleet is None
        assert error is not None
        assert not error.is_valid

    def test_no_active_empire_returns_error(self):
        """Defensive: missing active_empire is a session-construction
        failure, not a silent allow."""
        session = MagicMock()
        session._get_fleet_by_id = MagicMock()
        session.active_empire = None
        result_fleet, error = BaseCommandHandler._resolve_player_fleet(session, 1)
        assert result_fleet is None
        assert error is not None

    def test_fleet_not_found(self):
        """Nonexistent fleet returns error regardless of authorization."""
        session = MagicMock()
        session._get_fleet_by_id = MagicMock(return_value=None)
        session.active_empire = MagicMock()
        session.active_empire.id = 0
        result_fleet, error = BaseCommandHandler._resolve_player_fleet(session, 999)
        assert result_fleet is None
        assert error is not None


class TestResolveFleetExplicitEmpireId:
    """`_resolve_fleet` still accepts an explicit `empire_id` for
    intercept-target lookup, where cross-empire targets are legitimate."""

    def test_resolve_fleet_no_empire_id_skips_validation(self):
        """`empire_id=None` is the intercept-target path."""
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=None)
        assert result_fleet is fleet
        assert error is None

    def test_resolve_fleet_matching_empire_succeeds(self):
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=0)
        assert result_fleet is fleet
        assert error is None

    def test_resolve_fleet_wrong_empire_returns_error(self):
        session, _fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=1)
        assert result_fleet is None
        assert error is not None
        assert not error.is_valid


class TestCommandHasNoEmpireIdField:
    """BUG-125: `Command.empire_id` removed entirely — identity is session
    context, not request body."""

    def test_move_command_has_no_empire_id_field(self):
        cmd = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(0, 0))
        assert not hasattr(cmd, "empire_id")

    def test_colonize_command_has_no_empire_id_field(self):
        cmd = IssueColonizeCommand(fleet_id=1, planet_id=5)
        assert not hasattr(cmd, "empire_id")

    def test_split_command_has_no_empire_id_field(self):
        cmd = SplitFleetCommand(fleet_id=1, ship_instance_ids=["s1"])
        assert not hasattr(cmd, "empire_id")
