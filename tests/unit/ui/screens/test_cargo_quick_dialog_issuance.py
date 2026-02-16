import pytest
from unittest.mock import MagicMock, patch
import pygame
from game.ui.screens.cargo_quick_dialog import CargoQuickDialog
from game.strategy.facade.dto.planet_dto import PlanetInfo
from game.strategy.engine.commands import IssueTransferCommand
from game.core.hex_math import HexCoord

class TestCargoQuickDialogIssuance:
    @pytest.fixture
    def mock_manager(self):
        return MagicMock()

    @pytest.fixture
    def mock_fleet(self):
        fleet = MagicMock()
        fleet.id = 123
        fleet.location = HexCoord(10, 10)
        return fleet

    @pytest.fixture
    def mock_scene(self):
        return MagicMock()

    @pytest.fixture
    def mock_facade(self):
        facade = MagicMock()
        # Return a colony
        colony = PlanetInfo(
            planet_id=456,
            name="Test Colony",
            planet_type="TERRESTRIAL",
            location=HexCoord(0,0),
            orbit_distance=3,
            owner_id=0,
            population_details=(('Human', 100, 0.5),),
            total_population=100
        )
        facade.get_planets_at_hex.return_value = [colony]
        facade.get_planet.return_value = colony
        return facade

    def test_confirm_issues_command(self, mock_manager, mock_fleet, mock_facade, mock_scene):
        """Verify that clicking confirm issues an IssueTransferCommand via the facade."""
        with patch('game.ui.screens.cargo_quick_dialog.log_info') as mock_log:
            rect = pygame.Rect(100, 100, 450, 300)
            # Create dialog
            dialog = CargoQuickDialog(
                rect, mock_manager, mock_fleet, (0, 0), 'load', mock_scene
            )
            dialog.facade = mock_facade
            
            # Manually trigger population (simulating initialization)
            dialog._populate_load_items()
            
            assert len(dialog.cargo_items) == 1
            item = dialog.cargo_items[0]
            
            # Set slider value to 50
            item['slider'].set_current_value(50)
            
            # Mock successful command handling
            mock_facade.handle_command.return_value = MagicMock(is_valid=True)
            
            # Act: Issue orders
            dialog._issue_orders()
            
            # Assert: Command was issued correctly
            mock_facade.handle_command.assert_called_once()
            cmd = mock_facade.handle_command.call_args[0][0]
            
            assert isinstance(cmd, IssueTransferCommand)
            assert cmd.fleet_id == mock_fleet.id
            assert cmd.planet_id == 456
            assert cmd.amount == 50
            assert cmd.direction == 'load'
            assert cmd.species_id == 'Human'

    def test_confirm_all_issues_amount_zero(self, mock_manager, mock_fleet, mock_facade, mock_scene):
        """Verify that transfering all issues amount=0 (engine convention)."""
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'load', mock_scene
        )
        dialog.facade = mock_facade
        dialog._populate_load_items()
        
        item = dialog.cargo_items[0]
        # Set slider to MAX
        item['slider'].set_current_value(item['max'])
        
        mock_facade.handle_command.return_value = MagicMock(is_valid=True)
        
        dialog._issue_orders()
        
        cmd = mock_facade.handle_command.call_args[0][0]
        assert cmd.amount == 0 # Should be 0 for 'all'
