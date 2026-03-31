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

    def test_confirm_fleet_to_fleet_dispatches_with_target_fleet_id(self, mock_manager, mock_scene, mock_fleet):
        """Confirming fleet-to-fleet transfer should dispatch command with target_fleet_id."""
        # Arrange
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f2 = MagicMock(fleet_id=2, owner_id=0)
        mock_scene._facade.get_fleets_at_hex.return_value = [f1, f2]
        mock_scene._facade.get_planets_at_hex.return_value = []

        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 50
        mock_fleet_info.cargo_resources = ()
        mock_fleet_info.cargo_capacities = ()
        mock_scene._facade.get_fleet.return_value = mock_fleet_info
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)

        rect = pygame.Rect(0, 0, 900, 700)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)

        # Set up: source=Fleet 1, target=Fleet 2, pending drop of 20 passengers
        dialog._current_source = {'type': 'fleet', 'id': 1, 'label': 'Fleet 1'}
        dialog._current_target = {'type': 'fleet', 'id': 2, 'label': 'Fleet 2'}
        dialog.pending_transfers = {"passengers": -20}  # Drop 20 passengers

        # Act
        dialog._on_confirm()

        # Assert
        mock_scene._facade.handle_command.assert_called_once()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.fleet_id == 1
        assert cmd.target_fleet_id == 2
        assert cmd.direction == 'unload'
        assert cmd.amount == 20
