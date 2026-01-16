import unittest
from unittest.mock import MagicMock, patch
import pygame

# We need to mock pygame_gui before importing builder_gui because it initializes UI
# Actually builder_screen imports pygame_gui. 
# We can use reference imports if we can instantiate BuilderSceneGUI without a full window.
# But BuilderSceneGUI __init__ creates UIManager which needs a window surface or size.
# We can mock UIManager.

from game.ui.screens import builder_screen
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.core.registry import RegistryManager
from game.simulation.entities.ship import LayerType

class TestBuilderDragDropReal(unittest.TestCase):
    
    def setUp(self):
        # ... existing setup code ...
        pass # Simplified for replacement efficiency - regex logic below addresses usage

        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode((1,1)) # Mock display for UIManager
            
        # Mock dependencies that BuilderSceneGUI init calls
        self.patchers = []
        
        # Patch UIManager to avoid theme loading real files or needing display
        p_manager = patch('game.ui.screens.builder_screen.pygame_gui.UIManager')
        self.MockUIManager = p_manager.start()
        self.patchers.append(p_manager)
        
        # Patch SpriteManager
        p_sprite = patch('game.ui.screens.builder_screen.SpriteManager')
        self.MockSpriteManager = p_sprite.start()
        self.patchers.append(p_sprite)
        
        # Patch PresetManager
        p_preset = patch('game.ui.screens.builder_screen.PresetManager')
        self.MockPresetManager = p_preset.start()
        self.patchers.append(p_preset)
        
        # Patch ThemeManager
        p_theme = patch('game.ui.screens.builder_screen.ShipThemeManager')
        self.MockThemeManager = p_theme.start()
        self.patchers.append(p_theme)
        
        # Patch Panels to isolate BuilderSceneGUI
        p_left = patch('game.ui.screens.builder_screen.BuilderLeftPanel')
        self.MockLeftPanel = p_left.start()
        self.patchers.append(p_left)
        
        p_layer = patch('game.ui.screens.builder_screen.LayerPanel')
        self.MockLayerPanel = p_layer.start()
        self.patchers.append(p_layer)
        
        p_right = patch('game.ui.screens.builder_screen.BuilderRightPanel')
        self.MockRightPanel = p_right.start()
        self.patchers.append(p_right)
        
        p_detail = patch('game.ui.screens.builder_screen.ComponentDetailPanel')
        self.MockDetailPanel = p_detail.start()
        self.patchers.append(p_detail)
        
        p_mod = patch('game.ui.screens.builder_screen.ModifierEditorPanel')
        self.MockModifierPanel = p_mod.start()
        self.patchers.append(p_mod)
        
        # Patch direct UI elements used in BuilderSceneGUI
        p_btn = patch('game.ui.screens.builder_screen.UIButton')
        self.MockUIButton = p_btn.start()
        self.patchers.append(p_btn)
        
        p_panel = patch('game.ui.screens.builder_screen.UIPanel')
        self.MockUIPanel = p_panel.start()
        self.patchers.append(p_panel)
        
        p_weapons = patch('game.ui.screens.builder_screen.WeaponsReportPanel')
        self.MockWeaponsPanel = p_weapons.start()
        self.patchers.append(p_weapons)
        
        p_view = patch('game.ui.screens.builder_screen.SchematicView')
        self.MockSchematicView = p_view.start()
        self.patchers.append(p_view)
        
        p_ctrl = patch('game.ui.screens.builder_screen.InteractionController')
        self.MockInteractionController = p_ctrl.start()
        self.patchers.append(p_ctrl)

        # Initialize Builder
        # We need a valid screen size
        self.builder = BuilderSceneGUI(1280, 720, lambda x: None)
        self.builder.event_bus = MagicMock()
        
        # Setup test ship
        self.builder.ship = MagicMock()
        self.builder.ship.layers = {
            LayerType.CORE: {'components': []},
            LayerType.INNER: {'components': []},
            LayerType.OUTER: {'components': []},
            LayerType.ARMOR: {'components': []}
        }
        # Add ship helper methods that event_router now uses
        def get_all_components():
            result = []
            for layer_data in self.builder.ship.layers.values():
                result.extend(layer_data['components'])
            return result

        def iter_components():
            for layer_type, layer_data in self.builder.ship.layers.items():
                for comp in layer_data['components']:
                    yield layer_type, comp

        def has_components():
            for layer_data in self.builder.ship.layers.values():
                if layer_data['components']:
                    return True
            return False

        self.builder.ship.get_all_components = get_all_components
        self.builder.ship.iter_components = iter_components
        self.builder.ship.has_components = has_components

        # Set benign defaults to satisfy update loop comparisons
        self.builder.ship.mass = 1000
        self.builder.ship.max_mass_budget = 10000
        self.builder.ship.resources.set_max_value('fuel', 100)
        self.builder.ship.resources.set_max_value('fuel', 100); self.builder.ship.resources.set_value('fuel', 100)
        self.builder.ship.resources.set_max_value('ammo', 100)
        self.builder.ship.resources.set_max_value('ammo', 100); self.builder.ship.resources.set_value('ammo', 100)
        self.builder.ship.resources.set_max_value('energy', 100)
        self.builder.ship.resources.set_max_value('energy', 100); self.builder.ship.resources.set_value('energy', 100)
        self.builder.ship.total_thrust = 500
        self.builder.ship.drag = 0.1
        self.builder.ship.name = "Test Ship"
        
    def tearDown(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        
        for p in self.patchers:
            p.stop()
        pygame.quit()
        RegistryManager.instance().clear()
            
    def test_drag_start(self):
        """Verify starting a drag sets dragged_item."""
        # Drag is typically started by InteractionController or UI event.
        # Let's interact with controller directly or simulate the action.
        
        # Simulate action: 'select_component_type' sets dragged_item
        comp_template = MagicMock()
        comp_template.clone.return_value = comp_template # Return self for simplicity
        
        # FIXED: Ensure mock has numeric stats and lists to avoid TypeError >
        comp_template.mass = 10
        comp_template.max_hp = 100
        comp_template.current_hp = 100
        comp_template.modifiers = []
        comp_template.name = "Template Component"
        comp_template.is_active = True
        
        # Create a fake event or just call the handler logic?
        # BuilderSceneGUI has handle_event which processes actions.
        # But actions come from panels.
        # Let's call the logic block directly via 'handle_event' mocking the action return from left_panel.
        
        # Mock left_panel.handle_event to return ('select_component_type', comp_template)
        self.builder.left_panel.handle_event = MagicMock(return_value=('select_component_type', comp_template))
        
        # Trigger builder handle_event with a dummy pygame event
        dummy_event = MagicMock()
        self.builder.handle_event(dummy_event)
        
        # Verify dragged item is set
        self.assertIsNotNone(self.builder.controller.dragged_item)
        self.assertEqual(self.builder.controller.dragged_item, comp_template)

    def test_drop_validation_success(self):
        """Verify dropping a valid component calls viewmodel.add_component_instance."""
        # Setup: Original component IS on the ship
        original = MagicMock()
        original.modifiers = []
        original.current_hp = 100
        original.max_hp = 100
        original.mass = 10
        original.is_active = True
        original.name = "Original Component"

        # Key Fix: clone() must return a mock with stats too!
        cloned = MagicMock()
        cloned.current_hp = 100
        cloned.max_hp = 100
        cloned.mass = 10
        cloned.is_active = True
        cloned.name = "Original Component"
        cloned.modifiers = []

        original.clone.return_value = cloned

        self.builder.ship.layers[LayerType.OUTER]['components'] = [original]

        # Mock the viewmodel's add_component_instance to return success
        self.builder.viewmodel.add_component_instance = MagicMock(return_value=True)

        self.builder.left_panel.handle_event = MagicMock(return_value=('add_individual', original))

        self.builder.handle_event(MagicMock())

        # Verify viewmodel.add_component_instance was called with cloned component
        self.builder.viewmodel.add_component_instance.assert_called()
        call_args = self.builder.viewmodel.add_component_instance.call_args
        # First arg should be the cloned component, second should be the layer
        self.assertEqual(call_args[0][1], LayerType.OUTER)

    def test_drop_validation_failure(self):
        """Verify showing error on invalid add."""
        original = MagicMock()
        original.modifiers = []
        original.current_hp = 100
        original.max_hp = 100
        original.mass = 10
        original.is_active = True
        original.name = "Original Component"

        # Key Fix: clone() must return a mock with stats too!
        cloned = MagicMock()
        cloned.current_hp = 100
        cloned.max_hp = 100
        cloned.mass = 10
        cloned.is_active = True
        cloned.name = "Original Component"
        cloned.modifiers = []

        original.clone.return_value = cloned

        self.builder.ship.layers[LayerType.OUTER]['components'] = [original]

        # Mock the viewmodel's add_component_instance to return failure
        self.builder.viewmodel.add_component_instance = MagicMock(return_value=False)
        # Mock the _last_result to have errors (last_errors is a property that reads from _last_result)
        mock_result = MagicMock()
        mock_result.errors = ["Overlapping"]
        self.builder.viewmodel._last_result = mock_result

        self.builder.left_panel.handle_event = MagicMock(return_value=('add_individual', original))

        # Capture show_error
        self.builder.show_error = MagicMock()

        self.builder.handle_event(MagicMock())

        # Verify error shown
        self.builder.show_error.assert_called_with("Cannot add: Overlapping")
        # Verify viewmodel was called but returned False
        self.builder.viewmodel.add_component_instance.assert_called()

if __name__ == '__main__':
    unittest.main()
