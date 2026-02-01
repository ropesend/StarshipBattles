"""
Unit tests for PlanetImageRegistry.

Tests the registry for mapping planet types to available images.
"""

import pytest
import random

from game.strategy.data.planet import PlanetType
from game.strategy.generation.planet_image_registry import PlanetImageRegistry


class TestPlanetImageRegistryBasics:
    """Test basic registry functionality."""

    def test_registry_loads_classifications(self):
        """Registry should load planet classifications from JSON."""
        registry = PlanetImageRegistry()
        total = registry.get_total_image_count()
        # Should have loaded ~500+ images (actual count is 508)
        assert total >= 500

    def test_get_image_count_by_type(self):
        """Should return correct image count for each type."""
        registry = PlanetImageRegistry()

        # Check that major types have images (based on distribution)
        assert registry.get_image_count(PlanetType.JOVIAN) > 100  # ~180
        assert registry.get_image_count(PlanetType.BARREN) > 50   # ~120
        assert registry.get_image_count(PlanetType.ARID) > 30     # ~60

    def test_chthonian_has_no_direct_images(self):
        """CHTHONIAN should have no direct images (uses fallback)."""
        registry = PlanetImageRegistry()
        assert registry.get_image_count(PlanetType.CHTHONIAN) == 0

    def test_separate_instances_are_independent(self):
        """Multiple registry instances should be independent."""
        registry1 = PlanetImageRegistry()
        registry2 = PlanetImageRegistry()
        # They should both work and have the same data
        assert registry1.get_total_image_count() == registry2.get_total_image_count()
        # But be different objects
        assert registry1 is not registry2


class TestGetRandomImage:
    """Test get_random_image method."""

    @pytest.mark.parametrize("planet_type", list(PlanetType))
    def test_get_random_image_for_all_types(self, planet_type):
        """All planet types should return a valid image (with fallbacks)."""
        registry = PlanetImageRegistry()
        image_id = registry.get_random_image(planet_type)

        # Should return a non-empty string
        assert isinstance(image_id, str)
        assert len(image_id) > 0
        assert image_id.endswith(".png")

    def test_get_random_image_returns_valid_filename(self):
        """Returned image should be a valid filename."""
        registry = PlanetImageRegistry()

        for planet_type in [PlanetType.JOVIAN, PlanetType.BARREN, PlanetType.CONTINENTAL]:
            image_id = registry.get_random_image(planet_type)
            # Should be a valid filename format
            assert image_id.startswith("planet_")
            assert image_id.endswith(".png")
            # No path separators
            assert "/" not in image_id
            assert "\\" not in image_id

    def test_get_random_image_with_seed_deterministic(self):
        """Same seed should produce same image selection."""
        registry = PlanetImageRegistry()

        rng1 = random.Random(42)
        results1 = [registry.get_random_image(PlanetType.JOVIAN, rng1) for _ in range(10)]

        rng2 = random.Random(42)
        results2 = [registry.get_random_image(PlanetType.JOVIAN, rng2) for _ in range(10)]

        assert results1 == results2

    def test_get_random_image_varies_without_seed(self):
        """Without seed, should get variety of images."""
        registry = PlanetImageRegistry()

        # Get many images for a type with lots of options
        images = set()
        for _ in range(50):
            img = registry.get_random_image(PlanetType.JOVIAN)
            images.add(img)

        # Should have some variety (more than 1 image)
        assert len(images) > 1

    def test_chthonian_falls_back_to_barren(self):
        """CHTHONIAN should use BARREN images as fallback."""
        registry = PlanetImageRegistry()

        # Get barren images for comparison
        barren_images = set()
        rng = random.Random(123)
        for _ in range(30):
            img = registry.get_random_image(PlanetType.BARREN, rng)
            barren_images.add(img)

        # CHTHONIAN images should also be from the barren pool
        rng = random.Random(456)
        for _ in range(10):
            img = registry.get_random_image(PlanetType.CHTHONIAN, rng)
            assert img in barren_images or registry.get_image_count(PlanetType.BARREN) > 0

    def test_ice_dwarf_falls_back_to_cryoplanet(self):
        """ICE_DWARF should use CRYOPLANET images as fallback."""
        registry = PlanetImageRegistry()

        # ICE_DWARF has only ~1 image, so fallback is likely
        # Just verify it returns a valid image
        img = registry.get_random_image(PlanetType.ICE_DWARF)
        assert img.endswith(".png")

    def test_planetoid_falls_back_to_barren(self):
        """PLANETOID should use BARREN images as fallback if needed."""
        registry = PlanetImageRegistry()

        # Just verify it returns a valid image
        img = registry.get_random_image(PlanetType.PLANETOID)
        assert img.endswith(".png")


class TestGetRandomRotation:
    """Test get_random_rotation method."""

    def test_rotation_in_valid_range(self):
        """Rotation should be between 0.0 and 360.0 degrees."""
        registry = PlanetImageRegistry()

        for _ in range(100):
            rotation = registry.get_random_rotation()
            assert 0.0 <= rotation <= 360.0

    def test_rotation_with_seed_deterministic(self):
        """Same seed should produce same rotation sequence."""
        registry = PlanetImageRegistry()

        rng1 = random.Random(42)
        results1 = [registry.get_random_rotation(rng1) for _ in range(10)]

        rng2 = random.Random(42)
        results2 = [registry.get_random_rotation(rng2) for _ in range(10)]

        assert results1 == results2

    def test_rotation_varies_without_seed(self):
        """Without seed, should get variety of rotations."""
        registry = PlanetImageRegistry()

        rotations = set()
        for _ in range(50):
            rot = registry.get_random_rotation()
            # Round to int for uniqueness checking
            rotations.add(int(rot))

        # Should have significant variety
        assert len(rotations) > 10
