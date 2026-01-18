"""
Design Report Panel - Reusable widget for displaying ship/design information.

This widget displays comprehensive design specifications including portrait
and detailed stats in a two-column scrollable layout, adapted from the
design workshop's BuilderRightPanel but without requirements/warnings.
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UIPanel, UIScrollingContainer, UITextBox, UILabel
from typing import Optional
from game.simulation.entities.ship import Ship
from ui.builder.right_panel import StatRow
from ui.builder.stats_config import STATS_CONFIG, get_logistics_rows, get_construction_rows


class DesignReportPanel:
    """
    Reusable panel that displays comprehensive ship/design information.

    Components:
    - Portrait (200x200 at top-right)
    - Stats scrolling container with two-column layout
    - Excludes requirements and warnings sections
    """

    def __init__(self, manager, rect, container=None):
        """
        Initialize design report panel.

        Args:
            manager: pygame_gui UIManager
            rect: pygame.Rect for panel dimensions
            container: Optional parent container
        """
        self.manager = manager
        self.rect = rect
        self.container = container
        self.current_ship = None
        self.rows_map = {}  # Map of stat key -> StatRow

        # Create panel container
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container
        )

        # Portrait (positioned top-right)
        img_x = rect.width - 210  # 200px portrait + 10px margin
        self.portrait_image = UIImage(
            relative_rect=pygame.Rect(img_x, 10, 200, 200),
            image_surface=pygame.Surface((200, 200)),
            manager=manager,
            container=self.panel
        )

        # Stats scrolling container (starts below portrait area)
        stats_y = 220  # Portrait height + margin
        stats_h = rect.height - stats_y - 10
        self.stats_container = UIScrollingContainer(
            relative_rect=pygame.Rect(10, stats_y, rect.width - 20, stats_h),
            manager=manager,
            container=self.panel
        )

        # Placeholder text (shown when no design selected)
        self.placeholder_text = None
        self.show_placeholder()

    def show_placeholder(self):
        """Show placeholder message when no design is selected."""
        # Clear current ship
        self.current_ship = None

        # Clear all stat rows
        for row in self.rows_map.values():
            row.label.kill()
            row.value.kill()
            row.unit.kill()
        self.rows_map = {}

        # Show placeholder message
        if self.placeholder_text:
            self.placeholder_text.kill()

        self.placeholder_text = UITextBox(
            html_text="<b>Select a design from Available Designs</b><br><br>"
                     "Click on a design in the left panel to view its specifications.",
            relative_rect=pygame.Rect(10, 10, self.rect.width - 230, 100),
            manager=self.manager,
            container=self.panel
        )

    def update_design(self, ship: Ship):
        """
        Update display for a selected design/ship.

        Args:
            ship: Ship object with stats to display
        """
        self.current_ship = ship

        # Hide placeholder
        if self.placeholder_text:
            self.placeholder_text.kill()
            self.placeholder_text = None

        # Update portrait
        self._update_portrait(ship)

        # Rebuild stats display
        self._rebuild_stats(ship)

    def _update_portrait(self, ship: Ship):
        """Update ship portrait image."""
        # Create placeholder portrait with ship class name
        portrait_surface = pygame.Surface((200, 200))

        # Simple gradient based on ship class
        class_colors = {
            'Fighter': (255, 150, 50),
            'Corvette': (100, 200, 100),
            'Frigate': (100, 150, 255),
            'Destroyer': (255, 100, 100),
            'Cruiser': (200, 100, 255),
            'Battleship': (255, 200, 50),
            'Carrier': (150, 255, 200)
        }

        base_color = class_colors.get(ship.ship_class, (150, 150, 150))

        # Gradient fill
        for y in range(200):
            fade = 1.0 - (y / 200.0) * 0.4
            color = tuple(int(c * fade) for c in base_color)
            pygame.draw.line(portrait_surface, color, (0, y), (200, y))

        # Add ship name and class
        font_large = pygame.font.SysFont("arial", 18, bold=True)
        font_small = pygame.font.SysFont("arial", 14)

        # Ship name
        name_text = font_large.render(ship.name[:25], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(100, 90))
        # Shadow
        shadow = font_large.render(ship.name[:25], True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(101, 91))
        portrait_surface.blit(shadow, shadow_rect)
        portrait_surface.blit(name_text, name_rect)

        # Ship class
        ship_class = getattr(ship, 'ship_class', 'Unknown')
        if ship_class:
            class_text = font_small.render(str(ship_class), True, (200, 200, 200))
            class_rect = class_text.get_rect(center=(100, 110))
            portrait_surface.blit(class_text, class_rect)

        # Border
        pygame.draw.rect(portrait_surface, (200, 200, 200), (0, 0, 200, 200), 2)

        # Update UIImage
        self.portrait_image.set_image(portrait_surface)

    def _rebuild_stats(self, ship: Ship):
        """Rebuild all stat displays in two-column layout."""
        # Clear existing rows
        for row in self.rows_map.values():
            row.label.kill()
            row.value.kill()
            row.unit.kill()
        self.rows_map = {}

        # Calculate column layout
        container_width = self.stats_container.get_container().get_size()[0]

        # Account for scrollbar
        scrollbar_width = 20
        available_width = container_width - scrollbar_width - 10

        # Two columns with gap
        col_gap = 10
        col_width = (available_width - col_gap) // 2
        col1_x = 10
        col2_x = col1_x + col_width + col_gap

        # Track y positions for each column
        y1 = 10
        y2 = 10

        # Get stat rows from config
        try:
            # Get static stat groups from STATS_CONFIG
            main_systems = STATS_CONFIG.get('main_systems', [])
            maneuvering = STATS_CONFIG.get('maneuvering', [])
            shields = STATS_CONFIG.get('shields', [])
            armor = STATS_CONFIG.get('armor', [])
            layers = STATS_CONFIG.get('layers', [])  # Usually empty/dynamic, skip for now
            targeting = STATS_CONFIG.get('targeting', [])
            crew = STATS_CONFIG.get('crew', [])
            fighter = STATS_CONFIG.get('fighter', [])

            # Get dynamic rows (logistics and construction)
            logistics = get_logistics_rows(ship)
            construction = get_construction_rows(ship)
        except Exception as e:
            # Fallback if stat config fails
            from game.core.logger import log_error
            log_error(f"Error loading stat rows: {e}")
            main_systems = []
            maneuvering = []
            shields = []
            armor = []
            targeting = []
            logistics = []
            crew = []
            fighter = []
            construction = []

        # Column 1: Main Systems, Maneuvering, Shields, Armor, Targeting
        sections_col1 = [
            ("Main Systems", main_systems),
            ("Maneuvering", maneuvering),
            ("Shields", shields),
            ("Armor", armor),
            ("Targeting", targeting)
        ]

        for section_name, rows in sections_col1:
            if rows:
                # Section header
                y1 = self._create_section_header(section_name, col1_x, y1, col_width)
                # Stat rows
                for stat_def in rows:
                    y1 = self._create_stat_row(stat_def, ship, col1_x, y1, col_width)
                y1 += 10  # Gap after section

        # Column 2: Logistics, Crew, Fighter Support, Build Cost
        sections_col2 = [
            ("Logistics", logistics),
            ("Crew Logistics", crew),
            ("Fighter Support", fighter),
            ("Build Cost", construction)
        ]

        for section_name, rows in sections_col2:
            if rows:
                # Section header
                y2 = self._create_section_header(section_name, col2_x, y2, col_width)
                # Stat rows
                for stat_def in rows:
                    y2 = self._create_stat_row(stat_def, ship, col2_x, y2, col_width)
                y2 += 10  # Gap after section

    def _create_section_header(self, title: str, x: int, y: int, width: int) -> int:
        """Create a section header label."""
        header = UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text=f"── {title} ──",
            manager=self.manager,
            container=self.stats_container,
            object_id="#section_header"
        )
        return y + 30

    def _create_stat_row(self, stat_def, ship: Ship, x: int, y: int, width: int) -> int:
        """Create a stat row and add to rows_map."""
        try:
            # Create StatRow
            row = StatRow(
                key=stat_def.key,
                label_text=stat_def.label,
                manager=self.manager,
                container=self.stats_container,
                x=x,
                y=y,
                width=width
            )

            # Get value and unit
            val = stat_def.get_value(ship)
            unit = stat_def.get_display_unit(ship, val)

            # Format value
            val_str = stat_def.format_value(val)

            # Update row
            row.update(val_str, unit)

            # Store in map
            self.rows_map[stat_def.key] = row

            return y + 22  # Row height + small gap

        except Exception as e:
            from game.core.logger import log_error
            log_error(f"Error creating stat row for {stat_def.key}: {e}")
            return y

    def get_width_required(self) -> int:
        """
        Get minimum width required for this panel.

        Returns:
            int: Minimum width in pixels (750px from design workshop)
        """
        return 750

    def kill(self):
        """Clean up all UI elements."""
        if hasattr(self, 'panel'):
            self.panel.kill()
