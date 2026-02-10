import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.ui.screens.transfer_dialog import TransferDialog
from game.strategy.facade.dto import FleetInfo, PlanetInfo

class TestTransferDialog:
    """Tests for TransferDialog UI and logic."""

    def _get_options(self, dropdown):
        """Extract labels from dropdown options_list (handles strings or tuples)."""
        opts = []
        for opt in dropdown.options_list:
            if isinstance(opt, tuple):
                opts.append(opt[0])
            else:
                opts.append(opt)
        return opts

    @pytest.fixture
    def mock_manager(self):
        return pygame_gui.UIManager((800, 600))

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene._facade = MagicMock()
        return scene

    @pytest.fixture
    def mock_fleet(self):
        fleet = MagicMock()
        fleet.id = 1
        fleet.fleet_id = 1
        fleet.location = (0, 0)
        return fleet

    def test_transfer_dialog_init_populates_sources(self, mock_manager, mock_scene, mock_fleet):
        """Dialog should find fleets and colonies at hex upon init."""
        # Arrange
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f1.location = (0, 0)
        f2 = MagicMock(fleet_id=2, owner_id=0)
        f2.location = (0, 0)
        mock_scene._facade.get_fleets_at_hex.return_value = [f1, f2]
        
        p1 = MagicMock(planet_id=10, owner_id=0)
        p1.name = "Alpha"
        p2 = MagicMock(planet_id=11, owner_id=None)
        p2.name = "Beta"
        mock_scene._facade.get_planets_at_hex.return_value = [p1, p2]
        
        # Mock DTOs for initial population calls
        dummy_fleet_info = MagicMock(spec=FleetInfo)
        dummy_fleet_info.passengers_current = 0
        mock_scene._facade.get_fleet.return_value = dummy_fleet_info
        
        dummy_planet_info = MagicMock(spec=PlanetInfo)
        dummy_planet_info.population_details = []
        dummy_planet_info.total_population = 0
        mock_scene._facade.get_planet.return_value = dummy_planet_info
        
        # Act
        rect = pygame.Rect(0, 0, 600, 500)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)
        
        # Assert
        # 2 fleets + 1 colonized planet = 3 sources
        assert len(dialog.available_sources) == 3
        options = self._get_options(dialog.drop_source)
        assert "Fleet 1" in options
        assert "Fleet 2" in options
        assert "Colony: Alpha" in options

    def test_source_change_updates_targets(self, mock_manager, mock_scene, mock_fleet):
        """Changing source should remove it from target options."""
        # Arrange
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f2 = MagicMock(fleet_id=2, owner_id=0)
        mock_scene._facade.get_fleets_at_hex.return_value = [f1, f2]
        mock_scene._facade.get_planets_at_hex.return_value = []
        
        # Mock FleetInfo DTO
        dummy_fleet_info = MagicMock(spec=FleetInfo)
        dummy_fleet_info.passengers_current = 0
        mock_scene._facade.get_fleet.return_value = dummy_fleet_info
        
        rect = pygame.Rect(0, 0, 600, 500)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)
        
        # Act
        dialog._on_source_changed("Fleet 2")
        
        # Assert
        options = self._get_options(dialog.drop_target)
        assert "Fleet 2" not in options
        assert "Fleet 1" in options

    def test_update_cargo_list_for_colony(self, mock_manager, mock_scene, mock_fleet):
        """Colony source should show population details from DTO."""
        # Arrange
        mock_scene._facade.get_fleets_at_hex.return_value = [mock_fleet]
        # Colony ID 10
        p1 = MagicMock(planet_id=10, owner_id=0)
        p1.name = "Alpha"
        mock_scene._facade.get_planets_at_hex.return_value = [p1]
        
        # Mock FleetInfo DTO
        dummy_f_info = MagicMock(spec=FleetInfo)
        dummy_f_info.passengers_current = 0
        mock_scene._facade.get_fleet.return_value = dummy_f_info
        
        # Mock PlanetInfo DTO
        mock_planet_info = MagicMock(spec=PlanetInfo)
        mock_planet_info.population_details = (
            ("human", 100, 1.0),
            ("vulcan", 50, 0.8)
        )
        mock_scene._facade.get_planet.return_value = mock_planet_info
        
        rect = pygame.Rect(0, 0, 600, 500)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)
        
        # Act - Selection change already happened in init implicitly if Fleet 1 was starting option,
        # but here we test explicit colony source update.
        dialog._update_cargo_list({'type': 'colony', 'id': 10})
        
        # Assert
        assert len(dialog.available_cargo) == 2
        assert any(c['species_id'] == 'human' for c in dialog.available_cargo)
        assert any(c['species_id'] == 'vulcan' for c in dialog.available_cargo)
        assert self._get_options(dialog.drop_item) == [
            "Population: human (100)",
            "Population: vulcan (50)"
        ]

    def test_issue_order_dispatches_command(self, mock_manager, mock_scene, mock_fleet):
        """Confirming transfer should dispatch IssueTransferCommand via facade."""
        # Arrange
        mock_scene._facade.get_fleets_at_hex.return_value = [mock_fleet]
        p1 = MagicMock(planet_id=10, owner_id=0)
        p1.name = "Alpha"
        mock_scene._facade.get_planets_at_hex.return_value = [p1]
        
        # Mock DTOs
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 80
        mock_scene._facade.get_fleet.return_value = mock_fleet_info
        
        rect = pygame.Rect(0, 0, 600, 500)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)
        
        # Setup selection state manually
        dialog.available_sources = [{'label': 'Fleet 1', 'type': 'fleet', 'id': 1}]
        dialog.available_targets = [{'label': 'Colony: Alpha', 'type': 'colony', 'id': 10}]
        dialog.available_cargo = [{'label': 'Passengers (80)', 'type': 'passengers', 'species_id': None, 'max': 80}]
        
        dialog.drop_source = MagicMock()
        dialog.drop_source.selected_option = "Fleet 1"
        dialog.drop_target = MagicMock()
        dialog.drop_target.selected_option = "Colony: Alpha"
        dialog.drop_item = MagicMock()
        dialog.drop_item.selected_option = "Passengers (80)"
        dialog.slider_amount = MagicMock()
        dialog.slider_amount.get_current_value.return_value = 30.0
        
        # Act
        with patch('game.ui.screens.transfer_dialog.IssueTransferCommand') as mock_cmd_class:
            dialog._issue_order()
            
            # Assert
            mock_cmd_class.assert_called_once_with(
                fleet_id=1,
                planet_id=10,
                cargo_type='passengers',
                direction='unload',
                amount=30,
                species_id=None
            )
            mock_scene._facade.handle_command.assert_called_once()
