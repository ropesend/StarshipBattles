"""Tests for IScene protocol compliance (PROJ-65).

Verifies that all scene classes properly implement the IScene protocol.
"""
import pytest
from unittest.mock import MagicMock, patch
import pygame


class TestISceneProtocolCompliance:
    """Tests that all scene classes implement IScene protocol."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up pygame for testing."""
        pygame.init()
        # Create a minimal display for tests that need it
        if not pygame.display.get_surface():
            pygame.display.set_mode((800, 600), pygame.NOFRAME)
        yield
        pygame.quit()

    def test_menu_scene_implements_iscene(self):
        """MenuScene implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.menu_scene import MenuScene

        # MenuScene should be an instance of IScene
        scene = MenuScene(800, 600, [])
        assert isinstance(scene, IScene), "MenuScene should implement IScene"

        # Verify all required methods exist
        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_battle_screen_implements_iscene(self):
        """BattleScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.battle_screen import BattleScreen

        scene = BattleScreen(800, 600, lambda action, **kw: None)
        assert isinstance(scene, IScene), "BattleScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_battle_setup_screen_implements_iscene(self):
        """BattleSetupScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.setup_screen import BattleSetupScreen

        scene = BattleSetupScreen(800, 600, lambda action, **kw: None)
        assert isinstance(scene, IScene), "BattleSetupScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_workshop_screen_implements_iscene(self):
        """DesignWorkshopScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.workshop_screen import DesignWorkshopScreen
        from game.ui.screens.workshop_context import WorkshopContext

        context = WorkshopContext.standalone(tech_preset_name="default")
        context.on_return = lambda x=None: None
        scene = DesignWorkshopScreen(800, 600, context)
        assert isinstance(scene, IScene), "DesignWorkshopScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_strategy_screen_implements_iscene(self):
        """StrategyScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.strategy_screen import StrategyScreen
        from game.ui.services.input_mapper import InputMapper

        input_mapper = InputMapper()
        scene = StrategyScreen(800, 600, scene_callback=lambda action, **kw: None, input_mapper=input_mapper)
        assert isinstance(scene, IScene), "StrategyScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_test_lab_screen_implements_iscene(self):
        """TestLabScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.test_lab import TestLabScreen

        mock_game = MagicMock()
        mock_game.width = 800
        mock_game.height = 600
        mock_game.font_med = MagicMock()
        scene = TestLabScreen(mock_game, scene_callback=lambda action, **kw: None)
        assert isinstance(scene, IScene), "TestLabScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_research_tree_scene_implements_iscene(self):
        """ResearchTreeScene implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.research.research_scene import ResearchTreeScene

        scene = ResearchTreeScene(800, 600, on_close_callback=lambda: None)
        assert isinstance(scene, IScene), "ResearchTreeScene should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_galaxy_test_screen_implements_iscene(self):
        """GalaxyTestScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from game.ui.screens.galaxy_test import GalaxyTestScreen

        scene = GalaxyTestScreen(800, 600, on_close_callback=lambda: None)
        assert isinstance(scene, IScene), "GalaxyTestScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')

    def test_formation_editor_screen_implements_iscene(self):
        """FormationEditorScreen implements IScene protocol."""
        from game.core.protocols import IScene
        from Tools.formation_editor import FormationEditorScreen

        scene = FormationEditorScreen(800, 600, on_return_menu=lambda: None)
        assert isinstance(scene, IScene), "FormationEditorScreen should implement IScene"

        assert hasattr(scene, 'handle_event')
        assert hasattr(scene, 'update')
        assert hasattr(scene, 'draw')
        assert hasattr(scene, 'handle_resize')


class TestSceneCallback:
    """Tests for scene_callback pattern."""

    def test_battle_screen_callback_dispatches_return_to_setup(self):
        """BattleScreen scene_callback dispatches 'return_to_setup' action."""
        callback_received = []

        def callback(action, **kwargs):
            callback_received.append((action, kwargs))

        pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((800, 600), pygame.NOFRAME)

        from game.ui.screens.battle_screen import BattleScreen
        scene = BattleScreen(800, 600, callback)

        # Trigger the callback
        scene._trigger_return_to_setup()

        assert len(callback_received) == 1
        assert callback_received[0][0] == "return_to_setup"

        pygame.quit()

    def test_battle_screen_callback_dispatches_return_to_test_lab(self):
        """BattleScreen scene_callback dispatches 'return_to_test_lab' action."""
        callback_received = []

        def callback(action, **kwargs):
            callback_received.append((action, kwargs))

        pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((800, 600), pygame.NOFRAME)

        from game.ui.screens.battle_screen import BattleScreen
        scene = BattleScreen(800, 600, callback)

        # Trigger the callback
        scene._trigger_return_to_test_lab()

        assert len(callback_received) == 1
        assert callback_received[0][0] == "return_to_test_lab"

        pygame.quit()
