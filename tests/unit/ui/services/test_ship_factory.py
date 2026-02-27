"""
Tests for ShipFactory - UI facade for Ship creation.

PROJ-43: ShipFactory provides UI layer with Ship creation capabilities
without directly importing from game.simulation.entities.ship.
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
        ship = factory.create_from_design(design_data, registry_provider=fresh_registries)

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
        radius = factory.get_ship_radius(design_data, registry_provider=fresh_registries)

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
        ship = factory.create_from_design(design_data, registry_provider=fresh_registries)

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
        master = factory.create_from_design(design_data, registry_provider=fresh_registries)
        master.position = pygame.math.Vector2(0, 0)
        master.angle = 0

        follower1 = factory.create_from_design(design_data, registry_provider=fresh_registries)
        follower1.position = pygame.math.Vector2(100, 0)

        follower2 = factory.create_from_design(design_data, registry_provider=fresh_registries)
        follower2.position = pygame.math.Vector2(0, 100)

        ships = [master, follower1, follower2]

        # Formation data: first ship is master (formation_id first seen)
        formation_data = [
            {'ship_index': 0, 'formation_id': 'test_formation', 'rotation_mode': 'relative'},
            {'ship_index': 1, 'formation_id': 'test_formation', 'rotation_mode': 'relative'},
            {'ship_index': 2, 'formation_id': 'test_formation', 'rotation_mode': 'fixed'},
        ]

        factory.setup_formation(ships, formation_data)

        assert follower1.formation.master is master
        assert follower2.formation.master is master
        assert follower1 in master.formation.members
        assert follower2 in master.formation.members
        assert follower1.formation.rotation_mode == 'relative'
        assert follower2.formation.rotation_mode == 'fixed'

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
        ship = factory.create_from_design(design_data, registry_provider=fresh_registries)
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
        """Set up registry data for tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
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

        ship1 = factory1.create_from_design(design_data, registry_provider=fresh_registries)
        ship2 = factory2.create_from_design(design_data, registry_provider=fresh_registries)

        # Both should work independently
        assert ship1 is not None
        assert ship2 is not None
        assert ship1 is not ship2


class TestSetupFormationEdgeCases:
    """Tests for edge cases in ShipFactory.setup_formation()."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up registry data for tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        yield

    def _create_ship(self, fresh_registries, x=0, y=0):
        """Helper to create a test ship at given position."""
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
        ship = factory.create_from_design(design_data, registry_provider=fresh_registries)
        ship.position = pygame.math.Vector2(x, y)
        ship.angle = 0
        return ship

    def test_empty_formation_data(self, fresh_registries):
        """setup_formation handles empty formation_data list."""
        from game.ui.services.ship_factory import ShipFactory

        factory = ShipFactory()
        ship1 = self._create_ship(fresh_registries, 0, 0)
        ship2 = self._create_ship(fresh_registries, 100, 0)
        ships = [ship1, ship2]

        # Empty formation data should do nothing, not crash
        factory.setup_formation(ships, [])

        # Ships should not be linked
        assert ship1.formation.master is None
        assert ship2.formation.master is None
        assert len(ship1.formation.members) == 0

    def test_formation_id_none_skipped(self, fresh_registries):
        """setup_formation skips entries with formation_id=None."""
        from game.ui.services.ship_factory import ShipFactory

        factory = ShipFactory()
        ship1 = self._create_ship(fresh_registries, 0, 0)
        ship2 = self._create_ship(fresh_registries, 100, 0)
        ships = [ship1, ship2]

        formation_data = [
            {'ship_index': 0, 'formation_id': None, 'rotation_mode': 'relative'},
            {'ship_index': 1, 'formation_id': None, 'rotation_mode': 'relative'},
        ]

        factory.setup_formation(ships, formation_data)

        # Ships should not be linked (formation_id was None)
        assert ship1.formation.master is None
        assert ship2.formation.master is None

    def test_multiple_independent_formations(self, fresh_registries):
        """setup_formation correctly handles multiple independent formation groups."""
        from game.ui.services.ship_factory import ShipFactory

        factory = ShipFactory()
        ship1 = self._create_ship(fresh_registries, 0, 0)
        ship2 = self._create_ship(fresh_registries, 100, 0)
        ship3 = self._create_ship(fresh_registries, 200, 0)
        ship4 = self._create_ship(fresh_registries, 300, 0)
        ships = [ship1, ship2, ship3, ship4]

        formation_data = [
            {'ship_index': 0, 'formation_id': 'alpha', 'rotation_mode': 'relative'},
            {'ship_index': 1, 'formation_id': 'alpha', 'rotation_mode': 'relative'},
            {'ship_index': 2, 'formation_id': 'beta', 'rotation_mode': 'fixed'},
            {'ship_index': 3, 'formation_id': 'beta', 'rotation_mode': 'fixed'},
        ]

        factory.setup_formation(ships, formation_data)

        # Alpha formation: ship1 is master, ship2 is follower
        assert ship2.formation.master is ship1
        assert ship2 in ship1.formation.members

        # Beta formation: ship3 is master, ship4 is follower
        assert ship4.formation.master is ship3
        assert ship4 in ship3.formation.members

        # Cross-formation: no links
        assert ship1.formation.master is None  # master has no master
        assert ship3.formation.master is None

    def test_single_ship_in_formation(self, fresh_registries):
        """Single ship in formation becomes master with no followers."""
        from game.ui.services.ship_factory import ShipFactory

        factory = ShipFactory()
        ship1 = self._create_ship(fresh_registries, 0, 0)
        ships = [ship1]

        formation_data = [
            {'ship_index': 0, 'formation_id': 'lonely', 'rotation_mode': 'relative'},
        ]

        factory.setup_formation(ships, formation_data)

        # Single ship is master with no followers
        assert ship1.formation.master is None
        assert len(ship1.formation.members) == 0

    def test_missing_rotation_mode_defaults_to_relative(self, fresh_registries):
        """Missing rotation_mode in formation data defaults to 'relative'."""
        from game.ui.services.ship_factory import ShipFactory

        factory = ShipFactory()
        ship1 = self._create_ship(fresh_registries, 0, 0)
        ship2 = self._create_ship(fresh_registries, 100, 0)
        ships = [ship1, ship2]

        formation_data = [
            {'ship_index': 0, 'formation_id': 'test'},  # No rotation_mode
            {'ship_index': 1, 'formation_id': 'test'},  # No rotation_mode
        ]

        factory.setup_formation(ships, formation_data)

        # Should default to 'relative'
        assert ship2.formation.rotation_mode == 'relative'
