import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
# Import the class to test. Need to ensure path is correct.
# Assuming builder_components is in root or accessible via sys.path logic in tests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from builder_components import ModifierEditorPanel
from components import MODIFIER_REGISTRY, Modifier

class TestMandatoryModifiers(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.window = pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(pygame.Rect(0,0,100,100), manager=self.manager)
        
        # Ensure registry has our mods
        # We might need to mock MODIFIER_REGISTRY if it isn't populated
        if 'simple_size' not in MODIFIER_REGISTRY:
            MODIFIER_REGISTRY['simple_size'] = Modifier({'id': 'simple_size', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100})
        if 'range_mount' not in MODIFIER_REGISTRY:
            MODIFIER_REGISTRY['range_mount'] = Modifier({'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10})
        if 'facing' not in MODIFIER_REGISTRY:
             MODIFIER_REGISTRY['facing'] = Modifier({'id': 'facing', 'name': 'Facing', 'type': 'linear', 'min_val': 0, 'max_val': 360})

    def tearDown(self):
        pygame.quit()

    def _setup_mock_comp(self, type_str):
        mock_comp = MagicMock()
        mock_comp.name = f"Test{type_str}"
        mock_comp.type_str = type_str
        
        mods = {}
        def get_mod(mid): return mods.get(mid)
        def add_mod(mid):
            m = MagicMock()
            m.value = 1.0 # Default
            mods[mid] = m
            return True
        def remove_mod(mid):
            if mid in mods: del mods[mid]
            
        mock_comp.get_modifier.side_effect = get_mod
        mock_comp.add_modifier.side_effect = add_mod
        mock_comp.remove_modifier.side_effect = remove_mod
        return mock_comp, mods

    def test_auto_apply_size(self):
        panel = ModifierEditorPanel(self.manager, self.container, 400, MagicMock(), MagicMock())
        mock_comp, mods = self._setup_mock_comp('reactor')
        # Ensure registry has simple_size_mount
        with patch.dict(MODIFIER_REGISTRY, {'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100})}, clear=True):
             # Run layout
             panel.rebuild(mock_comp, {})
             panel.layout(10)
        
        self.assertIn('simple_size_mount', mods)
        
    def test_auto_apply_range_weapon(self):
        panel = ModifierEditorPanel(self.manager, self.container, 400, MagicMock(), MagicMock())
        # USE CORRECT TYPE STRING
        mock_comp, mods = self._setup_mock_comp('ProjectileWeapon')
        
        # Setup registry with all needed mods and CORRECT RESTRICTIONS
        test_registry = {
            'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100}),
            'range_mount': Modifier({
                'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10,
                'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}
            }),
            'facing': Modifier({
                'id': 'facing', 'name': 'Facing', 'type': 'linear', 'min_val': 0, 'max_val': 360,
                'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}
            })
        }
        
        with patch.dict(MODIFIER_REGISTRY, test_registry, clear=True):
            # Run layout
            panel.rebuild(mock_comp, {})
            panel.layout(10)
            
        self.assertIn('range_mount', mods)
        self.assertIn('simple_size_mount', mods)
        self.assertIn('facing', mods)
        
    def test_no_auto_apply_range_non_weapon(self):
        panel = ModifierEditorPanel(self.manager, self.container, 400, MagicMock(), MagicMock())
        mock_comp, mods = self._setup_mock_comp('Reactor') # PascalCase for non-weapon too likely
        
        test_registry = {
             'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100}),
             'range_mount': Modifier({
                'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10,
                'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}
            })
        }

        with patch.dict(MODIFIER_REGISTRY, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)
        
        self.assertNotIn('range_mount', mods)
        self.assertIn('simple_size_mount', mods)

    def test_prevent_removal(self):
        panel = ModifierEditorPanel(self.manager, self.container, 400, MagicMock(), MagicMock())
        mock_comp, mods = self._setup_mock_comp('Reactor')
        
        # Pre-add
        m = MagicMock()
        m.value = 1.0
        mods['simple_size_mount'] = m
        
        test_registry = {
            'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100})
        }
        
        with patch.dict(MODIFIER_REGISTRY, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)
            
            # Find button
            try:
                idx = panel.modifier_id_list.index('simple_size_mount')
                btn = panel.modifier_buttons[idx]
            except ValueError:
                self.fail("simple_size_mount not found in UI")
                
            event = MagicMock()
            event.type = pygame_gui.UI_BUTTON_PRESSED
            event.ui_element = btn
            
            panel.handle_event(event)
        
        # Verify NOT removed
        self.assertIn('simple_size_mount', mods)
        mock_comp.remove_modifier.assert_not_called()

if __name__ == '__main__':
    unittest.main()
