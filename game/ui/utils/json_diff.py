"""
JSON Diff Algorithm - Computes structural differences between JSON objects.

This module provides utilities to compare two JSON structures and identify:
- Changed values (same key, different value)
- Added paths (key exists only in the "new" structure)
- Removed paths (key exists only in the "old" structure)

The diff algorithm traverses both structures recursively, building path strings
like "ships.0.current_hp" or "tick_count" to identify specific locations.

Usage:
    diff_paths = compute_json_diff(old_data, new_data)
    # Returns dict mapping paths to DiffResult status strings
"""
from __future__ import annotations

from typing import Any, Dict


class DiffResult:
    """Represents the diff status of a JSON path."""
    UNCHANGED = 'unchanged'
    CHANGED = 'changed'
    ADDED = 'added'
    REMOVED = 'removed'


# Keys to ignore in diff (always different between captures)
DIFF_IGNORE_KEYS = {'created_at'}


def compute_json_diff(initial: Any, final: Any, path: str = "") -> Dict[str, str]:
    """
    Compute differences between two JSON structures.

    Args:
        initial: The "old" JSON data to compare from
        final: The "new" JSON data to compare to
        path: Internal path prefix for recursive calls

    Returns:
        Dict mapping JSON paths to their diff status (DiffResult constants).
        Paths are like "ships.0.current_hp" or "tick_count".
    """
    diffs = {}

    if type(initial) != type(final):
        # Type changed - mark as changed
        diffs[path] = DiffResult.CHANGED
        return diffs

    if isinstance(initial, dict):
        all_keys = set(initial.keys()) | set(final.keys())
        for key in all_keys:
            # Skip keys that are always different (like timestamps)
            if key in DIFF_IGNORE_KEYS:
                continue
            child_path = f"{path}.{key}" if path else key
            if key not in initial:
                # Key added in final
                _mark_all_paths(final[key], child_path, DiffResult.ADDED, diffs)
            elif key not in final:
                # Key removed in final
                _mark_all_paths(initial[key], child_path, DiffResult.REMOVED, diffs)
            else:
                # Key exists in both - recurse
                child_diffs = compute_json_diff(initial[key], final[key], child_path)
                diffs.update(child_diffs)

    elif isinstance(initial, list):
        # For lists, compare by index
        max_len = max(len(initial), len(final))
        for i in range(max_len):
            child_path = f"{path}.{i}" if path else str(i)
            if i >= len(initial):
                _mark_all_paths(final[i], child_path, DiffResult.ADDED, diffs)
            elif i >= len(final):
                _mark_all_paths(initial[i], child_path, DiffResult.REMOVED, diffs)
            else:
                child_diffs = compute_json_diff(initial[i], final[i], child_path)
                diffs.update(child_diffs)

    else:
        # Primitive value
        if initial != final:
            diffs[path] = DiffResult.CHANGED

    return diffs


def _mark_all_paths(data: Any, path: str, status: str, diffs: Dict[str, str]) -> None:
    """
    Mark all paths in a data structure with the given status.

    Used to recursively mark entire subtrees as ADDED or REMOVED.

    Args:
        data: The JSON data subtree to mark
        path: The base path for this subtree
        status: The DiffResult status to assign
        diffs: The dict to populate with path -> status mappings
    """
    diffs[path] = status

    if isinstance(data, dict):
        for key, value in data.items():
            child_path = f"{path}.{key}"
            _mark_all_paths(value, child_path, status, diffs)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            child_path = f"{path}.{i}"
            _mark_all_paths(item, child_path, status, diffs)
