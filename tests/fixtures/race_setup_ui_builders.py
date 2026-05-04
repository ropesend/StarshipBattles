"""Test-only UI builders for ``RaceSetupScreen`` (PROJ-325 Phase 3).

These pair with the production ``RaceSetupUiBuilder`` at
``game/ui/screens/race_setup/ui_builder.py``. Both provide a ``build(screen)
-> None`` method matching the production builder protocol.

* ``NullRaceSetupUiBuilder`` is a no-op builder. Use it when a test only
  exercises cheap state + delegate behaviour and does not touch widget
  refs. The screen's ``_init_widget_refs()`` call has already populated
  every widget slot with ``None``/empty container, so the test sees an
  honest "widget tree absent, delegates present" instance.

* ``MockRaceSetupUiBuilder`` fills the widget slots with ``MagicMock``
  instances matching the shape the legacy ``_make_race_setup_screen``
  helper produced. Use it for tests that call ``screen.btn_save.show()``,
  iterate ``screen.step_panels``, or otherwise exercise widget-shaped
  behaviour without needing a real pygame display.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``),
this centralization replaces the previous pattern of repeating widget
mock-wiring inline in every test helper.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen


class NullRaceSetupUiBuilder:
    """No-op builder. Leaves every widget slot at the placeholder value
    set by ``RaceSetupScreen._init_widget_refs()``."""

    def build(self, screen: "RaceSetupScreen") -> None:
        return None


class MockRaceSetupUiBuilder:
    """Builder that populates ``RaceSetupScreen``'s widget slots with
    ``MagicMock`` instances matching the legacy helper's expectations.

    Mirrors the per-attribute wiring that ``_make_race_setup_screen``
    used to do inline (test_race_setup_screen.py:31-148 pre-PROJ-325).
    Centralized here so adding/renaming a widget slot only requires one
    edit instead of one per test.
    """

    NUM_TABS = 7

    def build(self, screen: "RaceSetupScreen") -> None:
        # Panel references (the seven tab panels + galleries).
        screen._summary_panel = MagicMock(name="summary_panel")
        screen._identity_panel = MagicMock(name="identity_panel")
        screen._environment_panel = MagicMock(name="environment_panel")
        screen._aptitudes_panel = MagicMock(name="aptitudes_panel")
        screen._description_panel = MagicMock(name="description_panel")
        screen._flag_gallery = MagicMock(name="flag_gallery")
        screen._portrait_gallery = MagicMock(name="portrait_gallery")
        screen._theme_gallery = MagicMock(name="theme_gallery")

        # Tab + step panel collections.
        screen.step_panels = [
            MagicMock(name=f"step_panel_{i}") for i in range(self.NUM_TABS)
        ]
        screen.tab_buttons = [
            MagicMock(name=f"tab_button_{i}") for i in range(self.NUM_TABS)
        ]
        for i, btn in enumerate(screen.tab_buttons):
            btn.tab_index = i

        # Bottom-bar action buttons.
        screen.btn_cancel = MagicMock(name="btn_cancel")
        screen.btn_save = MagicMock(name="btn_save")
        screen.btn_load = MagicMock(name="btn_load")
        screen.btn_randomize = MagicMock(name="btn_randomize")
        screen.btn_randomize_all = MagicMock(name="btn_randomize_all")

        # Misc widget refs.
        screen.error_label = MagicMock(name="error_label")
        screen.name_input = MagicMock(name="name_input")
        screen.ship_preview_scroll = MagicMock(name="ship_preview_scroll")

        # Renderer-internal widget refs that legacy tests reach into via
        # ``screen._renderer.<attr>``. Mirror the legacy helper.
        screen._renderer.save_update_dialog = None
        screen._renderer.btn_overwrite = None
        screen._renderer.btn_save_new = None
        screen._renderer.btn_save_cancel = None
        screen._renderer.llm_dialog_window = None
        screen._renderer.llm_dialog_btn_keep = None
        screen._renderer.llm_dialog_btn_stop = None
        screen._renderer.llm_dialog_field = ""
        screen._renderer.llm_error_popup = None
        screen._renderer.llm_error_popup_btn_ok = None
        screen._renderer._ship_preview = MagicMock(name="ship_preview")


__all__ = ["NullRaceSetupUiBuilder", "MockRaceSetupUiBuilder"]
