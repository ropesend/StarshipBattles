import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.simulation.components.component import Modifier


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
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {
            'control_type': 'linear_stepped',
            'step_buttons': [{'label': '<', 'value': 1, 'mode': 'delta_sub'}]
        }

        callback = MagicMock()
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, callback)

        row.build_ui(10)

        # New compact layout has: name_label, entry, slider, json_btn, and step buttons
        assert row.name_label is not None
        assert row.entry is not None
        assert row.slider is not None
        assert row.json_btn is not None
        assert len(row.buttons) == 1  # 1 step button
        assert row.height == 28  # Compact height

    def test_update_state(self):
        """Test that update correctly sets active state and value."""
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        # Mock component with no modifier (not active)
        mock_comp = MagicMock()
        mock_comp.get_modifier.return_value = None

        row.update(mock_comp)
        assert not row.is_active

        # Activate by having the component return a modifier
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod

        row.update(mock_comp)
        assert row.is_active
        assert row.current_value == 50

    def test_readonly_disables_controls(self):
        """Test that readonly mode disables all controls."""
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        mock_comp = MagicMock()
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod

        # Update with readonly=True
        row.update(mock_comp, is_readonly=True)

        assert row.is_active
        assert row.is_readonly
        # JSON button should still be enabled (read-only operation)
        assert row.json_btn.is_enabled

    def test_json_button_event(self):
        """Test that clicking JSON button triggers popup."""
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())
        row.build_ui(10)

        mock_comp = MagicMock()
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod
        row.update(mock_comp)

        # Mock the _show_json_popup method
        row._show_json_popup = MagicMock()

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = row.json_btn

        result = row.handle_event(event)

        assert result
        row._show_json_popup.assert_called_once()

    def test_value_change_callback(self):
        """Test that slider changes trigger callback."""
        from ui.builder.modifier_row import ModifierControlRow
        mod_def = Modifier({'id': 'test_mod', 'name': 'Test Mod', 'type': 'linear', 'min_val': 0, 'max_val': 100})
        config = {'control_type': 'linear'}
        callback = MagicMock()
        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, callback)
        row.build_ui(10)

        mock_comp = MagicMock()
        mock_mod = MagicMock()
        mock_mod.value = 50
        mock_comp.get_modifier.return_value = mock_mod
        row.update(mock_comp)

        # Simulate slider move event
        event = MagicMock()
        event.type = pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
        event.ui_element = row.slider
        row.slider.get_current_value = MagicMock(return_value=75.0)

        result = row.handle_event(event)

        assert result
        callback.assert_called_once_with('value_change', 'test_mod', 75.0)
