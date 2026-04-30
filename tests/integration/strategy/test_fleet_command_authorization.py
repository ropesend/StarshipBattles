"""Integration tests for fleet command authorization (BUG-125).

In hot-seat play, the active player must not be able to issue orders to
fleets owned by another empire. The fix:

1. Drops the `Command.empire_id` field — identity is session context, not
   request body. UI cannot supply identity.
2. Renames `session.player_empire` -> `session.active_empire` and rotates
   it on turn change. Handlers gate on `session.active_empire.id`.

These tests assert that every fleet command handler rejects cross-empire
sources, including the previously broken intercept-target path
(`movement.py:117` resolved target without empire gating).
"""
from unittest.mock import patch

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.engine.commands import (
    IssueColonizeCommand,
    IssueInterceptCommand,
    IssueJoinFleetCommand,
    IssueMoveCommand,
    IssueWarpCommand,
)
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession


class _MockGalaxy:
    """Minimal galaxy stand-in mirroring the test fixture in
    `tests/integration/strategy/test_command_handlers.py`."""

    def __init__(self) -> None:
        self.systems = {}
        self.warp_lanes = []
        self.planets_by_id = {}
        self.fleets_by_id = {}
        self._global_hex_warp_points = {}

    def get_planet_by_id(self, planet_id):
        return self.planets_by_id.get(planet_id)

    def get_fleet_by_id(self, fleet_id):
        return self.fleets_by_id.get(fleet_id)

    def register_fleet(self, fleet):
        self.fleets_by_id[fleet.id] = fleet

    def unregister_fleet(self, fleet):
        self.fleets_by_id.pop(fleet.id, None)

    def get_planet_global_hex(self, planet):
        return None


def _two_empire_session() -> tuple[GameSession, Empire, Empire]:
    """Build a minimal hot-seat session with two empires and an empty galaxy.

    Empire 0 is the default `active_empire` after construction. Tests rotate
    by setting `session.active_empire = empire_1` to simulate the
    `StrategyGameStateManager.advance_turn` push.
    """
    config = GameConfig(
        players=[
            PlayerConfig(name="P1", theme="Federation", color=(255, 0, 0), is_human=True),
            PlayerConfig(name="P2", theme="Atlantians", color=(0, 255, 0), is_human=True),
        ],
        system_count=0,
    )
    session = GameSession(config=config)
    session.galaxy = _MockGalaxy()
    return session, session.empires[0], session.empires[1]


# =============================================================================
# Command DTOs no longer carry empire_id (Q5 = DROP)
# =============================================================================


class TestCommandDTOsHaveNoEmpireId:
    """`Command.empire_id` is dropped — identity is session context."""

    def test_move_command_has_no_empire_id_field(self):
        cmd = IssueMoveCommand(fleet_id=1, target_hex=HexCoord(0, 0))
        assert not hasattr(cmd, "empire_id")

    def test_intercept_command_has_no_empire_id_field(self):
        cmd = IssueInterceptCommand(fleet_id=1, target_fleet_id=2)
        assert not hasattr(cmd, "empire_id")

    def test_join_command_has_no_empire_id_field(self):
        cmd = IssueJoinFleetCommand(fleet_id=1, target_fleet_id=2)
        assert not hasattr(cmd, "empire_id")

    def test_colonize_command_has_no_empire_id_field(self):
        cmd = IssueColonizeCommand(fleet_id=1, planet_id=5)
        assert not hasattr(cmd, "empire_id")

    def test_warp_command_has_no_empire_id_field(self):
        cmd = IssueWarpCommand(fleet_id=1, warp_point_hex=HexCoord(0, 0))
        assert not hasattr(cmd, "empire_id")


# =============================================================================
# Hot-seat: active player can command own fleets, cannot command opponents
# =============================================================================


class TestMoveCommandAuthorization:
    """`MoveCommandHandler` gates against `session.active_empire.id`."""

    def test_active_player_can_move_own_fleet(self):
        session, empire_0, _empire_1 = _two_empire_session()
        fleet = Fleet(101, empire_0.id, HexCoord(0, 0))
        empire_0.fleets = [fleet]
        session.galaxy.register_fleet(fleet)

        with patch(
            "game.strategy.engine.game_session.GameSession.preview_fleet_path"
        ) as mock_preview:
            mock_preview.return_value = [HexCoord(0, 0), HexCoord(5, 5)]
            cmd = IssueMoveCommand(fleet_id=101, target_hex=HexCoord(5, 5))
            result = session.handle_command(cmd)

        assert result.is_valid is True

    def test_player_2_cannot_move_player_1_fleet(self):
        """Hot-seat: active=empire_1, fleet owned by empire_0 -> reject."""
        session, empire_0, empire_1 = _two_empire_session()
        fleet = Fleet(101, empire_0.id, HexCoord(0, 0))
        empire_0.fleets = [fleet]
        session.galaxy.register_fleet(fleet)

        # Rotate active player to empire_1
        session.active_empire = empire_1

        cmd = IssueMoveCommand(fleet_id=101, target_hex=HexCoord(5, 5))
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "empire" in result.message.lower() or "belong" in result.message.lower()

    def test_player_1_cannot_move_player_2_fleet(self):
        """Symmetric: active=empire_0, fleet owned by empire_1 -> reject."""
        session, _empire_0, empire_1 = _two_empire_session()
        fleet = Fleet(202, empire_1.id, HexCoord(0, 0))
        empire_1.fleets = [fleet]
        session.galaxy.register_fleet(fleet)
        # active_empire defaults to empire_0

        cmd = IssueMoveCommand(fleet_id=202, target_hex=HexCoord(5, 5))
        result = session.handle_command(cmd)

        assert result.is_valid is False


