"""
Battle setup data I/O operations.

Functions for scanning ship designs, formations, loading/saving battle setups,
and loading ships from configuration entries.

PROJ-43: Uses ShipFactory facade instead of direct Ship import.
"""
import os
import glob
import json
import pygame

from game.core.logger import log_info, log_warning, log_error
from game.ui.services.ship_factory import ShipFactory
from game.core.json_utils import load_json, load_json_required, save_json
from game.core.paths import Paths


# Module-level factory instance for convenience
_ship_factory = ShipFactory()


def get_base_path():
    """Get the base path (root of project). Delegates to Paths.ROOT_DIR."""
    return Paths.ROOT_DIR


def scan_ship_designs():
    """Scan for available ship design JSON files in ships/ folder."""
    ships_folder = Paths.SHIPS_DIR
    json_files = glob.glob(os.path.join(ships_folder, "*.json"))

    designs = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        # Skip config files (builder_theme.json may end up in ships folder)
        if filename == 'builder_theme.json':
            continue
        # Try to load and verify it's a ship design
        try:
            data = load_json(filepath)
            if data and 'name' in data and 'layers' in data:
                designs.append({
                    'path': filepath,
                    'name': data.get('name', filename),
                    'ship_class': data.get('ship_class', 'Unknown'),
                    'ai_strategy': data.get('ai_strategy', 'standard_ranged')
                })
        except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            log_warning(f"Failed to load ship design from '{filepath}': {e}")
    return designs


def scan_formations():
    """Scan for available formation JSON files in data/formations directory."""
    formations_dir = Paths.FORMATIONS_DIR

    if not os.path.exists(formations_dir):
        os.makedirs(formations_dir)

    json_files = glob.glob(os.path.join(formations_dir, "*.json"))

    formations = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        if filename == 'builder_theme.json':
            continue

        try:
            data = load_json(filepath)
            if data and 'arrows' in data:
                formations.append({
                    'path': filepath,
                    'name': filename.replace('.json', ''),
                    'arrows': data['arrows']
                })
        except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            log_warning(f"Failed to load formation from '{filepath}': {e}")
    return formations


def load_ships_from_entries(team_entries, team_id, start_x, start_y, facing_angle=0):
    """
    Load ships from team entry list.

    PROJ-43: Uses ShipFactory facade instead of direct Ship import.

    Args:
        team_entries: List of team entry dicts with design and strategy info
        team_id: Team identifier (0 or 1)
        start_x: Starting X position
        start_y: Starting Y position
        facing_angle: Initial facing angle in degrees

    Returns:
        List of Ship objects
    """
    ships = []
    formation_data = []

    for i, entry in enumerate(team_entries):
        data = load_json_required(entry['design']['path'])
        ship = _ship_factory.create_from_design(data)

        # Calculate position
        if 'relative_position' in entry:
            rx, ry = entry['relative_position']
            position = pygame.math.Vector2(start_x + rx, start_y + ry)
        else:
            position = pygame.math.Vector2(start_x, start_y + i * 5000)

        # Configure ship via factory
        _ship_factory.configure_ship(
            ship,
            position=position,
            angle=facing_angle,
            team_id=team_id,
            ai_strategy=entry['strategy'],
            source_file=os.path.basename(entry['design']['path'])
        )
        ship.recalculate_stats()

        # Collect formation data for later linking
        if 'formation_id' in entry:
            formation_data.append({
                'ship_index': len(ships),
                'formation_id': entry['formation_id'],
                'rotation_mode': entry.get('rotation_mode', 'relative')
            })

        ships.append(ship)

    # Set up formations via factory
    if formation_data:
        _ship_factory.setup_formation(ships, formation_data)

    return ships


def save_battle_setup(file_path, team1, team2):
    """
    Save battle setup to JSON file.

    Args:
        file_path: Destination file path
        team1: Team 1 entry list
        team2: Team 2 entry list

    Returns:
        True if successful
    """
    data = {
        "name": os.path.basename(file_path).replace(".json", ""),
        "team1": [],
        "team2": []
    }

    def serialize_team(team_list, out_list):
        for entry in team_list:
            item = {
                "design_file": os.path.basename(entry['design']['path']),
                "strategy": entry['strategy']
            }
            if 'relative_position' in entry:
                item['relative_position'] = entry['relative_position']
            if 'formation_id' in entry:
                item['formation_id'] = entry['formation_id']
            if 'rotation_mode' in entry:
                item['rotation_mode'] = entry['rotation_mode']
            out_list.append(item)

    serialize_team(team1, data["team1"])
    serialize_team(team2, data["team2"])

    if save_json(file_path, data):
        log_info(f"Saved battle setup to {file_path}")
        return True
    else:
        log_error(f"Error saving setup to {file_path}")
        return False


def load_battle_setup(file_path, available_designs):
    """
    Load battle setup from JSON file.

    Args:
        file_path: Source file path
        available_designs: List of available ship designs for lookup

    Returns:
        Tuple of (team1, team2) or (None, None) on error
    """
    try:
        data = load_json_required(file_path)

        def find_design(filename):
            for d in available_designs:
                if os.path.basename(d['path']) == filename:
                    return d
            return None

        new_team1 = []
        new_team2 = []

        def load_team(in_list, out_list):
            for item in in_list:
                d = find_design(item['design_file'])
                if d:
                    entry = {
                        'design': d,
                        'strategy': item['strategy']
                    }
                    if 'relative_position' in item:
                        entry['relative_position'] = item['relative_position']
                    if 'formation_id' in item:
                        entry['formation_id'] = item['formation_id']
                    if 'rotation_mode' in item:
                        entry['rotation_mode'] = item['rotation_mode']
                    out_list.append(entry)
                else:
                    log_warning(f"Design {item['design_file']} not found")

        load_team(data.get('team1', []), new_team1)
        load_team(data.get('team2', []), new_team2)

        log_info(f"Loaded setup from {file_path}")
        return new_team1, new_team2

    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        log_error(f"Error loading setup: {e}")
        return None, None
