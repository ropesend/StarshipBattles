"""Tests for Transfer / Drop / Load Cargo mode handling in StrategyInputHandler (PROJ-100).

Verifies (parametrized across TRANSFER, DROP_CARGO, LOAD_CARGO modes):
- Mode hotkey sets input mode when a fleet is selected (else no-op)
- Left click in that mode opens the corresponding dialog at the clicked hex
- Right click / ESC cancels back to SELECT mode

PROJ-494 Task 1.2: 3 byte-identical mode-test classes (TRANSFER / DROP_CARGO /
LOAD_CARGO) consolidated into a single parametrized class.
"""
import pytest
from unittest.mock import MagicMock
import pygame
from game.ui.services.input_mapper import InputMapper
from game.ui.screens.strategy_input_handler import StrategyInputHandler


@pytest.fixture
def mock_scene():
    """Create a mock StrategyScreen for handler tests."""
    scene = MagicMock()
    scene.ui = MagicMock()
    scene.ui.manager = MagicMock()
    scene.ui.window_manager = MagicMock()  # PROJ-198: planet_list_window moved here
    scene.ui.window_manager.planet_list_window = None
    scene.selected_fleet = None
    scene.build_queue_screen = None
    scene.camera = MagicMock()
    scene.camera.zoom = 1.0  # PROJ-162: Fix for _resolve_click_target() comparison
    scene._get_system_at_hex = MagicMock(return_value=None)  # PROJ-162: Skip planet hit-testing
    scene.hex_size = 64
    scene._camera_nav = MagicMock()
    return scene


@pytest.fixture
def mapper():
    """Create an InputMapper loaded with defaults."""
    m = InputMapper()
    from game.core.paths import Paths
    m.load(Paths.DEFAULT_KEYBINDINGS_FILE)
    return m


# (mode_name, hotkey, dialog_attr, dialog_args_when_clicked)
# `dialog_args_when_clicked` is a tuple of *additional* args appended after
# (fleet, target_hex). For TRANSFER it's empty; for DROP/LOAD it's ('unload',)
# / ('load',).
_MODE_CASES = [
    pytest.param('TRANSFER', pygame.K_t, 'open_transfer_dialog', (), id='transfer'),
    pytest.param('DROP_CARGO', pygame.K_d, 'open_cargo_quick_dialog', ('unload',), id='drop_cargo'),
    pytest.param('LOAD_CARGO', pygame.K_l, 'open_cargo_quick_dialog', ('load',), id='load_cargo'),
]


class TestStrategyInputHandlerCargoModes:
    """Tests for T / D / L hotkeys and their input modes in StrategyInputHandler.

    Each mode follows the same contract:
    - Hotkey sets the mode (only if a fleet is selected)
    - Left click opens the appropriate dialog at the clicked hex, then returns to SELECT
    - Right click cancels back to SELECT (no dialog opened)
    - ESC cancels back to SELECT
    """

    @pytest.mark.parametrize("mode,hotkey,dialog_attr,dialog_extra_args", _MODE_CASES)
    def test_hotkey_sets_mode(self, mock_scene, mapper, mode, hotkey, dialog_attr, dialog_extra_args):
        """Pressing the mode hotkey should set input_mode when a fleet is selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet

        event = pygame.event.Event(pygame.KEYDOWN, {'key': hotkey, 'mod': 0})
        handler.handle_event(event)

        assert handler.input_mode == mode
        getattr(mock_scene.ui, dialog_attr).assert_not_called()

    @pytest.mark.parametrize("mode,hotkey,dialog_attr,dialog_extra_args", _MODE_CASES)
    def test_hotkey_ignored_without_fleet(self, mock_scene, mapper, mode, hotkey, dialog_attr, dialog_extra_args):
        """Pressing the mode hotkey should do nothing if no fleet is selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None

        event = pygame.event.Event(pygame.KEYDOWN, {'key': hotkey, 'mod': 0})
        handler.handle_event(event)

        assert handler.input_mode == 'SELECT'
        getattr(mock_scene.ui, dialog_attr).assert_not_called()

    @pytest.mark.parametrize("mode,hotkey,dialog_attr,dialog_extra_args", _MODE_CASES)
    def test_left_click_opens_dialog_at_clicked_hex(self, mock_scene, mapper, mode, hotkey, dialog_attr, dialog_extra_args):
        """In each cargo mode, left click opens the corresponding dialog at the clicked hex."""
        from game.core.hex_math import HexCoord

        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        handler.input_mode = mode

        # Mock UI handle_click to not consume the event
        mock_scene.ui.handle_click.return_value = False

        # Mock camera and hex resolution
        mock_scene.camera.screen_to_world.return_value = pygame.math.Vector2(100, 100)

        target_hex = HexCoord(3, 4)
        mock_scene.camera.hex_at_screen = MagicMock(return_value=target_hex)

        # Simulate left click
        result = handler.handle_click(200, 300, 1)

        assert result is True
        getattr(mock_scene.ui, dialog_attr).assert_called_once_with(
            mock_fleet, target_hex, *dialog_extra_args
        )
        assert handler.input_mode == 'SELECT'

    @pytest.mark.parametrize("mode,hotkey,dialog_attr,dialog_extra_args", _MODE_CASES)
    def test_right_click_cancels_to_select(self, mock_scene, mapper, mode, hotkey, dialog_attr, dialog_extra_args):
        """In each cargo mode, right click cancels back to SELECT mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        handler.input_mode = mode

        # Mock UI handle_click to not consume the event
        mock_scene.ui.handle_click.return_value = False

        result = handler.handle_click(200, 300, 3)

        assert result is True
        assert handler.input_mode == 'SELECT'
        getattr(mock_scene.ui, dialog_attr).assert_not_called()

    @pytest.mark.parametrize("mode,hotkey,dialog_attr,dialog_extra_args", _MODE_CASES)
    def test_escape_cancels_mode(self, mock_scene, mapper, mode, hotkey, dialog_attr, dialog_extra_args):
        """Pressing ESC in each cargo mode returns to SELECT mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        handler.input_mode = mode

        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE, 'mod': 0})
        handler.handle_event(event)

        assert handler.input_mode == 'SELECT'
