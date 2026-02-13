"""Tests for setup_data_io module - battle setup I/O operations."""

import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
import pygame


class TestGetBasePath:
    """Tests for get_base_path function."""

    def test_returns_paths_root_dir(self):
        """Verify get_base_path delegates to Paths.ROOT_DIR."""
        from game.ui.screens.setup_data_io import get_base_path
        from game.core.paths import Paths

        result = get_base_path()
        assert result == Paths.ROOT_DIR


class TestScanShipDesigns:
    """Tests for scan_ship_designs function."""

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_returns_valid_designs(self, mock_load_json, mock_glob):
        """Verify valid ship designs are returned."""
        from game.ui.screens.setup_data_io import scan_ship_designs

        mock_glob.return_value = ['/ships/frigate.json', '/ships/cruiser.json']
        mock_load_json.side_effect = [
            {'name': 'Frigate', 'layers': [], 'ship_class': 'Frigate', 'ai_strategy': 'aggressive'},
            {'name': 'Cruiser', 'layers': [], 'ship_class': 'Cruiser'}
        ]

        designs = scan_ship_designs()

        assert len(designs) == 2
        assert designs[0]['name'] == 'Frigate'
        assert designs[0]['ship_class'] == 'Frigate'
        assert designs[0]['ai_strategy'] == 'aggressive'
        assert designs[1]['name'] == 'Cruiser'
        assert designs[1]['ai_strategy'] == 'standard_ranged'  # default

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_skips_builder_theme_json(self, mock_load_json, mock_glob):
        """Verify builder_theme.json is skipped."""
        from game.ui.screens.setup_data_io import scan_ship_designs

        mock_glob.return_value = ['/ships/frigate.json', '/ships/builder_theme.json']
        mock_load_json.return_value = {'name': 'Frigate', 'layers': []}

        designs = scan_ship_designs()

        assert len(designs) == 1
        assert mock_load_json.call_count == 1

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_skips_invalid_designs(self, mock_load_json, mock_glob):
        """Verify files without 'name' or 'layers' are skipped."""
        from game.ui.screens.setup_data_io import scan_ship_designs

        mock_glob.return_value = ['/ships/valid.json', '/ships/no_layers.json', '/ships/no_name.json']
        mock_load_json.side_effect = [
            {'name': 'Valid', 'layers': []},
            {'name': 'NoLayers'},  # missing layers
            {'layers': []}  # missing name
        ]

        designs = scan_ship_designs()

        assert len(designs) == 1
        assert designs[0]['name'] == 'Valid'

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_handles_json_decode_error(self, mock_load_json, mock_glob):
        """Verify JSON decode errors are handled gracefully."""
        from game.ui.screens.setup_data_io import scan_ship_designs

        mock_glob.return_value = ['/ships/valid.json', '/ships/corrupt.json']
        mock_load_json.side_effect = [
            {'name': 'Valid', 'layers': []},
            json.JSONDecodeError('error', 'doc', 0)
        ]

        designs = scan_ship_designs()

        assert len(designs) == 1

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_handles_file_not_found(self, mock_load_json, mock_glob):
        """Verify FileNotFoundError is handled gracefully."""
        from game.ui.screens.setup_data_io import scan_ship_designs

        mock_glob.return_value = ['/ships/missing.json']
        mock_load_json.side_effect = FileNotFoundError()

        designs = scan_ship_designs()

        assert len(designs) == 0

    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_returns_empty_list_when_no_files(self, mock_load_json, mock_glob):
        """Verify empty list returned when no JSON files found."""
        from game.ui.screens.setup_data_io import scan_ship_designs

        mock_glob.return_value = []

        designs = scan_ship_designs()

        assert designs == []


