import sys
import os

from unittest.mock import MagicMock, patch, PropertyMock
import pygame
import pygame_gui

from game.simulation.components.abilities.ui_colors import HINT_CARGO_GENERIC, HINT_CREW_CAP


class TestDetailPanelRendering:

    # Removed setUpClass/tearDownClass to fix parallel execution failures
    # Cleanup now happens per-test in teardown_method to prevent pygame display state pollution

    def setup_method(self):
        # NOTE: pygame is initialized by the root conftest's session-scope fixture.
        # Do NOT call pygame.init() or set_mode() here as it interferes with
        # parallel test execution.

        # Clear module from cache to ensure patches take effect
        import importlib
        module_name = 'game.ui.screens.builder.detail_panel'
        if module_name in sys.modules:
            del sys.modules[module_name]

        # Patch UI elements at pygame_gui level (applied before module import)
        # NOTE: Must also patch the module-level import in detail_panel.py
        self.uipanel_patch = patch('pygame_gui.elements.UIPanel')
        self.uilabel_patch = patch('pygame_gui.elements.UILabel')
        self.uiimage_patch = patch('pygame_gui.elements.UIImage')
        self.uibutton_patch = patch('pygame_gui.elements.UIButton')
        self.uitextbox_patch = patch('pygame_gui.elements.UITextBox')
        self.modifier_grid_patch = patch('game.ui.panels.modifier_impact_grid.ModifierImpactGrid')
        # Also patch at the module's namespace where UITextBox is actually used
        self.uitextbox_module_patch = patch('game.ui.screens.builder.detail_panel.UITextBox')

        self.MockUIPanel = self.uipanel_patch.start()
        self.MockUILabel = self.uilabel_patch.start()
        self.MockUIImage = self.uiimage_patch.start()
        self.MockUIButton = self.uibutton_patch.start()
        self.MockUITextBox = self.uitextbox_patch.start()
        self.MockModifierGrid = self.modifier_grid_patch.start()
        # Start module-level patch for UITextBox
        self.MockUITextBoxModule = self.uitextbox_module_patch.start()

        # Configure mock grid
        self.mock_grid_instance = self.MockModifierGrid.return_value
        self.mock_grid_instance.panel = MagicMock()
        self.mock_grid_instance.panel.visible = False

        # Ensure the mock instance behaves like a UITextBox for our tests
        # Use the module-level mock since that's what detail_panel.py actually imports
        self.mock_textbox_instance = self.MockUITextBoxModule.return_value

        # Delayed import to allow pygame init (after patches applied)
        from game.ui.screens.builder.detail_panel import ComponentDetailPanel
        self.ComponentDetailPanel = ComponentDetailPanel

        # Mock Pygame and UI Manager
        self.mock_manager = MagicMock(spec=pygame_gui.UIManager)

        # Configure mock manager to return proper values for font dimensions
        # This prevents TypeError when pygame_gui compares MagicMock with int
        mock_rect = pygame.Rect(0, 0, 100, 20)
        mock_font = MagicMock()
        mock_font.get_rect.return_value = mock_rect
        self.mock_manager.get_theme.return_value.get_font.return_value = mock_font

        # Create the panel under test
        self.panel_rect = pygame.Rect(0, 0, 300, 600)
        self.panel = self.ComponentDetailPanel(self.mock_manager, self.panel_rect, "assets/images")

        # Reset mock calls from init
        self.MockUITextBox.reset_mock()

    def teardown_method(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        # Note: pygame and registry cleanup is handled by conftest fixtures
        # (pygame_display_reset and reset_game_state)
        # DO NOT call pygame.quit() or RegistryManager.clear() here as it conflicts with fixtures

    def test_html_stats_generation_basic(self):
        """Verify basic component stats (Name, Type, Mass, HP) are generated."""
        mock_comp = MagicMock()
        mock_comp.name = "Test Component"
        mock_comp.type_str = "Weapon"
        mock_comp.mass = 50.5
        mock_comp.max_hp = 100
        mock_comp.current_hp = 100
        mock_comp.get_ui_rows.return_value = [] # No extra stats
        mock_comp.abilities = {}
        mock_comp.modifiers = []
        mock_comp.sprite_index = 1

        # Set defaults to avoid TypeError
        mock_comp.base_mass = 50.5
        mock_comp.base_max_hp = 100
        mock_comp.allowed_vehicle_types = ["Ship"]
        mock_comp.cost = 0
        mock_comp.level = 0
        mock_comp.rarity = "Common"


        self.panel.show_component(mock_comp)

        # Verify html_text was set and rebuild was called (new API)
        # The panel now sets html_text directly then calls rebuild()
        # Note: Use panel.stats_text_box which is the actual mock instance
        self.panel.stats_text_box.rebuild.assert_called()
        html = self.panel.stats_text_box.html_text

        assert "<b>Test Component</b>" in html
        assert "Weapon" in html
        assert "Mass: 50.5t" in html
        assert "HP: 100" in html

    def test_html_stats_dynamic_abilities(self):
        """Verify dynamic ability stats from get_ui_rows are included."""
        mock_comp = MagicMock()
        mock_comp.name = "Laser"
        mock_comp.type_str = "Weapon"
        mock_comp.mass = 10
        mock_comp.max_hp = 50
        mock_comp.current_hp = 50
        mock_comp.abilities = {}
        mock_comp.modifiers = []
        mock_comp.sprite_index = 1

        # Set defaults to avoid TypeError
        mock_comp.base_mass = 10
        mock_comp.base_max_hp = 50
        mock_comp.allowed_vehicle_types = ["Ship"]
        mock_comp.cost = 0
        mock_comp.level = 0
        mock_comp.rarity = "Common"

        mock_comp.get_ui_rows.return_value = [
            {'label': 'Damage', 'value': '50', 'color_hint': '#FF0000'},
            {'label': 'Range', 'value': '1000m', 'color_hint': '#00FF00'}
        ]

        self.panel.show_component(mock_comp)

        # Verify html_text was set and rebuild was called (new API)
        self.panel.stats_text_box.rebuild.assert_called()
        html = self.panel.stats_text_box.html_text

        assert "<font color='#FF0000'>Damage: 50</font>" in html
        assert "<font color='#00FF00'>Range: 1000m</font>" in html

    def test_html_unregistered_abilities(self):
        """Verify unregistered abilities are shown in the fallback section."""
        mock_comp = MagicMock()
        mock_comp.name = "Mystery Box"
        mock_comp.type_str = "Unknown"
        mock_comp.mass = 1
        mock_comp.max_hp = 1
        mock_comp.current_hp = 1
        mock_comp.get_ui_rows.return_value = []
        mock_comp.modifiers = []
        mock_comp.sprite_index = 1

        # Random custom ability data (unregistered)
        mock_comp.abilities = {
            "SecretAbility": {"power": 9000},
            "CustomPowerAbility": {"energy": 42}
        }
        # Set attributes to avoid MagicMock comparison errors (TypeError: > not supported)
        mock_comp.cost = 0
        mock_comp.level = 0
        mock_comp.rarity = "Common"


        # Mock ABILITY_REGISTRY to ensure SecretAbility is treated as unregistered
        with patch.dict('game.simulation.components.abilities.ABILITY_REGISTRY', {}, clear=True):
             self.panel.show_component(mock_comp)

        # Verify html_text was set and rebuild was called (new API)
        self.panel.stats_text_box.rebuild.assert_called()
        html = self.panel.stats_text_box.html_text

        # Header changed to "Abilities:" in the code
        assert "Abilities:" in html
        # Abilities are formatted with bullet points
        assert "SecretAbility" in html
        assert "CustomPowerAbility" in html


    def test_html_modifiers(self):
        """Verify modifiers are displayed with correct formatting."""
        mock_comp = MagicMock()
        mock_comp.name = "Modded Engine"
        mock_comp.type_str = "Engine"
        mock_comp.mass = 10
        mock_comp.base_mass = 10
        mock_comp.max_hp = 10
        mock_comp.base_max_hp = 10
        mock_comp.current_hp = 10
        mock_comp.allowed_vehicle_types = ["Ship"]

        mock_comp.get_ui_rows.return_value = []
        mock_comp.abilities = {}
        mock_comp.sprite_index = 1

        # Set attributes to avoid MagicMock comparison errors (TypeError: > not supported)
        mock_comp.range = 0
        mock_comp.damage = 0
        mock_comp.firing_arc = 0
        mock_comp.projectile_speed = 0
        mock_comp.facing_angle = 0
        mock_comp.cost = 0
        mock_comp.level = 0
        mock_comp.rarity = "Common"


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
        with patch('game.ui.screens.builder.detail_panel.ModifierLogic.is_modifier_mandatory') as mock_is_mandatory:
            # Side effect: True for turbo_boost, False for heavy_plating
            def side_effect(mod_id, comp):
                return mod_id == "turbo_boost"
            mock_is_mandatory.side_effect = side_effect

            self.panel.show_component(mock_comp)

        # Verify html_text was set and rebuild was called (new API)
        self.panel.stats_text_box.rebuild.assert_called()
        html = self.panel.stats_text_box.html_text

        assert "Modifiers" in html

        # Mandatory: Gold + [A]
        assert "Turbo [A]" in html
        assert f"color='{HINT_CARGO_GENERIC}'" in html  # Gold

        # Optional: Green
        assert "Plating" in html
        assert f"color='{HINT_CREW_CAP}'" in html  # Green
