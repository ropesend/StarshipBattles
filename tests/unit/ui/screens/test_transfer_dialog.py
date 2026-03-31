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
        scene.facade = scene._facade  # Public accessor
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
        # 2 fleets + 1 colonized planet + 1 uncolonized planet = 4 sources
        assert len(dialog.available_sources) == 4
        options = self._get_options(dialog.drop_source)
        assert "Fleet 1" in options
        assert "Fleet 2" in options
        assert "Colony: Alpha" in options
        assert "Planet: Beta" in options

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

    def test_grid_builds_resource_rows(self, mock_manager, mock_scene, mock_fleet):
        """Grid should include rows for all 8 resource types."""
        # Arrange
        mock_scene._facade.get_fleets_at_hex.return_value = [mock_fleet]
        p1 = MagicMock(planet_id=10, owner_id=0)
        p1.name = "Alpha"
        mock_scene._facade.get_planets_at_hex.return_value = [p1]

        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 0
        mock_fleet_info.cargo_resources = (("metals", 100),)
        mock_fleet_info.cargo_capacities = (("metals", 1000),)
        mock_scene._facade.get_fleet.return_value = mock_fleet_info

        mock_planet_info = MagicMock(spec=PlanetInfo)
        mock_planet_info.population_details = ()
        mock_planet_info.stockpile = (("metals", 500.0),)
        mock_planet_info.max_stockpile = ()
        mock_scene._facade.get_planet.return_value = mock_planet_info

        rect = pygame.Rect(0, 0, 900, 700)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)

        # Assert - should have 8 resource rows
        resource_keys = [r['cargo_key'] for r in dialog._row_data
                         if not r['cargo_key'].startswith('passengers')]
        assert len(resource_keys) == 8
        assert "metals" in resource_keys
        assert "fuel" in resource_keys

    def test_confirm_dispatches_pending_transfers(self, mock_manager, mock_scene, mock_fleet):
        """Confirm should dispatch IssueTransferCommand for each non-zero pending."""
        # Arrange
        mock_scene._facade.get_fleets_at_hex.return_value = [mock_fleet]
        p1 = MagicMock(planet_id=10, owner_id=0)
        p1.name = "Alpha"
        mock_scene._facade.get_planets_at_hex.return_value = [p1]

        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 0
        mock_fleet_info.cargo_resources = ()
        mock_fleet_info.cargo_capacities = ()
        mock_scene._facade.get_fleet.return_value = mock_fleet_info

        mock_planet_info = MagicMock(spec=PlanetInfo)
        mock_planet_info.population_details = ()
        mock_planet_info.stockpile = ()
        mock_planet_info.max_stockpile = ()
        mock_scene._facade.get_planet.return_value = mock_planet_info

        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)

        rect = pygame.Rect(0, 0, 900, 700)
        dialog = TransferDialog(rect, mock_manager, mock_fleet, (0, 0), mock_scene)

        # Set up pending transfers manually
        dialog._current_source = {'type': 'fleet', 'id': 1, 'label': 'Fleet 1'}
        dialog._current_target = {'type': 'colony', 'id': 10, 'label': 'Colony: Alpha'}
        dialog.pending_transfers = {"metals": 50, "fuel": -100}  # Load 50 metals, drop 100 fuel

        # Act
        dialog._on_confirm()

        # Assert - should have called handle_command twice (one per non-zero transfer)
        assert mock_scene._facade.handle_command.call_count == 2
