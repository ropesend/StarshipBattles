"""Tests for builder I/O integration.

PROJ-43: Updated to use mock _ship_io_adapter instead of patching ShipIO directly.
The workshop_screen now uses adapters for ship I/O operations.
"""
from unittest.mock import patch, MagicMock
from game.ui.screens import workshop_screen
from game.ui.screens.workshop_screen import DesignWorkshopGUI
from game.ui.screens.workshop_context import WorkshopMode


class TestBuilderIOIntegration:

    def _create_gui_mock_standalone(self):
        """Create a gui mock configured for standalone mode"""
        gui_mock = MagicMock()
        gui_mock.context = MagicMock()
        gui_mock.context.mode = WorkshopMode.STANDALONE
        # PROJ-43: Add mock adapter (now used instead of direct ShipIO)
        gui_mock._ship_io_adapter = MagicMock()
        return gui_mock

    def test_save_ship_success_flow(self):
        """Verify GUI flow when save is successful."""
        # Mock 'self' with standalone context
        gui_mock = self._create_gui_mock_standalone()
        gui_mock.ship = MagicMock()
        gui_mock._ship_io_adapter.save_ship.return_value = (True, "Saved successfully")

        # Call the method (we grab it from the class and bind it to our mock)
        DesignWorkshopGUI._save_ship(gui_mock)

        # Verify adapter save_ship called
        gui_mock._ship_io_adapter.save_ship.assert_called_once_with(gui_mock.ship)

        # Verify show_error NOT called (success prints to console in current impl,
        # or we could verify print via mock, but key is no error dialog)
        gui_mock.show_error.assert_not_called()

    def test_save_ship_failure_flow(self):
        """Verify GUI flow when save fails."""
        gui_mock = self._create_gui_mock_standalone()
        gui_mock.ship = MagicMock()
        gui_mock._ship_io_adapter.save_ship.return_value = (False, "Permission Denied")

        DesignWorkshopGUI._save_ship(gui_mock)

        # Verify error shown
        gui_mock.show_error.assert_called_once_with("Permission Denied")

    def test_load_ship_success_flow(self):
        """Verify GUI flow when load is successful."""
        mock_new_ship = MagicMock()

        gui_mock = self._create_gui_mock_standalone()
        # Mock dependent attributes accessed in _load_ship
        gui_mock.width = 1920
        gui_mock.height = 1080
        gui_mock._ship_io_adapter.load_ship.return_value = (mock_new_ship, "Loaded successfully")

        # Mock _apply_loaded_ship to verify it's called with the right ship
        gui_mock._apply_loaded_ship = MagicMock()

        DesignWorkshopGUI._load_ship(gui_mock)

        # Verify adapter load_ship called with correct dimensions
        gui_mock._ship_io_adapter.load_ship.assert_called_once_with(1920, 1080)

        # Verify _apply_loaded_ship was called with the loaded ship
        gui_mock._apply_loaded_ship.assert_called_once()
        call_args = gui_mock._apply_loaded_ship.call_args
        assert call_args[0][0] == mock_new_ship  # First arg is the ship
        assert call_args[0][1] == "Loaded successfully"  # Second arg is message

        # Verify no error
        gui_mock.show_error.assert_not_called()

    def test_load_ship_failure_flow(self):
        """Verify GUI flow when load fails."""
        gui_mock = self._create_gui_mock_standalone()
        gui_mock.width = 1920
        gui_mock.height = 1080
        gui_mock.right_panel = MagicMock()
        gui_mock._ship_io_adapter.load_ship.return_value = (None, "Corrupt File")

        DesignWorkshopGUI._load_ship(gui_mock)

        # Verify error shown
        gui_mock.show_error.assert_called_once_with("Corrupt File")

        # Verify ship NOT updated
        # Accessing gui_mock.ship would be a getattr on mock,
        # but we can check if we assigned anything.
        # Since 'ship' attribute wasn't even set on mock initially,
        # we can just ensure no assignment happened if we want,
        # but 'self.ship = new_ship' would set it.
        # Let's ensure 'right_panel.refresh_controls' etc not called of course
        gui_mock.right_panel.refresh_controls.assert_not_called()
