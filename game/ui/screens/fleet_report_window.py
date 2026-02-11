"""
Fleet Report Window - Displays detailed fleet information, ship lists, and individual ship reports.

PROJ-03: Fleet Report Window feature implementation.
PROJ-44: Refactored to use FleetListViewModel, ColumnManager, and image scaling utilities.
"""
import pygame
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIVerticalScrollBar, UIImage

from game.core.config import UIConfig
from game.ui.screens.fleet_report_filters import calculate_fleet_stats
from game.ui.screens.fleet_report_view_model import FleetListViewModel
from game.ui.screens.column_manager import ColumnManager
from game.ui.utils import scale_image_by_visible_portion, scale_image_to_fit
from game.ui.panels.design_report_panel import DesignReportPanel
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.assets import ShipThemeManager


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
        self.detail_width = 750   # Right panel for ship details (DesignReportPanel)
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- State Managers ---
        self.view_model = FleetListViewModel(fleet.ships)
        self.column_manager = ColumnManager()
        self._design_loader = DesignLoaderAdapter()

        # Selection state - multi-select support
        self.selected_indices: set = set()  # Indices into filtered_ships
        self.selected_ship = None  # For detail panel (single ship when len(selected_indices) == 1)

        # Image cache for ship portraits and top-down sprites
        self._image_cache = {}  # {(ship_id, image_type): pygame.Surface}

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
        self._init_sidebar()

        # 2. Center Ship List
        list_width = window_rect.width - self.sidebar_width - self.detail_width - 10
        self.list_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, list_width, content_height),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        self._init_ship_list()

        # 3. Right Detail Panel
        self.detail_panel = UIPanel(
            relative_rect=pygame.Rect(-self.detail_width, 0, self.detail_width, content_height),
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        self._init_detail_panel()

    def _init_sidebar(self):
        """Initialize the left sidebar with summary and filters."""
        y = 10

        # --- Combat Stats Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="COMBAT STATUS",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 28

        # Ship count
        self.lbl_ship_count = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Ships: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Average HP
        self.lbl_avg_hp = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Avg HP: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Damaged count
        self.lbl_damaged = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Damaged: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Derelict count
        self.lbl_derelict = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Derelict: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 32

        # --- Logistics Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="LOGISTICS",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 28

        # Total tonnage
        self.lbl_tonnage = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Tonnage: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Fleet speed
        self.lbl_speed = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Speed: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Fuel
        self.lbl_fuel = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Fuel: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Energy
        self.lbl_energy = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Energy: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 32

        # --- Movement Capabilities Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="MOVEMENT",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 28

        # Warp Capable
        self.lbl_warp_capable = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Warp: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Fuel Endurance
        self.lbl_fuel_endurance = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Fuel Range: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 24

        # Warp Jumps Remaining
        self.lbl_warp_jumps = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Warp Jumps: --",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 32

        # --- Filters Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 30),
            text="FILTERS",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 35

        # Status filter checkboxes
        self.filter_buttons = {}
        filter_configs = [
            ('damaged', 'Damaged'),
            ('undamaged', 'Undamaged'),
            ('derelict', 'Derelict'),
            ('destroyed', 'Destroyed'),
        ]

        for filter_id, label in filter_configs:
            is_on = self.view_model.is_filter_enabled(filter_id)
            btn_text = f"[{label}]" if is_on else label
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                text=btn_text,
                manager=self.ui_manager,
                container=self.sidebar_panel,
                object_id=f"#filter_{filter_id}"
            )
            if is_on:
                btn.select()
            self.filter_buttons[filter_id] = btn
            y += 30

        y += 10

        # Warp capability filter section
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="WARP CAPABILITY",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 28

        warp_filter_configs = [
            ('warp_capable', 'Warp Capable'),
            ('not_warp_capable', 'Not Warp Capable'),
        ]

        for filter_id, label in warp_filter_configs:
            is_on = self.view_model.is_filter_enabled(filter_id)
            btn_text = f"[{label}]" if is_on else label
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                text=btn_text,
                manager=self.ui_manager,
                container=self.sidebar_panel,
                object_id=f"#filter_{filter_id}"
            )
            if is_on:
                btn.select()
            self.filter_buttons[filter_id] = btn
            y += 30

        y += 10

        # Spaceyard filter section
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="SPACEYARD",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 28

        spaceyard_filter_configs = [
            ('has_spaceyard', 'Has Yard'),
            ('no_spaceyard', 'No Yard'),
        ]

        for filter_id, label in spaceyard_filter_configs:
            is_on = self.view_model.is_filter_enabled(filter_id)
            btn_text = f"[{label}]" if is_on else label
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                text=btn_text,
                manager=self.ui_manager,
                container=self.sidebar_panel,
                object_id=f"#filter_{filter_id}"
            )
            if is_on:
                btn.select()
            self.filter_buttons[filter_id] = btn
            y += 30

        y += 10

        # Cargo filter section
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="CARGO",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 28

        cargo_filter_configs = [
            ('has_cargo', 'Has Cargo'),
            ('no_cargo', 'No Cargo'),
        ]

        for filter_id, label in cargo_filter_configs:
            is_on = self.view_model.is_filter_enabled(filter_id)
            btn_text = f"[{label}]" if is_on else label
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                text=btn_text,
                manager=self.ui_manager,
                container=self.sidebar_panel,
                object_id=f"#filter_{filter_id}"
            )
            if is_on:
                btn.select()
            self.filter_buttons[filter_id] = btn
            y += 30

        y += 10

        # --- Column Configuration Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 30),
            text="COLUMNS",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 35

        # Column visibility toggles
        self.column_buttons = {}
        for col in self.column_manager.get_toggleable_columns():
            col_id = col['id']
            title = col['title'] or col_id
            is_visible = col.get('visible', True)
            btn_text = f"[x] {title}" if is_visible else f"[ ] {title}"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                text=btn_text,
                manager=self.ui_manager,
                container=self.sidebar_panel,
                object_id=f"#column_{col_id}"
            )
            btn.col_ref = col  # Store reference to column config
            self.column_buttons[col_id] = btn
            y += 30

        y += 20

        # --- Actions Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 30),
            text="ACTIONS",
            manager=self.ui_manager,
            container=self.sidebar_panel
        )
        y += 35

        # Remove Selected button - creates new fleet from removed ships
        self.btn_remove_selected = UIButton(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 32),
            text="Remove Selected",
            manager=self.ui_manager,
            container=self.sidebar_panel,
            object_id="#btn_remove_selected"
        )
        self.btn_remove_selected.disable()  # Disabled until selection exists

    def _update_remove_button(self):
        """Enable/disable remove button and update text based on selection."""
        count = len(self.selected_indices)
        if count > 0 and self.empire:
            self.btn_remove_selected.enable()
            self.btn_remove_selected.set_text(f"Remove Selected ({count})")
        else:
            self.btn_remove_selected.disable()
            self.btn_remove_selected.set_text("Remove Selected")

    def _init_ship_list(self):
        """Initialize the center ship list panel."""
        panel_rect = self.list_panel.get_relative_rect()

        # Header row
        self.header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, panel_rect.width, self.header_height),
            manager=self.ui_manager,
            container=self.list_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top'}
        )

        # List viewport
        list_height = panel_rect.height - self.header_height
        self.list_view_panel = UIPanel(
            relative_rect=pygame.Rect(0, self.header_height, panel_rect.width - 20, list_height),
            manager=self.ui_manager,
            container=self.list_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Scrollbar
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, self.header_height, 20, list_height),
            visible_percentage=1.0,
            manager=self.ui_manager,
            container=self.list_panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Row pool for virtual scrolling
        self.row_pool = []
        self.virtual_scroll_y = 0.0

        # Build header buttons and row pool
        self._rebuild_headers()
        self._rebuild_row_pool()

    def _init_detail_panel(self):
        """Initialize the right detail panel with DesignReportPanel."""
        # Create the design report panel filling the detail_panel container
        panel_rect = self.detail_panel.get_relative_rect()
        detail_rect = pygame.Rect(0, 0, panel_rect.width, panel_rect.height)

        self.design_report_panel = DesignReportPanel(
            manager=self.ui_manager,
            rect=detail_rect,
            container=self.detail_panel
        )

    def _rebuild_headers(self):
        """Build column header buttons with reorder arrows."""
        # Clear existing headers
        if hasattr(self, 'header_widgets'):
            for widget in self.header_widgets:
                widget.kill()
        self.header_widgets = []

        # Get visible columns with their indices
        visible_cols = [(i, col) for i, col in enumerate(self.column_manager.get_columns())
                        if col.get('visible', True)]
        arrow_w = 20

        x = 0
        for vis_idx, (col_idx, col) in enumerate(visible_cols):
            width = col['width']
            title_w = width - (arrow_w * 2)

            # Left Arrow (can move left if not first visible column)
            if vis_idx > 0:
                btn_l = UIButton(
                    relative_rect=pygame.Rect(x, 0, arrow_w, self.header_height),
                    text="<",
                    manager=self.ui_manager,
                    container=self.header_container
                )
                btn_l.col_ref = col
                btn_l.direction = -1
                self.header_widgets.append(btn_l)

            # Sort indicator
            sort_indicator = ""
            if col['id'] == self.view_model.sort_column_id:
                sort_indicator = " ▼" if self.view_model.sort_descending else " ▲"

            # Title button (sortable)
            btn = UIButton(
                relative_rect=pygame.Rect(x + arrow_w, 0, title_w, self.header_height),
                text=col['title'] + sort_indicator,
                manager=self.ui_manager,
                container=self.header_container,
                object_id=f"#header_{col['id']}"
            )
            btn.sort_col_ref = col
            self.header_widgets.append(btn)

            # Right Arrow (can move right if not last visible column)
            if vis_idx < len(visible_cols) - 1:
                btn_r = UIButton(
                    relative_rect=pygame.Rect(x + width - arrow_w, 0, arrow_w, self.header_height),
                    text=">",
                    manager=self.ui_manager,
                    container=self.header_container
                )
                btn_r.col_ref = col
                btn_r.direction = 1
                self.header_widgets.append(btn_r)

            x += width

    def _swap_columns(self, col, direction):
        """Swap a column with its neighbor in the given direction."""
        if self.column_manager.swap_column(col, direction):
            # Rebuild UI
            self._rebuild_headers()
            self._rebuild_row_pool()
            self.refresh_list()

    def _rebuild_row_pool(self):
        """Build the row pool for virtual scrolling."""
        # Clear existing rows
        for row in self.row_pool:
            if 'bg' in row and row['bg']:
                row['bg'].kill()
            for widget in row.get('widgets', []):
                widget.kill()
        self.row_pool.clear()

        # Calculate how many rows we need
        panel_rect = self.list_view_panel.get_relative_rect()
        visible_rows = max(1, (panel_rect.height // self.row_height) + 2)  # +2 for buffer

        for i in range(visible_rows):
            y = i * self.row_height

            # Row background panel
            row_bg = UIPanel(
                relative_rect=pygame.Rect(0, y, panel_rect.width, self.row_height),
                manager=self.ui_manager,
                container=self.list_view_panel
            )

            # Create widgets for each visible column
            widgets = []
            x = 0
            for col in self.column_manager.get_columns():
                if not col.get('visible', True):
                    continue

                width = col['width']
                col_id = col['id']

                if self.column_manager.is_image_column(col):
                    # Use UIImage for portrait/topdown columns
                    # Create placeholder surface
                    placeholder = pygame.Surface((width - 4, self.row_height - 4))
                    placeholder.fill((40, 40, 40))
                    widget = UIImage(
                        relative_rect=pygame.Rect(x + 2, 2, width - 4, self.row_height - 4),
                        image_surface=placeholder,
                        manager=self.ui_manager,
                        container=row_bg
                    )
                    widget.col_id = col_id  # Tag with column ID for update
                else:
                    widget = UILabel(
                        relative_rect=pygame.Rect(x, 0, width, self.row_height),
                        text="",
                        manager=self.ui_manager,
                        container=row_bg
                    )
                widgets.append(widget)
                x += width

            self.row_pool.append({
                'bg': row_bg,
                'widgets': widgets,
                'ship_index': -1  # Will be set during update
            })

    def _update_visible_rows(self):
        """Update visible rows based on scroll position."""
        filtered_ships = self.view_model.get_filtered_ships()

        if not filtered_ships:
            # Hide all rows
            for row in self.row_pool:
                row['bg'].hide()
            return

        total_height = len(filtered_ships) * self.row_height
        panel_rect = self.list_view_panel.get_relative_rect()

        # Calculate scroll offset
        scroll_pct = self.scroll_bar.scroll_position if hasattr(self.scroll_bar, 'scroll_position') else 0
        max_scroll = max(0, total_height - panel_rect.height)
        scroll_y = scroll_pct * max_scroll

        # Determine which ships are visible
        first_visible = int(scroll_y // self.row_height)

        for i, row in enumerate(self.row_pool):
            ship_index = first_visible + i

            if 0 <= ship_index < len(filtered_ships):
                ship = filtered_ships[ship_index]
                row['ship_index'] = ship_index

                # Position the row
                y_pos = (ship_index * self.row_height) - scroll_y
                row['bg'].set_relative_position((0, int(y_pos)))
                row['bg'].show()

                # Update column values
                self._update_row_data(row, ship)

                # Apply selection highlighting
                self._apply_row_highlight(row, ship_index)
            else:
                row['bg'].hide()
                row['ship_index'] = -1

    def _apply_row_highlight(self, row, ship_index: int):
        """Apply visual highlighting to selected rows."""
        bg_panel = row['bg']
        is_selected = ship_index in self.selected_indices

        # Use pygame_gui's background_colour property if available
        if is_selected:
            # Darker blue tint for selection
            bg_panel.background_colour = pygame.Color(60, 80, 120)
        else:
            # Default panel background (dark grey)
            bg_panel.background_colour = pygame.Color(35, 35, 35)

        # Force redraw
        bg_panel.rebuild()

    def _update_row_data(self, row, ship):
        """Update a single row with ship data."""
        widget_idx = 0
        for col in self.column_manager.get_columns():
            if not col.get('visible', True):
                continue

            if widget_idx >= len(row['widgets']):
                break

            widget = row['widgets'][widget_idx]
            col_id = col['id']

            if self.column_manager.is_image_column(col):
                # Handle image columns
                image_surf = self._get_ship_image(ship, col_id)
                if image_surf and hasattr(widget, 'set_image'):
                    widget.set_image(image_surf)
            else:
                # Handle text columns using ColumnManager
                value = self.column_manager.get_column_value(ship, col)
                if hasattr(widget, 'set_text'):
                    widget.set_text(str(value))

            widget_idx += 1

    def _get_ship_image(self, ship, image_type: str) -> pygame.Surface:
        """Get a ship image (portrait or top-down) scaled for list display."""
        # Get theme and ship class from design_data
        theme_id = ship.design_data.get('theme_id', 'Federation')
        ship_class = ship.design_data.get('ship_class', 'Unknown')

        # Check cache
        cache_key = (ship.instance_id, image_type)
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Get image from theme manager
        theme_mgr = ShipThemeManager.instance()

        target_height = self.row_height - 4  # Match portrait height

        if image_type == 'portrait':
            target_size = (40, target_height)
            raw_surf = theme_mgr.get_portrait_image(theme_id, ship_class)
            # Use standard fit scaling for portraits
            if raw_surf:
                result = scale_image_to_fit(raw_surf, target_size)
            else:
                result = self._create_placeholder(target_size)
        elif image_type == 'topdown':
            raw_surf = theme_mgr.load_image(theme_id, ship_class)
            # Use visible-portion scaling for top-down images
            if raw_surf:
                result = scale_image_by_visible_portion(raw_surf, target_height)
            else:
                result = self._create_placeholder((80, target_height))
        else:
            result = self._create_placeholder((40, target_height))

        # Cache the result
        self._image_cache[cache_key] = result
        return result

    def _create_placeholder(self, size):
        """Create a placeholder surface for missing images."""
        result = pygame.Surface(size)
        result.fill((50, 50, 50))
        pygame.draw.rect(result, (80, 80, 80), (5, 10, 30, 20), 1)
        return result

    def refresh_list(self):
        """Refresh the ship list with current fleet data."""
        # Update view model with current fleet ships
        self.view_model.update_ships(self.fleet.ships)

        # Update summary
        self._update_summary()

        # Update scroll bar
        filtered_ships = self.view_model.get_filtered_ships()
        total_height = len(filtered_ships) * self.row_height
        panel_rect = self.list_view_panel.get_relative_rect()
        visible_pct = min(1.0, panel_rect.height / max(1, total_height))
        self.scroll_bar.set_visible_percentage(visible_pct)

        # Update visible rows
        self._update_visible_rows()

    def _update_summary(self):
        """Update the fleet summary labels using calculate_fleet_stats."""
        ships = self.fleet.ships
        stats = calculate_fleet_stats(ships)

        # Combat Status
        self.lbl_ship_count.set_text(
            f"Ships: {stats['combat_capable_count']}/{stats['ship_count']} combat ready"
        )
        if stats['ship_count'] > 0:
            self.lbl_avg_hp.set_text(f"Avg HP: {stats['avg_hp_percent'] * 100:.0f}%")
        else:
            self.lbl_avg_hp.set_text("Avg HP: --")
        self.lbl_damaged.set_text(f"Damaged: {stats['damaged_count']}")
        self.lbl_derelict.set_text(f"Derelict: {stats['derelict_count']}")

        # Logistics
        self.lbl_tonnage.set_text(f"Tonnage: {stats['total_tonnage']:,.0f}")
        self.lbl_speed.set_text(f"Speed: {self.fleet.speed}")

        # Fuel percentage
        if stats['max_fuel'] > 0:
            fuel_pct = stats['total_fuel'] / stats['max_fuel'] * 100
            self.lbl_fuel.set_text(f"Fuel: {stats['total_fuel']:.0f}/{stats['max_fuel']:.0f} ({fuel_pct:.0f}%)")
        else:
            self.lbl_fuel.set_text("Fuel: N/A")

        # Energy percentage
        if stats['max_energy'] > 0:
            energy_pct = stats['total_energy'] / stats['max_energy'] * 100
            self.lbl_energy.set_text(f"Energy: {stats['total_energy']:.0f}/{stats['max_energy']:.0f} ({energy_pct:.0f}%)")
        else:
            self.lbl_energy.set_text("Energy: N/A")

        # Movement Capabilities - use fleet methods
        capabilities = self.fleet.get_capability_summary()

        # Warp Capable
        if capabilities['can_warp']:
            self.lbl_warp_capable.set_text("Warp: Yes")
        else:
            limiting_ship = capabilities.get('warp_limiting_ship')
            if limiting_ship:
                self.lbl_warp_capable.set_text(f"Warp: No ({limiting_ship.name})")
            else:
                self.lbl_warp_capable.set_text("Warp: No")

        # Fuel Endurance
        fuel_endurance = capabilities['fuel_endurance']
        if fuel_endurance == -1:
            self.lbl_fuel_endurance.set_text("Fuel Range: Unlimited")
        elif fuel_endurance == 0:
            self.lbl_fuel_endurance.set_text("Fuel Range: EMPTY")
        else:
            self.lbl_fuel_endurance.set_text(f"Fuel Range: {fuel_endurance} hexes")

        # Warp Jumps Remaining
        warp_jumps = capabilities['warp_jumps']
        if not capabilities['can_warp']:
            self.lbl_warp_jumps.set_text("Warp Jumps: N/A")
        elif warp_jumps == -1:
            self.lbl_warp_jumps.set_text("Warp Jumps: Unlimited")
        elif warp_jumps == 0:
            self.lbl_warp_jumps.set_text("Warp Jumps: NONE")
        else:
            self.lbl_warp_jumps.set_text(f"Warp Jumps: {warp_jumps}")

    def process_event(self, event):
        """Handle UI events."""
        handled = super().process_event(event)

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
            if event.ui_element == self.scroll_bar:
                self._update_visible_rows()
                handled = True

        # Handle mouse clicks on ship rows
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._handle_row_click(event.pos):
                handled = True

        return handled

    def _handle_row_click(self, pos):
        """Handle click on a ship row with Ctrl+click multi-select support."""
        # Check if click is within the list view panel
        list_rect = self.list_view_panel.get_abs_rect()

        if not list_rect.collidepoint(pos):
            return False

        # Find which row was clicked
        filtered_ships = self.view_model.get_filtered_ships()
        for row in self.row_pool:
            if not row['bg'].visible:
                continue

            row_rect = row['bg'].get_abs_rect()
            if row_rect.collidepoint(pos):
                ship_index = row.get('ship_index', -1)
                if 0 <= ship_index < len(filtered_ships):
                    mods = pygame.key.get_mods()
                    ctrl_held = bool(mods & pygame.KMOD_CTRL)

                    if ctrl_held:
                        # Ctrl+click: toggle selection
                        if ship_index in self.selected_indices:
                            # Don't deselect if it's the last selected ship
                            if len(self.selected_indices) > 1:
                                self.selected_indices.discard(ship_index)
                        else:
                            self.selected_indices.add(ship_index)
                    else:
                        # Normal click: replace selection
                        self.selected_indices = {ship_index}

                    # Update detail panel based on selection
                    if len(self.selected_indices) == 1:
                        sole_idx = next(iter(self.selected_indices))
                        self.selected_ship = filtered_ships[sole_idx]
                    else:
                        self.selected_ship = None

                    self._update_detail_panel()
                    self._update_remove_button()
                    self._update_visible_rows()  # Refresh row highlighting
                    return True

        return False

    def _handle_header_click(self, col_id):
        """Handle clicking on a column header for sorting."""
        self.view_model.set_sort(col_id)
        self._rebuild_headers()
        self.refresh_list()

    def select_ship(self, ship):
        """Select a single ship to show in the detail panel (API for external callers)."""
        # Find the ship's index in filtered ships
        filtered_ships = self.view_model.get_filtered_ships()
        for i, s in enumerate(filtered_ships):
            if s is ship:
                self.selected_indices = {i}
                break
        else:
            self.selected_indices.clear()

        self.selected_ship = ship
        self._update_detail_panel()
        self._update_remove_button()
        self._update_visible_rows()

    def _update_detail_panel(self):
        """Update the detail panel with selected ship info."""
        if self.selected_ship:
            ship_obj = self._design_loader.load_ship_from_design_data(
                self.selected_ship.design_data, 0, 0
            )
            if ship_obj:
                self.design_report_panel.update_design(ship_obj)
            else:
                self.design_report_panel.show_placeholder()
        else:
            self.design_report_panel.show_placeholder()

    def _on_remove_ship(self, ship):
        """Handle remove single ship from fleet (legacy API)."""
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
        if not self.empire or not self.selected_indices:
            return

        filtered_ships = self.view_model.get_filtered_ships()
        ships_to_remove = [
            filtered_ships[i] for i in sorted(self.selected_indices)
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
        self.selected_indices.clear()
        self.selected_ship = None
        self.view_model.update_ships(self.fleet.ships)
        self._update_detail_panel()
        self.refresh_list()
        self._update_summary()
        self._update_remove_button()

    def update(self, time_delta: float):
        """Update UI elements and handle toggle button clicks."""
        super().update(time_delta)

        # Handle filter toggle buttons
        for filter_id, btn in self.filter_buttons.items():
            if btn.check_pressed():
                self._toggle_filter(filter_id)

        # Handle column visibility toggle buttons
        for col_id, btn in self.column_buttons.items():
            if btn.check_pressed():
                self._toggle_column(col_id)

        # Handle Remove Selected button
        if hasattr(self, 'btn_remove_selected') and self.btn_remove_selected.check_pressed():
            self._on_remove_selected_ships()

        # Handle header arrows and sort clicks
        if hasattr(self, 'header_widgets'):
            for el in self.header_widgets:
                if isinstance(el, UIButton) and el.check_pressed():
                    if hasattr(el, 'col_ref') and hasattr(el, 'direction'):
                        # Move Column
                        self._swap_columns(el.col_ref, el.direction)
                    elif hasattr(el, 'sort_col_ref'):
                        # Sort Column
                        col = el.sort_col_ref
                        self.view_model.set_sort(col['id'])
                        self._rebuild_headers()
                        self.refresh_list()

    def _toggle_filter(self, filter_id: str):
        """Toggle a filter state and update UI."""
        # Toggle the state via view model
        new_state = self.view_model.toggle_filter(filter_id)
        label = self.view_model.get_filter_label(filter_id)

        # Update button appearance
        btn = self.filter_buttons[filter_id]
        if new_state:
            btn.select()
            btn.set_text(f"[{label}]")
        else:
            btn.unselect()
            btn.set_text(label)

        # Refresh the list with new filters
        self.refresh_list()

    def _toggle_column(self, col_id: str):
        """Toggle a column's visibility and update UI."""
        btn = self.column_buttons[col_id]
        col = btn.col_ref

        # Toggle visibility via ColumnManager
        is_visible = self.column_manager.toggle_column(col_id)
        title = col['title'] or col_id

        # Update button text
        if is_visible:
            btn.set_text(f"[x] {title}")
        else:
            btn.set_text(f"[ ] {title}")

        # Rebuild headers and rows to reflect column changes
        self._rebuild_headers()
        self._rebuild_row_pool()
        self.refresh_list()

    def kill(self):
        """Clean up when window is closed."""
        # Clean up design report panel
        if hasattr(self, 'design_report_panel') and self.design_report_panel:
            self.design_report_panel.kill()

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
