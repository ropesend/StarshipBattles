"""Test-only UI builders for ``RaceBrowserDialog`` (PROJ-329B Phase 1).

These pair with the production ``RaceBrowserDialogUiBuilder`` at
``game/ui/screens/race_browser_dialog.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullRaceBrowserDialogUiBuilder`` is a no-op builder.

* ``MockRaceBrowserDialogUiBuilder`` populates ``screen.scroll_container``,
  ``screen.btn_cancel``, ``screen.btn_load``, ``screen.no_races_label``
  with MagicMock instances. ``btn_load`` starts disabled to mirror the
  production builder. ``no_races_label`` starts hidden.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.race_browser_dialog import RaceBrowserDialog


class NullRaceBrowserDialogUiBuilder:
    """No-op builder. Leaves widget slots unset."""

    def build(self, screen: "RaceBrowserDialog") -> None:
        return None


class MockRaceBrowserDialogUiBuilder:
    """Builder that populates the widget slots with MagicMocks.

    Defaults:
    * ``btn_load`` starts with ``is_enabled = False`` (production calls
      ``.disable()``). ``enable()`` / ``disable()`` flip this state.
    * ``btn_cancel`` starts enabled.
    * ``no_races_label.is_visible`` starts ``False`` (production calls
      ``.hide()``). ``show()`` / ``hide()`` flip the flag.
    """

    def build(self, screen: "RaceBrowserDialog") -> None:
        for required in ("race_library", "_asset_loader", "race_rows"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockRaceBrowserDialogUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.scroll_container = MagicMock(name="scroll_container")

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

        screen.btn_cancel = _make_button("btn_cancel", enabled=True)
        screen.btn_load = _make_button("btn_load", enabled=False)

        no_races_label = MagicMock(name="no_races_label")
        no_races_label.is_visible = False

        def _show() -> None:
            no_races_label.is_visible = True

        def _hide() -> None:
            no_races_label.is_visible = False

        no_races_label.show.side_effect = _show
        no_races_label.hide.side_effect = _hide
        screen.no_races_label = no_races_label


__all__ = [
    "NullRaceBrowserDialogUiBuilder",
    "MockRaceBrowserDialogUiBuilder",
]
