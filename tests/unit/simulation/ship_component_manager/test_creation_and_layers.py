"""
Tests for ShipComponentManager - creation, layer initialization, add/remove components.

PROJ-48: Split from test_ship_component_manager.py
"""
import pytest
from unittest.mock import MagicMock

from game.core.constants import LayerType


class TestShipComponentManagerCreation:
    """Tests for ShipComponentManager instantiation."""

    def test_component_manager_can_be_created(self):
        """ShipComponentManager can be instantiated with a ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        assert manager is not None
        assert manager._ship is ship

    def test_component_manager_stores_ship_reference(self):
        """ShipComponentManager stores reference to its ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        assert manager._ship is ship


class TestLayerInitialization:
    """Tests for layer initialization and management."""

    def test_initialize_layers_creates_hull_layer(self, fresh_registries):
        """initialize_layers creates HULL layer by default."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        assert LayerType.HULL in manager.layers
        assert hasattr(manager.layers[LayerType.HULL], 'components')
        assert manager.layers[LayerType.HULL].components == []

    def test_initialize_layers_creates_layers_from_class_def(self, fresh_registries):
        """initialize_layers creates layers based on vehicle class definition."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        # Use a real Ship with registries so initialize_layers can look up class def
        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        # Escort should have CORE, OUTER, ARMOR (plus HULL)
        assert LayerType.HULL in manager.layers
        assert LayerType.CORE in manager.layers
        assert LayerType.OUTER in manager.layers
        assert LayerType.ARMOR in manager.layers

    def test_initialize_layers_sets_layer_properties(self, fresh_registries):
        """initialize_layers sets radius_pct and restrictions for each layer."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        # Each layer should have required properties (LayerData attributes)
        for layer_type, layer_data in manager.layers.items():
            assert hasattr(layer_data, 'components')
            assert hasattr(layer_data, 'radius_pct')
            assert hasattr(layer_data, 'restrictions')
            assert hasattr(layer_data, 'max_mass_pct')


class TestAddComponent:
    """Tests for add_component method."""

    def test_add_component_to_valid_layer(self, engine_component, fresh_registries):
        """add_component adds component to specified layer."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        # Set layers on ship for validator
        ship.layers = manager.layers

        result = manager.add_component(engine_component, LayerType.OUTER)

        assert result is True
        assert engine_component in manager.layers[LayerType.OUTER].components

    def test_add_component_sets_layer_assigned(self, engine_component, fresh_registries):
        """add_component sets layer_assigned on component."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        manager.add_component(engine_component, LayerType.OUTER)

        assert engine_component.layer_assigned == LayerType.OUTER

    def test_add_component_sets_ship_reference(self, engine_component, fresh_registries):
        """add_component sets ship reference on component."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        manager.add_component(engine_component, LayerType.OUTER)

        assert engine_component.ship is ship

    def test_add_component_rejects_none(self, fresh_registries):
        """add_component returns False for None component."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        result = manager.add_component(None, LayerType.OUTER)

        assert result is False

    def test_add_component_triggers_recalculate_stats(self, engine_component, fresh_registries):
        """add_component triggers recalculate_stats on ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        ship.recalculate_stats = MagicMock()

        manager.add_component(engine_component, LayerType.OUTER)

        ship.recalculate_stats.assert_called_once()


class TestRemoveComponent:
    """Tests for remove_component method."""

    def test_remove_component_by_index(self, engine_component, fresh_registries):
        """remove_component removes component at specified index."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        manager.add_component(engine_component, LayerType.OUTER)
        removed = manager.remove_component(LayerType.OUTER, 0)

        assert removed is engine_component
        assert engine_component not in manager.layers[LayerType.OUTER].components

    def test_remove_component_invalid_index_returns_none(self, fresh_registries):
        """remove_component returns None for invalid index."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        removed = manager.remove_component(LayerType.OUTER, 99)

        assert removed is None

    def test_remove_component_triggers_recalculate_stats(self, engine_component, fresh_registries):
        """remove_component triggers recalculate_stats on ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.add_component(engine_component, LayerType.OUTER)
        ship.recalculate_stats = MagicMock()

        manager.remove_component(LayerType.OUTER, 0)

        ship.recalculate_stats.assert_called()


class TestClearNonHullComponents:
    """Tests for clear_non_hull_components method."""

    def test_clear_non_hull_components_removes_all_except_hull(self, engine_component, weapon_component, fresh_registries):
        """clear_non_hull_components removes components from all layers except HULL."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER].components.append(engine_component)
        manager.layers[LayerType.OUTER].components.append(weapon_component)
        ship.recalculate_stats = MagicMock()

        manager.clear_non_hull_components()

        assert manager.layers[LayerType.OUTER].components == []

    def test_clear_non_hull_components_preserves_hull(self, fresh_registries):
        """clear_non_hull_components preserves HULL layer components."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        # Add a mock hull component
        hull_comp = MagicMock()
        manager.layers[LayerType.HULL].components.append(hull_comp)
        ship.recalculate_stats = MagicMock()

        manager.clear_non_hull_components()

        assert hull_comp in manager.layers[LayerType.HULL].components


class TestAddComponentsBulk:
    """Tests for add_components_bulk method."""

    def test_add_components_bulk_adds_multiple_copies(self, engine_component, fresh_registries):
        """add_components_bulk adds multiple cloned copies."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        count = manager.add_components_bulk(engine_component, LayerType.OUTER, 3)

        assert count == 3
        assert len(manager.layers[LayerType.OUTER].components) == 3

    def test_add_components_bulk_returns_count_added(self, engine_component, fresh_registries):
        """add_components_bulk returns number successfully added."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        count = manager.add_components_bulk(engine_component, LayerType.OUTER, 2)

        assert count == 2
