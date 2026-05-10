"""Test-only UI builders for ``FleetSelectionWindow`` (PROJ-329A Phase 2
Task 2.2).

These pair with the production ``FleetSelectionUiBuilder`` at
``game/ui/screens/fleet_selection_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullFleetSelectionWindowUiBuilder`` is a no-op builder. Use it
  when a test only exercises Stage-1 cheap state (display labels,
  label-to-fleet mapping, callback) and does not touch widget refs.

* ``MockFleetSelectionWindowUiBuilder`` populates ``screen.label``,
  ``screen.selection_list``, ``screen.btn_confirm``, ``screen.btn_cancel``
  with MagicMock instances. The selection list and buttons default to
  no selection / unpressed; tests override per-case.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.fleet_selection_window import FleetSelectionWindow


class NullFleetSelectionWindowUiBuilder:
    """No-op builder. Leaves widget slots unset."""

    def build(self, screen: "FleetSelectionWindow") -> None:
        return None


class MockFleetSelectionWindowUiBuilder:
    """Builder that populates the four widget slots with MagicMocks.

    Defaults:
    * ``selection_list.get_single_selection`` returns ``None``.
    * ``btn_confirm.check_pressed`` returns ``False``.
    * ``btn_cancel.check_pressed`` returns ``False``.

    Tests override per-case via ``window.btn_confirm.check_pressed.return_value = True``
    etc.
    """

    def build(self, screen: "FleetSelectionWindow") -> None:
        for required in ("_display_labels", "_label_to_fleet"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockFleetSelectionWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.label = MagicMock(name="label")
        screen.selection_list = MagicMock(name="selection_list")
        screen.selection_list.get_single_selection.return_value = None
        screen.btn_confirm = MagicMock(name="btn_confirm")
        screen.btn_confirm.check_pressed.return_value = False
        screen.btn_cancel = MagicMock(name="btn_cancel")
        screen.btn_cancel.check_pressed.return_value = False


__all__ = [
    "NullFleetSelectionWindowUiBuilder",
    "MockFleetSelectionWindowUiBuilder",
]
