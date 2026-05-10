"""Tests for StrategySessionFacade fleet query methods."""
import pytest
from unittest.mock import Mock, MagicMock
from game.core.hex_math import HexCoord
from tests.integration.strategy.facade.conftest import create_mock_session_with_fleet_lookup


class TestGetFleet:
    """Tests for get_fleet query."""

    def test_get_fleet_returns_fleet_info_when_found(self):
        """get_fleet returns FleetInfo DTO for existing fleet."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import FleetInfo

        # Create mock fleet
        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.owner_id = 0
        mock_fleet.location = HexCoord(5, 5)
        mock_fleet.speed = 2.0
        mock_fleet.ships = []
        mock_fleet.orders = []
        mock_fleet.path = []
        mock_fleet.capabilities.can_use_warp.return_value = True

        # Create mock empire with fleet
        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        # Create mock session with fleet lookup support
        mock_session = create_mock_session_with_fleet_lookup([mock_empire])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet(101)

        assert result is not None
        assert isinstance(result, FleetInfo)
        assert result.fleet_id == 101
        assert result.owner_id == 0
        assert result.location == HexCoord(5, 5)

    def test_get_fleet_returns_none_when_not_found(self):
        """get_fleet returns None for non-existent fleet ID."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = Mock()
        mock_empire.fleets = []

        mock_session = create_mock_session_with_fleet_lookup([mock_empire])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet(9999)

        assert result is None

    def test_get_fleet_searches_all_empires(self):
        """get_fleet searches fleets across all empires."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import FleetInfo

        # Fleet in second empire
        mock_fleet = MagicMock()
        mock_fleet.id = 202
        mock_fleet.owner_id = 1
        mock_fleet.location = HexCoord(10, 10)
        mock_fleet.speed = 1.5
        mock_fleet.ships = []
        mock_fleet.orders = []
        mock_fleet.path = []
        mock_fleet.capabilities.can_use_warp.return_value = False

        mock_empire1 = Mock()
        mock_empire1.fleets = []

        mock_empire2 = Mock()
        mock_empire2.fleets = [mock_fleet]

        mock_session = create_mock_session_with_fleet_lookup([mock_empire1, mock_empire2])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet(202)

        assert result is not None
        assert result.fleet_id == 202
        assert result.owner_id == 1


class TestGetFleetsAtHex:
    """Tests for get_fleets_at_hex query."""

    def test_get_fleets_at_hex_returns_matching_fleets(self):
        """get_fleets_at_hex returns all fleets at given location."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import FleetInfo

        target_hex = HexCoord(5, 5)

        # Two fleets at same location
        mock_fleet1 = MagicMock()
        mock_fleet1.id = 101
        mock_fleet1.owner_id = 0
        mock_fleet1.location = target_hex
        mock_fleet1.speed = 2.0
        mock_fleet1.ships = []
        mock_fleet1.orders = []
        mock_fleet1.path = []
        mock_fleet1.can_use_warp.return_value = True

        mock_fleet2 = MagicMock()
        mock_fleet2.id = 102
        mock_fleet2.owner_id = 1
        mock_fleet2.location = target_hex
        mock_fleet2.speed = 1.5
        mock_fleet2.ships = []
        mock_fleet2.orders = []
        mock_fleet2.path = []
        mock_fleet2.can_use_warp.return_value = False

        mock_empire1 = Mock()
        mock_empire1.fleets = [mock_fleet1]

        mock_empire2 = Mock()
        mock_empire2.fleets = [mock_fleet2]

        mock_session = Mock()
        mock_session.empires = [mock_empire1, mock_empire2]

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleets_at_hex(target_hex)

        assert len(result) == 2
        assert all(isinstance(f, FleetInfo) for f in result)
        fleet_ids = [f.fleet_id for f in result]
        assert 101 in fleet_ids
        assert 102 in fleet_ids

    def test_get_fleets_at_hex_returns_empty_list_when_none(self):
        """get_fleets_at_hex returns empty list when no fleets at location."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(0, 0)  # Different location

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleets_at_hex(HexCoord(99, 99))

        assert result == []


class TestGetFleetPathPreview:
    """Tests for get_fleet_path_preview query."""

    def test_get_fleet_path_preview_returns_path_for_valid_fleet(self):
        """get_fleet_path_preview returns path when fleet found and path exists."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(0, 0)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        expected_path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]

        mock_session = create_mock_session_with_fleet_lookup(
            [mock_empire], preview_fleet_path=Mock(return_value=expected_path)
        )

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_path_preview(101, HexCoord(3, 0))

        assert result == expected_path
        mock_session.preview_fleet_path.assert_called_once_with(mock_fleet, HexCoord(3, 0))

    def test_get_fleet_path_preview_returns_none_for_invalid_fleet(self):
        """get_fleet_path_preview returns None when fleet not found."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = Mock()
        mock_empire.fleets = []

        mock_session = create_mock_session_with_fleet_lookup([mock_empire])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_path_preview(9999, HexCoord(3, 0))

        assert result is None

    def test_get_fleet_path_preview_returns_none_for_no_path(self):
        """get_fleet_path_preview returns None when no path possible."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(0, 0)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = create_mock_session_with_fleet_lookup(
            [mock_empire], preview_fleet_path=Mock(return_value=None)
        )

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_path_preview(101, HexCoord(100, 100))

        assert result is None


