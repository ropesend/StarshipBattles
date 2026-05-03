"""Tests for build_queue_list_window module - UI for showing all build queues."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


@pytest.fixture
def mock_window_base():
    """Fixture to mock UIWindow base class and _build_list."""
    with patch('pygame_gui.elements.UIWindow.__init__', return_value=None):
        with patch('game.ui.screens.build_queue_list_window.BuildQueueListWindow._build_list'):
            yield


class TestBuildQueueListWindowInit:
    """Tests for BuildQueueListWindow initialization."""

    def test_initializes_with_title(self, mock_window_base):
        """Verify window initializes with correct title."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        empire = MagicMock()
        manager = MagicMock()

        with patch('pygame_gui.elements.UIWindow.__init__') as mock_init:
            mock_init.return_value = None
            with patch.object(BuildQueueListWindow, '_build_list'):
                window = BuildQueueListWindow(
                    pygame.Rect(0, 0, 400, 300),
                    manager,
                    empire,
                    window_manager=None,
                )

            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            assert call_kwargs['window_display_title'] == "Build Yards"

    def test_stores_empire_reference(self, mock_window_base):
        """Verify empire reference is stored."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        empire = MagicMock()

        window = BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(),
            empire,
            window_manager=None,
        )

        assert window.empire is empire

    def test_stores_callback(self, mock_window_base):
        """Verify on_close_callback is stored."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        empire = MagicMock()
        callback = MagicMock()

        window = BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(),
            empire,
            window_manager=None,
            on_close_callback=callback
        )

        assert window.on_close_callback is callback

    def test_stores_input_mapper(self, mock_window_base):
        """Verify input_mapper is stored."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        empire = MagicMock()
        mapper = MagicMock()

        window = BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(),
            empire,
            window_manager=None,
            input_mapper=mapper
        )

        assert window._mapper is mapper


@patch('pygame_gui.elements.UIWindow.__init__')
@patch('game.ui.screens.build_queue_list_window.UILabel')
class TestBuildList:
    """Tests for _build_list method.

    PROJ-323 Task 1.28: Per-test `@patch` decorators promoted to class scope —
    every test in this class needs the same UIWindow + UILabel patches.
    """

    def test_shows_colony_queue_items(self, mock_label, mock_init):
        """Verify colony construction queue items are displayed."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        planet = MagicMock()
        planet.name = "Earth"
        planet.construction_queue = [
            {'design_id': 'Frigate', 'turns_remaining': 3, 'type': 'ship'}
        ]

        empire = MagicMock()
        empire.colonies = [planet]
        empire.fleets = []

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                window = BuildQueueListWindow(
                    pygame.Rect(0, 0, 400, 300),
                    MagicMock(),
                    empire,
                    window_manager=None,
                )

        # Check that UILabel was called with text containing planet name and design
        label_texts = [call[1]['text'] for call in mock_label.call_args_list]
        assert any('Earth' in text and 'Frigate' in text for text in label_texts)

    def test_shows_fleet_queue_items(self, mock_label, mock_init):
        """Verify fleet construction queue items are displayed."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        fleet = MagicMock()
        fleet.name = "First Fleet"
        fleet.construction_queue = [
            {'design_id': 'Cruiser', 'turns_remaining': 5, 'type': 'ship'}
        ]

        empire = MagicMock()
        empire.colonies = []
        empire.fleets = [fleet]

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                window = BuildQueueListWindow(
                    pygame.Rect(0, 0, 400, 300),
                    MagicMock(),
                    empire,
                    window_manager=None,
                )

        label_texts = [call[1]['text'] for call in mock_label.call_args_list]
        assert any('First Fleet' in text and 'Cruiser' in text for text in label_texts)

    def test_skips_fleets_without_queue(self, mock_label, mock_init):
        """Verify fleets without construction queues are skipped."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        fleet_with_queue = MagicMock()
        fleet_with_queue.name = "Has Queue"
        fleet_with_queue.construction_queue = [{'design_id': 'Ship', 'turns_remaining': 1}]

        fleet_without = MagicMock()
        fleet_without.name = "No Queue"
        fleet_without.construction_queue = []

        empire = MagicMock()
        empire.colonies = []
        empire.fleets = [fleet_with_queue, fleet_without]

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                window = BuildQueueListWindow(
                    pygame.Rect(0, 0, 400, 300),
                    MagicMock(),
                    empire,
                    window_manager=None,
                )

        label_texts = [call[1]['text'] for call in mock_label.call_args_list]
        assert any('Has Queue' in text for text in label_texts)
        assert not any('No Queue' in text for text in label_texts)

    def test_shows_empty_message(self, mock_label, mock_init):
        """Verify 'No active build queues' shown when empty."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                window = BuildQueueListWindow(
                    pygame.Rect(0, 0, 400, 300),
                    MagicMock(),
                    empire,
                    window_manager=None,
                )

        label_texts = [call[1]['text'] for call in mock_label.call_args_list]
        assert any('No active build queues' in text for text in label_texts)

    def test_handles_missing_fields(self, mock_label, mock_init):
        """Verify missing fields default to '?'."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        planet = MagicMock()
        planet.name = "Mars"
        planet.construction_queue = [{}]  # No design_id, turns_remaining, type

        empire = MagicMock()
        empire.colonies = [planet]
        empire.fleets = []

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                window = BuildQueueListWindow(
                    pygame.Rect(0, 0, 400, 300),
                    MagicMock(),
                    empire,
                    window_manager=None,
                )

        label_texts = [call[1]['text'] for call in mock_label.call_args_list]
        # Should show '?' for missing fields and default 'ship' for type
        assert any('Mars' in text and '?' in text for text in label_texts)


