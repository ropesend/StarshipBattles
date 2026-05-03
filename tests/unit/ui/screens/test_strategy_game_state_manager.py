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
    mock_screen.active_empire = empire0

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


class TestProcessFullTurnLegacy:
    """Test process_full_turn() method (formerly _process_full_turn, FEAT-20 made public)."""

    def test_sets_turn_processing_flag(self):
        """process_full_turn() should set turn_processing during processing."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        # Track the flag value during processing
        processing_values = []

        def track_processing(*args, **kwargs):
            processing_values.append(screen.turn_processing)

        screen._facade.process_turn.side_effect = track_processing

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        # Flag should have been True during process_turn
        assert True in processing_values
        # Flag should be False after completion
        assert screen.turn_processing is False

    def test_calls_facade_process_turn(self):
        """process_full_turn() should call facade.process_turn()."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen._facade.process_turn.assert_called_once()

    def test_checks_turn_events(self):
        """process_full_turn() should check for turn events."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen._facade.get_turn_events.assert_called()

    def test_opens_event_log_when_events_exist(self):
        """process_full_turn() should open event log if there are events.

        BUG-123: empire_name is forwarded as a keyword arg sourced from
        ``current_empire.name`` so the window title shows the active
        empire.
        """
        manager, screen = _make_game_state_manager()
        mock_events = [MagicMock()]
        screen._facade.get_turn_events.return_value = mock_events

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen.ui.open_event_log_with_events.assert_called_once_with(
            mock_events, empire_name=screen.current_empire.name
        )

    def test_auto_saves_when_save_path_exists(self):
        """process_full_turn() should auto-save when session has save_path."""
        manager, screen = _make_game_state_manager()
        screen.session.save_path = "/test/save.json"
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None), \
             patch('game.strategy.systems.save_game_service.SaveGameService') as MockSGS:
            MockSGS.save_game.return_value = (True, "Saved", "/test/save.json")
            manager.process_full_turn()

        MockSGS.save_game.assert_called_once_with(screen.session)

    def test_refreshes_selected_object(self):
        """process_full_turn() should refresh UI for selected object."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen.selected_object = MagicMock()

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen.on_ui_selection.assert_called_once_with(screen.selected_object)


class TestProcessFullTurnEmpireFilter:
    """BUG-123: per-empire scoping of the per-turn auto-popup."""

    def test_passes_active_empire_id_to_get_turn_events(self):
        """process_full_turn must scope facade.get_turn_events to current_empire."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen._facade.get_turn_number.return_value = 7

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen._facade.get_turn_events.assert_called_once_with(
            turn=7, empire_id=screen.current_empire.id
        )

    def test_does_not_open_popup_when_active_empire_has_no_events(self):
        """Empty turn_events suppresses the popup even if other empires had events.

        Per-empire filtering happens at the facade call, so the manager
        only sees the active empire's slice. Empty list -> no popup.
        """
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen.ui.open_event_log_with_events.assert_not_called()


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


# ===========================================================================
# FEAT-20: process_full_turn (renamed public) + run_n_turns
# ===========================================================================

class TestProcessFullTurnPublic:
    """`_process_full_turn` is renamed to public `process_full_turn` (FEAT-20)."""

    def test_public_alias_exists(self):
        """A public `process_full_turn` method must exist."""
        manager, _screen = _make_game_state_manager()
        assert callable(getattr(manager, "process_full_turn", None))


class TestRunNTurns:
    """FEAT-20: dev-mode `run_n_turns(n)` runs the full turn n times with cancel support."""

    def test_calls_process_full_turn_n_times(self):
        """Calling run_n_turns(5) invokes process_full_turn 5 times."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen.dev_run_cancel_requested = False

        with patch.object(manager, "process_full_turn") as mock_pft, \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(5)

        assert mock_pft.call_count == 5
        assert completed == 5

    def test_stops_on_cancel_after_current_turn(self):
        """If cancel is requested between iterations, the loop stops cleanly.

        PROJ-323 Task 5.1: use itertools.count Counter for tick-tracking
        side_effect, assert on outcome (completed) rather than internal
        mock call counts.
        """
        from itertools import count
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen.dev_run_cancel_requested = False

        # Set the cancel flag after the second process_full_turn call so the
        # loop should stop before iteration 3.
        counter = count(1)

        def trip_cancel_after_two(*args, **kwargs):
            if next(counter) == 2:
                screen.dev_run_cancel_requested = True

        with patch.object(manager, "process_full_turn", side_effect=trip_cancel_after_two), \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(10)

        # Outcome assertion: 2 turns completed before cancel halted the loop.
        assert completed == 2

    def test_returns_completed_count(self):
        """run_n_turns returns the number of turns actually completed."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen.dev_run_cancel_requested = False

        with patch.object(manager, "process_full_turn"), \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(3)

        assert completed == 3

    def test_resets_cancel_flag_at_start(self):
        """A stale `dev_run_cancel_requested` flag should be cleared on entry."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        # Pre-set: simulate a leftover flag from a prior aborted run.
        screen.dev_run_cancel_requested = True

        with patch.object(manager, "process_full_turn") as mock_pft, \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(2)

        assert mock_pft.call_count == 2
        assert completed == 2

    def test_suppresses_event_log_during_loop_and_surfaces_combined_at_end(self):
        """Per-turn event log auto-open is suppressed during the loop;
        a combined log opens once at the end with all events."""
        manager, screen = _make_game_state_manager()
        # Each call returns a different list of events.
        e1 = [MagicMock(name="evt1")]
        e2 = [MagicMock(name="evt2"), MagicMock(name="evt3")]
        e3 = []
        screen._facade.get_turn_events.side_effect = [e1, e2, e3]
        screen.dev_run_cancel_requested = False
        # Reset the open-event-log mock since process_full_turn will be REAL here.
        screen.ui.open_event_log_with_events.reset_mock()

        with patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            manager.run_n_turns(3)

        # During the loop, open_event_log_with_events must NOT be called per-turn —
        # only once at the end with the combined event list (e1 + e2).
        # (Empty per-turn lists contribute nothing.)
        assert screen.ui.open_event_log_with_events.call_count == 1
        combined_events = screen.ui.open_event_log_with_events.call_args[0][0]
        assert len(combined_events) == 3  # 1 + 2 + 0
        assert combined_events[0] is e1[0]
        assert combined_events[1] is e2[0]
        assert combined_events[2] is e2[1]

    def test_no_combined_log_when_no_events(self):
        """If no turn produced events, no event log opens at the end."""
        manager, screen = _make_game_state_manager()
        screen._facade.get_turn_events.return_value = []
        screen.dev_run_cancel_requested = False
        screen.ui.open_event_log_with_events.reset_mock()

        with patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            manager.run_n_turns(2)

        screen.ui.open_event_log_with_events.assert_not_called()
