"""Test-only UI builders for ``SaveSelectionWindow`` (PROJ-329B Phase 1).

These pair with the production ``SaveSelectionUiBuilder`` at
``game/ui/screens/save_selection_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullSaveSelectionWindowUiBuilder`` is a no-op builder.

* ``MockSaveSelectionWindowUiBuilder`` populates ``screen.saves_listbox``,
  ``screen.info_label``, ``screen.btn_load``, ``screen.btn_expand``,
  ``screen.btn_delete``, ``screen.btn_cancel`` with MagicMock instances
  pre-wired with safe defaults (action buttons start disabled to mirror
  production).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.save_selection_window import SaveSelectionWindow


class NullSaveSelectionWindowUiBuilder:
    """No-op builder. Leaves widget slots unset."""

    def build(self, screen: "SaveSelectionWindow") -> None:
        return None


class MockSaveSelectionWindowUiBuilder:
    """Builder that populates the widget slots with MagicMocks.

    Defaults:
    * ``saves_listbox.get_single_selection`` returns ``None``.
    * ``saves_listbox.item_list`` is an empty list (matches production
      shape: list of dicts with "text"/"selected" keys once populated).
    * ``btn_load`` / ``btn_expand`` / ``btn_delete`` start with
      ``is_enabled = False`` to mirror the production builder which
      calls ``.disable()`` on each.
    * ``btn_cancel`` starts enabled.
    """

    def build(self, screen: "SaveSelectionWindow") -> None:
        for required in ("saves_list", "list_item_mapping"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockSaveSelectionWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.saves_listbox = MagicMock(name="saves_listbox")
        screen.saves_listbox.get_single_selection.return_value = None
        screen.saves_listbox.item_list = []

        screen.info_label = MagicMock(name="info_label")

        # Helper: button mock honoring enable/disable like pygame_gui buttons.
        def _make_button(name: str, *, enabled: bool = True) -> MagicMock:
            btn = MagicMock(name=name)
            btn.is_enabled = enabled
            btn.check_pressed.return_value = False

            def _enable() -> None:
                btn.is_enabled = True

            def _disable() -> None:
                btn.is_enabled = False

            btn.enable.side_effect = _enable
            btn.disable.side_effect = _disable
            return btn

        screen.btn_load = _make_button("btn_load", enabled=False)
        screen.btn_expand = _make_button("btn_expand", enabled=False)
        screen.btn_delete = _make_button("btn_delete", enabled=False)
        screen.btn_cancel = _make_button("btn_cancel", enabled=True)


__all__ = [
    "NullSaveSelectionWindowUiBuilder",
    "MockSaveSelectionWindowUiBuilder",
]
