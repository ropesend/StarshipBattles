"""
Battle setup data I/O operations.

Functions for scanning ship designs, formations, loading/saving battle setups,
and loading ships from configuration entries.

PROJ-43: Uses ShipFactory facade instead of direct Ship import.
PROJ-211: ShipFactory now requires registry_provider. Uses lazy initialization.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
import glob
# PROJ-382 Phase 3 (Pattern #12): bare ``json`` import preserved for the
# ``json.JSONDecodeError`` exception type used in the file-IO except
# clauses below. Persistence itself routes through json_utils.
import json
import pygame

import logging

logger = logging.getLogger(__name__)
from game.ui.services.ship_factory import ShipFactory
from game.core.json_utils import load_json, load_json_required, save_json
from game.core.paths import Paths
# PROJ-420: shared lazy GameRegistries cache (see game/core/registry_cache.py).
# Core cannot import UI, so the ShipFactory itself isn't cached here — it's
# constructed inline at the call site below. ShipFactory.__init__ only stores
# the registry_provider reference (no expensive work).
from game.core.registry_cache import get_cached_registries


def get_base_path() -> str:
    """Get the base path (root of project). Delegates to Paths.ROOT_DIR."""
    return Paths.ROOT_DIR


def scan_ship_designs() -> list[dict[str, Any]]:
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
                    'movement_policy': data.get('movement_policy', 'kite_max')
                })
        except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning(f"Failed to load ship design from '{filepath}': {e}")
    return designs


def load_ships_from_entries(team_entries, team_id, start_x, start_y, facing_angle=0) -> list["Ship"]:
    """
    Load ships from team entry list.

    PROJ-43: Uses ShipFactory facade instead of direct Ship import.
    PROJ-211: Uses lazy-initialized factory getter.

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
    # PROJ-420: construct ShipFactory inline using the shared registries
    # cache. ShipFactory.__init__ only stores the provider ref (no expensive
    # work), so this is cheap to repeat per call.
    factory = ShipFactory(registry_provider=get_cached_registries())

    for i, entry in enumerate(team_entries):
        data = load_json_required(entry['design']['path'])
        ship = factory.create_from_design(data)

        # Calculate position
        if 'relative_position' in entry:
            rx, ry = entry['relative_position']
            position = pygame.math.Vector2(start_x + rx, start_y + ry)
        else:
            position = pygame.math.Vector2(start_x, start_y + i * 5000)

        # Configure ship via factory
        factory.configure_ship(
            ship,
            position=position,
            angle=facing_angle,
            team_id=team_id,
            movement_policy=entry['strategy'],
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
        factory.setup_formation(ships, formation_data)

    return ships


def save_battle_setup(file_path, team1, team2) -> bool:
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

    def serialize_team(team_list, out_list) -> None:
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
        logger.info(f"Saved battle setup to {file_path}")
        return True
    else:
        logger.error(f"Error saving setup to {file_path}")
        return False


def load_battle_setup(file_path, available_designs) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | tuple[None, None]:
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

        def find_design(filename) -> Any:
            for d in available_designs:
                if os.path.basename(d['path']) == filename:
                    return d
            return None

        new_team1 = []
        new_team2 = []

        def load_team(in_list, out_list) -> None:
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
                    logger.warning(f"Design {item['design_file']} not found")

        load_team(data.get('team1', []), new_team1)
        load_team(data.get('team2', []), new_team2)

        logger.info(f"Loaded setup from {file_path}")
        return new_team1, new_team2

    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.error(f"Error loading setup: {e}")
        return None, None
