import pytest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui
from game.ui.screens.builder.layer_panel import LayerComponentItem, IndividualComponentItem
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.simulation.components.component_constants import ApplicationModifier
from game.core.registry import RegistryManager


@pytest.fixture
def pygame_manager():
    pygame.init()
    pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))
    yield manager
    pygame.quit()
    RegistryManager.instance().clear()


@pytest.fixture
def builder_setup():
    pygame.init()
    pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))

    # Patch _create_ui to avoid complex UI initialization
    patcher_create_ui = patch('game.ui.screens.workshop_screen.DesignWorkshopScreen._create_ui')
    mock_create_ui = patcher_create_ui.start()

    # Patch internal managers
    p1 = patch('game.ui.screens.workshop_screen.SpriteManager')
    p2 = patch('game.ui.screens.workshop_screen.ShipThemeManager')
    p1.start()
    p2.start()

    # Mock Ship and Components
    ship = MagicMock(spec=Ship)
    ship.layers = {
        'core': {
            'components': [],
            'max_mass': 100
        }
    }

    comp_data = {
        "id": "test_id",
        "name": "Test Component",
        "type": "core",
        "mass": 10,
        "hp": 100,
        "damage": 0,
        "modifiers": []
    }
    component = Component(comp_data)
    component.mass = 10
    component.name = "Test Component"

    # Populate ship
    ship.layers['core']['components'] = [component]

    # Add ship helper methods that event_router now uses
    def get_all_components():
        result = []
        for layer_data in ship.layers.values():
            result.extend(layer_data['components'])
        return result

    def iter_components():
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data['components']:
                yield layer_type, comp

    def has_components():
        for layer_data in ship.layers.values():
            if layer_data['components']:
                return True
        return False

    ship.get_all_components = get_all_components
    ship.iter_components = iter_components
    ship.has_components = has_components

    # Create Builder GUI (_create_ui is mocked so panels won't be created)
    context = WorkshopContext.standalone(tech_preset_name="default")
    builder_gui = DesignWorkshopScreen(800, 600, context)

    # Manually setup the mocks that _create_ui would have created
    builder_gui.ui_manager = MagicMock()
    builder_gui.left_panel = MagicMock()
    builder_gui.right_panel = MagicMock()
    builder_gui.layer_panel = MagicMock()
    builder_gui.modifier_panel = MagicMock()
    builder_gui.weapons_report_panel = MagicMock()
    builder_gui.detail_panel = MagicMock()

    builder_gui.ship = ship

    # Ensure panel mocks return False by default for handle_event so logic flows through
    builder_gui.left_panel.handle_event.return_value = False
    builder_gui.modifier_panel.handle_event.return_value = False
    builder_gui.layer_panel.handle_event.return_value = False

    yield {
        'manager': manager,
        'builder_gui': builder_gui,
        'ship': ship,
        'component': component,
        'comp_data': comp_data,
        'patcher_create_ui': patcher_create_ui,
        'p1': p1,
        'p2': p2
    }

    # Stop patches
    patcher_create_ui.stop()
    p1.stop()
    p2.stop()

    pygame.quit()
    RegistryManager.instance().clear()


