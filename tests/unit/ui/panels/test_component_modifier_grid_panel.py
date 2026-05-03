"""Tests for ComponentModifierGridPanel (PROJ-142 Phase 2 Task 2.6).

Tests the dedicated panel for displaying component modifier impact grids.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Helpers ---

def _make_mock_component():
    """Create a mock Component with modifiers."""
    comp = MagicMock()
    comp.id = "laser_standard"
    comp.modifiers = {
        'accuracy': {'flat': 5, 'mult': 1.1},
        'damage': {'flat': 10, 'mult': 1.0}
    }
    return comp


def _make_mock_event_bus():
    """Create a mock EventBus."""
    bus = MagicMock()
    bus.subscribe = MagicMock()
    return bus


# --- Selection Changed Handler Tests ---

class TestOnSelectionChanged:
    """Tests for selection change handling."""

    def test_selection_tuple_extracts_component(self):
        """_on_selection_changed extracts component from tuple."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        comp = _make_mock_component()
        panel.update_component = MagicMock()

        selection_data = ("layer", "slot", comp)
        panel._on_selection_changed(selection_data)

        panel.update_component.assert_called_once_with(comp)

    def test_selection_object_with_id(self):
        """_on_selection_changed handles object with id attribute."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        comp = _make_mock_component()
        panel.update_component = MagicMock()

        panel._on_selection_changed(comp)

        panel.update_component.assert_called_once_with(comp)

    def test_selection_none_clears_component(self):
        """_on_selection_changed with None clears component."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.update_component = MagicMock()

        panel._on_selection_changed(None)

        panel.update_component.assert_called_once_with(None)

    def test_selection_invalid_clears_component(self):
        """_on_selection_changed with invalid data clears component."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.update_component = MagicMock()

        # String doesn't have 'id' attribute
        panel._on_selection_changed("invalid")

        panel.update_component.assert_called_once_with(None)


# --- Ship Updated Handler Tests ---

class TestOnShipUpdated:
    """Tests for ship update handling."""

    def test_ship_updated_refreshes_grid(self):
        """_on_ship_updated refreshes modifier_grid."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        comp = _make_mock_component()
        panel.current_component = comp
        panel.modifier_grid = MagicMock()

        panel._on_ship_updated(None)

        panel.modifier_grid.update.assert_called_once_with(comp)

    def test_ship_updated_no_component_no_refresh(self):
        """_on_ship_updated does nothing without current_component."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.current_component = None
        panel.modifier_grid = MagicMock()

        panel._on_ship_updated(None)

        panel.modifier_grid.update.assert_not_called()


# --- Update Component Tests ---

class TestUpdateComponent:
    """Tests for component update."""

    def test_update_stores_component(self):
        """update_component stores component reference."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        comp = _make_mock_component()
        panel.modifier_grid = MagicMock()

        panel.update_component(comp)

        assert panel.current_component is comp

    def test_update_with_modifiers_updates_grid(self):
        """update_component with modifiers updates grid."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        comp = _make_mock_component()
        panel.modifier_grid = MagicMock()

        panel.update_component(comp)

        panel.modifier_grid.update.assert_called_once_with(comp)

    def test_update_none_clears_grid(self):
        """update_component(None) clears grid."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.modifier_grid = MagicMock()

        panel.update_component(None)

        panel.modifier_grid.update.assert_called_once_with(None)

    def test_update_no_modifiers_clears_grid(self):
        """update_component with no modifiers clears grid."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        comp = MagicMock()
        comp.modifiers = None
        panel.modifier_grid = MagicMock()

        panel.update_component(comp)

        panel.modifier_grid.update.assert_called_once_with(None)


# --- Draw Tests ---

class TestDraw:
    """Tests for draw method."""

    def test_draw_calls_grid_draw(self):
        """draw calls modifier_grid.draw when visible."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.panel = MagicMock()
        panel.panel.visible = True
        panel.modifier_grid = MagicMock()

        screen = pygame.Surface((800, 600))
        panel.draw(screen)

        panel.modifier_grid.draw.assert_called_once_with(screen)

    def test_draw_skips_when_hidden(self):
        """draw skips grid.draw when panel hidden."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.panel = MagicMock()
        panel.panel.visible = False
        panel.modifier_grid = MagicMock()

        screen = pygame.Surface((800, 600))
        panel.draw(screen)

        panel.modifier_grid.draw.assert_not_called()


# --- Event Handling Tests ---

class TestHandleEvent:
    """Tests for event handling."""

    def test_handle_event_visible_delegates(self):
        """handle_event delegates to modifier_grid when visible."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.panel = MagicMock()
        panel.panel.visible = True
        panel.modifier_grid = MagicMock()
        panel.modifier_grid.handle_event.return_value = True

        event = MagicMock()
        result = panel.handle_event(event)

        panel.modifier_grid.handle_event.assert_called_once_with(event)
        assert result is True

    def test_handle_event_hidden_returns_false(self):
        """handle_event returns False when panel hidden."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.panel = MagicMock()
        panel.panel.visible = False
        panel.modifier_grid = MagicMock()

        event = MagicMock()
        result = panel.handle_event(event)

        panel.modifier_grid.handle_event.assert_not_called()
        assert result is False


# --- Visibility Tests ---

class TestVisibility:
    """Tests for show/hide methods."""

    def test_show_shows_panel(self):
        """show calls panel.show."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.panel = MagicMock()

        panel.show()

        panel.panel.show.assert_called_once()

    def test_hide_hides_panel(self):
        """hide calls panel.hide."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.panel = MagicMock()

        panel.hide()

        panel.panel.hide.assert_called_once()


# --- Kill / Cleanup Tests ---

class TestPanelKill:
    """Tests for panel cleanup."""

    def test_kill_destroys_modifier_grid(self):
        """kill destroys modifier_grid."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.modifier_grid = MagicMock()
        panel.panel = MagicMock()
        panel.panel.alive.return_value = True

        panel.kill()

        panel.modifier_grid.kill.assert_called_once()

    def test_kill_destroys_main_panel(self):
        """kill destroys main panel."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.modifier_grid = MagicMock()
        panel.panel = MagicMock()
        panel.panel.alive.return_value = True

        panel.kill()

        panel.panel.kill.assert_called_once()

    def test_kill_handles_dead_panel(self):
        """kill handles case where panel is already dead."""
        from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel

        with patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None):
            panel = ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)

        panel.modifier_grid = MagicMock()
        panel.panel = MagicMock()
        panel.panel.alive.return_value = False

        # Should not raise
        panel.kill()

        panel.panel.kill.assert_not_called()
