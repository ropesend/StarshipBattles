"""
BuildQueuePortraitLoader - Loads and caches design portraits for build queue UI.

Extracted from build_queue_screen.py as part of PROJ-63 decomposition.
PROJ-79: Added resource icon loading for column headers.
"""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Optional, Dict

import pygame

from game.ui.colors import (
    RESOURCE_METALS, RESOURCE_ORGANICS, RESOURCE_VAPORS,
    RESOURCE_RADIOACTIVES, RESOURCE_EXOTICS,
    RESOURCE_FUEL, RESOURCE_ENERGY, RESOURCE_AMMO,
    VEHICLE_SHIP, VEHICLE_FIGHTER, VEHICLE_STATION, VEHICLE_COMPLEX,
    TEXT_DIM, WHITE
)
from game.ui.utils.portraits import get_portrait_search_paths

logger = logging.getLogger(__name__)

# Resource portrait filenames in assets/Images/Resource Portraits/
RESOURCE_PORTRAIT_FILES = {
    "metals": "resource_metals_portrait.png",
    "organics": "resource_organics_portrait.png",
    "vapors": "resource_vapors_portrait.png",
    "radioactives": "resource_radioactives_portrait.png",
    "exotics": "resource_exotics_portrait.png",
    "fuel": "resource_fuel_portrait.png",
    "energy": "resource_energy_portrait.png",
    "ammo": "resource_ammo_portrait.png",
}

# Fallback colors if portrait not found
RESOURCE_FALLBACK_COLORS = {
    "metals": RESOURCE_METALS,
    "organics": RESOURCE_ORGANICS,
    "vapors": RESOURCE_VAPORS,
    "radioactives": RESOURCE_RADIOACTIVES,
    "exotics": RESOURCE_EXOTICS,
    "fuel": RESOURCE_FUEL,
    "energy": RESOURCE_ENERGY,
    "ammo": RESOURCE_AMMO,
}

if TYPE_CHECKING:
    from game.strategy.systems.design_library import DesignLibrary


# Vehicle type color map for placeholder generation
# Used when no portrait image is found
VEHICLE_TYPE_COLORS = {
    'ship': VEHICLE_SHIP,
    'complex': VEHICLE_COMPLEX,
    'planetary complex': VEHICLE_COMPLEX,
    'station': VEHICLE_STATION,
    'satellite': VEHICLE_STATION,
    'fighter': VEHICLE_FIGHTER,
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

        # Use shared portrait search paths
        portrait_paths = get_portrait_search_paths(theme, ship_class)

        for path in portrait_paths:
            if os.path.exists(path):
                try:
                    loaded_img = pygame.image.load(path)
                    return pygame.transform.smoothscale(loaded_img, (size, size))
                except pygame.error as e:
                    logger.warning(f"Failed to load portrait from '{path}': {e}")
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
        color = VEHICLE_TYPE_COLORS.get(type_key, TEXT_DIM)

        placeholder.fill(color)
        pygame.draw.rect(placeholder, WHITE, placeholder.get_rect(), 1)

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
        color = VEHICLE_TYPE_COLORS.get(type_lower, TEXT_DIM)

        placeholder.fill(color)
        pygame.draw.rect(placeholder, WHITE, placeholder.get_rect(), 1)

        return placeholder

    def load_resource_icons(self, icon_size: int = 20) -> Dict[str, pygame.Surface]:
        """Load resource portrait icons scaled to icon_size.

        PROJ-79: Used for column headers in build queue display.

        Args:
            icon_size: Size of the square icon in pixels (default 20).

        Returns:
            Dict mapping resource name to scaled pygame.Surface.
            All 5 resources are always present (fallback to colored square if file missing).
        """
        icons: Dict[str, pygame.Surface] = {}
        base_path = os.path.join("assets", "Images", "Resource Portraits")

        for resource, filename in RESOURCE_PORTRAIT_FILES.items():
            path = os.path.join(base_path, filename)
            try:
                img = pygame.image.load(path)
                icons[resource] = pygame.transform.smoothscale(img, (icon_size, icon_size))
            except (FileNotFoundError, pygame.error) as e:
                logger.warning(f"Failed to load resource portrait '{path}': {e}")
                # Create fallback colored square
                surf = pygame.Surface((icon_size, icon_size))
                color = RESOURCE_FALLBACK_COLORS.get(resource, TEXT_DIM)
                surf.fill(color)
                pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)
                icons[resource] = surf

        return icons
