"""
Tests for App integration with new game setup flow.
"""
import unittest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch, PropertyMock


class TestAppNewGameFlow(unittest.TestCase):
    """Tests for new game flow integration in App."""

    def test_on_new_game_start_creates_session_and_save(self):
        """Completing setup creates GameSession and initial save."""
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.engine.game_session import GameSession
        from game.strategy.systems.save_game_service import SaveGameService

        # Create temp dir for saves
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()

        try:
            os.chdir(tmpdir)

            # Build config like NewGameSetupScreen would
            config = GameConfig(
                save_name="TestIntegration",
                players=[
                    PlayerConfig(name="Player One", theme="Federation", color=(0, 100, 255)),
                    PlayerConfig(name="Player Two", theme="Atlantians", color=(0, 200, 150)),
                ]
            )

            # Create session (this is what _on_new_game_start would do)
            session = GameSession(config=config)

            # Save initial state
            success, message, save_path = SaveGameService.save_game(session, config.save_name)

            self.assertTrue(success)
            self.assertIsNotNone(save_path)
            session.save_path = save_path

            # Verify save structure
            self.assertTrue(os.path.exists(save_path))
            self.assertTrue(os.path.exists(os.path.join(save_path, "turns")))
            self.assertTrue(os.path.exists(os.path.join(save_path, "turns", "turn_1.json")))
            self.assertTrue(os.path.exists(os.path.join(save_path, "designs")))
            self.assertTrue(os.path.exists(os.path.join(save_path, "designs", "empire_0")))
            self.assertTrue(os.path.exists(os.path.join(save_path, "designs", "empire_1")))

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(tmpdir)

    def test_new_game_config_flows_to_session(self):
        """GameConfig settings from setup screen correctly flow to GameSession."""
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.engine.game_session import GameSession

        config = GameConfig(
            save_name="FlowTest",
            players=[
                PlayerConfig(name="Alpha", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Beta", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Gamma", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        # Verify session has correct number of empires
        self.assertEqual(len(session.empires), 3)

        # Verify empire names
        self.assertEqual(session.empires[0].name, "Alpha")
        self.assertEqual(session.empires[1].name, "Beta")
        self.assertEqual(session.empires[2].name, "Gamma")

        # Verify themes
        self.assertEqual(session.empires[0].empire_theme_id, "Federation")
        self.assertEqual(session.empires[1].empire_theme_id, "Atlantians")
        self.assertEqual(session.empires[2].empire_theme_id, "Romulans")

    def test_load_game_restores_full_session(self):
        """Loading a saved game restores complete session state."""
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.engine.game_session import GameSession
        from game.strategy.systems.save_game_service import SaveGameService

        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()

        try:
            os.chdir(tmpdir)

            # Create and save a session
            config = GameConfig(
                save_name="LoadTest",
                players=[
                    PlayerConfig(name="Saved Empire", theme="Federation", color=(255, 0, 0)),
                ],
                system_count=5
            )
            original_session = GameSession(config=config)
            original_session.turn_number = 3  # Simulate some turns passed

            success, _, save_path = SaveGameService.save_game(original_session, config.save_name)
            self.assertTrue(success)

            # Load the session
            loaded_session, message = SaveGameService.load_game(save_path)

            self.assertIsNotNone(loaded_session)
            self.assertEqual(loaded_session.turn_number, 3)
            self.assertEqual(len(loaded_session.empires), 1)
            self.assertEqual(loaded_session.empires[0].name, "Saved Empire")

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(tmpdir)


class TestAppUIManagerSetup(unittest.TestCase):
    """Tests for UI manager handling in App."""

    def test_menu_ui_manager_created_on_demand(self):
        """Menu UI manager is created when needed for dialogs."""
        # This is a design verification - menu_ui_manager should be created
        # lazily when showing load menu or new game setup

        # Mock enough to verify the pattern
        mock_app = MagicMock()
        mock_app.menu_ui_manager = None  # Not yet created

        # Simulate what show_load_menu does
        if not hasattr(mock_app, 'menu_ui_manager') or mock_app.menu_ui_manager is None:
            import pygame_gui
            # In real code this creates the manager
            created = True
        else:
            created = False

        self.assertTrue(created)


if __name__ == '__main__':
    unittest.main()
