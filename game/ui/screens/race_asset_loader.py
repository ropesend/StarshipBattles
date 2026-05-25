"""
Race Asset Loader - Loads race-related assets (flags, portraits).

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Provides centralized asset loading for race configuration UI.
"""
import os
import pygame
from typing import Dict, List, Optional

import logging

logger = logging.getLogger(__name__)
from game.core.paths import Paths
from game.core.ship_classes import FLEET_ICON_SHIP_CLASS
from game.ui.assets.ship_theme_manager import get_default_ship_theme_manager
from game.ui.colors import PLACEHOLDER_BORDER


class RaceAssetLoader:
    """
    Loader for race configuration assets.

    Handles loading:
    - Flags (all three shapes: rectangle, shield, triangle)
    - Portraits (full and preview sizes)
    - Placeholder surfaces for missing assets
    """

    def __init__(self):
        """Initialize the asset loader."""
        pass

    def load_flag_full(self, flag_id: str) -> List[pygame.Surface]:
        """
        Load all three shapes for a flag at full display size.

        Args:
            flag_id: Flag directory name

        Returns:
            List of [rectangle, shield, triangle] surfaces (original size, caller scales)
        """
        shapes = []
        flag_dir = os.path.join(Paths.FLAGS_PROCESSED_DIR, flag_id)

        for shape in ["rectangle", "shield", "triangle"]:
            # Try 1024px first for best quality, then 512, 256, then root
            shape_path = None
            for size_dir in ["1024", "512", "256", ""]:
                if size_dir:
                    test_path = os.path.join(flag_dir, size_dir, f"{shape}.png")
                else:
                    test_path = os.path.join(flag_dir, f"{shape}.png")
                if os.path.exists(test_path):
                    shape_path = test_path
                    break

            if shape_path:
                try:
                    surf = pygame.image.load(shape_path).convert_alpha()
                    shapes.append(surf)
                except (FileNotFoundError, OSError, pygame.error) as e:
                    logger.error(f"Failed to load flag shape {shape_path}: {e}")
                    shapes.append(self.create_placeholder(256, 256))
            else:
                shapes.append(self.create_placeholder(256, 256))

        return shapes

    def load_portrait_full(self, portrait_id: str) -> Optional[pygame.Surface]:
        """
        Load a portrait at full display size.

        Args:
            portrait_id: Portrait filename

        Returns:
            Surface (original size, caller scales as needed) or None
        """
        portrait_path = os.path.join(Paths.RACE_PORTRAITS_DIR, portrait_id)

        if os.path.exists(portrait_path):
            try:
                surf = pygame.image.load(portrait_path).convert_alpha()
                return surf
            except (FileNotFoundError, OSError, pygame.error) as e:
                logger.error(f"Failed to load portrait {portrait_path}: {e}")

        return None

    def create_placeholder(self, width: int, height: int) -> pygame.Surface:
        """
        Create a placeholder surface for missing assets.

        Args:
            width: Placeholder width in pixels
            height: Placeholder height in pixels

        Returns:
            A placeholder surface with crossed lines
        """
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, PLACEHOLDER_BORDER, surf.get_rect(), 2)
        pygame.draw.line(surf, PLACEHOLDER_BORDER, (0, 0), (width, height), 1)
        pygame.draw.line(surf, PLACEHOLDER_BORDER, (width, 0), (0, height), 1)
        return surf

    def load_portrait_preview(
        self,
        portrait_id: Optional[str],
        preview_size: int
    ) -> Optional[pygame.Surface]:
        """
        Load and scale a portrait for preview.

        Args:
            portrait_id: Portrait ID or None
            preview_size: Size in pixels for the preview

        Returns:
            Scaled surface or None if portrait_id is None or not found
        """
        if not portrait_id:
            return None

        portraits_dir = os.path.join(Paths.ASSET_DIR, "RacePortraits")
        portrait_path = os.path.join(portraits_dir, portrait_id)

        if not os.path.exists(portrait_path):
            return None

        try:
            # Load first image in the directory
            for fname in os.listdir(portrait_path):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(portrait_path, fname)
                    surf = pygame.image.load(img_path).convert_alpha()
                    # Scale to preview size
                    return pygame.transform.smoothscale(surf, (preview_size, preview_size))
        except (FileNotFoundError, OSError, pygame.error) as e:
            logger.warning(f"Failed to load portrait preview: {e}")

        return None

    def load_flag_preview(
        self,
        flag_id: Optional[str],
        preview_size: int
    ) -> Optional[pygame.Surface]:
        """
        Load and scale a flag for preview (rectangle shape only).

        Args:
            flag_id: Flag ID or None
            preview_size: Size in pixels for the preview

        Returns:
            Scaled surface or None if flag_id is None or not found
        """
        if not flag_id:
            return None

        flags_dir = os.path.join(Paths.ASSET_DIR, "RaceFlags")
        flag_path = os.path.join(flags_dir, flag_id)

        if not os.path.exists(flag_path):
            return None

        try:
            # Look for rectangle flag
            for fname in os.listdir(flag_path):
                if 'rectangle' in fname.lower() and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(flag_path, fname)
                    surf = pygame.image.load(img_path).convert_alpha()
                    # Scale to preview size
                    return pygame.transform.smoothscale(surf, (preview_size, preview_size))
            # Fallback to any image
            for fname in os.listdir(flag_path):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(flag_path, fname)
                    surf = pygame.image.load(img_path).convert_alpha()
                    return pygame.transform.smoothscale(surf, (preview_size, preview_size))
        except (FileNotFoundError, OSError, pygame.error) as e:
            logger.warning(f"Failed to load flag preview: {e}")

        return None

    def load_empire_race_assets(self, flag_id: str) -> Dict[str, pygame.Surface]:
        """
        Load race flag assets for empire display in strategy view.

        Args:
            flag_id: The race flag identifier (e.g., 'flag_2fl0bh')

        Returns:
            Dict with keys 'colony' (rectangle flag) and 'fleet_flag' (shield flag).
            Returns empty dict for missing flag_id.
        """
        result = {}

        if not flag_id:
            return result

        # Load full flags using existing method
        shapes = self.load_flag_full(flag_id)

        # shapes[0] = rectangle, shapes[1] = shield, shapes[2] = triangle
        if len(shapes) >= 1 and shapes[0]:
            result['colony'] = shapes[0]
        if len(shapes) >= 2 and shapes[1]:
            result['fleet_flag'] = shapes[1]

        return result

    def load_empire_theme_assets(self, theme_id: str) -> Dict[str, pygame.Surface]:
        """
        Load theme-based assets for empire display in strategy view.

        Delegates to :class:`ShipThemeManager` (PROJ-314), the canonical
        reader of ``theme.json``'s ``assets:`` schema. The fleet-icon ship
        class is governed by :data:`FLEET_ICON_SHIP_CLASS`.

        Args:
            theme_id: The empire theme identifier (e.g., 'Federation', 'Atlantians')

        Returns:
            Dict with key 'fleet' when the theme declares the fleet-icon
            skin and the file is present on disk; empty dict otherwise.
        """
        if not theme_id:
            return {}

        manager = get_default_ship_theme_manager()
        manager.initialize()

        if manager.get_skin_path(theme_id, FLEET_ICON_SHIP_CLASS) is None:
            return {}

        return {'fleet': manager.load_image(theme_id, FLEET_ICON_SHIP_CLASS)}

    def load_all_empire_assets(self, empire) -> Dict[str, pygame.Surface]:
        """
        Load all visual assets for an empire (flags and fleet icon).

        Race assets take precedence over theme assets for 'colony' key.

        Args:
            empire: Empire object with flag_id and empire_theme_id attributes

        Returns:
            Dict with keys 'colony', 'fleet', and optionally 'fleet_flag'.
        """
        result = {}

        # Load theme assets first (lower priority)
        if empire.empire_theme_id:
            theme_assets = self.load_empire_theme_assets(empire.empire_theme_id)
            result.update(theme_assets)

        # Load race assets second (higher priority - overwrites theme 'colony')
        if empire.flag_id:
            race_assets = self.load_empire_race_assets(empire.flag_id)
            result.update(race_assets)

        return result
