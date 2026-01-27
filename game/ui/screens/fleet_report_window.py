"""
Fleet Report Window - Displays detailed fleet information, ship lists, and individual ship reports.

PROJ-03: Fleet Report Window feature implementation.
"""
import pygame
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIScrollingContainer, UIVerticalScrollBar, UIImage

from game.core.config import UIConfig
from game.core.logger import log_info
from game.ui.screens.fleet_report_filters import calculate_fleet_stats, filter_ships, sort_ships
from game.ui.panels.ship_detail_panel import ShipDetailPanel
from game.ui.assets import ShipThemeManager


class FleetReportWindow(UIWindow):
    """
    Window to view detailed fleet information including:
    - Fleet summary statistics (left panel)
    - Ship list with filtering/sorting (center)
    - Individual ship details with damage (right panel)
    """

    def __init__(self, rect, manager, fleet, on_close_callback=None):
        """
        Initialize the Fleet Report Window.

        Args:
            rect: Window position and size (pygame.Rect)
            manager: pygame_gui UIManager
            fleet: Fleet object to display
            on_close_callback: Function to call when window is closed
        """
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=f"Fleet Report: {fleet.id}",
            resizable=True
        )

        self.fleet = fleet
        self.on_close_callback = on_close_callback

        # --- Layout Constants ---
        self.sidebar_width = 300  # Left panel for summary + filters
        self.detail_width = 350   # Right panel for ship details
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- State ---
        self.selected_ship = None
        self.filtered_ships = []

        # Filter State
        self.filter_show_damaged = True
        self.filter_show_undamaged = True
        self.filter_show_derelict = True
        self.filter_show_destroyed = False
        self.filter_show_warp_capable = True
        self.filter_show_not_warp_capable = True

        # Sort State
        self.sort_column_id = 'serial'
        self.sort_descending = False

        # Column Configuration
        # ID, Width, Title, Visible
        self.columns = [
            {'id': 'portrait', 'width': 44, 'title': '', 'type': 'image', 'visible': True},
            {'id': 'topdown', 'width': 60, 'title': '', 'type': 'image', 'visible': True},  # Larger for top-down view
            {'id': 'serial', 'width': 130, 'title': 'Serial ID', 'visible': True},
            {'id': 'design', 'width': 100, 'title': 'Design', 'visible': True},
            {'id': 'name', 'width': 120, 'title': 'Name', 'visible': True},
            {'id': 'hp_pct', 'width': 80, 'title': 'HP %', 'visible': True},
            {'id': 'status', 'width': 100, 'title': 'Status', 'visible': True},
        ]

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
            ('damaged', 'Damaged', self.filter_show_damaged),
            ('undamaged', 'Undamaged', self.filter_show_undamaged),
            ('derelict', 'Derelict', self.filter_show_derelict),
            ('destroyed', 'Destroyed', self.filter_show_destroyed),
        ]

        for filter_id, label, is_on in filter_configs:
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
            ('warp_capable', 'Warp Capable', self.filter_show_warp_capable),
            ('not_warp_capable', 'Not Warp Capable', self.filter_show_not_warp_capable),
        ]

        for filter_id, label, is_on in warp_filter_configs:
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
        for col in self.columns:
            col_id = col['id']
            title = col['title'] or col_id

            # Skip image columns (always visible, no title)
            if col.get('type') == 'image':
                continue

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
        """Initialize the right detail panel with ShipDetailPanel."""
        # Create the ship detail panel filling the detail_panel container
        panel_rect = self.detail_panel.get_relative_rect()
        detail_rect = pygame.Rect(0, 0, panel_rect.width, panel_rect.height)

        self.ship_detail_panel = ShipDetailPanel(
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
        visible_cols = [(i, col) for i, col in enumerate(self.columns) if col.get('visible', True)]
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
            if col['id'] == self.sort_column_id:
                sort_indicator = " ▼" if self.sort_descending else " ▲"

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
        idx = self.columns.index(col)
        new_idx = idx + direction

        if 0 <= new_idx < len(self.columns):
            # Swap in the columns list
            self.columns[idx], self.columns[new_idx] = self.columns[new_idx], self.columns[idx]
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
            for col in self.columns:
                if not col.get('visible', True):
                    continue

                width = col['width']
                col_id = col['id']

                if col.get('type') == 'image':
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
        if not self.filtered_ships:
            # Hide all rows
            for row in self.row_pool:
                row['bg'].hide()
            return

        total_height = len(self.filtered_ships) * self.row_height
        panel_rect = self.list_view_panel.get_relative_rect()

        # Calculate scroll offset
        scroll_pct = self.scroll_bar.scroll_position if hasattr(self.scroll_bar, 'scroll_position') else 0
        max_scroll = max(0, total_height - panel_rect.height)
        scroll_y = scroll_pct * max_scroll

        # Determine which ships are visible
        first_visible = int(scroll_y // self.row_height)

        for i, row in enumerate(self.row_pool):
            ship_index = first_visible + i

            if 0 <= ship_index < len(self.filtered_ships):
                ship = self.filtered_ships[ship_index]
                row['ship_index'] = ship_index

                # Position the row
                y_pos = (ship_index * self.row_height) - scroll_y
                row['bg'].set_relative_position((0, int(y_pos)))
                row['bg'].show()

                # Update column values
                self._update_row_data(row, ship)
            else:
                row['bg'].hide()
                row['ship_index'] = -1

    def _update_row_data(self, row, ship):
        """Update a single row with ship data."""
        widget_idx = 0
        for col in self.columns:
            if not col.get('visible', True):
                continue

            if widget_idx >= len(row['widgets']):
                break

            widget = row['widgets'][widget_idx]
            col_id = col['id']

            if col.get('type') == 'image':
                # Handle image columns
                image_surf = self._get_ship_image(ship, col_id)
                if image_surf and hasattr(widget, 'set_image'):
                    widget.set_image(image_surf)
            else:
                # Handle text columns
                value = self._get_column_value(ship, col)
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
            target_size = (40, target_height)  # Standard portrait size
            raw_surf = theme_mgr.get_portrait_image(theme_id, ship_class)
            use_visible_sizing = False
        elif image_type == 'topdown':
            target_size = (80, target_height)  # Wider for top-down view
            raw_surf = theme_mgr.get_image(theme_id, ship_class)
            use_visible_sizing = True  # Size based on visible portion
        else:
            target_size = (40, target_height)
            raw_surf = None
            use_visible_sizing = False

        if raw_surf:
            if use_visible_sizing:
                # For top-down images, size based on visible (non-transparent) portion
                result = self._scale_by_visible_portion(raw_surf, target_height)
            else:
                # For portraits, scale normally
                w, h = raw_surf.get_size()
                scale = min(target_size[0] / w, target_size[1] / h)
                new_w, new_h = int(w * scale), int(h * scale)
                scaled = pygame.transform.smoothscale(raw_surf, (new_w, new_h))

                # Center on target surface
                result = pygame.Surface(target_size, pygame.SRCALPHA)
                result.fill((30, 30, 30))
                x_off = (target_size[0] - new_w) // 2
                y_off = (target_size[1] - new_h) // 2
                result.blit(scaled, (x_off, y_off))
        else:
            # Create placeholder
            result = pygame.Surface(target_size)
            result.fill((50, 50, 50))
            # Draw a simple ship silhouette placeholder
            pygame.draw.rect(result, (80, 80, 80), (5, 10, 30, 20), 1)

        # Cache the result
        self._image_cache[cache_key] = result
        return result

    def _scale_by_visible_portion(self, surface: pygame.Surface, target_height: int) -> pygame.Surface:
        """
        Scale an image based on its visible (non-transparent) portion.

        The visible height will match target_height, and the entire image scales
        proportionally to maintain the original aspect ratio.

        Args:
            surface: Source surface with alpha channel
            target_height: Target height for the visible portion

        Returns:
            Scaled surface maintaining original aspect ratio
        """
        # Find visible bounding box
        bbox = self._get_visible_bounding_box(surface)
        if bbox is None:
            # Fully transparent - return placeholder
            placeholder = pygame.Surface((40, target_height), pygame.SRCALPHA)
            placeholder.fill((50, 50, 50))
            return placeholder

        min_x, min_y, max_x, max_y = bbox
        visible_width = max_x - min_x
        visible_height = max_y - min_y

        if visible_height <= 0 or visible_width <= 0:
            placeholder = pygame.Surface((40, target_height), pygame.SRCALPHA)
            placeholder.fill((50, 50, 50))
            return placeholder

        # Calculate scale to make visible height match target_height
        scale = target_height / visible_height
        new_width = int(surface.get_width() * scale)
        new_height = int(surface.get_height() * scale)

        # Scale the full image (maintains original aspect ratio)
        scaled_img = pygame.transform.smoothscale(surface, (new_width, new_height))

        return scaled_img

    def _get_visible_bounding_box(self, surface: pygame.Surface):
        """
        Find the bounding box of the visible (non-transparent) area of a surface.

        Args:
            surface: pygame.Surface with alpha channel

        Returns:
            Tuple (min_x, min_y, max_x, max_y) or None if fully transparent
        """
        width = surface.get_width()
        height = surface.get_height()

        min_x, min_y = width, height
        max_x, max_y = 0, 0

        # Check each pixel for non-transparent content
        for y in range(height):
            for x in range(width):
                pixel = surface.get_at((x, y))
                if pixel[3] > 10:  # Alpha > 10 (not fully transparent)
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if max_x <= min_x or max_y <= min_y:
            return None

        return (min_x, min_y, max_x + 1, max_y + 1)

    def _get_column_value(self, ship, col):
        """Get the display value for a column."""
        col_id = col['id']

        if col_id in ('portrait', 'topdown'):
            return ""  # Images handled separately
        elif col_id == 'serial':
            display_id = ship.get_display_id()
            return display_id if display_id else ship.instance_id[:8]
        elif col_id == 'design':
            return ship.design_data.get('name', ship.design_id)
        elif col_id == 'name':
            return ship.name
        elif col_id == 'hp_pct':
            return f"{ship.get_hp_percentage() * 100:.0f}%"
        elif col_id == 'status':
            if ship.is_destroyed:
                return "DESTROYED"
            elif ship.is_derelict:
                return "DERELICT"
            elif ship.is_damaged():
                return "DAMAGED"
            else:
                return "OK"
        else:
            return ""

    def refresh_list(self):
        """Refresh the ship list with current fleet data."""
        # Get ships from fleet
        ships = self.fleet.ships

        # Apply filters
        self.filtered_ships = self._apply_filters(ships)

        # Apply sort
        self.filtered_ships = self._apply_sort(self.filtered_ships)

        # Update summary
        self._update_summary()

        # Update scroll bar
        total_height = len(self.filtered_ships) * self.row_height
        panel_rect = self.list_view_panel.get_relative_rect()
        visible_pct = min(1.0, panel_rect.height / max(1, total_height))
        self.scroll_bar.set_visible_percentage(visible_pct)

        # Update visible rows
        self._update_visible_rows()

    def _apply_filters(self, ships):
        """Apply current filter state to ship list using filter_ships."""
        filter_state = {
            'show_damaged': self.filter_show_damaged,
            'show_undamaged': self.filter_show_undamaged,
            'show_derelict': self.filter_show_derelict,
            'show_destroyed': self.filter_show_destroyed,
            'show_warp_capable': self.filter_show_warp_capable,
            'show_not_warp_capable': self.filter_show_not_warp_capable,
        }
        return filter_ships(ships, filter_state)

    def _apply_sort(self, ships):
        """Apply current sort to ship list using sort_ships."""
        return sort_ships(ships, self.sort_column_id, self.sort_descending)

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

        # Forward events to ship detail panel for layer toggle buttons
        if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:
            if self.ship_detail_panel.process_event(event):
                handled = True

        return handled

    def _handle_row_click(self, pos):
        """Handle click on a ship row to select it."""
        # Check if click is within the list view panel
        list_rect = self.list_view_panel.get_abs_rect()

        if not list_rect.collidepoint(pos):
            return False

        # Find which row was clicked
        for row in self.row_pool:
            if not row['bg'].visible:
                continue

            row_rect = row['bg'].get_abs_rect()
            if row_rect.collidepoint(pos):
                ship_index = row.get('ship_index', -1)
                if 0 <= ship_index < len(self.filtered_ships):
                    ship = self.filtered_ships[ship_index]
                    self.select_ship(ship)
                    return True

        return False

    def _handle_header_click(self, col_id):
        """Handle clicking on a column header for sorting."""
        if self.sort_column_id == col_id:
            # Toggle direction
            self.sort_descending = not self.sort_descending
        else:
            # New column, default to ascending
            self.sort_column_id = col_id
            self.sort_descending = False

        self._rebuild_headers()
        self.refresh_list()

    def select_ship(self, ship):
        """Select a ship to show in the detail panel."""
        self.selected_ship = ship
        self._update_detail_panel()

    def _update_detail_panel(self):
        """Update the detail panel with selected ship info."""
        self.ship_detail_panel.update_ship(self.selected_ship)

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
                        if self.sort_column_id == col['id']:
                            self.sort_descending = not self.sort_descending
                        else:
                            self.sort_column_id = col['id']
                            self.sort_descending = False
                        self._rebuild_headers()
                        self.refresh_list()

    def _toggle_filter(self, filter_id: str):
        """Toggle a filter state and update UI."""
        # Toggle the state
        if filter_id == 'damaged':
            self.filter_show_damaged = not self.filter_show_damaged
            new_state = self.filter_show_damaged
            label = 'Damaged'
        elif filter_id == 'undamaged':
            self.filter_show_undamaged = not self.filter_show_undamaged
            new_state = self.filter_show_undamaged
            label = 'Undamaged'
        elif filter_id == 'derelict':
            self.filter_show_derelict = not self.filter_show_derelict
            new_state = self.filter_show_derelict
            label = 'Derelict'
        elif filter_id == 'destroyed':
            self.filter_show_destroyed = not self.filter_show_destroyed
            new_state = self.filter_show_destroyed
            label = 'Destroyed'
        elif filter_id == 'warp_capable':
            self.filter_show_warp_capable = not self.filter_show_warp_capable
            new_state = self.filter_show_warp_capable
            label = 'Warp Capable'
        elif filter_id == 'not_warp_capable':
            self.filter_show_not_warp_capable = not self.filter_show_not_warp_capable
            new_state = self.filter_show_not_warp_capable
            label = 'Not Warp Capable'
        else:
            return

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

        # Toggle visibility
        col['visible'] = not col['visible']
        is_visible = col['visible']
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
        # Clean up ship detail panel
        if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:
            self.ship_detail_panel.kill()

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
