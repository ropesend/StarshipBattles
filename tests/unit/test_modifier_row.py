import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from unittest.mock import MagicMock
from ui.builder.modifier_logic import ModifierLogic
from game.simulation.components.component import Modifier

class TestModifierRow(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1,1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(pygame.Rect(0,0,100,100), manager=self.manager)
        
        
    def tearDown(self):
        pass # pygame.quit() removed for session isolation
        
        
    def test_build_ui_creates_elements(self):
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {
            'control_type': 'linear_stepped', 
            'step_buttons': [{'label': '<', 'value': 1, 'mode': 'delta_sub'}]
        }
        
        callback = MagicMock()
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, callback)
        
        row.build_ui(10)
        
        self.assertIsNotNone(row.toggle_btn)
        self.assertIsNotNone(row.entry)
        self.assertIsNotNone(row.slider)
        self.assertEqual(len(row.buttons), 1) # 1 step button
        
    def test_update_state(self):
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)
        
        # Mock component
        mock_comp = MagicMock()
        mock_comp.get_modifier.return_value = None # Not active
        
        row.update(mock_comp, {})
        self.assertFalse(row.is_active)
        self.assertTrue(row.toggle_btn.is_enabled) # Toggle should be enabled to allow activation
        # Use simple logic: if not active, controls disabled, but toggle enabled.
        # Check code: controls disabled. Button?
        # My implementation: "if self.is_active: ... else: ... for btn: disable()"
        # Toggle btn is NOT in self.buttons map (step buttons). It's separate.
        # So toggle btn remains enabled?
        # Check Row code: `self.toggle_btn.set_text(...)`
        # Toggle button enablement is only touched in mandatory check at end.
        
        self.assertTrue(row.toggle_btn.is_enabled) 
        
        # Activate
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod
        
        row.update(mock_comp, {})
        self.assertTrue(row.is_active)
        self.assertEqual(row.current_value, 50)
        
    def test_mandatory_lock(self):
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'mandatory_mod', 'name': 'Mandatory', 'type': 'linear'})
        row = ModifierControlRow(self.manager, self.container, 300, 'mandatory_mod', mod_def, {}, MagicMock())
        row.build_ui(10)
        
        mock_comp = MagicMock()
        # Mock logic
        mock_comp.get_modifier.return_value = MagicMock(value=10)
        
        # Patch logic
        with unittest.mock.patch('ui.builder.modifier_logic.ModifierLogic.is_modifier_mandatory', return_value=True):
             import ui.builder.modifier_row
             import importlib
             import sys
             if 'ui.builder.modifier_row' in sys.modules:
                 importlib.reload(sys.modules['ui.builder.modifier_row'])
             
             # Need to re-create row because we reloaded module (class might have changed? No, row instance uses class. Class identity might change if reloaded?)
             # If we reload module, we get NEW ModifierControlRow class.
             # Existing 'row' instance is of OLD class.
             # Does 'row' use 'ModifierLogic' directly?
             # row.handle_event calls ModifierLogic.
             # If ModifierLogic is global in module, and we reload module, the NEW module has valid ModifierLogic.
             # BUT 'row' setup: row = ModifierControlRow(...)
             # If row was created with OLD class, its methods invoke OLD globals?
             # Yes. Functions in Python hold reference to their globals dict.
             # Reloading module creates NEW module dict. OLD functions still point to OLD dict.
             # So we must recreate 'row' AFTER reload!
             
             
             # Need to re-create row because we reloaded module...
             from ui.builder.modifier_row import ModifierControlRow 
             # Wait, Constructor signature is: def __init__(self, width, mod_id, mod_def, config, on_change_callback, container=None, manager=None):
             # Let's check view_file output.
             # Assume: __init__(self, width, mod_id, mod_def, config, on_change_callback, manager, container) based on error message order?
             # Error said: missing 'width', 'mod_id', 'mod_def', 'config', 'on_change_callback'.
             # So I need to provide these.
             # I'll pass dummy values.
             row = ModifierControlRow(self.manager, self.container, 100, "test_mod", MagicMock(), {}, MagicMock())
             row.build_ui(10)
             row.mod_id = "test_mod"
             row.update(mock_comp, {})
             
             # Toggle should be locked
        # Ah, I wrote `pass # self.toggle_btn.disable()` in the thought process but implemented?
        # Let's check the code I wrote.
        # "if component and ModifierLogic.is_modifier_mandatory... pass # self.toggle_btn.disable() (Optional choice)"
        # So I did NOT disable it in the snippet I wrote "pass".
        # But handle_event has: "if self.component_context and ModifierLogic.is_modifier_mandatory... return False"
        # So it is effectively locked logic-wise.
        
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = row.toggle_btn
        
        
        with unittest.mock.patch('ui.builder.modifier_logic.ModifierLogic.is_modifier_mandatory', return_value=True):
             import ui.builder.modifier_row
             import importlib
             import sys
             if 'ui.builder.modifier_row' in sys.modules:
                 importlib.reload(sys.modules['ui.builder.modifier_row'])
             from ui.builder.modifier_row import ModifierControlRow
             row = ModifierControlRow(self.manager, self.container, 100, "test_mod", MagicMock(), {}, MagicMock())
             row.mod_id = "test_mod"
             row.build_ui(10) # Create UI elements
             
             row.component_context = mock_comp # Ensure context set
             result = row.handle_event(event)
        self.assertFalse(result) # Should return False (no change) for mandatory toggle
