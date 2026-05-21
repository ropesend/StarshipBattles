"""
Service for loading and scaling modifier icons.

This service manages the mapping between modifier IDs and their corresponding
icon assets, providing scaled pygame Surfaces and handling caching.
"""
from __future__ import annotations

import os
import logging
import pygame
from typing import Dict, Optional, Tuple
from game.core.paths import Paths

logger = logging.getLogger(__name__)

MODIFIER_ICON_MAP = {
    "hardened_mount": "mod_hardened_mount.png",
    "turret_mount": "mod_turret_mount.png",
    "simple_size_mount": "mod_size_mount.png",
    "range_mount": "mod_range_mount.png",
    "facing": "mod_facing_angle.png",
    "precision_mount": "mod_precision_mount.png",
    "rapid_fire": "mod_rapid_fire.png",
    "seeker_endurance": "mod_seeker_endurance.png",
    "seeker_damage": "mod_seeker_damage.png",
    "seeker_armored": "mod_seeker_armored.png",
    "seeker_stealth": "mod_seeker_stealth.png",
    "automation": "mod_automation.png",
    "efficient_engines": "mod_efficient_engines.png",
    "efficiency_mount": "mod_efficiency_mount.png"
}

class ModifierIconService:
    """Manages modifier icon assets with caching and scaling."""

    def __init__(self, icon_size: int = 26):
        """
        Initialize the service.

        Args:
            icon_size: The target size (width and height) for icons.
        """
        self.icon_size = icon_size
        self._cache: Dict[str, pygame.Surface] = {}
        self._base_path = os.path.join(Paths.ASSET_DIR, "Images", "Modifier Icons")

    def get_icon(self, modifier_id: str) -> Optional[pygame.Surface]:
        """
        Get the scaled icon surface for a modifier ID.

        Args:
            modifier_id: The ID of the modifier.

        Returns:
            A scaled pygame.Surface, or None if the icon or mapping is missing.
        """
        if modifier_id in self._cache:
            return self._cache[modifier_id]

        filename = MODIFIER_ICON_MAP.get(modifier_id)
        if not filename:
            # Fallback for direct mod_{id}.png if not in map
            filename = f"mod_{modifier_id}.png"

        icon_path = os.path.join(self._base_path, filename)
        
        if not os.path.exists(icon_path):
            # If the specific filename doesn't exist, log warning and return None
            if modifier_id in MODIFIER_ICON_MAP:
                logger.warning(f"Modifier icon not found at {icon_path} for ID {modifier_id}")
            return None

        try:
            surface = pygame.image.load(icon_path).convert_alpha()
            if surface.get_width() != self.icon_size or surface.get_height() != self.icon_size:
                surface = pygame.transform.smoothscale(surface, (self.icon_size, self.icon_size))
            
            self._cache[modifier_id] = surface
            return surface
        except (pygame.error, OSError) as e:
            logger.error(f"Error loading modifier icon {icon_path}: {e}")
            return None

    def clear_cache(self) -> None:
        """Clear the icon cache."""
        self._cache.clear()
