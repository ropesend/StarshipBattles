"""
Tests for Ship component getter methods.

Task 2.1-2.4 of Consolidation Plan Phase 2:
- get_all_components()
- iter_components()
- get_components_by_ability()
- get_components_by_layer()
"""
import pytest
from typing import List, Tuple

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.core.constants import LayerType


@pytest.mark.use_custom_data
class TestGetAllComponents:
    """Tests for Ship.get_all_components() method."""

    def test_returns_list(self, empty_ship):
        """get_all_components() returns a list."""
        result = empty_ship.get_all_components()
        assert isinstance(result, list)

    def test_empty_ship_has_hull_only(self, empty_ship):
        """Empty ship returns only the auto-equipped hull component."""
        result = empty_ship.get_all_components()
        # Hull is auto-equipped
        assert len(result) == 1
        assert result[0].id == "hull_escort"

    def test_returns_all_components(self, armed_ship):
        """Returns all components from all layers."""
        result = armed_ship.get_all_components()
        # Hull + bridge + engine + shield + 2 lasers + armor = 7
        assert len(result) == 7

    def test_includes_hull_layer(self, armed_ship):
        """Includes components from HULL layer."""
        result = armed_ship.get_all_components()
        hull_comps = [c for c in result if c.layer_assigned == LayerType.HULL]
        assert len(hull_comps) == 1

    def test_includes_core_layer(self, armed_ship):
        """Includes components from CORE layer."""
        result = armed_ship.get_all_components()
        core_comps = [c for c in result if c.layer_assigned == LayerType.CORE]
        # bridge + engine
        assert len(core_comps) == 2

    def test_includes_outer_layer(self, armed_ship):
        """Includes components from OUTER layer."""
        result = armed_ship.get_all_components()
        outer_comps = [c for c in result if c.layer_assigned == LayerType.OUTER]
        # 2 lasers + armor
        assert len(outer_comps) == 3

    def test_returns_cached_list(self, basic_ship):
        """Each call returns the same cached list for performance (PROJ-49).

        PROJ-49 Phase 3: get_all_components() now returns cached list.
        Callers should not modify the returned list directly.
        """
        result1 = basic_ship.get_all_components()
        result2 = basic_ship.get_all_components()
        # PROJ-49: Now returns cached list for performance
        assert result1 is result2
        assert result1 == result2  # Same contents


@pytest.mark.use_custom_data
class TestIterComponents:
    """Tests for Ship.iter_components() generator."""

    def test_yields_tuples(self, basic_ship):
        """iter_components() yields (LayerType, Component) tuples."""
        for item in basic_ship.iter_components():
            assert isinstance(item, tuple)
            assert len(item) == 2
            layer_type, component = item
            assert isinstance(layer_type, LayerType)
            assert isinstance(component, Component)

    def test_iterates_all_layers(self, armed_ship):
        """Iterates through components from all layers."""
        layers_seen = set()
        for layer_type, component in armed_ship.iter_components():
            layers_seen.add(layer_type)

        # Should see HULL, CORE, INNER, OUTER
        assert LayerType.HULL in layers_seen
        assert LayerType.CORE in layers_seen
        assert LayerType.INNER in layers_seen
        assert LayerType.OUTER in layers_seen

    def test_count_matches_get_all_components(self, armed_ship):
        """Iterator yields same number of components as get_all_components()."""
        iter_count = sum(1 for _ in armed_ship.iter_components())
        list_count = len(armed_ship.get_all_components())
        assert iter_count == list_count

    def test_can_be_consumed_multiple_times(self, basic_ship):
        """Generator can be re-invoked to iterate multiple times."""
        count1 = sum(1 for _ in basic_ship.iter_components())
        count2 = sum(1 for _ in basic_ship.iter_components())
        assert count1 == count2

    def test_layer_matches_component_assignment(self, armed_ship):
        """Layer type in tuple matches component's layer_assigned."""
        for layer_type, component in armed_ship.iter_components():
            assert component.layer_assigned == layer_type

    def test_empty_ship_yields_hull(self, empty_ship):
        """Empty ship yields only the hull component."""
        items = list(empty_ship.iter_components())
        assert len(items) == 1
        layer_type, component = items[0]
        assert layer_type == LayerType.HULL
        assert component.id == "hull_escort"


