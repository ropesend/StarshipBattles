import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.ui.screens.transfer_dialog import TransferDialog
from game.strategy.facade.dto import FleetInfo, PlanetInfo

class TestTransferDialogEnhanced:
    """Enhanced tests for TransferDialog to support the new requirements."""

    @pytest.fixture
    def mock_manager(self):
        return pygame_gui.UIManager((800, 600))

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene._facade = MagicMock()
        scene.facade = scene._facade
        return scene

    @pytest.fixture
    def mock_fleet(self):
        fleet = MagicMock()
        fleet.id = 1
        return fleet

    def test_transfer_dialog_allows_fleet_to_fleet_selection(self, mock_manager, mock_scene, mock_fleet):
        """Dialog should allow selecting another fleet as target."""
        # Arrange
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f1.location = (0, 0)
        f2 = MagicMock(fleet_id=2, owner_id=0)
        f2.location = (0, 0)
        mock_scene._facade.get_fleets_at_hex.return_value = [f1, f2]
        mock_scene._facade.get_planets_at_hex.return_value = []
        
        # Mock DTOs
        mock_scene._facade.get_fleet.return_value = MagicMock(passengers_current=100)
        
        rect = pygame.Rect(0, 0, 600, 500)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)
        
        # Act
        dialog._on_source_changed("Fleet 1")
        
        # Assert
        target_options = [opt[0] if isinstance(opt, tuple) else opt for opt in dialog.drop_target.options_list]
        assert "Fleet 2" in target_options

    def test_issue_order_fleet_to_fleet(self, mock_manager, mock_scene, mock_fleet):
        """Confirming fleet-to-fleet transfer should dispatch command with target_fleet_id."""
        # Arrange
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 50
        mock_scene._facade.get_fleet.return_value = mock_fleet_info
        
        rect = pygame.Rect(0, 0, 600, 500)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)
        
        # Manually setup valid state for fleet-to-fleet
        dialog.available_sources = [{'label': 'Fleet 1', 'type': 'fleet', 'id': 1}]
        dialog.available_targets = [{'label': 'Fleet 2', 'type': 'fleet', 'id': 2}]
        dialog.available_cargo = [{'label': 'Passengers (50)', 'type': 'passengers', 'species_id': None, 'max': 50}]
        
        dialog.drop_source.selected_option = "Fleet 1"
        dialog.drop_target.selected_option = "Fleet 2"
        dialog.drop_item.selected_option = "Passengers (50)"
        dialog.slider_amount.set_current_value(20)
        
        # Act
        with patch('game.ui.screens.transfer_dialog.IssueTransferCommand') as mock_cmd_class:
            dialog._issue_order()
            
            # Assert
            mock_cmd_class.assert_called_once()
            args, kwargs = mock_cmd_class.call_args
            # We expect fleet_id=1, target_fleet_id=2, direction='unload' (from 1 to 2) 
            # OR fleet_id=1, target_fleet_id=2, direction='unload' might be interpreted differently.
            # In process_transfer: source = fleet if direction == "unload" else target_fleet
            assert kwargs['fleet_id'] == 1
            assert kwargs['target_fleet_id'] == 2
            assert kwargs['direction'] == 'unload'
            assert kwargs['amount'] == 20