class TestScanFormations:
    """Tests for scan_formations function."""

    @patch('game.ui.screens.setup_data_io.os.path.exists')
    @patch('game.ui.screens.setup_data_io.os.makedirs')
    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_returns_valid_formations(self, mock_load_json, mock_glob, mock_makedirs, mock_exists):
        """Verify valid formations are returned."""
        from game.ui.screens.setup_data_io import scan_formations

        mock_exists.return_value = True
        mock_glob.return_value = ['/formations/wedge.json', '/formations/line.json']
        mock_load_json.side_effect = [
            {'arrows': [{'x': 0, 'y': 0}]},
            {'arrows': [{'x': 1, 'y': 1}]}
        ]

        formations = scan_formations()

        assert len(formations) == 2
        assert formations[0]['name'] == 'wedge'
        assert formations[1]['name'] == 'line'

    @patch('game.ui.screens.setup_data_io.os.path.exists')
    @patch('game.ui.screens.setup_data_io.os.makedirs')
    @patch('game.ui.screens.setup_data_io.glob.glob')
    def test_creates_directory_if_missing(self, mock_glob, mock_makedirs, mock_exists):
        """Verify formations directory is created if missing."""
        from game.ui.screens.setup_data_io import scan_formations

        mock_exists.return_value = False
        mock_glob.return_value = []

        scan_formations()

        mock_makedirs.assert_called_once()

    @patch('game.ui.screens.setup_data_io.os.path.exists')
    @patch('game.ui.screens.setup_data_io.os.makedirs')
    @patch('game.ui.screens.setup_data_io.glob.glob')
    @patch('game.ui.screens.setup_data_io.load_json')
    def test_skips_files_without_arrows(self, mock_load_json, mock_glob, mock_makedirs, mock_exists):
        """Verify files without 'arrows' key are skipped."""
        from game.ui.screens.setup_data_io import scan_formations

        mock_exists.return_value = True
        mock_glob.return_value = ['/formations/valid.json', '/formations/invalid.json']
        mock_load_json.side_effect = [
            {'arrows': []},
            {'other_key': 'value'}
        ]

        formations = scan_formations()

        assert len(formations) == 1


class TestSaveBattleSetup:
    """Tests for save_battle_setup function."""

    @patch('game.ui.screens.setup_data_io.save_json')
    def test_saves_basic_setup(self, mock_save_json):
        """Verify basic battle setup is saved correctly."""
        from game.ui.screens.setup_data_io import save_battle_setup

        mock_save_json.return_value = True
        team1 = [{'design': {'path': '/ships/frigate.json'}, 'strategy': 'aggressive'}]
        team2 = [{'design': {'path': '/ships/cruiser.json'}, 'strategy': 'defensive'}]

        result = save_battle_setup('/setups/battle1.json', team1, team2)

        assert result is True
        call_args = mock_save_json.call_args[0]
        assert call_args[0] == '/setups/battle1.json'
        data = call_args[1]
        assert data['name'] == 'battle1'
        assert len(data['team1']) == 1
        assert len(data['team2']) == 1
        assert data['team1'][0]['design_file'] == 'frigate.json'
        assert data['team1'][0]['strategy'] == 'aggressive'

    @patch('game.ui.screens.setup_data_io.save_json')
    def test_saves_with_formation_data(self, mock_save_json):
        """Verify formation data is included in save."""
        from game.ui.screens.setup_data_io import save_battle_setup

        mock_save_json.return_value = True
        team1 = [{
            'design': {'path': '/ships/frigate.json'},
            'strategy': 'aggressive',
            'relative_position': [100, 200],
            'formation_id': 'leader',
            'rotation_mode': 'absolute'
        }]

        save_battle_setup('/setups/battle.json', team1, [])

        data = mock_save_json.call_args[0][1]
        assert data['team1'][0]['relative_position'] == [100, 200]
        assert data['team1'][0]['formation_id'] == 'leader'
        assert data['team1'][0]['rotation_mode'] == 'absolute'

    @patch('game.ui.screens.setup_data_io.save_json')
    def test_returns_false_on_save_failure(self, mock_save_json):
        """Verify False is returned when save fails."""
        from game.ui.screens.setup_data_io import save_battle_setup

        mock_save_json.return_value = False

        result = save_battle_setup('/setups/battle.json', [], [])

        assert result is False


