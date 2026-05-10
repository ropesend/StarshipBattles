"""Test-only UI builders for ``EventLogWindow`` (PROJ-329B Phase 3).

Production builder lives at
``game.ui.screens.event_log_window:EventLogUiBuilder``.

* ``NullEventLogWindowUiBuilder`` — no-op.

* ``MockEventLogWindowUiBuilder`` — populates filter buttons, sidebar
  panel, header panel, table panel, VirtualTable + DataSource +
  ColumnManager + Sidebar mocks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.event_log_window import EventLogWindow


class NullEventLogWindowUiBuilder:
    """No-op builder."""

    def build(self, screen: "EventLogWindow") -> None:
        return None


class MockEventLogWindowUiBuilder:
    """Populate filter buttons, sidebar, panel, table mocks."""

    def build(self, screen: "EventLogWindow") -> None:
        if not hasattr(screen, "all_events"):
            raise AssertionError(
                "MockEventLogWindowUiBuilder.build: screen has no "
                "`all_events` attribute. Build the screen via bypass_init "
                "AFTER Stage-1 cheap-state construction."
            )

        screen.sidebar_panel = MagicMock(name="sidebar_panel")
        screen.header_panel = MagicMock(name="header_panel")
        screen.table_panel = MagicMock(name="table_panel")

        def _filter_btn(name: str, *, selected: bool = False) -> MagicMock:
            btn = MagicMock(name=name)
            btn.is_selected = selected

            def _select(_b=btn) -> None:
                _b.is_selected = True

            def _unselect(_b=btn) -> None:
                _b.is_selected = False

            btn.select.side_effect = _select
            btn.unselect.side_effect = _unselect
            return btn

        screen.btn_all = _filter_btn("btn_all", selected=True)
        screen.btn_combat = _filter_btn("btn_combat")
        screen.btn_production = _filter_btn("btn_production")
        screen.btn_colonies = _filter_btn("btn_colonies")
        screen.btn_fleet_ops = _filter_btn("btn_fleet_ops")

        screen.filter_buttons = {
            "all": screen.btn_all,
            "combat": screen.btn_combat,
            "production": screen.btn_production,
            "colonies": screen.btn_colonies,
            "fleet_operations": screen.btn_fleet_ops,
        }

        screen.data_source = MagicMock(name="data_source")
        screen.data_source.get_row_count.return_value = 0
        screen.column_manager = MagicMock(name="column_manager")
        screen.virtual_table = MagicMock(name="virtual_table")
        screen.virtual_table.scroll_bar = MagicMock(name="scroll_bar")
        screen.sidebar = MagicMock(name="sidebar")
        screen.sidebar.handle_button_click = MagicMock(return_value=None)


__all__ = [
    "NullEventLogWindowUiBuilder",
    "MockEventLogWindowUiBuilder",
]
