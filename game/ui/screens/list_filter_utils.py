"""Shared filter / sort utilities for VirtualTable list windows.

Extracted in PROJ-319 Phase 6 (DUP-X-17 / OpenCode review H3) to remove the
duplicated `sort_key` inner function that lived in `planet_list_filters.py`
and `star_list_filters.py`. Both filter files used identical fallback
column-sort logic (func / attr extraction with dotted-path support and an
empty-string fallback for missing attributes) — the only difference was
the lambda parameter name.

This is NOT shared with `ListDataSource._extract_value` (in
`list_data_source_base.py`) because the two helpers have different
return-type contracts: `_extract_value` returns a `str` for display
rendering, whereas the sort-key needs the typed underlying value (int,
float, etc.) so `list.sort(key=...)` orders correctly.
"""
from __future__ import annotations

from typing import Any, Callable, Dict


def make_attr_sort_key(col: Dict[str, Any]) -> Callable[[Any], Any]:
    """Build a sort-key callable for a column with `func` or `attr` extraction.

    Used by `sort_planets` and `sort_stars` for the fallback (non-id, non-name,
    non-type) column sort path. Returns the typed underlying value, NOT a
    string. Falls back to `""` (empty string) when the attribute path doesn't
    resolve, matching the original inline behavior so partial / missing data
    sorts to the bottom under both ascending and descending order.
    """
    def _key(entity: Any) -> Any:
        if "func" in col:
            return col["func"](entity)
        if "attr" in col:
            attrs = col["attr"].split(".")
            obj: Any = entity
            for a in attrs:
                if hasattr(obj, a):
                    obj = getattr(obj, a)
                else:
                    return ""
            return obj
        return ""
    return _key
