"""
BuildQueuePortraitLoader - Loads and caches design portraits for build queue UI.

Extracted from build_queue_screen.py as part of PROJ-63 decomposition.
"""
from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Optional

import pygame

from game.core.logger import log_warning

if TYPE_CHECKING:
    from game.strategy.systems.design_library import DesignLibrary


# Vehicle type color map for placeholder generation
# Used when no portrait image is found
VEHICLE_TYPE_COLORS = {
    'ship': (80, 100, 180),           # Blue for ships
    'complex': (80, 180, 100),        # Green for complexes/facilities
    'planetary complex': (80, 180, 100),  # Green (alternate key)
    'station': (180, 100, 80),        # Red for stations
    'satellite': (180, 100, 80),      # Red for satellites
    'fighter': (180, 180, 80),        # Yellow for fighters
}


class BuildQueuePortraitLoader:
    """
    Loads and manages portrait images for designs in the build queue UI.

    Handles:
    - Loading themed portrait images from assets
    - Parsing ship class names for portrait file lookup
    - Generating colored placeholder icons when images not found
    """

    def __init__(self, design_library: DesignLibrary, session):
        """
        Initialize the portrait loader.

        Args:
            design_library: DesignLibrary for looking up designs
            session: Game session with player_empire for theme lookup
        """
        self.design_library = design_library
        self.session = session

    def load_design_portrait(self, design, size: int) -> Optional[pygame.Surface]:
        """
        Load a miniature portrait for a design.

        Args:
            design: DesignMetadata object
            size: Size of the square icon in pixels

        Returns:
            Scaled pygame.Surface or None if not found
        """
        # Get theme from session's player empire
        theme = "Federation"  # Default
        if hasattr(self.session, 'player_empire') and hasattr(self.session.player_empire, 'empire_theme_id'):
            theme = self.session.player_empire.empire_theme_id

        ship_class = getattr(design, 'ship_class', 'Unknown')
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
            os.path.join("assets", "Images", "Default_Ship_Portrait.png")
        ]

        for path in portrait_paths:
            if os.path.exists(path):
                try:
                    loaded_img = pygame.image.load(path)
                    return pygame.transform.smoothscale(loaded_img, (size, size))
                except Exception as e:
                    log_warning(f"Failed to load portrait from '{path}': {e}")
                    continue

        # Fallback: Create a colored placeholder based on vehicle type
        return self._create_placeholder(design, size)

    def load_queue_item_portrait(self, design_id: str, item_type: str, size: int) -> Optional[pygame.Surface]:
        """
        Load a miniature portrait for a queue item.

        Args:
            design_id: ID of the design
            item_type: Type of item (ship, complex, etc.)
            size: Size of the square icon in pixels

        Returns:
            Scaled pygame.Surface or None if not found
        """
        # Try to find design metadata for this design_id
        designs = self.design_library.scan_designs()
        design = next((d for d in designs if d.design_id == design_id), None)

        if design:
            return self.load_design_portrait(design, size)

        # Fallback: Create a colored placeholder based on item type
        return self._create_type_placeholder(item_type, size)

    def _create_placeholder(self, design, size: int) -> pygame.Surface:
        """
        Create a colored placeholder icon for a design.

        Args:
            design: DesignMetadata object
            size: Size of the square icon in pixels

        Returns:
            Colored pygame.Surface placeholder
        """
        placeholder = pygame.Surface((size, size))
        vehicle_type = getattr(design, 'vehicle_type', 'Ship')

        # Normalize for lookup
        type_key = vehicle_type.lower() if vehicle_type else 'ship'
        color = VEHICLE_TYPE_COLORS.get(type_key, (100, 100, 100))

        placeholder.fill(color)
        pygame.draw.rect(placeholder, (255, 255, 255), placeholder.get_rect(), 1)

        return placeholder

    def _create_type_placeholder(self, item_type: str, size: int) -> pygame.Surface:
        """
        Create a colored placeholder icon for an item type.

        Args:
            item_type: Type string (ship, complex, etc.)
            size: Size of the square icon in pixels

        Returns:
            Colored pygame.Surface placeholder
        """
        placeholder = pygame.Surface((size, size))
        type_lower = item_type.lower() if item_type else 'unknown'
        color = VEHICLE_TYPE_COLORS.get(type_lower, (100, 100, 100))

        placeholder.fill(color)
        pygame.draw.rect(placeholder, (255, 255, 255), placeholder.get_rect(), 1)

        return placeholder
