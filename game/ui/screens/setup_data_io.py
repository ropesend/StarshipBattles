"""
Battle setup data I/O operations.

Functions for scanning ship designs, formations, loading/saving battle setups,
and loading ships from configuration entries.
"""
import os
import glob
import pygame

from game.core.logger import log_info, log_warning, log_error
from game.simulation.entities.ship import Ship
from game.core.json_utils import load_json, load_json_required, save_json


def get_base_path():
    """Get the base path (root of project)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def scan_ship_designs():
    """Scan for available ship design JSON files in ships/ folder."""
    base_path = get_base_path()
    ships_folder = os.path.join(base_path, "ships")
    json_files = glob.glob(os.path.join(ships_folder, "*.json"))

    designs = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        # Skip config files
        if filename in ['builder_theme.json', 'component_presets.json']:
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
        except Exception:
            pass  # Skip invalid ship files
    return designs


def scan_formations():
    """Scan for available formation JSON files in data/formations directory."""
    base_path = get_base_path()
    formations_dir = os.path.join(base_path, "data", "formations")

    if not os.path.exists(formations_dir):
        os.makedirs(formations_dir)

    json_files = glob.glob(os.path.join(formations_dir, "*.json"))

    formations = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        if filename in ['builder_theme.json', 'component_presets.json']:
            continue

        try:
            data = load_json(filepath)
            if data and 'arrows' in data:
                formations.append({
                    'path': filepath,
                    'name': filename.replace('.json', ''),
                    'arrows': data['arrows']
                })
        except Exception:
            pass
    return formations


def load_ships_from_entries(team_entries, team_id, start_x, start_y, facing_angle=0):
    """
    Load ships from team entry list.

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
    formation_masters = {}

    for i, entry in enumerate(team_entries):
        data = load_json_required(entry['design']['path'])
        ship = Ship.from_dict(data)

        # Position Logic
        if 'relative_position' in entry:
            rx, ry = entry['relative_position']
            ship.position = pygame.math.Vector2(start_x + rx, start_y + ry)
        else:
            ship.position = pygame.math.Vector2(start_x, start_y + i * 5000)

        ship.angle = facing_angle
        ship.ai_strategy = entry['strategy']
        ship.source_file = os.path.basename(entry['design']['path'])
        ship.team_id = team_id
        ship.recalculate_stats()

        # Formation Linking
        if 'formation_id' in entry:
            f_id = entry['formation_id']
            if f_id not in formation_masters:
                formation_masters[f_id] = ship
            else:
                master = formation_masters[f_id]
                ship.formation_master = master
                master.formation_members.append(ship)

                diff = ship.position - master.position
                rot_mode = entry.get('rotation_mode', 'relative')
                ship.formation_rotation_mode = rot_mode

                if rot_mode == 'fixed':
                    ship.formation_offset = diff
                else:
                    ship.formation_offset = diff.rotate(-master.angle)

        ships.append(ship)
    return ships


def save_battle_setup(filepath, team1, team2):
    """
    Save battle setup to JSON file.

    Args:
        filepath: Destination file path
        team1: Team 1 entry list
        team2: Team 2 entry list

    Returns:
        True if successful
    """
    data = {
        "name": os.path.basename(filepath).replace(".json", ""),
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

    if save_json(filepath, data):
        log_info(f"Saved battle setup to {filepath}")
        return True
    else:
        log_error(f"Error saving setup to {filepath}")
        return False


def load_battle_setup(filepath, available_designs):
    """
    Load battle setup from JSON file.

    Args:
        filepath: Source file path
        available_designs: List of available ship designs for lookup

    Returns:
        Tuple of (team1, team2) or (None, None) on error
    """
    try:
        data = load_json_required(filepath)

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

        log_info(f"Loaded setup from {filepath}")
        return new_team1, new_team2

    except Exception as e:
        log_error(f"Error loading setup: {e}")
        return None, None
