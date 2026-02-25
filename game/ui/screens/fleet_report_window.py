"""
Fleet Report Window - Displays detailed fleet information, ship lists, and individual ship reports.

PROJ-03: Fleet Report Window feature implementation.
PROJ-44: Refactored to use FleetListViewModel, ColumnManager, and image scaling utilities.
PROJ-173 Phase 1: Extracted FleetReportSidebar and FleetListRenderer for god class decomposition.
PROJ-188 Phase 2: Migrated to VirtualTable + FleetDataSource + MultiSelect.
"""
import pygame
from pygame_gui.elements import UIWindow, UIPanel

from game.ui.config import UIConfig
from game.ui.screens.fleet_report_view_model import FleetListViewModel
from game.ui.components.table import VirtualTable, TableColumnManager, MultiSelect
from game.ui.screens.fleet_data_source import FleetDataSource, DEFAULT_FLEET_COLUMNS
from game.ui.screens.fleet_report_sidebar import FleetReportSidebar
from game.ui.panels.ship_detail_panel import ShipDetailPanel


class FleetReportWindow(UIWindow):
    """
    Window to view detailed fleet information including:
    - Fleet summary statistics (left panel)
    - Ship list with filtering/sorting (center)
    - Individual ship details with damage (right panel)
    """

    def __init__(self, rect, manager, fleet, empire=None, on_close_callback=None):
        """
        Initialize the Fleet Report Window.

        Args:
            rect: Window position and size (pygame.Rect)
            manager: pygame_gui UIManager
            fleet: Fleet object to display
            empire: Empire object for fleet management operations
            on_close_callback: Function to call when window is closed
        """
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=f"Fleet Report: {fleet.id}",
            resizable=True
        )

        self.fleet = fleet
        self.empire = empire
        self.on_close_callback = on_close_callback

        # --- Layout Constants ---
        self.sidebar_width = 300  # Left panel for summary + filters
        self.detail_width = 750   # Right panel for ship details (ShipDetailPanel)
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- State Managers ---
        self.view_model = FleetListViewModel(fleet.ships)
        self.column_manager = TableColumnManager(DEFAULT_FLEET_COLUMNS)
        self.selection = MultiSelect()
        self.selected_ship = None  # For detail panel (single ship when 1 selected)

        # --- Build UI ---
        self._init_layout()

        # Initial data load
        self.refresh_list()

    def _init_layout(self):
        """Initialize the three-panel layout."""
        window_rect = self.get_container().get_rect()
        content_height = window_rect.height - 50  # Account for title bar

        # 1. Left Sidebar (Summary + Filters)
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, content_height),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )
        self.sidebar = FleetReportSidebar(
            panel=self.sidebar_panel,
            manager=self.ui_manager,
            view_model=self.view_model,
            column_manager=self.column_manager,
            empire=self.empire,
            on_remove_selected=self._on_remove_selected_ships
        )

        # 2. Center Ship List
        list_width = window_rect.width - self.sidebar_width - self.detail_width - 10
        self.list_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, list_width, content_height),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Create data source and VirtualTable
        self.data_source = FleetDataSource(self.view_model)
        self.virtual_table = VirtualTable(
            panel=self.list_panel,
            manager=self.ui_manager,
            data_source=self.data_source,
            column_manager=self.column_manager,
            selection_strategy=self.selection,
            row_height=self.row_height,
            header_height=self.header_height
        )

        # 3. Right Detail Panel
        self.detail_panel = UIPanel(
            relative_rect=pygame.Rect(-self.detail_width, 0, self.detail_width, content_height),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        self._init_detail_panel()

    def _init_detail_panel(self):
        """Initialize the right detail panel with ShipDetailPanel."""
        panel_rect = self.detail_panel.get_relative_rect()
        detail_rect = pygame.Rect(0, 0, panel_rect.width, panel_rect.height)

        self.ship_detail_panel = ShipDetailPanel(
            manager=self.ui_manager,
            rect=detail_rect,
            container=self.detail_panel,
            on_remove_ship=self._on_remove_ship
        )

    def _swap_columns(self, col, direction):
        """Swap a column with its neighbor in the given direction."""
        col_id = col['id']
        if self.column_manager.swap_column(col_id, direction):
            # Rebuild UI via VirtualTable
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()

    def refresh_list(self):
        """Refresh the ship list with current fleet data."""
        # Update view model with current fleet ships
        self.view_model.update_ships(self.fleet.ships)

        # Update sidebar summary
        self.sidebar.update_summary(self.fleet)

        # Update scroll bar and visible rows via VirtualTable
        self.virtual_table.update_scroll_bar()
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()

    def process_event(self, event):
        """Handle UI events."""
        handled = super().process_event(event)

        # Forward events to ship detail panel (remove button, layer toggles)
        if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel.process_event(event):
            return True

        if event.type == pygame.USEREVENT:
            if hasattr(event, 'user_type') and event.user_type == 'ui_button_pressed':
                # Check for header clicks (sorting)
                obj_id = event.ui_element.object_ids[-1] if event.ui_element.object_ids else ""
                if obj_id.startswith("#header_"):
                    col_id = obj_id[8:]  # Remove "#header_" prefix
                    self._handle_header_click(col_id)
                    handled = True

        # Handle scroll events
        if hasattr(event, 'user_type') and event.user_type == 'ui_vertical_scroll_bar_moved':
            if event.ui_element == self.virtual_table.scroll_bar:
                self.virtual_table.update_visible_rows()
                handled = True

        # Handle mouse clicks on ship rows
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._handle_row_click(event.pos):
                handled = True

        return handled

    def _handle_row_click(self, pos):
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

    def _handle_header_click(self, col_id):
        """Handle clicking on a column header for sorting."""
        # Update sort state in both column_manager (for header display) and view_model (for sorting)
        self.column_manager.set_sort(col_id)
        self.view_model.set_sort(col_id)
        self.virtual_table.rebuild_headers()
        self.refresh_list()

    def select_ship(self, ship):
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

    def _update_detail_panel(self):
        """Update the detail panel with selected ship instance."""
        self.ship_detail_panel.update_ship(self.selected_ship)

    def _on_remove_ship(self, ship):
        """Handle remove single ship from fleet via ShipDetailPanel callback."""
        if not self.empire:
            # No empire, just remove ship without creating new fleet
            if self.fleet.remove_ship(ship):
                self._post_removal_refresh()
            return

        # Create a new fleet with the removed ship
        if ship in self.fleet.ships:
            self.fleet.remove_ship(ship)
            new_fleet = self._create_fleet_for_ships([ship])
            self.empire.add_fleet(new_fleet)
            self._post_removal_refresh()

    def _on_remove_selected_ships(self):
        """Remove all selected ships and create a new fleet with them."""
        if not self.empire:
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

        # Remove ships from source fleet
        for ship in ships_to_remove:
            self.fleet.remove_ship(ship)

        # Create one new fleet with all removed ships
        new_fleet = self._create_fleet_for_ships(ships_to_remove)
        self.empire.add_fleet(new_fleet)
        self._post_removal_refresh()

    def _create_fleet_for_ships(self, ships):
        """Create a new fleet containing the given ships at the source fleet's location."""
        from game.strategy.data.fleet import Fleet

        new_fleet_id = self.empire.get_next_fleet_id()
        new_fleet = Fleet(new_fleet_id, self.fleet.owner_id, self.fleet.location, speed=0)

        for ship in ships:
            new_fleet.add_ship(ship)

        return new_fleet

    def _post_removal_refresh(self):
        """Refresh UI state after ships have been removed."""
        self.selection.clear()
        self.selected_ship = None
        self.view_model.update_ships(self.fleet.ships)
        self._update_detail_panel()
        self.refresh_list()
        self.sidebar.update_remove_button(len(self.selection.get_selected_indices()))

    def update(self, time_delta: float):
        """Update UI elements and handle toggle button clicks."""
        super().update(time_delta)

        # Check sidebar button presses
        sidebar_actions = self.sidebar.check_button_presses()

        if sidebar_actions['filter_toggled']:
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

    def _toggle_filter(self, filter_id: str):
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

    def _toggle_column(self, col_id: str):
        """Toggle a column's visibility and update UI."""
        # Toggle visibility via TableColumnManager
        is_visible = self.column_manager.toggle_column(col_id)

        # Update sidebar button appearance
        self.sidebar.update_column_button(col_id, is_visible)

        # Rebuild headers and rows to reflect column changes
        self.virtual_table.rebuild_headers()
        self.virtual_table.rebuild_row_pool()
        self.refresh_list()

    def kill(self):
        """Clean up when window is closed."""
        # Clean up VirtualTable
        if hasattr(self, 'virtual_table') and self.virtual_table:
            self.virtual_table.kill()

        # Clean up ship detail panel
        if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:
            self.ship_detail_panel.kill()

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
