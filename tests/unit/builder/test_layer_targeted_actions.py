"""Tests for BUG-71: +/- buttons should target the correct layer.

When the same component type exists in multiple layers, add/remove
actions must operate on the specific layer the user clicked, not
the first matching layer found by iteration order.
"""
import pytest
from unittest.mock import MagicMock, patch
from game.core.constants import LayerType
from game.ui.screens.workshop_event_router import WorkshopEventRouter


def _make_component(name, comp_type="weapon"):
    """Create a minimal mock component for testing."""
    comp = MagicMock()
    comp.name = name
    comp.type = comp_type
    comp.definition = MagicMock()
    comp.definition.id = name
    comp.definition.type = comp_type
    comp.mass = 10
    comp.modifiers = []
    comp.clone.return_value = comp  # clone returns itself for simplicity
    comp.recalculate_stats = MagicMock()
    return comp


@pytest.fixture
def router_setup():
    """Create a WorkshopEventRouter with a mocked GUI."""
    from game.simulation.entities.layer_data import LayerData
    gui = MagicMock()
    gui.ship.layers = {
        LayerType.CORE: LayerData(),
        LayerType.INNER: LayerData(),
        LayerType.OUTER: LayerData(),
        LayerType.ARMOR: LayerData(),
    }

    def iter_components():
        for l_type, data in gui.ship.layers.items():
            for c in data.components:
                yield l_type, c

    gui.ship.iter_components = iter_components

    def get_all_components():
        result = []
        for data in gui.ship.layers.values():
            result.extend(data.components)
        return result

    gui.ship.get_all_components = get_all_components

    gui.selected_components = []
    gui.viewmodel.remove_component = MagicMock()
    gui.viewmodel.add_component_instance = MagicMock(return_value=True)
    gui.update_stats = MagicMock()

    router = WorkshopEventRouter(gui)
    return router, gui


class TestRemoveGroupLayerTargeted:
    """Test _handle_remove_group with layer-targeted tuple data."""

    def test_remove_from_correct_layer_when_same_component_in_multiple_layers(self, router_setup):
        """BUG-71: Remove should target the specified layer, not first match."""
        router, gui = router_setup

        # Place "laser" in CORE and INNER
        core_laser = _make_component("laser")
        inner_laser = _make_component("laser")
        gui.ship.layers[LayerType.CORE].components = [core_laser]
        gui.ship.layers[LayerType.INNER].components = [inner_laser]

        # Remove from INNER (tuple format: group_key, layer_type)
        with patch('game.ui.screens.builder.grouping_strategies.get_component_group_key', return_value="laser"):
            router._handle_remove_group(("laser", LayerType.INNER))

        # Should remove from INNER (index 0), not CORE
        gui.viewmodel.remove_component.assert_called_once_with(LayerType.INNER, 0)

    def test_remove_from_core_when_targeted(self, router_setup):
        """Verify CORE targeting works when component also exists in INNER."""
        router, gui = router_setup

        core_laser = _make_component("laser")
        inner_laser = _make_component("laser")
        gui.ship.layers[LayerType.CORE].components = [core_laser]
        gui.ship.layers[LayerType.INNER].components = [inner_laser]

        with patch('game.ui.screens.builder.grouping_strategies.get_component_group_key', return_value="laser"):
            router._handle_remove_group(("laser", LayerType.CORE))

        gui.viewmodel.remove_component.assert_called_once_with(LayerType.CORE, 0)

    def test_remove_group_backwards_compat_plain_string(self, router_setup):
        """Plain string group_key should still work (backwards compat)."""
        router, gui = router_setup

        core_laser = _make_component("laser")
        gui.ship.layers[LayerType.CORE].components = [core_laser]

        with patch('game.ui.screens.builder.grouping_strategies.get_component_group_key', return_value="laser"):
            router._handle_remove_group("laser")

        gui.viewmodel.remove_component.assert_called_once()


class TestRemoveIndividualLayerTargeted:
    """Test _handle_remove_individual with layer-targeted tuple data."""

    def test_remove_individual_from_correct_layer(self, router_setup):
        """BUG-71: Individual remove should use layer hint."""
        router, gui = router_setup

        inner_comp = _make_component("reactor")
        gui.ship.layers[LayerType.INNER].components = [inner_comp]

        router._handle_remove_individual((inner_comp, LayerType.INNER))

        gui.viewmodel.remove_component.assert_called_once_with(LayerType.INNER, 0)

    def test_remove_individual_backwards_compat(self, router_setup):
        """Plain component should still work (backwards compat)."""
        router, gui = router_setup

        core_comp = _make_component("reactor")
        gui.ship.layers[LayerType.CORE].components = [core_comp]

        router._handle_remove_individual(core_comp)

        gui.viewmodel.remove_component.assert_called_once_with(LayerType.CORE, 0)


class TestAddComponentLayerTargeted:
    """Test _handle_add_component with layer-targeted tuple data."""

    def test_add_group_to_correct_layer_when_same_in_multiple(self, router_setup):
        """BUG-71: Add should clone into the specified layer, not first match."""
        router, gui = router_setup

        core_laser = _make_component("laser")
        inner_laser = _make_component("laser")
        gui.ship.layers[LayerType.CORE].components = [core_laser]
        gui.ship.layers[LayerType.INNER].components = [inner_laser]

        with patch('game.ui.screens.builder.grouping_strategies.get_component_group_key', return_value="laser"):
            router._handle_add_component('add_group', ("laser", LayerType.INNER))

        # Should add to INNER, not CORE
        gui.viewmodel.add_component_instance.assert_called_once()
        call_args = gui.viewmodel.add_component_instance.call_args
        assert call_args[0][1] == LayerType.INNER

    def test_add_individual_to_correct_layer(self, router_setup):
        """BUG-71: Individual add should use layer hint."""
        router, gui = router_setup

        inner_comp = _make_component("reactor")
        gui.ship.layers[LayerType.INNER].components = [inner_comp]

        router._handle_add_component('add_individual', (inner_comp, LayerType.INNER))

        gui.viewmodel.add_component_instance.assert_called_once()
        call_args = gui.viewmodel.add_component_instance.call_args
        assert call_args[0][1] == LayerType.INNER

    def test_add_group_backwards_compat(self, router_setup):
        """Plain group_key should still work."""
        router, gui = router_setup

        core_laser = _make_component("laser")
        gui.ship.layers[LayerType.CORE].components = [core_laser]

        with patch('game.ui.screens.builder.grouping_strategies.get_component_group_key', return_value="laser"):
            router._handle_add_component('add_group', "laser")

        gui.viewmodel.add_component_instance.assert_called_once()
        call_args = gui.viewmodel.add_component_instance.call_args
        assert call_args[0][1] == LayerType.CORE
