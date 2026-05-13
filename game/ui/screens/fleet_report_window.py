"""
Fleet Report Window - Displays detailed fleet information, ship lists, and individual ship reports.

PROJ-03: Fleet Report Window feature implementation.
PROJ-44: Refactored to use FleetListViewModel, ColumnManager, and image scaling utilities.
PROJ-173 Phase 1: Extracted FleetReportSidebar and FleetListRenderer for god class decomposition.
PROJ-188 Phase 2: Migrated to VirtualTable + FleetDataSource + MultiSelect.
PROJ-208 Phase 1: Refactored to use SplitFleetCommand via command pipeline.
PROJ-328 Phase A Task A.4: Two-stage construction. The existing
FleetListViewModel / FleetDataSource / VirtualTable / sidebar
plumbing is preserved verbatim; ``_init_layout`` is extracted into
``FleetReportLayoutBuilder`` so tests can swap in
``Mock{...}UiBuilder`` from
``tests/fixtures/fleet_report_ui_builder.py``.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional, TYPE_CHECKING

import pygame
from pygame_gui.elements import UIPanel

from game.ui.config import UIConfig
from game.ui.screens.fleet_report_view_model import FleetListViewModel
from game.ui.components.table import VirtualTable, TableColumnManager, MultiSelect
from game.ui.screens.fleet_data_source import FleetDataSource, DEFAULT_FLEET_COLUMNS
from game.ui.screens.fleet_report_sidebar import FleetReportSidebar
from game.ui.panels.ship_detail_panel import ShipDetailPanel
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


class FleetReportLayoutBuilder:
    """Production layout builder. Constructs the three-panel layout
    (sidebar, center list, right detail) and wires the
    ``FleetReportSidebar`` + ``VirtualTable`` + ``ShipDetailPanel``.

    The window is the local composition root: it owns the cheap state
    + delegates (``view_model``, ``column_manager``, ``selection``,
    ``data_source``) and exposes them to the layout builder. The
    layout builder reads them and creates panels/widgets.
    """

    def build(self, screen: "FleetReportWindow") -> None:
        window_rect = screen.get_container().get_rect()
        content_height = window_rect.height - 50  # account for title bar

        # 1. Left Sidebar (Summary + Filters)
        screen.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(
                0, 0, screen.sidebar_width, content_height),
            manager=screen.ui_manager,
            container=screen,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )
        screen.sidebar = FleetReportSidebar(
            panel=screen.sidebar_panel,
            manager=screen.ui_manager,
            view_model=screen.view_model,
            column_manager=screen.column_manager,
            empire=screen.empire,
            on_remove_selected=screen._on_remove_selected_ships,
        )

        # 2. Center Ship List
        list_width = (window_rect.width - screen.sidebar_width
                      - screen.detail_width - 10)
        screen.list_panel = UIPanel(
            relative_rect=pygame.Rect(
                screen.sidebar_width, 0, list_width, content_height),
            manager=screen.ui_manager,
            container=screen,
            anchors={'left': 'left', 'right': 'right',
                     'top': 'top', 'bottom': 'bottom'},
        )

        # Data source + VirtualTable.
        screen.data_source = FleetDataSource(screen.view_model)
        screen.virtual_table = VirtualTable(
            panel=screen.list_panel,
            manager=screen.ui_manager,
            data_source=screen.data_source,
            column_manager=screen.column_manager,
            selection_strategy=screen.selection,
            row_height=screen.row_height,
            header_height=screen.header_height,
        )

        # 3. Right Detail Panel
        screen.detail_panel = UIPanel(
            relative_rect=pygame.Rect(
                -screen.detail_width, 0, screen.detail_width, content_height),
            manager=screen.ui_manager,
            container=screen,
            anchors={'left': 'right', 'right': 'right',
                     'top': 'top', 'bottom': 'bottom'},
        )

        panel_rect = screen.detail_panel.get_relative_rect()
        detail_rect = pygame.Rect(0, 0, panel_rect.width, panel_rect.height)
        screen.ship_detail_panel = ShipDetailPanel(
            manager=screen.ui_manager,
            rect=detail_rect,
            container=screen.detail_panel,
            on_remove_ship=screen._on_remove_ship,
        )

        # Initial data load.
        screen.refresh_list()


class FleetReportWindow(StrategyModalWindow):
    """
    Window to view detailed fleet information including:
    - Fleet summary statistics (left panel)
    - Ship list with filtering/sorting (center)
    - Individual ship details with damage (right panel)

    PROJ-313: Migrated to ``StrategyModalWindow`` base class.
    PROJ-328 Phase A Task A.4: Two-stage construction. Cheap state
    (view_model, column_manager, selection) constructed before the
    bypass point so test fixtures see the real delegate graph.
    Layout/widget construction lives behind
    ``FleetReportLayoutBuilder``.

    Issue #28: opts into per-player UI view-state container so column
    toggles, sort order, and filter selections survive hot-seat
    rotation. Uses window reuse via ``open_for_fleet`` instead of
    kill-and-reconstruct so the central state swap has a live
    instance to ``apply_view_state`` against.
    """

    # Issue #28: opts into per-player UI view-state container.
    SNAPSHOT_SLOT: str = "fleet_report"

    def __init__(
        self,
        rect,
        manager,
        fleet,
        empire=None,
        *,
        window_manager: "StrategyWindowManager | None",
        on_close_callback=None,
        split_fleet_callback: Optional[Callable[[int, list], None]] = None,
        ui_builder: Optional[FleetReportLayoutBuilder] = None,
    ):
        """
        Initialize the Fleet Report Window.

        Args:
            rect: Window position and size (pygame.Rect)
            manager: pygame_gui UIManager
            fleet: Fleet object to display
            empire: Empire object for fleet management operations (used for remove button visibility)
            window_manager: PROJ-313 StrategyWindowManager (or None outside the strategy screen).
            on_close_callback: Function to call when window is closed
            split_fleet_callback: Callback to dispatch SplitFleetCommand(fleet_id, ship_instance_ids).
                When provided, ship removal goes through command pipeline.
            ui_builder: PROJ-328 — UI builder seam. Defaults to
                ``FleetReportLayoutBuilder``. Tests pass
                ``NullFleetReportUiBuilder`` /
                ``MockFleetReportUiBuilder`` from
                ``tests/fixtures/fleet_report_ui_builder.py``.
        """
        # ---- Stage 1: cheap state + delegates ----
        self.fleet = fleet
        self.empire = empire
        self.on_close_callback = on_close_callback
        self._split_fleet_callback = split_fleet_callback

        # Layout constants — pure ints, safe to set before super().__init__.
        self.sidebar_width = 300
        self.detail_width = 750
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # State managers — cheap collaborators in the PROJ-325 sense:
        # constructors are pure-Python, no pygame_gui widgets created.
        self.view_model = FleetListViewModel(fleet.ships)
        self.column_manager = TableColumnManager(DEFAULT_FLEET_COLUMNS)
        self.selection = MultiSelect()
        self.selected_ship = None  # for detail panel (single-ship mode)

        # Widget refs filled in by the layout builder; placeholders so
        # bypassed instances are honest.
        self.sidebar_panel = None
        self.sidebar = None
        self.list_panel = None
        self.data_source = None
        self.virtual_table = None
        self.detail_panel = None
        self.ship_detail_panel = None

        # ---- Stage 2: shell ----
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=f"Fleet Report: {fleet.id}",
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or FleetReportLayoutBuilder()).build(self)

    def _swap_columns(self, col, direction) -> None:
        """Swap a column with its neighbor in the given direction."""
        col_id = col['id']
        if self.column_manager.swap_column(col_id, direction):
            # Rebuild UI via VirtualTable
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()

    def refresh_list(self) -> None:
        """Refresh the ship list with current fleet data."""
        # Update view model with current fleet ships
        self.view_model.update_ships(self.fleet.ships)

        # Update sidebar summary
        self.sidebar.update_summary(self.fleet)

        # Update scroll bar and visible rows via VirtualTable
        self.virtual_table.update_scroll_bar()
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()

    def process_event(self, event) -> Any:
        """Handle UI events."""
        handled = super().process_event(event)

        # Forward events to ship detail panel (remove button, layer toggles)
        if self.ship_detail_panel and self.ship_detail_panel.process_event(event):
            return True

        # Handle scroll events
        if hasattr(event, 'user_type') and event.user_type == 'ui_vertical_scroll_bar_moved':
            if event.ui_element == self.virtual_table.scroll_bar:
                self.virtual_table.update_visible_rows()
                handled = True

        # Handle mouse clicks on ship rows
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._handle_row_click(event.pos):
                handled = True

        return handled

    def _handle_row_click(self, pos) -> bool:
        """Handle click on a ship row with Ctrl+click multi-select support."""
        mods = pygame.key.get_mods()
        ctrl_held = bool(mods & pygame.KMOD_CTRL)

        # Use VirtualTable to handle click (updates selection strategy)
        ship_index = self.virtual_table.handle_click(pos, ctrl_held)
        if ship_index < 0:
            return False

        # Update detail panel based on selection
        selected_indices = self.selection.get_selected_indices()
        if len(selected_indices) == 1:
            sole_idx = next(iter(selected_indices))
            self.selected_ship = self.data_source.get_ship_at_index(sole_idx)
        else:
            self.selected_ship = None

        self._update_detail_panel()
        self.sidebar.update_remove_button(len(selected_indices))
        return True


    def select_ship(self, ship) -> None:
        """Select a single ship to show in the detail panel (API for external callers)."""
        # Find the ship's index in filtered ships
        filtered_ships = self.view_model.get_filtered_ships()
        for i, s in enumerate(filtered_ships):
            if s is ship:
                self.selection.clear()
                self.selection.handle_click(i, ctrl_held=False)
                break
        else:
            self.selection.clear()

        self.selected_ship = ship
        self._update_detail_panel()
        self.sidebar.update_remove_button(len(self.selection.get_selected_indices()))
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()

    def _update_detail_panel(self) -> None:
        """Update the detail panel with selected ship instance."""
        self.ship_detail_panel.update_ship(self.selected_ship)

    def _on_remove_ship(self, ship) -> None:
        """Handle remove single ship from fleet via ShipDetailPanel callback.

        PROJ-208: Routes through SplitFleetCommand via command pipeline.
        """
        if not self.empire or not self._split_fleet_callback:
            return

        if ship in self.fleet.ships:
            result = self._split_fleet_callback(self.fleet.id, [ship.instance_id])
            if result and not result.is_valid:
                logger.warning(f"Remove ship failed: {result.message}")
                return
            self._post_removal_refresh()

    def _on_remove_selected_ships(self) -> None:
        """Remove all selected ships and create a new fleet with them.

        PROJ-208: Routes through SplitFleetCommand via command pipeline.
        """
        if not self.empire or not self._split_fleet_callback:
            return

        selected_indices = self.selection.get_selected_indices()
        if not selected_indices:
            return

        filtered_ships = self.view_model.get_filtered_ships()
        ships_to_remove = [
            filtered_ships[i] for i in sorted(selected_indices)
            if 0 <= i < len(filtered_ships)
        ]
        if not ships_to_remove:
            return

        ship_ids = [ship.instance_id for ship in ships_to_remove]
        result = self._split_fleet_callback(self.fleet.id, ship_ids)
        if result and not result.is_valid:
            logger.warning(f"Remove ships failed: {result.message}")
            return
        self._post_removal_refresh()

    def _post_removal_refresh(self) -> None:
        """Refresh UI state after ships have been removed."""
        self.selection.clear()
        self.selected_ship = None
        self.view_model.update_ships(self.fleet.ships)
        self._update_detail_panel()
        self.refresh_list()
        self.sidebar.update_remove_button(len(self.selection.get_selected_indices()))

    def update(self, time_delta: float) -> None:
        """Update UI elements and handle toggle button clicks."""
        super().update(time_delta)

        # Check sidebar button presses
        sidebar_actions = self.sidebar.check_button_presses()

        if sidebar_actions.get('filter_state_changed'):
            attr, new_state = sidebar_actions['filter_state_changed']
            self._apply_tri_state_filter(attr, new_state)
        elif sidebar_actions['filter_toggled']:
            self._toggle_filter(sidebar_actions['filter_toggled'])
        elif sidebar_actions['column_toggled']:
            self._toggle_column(sidebar_actions['column_toggled'])
        elif sidebar_actions['remove_selected']:
            self._on_remove_selected_ships()

        # Handle header arrows and sort clicks via VirtualTable
        header_actions = self.virtual_table.check_header_presses()
        if header_actions['swap_column']:
            col, direction = header_actions['swap_column']
            self._swap_columns(col, direction)
        elif header_actions['sort_column']:
            col_id = header_actions['sort_column']
            self.column_manager.set_sort(col_id)
            self.view_model.set_sort(col_id)
            self.virtual_table.rebuild_headers()
            self.refresh_list()

    def _toggle_filter(self, filter_id: str) -> None:
        """Toggle a filter state and update UI."""
        # Toggle the state via view model
        new_state = self.view_model.toggle_filter(filter_id)

        # Update sidebar button appearance
        self.sidebar.update_filter_button(filter_id, new_state)

        # Selection may now reference invalid indices, clear it
        self.selection.clear()
        self.selected_ship = None
        self._update_detail_panel()
        self.sidebar.update_remove_button(0)

        # Refresh the list with new filters
        self.refresh_list()

    def _apply_tri_state_filter(self, attribute: str, state) -> None:
        """Apply a tri-state filter change and refresh UI."""
        self.view_model.set_filter_state(attribute, state)

        # Selection may now reference invalid indices, clear it
        self.selection.clear()
        self.selected_ship = None
        self._update_detail_panel()
        self.sidebar.update_remove_button(0)

        self.refresh_list()

    def _toggle_column(self, col_id: str) -> None:
        """Toggle a column's visibility and update UI."""
        # Toggle visibility via TableColumnManager
        is_visible = self.column_manager.toggle_column(col_id)

        # Update sidebar button appearance
        self.sidebar.update_column_button(col_id, is_visible)

        # Rebuild headers and rows to reflect column changes
        self.virtual_table.rebuild_headers()
        self.virtual_table.rebuild_row_pool()
        self.refresh_list()

    # -----------------------------------------------------------------------
    # Issue #28: window reuse (Pattern §29) + per-player view-state opt-in
    # -----------------------------------------------------------------------

    def on_close_window_button_pressed(self) -> None:
        """X-button close hides for reuse."""
        self.hide()

    def request_close(self) -> None:
        """Esc-key close hides for reuse."""
        self.hide()

    def open_for_fleet(self, fleet, empire=None) -> None:
        """Rebind fleet (and optionally empire), refresh, show.

        Called by ``FleetReportRegistrar.open()`` on slot reuse. Per-
        player column visibility / sort / filter state was already
        swapped onto this instance by ``StrategyGameStateManager`` at
        turn-start, so this method only handles the fleet rebind.
        """
        self.fleet = fleet
        if empire is not None:
            self.empire = empire
        self.selected_ship = None
        self.selection.clear()
        if self.virtual_table is not None:
            self.refresh_list()
        self.show()

    def capture_view_state(self) -> dict:
        """Snapshot column visibility + order + sort + filter state.

        ``column_manager`` is the source of truth for column state
        (accessed via ``get_columns()``). ``view_model`` owns the
        filter state via its FilterStateManager.
        """
        cm_cols = self.column_manager.get_columns()
        cols = [
            {"id": col["id"], "visible": col.get("visible", True)}
            for col in cm_cols
        ]
        filters = {}
        fm = getattr(self.view_model, "_filter_mgr", None)
        if fm is not None and hasattr(fm, "get_all_states"):
            filters = {
                key: state.value for key, state in fm.get_all_states().items()
            }
        return {
            "columns": cols,
            "sort_column_id": getattr(self.column_manager, "sort_column_id", None),
            "sort_descending": getattr(self.column_manager, "sort_descending", False),
            "filters": filters,
        }

    def apply_view_state(self, state: dict | None) -> None:
        """Restore previously-captured snapshot. ``None`` is a no-op."""
        if state is None:
            return

        cm_cols = self.column_manager.get_columns()
        saved_cols = state.get("columns") or []
        if saved_cols:
            current_map = {c["id"]: c for c in cm_cols}
            new_cols = []
            for item in saved_cols:
                col = current_map.get(item["id"])
                if col is not None:
                    col["visible"] = item.get("visible", True)
                    new_cols.append(col)
                    del current_map[item["id"]]
            new_cols.extend(current_map.values())
            # ``get_columns()`` returns the live ``_columns`` reference,
            # so mutating in place is sufficient — but the reorder requires
            # the underlying list to be replaced.
            cm_cols[:] = new_cols

        sort_col = state.get("sort_column_id")
        if sort_col is not None:
            self.column_manager.sort_column_id = sort_col
            self.column_manager.sort_descending = state.get("sort_descending", False)

        from game.ui.filters.filter_state import FilterState
        fm = getattr(self.view_model, "_filter_mgr", None)
        if fm is not None and hasattr(fm, "set_state"):
            for key, raw in (state.get("filters") or {}).items():
                try:
                    fm.set_state(key, FilterState(raw))
                except (ValueError, KeyError):
                    continue

    def kill(self) -> None:
        """Clean up when window is closed."""
        # Clean up VirtualTable
        if self.virtual_table:
            self.virtual_table.kill()

        # Clean up ship detail panel
        if self.ship_detail_panel:
            self.ship_detail_panel.kill()

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
