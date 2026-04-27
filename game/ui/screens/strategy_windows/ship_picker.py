"""Ship Picker placeholder (PROJ-198).

Currently a stub that auto-selects every ship and logs the choice. A real
ship-picker dialog with individual selection is a future enhancement —
filing this in its own module makes that TODO visible to anyone scanning
the package directory.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

import logging
from typing import Callable


class ShipPickerStub:
    """Auto-selecting placeholder for the future ship-picker dialog."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def show(
        self,
        ships,
        ability_name: str,
        on_selected: Callable,
    ) -> None:
        """Show ship picker dialog for multi-select.

        PROJ-198: Currently auto-selects all ships for simplicity.
        A full ship picker dialog with individual selection is a future
        enhancement.

        Args:
            ships: List of ships to pick from.
            ability_name: Ability name (for display/logging).
            on_selected: Callback with list of selected ship IDs.
        """
        self._logger.info(
            f"Ship picker ({ability_name}): Auto-selecting all {len(ships)} ships"
        )
        # Auto-select all ships - full picker UI is a future enhancement
        on_selected([s.id for s in ships])
