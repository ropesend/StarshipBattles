import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.ui.screens.cargo_quick_dialog import CargoQuickDialog
from game.strategy.facade.dto import FleetInfo, PlanetInfo

class TestCargoQuickDialogResolutionBug:
    """Tests specifically reproducing the planet resolution coordinate bug."""

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
        # A fleet at a global galaxy position
        fleet = MagicMock()
        fleet.id = 1
        fleet.location = (50, 100) # Global Hex
        return fleet

    def test_load_fails_with_relative_hex_at_colony(self, mock_manager, mock_scene, mock_fleet):
        """
        Reproduce the bug: Clicking at system center (0,0) while in system view
        should resolve the colony if the fleet is at that system's global hex.
        Currently it fails because it tries to find a system at global hex (0,0).
        """
        # Arrange: Colony is at global hex (50, 100)
        # In reality, facade.planets.at_hex(global_hex) should return it.
        
        # Define what the facade SHOULD return if called with the CORRECT hex
        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_colony.name = "Home Colony"
        
        # Proper PlanetInfo mock
        mock_planet_info = MagicMock(spec=PlanetInfo)
        mock_planet_info.population_details = (
            ("human", 100, 1.0),
        )
        mock_scene._facade.planets.get.return_value = mock_planet_info
        
        # The facade is called with the hex passed to the dialog
        # Current implementation:
        # planets = self.facade.planets.at_hex(self.hex_coord)
        def side_effect(hex_val):
            if hex_val == (50, 100):
                return [mock_colony]
            return [] # No system at (0,0)
            
        mock_scene._facade.planets.at_hex.side_effect = side_effect
        
        # Act: Pass (0,0) as the hex_coord (simulating a click in system view)
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'load', mock_scene, window_manager=None
        )
        
        # Assert: With the fix, the dialog should fallback to fleet.location (50, 100)
        # and find the colony, so cargo_items should NOT be empty.
        assert len(dialog.cargo_items) > 0, "FIX FAILED: dialog should find items via fleet.location fallback"
        assert not hasattr(dialog, 'lbl_no_items'), "FIX FAILED: should NOT show 'No colony' message"
        assert "Home Colony" in dialog.cargo_items[0]['label']

    def test_unload_falls_back_to_fleet_location(self, mock_manager, mock_scene, mock_fleet):
        """Verify that unload (drop) also falls back to fleet location."""
        # Arrange: Fleet with passengers
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 50
        mock_scene._facade.fleets.get.return_value = mock_fleet_info
        
        # Colony is at global hex (50, 100)
        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_colony.name = "Home Colony"
        
        def side_effect(hex_val):
            if hex_val == (50, 100):
                return [mock_colony]
            return []
            
        mock_scene._facade.planets.at_hex.side_effect = side_effect
        
        # Act
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )
        
        # Assert
        assert len(dialog.cargo_items) == 1
        assert dialog.cargo_items[0]['type'] == 'passengers'
        assert not hasattr(dialog, 'lbl_no_items')
