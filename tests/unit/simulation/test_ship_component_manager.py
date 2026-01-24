"""
Tests for ShipComponentManager - extracted component management from Ship class.

Follows TDD: Tests written first, then implementation.
This module tests the ShipComponentManager class which handles:
- Adding/removing components
- Layer management
- Component queries (get_all, get_by_ability, get_by_layer)
- Component iteration
- Layer initialization

PROJ-12: God Class Decomposition - Phase 2
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import List, Tuple

from game.simulation.components.component import Component, LayerType, create_component


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

    def test_initialize_layers_creates_hull_layer(self):
        """initialize_layers creates HULL layer by default."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        assert LayerType.HULL in manager.layers
        assert 'components' in manager.layers[LayerType.HULL]
        assert manager.layers[LayerType.HULL]['components'] == []

    def test_initialize_layers_creates_layers_from_class_def(self):
        """initialize_layers creates layers based on vehicle class definition."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        # Escort should have CORE, OUTER, ARMOR (plus HULL)
        assert LayerType.HULL in manager.layers
        assert LayerType.CORE in manager.layers
        assert LayerType.OUTER in manager.layers
        assert LayerType.ARMOR in manager.layers

    def test_initialize_layers_sets_layer_properties(self):
        """initialize_layers sets radius_pct and restrictions for each layer."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager

        ship = MagicMock()
        ship.ship_class = "Escort"

        manager = ShipComponentManager(ship)
        manager.initialize_layers()

        # Each layer should have required properties
        for layer_type, layer_data in manager.layers.items():
            assert 'components' in layer_data
            assert 'radius_pct' in layer_data
            assert 'restrictions' in layer_data
            assert 'max_mass_pct' in layer_data


