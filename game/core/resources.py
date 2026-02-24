"""
Resource Registry Loading

Loads resource type definitions from data/resources.json.

Exceptions:
    FileNotFoundError: File not found (handled with fallback to defaults)
    json.JSONDecodeError: Invalid JSON (handled with fallback to defaults)
    PermissionError: Cannot read file (handled with fallback to defaults)
    TypeError: Malformed data structure (handled with fallback to defaults)
"""

import json
import logging
import os
from typing import Optional
from game.core.json_utils import load_json_required
from game.core.constants import ResourceType

logger = logging.getLogger(__name__)
from game.core.paths import Paths


def _get_default_resources() -> dict:
    """Return default resource definitions."""
    return {
        ResourceType.FUEL: {'id': ResourceType.FUEL},
        ResourceType.ENERGY: {'id': ResourceType.ENERGY},
        ResourceType.AMMO: {'id': ResourceType.AMMO},
    }


def _resolve_resource_path(file_path: str) -> Optional[str]:
    """
    Resolve resource file path using Paths.ROOT_DIR for project root.

    Args:
        file_path: Path to the resources JSON file (relative or absolute)

    Returns:
        Resolved absolute path if file exists, None otherwise
    """
    if os.path.exists(file_path):
        return file_path

    # Try absolute path using centralized Paths configuration
    abs_path = os.path.join(Paths.ROOT_DIR, file_path)

    if os.path.exists(abs_path):
        return abs_path

    return None


def load_resources_data(file_path: str = "data/resources.json") -> dict:
    """
    Pure function to load resource definitions from JSON.

    PROJ-38: Returns a dictionary of resource definitions without
    modifying any global state. Use this for DI patterns.

    Args:
        file_path: Path to the resources JSON file. Defaults to data/resources.json.

    Returns:
        Dict[str, dict]: Resource definitions keyed by resource ID
    """
    import copy

    resolved_path = _resolve_resource_path(file_path)
    if resolved_path is None:
        logger.warning(f"Resources file not found at {file_path}, using defaults")
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
        logger.warning(f"Resources file not found: {resolved_path}, using defaults")
        return copy.deepcopy(_get_default_resources())
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in resources file {resolved_path}: {e}, using defaults")
        return copy.deepcopy(_get_default_resources())
    except (PermissionError, OSError) as e:
        logger.warning(f"Cannot read resources file {resolved_path}: {e}, using defaults")
        return copy.deepcopy(_get_default_resources())
    except (TypeError, AttributeError) as e:
        # Malformed data structure (e.g., resources is not a list)
        logger.warning(f"Malformed resources data in {resolved_path}: {e}, using defaults")
        return copy.deepcopy(_get_default_resources())
