# -*- coding: utf-8 -*-
"""Tests for command ownership validation.

Part 3 of fleet ID collision fix: commands must carry empire_id and
handlers must validate that the commanding empire owns the fleet.
"""
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.engine.command_handlers import BaseCommandHandler
from game.strategy.engine.commands import (
    IssueMoveCommand,
    IssueColonizeCommand,
    SplitFleetCommand,
)


def _make_session_with_fleet(fleet_id, owner_id):
    """Create a mock session with one fleet in the galaxy registry."""
    fleet = Fleet(fleet_id=fleet_id, owner_id=owner_id, location=HexCoord(0, 0))
    ship = MagicMock()
    ship.instance_id = "ship_1"
    ship.name = "Test Ship"
    ship.is_combat_capable = MagicMock(return_value=True)
    ship.get_calculated_stats = MagicMock(return_value={'strategic_movement': 5.0})
    fleet.ships.append(ship)

    session = MagicMock()
    session._get_fleet_by_id = MagicMock(return_value=fleet)
    return session, fleet


class TestResolveFleetOwnership:
    """BaseCommandHandler._resolve_fleet ownership validation."""

    def test_resolve_fleet_matching_empire_succeeds(self):
        """_resolve_fleet with correct empire_id should return the fleet."""
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=0)
        assert result_fleet is fleet
        assert error is None

    def test_resolve_fleet_wrong_empire_returns_error(self):
        """_resolve_fleet with wrong empire_id should return an error."""
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=1)
        assert result_fleet is None
        assert error is not None
        assert not error.is_valid

    def test_resolve_fleet_no_empire_id_skips_validation(self):
        """_resolve_fleet without empire_id should skip ownership check."""
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=None)
        assert result_fleet is fleet
        assert error is None

    def test_resolve_fleet_negative_one_skips_validation(self):
        """_resolve_fleet with empire_id=-1 should skip validation (backward compat)."""
        session, fleet = _make_session_with_fleet(fleet_id=1, owner_id=0)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 1, empire_id=-1)
        assert result_fleet is fleet
        assert error is None

    def test_resolve_fleet_not_found(self):
        """_resolve_fleet for nonexistent fleet returns error regardless of empire_id."""
        session = MagicMock()
        session._get_fleet_by_id = MagicMock(return_value=None)
        result_fleet, error = BaseCommandHandler._resolve_fleet(session, 999, empire_id=0)
        assert result_fleet is None
        assert error is not None


class TestCommandEmpireIdField:
    """Command base class should carry empire_id."""

    def test_command_has_empire_id_field(self):
        """All commands should have an empire_id field."""
        cmd = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(0, 0))
        assert hasattr(cmd, 'empire_id')

    def test_command_empire_id_defaults_to_negative_one(self):
        """empire_id should default to -1 (skip validation) for backward compat."""
        cmd = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(0, 0))
        assert cmd.empire_id == -1

    def test_command_empire_id_can_be_set(self):
        """empire_id should be settable at construction."""
        cmd = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(0, 0), empire_id=2)
        assert cmd.empire_id == 2

    def test_colonize_command_has_empire_id(self):
        """IssueColonizeCommand should inherit empire_id from Command."""
        cmd = IssueColonizeCommand(fleet_id=1, planet_id=5, empire_id=0)
        assert cmd.empire_id == 0

    def test_split_command_has_empire_id(self):
        """SplitFleetCommand should inherit empire_id from Command."""
        cmd = SplitFleetCommand(fleet_id=1, ship_instance_ids=["s1"], empire_id=3)
        assert cmd.empire_id == 3
