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
from game.ui.utils.portraits import (
    get_ship_class_color,
    get_portrait_search_paths,
    create_placeholder_portrait,
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

    def show_placeholder(self) -> None:
        """Show placeholder message when no design is selected."""
        # Clear current ship
        self.current_ship = None

        # Kill stats panel if present
        if self._stats_panel is not None:
            self._stats_panel.kill()
            self._stats_panel = None
        self.rows_map = {}

        # PROJ-81: Clear identity labels
        self.name_label.set_text("")
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

    def update_design(self, ship: Ship) -> None:
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

    def _update_portrait(self, ship: Ship) -> None:
        """Update ship portrait image by loading from file system."""
        import os
        import logging

        logger = logging.getLogger(__name__)

        # Get portrait dimensions from the UIImage widget
        portrait_rect = self.portrait_image.relative_rect
        portrait_width = portrait_rect.width
        portrait_height = portrait_rect.height

        # Determine portrait file path
        theme = ship.theme_id
        ship_class = ship.ship_class
        if not isinstance(ship_class, str):
            ship_class = str(ship_class) if ship_class else 'Unknown'

        # Try loading from file system using shared search paths
        portrait_paths = get_portrait_search_paths(theme, ship_class)

        portrait_surface = None
        for path in portrait_paths:
            if os.path.exists(path):
                try:
                    loaded_img = pygame.image.load(path)
                    portrait_surface = pygame.transform.smoothscale(
                        loaded_img, (portrait_width, portrait_height)
                    )
                    break
                except (FileNotFoundError, OSError, pygame.error) as e:
                    logger.warning(f"Failed to load portrait from {path}: {e}")
                    continue

        # Fallback: Create placeholder portrait using shared utility
        if portrait_surface is None:
            base_color = get_ship_class_color(ship_class)
            portrait_surface = create_placeholder_portrait(
                portrait_width, portrait_height, base_color,
                ship.name, subtitle=ship_class,
            )

        # Update UIImage
        self.portrait_image.set_image(portrait_surface)

    def get_width_required(self) -> int:
        """
        Get minimum width required for this panel.

        Returns:
            int: Minimum width in pixels (750px from design workshop)
        """
        return 750

    def kill(self) -> None:
        """Clean up all UI elements."""
        if self._stats_panel is not None:
            self._stats_panel.kill()
            self._stats_panel = None
        self.panel.kill()
