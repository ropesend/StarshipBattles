import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame
import pygame_gui

class TestDetailPanelRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        # Delayed import to allow pygame init
        from ui.builder.detail_panel import ComponentDetailPanel
        self.ComponentDetailPanel = ComponentDetailPanel

        # Mock Pygame and UI Manager
        self.mock_manager = MagicMock(spec=pygame_gui.UIManager)
        
        # Patch pygame.Rect to behave like a real Rect for layout logic
        self.rect_patcher = patch('pygame.Rect')
        self.MockRect = self.rect_patcher.start()
        # Side effect to return a mock that stores x,y,w,h
        def mock_rect(*args):
            r = MagicMock()
            if len(args) == 4:
                r.x, r.y, r.width, r.height = args
            elif len(args) == 1 and isinstance(args[0], tuple) and len(args[0]) == 4:
                r.x, r.y, r.width, r.height = args[0]
            else:
                 # Default fallback
                 r.x, r.y, r.width, r.height = 0, 0, 100, 100
            
            r.bottom = r.y + r.height
            return r
        self.MockRect.side_effect = mock_rect
        
        # Patch UI elements to avoid actual GUI creation
        self.uipanel_patch = patch('ui.builder.detail_panel.UIPanel')
        self.uilabel_patch = patch('ui.builder.detail_panel.UILabel')
        self.uiimage_patch = patch('ui.builder.detail_panel.UIImage')
        self.uibutton_patch = patch('ui.builder.detail_panel.UIButton')
        
        # Patch both possible import locations for UITextBox to catch local import
        self.uitextbox_patch = patch('pygame_gui.elements.UITextBox')
        self.uitextbox_patch_real = patch('pygame_gui.elements.ui_text_box.UITextBox')
        
        self.uipanel_patch.start()
        self.uilabel_patch.start()
        self.uiimage_patch.start()
        self.uibutton_patch.start()
        self.MockUITextBox = self.uitextbox_patch.start()
        self.MockUITextBoxReal = self.uitextbox_patch_real.start()
        
        # Create the panel under test
        self.panel_rect = pygame.Rect(0, 0, 300, 600)
        self.panel = ComponentDetailPanel(self.mock_manager, self.panel_rect, "assets/images")
        
        # Reset mock calls from init
        self.MockUITextBox.reset_mock()

    def tearDown(self):
        self.rect_patcher.stop()
        self.uipanel_patch.stop()
        self.uilabel_patch.stop()
        self.uiimage_patch.stop()
        self.uibutton_patch.stop()
        self.uitextbox_patch.stop()

    def test_html_stats_generation_basic(self):
        """Verify basic component stats (Name, Type, Mass, HP) are generated."""
        mock_comp = MagicMock()
        mock_comp.name = "Test Component"
        mock_comp.type_str = "Weapon"
        mock_comp.mass = 50.5
        mock_comp.max_hp = 100
        mock_comp.get_ui_rows.return_value = [] # No extra stats
        mock_comp.abilities = {}
        mock_comp.modifiers = []
        mock_comp.sprite_index = 1
        
        self.panel.show_component(mock_comp)
        
        # Get the HTML text set on the textbox
        # Access the instance created by the mock class
        textbox_instance = self.panel.stats_text_box
        self.assertTrue(textbox_instance.html_text) # Should be set
        
        html = textbox_instance.html_text
        self.assertIn("<b>Test Component</b>", html)
        self.assertIn("Weapon", html)
        self.assertIn("Mass: 50.5t", html)
        self.assertIn("HP: 100", html)

    def test_html_stats_dynamic_abilities(self):
        """Verify dynamic ability stats from get_ui_rows are included."""
        mock_comp = MagicMock()
        mock_comp.name = "Laser"
        mock_comp.type_str = "Weapon"
        mock_comp.mass = 10
        mock_comp.max_hp = 50
        mock_comp.abilities = {}
        mock_comp.modifiers = []
        mock_comp.sprite_index = 1
        
        # Mock get_ui_rows
        mock_comp.get_ui_rows.return_value = [
            {'label': 'Damage', 'value': '50', 'color_hint': '#FF0000'},
            {'label': 'Range', 'value': '1000m', 'color_hint': '#00FF00'}
        ]
        
        self.panel.show_component(mock_comp)
        
        html = self.panel.stats_text_box.html_text
        self.assertIn("<font color='#FF0000'>Damage: 50</font>", html)
        self.assertIn("<font color='#00FF00'>Range: 1000m</font>", html)

    def test_html_unregistered_abilities(self):
        """Verify unregistered abilities are shown in the fallback section."""
        mock_comp = MagicMock()
        mock_comp.name = "Mystery Box"
        mock_comp.type_str = "Unknown"
        mock_comp.mass = 1
        mock_comp.max_hp = 1
        mock_comp.get_ui_rows.return_value = []
        mock_comp.modifiers = []
        mock_comp.sprite_index = 1
        
        # Random custom ability data
        mock_comp.abilities = {
            "SecretAbility": {"power": 9000},
            "ProjectileWeapon": {} # Should be skipped (legacy shim)
        }
        
        # Mock ABILITY_REGISTRY to ensure SecretAbility is treated as unregistered
        with patch.dict('abilities.ABILITY_REGISTRY', {}, clear=True):
             self.panel.show_component(mock_comp)
        
        html = self.panel.stats_text_box.html_text
        self.assertIn("Abilities:", html)
        self.assertIn("SecretAbility: {'power': 9000}", html)
        self.assertNotIn("ProjectileWeapon", html)

    def test_html_modifiers(self):
        """Verify modifiers are displayed with correct formatting."""
        mock_comp = MagicMock()
        mock_comp.name = "Modded Engine"
        mock_comp.type_str = "Engine"
        mock_comp.mass = 10
        mock_comp.max_hp = 10
        mock_comp.get_ui_rows.return_value = []
        mock_comp.abilities = {}
        mock_comp.sprite_index = 1
        
        # Mock Modifiers
        mock_mod1 = MagicMock()
        mock_mod1.definition.id = "turbo_boost"
        mock_mod1.definition.name = "Turbo"
        mock_mod1.value = 1.5
        
        mock_mod2 = MagicMock()
        mock_mod2.definition.id = "heavy_plating"
        mock_mod2.definition.name = "Plating"
        mock_mod2.value = 2.0
        
        mock_comp.modifiers = [mock_mod1, mock_mod2]
        
        # Patch ModifierLogic to simulate one mandatory and one optional modifier
        with patch('ui.builder.detail_panel.ModifierLogic.is_modifier_mandatory') as mock_is_mandatory:
            # Side effect: True for turbo_boost, False for heavy_plating
            def side_effect(mod_id, comp):
                return mod_id == "turbo_boost"
            mock_is_mandatory.side_effect = side_effect
            
            self.panel.show_component(mock_comp)
            
        html = self.panel.stats_text_box.html_text
        self.assertIn("Modifiers:", html)
        
        # Mandatory: Gold + [A]
        self.assertIn("Turbo [A]", html)
        self.assertIn("color='#FFD700'", html) # Gold
        
        # Optional: Green
        self.assertIn("Plating", html)
        self.assertIn("color='#96FF96'", html) # Green

if __name__ == '__main__':
    unittest.main()
