"""
Fleet List Renderer - Renders the ship list with virtual scrolling and column headers.

PROJ-173 Phase 1: Extracted from FleetReportWindow to reduce god class size.
"""
import pygame
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIVerticalScrollBar, UIImage

from game.ui.config import UIConfig
from game.ui.utils import scale_image_by_visible_portion, scale_image_to_fit
from game.ui.assets import ShipThemeManager


class FleetListRenderer:
    """
    Renders the ship list with virtual scrolling, sortable column headers,
    and row highlighting for selection.

    This is a UI component that manages a collection of pygame_gui elements
    within a container panel.
    """

    def __init__(
        self,
        panel: UIPanel,
        manager,
        column_manager,
        view_model,
        header_height: int = None,
        row_height: int = None
    ):
        """
        Initialize the fleet list renderer.

        Args:
            panel: The UIPanel container to build the list in
            manager: pygame_gui UIManager
            column_manager: ColumnManager for column configuration
            view_model: FleetListViewModel for sort state
            header_height: Height of column headers (default from UIConfig)
            row_height: Height of each row (default from UIConfig)
        """
        self.panel = panel
        self.manager = manager
        self.column_manager = column_manager
        self.view_model = view_model

        # Layout constants
        self.header_height = header_height or UIConfig.HEADER_HEIGHT
        self.row_height = row_height or UIConfig.ROW_HEIGHT_LARGE

        # Containers
        self.header_container = None
        self.list_view_panel = None
        self.scroll_bar = None

        # Widget collections
        self.header_widgets = []
        self.row_pool = []

        # Image cache
        self._image_cache = {}  # {(ship_id, image_type): pygame.Surface}

        # Build UI
        self._build_containers()
        self._rebuild_headers()
        self._rebuild_row_pool()

    def _build_containers(self):
        """Build the header container, list viewport, and scrollbar."""
        panel_rect = self.panel.get_relative_rect()

        # Header row
        self.header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, panel_rect.width, self.header_height),
            manager=self.manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top'}
        )

        # List viewport
        list_height = panel_rect.height - self.header_height
        self.list_view_panel = UIPanel(
            relative_rect=pygame.Rect(0, self.header_height, panel_rect.width - 20, list_height),
            manager=self.manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Scrollbar
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, self.header_height, 20, list_height),
            visible_percentage=1.0,
            manager=self.manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

    def rebuild_headers(self):
        """Public method to rebuild column headers."""
        self._rebuild_headers()

    def _rebuild_headers(self):
        """Build column header buttons with reorder arrows."""
        # Clear existing headers
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
                    manager=self.manager,
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
                manager=self.manager,
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
                    manager=self.manager,
                    container=self.header_container
                )
                btn_r.col_ref = col
                btn_r.direction = 1
                self.header_widgets.append(btn_r)

            x += width

    def rebuild_row_pool(self):
        """Public method to rebuild the row pool."""
        self._rebuild_row_pool()

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
                manager=self.manager,
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
                        manager=self.manager,
                        container=row_bg
                    )
                    widget.col_id = col_id  # Tag with column ID for update
                else:
                    widget = UILabel(
                        relative_rect=pygame.Rect(x, 0, width, self.row_height),
                        text="",
                        manager=self.manager,
                        container=row_bg
                    )
                widgets.append(widget)
                x += width

            self.row_pool.append({
                'bg': row_bg,
                'widgets': widgets,
                'ship_index': -1  # Will be set during update
            })

    def update_visible_rows(self, filtered_ships, selected_indices: set):
        """
        Update visible rows based on scroll position.

        Args:
            filtered_ships: List of ships to display
            selected_indices: Set of selected ship indices
        """
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
                self._apply_row_highlight(row, ship_index, selected_indices)
            else:
                row['bg'].hide()
                row['ship_index'] = -1

    def _apply_row_highlight(self, row, ship_index: int, selected_indices: set):
        """Apply visual highlighting to selected rows."""
        bg_panel = row['bg']
        is_selected = ship_index in selected_indices

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

    def update_scroll_bar(self, filtered_ships):
        """
        Update the scroll bar's visible percentage.

        Args:
            filtered_ships: List of ships to calculate scroll for
        """
        total_height = len(filtered_ships) * self.row_height
        panel_rect = self.list_view_panel.get_relative_rect()
        visible_pct = min(1.0, panel_rect.height / max(1, total_height))
        self.scroll_bar.set_visible_percentage(visible_pct)

    def find_clicked_row(self, pos, list_rect=None):
        """
        Find which row was clicked.

        Args:
            pos: Mouse position (x, y)
            list_rect: Optional pre-computed list view panel rect

        Returns:
            ship_index if a row was clicked, -1 otherwise
        """
        if list_rect is None:
            list_rect = self.list_view_panel.get_abs_rect()

        if not list_rect.collidepoint(pos):
            return -1

        for row in self.row_pool:
            if not row['bg'].visible:
                continue

            row_rect = row['bg'].get_abs_rect()
            if row_rect.collidepoint(pos):
                return row.get('ship_index', -1)

        return -1

    def check_header_presses(self):
        """
        Check for header button presses.

        Returns:
            Dict with keys:
            - 'swap_column': (col, direction) or None
            - 'sort_column': col_id or None
        """
        result = {
            'swap_column': None,
            'sort_column': None
        }

        for el in self.header_widgets:
            if isinstance(el, UIButton) and el.check_pressed():
                if hasattr(el, 'col_ref') and hasattr(el, 'direction'):
                    # Move Column
                    result['swap_column'] = (el.col_ref, el.direction)
                    return result
                elif hasattr(el, 'sort_col_ref'):
                    # Sort Column
                    result['sort_column'] = el.sort_col_ref['id']
                    return result

        return result
