"""
JSON utility functions for consistent file loading and saving.

This module is the CANONICAL location for file-based JSON operations in game/.
All JSON file I/O should use these functions for consistent error handling.

Usage:
    from game.core.json_utils import load_json, save_json, load_json_required
    from game.core.json_utils import deserialize_list

    # Safe loading with default
    data = load_json("config.json", default={})

    # Required loading (raises on error)
    data = load_json_required("critical_data.json")

    # Saving
    success = save_json("output.json", data)

    # Resilient list deserialization (skips invalid items)
    planets = deserialize_list(
        data.get('planets', []),
        Planet.from_dict,
        entity_name='planet',
        parent_name=f"StarSystem '{system.name}'"
    )

Exceptions:
    load_json_required raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid

    load_json and save_json return defaults/False on error (no exceptions raised)

Note:
    Do NOT use json.load/json.dump directly for file operations in game/.
    Use these functions instead for consistent error handling and logging.
"""
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)


# =============================================================================
# Serializable Type Registry (PROJ-223)
# =============================================================================

_SERIALIZABLE_REGISTRY: Dict[str, type] = {}


def register_serializable(type_name: str = None):
    """Decorator that registers a class as a serializable type.

    Optional — not required for serialization to work. Supports gradual adoption.

    Args:
        type_name: Custom registry key. Defaults to cls.__name__.

    Returns:
        The class unchanged.
    """
    def decorator(cls):
        key = type_name if type_name is not None else cls.__name__
        _SERIALIZABLE_REGISTRY[key] = cls
        return cls
    return decorator


def get_serializable_registry() -> Dict[str, type]:
    """Return a copy of the serializable type registry."""
    return dict(_SERIALIZABLE_REGISTRY)


def load_json(
    file_path: Union[str, Path],
    default: Optional[Any] = None,
    encoding: str = 'utf-8'
) -> Any:
    """
    Load JSON from a file with consistent error handling.

    Args:
        file_path: Path to the JSON file (string or Path object)
        default: Value to return if loading fails (default: None)
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed JSON data, or default if loading fails

    Examples:
        >>> data = load_json("config.json")
        >>> data = load_json("config.json", default={})
        >>> data = load_json(Path("data") / "config.json")
    """
    file_path = Path(file_path)

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug(f"JSON file not found: {file_path}")
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return default
    except PermissionError as e:
        logger.error(f"Permission denied reading {file_path}: {e}")
        return default
    except OSError as e:
        logger.error(f"Error reading {file_path}: {e}")
        return default


def load_json_required(
    file_path: Union[str, Path],
    encoding: str = 'utf-8'
) -> Any:
    """
    Load JSON from a file, raising exceptions on failure.

    Use this for critical files that must exist and be valid.

    Args:
        file_path: Path to the JSON file (string or Path object)
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid

    Examples:
        >>> data = load_json_required("critical_config.json")
    """
    file_path = Path(file_path)

    with open(file_path, 'r', encoding=encoding) as f:
        return json.load(f)


def save_json(
    file_path: Union[str, Path],
    data: Any,
    indent: int = 2,
    encoding: str = 'utf-8',
    ensure_ascii: bool = False
) -> bool:
    """
    Save data to a JSON file with consistent error handling.

    Creates parent directories if they don't exist.

    Args:
        file_path: Path to the output file (string or Path object)
        data: Data to serialize to JSON
        indent: Indentation level for pretty printing (default: 2)
        encoding: File encoding (default: utf-8)
        ensure_ascii: If True, escape non-ASCII characters (default: False)

    Returns:
        True if save succeeded, False otherwise

    Examples:
        >>> save_json("output.json", {"key": "value"})
        True
        >>> save_json(Path("data") / "output.json", data, indent=4)
        True
    """
    file_path = Path(file_path)

    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: serialize to temp file first, then rename.
        # If serialization or writing fails, the original file is untouched.
        tmp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        with open(tmp_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        # Replace original with completed temp file (atomic on most OS)
        tmp_path.replace(file_path)

        logger.debug(f"Saved JSON to {file_path}")
        return True
    except PermissionError as e:
        logger.error(f"Permission denied writing to {file_path}: {e}")
        return False
    except OSError as e:
        logger.error(f"Failed to save JSON to {file_path}: {e}")
        return False
    except TypeError as e:
        logger.error(f"Failed to serialize data to JSON for {file_path}: {e}")
        # Clean up temp file if serialization failed
        tmp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        tmp_path.unlink(missing_ok=True)
        return False


# Type variable for generic deserializer return type
T = TypeVar('T')


def deserialize_list(
    items: Optional[List[dict]],
    deserializer: Callable[[dict], T],
    entity_name: str,
    parent_name: str
) -> List[T]:
    """
    Deserialize a list of items with resilient error handling.

    PROJ-204 Phase 4: Consolidates 11+ identical error-handling loops (CQ-22).

    Invalid items are skipped with a warning log, allowing resilient degradation
    when loading saved game data. This ensures partial save files can still be
    loaded rather than failing entirely.

    Args:
        items: List of dicts to deserialize (None treated as empty list)
        deserializer: Function that converts a dict to the target type
        entity_name: Name of entity type for logging (e.g., 'planet', 'star')
        parent_name: Name of parent object for logging context (e.g., "StarSystem 'Alpha'")

    Returns:
        List of successfully deserialized items (invalid items omitted)

    Example:
        planets = deserialize_list(
            data.get('planets', []),
            Planet.from_dict,
            entity_name='planet',
            parent_name=f"StarSystem '{system.name}'"
        )
    """
    from game.core.exceptions import PersistenceException

    if items is None:
        return []

    result = []
    for i, item in enumerate(items):
        try:
            result.append(deserializer(item))
        except (PersistenceException, KeyError, TypeError, ValueError) as e:
            logger.warning(
                f"{parent_name}: skipping invalid {entity_name} at index {i} - "
                f"{type(e).__name__}: {e}"
            )

    return result
