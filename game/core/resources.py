"""
Resource Registry Loading

Loads resource type definitions from data/resources.json into the RegistryManager.

Exceptions:
    FileNotFoundError: File not found (handled with fallback to defaults)
    json.JSONDecodeError: Invalid JSON (handled with fallback to defaults)
    PermissionError: Cannot read file (handled with fallback to defaults)
    TypeError: Malformed data structure (handled with fallback to defaults)
"""

import json
import os
from game.core.registry import RegistryManager
from game.core.json_utils import load_json_required
from game.core.logger import log_warning, log_info


def _get_default_resources() -> dict:
    """Return default resource definitions."""
    return {
        'fuel': {'id': 'fuel'},
        'energy': {'id': 'energy'},
        'ammo': {'id': 'ammo'},
    }


def _resolve_resource_path(filepath: str) -> str | None:
    """
    Resolve resource file path, trying relative then absolute paths.

    Args:
        filepath: Path to the resources JSON file (relative or absolute)

    Returns:
        Resolved absolute path if file exists, None otherwise
    """
    if os.path.exists(filepath):
        return filepath

    # Try absolute path based on this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))  # game/core -> game -> project
    abs_path = os.path.join(project_root, filepath)

    if os.path.exists(abs_path):
        return abs_path

    return None


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

    resolved_path = _resolve_resource_path(filepath)
    if resolved_path is None:
        return copy.deepcopy(_get_default_resources())

    try:
        data = load_json_required(resolved_path)

        result = {}
        # Parse resources list into dict keyed by ID
        for res_def in data.get('resources', []):
            res_id = res_def.get('id')
            if res_id:
                result[res_id] = copy.deepcopy(res_def)

        return result

    except FileNotFoundError:
        log_warning(f"Resources file not found: {resolved_path}, using defaults")
        return copy.deepcopy(_get_default_resources())
    except json.JSONDecodeError as e:
        log_warning(f"Invalid JSON in resources file {resolved_path}: {e}, using defaults")
        return copy.deepcopy(_get_default_resources())
    except (PermissionError, OSError) as e:
        log_warning(f"Cannot read resources file {resolved_path}: {e}, using defaults")
        return copy.deepcopy(_get_default_resources())
    except (TypeError, AttributeError) as e:
        # Malformed data structure (e.g., resources is not a list)
        log_warning(f"Malformed resources data in {resolved_path}: {e}, using defaults")
        return copy.deepcopy(_get_default_resources())


def load_resources(filepath: str = "data/resources.json") -> None:
    """
    Load resource definitions from JSON into the resource registry.

    This is a thin wrapper around load_resources_data() for backward
    compatibility. New code should prefer DI via load_resources_data().

    Args:
        filepath: Path to the resources JSON file. Defaults to data/resources.json.
    """
    resources = RegistryManager.instance().resources

    resolved_path = _resolve_resource_path(filepath)
    if resolved_path is None:
        log_warning(f"Resources file not found at {filepath}, using defaults")
        resources.update(_get_default_resources())
        return

    try:
        data = load_json_required(resolved_path)

        # Parse resources list into dict keyed by ID
        for res_def in data.get('resources', []):
            res_id = res_def.get('id')
            if res_id:
                resources[res_id] = res_def

        log_info(f"Loaded {len(resources)} resource types")

    except FileNotFoundError:
        log_warning(f"Resources file not found: {resolved_path}, using defaults")
        resources.update(_get_default_resources())
    except json.JSONDecodeError as e:
        log_warning(f"Invalid JSON in resources file {resolved_path}: {e}, using defaults")
        resources.update(_get_default_resources())
    except (PermissionError, OSError) as e:
        log_warning(f"Cannot read resources file {resolved_path}: {e}, using defaults")
        resources.update(_get_default_resources())
    except (TypeError, AttributeError) as e:
        # Malformed data structure (e.g., resources is not a list)
        log_warning(f"Malformed resources data in {resolved_path}: {e}, using defaults")
        resources.update(_get_default_resources())
