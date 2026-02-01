"""
Planet Image Registry - Maps planet types to available images.

This module provides a registry for assigning persistent planet images during
galaxy generation. Each planet type has a set of available images, and the
registry handles random selection and fallbacks for types with no images.
"""
import random
from typing import Dict, List, Optional

from game.core.paths import Paths
from game.core.json_utils import load_json
from game.core.logger import log_info, log_warning, log_error
from game.strategy.data.planet import PlanetType


# Type-specific fallbacks for missing/sparse image types
_TYPE_FALLBACKS: Dict[PlanetType, PlanetType] = {
    PlanetType.CHTHONIAN: PlanetType.BARREN,    # Stripped core looks rocky
    PlanetType.ICE_DWARF: PlanetType.CRYOPLANET,  # Similar icy appearance
    PlanetType.PLANETOID: PlanetType.BARREN,    # Small rocky bodies
}


class PlanetImageRegistry:
    """Registry for planet type to image mappings.

    Loads planet classifications from JSON and provides random image selection
    for each planet type. Uses singleton pattern for efficient reuse.
    """

    _instance: Optional['PlanetImageRegistry'] = None

    def __new__(cls) -> 'PlanetImageRegistry':
        """Singleton pattern - return existing instance if available."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry by loading classifications."""
        if self._initialized:
            return

        self._type_to_images: Dict[PlanetType, List[str]] = {
            ptype: [] for ptype in PlanetType
        }
        self._load_classifications()
        self._initialized = True

    def _load_classifications(self) -> None:
        """Load planet classifications from JSON file."""
        classifications_path = Paths.PLANET_CLASSIFICATIONS_FILE

        data = load_json(classifications_path)
        if data is None:
            log_error(f"Failed to load planet classifications from {classifications_path}")
            return

        # Build reverse index: PlanetType -> List[filename]
        for filename, type_name in data.items():
            try:
                planet_type = PlanetType[type_name]
                self._type_to_images[planet_type].append(filename)
            except KeyError:
                log_warning(f"Unknown planet type '{type_name}' for image '{filename}'")

        # Log distribution
        total = sum(len(imgs) for imgs in self._type_to_images.values())
        log_info(f"Loaded {total} planet images across {len(PlanetType)} types")

    def get_random_image(self, planet_type: PlanetType, rng: Optional[random.Random] = None) -> str:
        """Get a random image filename for the given planet type.

        Args:
            planet_type: The type of planet to get an image for
            rng: Random number generator (uses global random if None)

        Returns:
            Image filename (e.g., "planet_5_994_1769750020702.png")
            Returns empty string if no images available even with fallbacks
        """
        if rng is None:
            rng = random.Random()

        # Try direct type first
        images = self._type_to_images.get(planet_type, [])

        # Apply fallback if needed
        if not images:
            fallback_type = _TYPE_FALLBACKS.get(planet_type)
            if fallback_type:
                images = self._type_to_images.get(fallback_type, [])

        # Ultimate fallback to BARREN (should have plenty of images)
        if not images:
            images = self._type_to_images.get(PlanetType.BARREN, [])

        if not images:
            log_warning(f"No images available for planet type {planet_type.name}")
            return ""

        return rng.choice(images)

    def get_random_rotation(self, rng: Optional[random.Random] = None) -> float:
        """Get a random rotation value for visual variety.

        Args:
            rng: Random number generator (uses global random if None)

        Returns:
            Random float from 0.0 to 360.0 degrees
        """
        if rng is None:
            rng = random.Random()
        return rng.uniform(0.0, 360.0)

    def get_image_count(self, planet_type: PlanetType) -> int:
        """Get the number of available images for a planet type.

        Args:
            planet_type: The planet type to check

        Returns:
            Number of available images (not counting fallbacks)
        """
        return len(self._type_to_images.get(planet_type, []))

    def get_total_image_count(self) -> int:
        """Get the total number of loaded images.

        Returns:
            Total count of all images across all types
        """
        return sum(len(imgs) for imgs in self._type_to_images.values())

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (primarily for testing)."""
        cls._instance = None
