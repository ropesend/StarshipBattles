"""
Tests for game.core.constants module.

PROJ-11: Verifies constants are properly exported from core layer.
"""
from game.core.resources import ResourceCatalog


class TestPlanetaryResources:
    """Test planetary resources via ResourceCatalog (replaces legacy PLANET_RESOURCES)."""

    def test_planetary_resources_from_catalog(self):
        """ResourceCatalog should provide planetary resource IDs."""
        catalog = ResourceCatalog.from_json()
        ids = [d.id for d in catalog.by_display_group("planetary")]
        assert ids is not None

    def test_planetary_resources_is_list(self):
        """Planetary resource IDs should be a list."""
        catalog = ResourceCatalog.from_json()
        ids = [d.id for d in catalog.by_display_group("planetary")]
        assert isinstance(ids, list)

    def test_planetary_resources_has_expected_values(self):
        """Planetary resources should contain the expected resource types."""
        catalog = ResourceCatalog.from_json()
        ids = [d.id for d in catalog.by_display_group("planetary")]
        expected = ["metals", "organics", "vapors", "radioactives", "exotics"]
        assert ids == expected

    def test_planetary_resources_has_five_elements(self):
        """Planetary resources should have exactly 5 resource types."""
        catalog = ResourceCatalog.from_json()
        ids = [d.id for d in catalog.by_display_group("planetary")]
        assert len(ids) == 5

    def test_planetary_resources_elements_are_strings(self):
        """All planetary resource IDs should be strings."""
        catalog = ResourceCatalog.from_json()
        ids = [d.id for d in catalog.by_display_group("planetary")]
        for resource in ids:
            assert isinstance(resource, str)


class TestPhysicsConstants:
    """Test physics constants from core.constants."""

    def test_earth_mass_importable(self):
        """EARTH_MASS should be importable from game.core.constants."""
        from game.core.constants import EARTH_MASS
        assert EARTH_MASS is not None

    def test_earth_mass_value(self):
        """EARTH_MASS should be approximately 5.97e24 kg."""
        from game.core.constants import EARTH_MASS
        assert 5.96e24 < EARTH_MASS < 5.98e24

    def test_earth_mass_is_float(self):
        """EARTH_MASS should be a float."""
        from game.core.constants import EARTH_MASS
        assert isinstance(EARTH_MASS, float)
