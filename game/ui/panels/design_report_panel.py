"""
Design Report Panel - Reusable widget for displaying ship/design information.

This widget displays comprehensive design specifications including portrait
and detailed stats in a two-column scrollable layout. It delegates stats display
to the shared DesignStatsPanel widget.

Cross-layer imports (acceptable for UI display):
- Ship: TYPE_CHECKING only - used for type hints in method signatures
"""
from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UILabel, UIPanel, UITextBox
from typing import Optional, TYPE_CHECKING
from game.ui.panels.design_stats_panel import DesignStatsPanel
from game.ui.colors import (
    SHIP_CLASS_FIGHTER, SHIP_CLASS_CORVETTE, SHIP_CLASS_ESCORT, SHIP_CLASS_DESTROYER,
    SHIP_CLASS_CRUISER, SHIP_CLASS_BATTLESHIP, SHIP_CLASS_CARRIER, SHIP_CLASS_DEFAULT
)

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
        self._stats_panel: Optional[DesignStatsPanel] = None
        self.rows_map = {}  # Map of stat key -> StatRow (exposed for test access)

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

        # PROJ-81 Phase 4: Design identity labels (below portrait)
        identity_y = portrait_height + 15
        self.name_label = UILabel(
            relative_rect=pygame.Rect(10, identity_y, rect.width - 20, 24),
            text="",
            manager=manager,
            container=self.panel
        )
        self.type_class_label = UILabel(
            relative_rect=pygame.Rect(10, identity_y + 24, rect.width - 20, 20),
            text="",
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

        # Kill stats panel if present
        if self._stats_panel is not None:
            self._stats_panel.kill()
            self._stats_panel = None
        self.rows_map = {}

        # PROJ-81: Clear identity labels
        if hasattr(self, 'name_label'):
            self.name_label.set_text("")
        if hasattr(self, 'type_class_label'):
            self.type_class_label.set_text("")

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

        # PROJ-81 Phase 4: Populate design identity labels
        self.name_label.set_text(ship.name)
        self.type_class_label.set_text(f"{ship.vehicle_type} - {ship.ship_class}")

        # Kill old stats panel
        if self._stats_panel is not None:
            self._stats_panel.kill()

        # Create stats panel below portrait + identity labels (50px for labels)
        portrait_h = self.portrait_image.relative_rect.height
        identity_h = 50  # Height for name + type/class labels
        stats_y = portrait_h + 15 + identity_h
        stats_w = self.rect.width - 20
        stats_h = self.rect.height - stats_y - 20

        self._stats_panel = DesignStatsPanel(
            manager=self.manager,
            rect=pygame.Rect(10, stats_y, stats_w, stats_h),
            container=self.panel,
            ship=ship,
            show_requirements=False
        )

        # Populate stat values (panel only builds layout with "--" placeholders)
        self._stats_panel.update_stats(ship)

        # Expose rows_map for convenient test access
        self.rows_map = self._stats_panel.rows_map

    def _update_portrait(self, ship: Ship):
        """Update ship portrait image by loading from file system."""
        import os
        import re

        # Get portrait dimensions from the UIImage widget
        portrait_rect = self.portrait_image.relative_rect
        portrait_width = portrait_rect.width
        portrait_height = portrait_rect.height

        # Determine portrait file path
        theme = ship.theme_id
        ship_class = ship.ship_class

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
                except (FileNotFoundError, OSError, pygame.error) as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to load portrait from {path}: {e}")
                    continue

        # Fallback: Create placeholder portrait if no image found
        if portrait_surface is None:
            portrait_surface = pygame.Surface((portrait_width, portrait_height))

            # Simple gradient based on ship class
            class_colors = {
                'Fighter': SHIP_CLASS_FIGHTER,
                'Corvette': SHIP_CLASS_CORVETTE,
                'Escort': SHIP_CLASS_ESCORT,
                'Frigate': SHIP_CLASS_ESCORT,  # Same as Escort
                'Destroyer': SHIP_CLASS_DESTROYER,
                'Cruiser': SHIP_CLASS_CRUISER,
                'Battleship': SHIP_CLASS_BATTLESHIP,
                'Carrier': SHIP_CLASS_CARRIER
            }

            base_color = class_colors.get(ship_class, SHIP_CLASS_DEFAULT)

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

    def get_width_required(self) -> int:
        """
        Get minimum width required for this panel.

        Returns:
            int: Minimum width in pixels (750px from design workshop)
        """
        return 750

    def kill(self):
        """Clean up all UI elements."""
        if self._stats_panel is not None:
            self._stats_panel.kill()
            self._stats_panel = None
        if hasattr(self, 'panel'):
            self.panel.kill()
