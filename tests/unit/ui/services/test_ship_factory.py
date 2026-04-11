"""
Tests for ShipFactory - UI facade for Ship creation.

PROJ-43: ShipFactory provides UI layer with Ship creation capabilities
without directly importing from game.simulation.entities.ship.
PROJ-211: ShipFactory now requires registry_provider (no fallback).
"""
import pytest
import pygame
import os

from tests.fixtures.paths import get_project_root, get_data_dir


class TestShipFactory:
    """Tests for ShipFactory class."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up registry data for tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        self._registries = fresh_registries
        yield

    def test_create_from_design_returns_ship(self, fresh_registries):
        """ShipFactory.create_from_design should create a Ship from dict data."""
        from game.ui.services.ship_factory import ShipFactory

        design_data = {
            "name": "Test Ship",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        # PROJ-211: registry_provider is now required
        factory = ShipFactory(registry_provider=fresh_registries)
        ship = factory.create_from_design(design_data)

        assert ship is not None
        assert ship.name == "Test Ship"
        assert ship.ship_class == "Escort"

    def test_get_ship_radius_without_full_ship(self, fresh_registries):
        """ShipFactory.get_ship_radius should return radius without needing ship reference."""
        from game.ui.services.ship_factory import ShipFactory

        design_data = {
            "name": "Test Ship",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        factory = ShipFactory(registry_provider=fresh_registries)
        radius = factory.get_ship_radius(design_data)

        assert radius > 0
        assert isinstance(radius, float)

    def test_configure_ship_sets_properties(self, fresh_registries):
        """ShipFactory.configure_ship should set ship position, angle, team_id, etc."""
        from game.ui.services.ship_factory import ShipFactory
        import pygame

        design_data = {
            "name": "Test Ship",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        factory = ShipFactory(registry_provider=fresh_registries)
        ship = factory.create_from_design(design_data)

        factory.configure_ship(
            ship,
            position=pygame.math.Vector2(1000, 2000),
            angle=45.0,
            team_id=1,
            ai_strategy="aggressive_short",
            source_file="test_ship.json"
        )

        assert ship.position.x == 1000
        assert ship.position.y == 2000
        assert ship.angle == 45.0
        assert ship.team_id == 1
        assert ship.ai_strategy == "aggressive_short"
        assert ship.source_file == "test_ship.json"

    def test_create_and_configure_combined(self, fresh_registries):
        """Test full workflow: create, configure, recalculate."""
        from game.ui.services.ship_factory import ShipFactory
        import pygame

        design_data = {
            "name": "Full Test",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        factory = ShipFactory(registry_provider=fresh_registries)
        ship = factory.create_from_design(design_data)
        factory.configure_ship(
            ship,
            position=pygame.math.Vector2(500, 500),
            angle=90.0,
            team_id=0,
            ai_strategy="standard_ranged",
            source_file="test.json"
        )
        ship.recalculate_stats()

        assert ship.radius > 0
        assert ship.team_id == 0
        assert ship.position.x == 500

    def test_raises_when_none_provider(self, fresh_registries):
        """PROJ-211: Test ShipFactory raises ValidationException when None provider."""
        from game.ui.services.ship_factory import ShipFactory
        from game.core.exceptions import ValidationException

        with pytest.raises(ValidationException) as exc_info:
            ShipFactory(registry_provider=None)

        assert "registry_provider is required" in str(exc_info.value)


class TestShipFactoryStaticMethods:
    """Tests for any static or class methods on ShipFactory."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up registry data for tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        self._registries = fresh_registries
        yield

    def test_factory_can_be_used_without_instance(self, fresh_registries):
        """Factory methods can be called on instance without requiring singleton."""
        from game.ui.services.ship_factory import ShipFactory

        factory1 = ShipFactory(registry_provider=fresh_registries)
        factory2 = ShipFactory(registry_provider=fresh_registries)

        design_data = {
            "name": "Test",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        ship1 = factory1.create_from_design(design_data)
        ship2 = factory2.create_from_design(design_data)

        # Both should work independently
        assert ship1 is not None
        assert ship2 is not None
        assert ship1 is not ship2


