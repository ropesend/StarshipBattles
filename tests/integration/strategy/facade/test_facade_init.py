"""Tests for StrategySessionFacade initialization and basic structure."""
import pytest
from unittest.mock import Mock, MagicMock
from game.strategy.data.hex_math import HexCoord


class TestFacadeInitialization:
    """Tests for StrategySessionFacade initialization."""

    def test_facade_accepts_game_session(self):
        """Facade can be initialized with a GameSession."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        facade = StrategySessionFacade(mock_session)

        assert facade._session is mock_session

    def test_facade_requires_session(self):
        """Facade requires a session parameter."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        with pytest.raises(TypeError):
            StrategySessionFacade()


class TestCommandDelegation:
    """Tests for command handling delegation."""

    def test_handle_command_delegates_to_session(self):
        """handle_command delegates to session.handle_command."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.core.validation import ValidationResult

        mock_session = Mock()
        mock_result = ValidationResult(is_valid=True)
        mock_session.handle_command.return_value = mock_result

        facade = StrategySessionFacade(mock_session)
        mock_command = Mock()

        result = facade.handle_command(mock_command)

        mock_session.handle_command.assert_called_once_with(mock_command)
        assert result is mock_result

    def test_process_turn_delegates_to_session(self):
        """process_turn delegates to session turn processing."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_session = Mock()
        mock_session.process_turn = Mock()

        facade = StrategySessionFacade(mock_session)
        facade.process_turn()

        mock_session.process_turn.assert_called_once()


# Note: TestQueryStubs class was removed as all query methods have been
# implemented. The stub tests are replaced by actual functional tests in:
# - test_fleet_queries.py
# - test_system_queries.py
# - test_empire_queries.py
# - test_validation_queries.py