class TestLoadBattleSetup:
    """Tests for load_battle_setup function."""

    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_loads_basic_setup(self, mock_load_json):
        """Verify basic battle setup is loaded correctly."""
        from game.ui.screens.setup_data_io import load_battle_setup

        mock_load_json.return_value = {
            'team1': [{'design_file': 'frigate.json', 'strategy': 'aggressive'}],
            'team2': [{'design_file': 'cruiser.json', 'strategy': 'defensive'}]
        }
        available_designs = [
            {'path': '/ships/frigate.json'},
            {'path': '/ships/cruiser.json'}
        ]

        team1, team2 = load_battle_setup('/setups/battle.json', available_designs)

        assert len(team1) == 1
        assert len(team2) == 1
        assert team1[0]['strategy'] == 'aggressive'
        assert team2[0]['strategy'] == 'defensive'

    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_loads_formation_data(self, mock_load_json):
        """Verify formation data is loaded correctly."""
        from game.ui.screens.setup_data_io import load_battle_setup

        mock_load_json.return_value = {
            'team1': [{
                'design_file': 'frigate.json',
                'strategy': 'aggressive',
                'relative_position': [100, 200],
                'formation_id': 'leader',
                'rotation_mode': 'absolute'
            }],
            'team2': []
        }
        available_designs = [{'path': '/ships/frigate.json'}]

        team1, team2 = load_battle_setup('/setups/battle.json', available_designs)

        assert team1[0]['relative_position'] == [100, 200]
        assert team1[0]['formation_id'] == 'leader'
        assert team1[0]['rotation_mode'] == 'absolute'

    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_skips_missing_designs(self, mock_load_json):
        """Verify entries with missing designs are skipped."""
        from game.ui.screens.setup_data_io import load_battle_setup

        mock_load_json.return_value = {
            'team1': [
                {'design_file': 'exists.json', 'strategy': 'aggressive'},
                {'design_file': 'missing.json', 'strategy': 'defensive'}
            ],
            'team2': []
        }
        available_designs = [{'path': '/ships/exists.json'}]

        team1, team2 = load_battle_setup('/setups/battle.json', available_designs)

        assert len(team1) == 1

    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_returns_none_on_error(self, mock_load_json):
        """Verify (None, None) returned on load error."""
        from game.ui.screens.setup_data_io import load_battle_setup

        mock_load_json.side_effect = FileNotFoundError()

        team1, team2 = load_battle_setup('/setups/missing.json', [])

        assert team1 is None
        assert team2 is None

    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_handles_json_decode_error(self, mock_load_json):
        """Verify JSON decode errors are handled."""
        from game.ui.screens.setup_data_io import load_battle_setup

        mock_load_json.side_effect = json.JSONDecodeError('error', 'doc', 0)

        team1, team2 = load_battle_setup('/setups/corrupt.json', [])

        assert team1 is None
        assert team2 is None

    @patch('game.ui.screens.setup_data_io.load_json_required')
    def test_handles_empty_teams(self, mock_load_json):
        """Verify empty teams are handled correctly."""
        from game.ui.screens.setup_data_io import load_battle_setup

        mock_load_json.return_value = {}  # No team1/team2 keys

        team1, team2 = load_battle_setup('/setups/empty.json', [])

        assert team1 == []
        assert team2 == []


