"""
Resource Registry Loading

Loads resource type definitions from data/resources.json into the RegistryManager.
"""

import os
from game.core.registry import get_resource_registry
from game.core.json_utils import load_json_required
from game.core.logger import log_warning, log_info


def _get_default_resources() -> dict:
    """Return default resource definitions."""
    return {
        'fuel': {'id': 'fuel'},
        'energy': {'id': 'energy'},
        'ammo': {'id': 'ammo'},
    }


def load_resources_data(filepath: str = "data/resources.json") -> dict:
    """
    Pure function to load resource definitions from JSON.

    PROJ-38: Returns a dictionary of resource definitions without
    modifying any global state. Use this for DI patterns.

    Args:
        filepath: Path to the resources JSON file. Defaults to data/resources.json.

    Returns:
        Dict[str, dict]: Resource definitions keyed by resource ID
    """
    import copy

    if not os.path.exists(filepath):
        # Try absolute path based on this file's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(base_dir))  # game/core -> game -> project
        abs_path = os.path.join(project_root, filepath)

        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            # File doesn't exist - use defaults
            return copy.deepcopy(_get_default_resources())

    try:
        data = load_json_required(filepath)

        result = {}
        # Parse resources list into dict keyed by ID
        for res_def in data.get('resources', []):
            res_id = res_def.get('id')
            if res_id:
                result[res_id] = copy.deepcopy(res_def)

        return result

    except Exception as e:
        # Fall back to defaults on error
        return copy.deepcopy(_get_default_resources())


def load_resources(filepath: str = "data/resources.json") -> None:
    """
    Load resource definitions from JSON into the resource registry.

    This is a thin wrapper around load_resources_data() for backward
    compatibility. New code should prefer DI via load_resources_data().

    Args:
        filepath: Path to the resources JSON file. Defaults to data/resources.json.
    """
    resources = get_resource_registry()

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
            default_resources = _get_default_resources()
            resources.update(default_resources)
            return

    try:
        data = load_json_required(filepath)

        # Parse resources list into dict keyed by ID
        for res_def in data.get('resources', []):
            res_id = res_def.get('id')
            if res_id:
                resources[res_id] = res_def

        log_info(f"Loaded {len(resources)} resource types")

    except Exception as e:
        log_warning(f"Failed to load resources from {filepath}: {e}")
        # Fall back to defaults
        default_resources = _get_default_resources()
        resources.update(default_resources)
