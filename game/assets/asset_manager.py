from __future__ import annotations

import logging
import os
from typing import Optional

import pygame
from game.core.json_utils import load_json
from game.core.paths import Paths
from game.core.exceptions import ResourceException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)

_default_asset_manager: Optional['AssetManager'] = None


class AssetManager:
    """
    Manager for game assets (images, etc.).

    Usage:
        manager = get_default_asset_manager()
        image = manager.load_image("category", "key")

    Testing:
        - Use set_default_asset_manager(AssetManager()) to replace the default
        - Use clear() to reset caches but preserve instance
    """

    def __init__(self):
        self.assets = {}  # Cache: {key: Surface} or {key: [Surfaces]}
        self.manifest = {}
        self.manifest_path = Paths.ASSET_MANIFEST_FILE
        self.missing_texture = None
        self.star_metadata = {}
        self._load_star_metadata()

    def _load_star_metadata(self) -> None:
        """Load the star core metadata JSON."""
        metadata_path = os.path.join(Paths.ASSET_DIR, "star_metadata.json")
        if os.path.exists(metadata_path):
            self.star_metadata = load_json(metadata_path)
            logger.info(f"Loaded star metadata from {metadata_path}")
        else:
            logger.warning(f"Star metadata not found at {metadata_path}")

    def clear(self) -> None:
        """Reset all caches. Used for test isolation."""
        self.assets = {}
        self.manifest = {}
        self.missing_texture = None 
        
    def load_manifest(self, path=None) -> None:
        """Load the asset manifest JSON."""
        if path:
            self.manifest_path = path
            
        if not os.path.exists(self.manifest_path):
            logger.error(f"Asset Manifest not found: {self.manifest_path}")
            return

        data = load_json(self.manifest_path)
        if data:
            self.manifest = data
            logger.info(f"Loaded asset manifest from {self.manifest_path}")
        else:
            logger.error(f"Failed to load asset manifest from {self.manifest_path}")

    def load_image(self, category, key) -> pygame.Surface:
        """Load a single image from the manifest. Returns cached copy if available."""
        # Check cache
        cache_key = f"{category}.{key}"
        if cache_key in self.assets:
            return self.assets[cache_key]
        
        # Resolve path
        cat_data = self.manifest.get(category, {})
        file_path = cat_data.get(key)
        
        if not file_path:
            logger.warning(f"Asset not found in manifest: {category}.{key}")
            return self.get_missing_texture()

        # Load
        try:
            return self._load_image(cache_key, file_path)
        except FileNotFoundError as e:
            logger.error(f"Image file not found {file_path}: {e}")
            return self.get_missing_texture()
        except pygame.error as e:
            logger.error(f"Failed to load image {file_path} (pygame error): {e}")
            return self.get_missing_texture()

    def load_group(self, category, group_key) -> list[pygame.Surface]:
        """Load a group of images (e.g., planet variations). Returns cached copy if available."""
        cache_key = f"{category}.{group_key}"
        if cache_key in self.assets:
            return self.assets[cache_key]
            
        cat_data = self.manifest.get(category, {})
        file_paths = cat_data.get(group_key)
        
        if not file_paths or not isinstance(file_paths, list):
            logger.warning(f"Asset group not found in manifest: {category}.{group_key}")
            return [self.get_missing_texture()]

        images = []
        for i, path in enumerate(file_paths):
            sub_key = f"{cache_key}.{i}"
            try:
                images.append(self._load_image(sub_key, path))
            except FileNotFoundError as e:
                logger.error(f"Group image file not found {path}: {e}")
            except pygame.error as e:
                logger.error(f"Failed to load group image {path} (pygame error): {e}")
        
        self.assets[cache_key] = images
        return images
        
    def get_random_from_group(self, category, group_key, seed_id=None) -> pygame.Surface:
        """Get a specific item from a group deterministically using an ID."""
        group = self.load_group(category, group_key)
        if not group:
            return self.get_missing_texture()

        if seed_id is not None:
             idx = seed_id % len(group)
             return group[idx]
        return group[0]

    def load_star_image(self, image_filename: str, requested_size: int = 512) -> pygame.Surface:
        """
        Load a star image at the most appropriate resolution.
        
        Args:
            image_filename: The star image filename (basename only, e.g., "StarBlueAsset.png")
            requested_size: Target display size in pixels (default 512)
        """
        size_chain = [128, 256, 512, 1024]
        start_index = 0
        for i, size in enumerate(size_chain):
            if requested_size <= size:
                start_index = i
                break
        
        for size in size_chain[start_index:]:
            try:
                folder = self._get_star_folder_for_size(size)
                image_path = os.path.join(folder, image_filename)
                img = self.load_external_image(image_path)
                if img and img != self.get_missing_texture():
                    return img
            except (FileNotFoundError, pygame.error, ValueError, OSError) as e:
                # PROJ-381 Phase 2 (ERR-02-001): narrow to match
                # load_planet_image so MemoryError / KeyboardInterrupt /
                # other genuinely-fatal types are not silently swallowed.
                logger.warning(f"Could not load star image {image_filename} at {size}px: {e}")
                continue
                
        return self.get_missing_texture()

    def get_star_core_info(self, image_filename: str) -> dict:
        """
        Get the normalized core information (center and radius) for a star.

        Args:
            image_filename: Basename of the star image.

        Returns:
            Dict with 'centerX', 'centerY', 'radiusCore', 'radiusCorona' (all 0.0-1.0)
            Returns defaults if not found.
        """
        return self.star_metadata.get(image_filename, {
            "centerX": 0.5,
            "centerY": 0.5,
            "radiusCore": 0.25,
            "radiusCorona": 0.35
        })

    def get_star_asset_key_for_type(self, star_type_name: str) -> str:
        """Get the star asset key for a given StarType enum name.

        Uses the 'star_type_assets' section of the manifest to map
        StarType names to star image asset keys.

        Args:
            star_type_name: StarType enum name (e.g., 'MAIN_SEQUENCE', 'RED_GIANT')

        Returns:
            Asset key string (e.g., 'yellow', 'red', 'blue')
        """
        type_assets = self.manifest.get('star_type_assets', {})
        return type_assets.get(star_type_name, 'yellow')


    def load_external_image(self, path) -> pygame.Surface:
        """Load an image from an absolute or relative path, using the cache."""
        if not path:
             return self.get_missing_texture()
             
        # Normalize path for cache key
        norm_path = os.path.normpath(path)
        cache_key = f"external.{norm_path}"
        
        if cache_key in self.assets:
             return self.assets[cache_key]
             
        try:
             return self._load_image(cache_key, norm_path)
        except FileNotFoundError as e:
             logger.error(f"External image file not found {path}: {e}")
             return self.get_missing_texture()
        except pygame.error as e:
             logger.error(f"Failed to load external image {path} (pygame error): {e}")
             return self.get_missing_texture()

    def _get_planet_folder_for_size(self, size: int) -> str:
        """
        Map a resolution size to the corresponding Planets_V3 folder path.

        Args:
            size: Target resolution (128, 256, 512, 1024, or 2048)

        Returns:
            Full path to the resolution-specific folder

        Raises:
            ResourceException: If size is not a valid resolution
        """
        size_to_path = {
            128: Paths.PLANETS_V3_128_DIR,
            256: Paths.PLANETS_V3_256_DIR,
            512: Paths.PLANETS_V3_512_DIR,
            1024: Paths.PLANETS_V3_1024_DIR,
            2048: Paths.PLANETS_V3_2048_DIR,
        }

        if size not in size_to_path:
            raise ResourceException(
                f"Invalid planet image size: {size}",
                code=ErrorCode.INVALID_FORMAT.value,
                context={"requested_size": size, "valid_sizes": list(size_to_path.keys())}
            )

        return size_to_path[size]

    def _get_star_folder_for_size(self, size: int) -> str:
        """Map a resolution size to the corresponding Stars folder path."""
        size_to_path = {
            128: Paths.STARS_128_DIR,
            256: Paths.STARS_256_DIR,
            512: Paths.STARS_512_DIR,
            1024: Paths.STARS_1024_DIR,
        }
        if size not in size_to_path:
            raise ResourceException(f"Invalid star image size: {size}")
        return size_to_path[size]

    # Special stellar-object portraits live outside Planets_V3_* in their own
    # dedicated directories. See docs/03_CONVENTIONS.md (Image Assets) for the
    # split convention. Append new entries here to support future special
    # stellar objects (ringworlds, etc.) without duplicating assets.
    _STELLAR_OBJECT_FALLBACK_DIRS: tuple = (Paths.SPHERE_WORLD_DIR,)

    def load_planet_image(self, image_filename: str, requested_size: int = 512) -> pygame.Surface:
        """
        Load a planet image at the most appropriate resolution.

        Implements fallback chain: requested size → higher resolutions →
        stellar-object directories → missing texture.

        Most planet portraits live in `Planets_V3_<size>/` size folders. A few
        special stellar objects (e.g., the Dyson Sphere) live in dedicated
        `Stellar Objects/<thing>/` folders and have only one resolution. When
        the size-chain probe fails, the loader falls back to those directories
        (see `_STELLAR_OBJECT_FALLBACK_DIRS` and
        docs/03_CONVENTIONS.md Image Assets section).

        Args:
            image_filename: The planet image filename (e.g., "planet_5_994_1769750020702.png")
            requested_size: Target display size in pixels (default 512 for portraits)

        Returns:
            pygame.Surface with the loaded image, or missing texture if not found

        Examples:
            # Load for 150x150 portrait (will use 512px)
            surface = manager.load_planet_image("planet_5_994.png", 512)

            # Load for 40x40 icon (will use 128px)
            surface = manager.load_planet_image("planet_5_994.png", 128)

            # Load Dyson Sphere portrait (resolves via stellar-object fallback)
            surface = manager.load_planet_image("Sphereworld_Portrait.png", 128)
        """
        # Resolution fallback chain (try requested size, then progressively higher)
        size_chain = [128, 256, 512, 1024, 2048]
        start_index = 0

        # Find starting point in chain based on requested size
        for i, size in enumerate(size_chain):
            if requested_size <= size:
                start_index = i
                break

        # Try each resolution in order
        for size in size_chain[start_index:]:
            try:
                folder = self._get_planet_folder_for_size(size)
                image_path = os.path.join(folder, image_filename)

                # Try to load using existing load_external_image
                img = self.load_external_image(image_path)

                # If we got a real image (not missing texture), return it
                if img and img != self.get_missing_texture():
                    return img

            except (FileNotFoundError, pygame.error, ValueError) as e:
                # Log warning but continue to next resolution
                logger.warning(f"Could not load planet image {image_filename} at {size}px: {e}")
                continue

        # Size chain exhausted — try stellar-object fallback directories for
        # special portraits (e.g., Dyson Sphere) that live outside Planets_V3_*.
        for stellar_dir in self._STELLAR_OBJECT_FALLBACK_DIRS:
            try:
                image_path = os.path.join(stellar_dir, image_filename)
                img = self.load_external_image(image_path)
                if img and img != self.get_missing_texture():
                    return img
            except (FileNotFoundError, pygame.error, ValueError):
                continue

        # All resolutions and fallbacks failed - return missing texture
        logger.error(f"Could not load planet image {image_filename} at any resolution")
        return self.get_missing_texture()

    def _load_image(self, cache_key, path) -> pygame.Surface:
        """Internal load helper."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        # Extension handling
        if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
             img = pygame.image.load(path).convert()
        else:
             img = pygame.image.load(path).convert_alpha()
             
        self.assets[cache_key] = img
        return img
        
    def get_missing_texture(self) -> pygame.Surface:
        """Return a placeholder texture."""
        if self.missing_texture:
            return self.missing_texture
            
        s = pygame.Surface((32, 32))
        s.fill((255, 0, 255)) # Hot pink
        self.missing_texture = s
        return s

def get_default_asset_manager() -> AssetManager:
    """Get the module-level AssetManager instance, creating one if needed."""
    global _default_asset_manager
    if _default_asset_manager is None:
        _default_asset_manager = AssetManager()
    return _default_asset_manager


def set_default_asset_manager(manager: AssetManager) -> None:
    """Set the module-level AssetManager instance."""
    global _default_asset_manager
    _default_asset_manager = manager
