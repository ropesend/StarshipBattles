"""PROJ-475 Phase 1 Task 1.2 — ``facade.session_meta.save_current_game``.

The facade owns the live session; this surface lets the UI trigger a save
without ever holding the ``GameSession`` itself. It calls
``SaveGameService.save_game(session, save_name)`` internally and returns the
``(success, message, save_path)`` triple the service produces.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.strategy.facade.strategy_session_facade import StrategySessionFacade


def _facade() -> tuple[StrategySessionFacade, MagicMock]:
    session = MagicMock()
    session.galaxy.systems = {}
    session.empires = []
    return StrategySessionFacade(session), session


class TestSaveCurrentGame:
    def test_calls_save_game_with_live_session_and_returns_triple(self) -> None:
        facade, session = _facade()
        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.save_game",
            return_value=(True, "Game saved: Turn 1", "/saves/foo"),
        ) as mock_save:
            result = facade.session_meta.save_current_game()

        mock_save.assert_called_once_with(session, None)
        assert result == (True, "Game saved: Turn 1", "/saves/foo")

    def test_passes_save_name_through(self) -> None:
        facade, session = _facade()
        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.save_game",
            return_value=(True, "Game saved", "/saves/bar"),
        ) as mock_save:
            facade.session_meta.save_current_game(save_name="bar")

        mock_save.assert_called_once_with(session, "bar")