class TestAddComponent:
    """Tests for add_component method."""

    def test_add_component_to_valid_layer(self, engine_component):
        """add_component adds component to specified layer."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        # Set layers on ship for validator
        ship.layers = manager.layers

        result = manager.add_component(engine_component, LayerType.OUTER)

        assert result is True
        assert engine_component in manager.layers[LayerType.OUTER]['components']

    def test_add_component_sets_layer_assigned(self, engine_component):
        """add_component sets layer_assigned on component."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        manager.add_component(engine_component, LayerType.OUTER)

        assert engine_component.layer_assigned == LayerType.OUTER

    def test_add_component_sets_ship_reference(self, engine_component):
        """add_component sets ship reference on component."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        manager.add_component(engine_component, LayerType.OUTER)

        assert engine_component.ship is ship

    def test_add_component_rejects_none(self):
        """add_component returns False for None component."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        result = manager.add_component(None, LayerType.OUTER)

        assert result is False

    def test_add_component_triggers_recalculate_stats(self, engine_component):
        """add_component triggers recalculate_stats on ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        ship.recalculate_stats = MagicMock()

        manager.add_component(engine_component, LayerType.OUTER)

        ship.recalculate_stats.assert_called_once()


class TestRemoveComponent:
    """Tests for remove_component method."""

    def test_remove_component_by_index(self, engine_component):
        """remove_component removes component at specified index."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        manager.add_component(engine_component, LayerType.OUTER)
        removed = manager.remove_component(LayerType.OUTER, 0)

        assert removed is engine_component
        assert engine_component not in manager.layers[LayerType.OUTER]['components']

    def test_remove_component_invalid_index_returns_none(self):
        """remove_component returns None for invalid index."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        removed = manager.remove_component(LayerType.OUTER, 99)

        assert removed is None

    def test_remove_component_triggers_recalculate_stats(self, engine_component):
        """remove_component triggers recalculate_stats on ship."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.add_component(engine_component, LayerType.OUTER)
        ship.recalculate_stats = MagicMock()

        manager.remove_component(LayerType.OUTER, 0)

        ship.recalculate_stats.assert_called()


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

    def test_get_all_components_returns_all(self, engine_component, weapon_component):
        """get_all_components returns components from all layers."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        # Add components to different layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)

        all_comps = manager.get_all_components()

        assert engine_component in all_comps
        assert weapon_component in all_comps

    def test_get_all_components_returns_fresh_list(self, engine_component):
        """get_all_components returns a new list each call."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
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

    def test_iter_components_yields_layer_and_component(self, engine_component):
        """iter_components yields (layer_type, component) tuples."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
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
        assert found

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

    def test_get_components_by_ability_finds_matching(self, weapon_component):
        """get_components_by_ability returns components with specified ability."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)
        # Component uses is_active and _is_operational for is_operational property
        weapon_component.is_active = True
        weapon_component._is_operational = True

        result = manager.get_components_by_ability('WeaponAbility')

        assert weapon_component in result

    def test_get_components_by_ability_excludes_non_operational(self, weapon_component):
        """get_components_by_ability excludes non-operational components by default."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)
        # Make component non-operational
        weapon_component.is_active = False

        result = manager.get_components_by_ability('WeaponAbility')

        assert weapon_component not in result

    def test_get_components_by_ability_includes_non_operational_when_flag_false(self, weapon_component):
        """get_components_by_ability includes non-operational when operational_only=False."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
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

    def test_get_components_by_layer_returns_correct_layer(self, engine_component):
        """get_components_by_layer returns components from specified layer."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
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

    def test_get_components_by_layer_returns_fresh_list(self, engine_component):
        """get_components_by_layer returns a new list each call."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
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

    def test_has_components_returns_true_when_has_components(self, engine_component):
        """has_components returns True when components exist."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        assert manager.has_components() is True


class TestFindComponentWithIndex:
    """Tests for find_component_with_index method."""

    def test_find_component_with_index_finds_matching(self, engine_component, weapon_component):
        """find_component_with_index returns matching component with location."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
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

    def test_find_component_with_index_returns_none_if_not_found(self, engine_component):
        """find_component_with_index returns None when no match."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)

        result = manager.find_component_with_index(lambda c: False)

        assert result is None


class TestClearNonHullComponents:
    """Tests for clear_non_hull_components method."""

    def test_clear_non_hull_components_removes_all_except_hull(self, engine_component, weapon_component):
        """clear_non_hull_components removes components from all layers except HULL."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers
        manager.layers[LayerType.OUTER]['components'].append(engine_component)
        manager.layers[LayerType.OUTER]['components'].append(weapon_component)
        ship.recalculate_stats = MagicMock()

        manager.clear_non_hull_components()

        assert manager.layers[LayerType.OUTER]['components'] == []

    def test_clear_non_hull_components_preserves_hull(self):
        """clear_non_hull_components preserves HULL layer components."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        # Add a mock hull component
        hull_comp = MagicMock()
        manager.layers[LayerType.HULL]['components'].append(hull_comp)
        ship.recalculate_stats = MagicMock()

        manager.clear_non_hull_components()

        assert hull_comp in manager.layers[LayerType.HULL]['components']


class TestAddComponentsBulk:
    """Tests for add_components_bulk method."""

    def test_add_components_bulk_adds_multiple_copies(self, engine_component):
        """add_components_bulk adds multiple cloned copies."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        count = manager.add_components_bulk(engine_component, LayerType.OUTER, 3)

        assert count == 3
        assert len(manager.layers[LayerType.OUTER]['components']) == 3

    def test_add_components_bulk_returns_count_added(self, engine_component):
        """add_components_bulk returns number successfully added."""
        from game.simulation.entities.ship_component_manager import ShipComponentManager
        from game.simulation.entities.ship import Ship

        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        manager = ShipComponentManager(ship)
        manager.initialize_layers()
        ship.layers = manager.layers

        count = manager.add_components_bulk(engine_component, LayerType.OUTER, 2)

        assert count == 2


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


# Fixtures
@pytest.fixture
def weapon_component():
    """Create a weapon component (laser cannon)."""
    from tests.fixtures.components import create_weapon
    return create_weapon()


@pytest.fixture
def engine_component():
    """Create an engine component (standard engine)."""
    from tests.fixtures.components import create_engine
    return create_engine()


@pytest.fixture
def basic_ship():
    """Create a basic ship with bridge and engine."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="BasicShip",
        add_bridge=True,
        add_engine=True
    )


@pytest.fixture
def armed_ship():
    """Create an armed ship for testing."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="ArmedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
    )
