import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from ui.builder.modifier_row import ModifierControlRow
from ui.builder.modifier_logic import ModifierLogic
from components import Modifier

class TestModifierRow(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1,1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(pygame.Rect(0,0,100,100), manager=self.manager)
        
    def tearDown(self):
        pygame.quit()
        
    def test_build_ui_creates_elements(self):
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
        mod_def = Modifier({'id': 'mandatory_mod', 'name': 'Mandatory', 'type': 'linear'})
        row = ModifierControlRow(self.manager, self.container, 300, 'mandatory_mod', mod_def, {}, MagicMock())
        row.build_ui(10)
        
        mock_comp = MagicMock()
        # Mock logic
        mock_comp.get_modifier.return_value = MagicMock(value=10)
        
        # Patch logic
        with unittest.mock.patch('ui.builder.modifier_row.ModifierLogic.is_modifier_mandatory', return_value=True):
             row.update(mock_comp, {})
             
        # Toggle should be locked? Code didn't explicitly implement lock yet in my snippet?
        # Ah, I wrote `pass # self.toggle_btn.disable()` in the thought process but implemented?
        # Let's check the code I wrote.
        # "if component and ModifierLogic.is_modifier_mandatory... pass # self.toggle_btn.disable() (Optional choice)"
        # So I did NOT disable it in the snippet I wrote "pass".
        # But handle_event has: "if self.component_context and ModifierLogic.is_modifier_mandatory... return False"
        # So it is effectively locked logic-wise.
        
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = row.toggle_btn
        
        with unittest.mock.patch('ui.builder.modifier_row.ModifierLogic.is_modifier_mandatory', return_value=True):
             row.component_context = mock_comp # Ensure context set
             result = row.handle_event(event)
             
        self.assertFalse(result) # Should return False (no change) for mandatory toggle
