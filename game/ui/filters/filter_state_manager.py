"""Base class for unified filter state management across all filter windows."""
from __future__ import annotations

from typing import Dict

from game.ui.filters.filter_state import FilterState


class FilterStateManager:
    """Manages tri-state filter values for a set of named attributes.

    Pure Python — no pygame dependency. Subclass or compose into
    window-specific filter managers.
    """

    def __init__(self, filter_definitions: Dict[str, FilterState]) -> None:
        self._filter_states: Dict[str, FilterState] = dict(filter_definitions)

    def get_state(self, attribute: str) -> FilterState:
        """Get the current filter state for an attribute."""
        return self._filter_states[attribute]

    def set_state(self, attribute: str, state: FilterState) -> None:
        """Set the filter state for an attribute. Raises KeyError if attribute unknown."""
        if attribute not in self._filter_states:
            raise KeyError(attribute)
        self._filter_states[attribute] = state

    def get_all_states(self) -> Dict[str, FilterState]:
        """Return a snapshot (copy) of all filter states."""
        return dict(self._filter_states)

    def reset_all(self) -> None:
        """Reset all filters to IGNORE (show all)."""
        for key in self._filter_states:
            self._filter_states[key] = FilterState.IGNORE

    def has_active_filters(self) -> bool:
        """Return True if any filter is not IGNORE."""
        return any(s is not FilterState.IGNORE for s in self._filter_states.values())

    def should_include(self, attribute: str, item_value: bool) -> bool:
        """Check whether an item passes this filter attribute.

        - IGNORE: always include (True)
        - YES: include only if item_value is True
        - NO: include only if item_value is False
        """
        state = self._filter_states[attribute]
        if state is FilterState.IGNORE:
            return True
        if state is FilterState.YES:
            return item_value
        return not item_value
