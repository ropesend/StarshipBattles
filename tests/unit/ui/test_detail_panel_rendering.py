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
        # Clear module from cache to ensure patches take effect
        module_name = 'game.ui.screens.builder.detail_panel'
        if module_name in sys.modules:
            del sys.modules[module_name]

        # PROJ-494 T2.2: collapsed 7 individual `patch(...).start()` setups
        # into a single loop iterating a `_PATCH_TARGETS` table. `patch.stopall()`
        # in teardown_method handles cleanup uniformly.
        _PATCH_TARGETS = [
            ('MockUIPanel', 'pygame_gui.elements.UIPanel'),
            ('MockUILabel', 'pygame_gui.elements.UILabel'),
            ('MockUIImage', 'pygame_gui.elements.UIImage'),
            ('MockUIButton', 'pygame_gui.elements.UIButton'),
            ('MockUITextBox', 'pygame_gui.elements.UITextBox'),
            ('MockModifierGrid', 'game.ui.panels.modifier_impact_grid.ModifierImpactGrid'),
            # Patch UITextBox in the module's own namespace where it's actually used.
            ('MockUITextBoxModule', 'game.ui.screens.builder.detail_panel.UITextBox'),
        ]
        for attr, target in _PATCH_TARGETS:
            setattr(self, attr, patch(target).start())

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
        # PROJ-388: ComponentDetailPanel requires a ModifierLogicService instance
        # (constructor injection — the deprecated ``ModifierLogic`` static
        # wrapper has been removed).
        self.mock_modifier_logic = MagicMock()
        self.panel = self.ComponentDetailPanel(
            self.mock_manager,
            self.panel_rect,
            modifier_logic=self.mock_modifier_logic,
        )

        # Reset mock calls from init
        self.MockUITextBox.reset_mock()

    def teardown_method(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

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

        # PROJ-388: Configure injected ModifierLogicService mock to simulate
        # one mandatory and one optional modifier.
        def side_effect(mod_id, comp):
            return mod_id == "turbo_boost"
        self.mock_modifier_logic.is_modifier_mandatory.side_effect = side_effect

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
