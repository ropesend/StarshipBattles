"""Tests for StarImageRegistry (PROJ-231)."""
import random
import pytest
from game.strategy.data.stars import StarType
from game.strategy.generation.star_image_registry import StarImageRegistry


class TestStarImageRegistryLoading:
    """Test that the registry loads images from the manifest."""

    def test_loads_images_for_all_star_types(self):
        """Every StarType should have at least one image available."""
        registry = StarImageRegistry()
        for star_type in StarType:
            count = registry.get_image_count(star_type)
            assert count > 0, f"No images for {star_type.name}"

    def test_total_image_count(self):
        """Should load 42 images (7 colors × 6 variants)."""
        registry = StarImageRegistry()
        total = registry.get_total_image_count()
        assert total == 42

    def test_each_color_has_six_variants(self):
        """Each star type maps to a color with 6 variants."""
        registry = StarImageRegistry()
        # MAIN_SEQUENCE -> yellow (6 variants)
        assert registry.get_image_count(StarType.MAIN_SEQUENCE) == 6
        # RED_GIANT and RED_DWARF both -> red (same 6 images)
        assert registry.get_image_count(StarType.RED_GIANT) == 6
        assert registry.get_image_count(StarType.RED_DWARF) == 6
        assert registry.get_image_count(StarType.BLACK_HOLE) == 6


class TestStarImageRegistrySelection:
    """Test random image selection."""

    def test_get_random_image_returns_filename(self):
        """Should return a string filename ending in .png."""
        registry = StarImageRegistry()
        img = registry.get_random_image(StarType.MAIN_SEQUENCE)
        assert isinstance(img, str)
        assert img.endswith('.png')

    def test_get_random_image_returns_basename(self):
        """Should return just the basename, not a full path."""
        registry = StarImageRegistry()
        img = registry.get_random_image(StarType.BLUE_GIANT)
        assert '/' not in img
        assert '\\' not in img

    def test_deterministic_with_seed(self):
        """Same seed should produce same image selection."""
        registry = StarImageRegistry()
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        img1 = registry.get_random_image(StarType.MAIN_SEQUENCE, rng1)
        img2 = registry.get_random_image(StarType.MAIN_SEQUENCE, rng2)
        assert img1 == img2

    def test_produces_variety(self):
        """Multiple calls with different seeds should produce different images."""
        registry = StarImageRegistry()
        images = set()
        for seed in range(100):
            rng = random.Random(seed)
            img = registry.get_random_image(StarType.MAIN_SEQUENCE, rng)
            images.add(img)
        # With 6 variants and 100 seeds, we should see multiple unique images
        assert len(images) > 1

    def test_correct_color_for_type(self):
        """Images should match the expected color category for the star type."""
        registry = StarImageRegistry()
        # BLUE_GIANT -> blue images
        img = registry.get_random_image(StarType.BLUE_GIANT, random.Random(0))
        assert 'Blue' in img
        # BLACK_HOLE -> black images
        img = registry.get_random_image(StarType.BLACK_HOLE, random.Random(0))
        assert 'Black' in img
        # NEUTRON_STAR -> neutron images
        img = registry.get_random_image(StarType.NEUTRON_STAR, random.Random(0))
        assert 'Neutron' in img
