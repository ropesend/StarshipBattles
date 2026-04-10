"""
Tests for game.core.constants module.

PROJ-11: Verifies constants are properly exported from core layer.
"""
from game.core.resources import ResourceCatalog


class TestPlanetaryResources:
    """Test planetary resources via ResourceCatalog (replaces legacy PLANET_RESOURCES)."""

    def test_planetary_resources_has_expected_values(self):
        """Planetary resources should contain the expected resource types."""
        catalog = ResourceCatalog.from_json()
        ids = [d.id for d in catalog.by_display_group("planetary")]
        expected = ["metals", "organics", "vapors", "radioactives", "exotics"]
        assert ids == expected


class TestPhysicsConstants:
    """Test physics constants from core.constants."""

    def test_earth_mass_value(self):
        """EARTH_MASS should be approximately 5.97e24 kg."""
        from game.core.constants import EARTH_MASS
        assert 5.96e24 < EARTH_MASS < 5.98e24
