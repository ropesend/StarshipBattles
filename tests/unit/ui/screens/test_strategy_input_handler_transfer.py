"""Tests for Transfer mode handling in StrategyInputHandler (PROJ-100).

Verifies:
- T key sets TRANSFER input mode (not immediate dialog open)
- Left click in TRANSFER mode opens dialog at clicked hex
- Right click / ESC cancels TRANSFER mode
"""
import pytest
from unittest.mock import MagicMock, patch
import pygame
from game.ui.screens.strategy_input_handler import StrategyInputHandler


class TestStrategyInputHandlerTransfer:
    """Tests for T key and TRANSFER mode in StrategyInputHandler."""

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene.ui = MagicMock()
        scene.ui.manager = MagicMock()
        scene.ui.planet_list_window = None
        scene.selected_fleet = None
        scene.build_queue_screen = None
        scene.camera = MagicMock()
        scene.hex_size = 64
        return scene

    def test_t_key_sets_transfer_mode(self, mock_scene):
        """Pressing 'T' should set input_mode to TRANSFER if a fleet is selected."""
        handler = StrategyInputHandler(mock_scene)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet

        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t})
        handler.handle_event(event)

        assert handler.input_mode == 'TRANSFER'
        mock_scene.ui.open_transfer_dialog.assert_not_called()

    def test_t_key_ignored_if_no_fleet_selected(self, mock_scene):
        """Pressing 'T' should do nothing if no fleet is selected."""
        handler = StrategyInputHandler(mock_scene)
        mock_scene.selected_fleet = None

        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t})
        handler.handle_event(event)

        assert handler.input_mode == 'SELECT'
        mock_scene.ui.open_transfer_dialog.assert_not_called()

    def test_transfer_mode_left_click_opens_dialog_at_clicked_hex(self, mock_scene):
        """In TRANSFER mode, left click opens transfer dialog at clicked hex."""
        from game.core.hex_math import HexCoord

        handler = StrategyInputHandler(mock_scene)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        handler.input_mode = 'TRANSFER'

        # Mock UI handle_click to not consume the event
        mock_scene.ui.handle_click.return_value = False

        # Mock camera and hex resolution
        mock_scene.camera.screen_to_world.return_value = pygame.math.Vector2(100, 100)

        with patch('game.ui.screens.strategy_input_handler.pixel_to_hex') as mock_pixel_to_hex:
            target_hex = HexCoord(3, 4)
            mock_pixel_to_hex.return_value = target_hex

            # Simulate left click
            result = handler.handle_click(200, 300, 1)

            assert result is True
            mock_scene.ui.open_transfer_dialog.assert_called_once_with(mock_fleet, target_hex)
            assert handler.input_mode == 'SELECT'

    def test_transfer_mode_right_click_cancels_to_select(self, mock_scene):
        """In TRANSFER mode, right click cancels back to SELECT mode."""
        handler = StrategyInputHandler(mock_scene)
        mock_scene.selected_fleet = MagicMock()
        handler.input_mode = 'TRANSFER'

        # Mock UI handle_click to not consume the event
        mock_scene.ui.handle_click.return_value = False

        result = handler.handle_click(200, 300, 3)

        assert result is True
        assert handler.input_mode == 'SELECT'
        mock_scene.ui.open_transfer_dialog.assert_not_called()

    def test_escape_cancels_transfer_mode(self, mock_scene):
        """Pressing ESC in TRANSFER mode returns to SELECT mode."""
        handler = StrategyInputHandler(mock_scene)
        mock_scene.selected_fleet = MagicMock()
        handler.input_mode = 'TRANSFER'

        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        handler.handle_event(event)

        assert handler.input_mode == 'SELECT'
