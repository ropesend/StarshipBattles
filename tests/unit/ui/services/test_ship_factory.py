"""
Tests for ShipFactory - UI facade for Ship creation.

PROJ-43: ShipFactory provides UI layer with Ship creation capabilities
without directly importing from game.simulation.entities.ship.
"""
import pytest
import pygame
import os

from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


class TestShipFactory:
    """Tests for ShipFactory class."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up registry data for tests."""
        mgr = RegistryManager.instance()
        mgr.hydrate(
            fresh_registries.components,
            fresh_registries.modifiers,
            fresh_registries.vehicle_classes
        )
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

        factory = ShipFactory()
        ship = factory.create_from_design(design_data, registries=fresh_registries)

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

        factory = ShipFactory()
        radius = factory.get_ship_radius(design_data, registries=fresh_registries)

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

        factory = ShipFactory()
        ship = factory.create_from_design(design_data, registries=fresh_registries)

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

    def test_setup_formation_links_ships(self, fresh_registries):
        """ShipFactory.setup_formation should link ships in formation."""
        from game.ui.services.ship_factory import ShipFactory
        import pygame

        design_data = {
            "name": "Formation Ship",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        factory = ShipFactory()
        master = factory.create_from_design(design_data, registries=fresh_registries)
        master.position = pygame.math.Vector2(0, 0)
        master.angle = 0

        follower1 = factory.create_from_design(design_data, registries=fresh_registries)
        follower1.position = pygame.math.Vector2(100, 0)

        follower2 = factory.create_from_design(design_data, registries=fresh_registries)
        follower2.position = pygame.math.Vector2(0, 100)

        ships = [master, follower1, follower2]

        # Formation data: first ship is master (formation_id first seen)
        formation_data = [
            {'ship_index': 0, 'formation_id': 'test_formation', 'rotation_mode': 'relative'},
            {'ship_index': 1, 'formation_id': 'test_formation', 'rotation_mode': 'relative'},
            {'ship_index': 2, 'formation_id': 'test_formation', 'rotation_mode': 'fixed'},
        ]

        factory.setup_formation(ships, formation_data)

        assert follower1.formation_master is master
        assert follower2.formation_master is master
        assert follower1 in master.formation_members
        assert follower2 in master.formation_members
        assert follower1.formation_rotation_mode == 'relative'
        assert follower2.formation_rotation_mode == 'fixed'

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

        factory = ShipFactory()
        ship = factory.create_from_design(design_data, registries=fresh_registries)
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


class TestShipFactoryStaticMethods:
    """Tests for any static or class methods on ShipFactory."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up registry data for tests."""
        mgr = RegistryManager.instance()
        mgr.hydrate(
            fresh_registries.components,
            fresh_registries.modifiers,
            fresh_registries.vehicle_classes
        )
        yield

    def test_factory_can_be_used_without_instance(self, fresh_registries):
        """Factory methods can be called on instance without requiring singleton."""
        from game.ui.services.ship_factory import ShipFactory

        factory1 = ShipFactory()
        factory2 = ShipFactory()

        design_data = {
            "name": "Test",
            "ship_class": "Escort",
            "theme_id": "default",
            "color": [255, 255, 255],
            "layers": {}
        }

        ship1 = factory1.create_from_design(design_data, registries=fresh_registries)
        ship2 = factory2.create_from_design(design_data, registries=fresh_registries)

        # Both should work independently
        assert ship1 is not None
        assert ship2 is not None
        assert ship1 is not ship2
