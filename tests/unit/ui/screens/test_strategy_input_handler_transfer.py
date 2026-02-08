import pytest
from unittest.mock import MagicMock, patch
import pygame
from game.ui.screens.strategy_input_handler import StrategyInputHandler

class TestStrategyInputHandlerTransfer:
    """Tests for T key handling in StrategyInputHandler."""

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene.ui = MagicMock()
        scene.ui.manager = MagicMock()
        scene.ui.planet_list_window = None
        scene.selected_fleet = None
        scene.build_queue_screen = None
        return scene

    def test_t_key_triggers_transfer_dialog(self, mock_scene):
        """Pressing 'T' should call open_transfer_dialog if a fleet is selected."""
        # Arrange
        handler = StrategyInputHandler(mock_scene)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        mock_fleet.location = (5, 5)
        
        # Mock the UI method we expect to be called
        mock_scene.ui.open_transfer_dialog = MagicMock()
        
        # Create a 'T' key event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t})
        
        # Act
        handler.handle_event(event)
        
        # Assert
        mock_scene.ui.open_transfer_dialog.assert_called_once_with(mock_fleet, (5, 5))

    def test_t_key_ignored_if_no_fleet_selected(self, mock_scene):
        """Pressing 'T' should do nothing if no fleet is selected."""
        # Arrange
        handler = StrategyInputHandler(mock_scene)
        mock_scene.selected_fleet = None
        mock_scene.ui.open_transfer_dialog = MagicMock()
        
        # Create a 'T' key event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_t})
        
        # Act
        handler.handle_event(event)
        
        # Assert
        mock_scene.ui.open_transfer_dialog.assert_not_called()
