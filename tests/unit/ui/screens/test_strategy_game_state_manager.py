"""Tests for StrategyGameStateManager (PROJ-173 Phase 4).

Tests the extracted turn processing and game state management functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


def _make_game_state_manager():
    """Create a StrategyGameStateManager with mocked screen dependency."""
    from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager

    # Create mock screen
    mock_screen = MagicMock()
    mock_screen.session = MagicMock()
    mock_screen._facade = MagicMock()
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.ui.width = 1920
    mock_screen.ui.height = 1080
    mock_screen.turn_processing = False
    mock_screen.current_player_index = 0
    mock_screen.selected_object = None

    # Setup empire mocking
    empire0 = MagicMock()
    empire0.id = 0
    empire0.colonies = [MagicMock()]
    empire1 = MagicMock()
    empire1.id = 1
    empire1.colonies = [MagicMock()]
    mock_screen.empires = [empire0, empire1]
    mock_screen.session.empires = [empire0, empire1]
    mock_screen.session.human_player_ids = [0, 1]
    mock_screen.human_player_ids = [0, 1]
    mock_screen.player_empire = empire0

    # Property mock for current_empire
    type(mock_screen).current_empire = property(lambda s: empire0)

    # Setup draw method for rendering
    mock_screen.draw = MagicMock()
    mock_screen.center_camera_on = MagicMock()
    mock_screen.on_ui_selection = MagicMock()

    manager = StrategyGameStateManager(mock_screen)

    return manager, mock_screen


class TestGameStateManagerInit:
    """Test StrategyGameStateManager initialization."""

    def test_init_stores_screen_reference(self):
        """Manager should store reference to parent screen."""
        manager, screen = _make_game_state_manager()
        assert manager._screen is screen


class TestAdvanceTurn:
    """Test advance_turn() method."""

    def test_increments_player_index(self):
        """advance_turn() should increment current_player_index."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        manager.advance_turn()

        assert screen.current_player_index == 1

    def test_wraps_and_processes_when_all_ready(self):
        """advance_turn() should wrap and process turn when all players ready."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0]
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.advance_turn()

        assert screen.current_player_index == 0
        screen._facade.process_turn.assert_called_once()

    def test_updates_player_label(self):
        """advance_turn() should update player label."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        manager.advance_turn()

        screen.ui.lbl_current_player.set_text.assert_called()

    def test_centers_camera_on_next_player_home(self):
        """advance_turn() should center camera on next player's home colony."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        manager.advance_turn()

        screen.center_camera_on.assert_called_once()


class TestProcessFullTurn:
    """Test _process_full_turn() method."""

    def test_sets_turn_processing_flag(self):
        """_process_full_turn() should set turn_processing during processing."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        # Track the flag value during processing
        processing_values = []

        def track_processing(*args, **kwargs):
            processing_values.append(screen.turn_processing)

        screen._facade.process_turn.side_effect = track_processing

        with patch('pygame.display.get_surface', return_value=None):
            manager._process_full_turn()

        # Flag should have been True during process_turn
        assert True in processing_values
        # Flag should be False after completion
        assert screen.turn_processing is False

    def test_calls_facade_process_turn(self):
        """_process_full_turn() should call facade.process_turn()."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager._process_full_turn()

        screen._facade.process_turn.assert_called_once()

    def test_checks_turn_events(self):
        """_process_full_turn() should check for turn events."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager._process_full_turn()

        screen._facade.get_turn_events.assert_called()

    def test_opens_event_log_when_events_exist(self):
        """_process_full_turn() should open event log if there are events."""
        manager, screen = _make_game_state_manager()
        mock_events = [MagicMock()]
        screen._facade.get_turn_events.return_value = mock_events

        with patch('pygame.display.get_surface', return_value=None):
            manager._process_full_turn()

        screen.ui.open_event_log_with_events.assert_called_once_with(mock_events)

    def test_auto_saves_when_save_path_exists(self):
        """_process_full_turn() should auto-save when session has save_path."""
        manager, screen = _make_game_state_manager()
        screen.session.save_path = "/test/save.json"
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None), \
             patch('game.strategy.systems.save_game_service.SaveGameService') as MockSGS:
            MockSGS.save_game.return_value = (True, "Saved", "/test/save.json")
            manager._process_full_turn()

        MockSGS.save_game.assert_called_once_with(screen.session)

    def test_refreshes_selected_object(self):
        """_process_full_turn() should refresh UI for selected object."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen.selected_object = MagicMock()

        with patch('pygame.display.get_surface', return_value=None):
            manager._process_full_turn()

        screen.on_ui_selection.assert_called_once_with(screen.selected_object)


class TestUpdatePlayerLabel:
    """Test _update_player_label() method."""

    def test_updates_label_text(self):
        """Should update player label with correct player number."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 1

        manager._update_player_label()

        screen.ui.lbl_current_player.set_text.assert_called_with("Player 2's Turn")

    def test_uses_1_indexed_player_number(self):
        """Player number should be 1-indexed."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0

        manager._update_player_label()

        screen.ui.lbl_current_player.set_text.assert_called_with("Player 1's Turn")