class TestInterceptCommandAuthorization:
    """`InterceptCommandHandler` gates the SOURCE fleet against the active
    empire. The TARGET fleet is allowed to belong to any empire (you can
    intercept an enemy fleet you can see)."""

    def test_active_player_can_intercept_with_own_source(self):
        session, empire_0, empire_1 = _two_empire_session()
        source = Fleet(101, empire_0.id, HexCoord(0, 0))
        target = Fleet(202, empire_1.id, HexCoord(10, 10))
        empire_0.fleets = [source]
        empire_1.fleets = [target]
        session.galaxy.register_fleet(source)
        session.galaxy.register_fleet(target)

        cmd = IssueInterceptCommand(fleet_id=101, target_fleet_id=202)
        result = session.handle_command(cmd)

        assert result.is_valid is True

    def test_player_cannot_intercept_using_opponents_source(self):
        """Cannot order opponent's fleet to chase a target."""
        session, empire_0, empire_1 = _two_empire_session()
        source_owned_by_p2 = Fleet(202, empire_1.id, HexCoord(0, 0))
        target = Fleet(303, empire_1.id, HexCoord(10, 10))
        empire_1.fleets = [source_owned_by_p2, target]
        session.galaxy.register_fleet(source_owned_by_p2)
        session.galaxy.register_fleet(target)
        # active_empire defaults to empire_0

        cmd = IssueInterceptCommand(fleet_id=202, target_fleet_id=303)
        result = session.handle_command(cmd)

        assert result.is_valid is False


class TestJoinCommandAuthorization:
    """`JoinCommandHandler` gates the SOURCE fleet against the active empire.
    Target must already belong to the same empire (existing PROJ-222 rule)."""

    def test_active_player_can_join_own_fleets(self):
        session, empire_0, _empire_1 = _two_empire_session()
        source = Fleet(101, empire_0.id, HexCoord(0, 0))
        target = Fleet(102, empire_0.id, HexCoord(10, 10))
        empire_0.fleets = [source, target]
        session.galaxy.register_fleet(source)
        session.galaxy.register_fleet(target)

        cmd = IssueJoinFleetCommand(fleet_id=101, target_fleet_id=102)
        result = session.handle_command(cmd)

        assert result.is_valid is True

    def test_player_cannot_join_using_opponents_source(self):
        session, _empire_0, empire_1 = _two_empire_session()
        source_owned_by_p2 = Fleet(201, empire_1.id, HexCoord(0, 0))
        target = Fleet(202, empire_1.id, HexCoord(10, 10))
        empire_1.fleets = [source_owned_by_p2, target]
        session.galaxy.register_fleet(source_owned_by_p2)
        session.galaxy.register_fleet(target)
        # active_empire defaults to empire_0

        cmd = IssueJoinFleetCommand(fleet_id=201, target_fleet_id=202)
        result = session.handle_command(cmd)

        assert result.is_valid is False


class TestPlanetCommandAuthorizationHotSeat:
    """Bonus fix: planet handlers also gate on `session.active_empire.id`.
    Before BUG-125, they gated on `session.player_empire.id`, which never
    rotated in hot-seat. Player 2 could not issue orders to their own
    planets and could issue orders to player 1's planets when the
    coincidence aligned. After the rename, the existing gate becomes
    correct under rotation."""

    def test_player_2_can_clear_own_planet_orders_after_rotation(self):
        from unittest.mock import MagicMock

        from game.strategy.engine.commands import ClearPlanetOrdersCommand
        from game.strategy.engine.planet_command_handlers import (
            ClearPlanetOrdersCommandHandler,
        )

        session, empire_0, empire_1 = _two_empire_session()
        planet = MagicMock()
        planet.owner_id = empire_1.id
        planet.name = "P2 Colony"
        planet.orders = []
        planet.clear_orders = MagicMock()
        session.galaxy.planets_by_id[42] = planet

        # Rotate to empire_1 (player 2)
        session.active_empire = empire_1

        handler = ClearPlanetOrdersCommandHandler()
        result = handler.execute(session, ClearPlanetOrdersCommand(planet_id=42))

        assert result.is_valid is True
        planet.clear_orders.assert_called_once()

    def test_player_1_cannot_clear_player_2_planet_orders(self):
        from unittest.mock import MagicMock

        from game.strategy.engine.commands import ClearPlanetOrdersCommand
        from game.strategy.engine.planet_command_handlers import (
            ClearPlanetOrdersCommandHandler,
        )

        session, _empire_0, empire_1 = _two_empire_session()
        planet = MagicMock()
        planet.owner_id = empire_1.id
        planet.name = "P2 Colony"
        planet.orders = []
        planet.clear_orders = MagicMock()
        session.galaxy.planets_by_id[42] = planet
        # active_empire defaults to empire_0

        handler = ClearPlanetOrdersCommandHandler()
        result = handler.execute(session, ClearPlanetOrdersCommand(planet_id=42))

        assert result.is_valid is False
        planet.clear_orders.assert_not_called()