class TestGetFleetPathProjection:
    """Tests for get_fleet_path_projection query."""

    def test_get_fleet_path_projection_returns_projection(self):
        """get_fleet_path_projection returns turn-by-turn projection."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_fleet = MagicMock()
        mock_fleet.id = 101
        mock_fleet.location = HexCoord(0, 0)

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        expected_projection = [
            {"turn": 1, "hex": HexCoord(1, 0), "status": "moving"},
            {"turn": 2, "hex": HexCoord(2, 0), "status": "arrived"},
        ]

        mock_session = create_mock_session_with_fleet_lookup(
            [mock_empire], get_fleet_path_projection=Mock(return_value=expected_projection)
        )

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_path_projection(101, max_turns=10)

        assert result == expected_projection
        mock_session.get_fleet_path_projection.assert_called_once_with(mock_fleet, 10)

    def test_get_fleet_path_projection_returns_empty_for_invalid_fleet(self):
        """get_fleet_path_projection returns empty list for invalid fleet."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = Mock()
        mock_empire.fleets = []

        mock_session = create_mock_session_with_fleet_lookup([mock_empire])

        facade = StrategySessionFacade(mock_session)
        result = facade.get_fleet_path_projection(9999)

        assert result == []


class TestGetEmpireFleets:
    """Tests for get_empire_fleets query."""

    def test_get_empire_fleets_returns_fleet_summaries(self):
        """get_empire_fleets returns FleetSummary DTOs for empire's fleets."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import FleetSummary

        mock_fleet1 = MagicMock()
        mock_fleet1.id = 101
        mock_fleet1.ships = [Mock(), Mock()]  # 2 ships
        mock_fleet1.orders = []

        mock_fleet2 = MagicMock()
        mock_fleet2.id = 102
        mock_fleet2.ships = [Mock()]  # 1 ship
        mock_fleet2.orders = [Mock()]  # has orders

        mock_empire = Mock()
        mock_empire.id = 0
        mock_empire.fleets = [mock_fleet1, mock_fleet2]

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.get_empire_fleets(0)

        assert len(result) == 2
        assert all(isinstance(f, FleetSummary) for f in result)

        # Check first fleet
        fleet1 = next(f for f in result if f.fleet_id == 101)
        assert fleet1.ship_count == 2
        assert fleet1.has_orders is False

        # Check second fleet
        fleet2 = next(f for f in result if f.fleet_id == 102)
        assert fleet2.ship_count == 1
        assert fleet2.has_orders is True

    def test_get_empire_fleets_returns_empty_for_invalid_empire(self):
        """get_empire_fleets returns empty list for non-existent empire."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = Mock()
        mock_empire.id = 0
        mock_empire.fleets = []

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.get_empire_fleets(9999)

        assert result == []
