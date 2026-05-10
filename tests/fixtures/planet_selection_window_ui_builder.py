"""Test-only UI builders for ``PlanetSelectionWindow`` (PROJ-329A
Phase 2 Task 2.3).

These pair with the production ``PlanetSelectionUiBuilder`` at
``game/ui/screens/planet_selection_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullPlanetSelectionWindowUiBuilder`` is a no-op builder.

* ``MockPlanetSelectionWindowUiBuilder`` populates ``screen.label``,
  ``screen.selection_list``, ``screen.lbl_details``, ``screen.btn_select``
  with MagicMock instances. Honours ``screen._show_any_button`` —
  populates ``screen.btn_any`` only when the flag is True (matches
  production behaviour where the button is conditionally constructed).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.planet_selection_window import PlanetSelectionWindow


class NullPlanetSelectionWindowUiBuilder:
    """No-op builder. Leaves widget slots unset (except ``btn_any`` which
    Stage-1 wiring already initializes to None)."""

    def build(self, screen: "PlanetSelectionWindow") -> None:
        return None


class MockPlanetSelectionWindowUiBuilder:
    """Builder that populates the widget slots with MagicMocks.

    Defaults:
    * ``selection_list.get_single_selection`` returns ``None``.
    * ``btn_select.check_pressed`` returns ``False``.
    * ``btn_any.check_pressed`` returns ``False`` (only populated when
      ``screen._show_any_button`` is True).
    """

    def build(self, screen: "PlanetSelectionWindow") -> None:
        for required in ("planets", "_list_label", "_show_any_button"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockPlanetSelectionWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.label = MagicMock(name="label")
        screen.selection_list = MagicMock(name="selection_list")
        screen.selection_list.get_single_selection.return_value = None
        screen.lbl_details = MagicMock(name="lbl_details")
        screen.btn_select = MagicMock(name="btn_select")
        screen.btn_select.check_pressed.return_value = False

        if screen._show_any_button:
            screen.btn_any = MagicMock(name="btn_any")
            screen.btn_any.check_pressed.return_value = False
        else:
            screen.btn_any = None


__all__ = [
    "NullPlanetSelectionWindowUiBuilder",
    "MockPlanetSelectionWindowUiBuilder",
]
