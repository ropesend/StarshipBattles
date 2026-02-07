"""Virtual list renderer for planet list window.

This module handles the virtual scrolling and row rendering for the planet list,
separated from the main window logic.
"""
import pygame
from pygame_gui.elements import UIPanel, UILabel, UIImage

from game.assets.asset_manager import AssetManager
from game.ui.screens.planet_list_filters import get_column_value


class VirtualListRenderer:
    """Manages virtual scrolling and row rendering for planet list.

    This class handles:
    - Row pool management (creating reusable row widgets)
    - Virtual scrolling (only rendering visible rows)
    - Icon caching for performance
    - Click-to-index calculation
    """

    def __init__(self, list_panel, row_height, manager):
        """Initialize the virtual list renderer.

        Args:
            list_panel: The UIPanel that contains the list rows
            row_height: Height in pixels of each row
            manager: pygame_gui UIManager instance
        """
        self.list_panel = list_panel
        self.row_height = row_height
        self.manager = manager
        self.row_pool = []
        self._icon_cache = {}
        self._last_scroll_pct = -1.0
        self._last_filtered_count = -1

    def rebuild_row_pool(self, visible_columns):
        """Create pool of reusable row widgets.

        Args:
            visible_columns: List of visible column definitions
        """
        # Clear existing
        for r in self.row_pool:
            for w in r['widgets']:
                w['el'].kill()
            if 'bg' in r:
                r['bg'].kill()

        self.row_pool = []

        # How many rows fit?
        visible_h = self.list_panel.relative_rect.height
        count = int(visible_h / self.row_height) + 2  # buffer

        for i in range(count):
            # Using Panel for row background
            row_panel = UIPanel(
                relative_rect=pygame.Rect(0, 0, self.list_panel.relative_rect.width, self.row_height),
                manager=self.manager,
                container=self.list_panel,
                object_id='#planet_list_row'
            )

            widgets = []
            x_off = 0
            for col in visible_columns:
                w = col['width']
                rect = pygame.Rect(x_off, 0, w, self.row_height)

                if col['id'] == 'icon':
                    # Placeholder image
                    img = UIImage(
                        relative_rect=pygame.Rect(x_off + 5, 5, 40, 40),
                        image_surface=pygame.Surface((40, 40)),
                        manager=self.manager,
                        container=row_panel
                    )
                    widgets.append({'type': 'image', 'el': img, 'col': col})
                else:
                    lbl = UILabel(rect, "", self.manager, container=row_panel)
                    widgets.append({'type': 'label', 'el': lbl, 'col': col})

                x_off += w

            self.row_pool.append({'bg': row_panel, 'widgets': widgets})

    def update_visible_rows(self, filtered_planets, scroll_bar):
        """Update content of row pool based on scroll position.

        Args:
            filtered_planets: List of filtered planet objects
            scroll_bar: UIVerticalScrollBar for scroll position
        """
        # Dirty check: skip if nothing changed
        current_pct = scroll_bar.start_percentage
        current_count = len(filtered_planets)

        if (current_pct == self._last_scroll_pct and
            current_count == self._last_filtered_count):
            return  # Nothing changed, skip update

        self._last_scroll_pct = current_pct
        self._last_filtered_count = current_count

        # Calculate scroll position
        total_h = current_count * self.row_height
        scroll_y = current_pct * total_h
        start_index = int(scroll_y // self.row_height)
        offset_y = scroll_y % self.row_height

        # Local refs for performance
        icon_cache = self._icon_cache

        for i, row_data in enumerate(self.row_pool):
            data_index = start_index + i
            row_panel = row_data['bg']

            if data_index < len(filtered_planets):
                planet = filtered_planets[data_index]

                # Store planet reference in row for selection tracking
                row_data['planet'] = planet

                y_pos = (i * self.row_height) - offset_y

                # Make visible and set position
                row_panel.show()
                row_panel.set_relative_position((0, y_pos))

                # Update Content
                for widget_data in row_data['widgets']:
                    col = widget_data['col']
                    el = widget_data['el']

                    if widget_data['type'] == 'label':
                        val = get_column_value(planet, col)
                        el.set_text(val)

                    elif widget_data['type'] == 'image':
                        # Load 128px planet image directly for 40x40 icons
                        img = None
                        if hasattr(planet, 'image_id') and planet.image_id:
                            # Use cached icon if already loaded for this planet
                            cache_key = f"icon_{planet.image_id}_{planet.image_rotation or 0}"

                            if cache_key not in icon_cache:
                                # Load 128px version directly from AssetManager
                                am = AssetManager.instance()
                                img = am.load_planet_image(planet.image_id, requested_size=128)

                                if img and img != am.get_missing_texture():
                                    # Apply rotation if specified
                                    if hasattr(planet, 'image_rotation') and planet.image_rotation and planet.image_rotation != 0.0:
                                        img = pygame.transform.rotate(img, planet.image_rotation)

                                    # Scale to 40x40 and cache
                                    icon_cache[cache_key] = pygame.transform.smoothscale(img, (40, 40))
                                else:
                                    # Image load failed - use blank
                                    img = None

                            if cache_key in icon_cache:
                                el.set_image(icon_cache[cache_key])
                            else:
                                # Fallback: blank surface
                                if '_blank_icon' not in icon_cache:
                                    icon_cache['_blank_icon'] = pygame.Surface((40, 40))
                                el.set_image(icon_cache['_blank_icon'])
                        else:
                            # No image_id - use blank surface
                            if '_blank_icon' not in icon_cache:
                                icon_cache['_blank_icon'] = pygame.Surface((40, 40))
                            el.set_image(icon_cache['_blank_icon'])
            else:
                # Scrolled past end
                row_panel.hide()
                row_data['planet'] = None  # Clear planet reference

    def get_clicked_planet_index(self, mouse_pos, list_abs_rect, scroll_bar, total_planets):
        """Calculate which planet index was clicked.

        Args:
            mouse_pos: (x, y) tuple of mouse position
            list_abs_rect: Absolute rect of the list panel
            scroll_bar: UIVerticalScrollBar for scroll position
            total_planets: Total number of filtered planets

        Returns:
            int: Index of clicked planet, or -1 if outside bounds
        """
        if not list_abs_rect.collidepoint(mouse_pos):
            return -1

        # Calculate which row was clicked based on scroll position
        relative_y = mouse_pos[1] - list_abs_rect.top

        # Account for scroll offset
        scroll_pct = scroll_bar.start_percentage
        total_h = total_planets * self.row_height
        scroll_y = scroll_pct * total_h

        # Calculate the data index of the clicked row
        absolute_y = relative_y + scroll_y
        clicked_index = int(absolute_y // self.row_height)

        if 0 <= clicked_index < total_planets:
            return clicked_index
        return -1

    def force_update(self):
        """Reset dirty tracking to force next update_visible_rows to process."""
        self._last_scroll_pct = -1.0
        self._last_filtered_count = -1

    def kill(self):
        """Clean up all row pool widgets."""
        for r in self.row_pool:
            for w in r['widgets']:
                w['el'].kill()
            if 'bg' in r:
                r['bg'].kill()
        self.row_pool = []
        self._icon_cache.clear()