class TestLoadShipsFromEntries:
    """Tests for load_ships_from_entries function."""

    @patch('game.ui.screens.setup_data_io.load_json_required')
    @patch('game.ui.screens.setup_data_io._ship_factory')
    def test_loads_basic_ships(self, mock_factory, mock_load_json):
        """Verify basic ship loading works."""
        from game.ui.screens.setup_data_io import load_ships_from_entries

        mock_ship = MagicMock()
        mock_factory.create_from_design.return_value = mock_ship
        mock_load_json.return_value = {'name': 'Frigate', 'layers': []}

        entries = [{'design': {'path': '/ships/frigate.json'}, 'strategy': 'aggressive'}]

        ships = load_ships_from_entries(entries, team_id=0, start_x=1000, start_y=2000)

        assert len(ships) == 1
        mock_factory.configure_ship.assert_called_once()
        mock_ship.recalculate_stats.assert_called_once()

    @patch('game.ui.screens.setup_data_io.load_json_required')
    @patch('game.ui.screens.setup_data_io._ship_factory')
    def test_uses_relative_position(self, mock_factory, mock_load_json):
        """Verify relative positions are applied."""
        from game.ui.screens.setup_data_io import load_ships_from_entries

        mock_ship = MagicMock()
        mock_factory.create_from_design.return_value = mock_ship
        mock_load_json.return_value = {'name': 'Frigate', 'layers': []}

        entries = [{
            'design': {'path': '/ships/frigate.json'},
            'strategy': 'aggressive',
            'relative_position': [100, 200]
        }]

        load_ships_from_entries(entries, team_id=0, start_x=1000, start_y=2000)

        call_kwargs = mock_factory.configure_ship.call_args[1]
        position = call_kwargs['position']
        assert position.x == 1100  # 1000 + 100
        assert position.y == 2200  # 2000 + 200

    @patch('game.ui.screens.setup_data_io.load_json_required')
    @patch('game.ui.screens.setup_data_io._ship_factory')
    def test_default_position_spacing(self, mock_factory, mock_load_json):
        """Verify default position spacing when no relative_position."""
        from game.ui.screens.setup_data_io import load_ships_from_entries

        mock_ship = MagicMock()
        mock_factory.create_from_design.return_value = mock_ship
        mock_load_json.return_value = {'name': 'Frigate', 'layers': []}

        entries = [
            {'design': {'path': '/ships/ship1.json'}, 'strategy': 'a'},
            {'design': {'path': '/ships/ship2.json'}, 'strategy': 'b'}
        ]

        load_ships_from_entries(entries, team_id=0, start_x=0, start_y=0)

        calls = mock_factory.configure_ship.call_args_list
        pos1 = calls[0][1]['position']
        pos2 = calls[1][1]['position']
        assert pos1.y == 0
        assert pos2.y == 5000  # i * 5000

    @patch('game.ui.screens.setup_data_io.load_json_required')
    @patch('game.ui.screens.setup_data_io._ship_factory')
    def test_sets_up_formations(self, mock_factory, mock_load_json):
        """Verify formations are set up when formation_id present."""
        from game.ui.screens.setup_data_io import load_ships_from_entries

        mock_ship = MagicMock()
        mock_factory.create_from_design.return_value = mock_ship
        mock_load_json.return_value = {'name': 'Frigate', 'layers': []}

        entries = [{
            'design': {'path': '/ships/frigate.json'},
            'strategy': 'aggressive',
            'formation_id': 'leader',
            'rotation_mode': 'relative'
        }]

        ships = load_ships_from_entries(entries, team_id=0, start_x=0, start_y=0)

        mock_factory.setup_formation.assert_called_once()
        formation_data = mock_factory.setup_formation.call_args[0][1]
        assert formation_data[0]['formation_id'] == 'leader'
        assert formation_data[0]['rotation_mode'] == 'relative'

    @patch('game.ui.screens.setup_data_io.load_json_required')
    @patch('game.ui.screens.setup_data_io._ship_factory')
    def test_passes_facing_angle(self, mock_factory, mock_load_json):
        """Verify facing angle is passed to configure_ship."""
        from game.ui.screens.setup_data_io import load_ships_from_entries

        mock_ship = MagicMock()
        mock_factory.create_from_design.return_value = mock_ship
        mock_load_json.return_value = {'name': 'Frigate', 'layers': []}

        entries = [{'design': {'path': '/ships/frigate.json'}, 'strategy': 'a'}]

        load_ships_from_entries(entries, team_id=1, start_x=0, start_y=0, facing_angle=90)

        call_kwargs = mock_factory.configure_ship.call_args[1]
        assert call_kwargs['angle'] == 90
        assert call_kwargs['team_id'] == 1
