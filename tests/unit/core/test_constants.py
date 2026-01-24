"""
Tests for game.core.constants module.

PROJ-11: Verifies constants are properly exported from core layer.
"""
import pytest


class TestPlanetResources:
    """Test PLANET_RESOURCES constant from core.constants."""

    def test_planet_resources_importable_from_core(self):
        """PLANET_RESOURCES should be importable from game.core.constants."""
        from game.core.constants import PLANET_RESOURCES
        assert PLANET_RESOURCES is not None

    def test_planet_resources_is_list(self):
        """PLANET_RESOURCES should be a list."""
        from game.core.constants import PLANET_RESOURCES
        assert isinstance(PLANET_RESOURCES, list)

    def test_planet_resources_has_expected_values(self):
        """PLANET_RESOURCES should contain the expected resource types."""
        from game.core.constants import PLANET_RESOURCES

        expected = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]
        assert PLANET_RESOURCES == expected

    def test_planet_resources_has_five_elements(self):
        """PLANET_RESOURCES should have exactly 5 resource types."""
        from game.core.constants import PLANET_RESOURCES
        assert len(PLANET_RESOURCES) == 5

    def test_planet_resources_elements_are_strings(self):
        """All elements of PLANET_RESOURCES should be strings."""
        from game.core.constants import PLANET_RESOURCES

        for resource in PLANET_RESOURCES:
            assert isinstance(resource, str)