@pytest.mark.use_custom_data
class TestGetComponentsByAbility:
    """Tests for Ship.get_components_by_ability() method."""

    def test_returns_list(self, armed_ship):
        """get_components_by_ability() returns a list."""
        result = armed_ship.get_components_by_ability('WeaponAbility')
        assert isinstance(result, list)

    def test_returns_empty_when_no_matches(self, basic_ship):
        """Returns empty list when no components have the ability."""
        # basic_ship has no weapons
        result = basic_ship.get_components_by_ability('WeaponAbility')
        assert result == []

    def test_returns_components_with_ability(self, armed_ship):
        """Returns only components that have the specified ability."""
        weapons = armed_ship.get_components_by_ability('WeaponAbility')
        assert len(weapons) == 2  # 2 lasers
        for comp in weapons:
            assert comp.has_ability('WeaponAbility')

    def test_finds_shield_generators(self, armed_ship):
        """Finds components with ShieldGenerator ability."""
        shields = armed_ship.get_components_by_ability('ShieldGenerator')
        assert len(shields) == 1
        assert shields[0].id == "test_shield"

    def test_finds_command_and_control(self, armed_ship):
        """Finds components with CommandAndControl ability."""
        bridges = armed_ship.get_components_by_ability('CommandAndControl')
        assert len(bridges) == 1
        assert bridges[0].id == "test_bridge"

    def test_operational_only_true_filters_damaged(self, armed_ship):
        """operational_only=True excludes non-operational components."""
        # Damage one weapon
        weapons = armed_ship.get_components_by_ability('WeaponAbility')
        weapons[0].current_hp = 0
        weapons[0].is_active = False

        # Should only return operational weapons
        result = armed_ship.get_components_by_ability('WeaponAbility', operational_only=True)
        assert len(result) == 1

    def test_operational_only_false_includes_all(self, armed_ship):
        """operational_only=False includes non-operational components."""
        # Damage one weapon
        weapons = armed_ship.get_components_by_ability('WeaponAbility')
        weapons[0].current_hp = 0
        weapons[0].is_active = False

        # Should return all weapons regardless of status
        result = armed_ship.get_components_by_ability('WeaponAbility', operational_only=False)
        assert len(result) == 2

    def test_default_operational_only_is_true(self, armed_ship):
        """Default behavior filters to operational components only."""
        # Damage one weapon
        weapons = armed_ship.get_components_by_ability('WeaponAbility', operational_only=False)
        weapons[0].current_hp = 0
        weapons[0].is_active = False

        # Call without operational_only parameter
        result = armed_ship.get_components_by_ability('WeaponAbility')
        assert len(result) == 1


@pytest.mark.use_custom_data
class TestGetComponentsByLayer:
    """Tests for Ship.get_components_by_layer() method."""

    def test_returns_list(self, armed_ship):
        """get_components_by_layer() returns a list."""
        result = armed_ship.get_components_by_layer(LayerType.CORE)
        assert isinstance(result, list)

    def test_returns_components_for_layer(self, armed_ship):
        """Returns all components in specified layer."""
        core_comps = armed_ship.get_components_by_layer(LayerType.CORE)
        # bridge + engine
        assert len(core_comps) == 2

    def test_returns_hull_layer(self, armed_ship):
        """Returns components from HULL layer."""
        hull_comps = armed_ship.get_components_by_layer(LayerType.HULL)
        assert len(hull_comps) == 1
        assert hull_comps[0].id == "hull_escort"

    def test_returns_outer_layer(self, armed_ship):
        """Returns components from OUTER layer."""
        outer_comps = armed_ship.get_components_by_layer(LayerType.OUTER)
        # 2 lasers + armor
        assert len(outer_comps) == 3

    def test_empty_layer_returns_empty_list(self, basic_ship):
        """Empty layer returns empty list."""
        # basic_ship has no components in OUTER layer
        outer_comps = basic_ship.get_components_by_layer(LayerType.OUTER)
        assert outer_comps == []

    def test_nonexistent_layer_returns_empty(self, basic_ship):
        """Returns empty list for layer not in ship's layers dict."""
        # ARMOR layer may not exist in all ships
        armor_comps = basic_ship.get_components_by_layer(LayerType.ARMOR)
        assert armor_comps == []

    def test_returns_fresh_list(self, armed_ship):
        """Each call returns a fresh list (not the internal reference)."""
        result1 = armed_ship.get_components_by_layer(LayerType.CORE)
        result2 = armed_ship.get_components_by_layer(LayerType.CORE)
        assert result1 is not result2
        assert result1 == result2  # Same contents

    def test_all_returned_components_in_layer(self, armed_ship):
        """All returned components have matching layer_assigned."""
        for layer_type in [LayerType.HULL, LayerType.CORE, LayerType.INNER, LayerType.OUTER]:
            comps = armed_ship.get_components_by_layer(layer_type)
            for comp in comps:
                assert comp.layer_assigned == layer_type
