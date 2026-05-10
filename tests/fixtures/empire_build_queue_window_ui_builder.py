"""Test-only UI builders for ``EmpireBuildQueueWindow`` (PROJ-329B Phase 2).

Production builder lives at
``game.ui.screens.empire_build_queue_window:EmpireBuildQueueUiBuilder``.

* ``NullEmpireBuildQueueWindowUiBuilder`` — no-op.

* ``MockEmpireBuildQueueWindowUiBuilder`` — populates ``screen.sidebar_panel``,
  ``screen._sidebar``, ``screen.main_panel``, ``screen._data_source``,
  ``screen._column_manager``, ``screen._selection``, ``screen._virtual_table``,
  ``screen.scroll_bar`` with MagicMocks. Subscribes nothing on the
  event bus (tests that need event-driven refresh wire it explicitly).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow


class NullEmpireBuildQueueWindowUiBuilder:
    """No-op builder."""

    def build(self, screen: "EmpireBuildQueueWindow") -> None:
        return None


class MockEmpireBuildQueueWindowUiBuilder:
    """Populate widget slots + sidebar mock with MagicMocks."""

    def build(self, screen: "EmpireBuildQueueWindow") -> None:
        for required in ("_event_bus", "_viewmodel", "_filter_mgr"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockEmpireBuildQueueWindowUiBuilder.build: screen "
                    f"has no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction."
                )

        screen.sidebar_panel = MagicMock(name="sidebar_panel")

        sidebar = MagicMock(name="_sidebar")
        sidebar.column_toggle_buttons = {}
        sidebar.tri_state_widgets = {}
        sidebar.search_entry = None
        sidebar.btn_apply_filters = None
        sidebar.handle_button_click = MagicMock(return_value=False)
        sidebar.check_tri_state_presses = MagicMock(return_value=None)
        screen._sidebar = sidebar

        screen.main_panel = MagicMock(name="main_panel")
        screen._data_source = MagicMock(name="_data_source")
        screen._column_manager = MagicMock(name="_column_manager")
        screen._selection = MagicMock(name="_selection")

        virtual_table = MagicMock(name="_virtual_table")
        scroll_bar = MagicMock(name="scroll_bar")
        scroll_bar.start_percentage = 0.0
        scroll_bar.visible_percentage = 1.0
        virtual_table.scroll_bar = scroll_bar
        screen._virtual_table = virtual_table
        screen.scroll_bar = scroll_bar


__all__ = [
    "NullEmpireBuildQueueWindowUiBuilder",
    "MockEmpireBuildQueueWindowUiBuilder",
]
