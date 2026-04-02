"""Tests for IScene protocol compliance (PROJ-65).

Verifies that all scene classes properly implement the IScene protocol.
"""
from game.core.protocols import IScene

# Required methods from IScene protocol
_ISCENE_METHODS = ('handle_event', 'update', 'draw', 'handle_resize')


def _assert_implements_iscene(cls):
    """Assert that a class structurally implements IScene (no instantiation needed)."""
    for method_name in _ISCENE_METHODS:
        assert hasattr(cls, method_name), (
            f"{cls.__name__} missing IScene method: {method_name}"
        )
        member = getattr(cls, method_name)
        assert callable(member), (
            f"{cls.__name__}.{method_name} is not callable"
        )
    # Also verify issubclass for runtime_checkable protocol
    assert issubclass(cls, IScene), (
        f"{cls.__name__} should be a structural subtype of IScene"
    )


class TestISceneProtocolCompliance:
    """Tests that all scene classes implement IScene protocol.

    These are purely structural checks (hasattr/issubclass) that do NOT
    require instantiating screen objects, avoiding expensive __init__ calls.
    """

    def test_menu_scene_implements_iscene(self):
        """MenuScene implements IScene protocol."""
        from game.ui.screens.menu_scene import MenuScene
        _assert_implements_iscene(MenuScene)

    def test_battle_screen_implements_iscene(self):
        """BattleScreen implements IScene protocol."""
        from game.ui.screens.battle_screen import BattleScreen
        _assert_implements_iscene(BattleScreen)

    def test_battle_setup_screen_implements_iscene(self):
        """BattleSetupScreen implements IScene protocol."""
        from game.ui.screens.setup_screen import BattleSetupScreen
        _assert_implements_iscene(BattleSetupScreen)

    def test_workshop_screen_implements_iscene(self):
        """DesignWorkshopScreen implements IScene protocol."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen
        _assert_implements_iscene(DesignWorkshopScreen)

    def test_strategy_screen_implements_iscene(self):
        """StrategyScreen implements IScene protocol."""
        from game.ui.screens.strategy_screen import StrategyScreen
        _assert_implements_iscene(StrategyScreen)

    def test_test_lab_screen_implements_iscene(self):
        """TestLabScreen implements IScene protocol."""
        from game.ui.screens.test_lab import TestLabScreen
        _assert_implements_iscene(TestLabScreen)

    def test_research_tree_scene_implements_iscene(self):
        """ResearchTreeScene implements IScene protocol."""
        from game.ui.research.research_scene import ResearchTreeScene
        _assert_implements_iscene(ResearchTreeScene)

    def test_galaxy_test_screen_implements_iscene(self):
        """GalaxyTestScreen implements IScene protocol."""
        from game.ui.screens.galaxy_test import GalaxyTestScreen
        _assert_implements_iscene(GalaxyTestScreen)

    def test_formation_editor_screen_implements_iscene(self):
        """FormationEditorScreen implements IScene protocol."""
        from game.ui.screens.formation_editor import FormationEditorScreen
        _assert_implements_iscene(FormationEditorScreen)


class TestSceneCallback:
    """Tests for scene_callback pattern.

    These tests require actual instances since they call methods.
    pygame lifecycle is handled by the autouse pygame_display_reset fixture.
    """

    def test_battle_screen_callback_dispatches_return_to_setup(self):
        """BattleScreen scene_callback dispatches 'return_to_setup' action."""
        callback_received = []

        def callback(action, **kwargs):
            callback_received.append((action, kwargs))

        from game.ui.screens.battle_screen import BattleScreen
        scene = BattleScreen(800, 600, callback)

        scene._trigger_return_to_setup()

        assert len(callback_received) == 1
        assert callback_received[0][0] == "return_to_setup"

    def test_battle_screen_callback_dispatches_return_to_test_lab(self):
        """BattleScreen scene_callback dispatches 'return_to_test_lab' action."""
        callback_received = []

        def callback(action, **kwargs):
            callback_received.append((action, kwargs))

        from game.ui.screens.battle_screen import BattleScreen
        scene = BattleScreen(800, 600, callback)

        scene._trigger_return_to_test_lab()

        assert len(callback_received) == 1
        assert callback_received[0][0] == "return_to_test_lab"
