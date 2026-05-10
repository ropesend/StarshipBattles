"""Test-only UI builders for ``SystemSelectionWindow`` (PROJ-329B Phase 1).

These pair with the production ``SystemSelectionUiBuilder`` at
``game/ui/screens/system_selection_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullSystemSelectionWindowUiBuilder`` is a no-op builder.

* ``MockSystemSelectionWindowUiBuilder`` populates ``screen.label``,
  ``screen.selection_list``, ``screen.btn_confirm``, ``screen.btn_cancel``
  with MagicMock instances pre-wired with safe defaults.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.system_selection_window import SystemSelectionWindow


class NullSystemSelectionWindowUiBuilder:
    """No-op builder. Leaves widget slots unset."""

    def build(self, screen: "SystemSelectionWindow") -> None:
        return None


class MockSystemSelectionWindowUiBuilder:
    """Builder that populates the widget slots with MagicMocks.

    Defaults:
    * ``selection_list.get_single_selection`` returns ``None``.
    * ``btn_confirm.check_pressed`` returns ``False``.
    * ``btn_cancel.check_pressed`` returns ``False``.
    * ``selection_list.item_list`` mirrors the Stage-1
      ``_sorted_display_list`` so existing tests reading
      ``window.selection_list.item_list`` still see the production
      shape (list of {"text": str} dicts).
    """

    def build(self, screen: "SystemSelectionWindow") -> None:
        for required in ("_sorted_display_list", "display_to_name"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockSystemSelectionWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.label = MagicMock(name="label")

        screen.selection_list = MagicMock(name="selection_list")
        screen.selection_list.get_single_selection.return_value = None
        # Mirror production shape: pygame_gui exposes item_list as a list
        # of dicts each with a "text" key.
        screen.selection_list.item_list = [
            {"text": display} for display in screen._sorted_display_list
        ]

        screen.btn_confirm = MagicMock(name="btn_confirm")
        screen.btn_confirm.check_pressed.return_value = False

        screen.btn_cancel = MagicMock(name="btn_cancel")
        screen.btn_cancel.check_pressed.return_value = False


__all__ = [
    "NullSystemSelectionWindowUiBuilder",
    "MockSystemSelectionWindowUiBuilder",
]
