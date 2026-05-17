"""Tests for StrategySessionFacade empire query methods."""
import pytest
from unittest.mock import Mock, MagicMock
from game.core.hex_math import HexCoord


class TestGetAllEmpires:
    """Tests for get_all_empires query."""

    def test_get_all_empires_returns_empire_infos(self):
        """get_all_empires returns list of EmpireInfo DTOs."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import EmpireInfo

        mock_empire1 = MagicMock()
        mock_empire1.id = 0
        mock_empire1.name = "Human Empire"
        mock_empire1.color = (0, 128, 255)
        mock_empire1.empire_theme_id = "terran"
        mock_empire1.flag_id = "flag_1"
        mock_empire1.colonies = []
        mock_empire1.fleets = []

        mock_empire2 = MagicMock()
        mock_empire2.id = 1
        mock_empire2.name = "AI Empire"
        mock_empire2.color = (255, 0, 0)
        mock_empire2.empire_theme_id = "alien"
        mock_empire2.flag_id = "flag_2"
        mock_empire2.colonies = [Mock()]
        mock_empire2.fleets = [Mock()]

        mock_session = Mock()
        mock_session.empires = [mock_empire1, mock_empire2]

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.all()

        assert len(result) == 2
        assert all(isinstance(e, EmpireInfo) for e in result)
        names = [e.name for e in result]
        assert "Human Empire" in names
        assert "AI Empire" in names

    def test_get_all_empires_returns_empty_for_no_empires(self):
        """get_all_empires returns empty list when no empires exist."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.empires = []

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.all()

        assert result == []


class TestGetEmpire:
    """Tests for get_empire query."""

    def test_get_empire_returns_empire_info_when_found(self):
        """get_empire returns EmpireInfo DTO for existing empire."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import EmpireInfo

        mock_empire = MagicMock()
        mock_empire.id = 0
        mock_empire.name = "Test Empire"
        mock_empire.color = (100, 100, 100)
        mock_empire.empire_theme_id = "test"
        mock_empire.flag_id = "test_flag"
        mock_empire.colonies = [Mock(), Mock()]
        mock_empire.fleets = [Mock()]

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.get(0)

        assert result is not None
        assert isinstance(result, EmpireInfo)
        assert result.empire_id == 0
        assert result.name == "Test Empire"
        assert result.colony_count == 2
        assert result.fleet_count == 1

    def test_get_empire_returns_none_when_not_found(self):
        """get_empire returns None for non-existent empire ID."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.empires = []

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.get(9999)

        assert result is None


class TestGetEmpireColonies:
    """Tests for get_empire_colonies query."""

    def test_get_empire_colonies_returns_colony_summaries(self):
        """get_empire_colonies returns ColonySummary DTOs for empire's colonies."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import ColonySummary

        mock_planet1 = MagicMock()
        mock_planet1.id = 1
        mock_planet1.name = "Earth"
        mock_planet1.has_space_shipyard = True

        mock_planet2 = MagicMock()
        mock_planet2.id = 2
        mock_planet2.name = "Mars"
        mock_planet2.has_space_shipyard = False

        mock_empire = MagicMock()
        mock_empire.id = 0
        mock_empire.colonies = [mock_planet1, mock_planet2]

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.colonies(0)

        assert len(result) == 2
        assert all(isinstance(c, ColonySummary) for c in result)

        # Check first colony
        earth = next(c for c in result if c.planet_name == "Earth")
        assert earth.planet_id == 1
        assert earth.has_shipyard is True

        # Check second colony
        mars = next(c for c in result if c.planet_name == "Mars")
        assert mars.planet_id == 2
        assert mars.has_shipyard is False

    def test_get_empire_colonies_returns_empty_for_invalid_empire(self):
        """get_empire_colonies returns empty list for non-existent empire."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.empires = []

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.colonies(9999)

        assert result == []

    def test_get_empire_colonies_returns_empty_for_no_colonies(self):
        """get_empire_colonies returns empty list for empire with no colonies."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_empire = MagicMock()
        mock_empire.id = 0
        mock_empire.colonies = []

        mock_session = Mock()
        mock_session.empires = [mock_empire]

        facade = StrategySessionFacade(mock_session)
        result = facade.empires.colonies(0)

        assert result == []


class TestGetHumanPlayerIds:
    """Tests for get_human_player_ids query."""

    def test_get_human_player_ids_returns_ids(self):
        """get_human_player_ids returns list of human player empire IDs."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.human_player_ids = [0, 2]

        facade = StrategySessionFacade(mock_session)
        result = facade.session_meta.human_player_ids()

        assert result == [0, 2]
        # Ensure it's a new list (defensive copy)
        assert result is not mock_session.human_player_ids

    def test_get_human_player_ids_returns_empty_for_all_ai(self):
        """get_human_player_ids returns empty list when all AI players."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.human_player_ids = []

        facade = StrategySessionFacade(mock_session)
        result = facade.session_meta.human_player_ids()

        assert result == []


class TestGetTurnNumber:
    """Tests for get_turn_number query."""

    def test_get_turn_number_returns_current_turn(self):
        """get_turn_number returns the current turn number."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.turn_number = 5

        facade = StrategySessionFacade(mock_session)
        result = facade.session_meta.turn_number()

        assert result == 5

    def test_get_turn_number_returns_one_at_start(self):
        """get_turn_number returns 1 at game start."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.turn_number = 1

        facade = StrategySessionFacade(mock_session)
        result = facade.session_meta.turn_number()

        assert result == 1