class TestBuilderStructureFeatures:
    def test_individual_item_ui_elements(self, pygame_manager):
        """Test that IndividualComponentItem has correct buttons and label style."""
        manager = pygame_manager
        container = manager.get_root_container()
        sprite_mgr = MagicMock()
        sprite_mgr.get_sprite.return_value = pygame.Surface((32, 32))

        comp_data = {
            "id": "test_id",
            "name": "Test Component",
            "type": "core",
            "mass": 10,
            "hp": 100,
            "damage": 0,
            "modifiers": []
        }
        component = Component(comp_data)
        component.mass = 10
        component.name = "Test Component"

        # Mock Event Handler
        event_handler = MagicMock()

        item = IndividualComponentItem(
            manager, container, component, 100, 0, 200, sprite_mgr,
            event_handler, False
        )

        # Check Label Alignment Style
        # Access elements via panel_container if available, or try get_container()
        # In pygame_gui UIPanel has a panel_container attribute which is the UIContainer
        container_obj = item.panel.panel_container
        label = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UILabel) and c.text == "Test Component"][0]
        assert '#left_aligned_label' in label.object_ids

        # Check Buttons
        buttons = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UIButton)]
        button_texts = [b.text for b in buttons]
        assert '+' in button_texts
        assert '-' in button_texts

    def test_layer_item_ui_elements(self, pygame_manager):
        """Test that LayerComponentItem has correct buttons and label style."""
        manager = pygame_manager
        container = manager.get_root_container()
        sprite_mgr = MagicMock()
        sprite_mgr.get_sprite.return_value = pygame.Surface((32, 32))

        comp_data = {
            "id": "test_id",
            "name": "Test Component",
            "type": "core",
            "mass": 10,
            "hp": 100,
            "damage": 0,
            "modifiers": []
        }
        component = Component(comp_data)
        component.mass = 10
        component.name = "Test Component"

        event_handler = MagicMock()

        item = LayerComponentItem(
            manager, container, component, 1, 10, 10.0, False,
            "key", False, 0, 200, sprite_mgr, event_handler
        )

        # Check Label
        container_obj = item.panel.panel_container
        label = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UILabel) and c.text == "Test Component"][0]
        assert '#left_aligned_label' in label.object_ids

        # Check Buttons
        buttons = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UIButton)]
        button_texts = [b.text for b in buttons]
        assert '+' in button_texts
        assert '-' in button_texts

    def test_multi_selection_logic(self, builder_setup):
        """Test selecting multiple components and property propagation."""
        builder_gui = builder_setup['builder_gui']
        comp_data = builder_setup['comp_data']

        c1 = Component(comp_data)
        c2 = Component(comp_data)
        c3 = Component(comp_data)
        c1.id = "test_id"  # Ensure they are same type
        c2.id = "test_id"
        c3.id = "test_id"

        # Select c1
        builder_gui.on_selection_changed(c1, append=False)
        assert len(builder_gui.selected_components) == 1
        assert builder_gui.selected_components[0][2] == c1

        # Add c2
        builder_gui.on_selection_changed(c2, append=True)
        assert len(builder_gui.selected_components) == 2

        # Add c3
        builder_gui.on_selection_changed(c3, append=True)
        assert len(builder_gui.selected_components) == 3

        # Select c1 again (should replace if append=False)
        builder_gui.on_selection_changed(c1, append=False)
        assert len(builder_gui.selected_components) == 1
        assert builder_gui.selected_components[0][2] == c1

    def test_modifier_propagation(self, builder_setup):
        """Test that changing a modifier on one selected component updates others."""
        builder_gui = builder_setup['builder_gui']
        comp_data = builder_setup['comp_data']

        c1 = Component(comp_data)
        c2 = Component(comp_data)
        c1.id = "test_id"
        c2.id = "test_id"

        # Setup modifiers
        mod_def = MagicMock()
        mod_def.id = "test_mod"
        mod_def.id = "test_mod"
        c1.modifiers = [ApplicationModifier(mod_def, 10)]
        c2.modifiers = [ApplicationModifier(mod_def, 5)]

        # Mock recalculate_stats
        c1.recalculate_stats = MagicMock()
        c2.recalculate_stats = MagicMock()

        # Select both (c1 last so it is primary editing target)
        builder_gui.on_selection_changed([c2, c1], append=False)

        # Simulate modifier change trigger
        # We need to manually simulate what happens when UI updates modifier
        # Usually it updates self.selected_component object directly, then calls _on_modifier_change

        # Verify initial
        assert c2.modifiers[0].value == 5

        # Change c1 mod (the primary selected)
        c1.modifiers[0].value = 20

        # Call propagation
        builder_gui._on_modifier_change()

        # Check c2 updated
        assert len(c2.modifiers) == 1
        assert c2.modifiers[0].value == 20
        c2.recalculate_stats.assert_called()

    def test_add_remove_actions(self, builder_setup):
        """Test that add/remove actions call appropriate viewmodel methods."""
        builder_gui = builder_setup['builder_gui']
        component = builder_setup['component']
        comp_data = builder_setup['comp_data']

        # Setup mock viewmodel to track calls
        builder_gui.viewmodel.remove_component = MagicMock(return_value=MagicMock())
        builder_gui.viewmodel.add_component_instance = MagicMock(return_value=True)

        # Simulate Remove Individual
        comp = component
        builder_gui.ship.layers['core']['components'] = [comp]

        # Let's mock layer_panel.handle_event to return the action
        event = MagicMock()
        builder_gui.layer_panel.handle_event.return_value = ('remove_individual', comp)

        builder_gui.handle_event(event)
        builder_gui.viewmodel.remove_component.assert_called_with('core', 0)

        # Simulate Add Individual
        builder_gui.layer_panel.handle_event.return_value = ('add_individual', comp)

        # Need to clone component
        comp.clone = MagicMock(return_value=Component(comp_data))

        builder_gui.handle_event(event)
        builder_gui.viewmodel.add_component_instance.assert_called()
