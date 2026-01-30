"""
Design Report Panel - Reusable widget for displaying ship/design information.

This widget displays comprehensive design specifications including portrait
and detailed stats in a two-column scrollable layout, adapted from the
design workshop's BuilderRightPanel but without requirements/warnings.

Cross-layer imports (acceptable for UI display):
- Ship: TYPE_CHECKING only - used for type hints in method signatures
- LayerType: Runtime - iterates ship layers for layer status display
"""
from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UIPanel, UIScrollingContainer, UITextBox, UILabel
from typing import Optional, TYPE_CHECKING
from game.core.constants import LayerType  # Canonical location for LayerType
from game.ui.screens.builder.right_panel import StatRow
from game.ui.screens.builder.stats_config import STATS_CONFIG, get_construction_rows

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


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

        # Portrait (positioned at top, full panel width)
        # Portrait width matches panel width minus margins
        portrait_width = rect.width - 20
        portrait_height = portrait_width  # Keep it square
        self.portrait_image = UIImage(
            relative_rect=pygame.Rect(10, 10, portrait_width, portrait_height),
            image_surface=pygame.Surface((portrait_width, portrait_height)),
            manager=manager,
            container=self.panel
        )

        # Stats scrolling container (below portrait, full width, single column)
        stats_y = portrait_height + 20  # Below portrait with gap
        stats_w = rect.width - 20  # Full width minus margins
        stats_h = rect.height - stats_y - 10  # Remaining height
        self.stats_container = UIScrollingContainer(
            relative_rect=pygame.Rect(10, stats_y, stats_w, stats_h),
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

        # Placeholder text positioned below where portrait would be
        placeholder_w = self.rect.width - 20  # Full width
        portrait_width = self.rect.width - 20
        portrait_height = portrait_width
        placeholder_y = portrait_height + 20  # Below portrait with gap
        self.placeholder_text = UITextBox(
            html_text="<b>Select a design from Available Designs</b><br><br>"
                     "Click on a design in the left panel to view its specifications.",
            relative_rect=pygame.Rect(10, placeholder_y, placeholder_w, 100),
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
        """Update ship portrait image by loading from file system."""
        import os
        import re

        # Get portrait dimensions from the UIImage widget
        portrait_rect = self.portrait_image.relative_rect
        portrait_width = portrait_rect.width
        portrait_height = portrait_rect.height

        # Determine portrait file path
        theme = getattr(ship, 'theme_id', 'Federation')
        ship_class = getattr(ship, 'ship_class', 'Unknown')

        # Ensure ship_class is a string
        if not isinstance(ship_class, str):
            ship_class = str(ship_class) if ship_class else 'Unknown'

        # Parse ship class name (handle formats like "Large Escort (Scout)")
        match = re.match(r"(.*)\s+\((.*)\)", ship_class)
        if match:
            base = match.group(1).strip().replace(" ", "")
            sub = match.group(2).strip().replace(" ", "")
            class_clean = f"{sub}{base}"
        else:
            class_clean = ship_class.replace(" ", "")

        filename = f"{class_clean}_Portrait.jpg"

        # Try multiple locations for portrait image
        portrait_paths = [
            os.path.join("assets", "ShipThemes", theme, "Portraits", filename),
            os.path.join("resources", "Portraits", theme, filename),
            os.path.join("resources", "Portraits", theme, f"{ship_class}_Portrait.jpg"),
            os.path.join("assets", "Images", "Default_Ship_Portrait.png")
        ]

        portrait_surface = None
        for path in portrait_paths:
            if os.path.exists(path):
                try:
                    loaded_img = pygame.image.load(path)
                    portrait_surface = pygame.transform.smoothscale(loaded_img, (portrait_width, portrait_height))
                    break
                except Exception as e:
                    from game.core.logger import log_warning
                    log_warning(f"Failed to load portrait from {path}: {e}")
                    continue

        # Fallback: Create placeholder portrait if no image found
        if portrait_surface is None:
            portrait_surface = pygame.Surface((portrait_width, portrait_height))

            # Simple gradient based on ship class
            class_colors = {
                'Fighter': (255, 150, 50),
                'Corvette': (100, 200, 100),
                'Escort': (100, 150, 255),
                'Frigate': (100, 150, 255),
                'Destroyer': (255, 100, 100),
                'Cruiser': (200, 100, 255),
                'Battleship': (255, 200, 50),
                'Carrier': (150, 255, 200)
            }

            base_color = class_colors.get(ship_class, (150, 150, 150))

            # Gradient fill
            for y in range(portrait_height):
                fade = 1.0 - (y / portrait_height) * 0.4
                color = tuple(int(c * fade) for c in base_color)
                pygame.draw.line(portrait_surface, color, (0, y), (portrait_width, y))

            # Add ship name and class
            # Scale font sizes based on portrait size
            font_scale = portrait_width / 200.0  # 200 was original portrait size
            font_large = pygame.font.SysFont("arial", int(18 * font_scale), bold=True)
            font_small = pygame.font.SysFont("arial", int(14 * font_scale))

            # Ship name
            name_text = font_large.render(ship.name[:25], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(portrait_width // 2, int(portrait_height * 0.45)))
            # Shadow
            shadow = font_large.render(ship.name[:25], True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(portrait_width // 2 + 1, int(portrait_height * 0.45) + 1))
            portrait_surface.blit(shadow, shadow_rect)
            portrait_surface.blit(name_text, name_rect)

            # Ship class
            if ship_class:
                class_text = font_small.render(str(ship_class), True, (200, 200, 200))
                class_rect = class_text.get_rect(center=(portrait_width // 2, int(portrait_height * 0.55)))
                portrait_surface.blit(class_text, class_rect)

            # Border
            pygame.draw.rect(portrait_surface, (200, 200, 200), (0, 0, portrait_width, portrait_height), 2)

        # Update UIImage
        self.portrait_image.set_image(portrait_surface)

    def _rebuild_stats(self, ship: Ship):
        """Rebuild all stat displays in single-column layout."""
        # Clear existing rows
        for row in self.rows_map.values():
            row.label.kill()
            row.value.kill()
            row.unit.kill()
        self.rows_map = {}

        # Calculate single column layout
        container_width = self.stats_container.get_container().get_size()[0]

        # Account for scrollbar
        scrollbar_width = 20
        col_width = container_width - scrollbar_width - 20  # Full width single column
        col_x = 10

        # Track y position
        y = 10

        # Get stat rows from config
        try:
            # Get static stat groups from STATS_CONFIG
            main_systems = STATS_CONFIG.get('main', [])
            maneuvering = STATS_CONFIG.get('maneuvering', [])
            shields = STATS_CONFIG.get('shields', [])
            armor = STATS_CONFIG.get('armor', [])
            targeting = STATS_CONFIG.get('targeting', [])
            crew = STATS_CONFIG.get('crewlogistics', [])
            fighter = STATS_CONFIG.get('fightersupport', [])

            # Get separate logistics sections (matching design workshop)
            fuel_logistics = STATS_CONFIG.get('fuel_logistics', [])
            ammo_logistics = STATS_CONFIG.get('ammo_logistics', [])
            energy_logistics = STATS_CONFIG.get('energy_logistics', [])

            # Get dynamic construction rows
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
            fuel_logistics = []
            ammo_logistics = []
            energy_logistics = []
            crew = []
            fighter = []
            construction = []

        # Single column: All sections in order (matching design workshop)
        all_sections = [
            ("Main Systems", main_systems),
            ("Fuel Logistics", fuel_logistics),
            ("Ordinance (Ammo)", ammo_logistics),
            ("Energy", energy_logistics),
            ("Armor", armor),
            # Layers will be added dynamically after Armor
            ("Maneuvering", maneuvering),
            ("Shields", shields),
            ("Targeting", targeting),
            ("Crew Logistics", crew),
            ("Fighter Support", fighter),
            ("Build Cost", construction)
        ]

        for section_name, rows in all_sections:
            if rows:
                # Section header
                y = self._create_section_header(section_name, col_x, y, col_width)
                # Stat rows
                for stat_def in rows:
                    y = self._create_stat_row(stat_def, ship, col_x, y, col_width)
                y += 10  # Gap after section

            # Add Layers section after Armor
            if section_name == "Armor":
                y = self._create_layers_section(ship, col_x, y, col_width)

    def _create_layers_section(self, ship: "Ship", x: int, y: int, width: int) -> int:
        """Create the Layers section showing layer distribution."""
        # LayerType now imported from game.core.constants at module level

        # Only show if ship has layers
        if not hasattr(ship, 'layers') or not ship.layers:
            return y

        # Section header
        y = self._create_section_header("Layers", x, y, width)

        # Get sorted layers
        sorted_layers = sorted(ship.layers.items(), key=lambda item: item[0].value)

        # Create row for each layer
        for layer_type, layer_data in sorted_layers:
            # Get layer status
            status = ship.layer_status.get(layer_type, {}) if hasattr(ship, 'layer_status') else {}
            ratio = status.get('ratio', 0) * 100
            limit = status.get('limit', 1.0) * 100
            is_ok = status.get('ok', True)
            mass = status.get('mass', 0)

            status_icon = "✓" if is_ok else "✗"

            # Create stat row for this layer
            key = f"layer_{layer_type.name}"
            row = StatRow(
                key=key,
                label_text=layer_type.name,
                manager=self.manager,
                container=self.stats_container,
                x=x,
                y=y,
                width=width
            )

            # Update with layer info
            row.update(f"{ratio:.0f}% / {limit:.0f}%", f"({mass:.0f}t) {status_icon}")

            # Store in map
            self.rows_map[key] = row

            y += 22  # Row height

        y += 10  # Gap after section
        return y

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
