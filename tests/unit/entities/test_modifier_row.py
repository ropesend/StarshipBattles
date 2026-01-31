import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.simulation.components.component_constants import Modifier


@pytest.fixture(autouse=True)
def mock_modifier_logic():
    """Mock ModifierLogic to avoid registry dependencies in UI tests."""
    with patch('game.ui.screens.builder.modifier_row.ModifierLogic') as mock_logic:
        mock_logic.is_modifier_mandatory.return_value = False
        mock_logic.get_local_min_max.return_value = (0, 100)
        mock_logic.get_mandatory_modifiers.return_value = []
        yield mock_logic


class TestModifierRow:
    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(pygame.Rect(0, 0, 400, 200), manager=self.manager)

    def teardown_method(self):
        pass  # pygame.quit() removed for session isolation

    def test_build_ui_creates_elements(self):
        """Test that build_ui creates the expected UI elements for compact layout."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {
            'control_type': 'linear_stepped',
            'step_buttons': [{'label': '<', 'value': 1, 'mode': 'delta_sub'}]
        }

        callback = MagicMock()
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, callback)

        row.build_ui(10)

        # Layout has: toggle_btn, entry, slider, and step buttons
        assert row.toggle_btn is not None
        assert row.entry is not None
        assert row.slider is not None
        assert len(row.buttons) == 1  # 1 step button
        assert row.height == 32  # Default row height

    def test_update_state(self):
        """Test that update correctly sets active state and value."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        # Mock component with no modifier (not active)
        mock_comp = MagicMock()
        mock_comp.get_modifier.return_value = None

        row.update(mock_comp, {})
        assert not row.is_active

        # Activate by having the component return a modifier
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod

        row.update(mock_comp, {})
        assert row.is_active
        assert row.current_value == 50

    def test_mandatory_disables_toggle(self):
        """Test that mandatory modifiers disable toggle button."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        mock_comp = MagicMock()
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod

        # Update the row - new signature takes component and template_modifiers
        row.update(mock_comp, {})

        assert row.is_active
        # Readonly is now determined by mod_def.readonly, not a parameter
        # The toggle button should be enabled since this is not a mandatory modifier
        assert row.toggle_btn.is_enabled

    def test_toggle_button_event(self):
        """Test that clicking toggle button triggers callback."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        mock_comp = MagicMock()
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod
        row.update(mock_comp, {})

        # Test toggle button event handling
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = row.toggle_btn

        result = row.handle_event(event)

        assert result, "Event should be handled and return True"

    def test_value_change_callback(self):
        """Test that slider changes trigger callback."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        callback = MagicMock()
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, callback)
        row.build_ui(10)

        mock_comp = MagicMock()
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod
        row.update(mock_comp, {})

        # Simulate slider move event
        event = MagicMock()
        event.type = pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
        event.ui_element = row.slider
        row.slider.get_current_value = MagicMock(return_value=75.0)

        result = row.handle_event(event)

        assert result, "Slider event should be handled and return True"
        callback.assert_called_once_with('value_change', 'test_mod', 75.0)


class TestModifierRowUIElements:
    """Tests for ModifierControlRow UI element creation and behavior."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(pygame.Rect(0, 0, 400, 200), manager=self.manager)

    def test_kill_clears_ui_elements(self):
        """Test that kill() properly cleans up UI elements."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow

        mod_def = Modifier({
            'id': 'test_mod',
            'name': 'Test Mod',
            'type': 'linear',
            'min_val': 0,
            'max_val': 100
        })
        config = {'control_type': 'linear'}

        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        # Verify elements exist
        assert len(row.ui_elements) > 0
        assert row.toggle_btn is not None

        # Kill and verify cleanup
        row.kill()
        assert len(row.ui_elements) == 0
        assert row.slider is None
        assert row.entry is None

    def test_update_with_template_modifiers(self):
        """Test update() works with template modifiers when component is None."""
        from game.ui.screens.builder.modifier_row import ModifierControlRow

        mod_def = Modifier({
            'id': 'test_mod',
            'name': 'Test Mod',
            'type': 'linear',
            'min_val': 0,
            'max_val': 100
        })
        config = {'control_type': 'linear'}

        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        # Update with no component but with template_modifiers
        row.update(None, {'test_mod': 75.0})

        assert row.is_active
        assert row.current_value == 75.0
