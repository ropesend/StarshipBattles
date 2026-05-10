"""Tests for fleet composition and ship loading.

PROJ-43: Uses ShipFactory mocking instead of direct Ship mocking.
PROJ-50: Added fresh_registries fixture for strict DI compliance.
PROJ-181: Removed deprecated set_default_registries() fixture - RegistryManager hydration
          from root conftest.py now sufficient (get_default_registry_provider reads from it).
"""
from unittest.mock import patch, MagicMock
import os
import pytest
import pygame

from game.ui.screens.setup_data_io import load_ships_from_entries, scan_ship_designs


class TestFleetComposition:
    """Tests for fleet composition and ship loading.

    PROJ-43: Updated to use ShipFactory mocking instead of direct Ship mocking.
    PROJ-50: Uses fresh_registries fixture via autouse setup_default_registries.
    """

    @patch('game.simulation.entities.ship.Ship.from_dict')
    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_load_ships_from_entries_basic(self, mock_load_json_required, mock_from_dict):
        """Test loading simple ships without formation."""
        # Setup
        # Create distinct mocks for each iteration
        mock_ship_1 = MagicMock()
        mock_ship_2 = MagicMock()
        mock_from_dict.side_effect = [mock_ship_1, mock_ship_2]

        team_entries = [
            {
                'design': {'path': 'path/to/ship1.json'},
                'strategy': 'brawl_close'
            },
            {
                'design': {'path': 'path/to/ship2.json'},
                'strategy': 'kite_medium'
            }
        ]

        mock_load_json_required.return_value = {"name": "Test Ship"}

        # Execute
        ships = load_ships_from_entries(team_entries, team_id=0, start_x=100, start_y=200, facing_angle=90)

        # Assert
        assert len(ships) == 2
        assert ships[0] == mock_ship_1
        assert ships[1] == mock_ship_2

        # verify Ship attributes set (via factory.configure_ship)
        assert mock_ship_1.position == pygame.math.Vector2(100, 200)
        assert mock_ship_1.angle == 90
        assert mock_ship_1.team_id == 0
        assert mock_ship_1.movement_policy == 'brawl_close'

        assert mock_ship_2.movement_policy == 'kite_medium'

    @patch('game.simulation.entities.ship.Ship.from_dict')
    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_load_ships_from_entries_formation(self, mock_load_json_required, mock_from_dict):
        """Test formation linking and positioning."""

        # Create distinct ship mocks
        master_ship = MagicMock()
        master_ship.position = pygame.math.Vector2(0, 0)
        master_ship.angle = 0
        master_ship.formation.members = []  # Initialize list as code appends to it

        follower_ship = MagicMock()
        follower_ship.position = pygame.math.Vector2(0, 0)

        mock_from_dict.side_effect = [master_ship, follower_ship]
        mock_load_json_required.return_value = {}

        team_entries = [
            {
                'design': {'path': 'master.json'},
                'strategy': 'std',
                'formation_id': 'form1',
                'relative_position': (0, 0)
            },
            {
                'design': {'path': 'follower.json'},
                'strategy': 'std',
                'formation_id': 'form1',
                'relative_position': (10, 10),
                'rotation_mode': 'fixed'
            }
        ]

        # Execute
        ships = load_ships_from_entries(team_entries, team_id=1, start_x=1000, start_y=1000)

        # Assert
        assert len(ships) == 2

        # Follower checks (via factory.setup_formation)
        assert follower_ship.formation.master == master_ship
        assert follower_ship in master_ship.formation.members

        # Position checks (via factory.configure_ship)
        # Master: start_x + 0, start_y + 0 = 1000, 1000
        assert master_ship.position == pygame.math.Vector2(1000, 1000)

        # Follower: start_x + 10, start_y + 10 = 1010, 1010
        assert follower_ship.position == pygame.math.Vector2(1010, 1010)

        # Check formation_offset calculation logic (via factory.setup_formation)
        assert follower_ship.formation.offset == pygame.math.Vector2(10, 10)
        assert follower_ship.formation.rotation_mode == 'fixed'

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_scan_ship_designs(self, mock_load_json, mock_glob):
        """Test scanning ship designs with valid and invalid files."""
        # Setup
        # List of files returned by glob
        mock_glob.return_value = [
            os.path.join('ships', 'valid.json'),
            os.path.join('ships', 'corrupt.json'),  # Will return None (simulating error)
            os.path.join('ships', 'missing_layers.json'),  # Valid JSON but missing schema
            os.path.join('ships', 'builder_theme.json')  # Should be skipped by name
        ]

        # Behavior for load_json
        # 1. valid.json -> Success
        # 2. corrupt.json -> None (simulating malformed file)
        # 3. missing_layers.json -> Dict without 'layers' key
        mock_load_json.side_effect = [
            {'name': 'Valid Ship', 'layers': []},
            None,  # Simulates load_json returning None on error
            {'name': 'Invalid Schema Ship'}
        ]

        # Execute
        designs = scan_ship_designs()

        # Assert
        # Only the first one should make it
        assert len(designs) == 1
        assert designs[0]['name'] == 'Valid Ship'
        assert designs[0]['path'] == os.path.join('ships', 'valid.json')

