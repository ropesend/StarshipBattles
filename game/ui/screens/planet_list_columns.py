"""Column management for the planet list window.

This module contains the ColumnManager class that handles column ordering,
visibility, sorting, and header button management.
"""

import pygame
from pygame_gui.elements import UIButton


class ColumnManager:
    """Manages column ordering, visibility, sorting, and header UI for PlanetListWindow.

    Attributes:
        columns: List of column definition dicts
        sort_column_id: ID of the column currently used for sorting
        sort_descending: Whether sort is in descending order
        header_elements: List of header UI elements (buttons)
    """

    def __init__(self, columns, manager, header_container, header_height):
        """Initialize the column manager.

        Args:
            columns: List of column definition dicts
            manager: pygame_gui UI manager
            header_container: UIPanel containing the header row
            header_height: Height of header row in pixels
        """
        self.columns = columns
        self.manager = manager
        self.header_container = header_container
        self.header_height = header_height

        # Sort state - default sort by owner name as per BUG-23
        self.sort_column_id = 'owner'
        self.sort_descending = False

        # Header UI elements
        self.header_elements = []

    def get_visible_columns(self):
        """Return list of currently visible columns.

        Returns:
            List of column dicts where visible is True
        """
        return [c for c in self.columns if c.get('visible', True)]

    def rebuild_headers(self):
        """Build header row based on current columns and sort state.

        Clears existing headers and creates new ones with:
        - Left/right arrow buttons for column reordering
        - Title buttons with sort indicators for sorting
        """
        # Clear existing headers
        for el in self.header_elements:
            el.kill()
        self.header_elements = []

        visible_cols = self.get_visible_columns()

        x_off = 0
        for i, col in enumerate(visible_cols):
            w = col['width']

            # Buttons: [<] [Title] [>]
            # Size: 20px for arrows
            arrow_w = 20
            title_w = w - (arrow_w * 2)

            # Left Arrow
            if i > 0:  # Can move left
                btn_l = UIButton(
                    relative_rect=pygame.Rect(x_off, 0, arrow_w, self.header_height),
                    text="<",
                    manager=self.manager,
                    container=self.header_container
                )
                self.header_elements.append(btn_l)
                # Store reference for click handling
                btn_l.col_ref = col
                btn_l.direction = -1

            # Title (Clickable for Sorting)
            # Visual indicator for sort direction
            t_str = col['title']
            if self.sort_column_id == col['id']:
                t_str += " v" if self.sort_descending else " ^"

            btn_title = UIButton(
                relative_rect=pygame.Rect(x_off + arrow_w, 0, title_w, self.header_height),
                text=t_str,
                manager=self.manager,
                container=self.header_container
            )
            self.header_elements.append(btn_title)
            btn_title.sort_col_ref = col

            # Right Arrow
            if i < len(visible_cols) - 1:  # Can move right
                btn_r = UIButton(
                    relative_rect=pygame.Rect(x_off + w - arrow_w, 0, arrow_w, self.header_height),
                    text=">",
                    manager=self.manager,
                    container=self.header_container
                )
                self.header_elements.append(btn_r)
                btn_r.col_ref = col
                btn_r.direction = 1

            x_off += w

    def swap_columns(self, col_ref, direction):
        """Swap a column with its visual neighbor.

        Args:
            col_ref: Column dict to move
            direction: -1 for left, 1 for right

        Returns:
            True if columns were swapped, False otherwise
        """
        # Find index in main list
        try:
            main_idx = self.columns.index(col_ref)
        except ValueError:
            return False

        visible_cols = self.get_visible_columns()
        try:
            vis_idx = visible_cols.index(col_ref)
        except ValueError:
            return False

        target_vis_idx = vis_idx + direction
        if 0 <= target_vis_idx < len(visible_cols):
            target_col = visible_cols[target_vis_idx]
            target_main_idx = self.columns.index(target_col)

            # Swap in main list
            self.columns[main_idx], self.columns[target_main_idx] = \
                self.columns[target_main_idx], self.columns[main_idx]
            return True

        return False

    def handle_header_clicks(self):
        """Check for header button clicks and handle column move/sort.

        Returns:
            Tuple of (sort_changed, columns_changed) booleans indicating
            what was modified so caller can refresh appropriately.
        """
        sort_changed = False
        columns_changed = False

        for el in self.header_elements:
            if isinstance(el, UIButton):
                if hasattr(el, 'col_ref') and el.check_pressed():
                    # Move Column
                    if self.swap_columns(el.col_ref, el.direction):
                        columns_changed = True
                        self.rebuild_headers()

                elif hasattr(el, 'sort_col_ref') and el.check_pressed():
                    # Sort Column
                    col = el.sort_col_ref
                    if self.sort_column_id == col['id']:
                        self.sort_descending = not self.sort_descending
                    else:
                        self.sort_column_id = col['id']
                        self.sort_descending = False

                    sort_changed = True
                    self.rebuild_headers()  # To update arrows

        return (sort_changed, columns_changed)

    def toggle_visibility(self, col_id):
        """Toggle visibility of a column by ID.

        Args:
            col_id: ID of the column to toggle

        Returns:
            True if visibility was toggled, False if column not found
        """
        for col in self.columns:
            if col['id'] == col_id:
                col['visible'] = not col['visible']
                return True
        return False

    def kill(self):
        """Clean up header elements."""
        for el in self.header_elements:
            el.kill()
        self.header_elements = []
