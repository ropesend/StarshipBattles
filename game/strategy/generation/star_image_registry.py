"""
Star Image Registry - Maps star types to available variant images.

This module provides a registry for assigning persistent star images during
galaxy generation. Each star type maps to a color category with multiple
visual variants. The registry reads from the asset manifest.

PROJ-231: Star List Panel / Star image variant support.
"""
import logging
import os
import random
from typing import Dict, List, Optional

from game.core.paths import Paths
from game.core.json_utils import load_json
from game.strategy.data.stars import StarType

logger = logging.getLogger(__name__)


class StarImageRegistry:
    """Registry for star type to image variant mappings.

    Reads star image paths from the asset manifest and the star_type_assets
    mapping to build a StarType -> List[basename] lookup. Should be instantiated
    once and injected as a dependency into StarGenerator.
    """

    def __init__(self) -> None:
        """Initialize the registry by loading from the asset manifest."""
        self._type_to_images: Dict[StarType, List[str]] = {
            stype: [] for stype in StarType
        }
        self._load_from_manifest()

    def _load_from_manifest(self) -> None:
        """Load star image data from asset_manifest.json."""
        manifest = load_json(Paths.ASSET_MANIFEST_FILE)
        if manifest is None:
            logger.error("Failed to load asset manifest for star images")
            return

        stars_section = manifest.get('stars', {})
        type_assets = manifest.get('star_type_assets', {})

        # Build color_key -> List[basename] from the stars section
        color_to_basenames: Dict[str, List[str]] = {}
        for color_key, paths in stars_section.items():
            if not isinstance(paths, list):
                continue
            basenames = [os.path.basename(p) for p in paths]
            color_to_basenames[color_key] = basenames

        # Map StarType -> List[basename] using star_type_assets
        for type_name, color_key in type_assets.items():
            try:
                star_type = StarType[type_name]
            except KeyError:
                logger.warning(f"Unknown StarType '{type_name}' in star_type_assets")
                continue

            basenames = color_to_basenames.get(color_key, [])
            self._type_to_images[star_type] = basenames

        total = sum(len(imgs) for imgs in self._type_to_images.values())
        unique = len(set(img for imgs in self._type_to_images.values() for img in imgs))
        logger.info(f"Loaded {unique} unique star images across {len(StarType)} types ({total} total mappings)")

    def get_random_image(self, star_type: StarType, rng: Optional[random.Random] = None) -> str:
        """Get a random image filename for the given star type.

        Args:
            star_type: The type of star to get an image for
            rng: Random number generator (uses global random if None)

        Returns:
            Image filename basename (e.g., "StarBlueVariant_3.png")
            Returns empty string if no images available
        """
        if rng is None:
            rng = random.Random()

        images = self._type_to_images.get(star_type, [])
        if not images:
            logger.warning(f"No images available for star type {star_type.name}")
            return ""

        return rng.choice(images)

    def get_image_count(self, star_type: StarType) -> int:
        """Get the number of available images for a star type.

        Args:
            star_type: The star type to check

        Returns:
            Number of available images
        """
        return len(self._type_to_images.get(star_type, []))

    def get_total_image_count(self) -> int:
        """Get the total number of unique images across all types.

        Returns:
            Total count of unique image filenames
        """
        all_images = set()
        for images in self._type_to_images.values():
            all_images.update(images)
        return len(all_images)
