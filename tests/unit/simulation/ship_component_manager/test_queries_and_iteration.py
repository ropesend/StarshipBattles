"""
Tests for ShipComponentManager - query methods, iteration, and integration tests.

PROJ-48: Split from test_ship_component_manager.py
"""
import pytest
from unittest.mock import MagicMock

from game.core.constants import LayerType


class TestGetAllComponents:
    """Tests for get_all_components method."""

    def test_get_all_components_empty_ship(self):
        """get_all_components returns empty list for ship with no components."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        all_comps = manager.get_all_components()
        assert all_comps == []

    def test_get_all_components_returns_all(self, engine_component, weapon_component, fresh_registries):
        """get_all_components returns components from all layers."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        # Add components to different layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)

        all_comps = manager.get_all_components()

        assert engine_component in all_comps
        assert weapon_component in all_comps

    def test_get_all_components_returns_fresh_list(self, engine_component, fresh_registries):
        """get_all_components returns a new list each call."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        list1 = manager.get_all_components()
        list2 = manager.get_all_components()

        assert list1 is not list2
        assert list1 == list2


class TestIterComponents:
    """Tests for iter_components method."""

    def test_iter_components_yields_layer_and_component(self, engine_component, fresh_registries):
        """iter_components yields (layer_type, component) tuples."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        items = list(manager.iter_components())

        assert len(items) >= 1
        # Find the engine component
        found = False
        for layer_type, comp in items:
            if comp is engine_component:
                assert layer_type == LayerType.OUTER
                found = True
                break
        assert found, "Engine component should be found in iteration"

    def test_iter_components_empty_ship(self):
        """iter_components yields nothing for empty ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        items = list(manager.iter_components())
        assert items == []


class TestGetComponentsByAbility:
    """Tests for get_components_by_ability method."""

    def test_get_components_by_ability_finds_matching(self, weapon_component, fresh_registries):
        """get_components_by_ability returns components with specified ability."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)
        # Component uses is_active and _is_operational for is_operational property
        weapon_component.is_active = True
        weapon_component._is_operational = True

        result = manager.get_components_by_ability('WeaponAbility')

        assert weapon_component in result

    def test_get_components_by_ability_excludes_non_operational(self, weapon_component, fresh_registries):
        """get_components_by_ability excludes non-operational components by default."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)
        # Make component non-operational
        weapon_component.is_active = False

        result = manager.get_components_by_ability('WeaponAbility')

        assert weapon_component not in result

    def test_get_components_by_ability_includes_non_operational_when_flag_false(self, weapon_component, fresh_registries):
        """get_components_by_ability includes non-operational when operational_only=False."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)
        # Make component non-operational
        weapon_component.is_active = False

        result = manager.get_components_by_ability('WeaponAbility', operational_only=False)

        assert weapon_component in result


class TestGetComponentsByLayer:
    """Tests for get_components_by_layer method."""

    def test_get_components_by_layer_returns_correct_layer(self, engine_component, fresh_registries):
        """get_components_by_layer returns components from specified layer."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        result = manager.get_components_by_layer(LayerType.OUTER)

        assert engine_component in result

    def test_get_components_by_layer_returns_empty_for_empty_layer(self):
        """get_components_by_layer returns empty list for layer with no components."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        result = manager.get_components_by_layer(LayerType.OUTER)

        assert result == []

    def test_get_components_by_layer_returns_fresh_list(self, engine_component, fresh_registries):
        """get_components_by_layer returns a new list each call."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        list1 = manager.get_components_by_layer(LayerType.OUTER)
        list2 = manager.get_components_by_layer(LayerType.OUTER)

        assert list1 is not list2


class TestHasComponents:
    """Tests for has_components method."""

    def test_has_components_returns_false_for_empty(self):
        """has_components returns False when no components."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        assert manager.has_components() is False

    def test_has_components_returns_true_when_has_components(self, engine_component, fresh_registries):
        """has_components returns True when components exist."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        assert manager.has_components() is True


class TestFindComponentWithIndex:
    """Tests for find_component_with_index method."""

    def test_find_component_with_index_finds_matching(self, engine_component, weapon_component, fresh_registries):
        """find_component_with_index returns matching component with location."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)

        result = manager.find_component_with_index(lambda c: c is weapon_component)

        assert result is not None
        layer_type, idx, comp = result
        assert layer_type == LayerType.OUTER
        assert idx == 1
        assert comp is weapon_component

    def test_find_component_with_index_returns_none_if_not_found(self, engine_component, fresh_registries):
        """find_component_with_index returns None when no match."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        result = manager.find_component_with_index(lambda c: False)

        assert result is None


class TestIntegrationWithShip:
    """Integration tests with real Ship objects."""

    def test_manager_works_with_real_ship(self, armed_ship):
        """ShipComponentManager works with actual Ship instance."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        manager = ShipComponentManager(armed_ship)
        manager.layers = armed_ship.layers  # Share layers with ship

        # Should be able to get all components
        all_comps = manager.get_all_components()
        assert len(all_comps) > 0

    def test_manager_iter_matches_ship_components(self, basic_ship):
        """iter_components matches components in ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        manager = ShipComponentManager(basic_ship)
        manager.layers = basic_ship.layers

        manager_comps = [comp for _, comp in manager.iter_components()]
        ship_comps = basic_ship.get_all_components()

        assert set(id(c) for c in manager_comps) == set(id(c) for c in ship_comps)
