"""Deep comparison utility for save/load round-trip verification.

Compares two dict representations of serialized game state and reports
field-level differences with full path tracking.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


@dataclass
class ComparisonResult:
    """A single difference found during deep comparison."""
    path: str
    expected: Any
    actual: Any
    message: str


def deep_compare(
    original: dict,
    loaded: dict,
    ignore_fields: Optional[Set[str]] = None,
    float_tolerance: float = 1e-10,
    unordered_lists: Optional[Set[str]] = None,
) -> List[ComparisonResult]:
    """Compare two dicts and return a list of differences.

    Args:
        original: The expected dict (from to_dict() before save).
        loaded: The actual dict (from to_dict() after load).
        ignore_fields: Set of dot-separated paths to skip (e.g. {"outer.b"}).
        float_tolerance: Maximum allowed absolute difference for floats.
        unordered_lists: Set of dot-separated paths where list order doesn't matter.

    Returns:
        List of ComparisonResult for each difference found. Empty list means identical.
    """
    ignore_fields = ignore_fields or set()
    unordered_lists = unordered_lists or set()
    results: List[ComparisonResult] = []
    _compare_values(original, loaded, "", results, ignore_fields, float_tolerance, unordered_lists)
    return results


def _compare_values(
    expected: Any,
    actual: Any,
    path: str,
    results: List[ComparisonResult],
    ignore_fields: Set[str],
    float_tolerance: float,
    unordered_lists: Set[str],
) -> None:
    """Recursively compare two values, appending differences to results."""
    if path in ignore_fields:
        return

    if isinstance(expected, dict) and isinstance(actual, dict):
        _compare_dicts(expected, actual, path, results, ignore_fields, float_tolerance, unordered_lists)
    elif isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
        # Treat tuples and lists as equivalent (JSON round-trip converts tuples to lists)
        _compare_lists(list(expected), list(actual), path, results, ignore_fields, float_tolerance, unordered_lists)
    elif isinstance(expected, float) and isinstance(actual, (int, float)):
        _compare_floats(expected, float(actual), path, results, float_tolerance)
    elif isinstance(actual, float) and isinstance(expected, (int, float)):
        _compare_floats(float(expected), actual, path, results, float_tolerance)
    elif expected != actual:
        results.append(ComparisonResult(
            path=path,
            expected=expected,
            actual=actual,
            message=f"Value differs: expected {expected!r}, got {actual!r}",
        ))


def _compare_dicts(
    expected: dict,
    actual: dict,
    path: str,
    results: List[ComparisonResult],
    ignore_fields: Set[str],
    float_tolerance: float,
    unordered_lists: Set[str],
) -> None:
    """Compare two dicts key by key."""
    all_keys = set(expected.keys()) | set(actual.keys())
    for key in sorted(all_keys):
        child_path = f"{path}.{key}" if path else key
        if child_path in ignore_fields:
            continue

        if key not in actual:
            results.append(ComparisonResult(
                path=child_path,
                expected=expected[key],
                actual=None,
                message=f"Missing key in loaded dict: {key!r}",
            ))
        elif key not in expected:
            results.append(ComparisonResult(
                path=child_path,
                expected=None,
                actual=actual[key],
                message=f"Extra/unexpected key in loaded dict: {key!r}",
            ))
        else:
            _compare_values(
                expected[key], actual[key], child_path,
                results, ignore_fields, float_tolerance, unordered_lists,
            )


def _compare_lists(
    expected: list,
    actual: list,
    path: str,
    results: List[ComparisonResult],
    ignore_fields: Set[str],
    float_tolerance: float,
    unordered_lists: Set[str],
) -> None:
    """Compare two lists, optionally ignoring order."""
    if path in unordered_lists:
        _compare_unordered(expected, actual, path, results)
        return

    if len(expected) != len(actual):
        results.append(ComparisonResult(
            path=path,
            expected=f"list of length {len(expected)}",
            actual=f"list of length {len(actual)}",
            message=f"List length differs: expected {len(expected)}, got {len(actual)}",
        ))
        # Still compare overlapping elements
        min_len = min(len(expected), len(actual))
    else:
        min_len = len(expected)

    for i in range(min_len):
        _compare_values(
            expected[i], actual[i], f"{path}[{i}]",
            results, ignore_fields, float_tolerance, unordered_lists,
        )


def _compare_unordered(
    expected: list,
    actual: list,
    path: str,
    results: List[ComparisonResult],
) -> None:
    """Compare two lists ignoring order (for sets serialized as lists)."""
    if len(expected) != len(actual):
        results.append(ComparisonResult(
            path=path,
            expected=f"list of length {len(expected)}",
            actual=f"list of length {len(actual)}",
            message=f"Unordered list length differs: expected {len(expected)}, got {len(actual)}",
        ))
        return

    sorted_expected = sorted(expected, key=_sort_key)
    sorted_actual = sorted(actual, key=_sort_key)
    if sorted_expected != sorted_actual:
        results.append(ComparisonResult(
            path=path,
            expected=sorted_expected,
            actual=sorted_actual,
            message=f"Unordered list contents differ",
        ))


def _sort_key(item: Any) -> Any:
    """Create a sort key that handles mixed types."""
    return (type(item).__name__, item)


def _compare_floats(
    expected: float,
    actual: float,
    path: str,
    results: List[ComparisonResult],
    tolerance: float,
) -> None:
    """Compare two floats with tolerance."""
    if abs(expected - actual) > tolerance:
        results.append(ComparisonResult(
            path=path,
            expected=expected,
            actual=actual,
            message=f"Float differs beyond tolerance ({tolerance}): expected {expected}, got {actual}",
        ))
