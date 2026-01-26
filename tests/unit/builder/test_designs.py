"""Tests for ship design factory functions."""
import pytest
import pygame

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components  # Phase 7: Removed legacy class imports
from game.simulation.designs import create_brick, create_interceptor
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


class TestDesignFactories:
    """Test programmatic ship creation functions."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        pygame.init()
        initialize_ship_data(str(get_project_root()))
        load_components(str(get_data_dir() / "components.json"))
        yield
        pygame.quit()
        RegistryManager.instance().clear()

    def test_create_brick_returns_ship(self):
        """create_brick should return a valid Ship object."""
        ship = create_brick(100, 200)

        assert isinstance(ship, Ship)
        assert ship.name == "The Brick"
        assert ship.position.x == 100
        assert ship.position.y == 200

    def test_create_brick_has_bridge(self):
        """create_brick ship should have a bridge component."""
        ship = create_brick(0, 0)

        core_components = ship.layers[LayerType.CORE]['components']
        has_bridge = any(c.type_str == 'Bridge' for c in core_components)

        assert has_bridge, "Brick should have a Bridge in CORE layer"

    def test_create_brick_has_engines(self):
        """create_brick ship should have engine components."""
        ship = create_brick(0, 0)

        all_components = ship.get_all_components()

        has_engine = any(c.has_ability('CombatPropulsion') for c in all_components)
        assert has_engine, "Brick should have engines"

    def test_create_brick_has_armor(self):
        """create_brick ship should have armor plates."""
        ship = create_brick(0, 0)

        armor_components = ship.layers[LayerType.ARMOR]['components']
        assert len(armor_components) > 0, "Brick should have armor"

    def test_create_interceptor_returns_ship(self):
        """create_interceptor should return a valid Ship object."""
        ship = create_interceptor(300, 400)

        assert isinstance(ship, Ship)
        assert ship.name == "The Interceptor"
        assert ship.position.x == 300
        assert ship.position.y == 400

    def test_create_interceptor_has_bridge(self):
        """create_interceptor ship should have a bridge component."""
        ship = create_interceptor(0, 0)

        core_components = ship.layers[LayerType.CORE]['components']
        has_bridge = any(c.type_str == 'Bridge' for c in core_components)

        assert has_bridge, "Interceptor should have a Bridge in CORE layer"

    def test_create_interceptor_has_weapons(self):
        """create_interceptor ship should have weapons."""
        ship = create_interceptor(0, 0)

        outer_components = ship.layers[LayerType.OUTER]['components']
        # Should have railguns in OUTER layer
        has_weapons = any(c.has_ability('WeaponAbility') for c in outer_components)

        assert has_weapons, "Interceptor should have weapons"

    def test_designs_can_recalculate_stats(self):
        """Design ships should be able to recalculate stats without error."""
        brick = create_brick(0, 0)
        interceptor = create_interceptor(0, 0)

        # Should not raise any exceptions
        brick.recalculate_stats()
        interceptor.recalculate_stats()

        # Should have positive mass after recalculating
        assert brick.mass > 0
        assert interceptor.mass > 0