class TestKeyboardHandling:
    """Tests for keyboard event handling."""

    def test_handle_keydown_without_mapper_returns_false(self, mock_window_base):
        """Verify _handle_keydown returns False without mapper."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        empire = MagicMock()

        window = BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(),
            empire,
            window_manager=None,
            input_mapper=None
        )

        event = MagicMock()
        assert window._handle_keydown(event) is False

    def test_close_action_kills_window(self, mock_window_base):
        """Verify BUILD_QUEUE_CLOSE action kills the window."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow
        from game.core.input_actions import InputAction

        empire = MagicMock()

        mapper = MagicMock()
        mapper.resolve.return_value = InputAction.BUILD_QUEUE_CLOSE

        window = BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(),
            empire,
            window_manager=None,
            input_mapper=mapper
        )
        window.row_labels = []

        with patch.object(BuildQueueListWindow, 'kill') as mock_kill:
            event = MagicMock()
            result = window._handle_keydown(event)

        assert result is True
        mock_kill.assert_called_once()

    def test_unhandled_action_returns_false(self, mock_window_base):
        """Verify unhandled actions return False."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow
        from game.core.input_actions import InputAction

        empire = MagicMock()

        mapper = MagicMock()
        mapper.resolve.return_value = InputAction.GLOBAL_EXIT  # Different action

        window = BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(),
            empire,
            window_manager=None,
            input_mapper=mapper
        )

        event = MagicMock()
        result = window._handle_keydown(event)

        assert result is False


class TestKill:
    """Tests for kill method."""

    @patch('pygame_gui.elements.UIWindow.__init__')
    @patch('pygame_gui.elements.UIWindow.kill')
    def test_kills_all_labels(self, mock_super_kill, mock_init):
        """Verify all row labels are killed."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                with patch('game.ui.screens.build_queue_list_window.UILabel') as mock_label:
                    mock_label_instance = MagicMock()
                    mock_label.return_value = mock_label_instance
                    window = BuildQueueListWindow(
                        pygame.Rect(0, 0, 400, 300),
                        MagicMock(),
                        empire,
                        window_manager=None,
                    )

        window.kill()

        mock_label_instance.kill.assert_called()
        assert window.row_labels == []
        mock_super_kill.assert_called_once()

    @patch('pygame_gui.elements.UIWindow.__init__')
    @patch('pygame_gui.elements.UIWindow.kill')
    def test_calls_close_callback(self, mock_super_kill, mock_init):
        """Verify on_close_callback is called on kill."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow

        mock_init.return_value = None
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        callback = MagicMock()

        with patch.object(BuildQueueListWindow, 'get_container') as mock_container:
            mock_container.return_value.get_size.return_value = (400, 300)
            with patch.object(BuildQueueListWindow, 'ui_manager', create=True):
                with patch('game.ui.screens.build_queue_list_window.UILabel'):
                    window = BuildQueueListWindow(
                        pygame.Rect(0, 0, 400, 300),
                        MagicMock(),
                        empire,
                        window_manager=None,
                        on_close_callback=callback
                    )

        window.kill()

        callback.assert_called_once()
