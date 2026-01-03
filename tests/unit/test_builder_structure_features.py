import unittest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui
from ui.builder.layer_panel import LayerComponentItem, IndividualComponentItem, LayerPanel
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, MODIFIER_REGISTRY, ApplicationModifier

class TestBuilderStructureFeatures(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.manager = pygame_gui.UIManager((800, 600))
        
        # Mock Ship and Components
        self.ship = MagicMock(spec=Ship)
        self.ship.layers = {
            'core': {
                'components': [],
                'max_mass': 100
            }
        }
        
        self.comp_data = {
            "id": "test_id",
            "name": "Test Component",
            "type": "core",
            "mass": 10,
            "hp": 100,
            "damage": 0,
            "modifiers": []
        }
        self.component = Component(self.comp_data)
        self.component.mass = 10
        self.component.name = "Test Component"
        
        # Populate ship
        self.ship.layers['core']['components'] = [self.component]
        
        # Mock Builder GUI
        with patch('game.ui.screens.builder_screen.BuilderLeftPanel'), \
             patch('game.ui.screens.builder_screen.BuilderRightPanel'), \
             patch('game.ui.screens.builder_screen.LayerPanel'), \
             patch('game.ui.screens.builder_screen.ModifierEditorPanel'), \
             patch('game.ui.screens.builder_screen.WeaponsReportPanel'):
            self.builder_gui = BuilderSceneGUI(800, 600, None)
            self.builder_gui.ship = self.ship
            # Ensure panel mocks return False by default for handle_event so logic flows through
            self.builder_gui.left_panel.handle_event.return_value = False
            self.builder_gui.modifier_panel.handle_event.return_value = False
            self.builder_gui.layer_panel.handle_event.return_value = False
            
        # Re-initialize real LayerPanel for testing its items if needed
        # But mostly we test BuilderSceneGUI logic and Item classes separately

    def tearDown(self):
        pygame.quit()

    def test_individual_item_ui_elements(self):
        """Test that IndividualComponentItem has correct buttons and label style."""
        container = self.manager.get_root_container()
        sprite_mgr = MagicMock()
        sprite_mgr.get_sprite.return_value = pygame.Surface((32, 32))
        
        # Mock Event Handler
        event_handler = MagicMock()
        
        item = IndividualComponentItem(
            self.manager, container, self.component, 100, 0, 200, sprite_mgr,
            event_handler, False
        )
        
        # Check Label Alignment Style
        # Access elements via panel_container if available, or try get_container()
        # In pygame_gui UIPanel has a panel_container attribute which is the UIContainer
        container_obj = item.panel.panel_container 
        label = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UILabel) and c.text == "Test Component"][0]
        self.assertIn('#left_aligned_label', label.object_ids)
        
        # Check Buttons
        buttons = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UIButton)]
        button_texts = [b.text for b in buttons]
        self.assertIn('+', button_texts)
        self.assertIn('-', button_texts)
        
    def test_layer_item_ui_elements(self):
        """Test that LayerComponentItem has correct buttons and label style."""
        container = self.manager.get_root_container()
        sprite_mgr = MagicMock()
        sprite_mgr.get_sprite.return_value = pygame.Surface((32, 32))

        event_handler = MagicMock()
        
        item = LayerComponentItem(
            self.manager, container, self.component, 1, 10, 10.0, False,
            "key", False, 0, 200, sprite_mgr, event_handler
        )
        
        # Check Label
        container_obj = item.panel.panel_container
        label = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UILabel) and c.text == "Test Component"][0]
        self.assertIn('#left_aligned_label', label.object_ids)
        
        # Check Buttons
        buttons = [c for c in container_obj.elements if isinstance(c, pygame_gui.elements.UIButton)]
        button_texts = [b.text for b in buttons]
        self.assertIn('+', button_texts)
        self.assertIn('-', button_texts)

    def test_multi_selection_logic(self):
        """Test selecting multiple components and property propagation."""
        c1 = Component(self.comp_data)
        c2 = Component(self.comp_data)
        c3 = Component(self.comp_data)
        c1.id = "test_id" # Ensure they are same type
        c2.id = "test_id"
        c3.id = "test_id"
        
        # Select c1
        self.builder_gui.on_selection_changed(c1, append=False)
        self.assertEqual(len(self.builder_gui.selected_components), 1)
        self.assertEqual(self.builder_gui.selected_components[0][2], c1)
        
        # Add c2
        self.builder_gui.on_selection_changed(c2, append=True)
        self.assertEqual(len(self.builder_gui.selected_components), 2)
        
        # Add c3
        self.builder_gui.on_selection_changed(c3, append=True)
        self.assertEqual(len(self.builder_gui.selected_components), 3)
        
        # Select c1 again (should replace if append=False)
        self.builder_gui.on_selection_changed(c1, append=False)
        self.assertEqual(len(self.builder_gui.selected_components), 1)
        self.assertEqual(self.builder_gui.selected_components[0][2], c1)

    def test_modifier_propagation(self):
        """Test that changing a modifier on one selected component updates others."""
        c1 = Component(self.comp_data)
        c2 = Component(self.comp_data)
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
        self.builder_gui.on_selection_changed([c2, c1], append=False)
        
        # Simulate modifier change trigger
        # We need to manually simulate what happens when UI updates modifier
        # Usually it updates self.selected_component object directly, then calls _on_modifier_change
        
        # Verify initial
        self.assertEqual(c2.modifiers[0].value, 5)
        
        # Change c1 mod (the primary selected)
        c1.modifiers[0].value = 20
        
        # Call propagation
        self.builder_gui._on_modifier_change()
        
        # Check c2 updated
        self.assertEqual(len(c2.modifiers), 1)
        self.assertEqual(c2.modifiers[0].value, 20)
        c2.recalculate_stats.assert_called()

    def test_add_remove_actions(self):
        """Test that add/remove actions call appropriate ship methods."""
        # Setup mock ship to track calls
        self.builder_gui.ship.remove_component = MagicMock()
        self.builder_gui.ship.add_component = MagicMock()
        
        # Simulate Remove Individual
        comp = self.component
        self.builder_gui.ship.layers['core']['components'] = [comp]
        
        # Action tuple: ('remove_individual', comp)
        # We need to trigger handle_event with this action, but handle_event calls panels.
        # We can bypass and call the logic block if we extract it or simulate the loop.
        # Ideally we refactor `handle_event` to use a dispatcher, but here we can just test the logic 
        # by reusing the code block or simulating the event flow if possible.
        # Since `handle_event` is complex, let's call the action handler part if possible 
        # or just test `_handle_action` if we had extracted it.
        # The logic is inline in `handle_event`.
        
        # Let's mock layer_panel.handle_event to return the action
        event = MagicMock()
        self.builder_gui.layer_panel.handle_event.return_value = ('remove_individual', comp)
        
        self.builder_gui.handle_event(event)
        self.builder_gui.ship.remove_component.assert_called_with('core', 0)
        
        # Simulate Add Individual
        self.builder_gui.layer_panel.handle_event.return_value = ('add_individual', comp)
        
        # Mock VALIDATOR
        with patch('game.simulation.entities.ship.VALIDATOR') as mock_val:
            mock_val.validate_addition.return_value.is_valid = True
            
            # Need to clone component
            comp.clone = MagicMock(return_value=Component(self.comp_data))
            
            self.builder_gui.handle_event(event)
            self.builder_gui.ship.add_component.assert_called()

if __name__ == '__main__':
    unittest.main()
