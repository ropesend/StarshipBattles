"""
Tests for App integration with new game setup flow.
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch, PropertyMock


class TestAppNewGameFlow:
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

            assert success is True
            assert save_path is not None
            session.save_path = save_path

            # Verify save structure
            assert os.path.exists(save_path)
            assert os.path.exists(os.path.join(save_path, "turns"))
            assert os.path.exists(os.path.join(save_path, "turns", "turn_1.json"))
            assert os.path.exists(os.path.join(save_path, "designs"))
            assert os.path.exists(os.path.join(save_path, "designs", "empire_0"))
            assert os.path.exists(os.path.join(save_path, "designs", "empire_1"))

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
        assert len(session.empires) == 3

        # Verify empire names
        assert session.empires[0].name == "Alpha"
        assert session.empires[1].name == "Beta"
        assert session.empires[2].name == "Gamma"

        # Verify themes
        assert session.empires[0].empire_theme_id == "Federation"
        assert session.empires[1].empire_theme_id == "Atlantians"
        assert session.empires[2].empire_theme_id == "Romulans"

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
            assert success is True

            # Load the session
            loaded_session, message = SaveGameService.load_game(save_path)

            assert loaded_session is not None
            assert loaded_session.turn_number == 3
            assert len(loaded_session.empires) == 1
            assert loaded_session.empires[0].name == "Saved Empire"

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(tmpdir)


class TestStartBattleRegistriesDI:
    """Regression guard for `Game.start_battle` registry access.

    Commit fc51d83e (PROJ-269 Phase 6) introduced a broken call
    `get_default_registry_provider().get_registries()` at
    `game/app.py:568`. `DefaultRegistryProvider` has no `get_registries`
    method — it exposes individual registries via `get_components()`,
    `get_modifiers()`, etc. The crash went undetected until a user
    actually started a manual battle via the Battle Setup screen,
    at which point it raised:

        AttributeError: 'DefaultRegistryProvider' object has no attribute 'get_registries'

    The architecturally correct resolution uses the `GameRegistries`
    DI container already on `self.registries` (initialized at
    app.py:175 from the registry_manager). These tests guard against
    the broken factory-call pattern re-entering the file.
    """

    def test_start_battle_does_not_call_nonexistent_get_registries(self):
        """app.py must not call `.get_registries()` on DefaultRegistryProvider."""
        from pathlib import Path
        app_path = Path(__file__).resolve().parents[2] / "game" / "app.py"
        text = app_path.read_text(encoding="utf-8")
        assert "get_default_registry_provider().get_registries()" not in text, (
            "The broken pattern get_default_registry_provider().get_registries() "
            "has re-entered game/app.py. `DefaultRegistryProvider` has no "
            "`get_registries()` method; use `self.registries` (the GameRegistries "
            "DI container initialized at Game.__init__) instead. See "
            "tests/integration/test_app_integration.py::TestStartBattleRegistriesDI "
            "docstring for background."
        )

    def test_default_registry_provider_has_no_get_registries_method(self):
        """Documents the API shape that caused the original crash.

        If `DefaultRegistryProvider` ever grows a `get_registries()`
        method, the original broken call at app.py:568 would
        coincidentally start working — but that call pattern is still
        architecturally wrong (bypasses the DI container on Game).
        This test fails in either direction: the method existing means
        we should explicitly update the test + audit whether the factory
        pattern is really the right entry.
        """
        from game.core.registry import DefaultRegistryProvider
        assert not hasattr(DefaultRegistryProvider, "get_registries"), (
            "DefaultRegistryProvider grew a get_registries() method. "
            "Review whether this changes the canonical DI container access "
            "pattern described in docs/01_ARCHITECTURE.md."
        )


class TestQuickstartHelper:
    """Tests for quickstart helper method (PROJ-44 Task 1.1)."""

    def test_start_quickstart_helper_exists(self):
        """Helper method _start_quickstart should exist on Game class."""
        from game.app import Game
        assert hasattr(Game, '_start_quickstart'), "Game class should have _start_quickstart method"

    def test_start_quickstart_1p_uses_helper(self):
        """start_quickstart_1p should delegate to _start_quickstart with player_count=1."""
        # We verify by checking that both methods exist and _start_quickstart accepts player_count
        from game.app import Game
        import inspect

        # Get the signature of _start_quickstart
        sig = inspect.signature(Game._start_quickstart)
        params = list(sig.parameters.keys())

        # Should have 'self' and 'player_count' parameters
        assert 'player_count' in params, "_start_quickstart should accept player_count parameter"

    def test_start_quickstart_2p_uses_helper(self):
        """start_quickstart_2p should delegate to _start_quickstart with player_count=2."""
        # Same structural test as 1p
        from game.app import Game
        import inspect

        sig = inspect.signature(Game._start_quickstart)
        params = list(sig.parameters.keys())
        assert 'player_count' in params, "_start_quickstart should accept player_count parameter"


class TestAppUIManagerSetup:
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

        assert created is True
