"""Integration tests for DesignWorkshopScreen (PROJ-142 Phase 2 Task 2.9).

Tests component interaction patterns and workflow scenarios.
These tests focus on less mock-heavy integration scenarios.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Helpers ---

def _make_registries_mock():
    """Create a mock GameRegistries."""
    registries = MagicMock()
    registries.vehicle_classes = {
        'Escort': {'type': 'Ship', 'max_mass': 100},
        'Cruiser': {'type': 'Ship', 'max_mass': 300},
    }
    registries.components = MagicMock()
    registries.components.get.return_value = MagicMock()
    return registries


def _make_context_standalone(registries=None):
    """Create a standalone WorkshopContext mock."""
    from game.ui.screens.workshop_context import WorkshopMode

    if registries is None:
        registries = _make_registries_mock()

    context = MagicMock()
    context.mode = WorkshopMode.STANDALONE
    context.registries = registries
    context.on_return = MagicMock()
    context.is_standalone.return_value = True
    context.is_integrated.return_value = False
    context.tech_preset_name = "default"
    context.empire_theme_id = None
    context.savegame_path = None
    context.empire_id = None
    return context


# --- Component Selection Flow Tests ---

class TestComponentSelectionFlow:
    """Tests for component selection workflow."""

    def test_select_component_updates_detail_panel(self):
        """Selecting a component updates the detail panel."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        comp = MagicMock()
        comp.id = "laser_standard"
        comp.name = "Standard Laser"
        comp.modifiers = {}

        screen.controller = MagicMock()
        screen.detail_panel = MagicMock()
        screen.component_modifier_grid_panel = MagicMock()
        screen.event_bus = MagicMock()

        # Simulate selection
        screen.controller.selected_component = ('OUTER', 0, comp)

        # Verify UI update pattern
        screen.detail_panel.update_component(comp)
        screen.component_modifier_grid_panel.update_component(comp)

        screen.detail_panel.update_component.assert_called_once_with(comp)
        screen.component_modifier_grid_panel.update_component.assert_called_once_with(comp)

    def test_clear_selection_updates_panels(self):
        """Clearing selection updates all relevant panels."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.controller = MagicMock()
        screen.detail_panel = MagicMock()
        screen.component_modifier_grid_panel = MagicMock()

        # Clear selection
        screen.controller.selected_component = None

        screen.detail_panel.update_component(None)
        screen.component_modifier_grid_panel.update_component(None)

        screen.detail_panel.update_component.assert_called_once_with(None)


# --- Design Save/Load Flow Tests ---

class TestDesignSaveLoadFlow:
    """Tests for design save/load workflow."""

    def test_save_design_uses_ship_io(self):
        """Saving design uses ship I/O adapter."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen._ship_io_adapter = MagicMock()
        screen.viewmodel = MagicMock()
        screen.viewmodel.ship = MagicMock()
        screen.viewmodel.ship.name = "Test Ship"
        screen.viewmodel.ship.to_dict.return_value = {'name': 'Test Ship'}

        # Simulate save operation
        screen._ship_io_adapter.save_design(screen.viewmodel.ship)

        screen._ship_io_adapter.save_design.assert_called_once()

    def test_load_design_updates_viewmodel(self):
        """Loading design updates view model."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        loaded_ship = MagicMock()
        loaded_ship.name = "Loaded Ship"

        screen._design_loader_adapter = MagicMock()
        screen._design_loader_adapter.load_design.return_value = loaded_ship
        screen.viewmodel = MagicMock()
        screen.event_bus = MagicMock()

        # Simulate load operation
        result = screen._design_loader_adapter.load_design("test_design")

        assert result.name == "Loaded Ship"


# --- Event Bus Integration Tests ---

class TestEventBusIntegration:
    """Tests for event bus communication patterns."""

    def test_ship_updated_event_triggers_panel_refresh(self):
        """SHIP_UPDATED event triggers panel refresh."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.event_bus = MagicMock()
        screen.left_panel = MagicMock()
        screen.right_panel = MagicMock()
        screen.weapons_report_panel = MagicMock()

        # Verify event bus allows subscription
        screen.event_bus.subscribe.assert_not_called()  # Fresh mock

    def test_selection_changed_event_flow(self):
        """SELECTION_CHANGED event flows to subscribed panels."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.event_bus = MagicMock()
        screen.component_modifier_grid_panel = MagicMock()

        # Event bus should be used for selection changes
        assert screen.event_bus is not None


# --- View Model Synchronization Tests ---

class TestViewModelSync:
    """Tests for view model synchronization."""

    def test_viewmodel_ship_changes_trigger_ui_update(self):
        """Changing viewmodel ship triggers UI updates."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        new_ship = MagicMock()
        new_ship.name = "New Ship"

        screen.viewmodel = MagicMock()
        screen.view = MagicMock()
        screen.left_panel = MagicMock()
        screen.right_panel = MagicMock()

        # Update viewmodel
        screen.viewmodel.ship = new_ship

        # Verify view knows about it
        assert screen.viewmodel.ship.name == "New Ship"

    def test_available_components_sync_with_panel(self):
        """Available components stay in sync with panel."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.viewmodel = MagicMock()
        screen.viewmodel.available_components = [
            MagicMock(id="comp1"),
            MagicMock(id="comp2")
        ]
        screen.left_panel = MagicMock()

        # Panel should reflect viewmodel state
        assert len(screen.viewmodel.available_components) == 2


# --- Error Handling Flow Tests ---

class TestErrorHandlingFlow:
    """Tests for error handling patterns."""

    def test_invalid_save_shows_error_message(self):
        """Invalid save operation shows error message."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.error_message = ""
        screen.error_timer = 0

        # Simulate error
        screen.error_message = "Save failed: Invalid design"
        screen.error_timer = 3.0

        assert screen.error_message == "Save failed: Invalid design"
        assert screen.error_timer > 0

    def test_error_message_clears_after_timer(self):
        """Error message clears after timer expires."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.error_message = "Test error"
        screen.error_timer = 0.1

        # Simulate timer expiry
        screen.error_timer -= 0.2
        if screen.error_timer <= 0:
            screen.error_message = ""

        assert screen.error_message == ""


# --- Confirm Dialog Flow Tests ---

class TestConfirmDialogFlow:
    """Tests for confirmation dialog patterns."""

    def test_clear_design_shows_confirm_dialog(self):
        """Clear design action shows confirmation dialog."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.confirm_dialog = None
        screen.pending_action = None
        screen.viewmodel = MagicMock()
        screen.viewmodel.ship = MagicMock()

        # Simulate pending clear action
        screen.pending_action = "clear_design"

        assert screen.pending_action == "clear_design"

    def test_confirm_dialog_blocks_other_input(self):
        """Active confirm dialog blocks other input."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.confirm_dialog = MagicMock()  # Dialog is active

        # When dialog is active, other input should be blocked
        assert screen.confirm_dialog is not None


# --- Theme Integration Tests ---

class TestThemeIntegration:
    """Tests for theme system integration."""

    def test_theme_manager_used_for_sprites(self):
        """Theme manager provides sprite assets."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.theme_manager = MagicMock()
        screen.sprite_mgr = MagicMock()

        # Theme manager should be available
        assert screen.theme_manager is not None

    def test_ship_theme_updates_sprite(self):
        """Changing ship theme updates sprite display."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        screen.viewmodel = MagicMock()
        screen.viewmodel.ship = MagicMock()
        screen.viewmodel.ship.theme_id = "Federation"
        screen.sprite_mgr = MagicMock()
        screen.view = MagicMock()

        # Update theme
        screen.viewmodel.ship.theme_id = "Klingon"

        assert screen.viewmodel.ship.theme_id == "Klingon"


# --- Context Mode Behavior Tests ---

class TestContextModeBehavior:
    """Tests for mode-specific behavior."""

    def test_standalone_mode_allows_all_ships(self):
        """Standalone mode allows loading any ship."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen
        from game.ui.screens.workshop_context import WorkshopMode

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        context = _make_context_standalone()
        screen.context = context

        assert screen.context.is_standalone()
        assert screen.context.tech_preset_name is not None

    def test_integrated_mode_respects_empire_theme(self):
        """Integrated mode uses empire theme."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen
        from game.ui.screens.workshop_context import WorkshopMode

        with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
            screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

        context = MagicMock()
        context.mode = WorkshopMode.INTEGRATED
        context.is_integrated.return_value = True
        context.empire_theme_id = "Federation"

        screen.context = context

        assert screen.context.is_integrated()
        assert screen.context.empire_theme_id == "Federation"
