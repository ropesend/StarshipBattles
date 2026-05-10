"""Tests for ship design factory functions.

PROJ-38: Migrated to use fresh_registries fixture for cleaner test setup.
PROJ-50: Updated to pass registries directly to design functions.
"""
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.designs import create_brick, create_interceptor


class TestDesignFactories:
    """Test programmatic ship creation functions."""

    def test_create_brick_returns_ship(self, fresh_registries):
        """create_brick should return a valid Ship object."""
        ship = create_brick(100, 200, registries=fresh_registries)

        assert isinstance(ship, Ship)
        assert ship.name == "The Brick"
        assert ship.position.x == 100
        assert ship.position.y == 200

    def test_create_brick_has_bridge(self, fresh_registries):
        """create_brick ship should have a bridge component."""
        ship = create_brick(0, 0, registries=fresh_registries)

        core_components = ship.layers[LayerType.CORE].components
        has_bridge = any(c.type_str == 'Bridge' for c in core_components)

        assert has_bridge, "Brick should have a Bridge in CORE layer"

    def test_create_brick_has_engines(self, fresh_registries):
        """create_brick ship should have engine components."""
        ship = create_brick(0, 0, registries=fresh_registries)

        all_components = ship.get_all_components()

        has_engine = any(c.has_ability('CombatPropulsion') for c in all_components)
        assert has_engine, "Brick should have engines"

    def test_create_brick_has_armor(self, fresh_registries):
        """create_brick ship should have armor plates."""
        ship = create_brick(0, 0, registries=fresh_registries)

        armor_components = ship.layers[LayerType.ARMOR].components
        assert len(armor_components) > 0, "Brick should have armor"

    def test_create_interceptor_returns_ship(self, fresh_registries):
        """create_interceptor should return a valid Ship object."""
        ship = create_interceptor(300, 400, registries=fresh_registries)

        assert isinstance(ship, Ship)
        assert ship.name == "The Interceptor"
        assert ship.position.x == 300
        assert ship.position.y == 400

    def test_create_interceptor_has_bridge(self, fresh_registries):
        """create_interceptor ship should have a bridge component."""
        ship = create_interceptor(0, 0, registries=fresh_registries)

        core_components = ship.layers[LayerType.CORE].components
        has_bridge = any(c.type_str == 'Bridge' for c in core_components)

        assert has_bridge, "Interceptor should have a Bridge in CORE layer"

    def test_create_interceptor_has_weapons(self, fresh_registries):
        """create_interceptor ship should have weapons."""
        ship = create_interceptor(0, 0, registries=fresh_registries)

        outer_components = ship.layers[LayerType.OUTER].components
        # Should have railguns in OUTER layer
        has_weapons = any(c.has_ability('WeaponAbility') for c in outer_components)

        assert has_weapons, "Interceptor should have weapons"

    def test_designs_can_recalculate_stats(self, fresh_registries):
        """Design ships should be able to recalculate stats without error."""
        brick = create_brick(0, 0, registries=fresh_registries)
        interceptor = create_interceptor(0, 0, registries=fresh_registries)

        # Should not raise any exceptions
        brick.recalculate_stats()
        interceptor.recalculate_stats()

        # Should have positive mass after recalculating
        assert brick.mass > 0
        assert interceptor.mass > 0
