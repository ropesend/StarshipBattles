"""Test-only UI builders for ``FleetReportWindow`` (PROJ-328 Phase A
Task A.4).

These pair with the production ``FleetReportLayoutBuilder`` at
``game/ui/screens/fleet_report_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol.

The cheap-state delegates (``view_model``, ``column_manager``,
``selection``, ``selected_ship``, layout-constant ints) are
constructed in Stage 1 of ``FleetReportWindow.__init__`` and survive
``bypass_init`` directly. The builders here are responsible only for
the *widget* slots that the production layout builder fills:
``sidebar_panel``, ``sidebar``, ``list_panel``, ``data_source``,
``virtual_table``, ``detail_panel``, ``ship_detail_panel``.

* ``NullFleetReportUiBuilder`` is a no-op builder. Use it when a test
  only exercises cheap state + delegate behaviour.

* ``MockFleetReportUiBuilder`` populates every widget slot with a
  ``MagicMock`` matching the legacy helper expectations. The
  ``ship_detail_panel.process_event`` mock returns ``False`` (matches
  the legacy helper).

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
and PROJ-325 PoC finding 2, the bypass branch invokes an explicitly
supplied ``ui_builder`` so these mocks are useful without per-call
wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.fleet_report_window import FleetReportWindow


class NullFleetReportUiBuilder:
    """No-op builder. Leaves widget slots at their Stage-1 ``None``
    placeholders."""

    def build(self, screen: "FleetReportWindow") -> None:
        return None


class MockFleetReportUiBuilder:
    """Builder that populates ``FleetReportWindow``'s widget slots with
    ``MagicMock`` instances.

    Cheap-state delegates (``view_model``, ``column_manager``,
    ``selection``) are real instances created by the constructor's
    Stage 1; this builder only fills in the widget slots so tests can
    exercise the public API (``sidebar.update_summary``,
    ``virtual_table.handle_click``, etc.) without a live pygame
    display.
    """

    def build(self, screen: "FleetReportWindow") -> None:
        screen.sidebar_panel = MagicMock(name="sidebar_panel")
        screen.sidebar = MagicMock(name="sidebar")
        screen.list_panel = MagicMock(name="list_panel")
        screen.data_source = MagicMock(name="data_source")
        screen.virtual_table = MagicMock(name="virtual_table")
        screen.detail_panel = MagicMock(name="detail_panel")

        ship_detail_panel = MagicMock(name="ship_detail_panel")
        # Default: detail panel does not consume events.
        ship_detail_panel.process_event = MagicMock(return_value=False)
        screen.ship_detail_panel = ship_detail_panel


__all__ = ["NullFleetReportUiBuilder", "MockFleetReportUiBuilder"]
