"""
Resource Registry Loading

Loads resource type definitions from data/resources.json into the RegistryManager.
"""

import os
from game.core.registry import RegistryManager
from game.core.json_utils import load_json_required
from game.core.logger import log_warning, log_info


def load_resources(filepath: str = "data/resources.json") -> None:
    """
    Load resource definitions from JSON into the resource registry.

    Args:
        filepath: Path to the resources JSON file. Defaults to data/resources.json.
    """
    registry = RegistryManager.instance()

    if not os.path.exists(filepath):
        # Try absolute path based on this file's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(base_dir))  # game/core -> game -> project
        abs_path = os.path.join(project_root, filepath)

        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            # File doesn't exist - use defaults
            log_warning(f"Resources file not found at {filepath}, using defaults")
            default_resources = {
                'fuel': {'id': 'fuel'},
                'energy': {'id': 'energy'},
                'ammo': {'id': 'ammo'},
            }
            registry.resources.update(default_resources)
            return

    try:
        data = load_json_required(filepath)

        # Parse resources list into dict keyed by ID
        for res_def in data.get('resources', []):
            res_id = res_def.get('id')
            if res_id:
                registry.resources[res_id] = res_def

        log_info(f"Loaded {len(registry.resources)} resource types")

    except Exception as e:
        log_warning(f"Failed to load resources from {filepath}: {e}")
        # Fall back to defaults
        default_resources = {
            'fuel': {'id': 'fuel'},
            'energy': {'id': 'energy'},
            'ammo': {'id': 'ammo'},
        }
        registry.resources.update(default_resources)
