
import unittest
from unittest.mock import patch, MagicMock
from game.ui.screens import builder_screen
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.ui.screens.workshop_context import WorkshopMode

class TestBuilderIOIntegration(unittest.TestCase):

    def setUp(self):
        # We can't easily instantiate BuilderSceneGUI because of its heavy __init__
        # So we will patch the class methods we want to test onto a Mock object
        # or just invoke the method with a 'self' mock.
        pass

    def _create_gui_mock_standalone(self):
        """Create a gui mock configured for standalone mode"""
        gui_mock = MagicMock()
        gui_mock.context = MagicMock()
        gui_mock.context.mode = WorkshopMode.STANDALONE
        return gui_mock

    @patch('game.ui.screens.builder_screen.ShipIO.save_ship')
    def test_save_ship_success_flow(self, mock_save):
        """Verify GUI flow when save is successful."""
        mock_save.return_value = (True, "Saved successfully")

        # Mock 'self' with standalone context
        gui_mock = self._create_gui_mock_standalone()
        gui_mock.ship = MagicMock()

        # Call the method (we grab it from the class and bind it to our mock)
        BuilderSceneGUI._save_ship(gui_mock)

        # Verify ShipIO called
        mock_save.assert_called_once_with(gui_mock.ship)

        # Verify show_error NOT called (success prints to console in current impl,
        # or we could verify print via mock, but key is no error dialog)
        gui_mock.show_error.assert_not_called()

    @patch('game.ui.screens.builder_screen.ShipIO.save_ship')
    def test_save_ship_failure_flow(self, mock_save):
        """Verify GUI flow when save fails."""
        mock_save.return_value = (False, "Permission Denied")

        gui_mock = self._create_gui_mock_standalone()
        gui_mock.ship = MagicMock()

        BuilderSceneGUI._save_ship(gui_mock)

        # Verify error shown
        gui_mock.show_error.assert_called_once_with("Permission Denied")

    @patch('game.ui.screens.builder_screen.ShipIO.load_ship')
    def test_load_ship_success_flow(self, mock_load):
        """Verify GUI flow when load is successful."""
        mock_new_ship = MagicMock()
        mock_load.return_value = (mock_new_ship, "Loaded successfully")

        gui_mock = self._create_gui_mock_standalone()
        # Mock dependent attributes accessed in _load_ship
        gui_mock.width = 1920
        gui_mock.height = 1080

        # Mock _apply_loaded_ship to verify it's called with the right ship
        gui_mock._apply_loaded_ship = MagicMock()

        BuilderSceneGUI._load_ship(gui_mock)

        # Verify _apply_loaded_ship was called with the loaded ship
        gui_mock._apply_loaded_ship.assert_called_once()
        call_args = gui_mock._apply_loaded_ship.call_args
        self.assertEqual(call_args[0][0], mock_new_ship)  # First arg is the ship
        self.assertEqual(call_args[0][1], "Loaded successfully")  # Second arg is message

        # Verify no error
        gui_mock.show_error.assert_not_called()

    @patch('game.ui.screens.builder_screen.ShipIO.load_ship')
    def test_load_ship_failure_flow(self, mock_load):
        """Verify GUI flow when load fails."""
        mock_load.return_value = (None, "Corrupt File")

        gui_mock = self._create_gui_mock_standalone()
        gui_mock.width = 1920
        gui_mock.height = 1080
        gui_mock.right_panel = MagicMock()

        BuilderSceneGUI._load_ship(gui_mock)

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

if __name__ == '__main__':
    unittest.main()
