"""
JSON utility functions for consistent file loading and saving.

This module consolidates JSON loading/saving patterns used throughout the codebase,
providing consistent error handling and logging.

Usage:
    from game.core.json_utils import load_json, save_json, load_json_required

    # Safe loading with default
    data = load_json("config.json", default={})

    # Required loading (raises on error)
    data = load_json_required("critical_data.json")

    # Saving
    success = save_json("output.json", data)
"""
import json
from pathlib import Path
from typing import Any, Optional, Union

from game.core.logger import log_error, log_debug


def load_json(
    filepath: Union[str, Path],
    default: Optional[Any] = None,
    encoding: str = 'utf-8'
) -> Any:
    """
    Load JSON from a file with consistent error handling.

    Args:
        filepath: Path to the JSON file (string or Path object)
        default: Value to return if loading fails (default: None)
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed JSON data, or default if loading fails

    Examples:
        >>> data = load_json("config.json")
        >>> data = load_json("config.json", default={})
        >>> data = load_json(Path("data") / "config.json")
    """
    filepath = Path(filepath)

    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        log_debug(f"JSON file not found: {filepath}")
        return default
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON in {filepath}: {e}")
        return default
    except IOError as e:
        log_error(f"Error reading {filepath}: {e}")
        return default


def load_json_required(
    filepath: Union[str, Path],
    encoding: str = 'utf-8'
) -> Any:
    """
    Load JSON from a file, raising exceptions on failure.

    Use this for critical files that must exist and be valid.

    Args:
        filepath: Path to the JSON file (string or Path object)
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid

    Examples:
        >>> data = load_json_required("critical_config.json")
    """
    filepath = Path(filepath)

    with open(filepath, 'r', encoding=encoding) as f:
        return json.load(f)


def save_json(
    filepath: Union[str, Path],
    data: Any,
    indent: int = 2,
    encoding: str = 'utf-8',
    ensure_ascii: bool = False
) -> bool:
    """
    Save data to a JSON file with consistent error handling.

    Creates parent directories if they don't exist.

    Args:
        filepath: Path to the output file (string or Path object)
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
    filepath = Path(filepath)

    try:
        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        log_debug(f"Saved JSON to {filepath}")
        return True
    except IOError as e:
        log_error(f"Failed to save JSON to {filepath}: {e}")
        return False
    except TypeError as e:
        log_error(f"Failed to serialize data to JSON for {filepath}: {e}")
        return False
