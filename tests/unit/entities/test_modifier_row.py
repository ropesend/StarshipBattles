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


class TestModifierRowErrorLogging:
    """Tests for error logging in modifier row (ERR-012)."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(pygame.Rect(0, 0, 400, 200), manager=self.manager)

    def test_tooltip_generation_failure_logs_warning(self, caplog):
        """Tooltip generation failure should log warning with modifier details (ERR-012)."""
        import logging
        from ui.builder.modifier_row import ModifierControlRow
        from game.simulation.components.component import Modifier
        from unittest.mock import patch

        # Need to include effects so the code path that calls evaluate_modifier is reached
        mod_def = Modifier({
            'id': 'test_mod',
            'name': 'Test Mod',
            'type': 'linear',
            'min_val': 0,
            'max_val': 100,
            'effects': [{'stat': 'mass', 'operation': 'add', 'value': '@param'}]
        })
        config = {'control_type': 'linear'}

        row = ModifierControlRow(self.manager, self.container, 300, 'test_mod', mod_def, config, MagicMock())

        # Mock ModifierEffectEvaluator.evaluate_modifier to raise during tooltip generation
        with patch('ui.builder.modifier_row.ModifierEffectEvaluator.evaluate_modifier',
                   side_effect=Exception("Test error")):
            with caplog.at_level(logging.WARNING):
                tooltip_text = row._generate_tooltip()

            # Should still return fallback tooltip
            assert tooltip_text is not None
            assert len(tooltip_text) > 0

            # Should have logged a warning about the failure
            warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warning_logs) > 0, "Should log warning when tooltip generation fails"
            warning_text = ' '.join(r.message for r in warning_logs)
            assert 'test_mod' in warning_text or 'tooltip' in warning_text.lower(), \
                f"Warning should include modifier info. Got: {warning_text}"

    def test_tooltip_generation_success_no_warning(self, caplog):
        """Successful tooltip generation should not produce warnings."""
        import logging
        from ui.builder.modifier_row import ModifierControlRow
        from game.simulation.components.component import Modifier

        mod_def = Modifier({
            'id': 'working_mod',
            'name': 'Working Mod',
            'type': 'linear',
            'min_val': 0,
            'max_val': 100,
            'description': 'A working modifier'
        })
        config = {'control_type': 'linear'}

        row = ModifierControlRow(self.manager, self.container, 300, 'working_mod', mod_def, config, MagicMock())

        with caplog.at_level(logging.WARNING):
            tooltip_text = row._generate_tooltip()

        assert tooltip_text is not None
        # Should NOT log warnings for successful tooltip generation
        tooltip_warnings = [r for r in caplog.records
                           if 'working_mod' in r.message.lower() or 'tooltip' in r.message.lower()]
        assert len(tooltip_warnings) == 0, "Successful tooltip should not log warnings"
