"""Selection strategies for table row selection.

Provides pluggable selection behavior:
- SingleSelect: One row at a time
- MultiSelect: Multiple rows with Ctrl+click
- NoSelect: No selection allowed
"""

from typing import Set


class ISelectionStrategy:
    """Base class for selection strategies.

    Subclasses must implement all methods.
    """

    def handle_click(self, index: int, ctrl_held: bool = False) -> Set[int]:
        """Handle a click on a row.

        Args:
            index: Row index that was clicked.
            ctrl_held: Whether Ctrl key was held during click.

        Returns:
            The new set of selected indices.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError

    def get_selected_indices(self) -> Set[int]:
        """Return the current set of selected indices.

        Returns:
            Set of selected row indices.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all selection.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError

    def set_selected(self, indices: Set[int]) -> None:
        """Set the selection to specific indices.

        Args:
            indices: Set of indices to select.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError


class SingleSelect(ISelectionStrategy):
    """Single selection strategy - only one row can be selected."""

    def __init__(self) -> None:
        self._selected: Set[int] = set()

    def handle_click(self, index: int, ctrl_held: bool = False) -> Set[int]:
        """Select only the clicked row, ignoring Ctrl modifier."""
        self._selected = {index}
        return self._selected.copy()

    def get_selected_indices(self) -> Set[int]:
        """Return the current selection."""
        return self._selected.copy()

    def clear(self) -> None:
        """Clear the selection."""
        self._selected = set()

    def set_selected(self, indices: Set[int]) -> None:
        """Set the selection to specific indices."""
        self._selected = indices.copy()


class MultiSelect(ISelectionStrategy):
    """Multiple selection strategy - Ctrl+click toggles, cannot remove last."""

    def __init__(self) -> None:
        self._selected: Set[int] = set()

    def handle_click(self, index: int, ctrl_held: bool = False) -> Set[int]:
        """Handle click with Ctrl modifier for toggling."""
        if ctrl_held:
            if index in self._selected:
                # Cannot remove the last selected item
                if len(self._selected) > 1:
                    self._selected.remove(index)
            else:
                self._selected.add(index)
        else:
            # Without Ctrl, replace entire selection
            self._selected = {index}
        return self._selected.copy()

    def get_selected_indices(self) -> Set[int]:
        """Return the current selection."""
        return self._selected.copy()

    def clear(self) -> None:
        """Clear the selection."""
        self._selected = set()

    def set_selected(self, indices: Set[int]) -> None:
        """Set the selection to specific indices."""
        self._selected = indices.copy()


class NoSelect(ISelectionStrategy):
    """No selection strategy - selection is always empty."""

    def handle_click(self, index: int, ctrl_held: bool = False) -> Set[int]:
        """Ignore all clicks."""
        return set()

    def get_selected_indices(self) -> Set[int]:
        """Always return empty set."""
        return set()

    def clear(self) -> None:
        """No-op."""
        pass

    def set_selected(self, indices: Set[int]) -> None:
        """Ignore set_selected calls."""
        pass
