"""Tests for StrategySessionFacade validation query methods."""
import pytest
from unittest.mock import Mock, MagicMock
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult, validation_result


class TestCanColonize:
    """Tests for can_colonize validation query."""

    def test_can_colonize_returns_valid_when_possible(self):
        """can_colonize returns valid ValidationResult when colonization is possible."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(5, 5)

        mock_planet = MagicMock()
        mock_planet.id = 42
        mock_planet.owner_id = None

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_system = MagicMock()
        mock_system.planets = [mock_planet]

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {HexCoord(5, 5): mock_system}

        mock_turn_engine = Mock()
        mock_turn_engine.validate_colonize_order.return_value = validation_result(
            True, "Planet is valid for colonization."
        )

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.galaxy = mock_galaxy
        mock_session.turn_engine = mock_turn_engine

        facade = StrategySessionFacade(mock_session)
        result = facade.can_colonize(101, 42)

        assert result.is_valid is True
        mock_turn_engine.validate_colonize_order.assert_called_once()

    def test_can_colonize_returns_invalid_when_not_possible(self):
        """can_colonize returns invalid ValidationResult when colonization fails."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(5, 5)

        mock_planet = MagicMock()
        mock_planet.id = 42
        mock_planet.owner_id = 1  # Already owned

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_system = MagicMock()
        mock_system.planets = [mock_planet]

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {HexCoord(5, 5): mock_system}

        mock_turn_engine = Mock()
        mock_turn_engine.validate_colonize_order.return_value = validation_result(
            False, "Planet already owned.", "ALREADY_OWNED"
        )

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.galaxy = mock_galaxy
        mock_session.turn_engine = mock_turn_engine

        facade = StrategySessionFacade(mock_session)
        result = facade.can_colonize(101, 42)

        assert result.is_valid is False

    def test_can_colonize_returns_invalid_for_missing_fleet(self):
        """can_colonize returns invalid when fleet not found."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = Mock()
        mock_empire.fleets = []

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.can_colonize(9999, 42)

        assert result.is_valid is False
        assert "Fleet not found" in result.message

    def test_can_colonize_with_none_planet_checks_location(self):
        """can_colonize with planet_id=None validates against current location."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(5, 5)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        mock_turn_engine = Mock()
        mock_turn_engine.validate_colonize_order.return_value = validation_result(
            True, "Colonization valid."
        )

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.galaxy = mock_galaxy
        mock_session.turn_engine = mock_turn_engine

        facade = StrategySessionFacade(mock_session)
        result = facade.can_colonize(101, None)

        # Should be called with fleet and None for planet
        mock_turn_engine.validate_colonize_order.assert_called_once()
        call_args = mock_turn_engine.validate_colonize_order.call_args
        assert call_args[0][1] == mock_fleet  # fleet argument
        assert call_args[0][2] is None  # planet argument


class TestCanMoveTo:
    """Tests for can_move_to validation query."""

    def test_can_move_to_returns_valid_when_path_exists(self):
        """can_move_to returns valid when path to target exists."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(0, 0)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.preview_fleet_path.return_value = [HexCoord(1, 0), HexCoord(2, 0)]

        facade = StrategySessionFacade(mock_session)
        result = facade.can_move_to(101, HexCoord(2, 0))

        assert result.is_valid is True

    def test_can_move_to_returns_invalid_when_no_path(self):
        """can_move_to returns invalid when no path to target."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(0, 0)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.preview_fleet_path.return_value = None  # No path

        facade = StrategySessionFacade(mock_session)
        result = facade.can_move_to(101, HexCoord(100, 100))

        assert result.is_valid is False
        assert "path" in result.message.lower() or "unreachable" in result.message.lower()

    def test_can_move_to_returns_invalid_for_missing_fleet(self):
        """can_move_to returns invalid when fleet not found."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = Mock()
        mock_empire.fleets = []

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.can_move_to(9999, HexCoord(5, 5))

        assert result.is_valid is False
        assert "Fleet not found" in result.message

    def test_can_move_to_returns_valid_for_empty_path(self):
        """can_move_to returns valid when path is empty (already at target)."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(5, 5)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = Mock()
        mock_session.empires = [mock_empire]
        mock_session.preview_fleet_path.return_value = []  # Already there

        facade = StrategySessionFacade(mock_session)
        result = facade.can_move_to(101, HexCoord(5, 5))

        assert result.is_valid is True
