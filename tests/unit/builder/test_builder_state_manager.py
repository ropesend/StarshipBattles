"""
Tests for BuilderStateManager.

PROJ-44 Phase 7 Task 7.3: Extract state management from BuilderScreen.
"""
import pytest
from unittest.mock import MagicMock, Mock, patch, PropertyMock
from game.simulation.components.component import Component
from game.core.constants import LayerType


class TestBuilderStateManager:
    """Tests for BuilderStateManager class."""

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship with layers."""
        ship = MagicMock()
        ship.layers = {
            LayerType.HULL: {'components': []},
            LayerType.ARMOR: {'components': []},
            LayerType.OUTER: {'components': []},
        }
        return ship

    @pytest.fixture
    def sample_component(self):
        """Create a sample component."""
        comp_data = {
            "id": "test_weapon",
            "name": "Test Weapon",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "modifiers": []
        }
        return Component(comp_data)

    @pytest.fixture
    def state_manager(self, mock_ship):
        """Create a BuilderStateManager instance."""
        from game.ui.screens.builder.state_manager import BuilderStateManager
        manager = BuilderStateManager(mock_ship)
        return manager

    # --- Selection Tests ---

    def test_initial_state(self, state_manager):
        """State manager starts with empty selection."""
        assert state_manager.selected_components == []
        assert state_manager.selected_component is None
        assert state_manager.template_modifiers == {}
        assert state_manager.pending_action is None
        assert state_manager.dragged_item is None

    def test_select_single_component(self, state_manager, sample_component):
        """Selecting a single component sets it as selected."""
        state_manager.on_selection_changed(sample_component, append=False)

        assert len(state_manager.selected_components) == 1
        assert state_manager.selected_component[2] == sample_component

    def test_clear_selection(self, state_manager, sample_component):
        """Passing None clears the selection."""
        state_manager.on_selection_changed(sample_component, append=False)
        state_manager.on_selection_changed(None, append=False)

        assert state_manager.selected_components == []
        assert state_manager.selected_component is None

    def test_append_selection(self, state_manager, sample_component):
        """Appending adds to existing selection."""
        comp_data = {
            "id": "test_weapon",
            "name": "Test Weapon 2",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "modifiers": []
        }
        comp2 = Component(comp_data)

        state_manager.on_selection_changed(sample_component, append=False)
        state_manager.on_selection_changed(comp2, append=True)

        assert len(state_manager.selected_components) == 2

    def test_toggle_selection_off(self, state_manager, sample_component):
        """Toggle removes component if already selected."""
        state_manager.on_selection_changed(sample_component, append=False)
        state_manager.on_selection_changed(sample_component, append=True, toggle=True)

        assert state_manager.selected_components == []

    def test_toggle_selection_on(self, state_manager, sample_component):
        """Toggle adds component if not selected."""
        comp_data = {
            "id": "test_weapon",
            "name": "Test Weapon 2",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "modifiers": []
        }
        comp2 = Component(comp_data)

        state_manager.on_selection_changed(sample_component, append=False)
        state_manager.on_selection_changed(comp2, append=True, toggle=True)

        assert len(state_manager.selected_components) == 2

    def test_homogeneous_selection_enforcement(self, state_manager, sample_component):
        """Selection only allows components with same definition ID."""
        # Same type
        comp_same = Component({
            "id": "test_weapon",  # Same ID
            "name": "Test Weapon Clone",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "modifiers": []
        })

        # Different type
        comp_different = Component({
            "id": "other_component",  # Different ID
            "name": "Other Component",
            "type": "System",
            "mass": 5,
            "hp": 50,
            "modifiers": []
        })

        state_manager.on_selection_changed(sample_component, append=False)
        state_manager.on_selection_changed(comp_same, append=True)

        assert len(state_manager.selected_components) == 2

        # Adding different type replaces selection
        state_manager.on_selection_changed(comp_different, append=True)
        assert len(state_manager.selected_components) == 1
        assert state_manager.selected_components[0][2].id == "other_component"

    def test_list_selection(self, state_manager):
        """Can select multiple components at once via list."""
        comps = [
            Component({"id": "w1", "name": "W1", "type": "Weapon", "mass": 5, "hp": 50, "modifiers": []}),
            Component({"id": "w1", "name": "W2", "type": "Weapon", "mass": 5, "hp": 50, "modifiers": []}),
            Component({"id": "w1", "name": "W3", "type": "Weapon", "mass": 5, "hp": 50, "modifiers": []}),
        ]

        state_manager.on_selection_changed(comps, append=False)

        assert len(state_manager.selected_components) == 3

    def test_tuple_selection(self, state_manager, sample_component, mock_ship):
        """Can select via (layer, index, component) tuple."""
        mock_ship.layers[LayerType.OUTER]['components'] = [sample_component]

        selection = (LayerType.OUTER, 0, sample_component)
        state_manager.on_selection_changed(selection, append=False)

        assert len(state_manager.selected_components) == 1
        assert state_manager.selected_component == selection

    # --- Template Modifiers Tests ---

    def test_set_template_modifiers(self, state_manager):
        """Can set template modifiers."""
        modifiers = {"mod_1": 5, "mod_2": 10}
        state_manager.set_template_modifiers(modifiers)

        assert state_manager.template_modifiers == modifiers

    def test_clear_template_modifiers(self, state_manager):
        """Can clear template modifiers."""
        state_manager.set_template_modifiers({"mod_1": 5})
        state_manager.clear_template_modifiers()

        assert state_manager.template_modifiers == {}

    # --- Pending Action Tests ---

    def test_set_pending_action(self, state_manager):
        """Can queue a pending action."""
        state_manager.set_pending_action('change_class', 'Cruiser')

        assert state_manager.pending_action == ('change_class', 'Cruiser')

    def test_clear_pending_action(self, state_manager):
        """Can clear pending action."""
        state_manager.set_pending_action('change_class', 'Cruiser')
        state_manager.clear_pending_action()

        assert state_manager.pending_action is None

    def test_get_and_clear_pending_action(self, state_manager):
        """get_and_clear returns action and clears it."""
        state_manager.set_pending_action('clear_design', None)

        action = state_manager.get_and_clear_pending_action()

        assert action == ('clear_design', None)
        assert state_manager.pending_action is None

    # --- Drag/Drop State Tests ---

    def test_set_dragged_item(self, state_manager, sample_component):
        """Can set dragged item."""
        state_manager.dragged_item = sample_component

        assert state_manager.dragged_item == sample_component

    def test_clear_dragged_item(self, state_manager, sample_component):
        """Can clear dragged item."""
        state_manager.dragged_item = sample_component
        state_manager.dragged_item = None

        assert state_manager.dragged_item is None

    # --- Callback Tests ---

    def test_selection_changed_callback(self, state_manager, sample_component):
        """Selection change triggers callback."""
        callback = MagicMock()
        state_manager.on_selection_changed_callback = callback

        state_manager.on_selection_changed(sample_component, append=False)

        callback.assert_called_once()

    def test_callback_not_called_without_registration(self, state_manager, sample_component):
        """No error if callback not registered."""
        # Should not raise
        state_manager.on_selection_changed(sample_component, append=False)

    # --- Integration Tests ---

    def test_clear_all_state(self, state_manager, sample_component):
        """clear_all resets all state."""
        state_manager.on_selection_changed(sample_component, append=False)
        state_manager.set_template_modifiers({"mod_1": 5})
        state_manager.set_pending_action('test', 'data')
        state_manager.dragged_item = sample_component

        state_manager.clear_all()

        assert state_manager.selected_components == []
        assert state_manager.template_modifiers == {}
        assert state_manager.pending_action is None
        assert state_manager.dragged_item is None

    def test_find_component_in_ship(self, state_manager, mock_ship, sample_component):
        """State manager can locate component in ship layers."""
        mock_ship.layers[LayerType.HULL]['components'] = [sample_component]

        state_manager.on_selection_changed(sample_component, append=False)

        # Should have found it and created proper tuple
        assert len(state_manager.selected_components) == 1
        layer, idx, comp = state_manager.selected_components[0]
        assert layer == LayerType.HULL
        assert idx == 0
        assert comp == sample_component

    def test_component_not_in_ship_still_selectable(self, state_manager, sample_component):
        """Components not in ship (e.g., templates) can still be selected."""
        # sample_component not added to ship layers
        state_manager.on_selection_changed(sample_component, append=False)

        assert len(state_manager.selected_components) == 1
        layer, idx, comp = state_manager.selected_components[0]
        assert layer is None  # Not in any layer
        assert idx == -1
        assert comp == sample_component


class TestBuilderStateManagerWithShip:
    """Integration tests with real ship fixture."""

    @pytest.fixture
    def state_manager_with_ship(self, initialized_ship_data, basic_escort_ship):
        """Create state manager with real ship."""
        from game.ui.screens.builder.state_manager import BuilderStateManager
        return BuilderStateManager(basic_escort_ship)

    def test_select_component_from_ship(self, state_manager_with_ship, basic_escort_ship):
        """Can select a component that's actually in the ship."""
        # Get first component from ship
        for layer_type, layer_data in basic_escort_ship.layers.items():
            if layer_data['components']:
                comp = layer_data['components'][0]
                break
        else:
            pytest.skip("No components in ship")

        state_manager_with_ship.on_selection_changed(comp, append=False)

        assert len(state_manager_with_ship.selected_components) == 1
        assert state_manager_with_ship.selected_component[2] == comp
