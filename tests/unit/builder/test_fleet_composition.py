from unittest.mock import patch, MagicMock
import os
import pygame

from game.ui.screens.setup_screen import BattleSetupScreen
from game.ui.screens.setup_data_io import load_ships_from_entries, scan_ship_designs


class TestFleetComposition:

    @patch('game.ui.screens.setup_data_io.Ship')
    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_load_ships_from_entries_basic(self, mock_load_json_required, MockShip):
        """Test loading simple ships without formation."""
        # Setup
        # Create distinct mocks for each iteration
        mock_ship_1 = MagicMock()
        mock_ship_2 = MagicMock()
        MockShip.from_dict.side_effect = [mock_ship_1, mock_ship_2]

        # Mock Vector2 behavior is not strictly needed if we just check attribute assignment,
        # but if the code did math, we'd need it. Here 'load_ships' does:
        # ship.position = pygame.math.Vector2(start_x, start_y + i * 5000)
        # So the checks below should just check if .position was set.

        team_entries = [
            {
                'design': {'path': 'path/to/ship1.json'},
                'strategy': 'aggressive'
            },
            {
                'design': {'path': 'path/to/ship2.json'},
                'strategy': 'defensive'
            }
        ]

        mock_load_json_required.return_value = {"name": "Test Ship"}

        # Execute
        ships = load_ships_from_entries(team_entries, team_id=0, start_x=100, start_y=200, facing_angle=90)

        # Assert
        assert len(ships) == 2
        assert ships[0] == mock_ship_1
        assert ships[1] == mock_ship_2

        # verify Ship attributes set
        assert mock_ship_1.angle == 90
        assert mock_ship_1.team_id == 0
        assert mock_ship_1.ai_strategy == 'aggressive'

        assert mock_ship_2.ai_strategy == 'defensive'

    @patch('game.ui.screens.setup_data_io.Ship')
    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_load_ships_from_entries_formation(self, mock_load_json_required, MockShip):
        """Test formation linking and positioning."""

        # Create distinct ship mocks
        master_ship = MagicMock()
        master_ship.position = pygame.math.Vector2(0, 0)
        master_ship.angle = 0
        master_ship.formation_members = []  # Initialize list as code appends to it

        follower_ship = MagicMock()
        follower_ship.position = pygame.math.Vector2(0, 0)

        MockShip.from_dict.side_effect = [master_ship, follower_ship]
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

        # Master checks
        # First ship in formation_id group is master
        # It shouldn't have formation_master set (or rather, code relies on existing value or doesn't set it)
        # The code: if f_id in formation_masters ... else ...
        # If not in, sets formation_masters[f_id] = ship.

        # Follower checks
        assert follower_ship.formation_master == master_ship
        assert follower_ship in master_ship.formation_members

        # Position checks
        # Master: start_x + 0, start_y + 0 = 1000, 1000
        assert master_ship.position == pygame.math.Vector2(1000, 1000)

        # Follower: start_x + 10, start_y + 10 = 1010, 1010
        assert follower_ship.position == pygame.math.Vector2(1010, 1010)

        # Check formation_offset calculation logic
        # diff = ship.position - master.position
        # The logic uses Vector2 subtraction. Since we mocked position with actual Vector2 (above),
        # or we rely on the code setting them to Vector2.
        # Wait, the code sets ship.position = Vector2(...).
        # So master.position IS a Vector2(1000, 1000).
        # follower.position IS a Vector2(1010, 1010).
        # diff = Vector2(10, 10).
        # fixed mode: formation_offset = diff
        assert follower_ship.formation_offset == pygame.math.Vector2(10, 10)
        assert follower_ship.formation_rotation_mode == 'fixed'

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

    @patch('game.ui.screens.setup_screen.Ship')
    @patch('game.ui.screens.setup_screen.filedialog.askopenfilename')
    @patch('game.ui.screens.setup_screen.tk.Tk')
    @patch('game.ui.screens.setup_screen.uuid.uuid4')
    @patch('game.ui.screens.setup_screen.load_json_required')
    def test_add_formation_to_team(self, mock_load_json_required, mock_uuid, mock_tk, mock_dialog, MockShip):
        """Test adding a formation to a team."""
        # Setup
        setup_screen = BattleSetupScreen()
        setup_screen.available_ship_designs = [
            {'path': '/abs/path/to/ship.json', 'name': 'Test Ship', 'ai_strategy': 'test_strat'}
        ]

        formation = {
            'name': 'Delta',
            'arrows': [
                {'pos': (0, 0)},        # Center
                {'pos': (-100, -100)},  # Left
                {'pos': (100, -100)}    # Right
            ]
        }

        # Mock User selection
        mock_dialog.return_value = '/abs/path/to/ship.json'

        # Mock Ship loaded data
        mock_load_json_required.return_value = {'name': 'Test Ship', 'ship_class': 'Frigate', 'ai_strategy': 'test_strat'}

        # Mock Ship instance processing
        mock_ship = MagicMock()
        mock_ship.radius = 50
        MockShip.from_dict.return_value = mock_ship

        # Mock UUID
        mock_uuid.return_value = 'form-uuid-123'

        # Execute
        setup_screen.add_formation_to_team(formation, team_idx=1)

        # Assert
        assert len(setup_screen.team1) == 3
        assert len(setup_screen.team2) == 0

        # Check entries
        entry0 = setup_screen.team1[0]
        assert entry0['formation_id'] == 'form-uuid-123'
        assert entry0['formation_name'] == 'Delta'
        assert entry0['design']['name'] == 'Test Ship'

        # Check positions
        # Diameter = 100. GRID_UNIT = 50.
        # Scale = 2.0
        # Center of input:
        # Xs: 0, -100, 100 -> Avg: 0
        # Ys: 0, -100, -100 -> Avg: -66.66...
        # Let's verify math relative to center
        # CenterX = 0
        # CenterY = -200/3 = -66.67

        # Point 1 (0,0): dx = 0, dy = 66.67.
        # world_x = 0 * 2 = 0
        # world_y = 66.67 / 50 * 100 = 133.34

        # Validating checking roughly
        p0 = setup_screen.team1[0]['relative_position']
        # We can't be 100% sure of order unless we know dict iteration or list order is preserved.
        # The code iterates 'arrows', which is a list. So order is preserved.

        # 1st arrow: (0,0)
        # 2nd arrow: (-100, -100)

        # Just ensure they are all present and have correct IDs
        for entry in setup_screen.team1:
            assert entry['formation_id'] == 'form-uuid-123'
