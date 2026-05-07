"""Unit coverage for `game.screen_router` scene wiring and flags."""
from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.core.constants import GameState


class FakeScene:
    """Small scene double with the methods ScreenRouter calls."""

    def __init__(self, label: str, *args: Any, **kwargs: Any) -> None:
        self.label = label
        self.args = args
        self.kwargs = kwargs
        self.screen_width = args[0] if args else 1600
        self.screen_height = args[1] if len(args) > 1 else 900
        self.cleanup = MagicMock(name=f"{label}.cleanup")
        self.handle_resize = MagicMock(name=f"{label}.handle_resize")
        self.start = MagicMock(name=f"{label}.start")
        self.start_battle = MagicMock(name=f"{label}.start_battle")
        self.update_input = MagicMock(name=f"{label}.update_input")
        self._ui = SimpleNamespace(_apply_tooltips=MagicMock())

    def handle_event(self, event: Any) -> None:
        self.last_event = event

    def update(self, dt: float) -> None:
        self.last_dt = dt

    def draw(self, screen: Any) -> None:
        self.last_screen = screen


class SceneFactory:
    def __init__(self, label: str) -> None:
        self.label = label
        self.calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.instances: list[FakeScene] = []

    def __call__(self, *args: Any, **kwargs: Any) -> FakeScene:
        scene = FakeScene(self.label, *args, **kwargs)
        self.calls.append((args, kwargs))
        self.instances.append(scene)
        return scene


class MenuSceneFactory(SceneFactory):
    def __call__(self, *args: Any, **kwargs: Any) -> FakeScene:
        scene = super().__call__(*args, **kwargs)
        scene.ui_manager = MagicMock(name="menu_ui_manager")
        scene.get_ui_manager = MagicMock(return_value=scene.ui_manager)
        return scene


class FakeStateMachine:
    def __init__(self, initial_state: GameState = GameState.MENU) -> None:
        self.state = initial_state
        self.transitions: list[tuple[GameState, GameState]] = []
        self.pushes: list[tuple[GameState, GameState]] = []
        self.stack: list[GameState] = []

    def transition(self, to_state: GameState) -> None:
        self.transitions.append((self.state, to_state))
        self.state = to_state

    def push_and_transition(self, to_state: GameState) -> None:
        self.pushes.append((self.state, to_state))
        self.stack.append(self.state)
        self.transition(to_state)

    def pop_and_return(self) -> GameState:
        return_state = self.stack.pop() if self.stack else GameState.MENU
        self.transition(return_state)
        return return_state


@pytest.fixture
def router_harness(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    from game import screen_router as router_mod

    factories = {
        "MenuScene": MenuSceneFactory("menu"),
        "DesignWorkshopScreen": SceneFactory("builder"),
        "BattleSetupScreen": SceneFactory("battle_setup"),
        "BattleScreen": SceneFactory("battle"),
        "StrategyScreen": SceneFactory("strategy"),
        "TestLabScreen": SceneFactory("test_lab"),
        "GalaxyTestScreen": SceneFactory("galaxy_test"),
        "NewGameSetupScreen": SceneFactory("new_game_setup"),
    }
    for attr, factory in factories.items():
        monkeypatch.setattr(router_mod, attr, factory)

    class FakeWorkshopContext:
        standalone_calls: list[dict[str, Any]] = []

        @classmethod
        def standalone(cls, **kwargs: Any) -> SimpleNamespace:
            cls.standalone_calls.append(kwargs)
            return SimpleNamespace(on_return=None, kwargs=kwargs)

    monkeypatch.setattr(router_mod, "WorkshopContext", FakeWorkshopContext)

    boot = SimpleNamespace(
        width=1600,
        height=900,
        registries=MagicMock(name="registries"),
        input_mapper=MagicMock(name="input_mapper"),
    )
    callbacks = router_mod.SceneCallbacks(
        battle_setup=MagicMock(name="battle_setup_callback"),
        battle=MagicMock(name="battle_callback"),
        strategy=MagicMock(name="strategy_callback"),
        test_lab=MagicMock(name="test_lab_callback"),
    )
    state_machine = FakeStateMachine()
    shutdown = MagicMock(name="request_shutdown")

    router = router_mod.ScreenRouter(
        boot=boot,
        state_machine=state_machine,
        request_shutdown=shutdown,
        menu_button_config=[("Start", MagicMock(name="start"))],
        scene_callbacks=callbacks,
    )

    return SimpleNamespace(
        mod=router_mod,
        router=router,
        factories=factories,
        context_factory=FakeWorkshopContext,
        boot=boot,
        callbacks=callbacks,
        state_machine=state_machine,
        shutdown=shutdown,
    )


def test_constructor_registers_scenes_and_delegates_callbacks(
    router_harness: SimpleNamespace,
) -> None:
    router = router_harness.router
    factories = router_harness.factories
    callbacks = router_harness.callbacks
    boot = router_harness.boot

    menu_scene = factories["MenuScene"].instances[0]
    builder_scene = factories["DesignWorkshopScreen"].instances[0]
    battle_setup = factories["BattleSetupScreen"].instances[0]
    battle_scene = factories["BattleScreen"].instances[0]
    strategy_scene = factories["StrategyScreen"].instances[0]
    test_lab_scene = factories["TestLabScreen"].instances[0]

    assert router.active_scene is menu_scene
    assert router.menu_ui_manager is menu_scene.ui_manager
    assert router.width == 1600
    assert router.height == 900
    assert router.registries is boot.registries
    assert router.input_mapper is boot.input_mapper
    assert router._request_shutdown is router_harness.shutdown

    assert router_harness.context_factory.standalone_calls == [
        {"tech_preset_name": "default", "registries": boot.registries}
    ]
    context = builder_scene.args[2]
    assert context.on_return.__self__ is router
    assert context.on_return.__func__ is router_harness.mod.ScreenRouter.on_builder_return

    assert battle_setup.args == (1600, 900, callbacks.battle_setup)
    assert battle_scene.args == (1600, 900, callbacks.battle)
    assert strategy_scene.args == (1600, 900)
    assert strategy_scene.kwargs == {
        "scene_callback": callbacks.strategy,
        "input_mapper": boot.input_mapper,
    }
    assert test_lab_scene.args == (1600, 900)
    assert test_lab_scene.kwargs == {
        "battle_scene": battle_scene,
        "scene_callback": callbacks.test_lab,
    }

    assert router.show_exit_dialog is False
    assert router.showing_load_menu is False
    assert router.showing_race_setup is False
    assert router.showing_new_game_setup is False
    assert router.race_setup_window is None
    assert router.new_game_setup_window is None
    assert router.save_selection_window is None


def test_start_battle_setup_starts_scene_and_switches_state(
    router_harness: SimpleNamespace,
) -> None:
    router = router_harness.router

    router.start_battle_setup(preserve_teams=True)

    router.battle_setup.start.assert_called_once_with(preserve_teams=True)
    assert router_harness.state_machine.transitions[-1] == (
        GameState.MENU,
        GameState.BATTLE_SETUP,
    )
    assert router.active_scene is router.battle_setup
    assert router.return_state == GameState.BATTLE_SETUP


def test_builder_lifecycle_uses_state_stack_cleanup_and_strategy_resize(
    router_harness: SimpleNamespace,
) -> None:
    router = router_harness.router
    state_machine = router_harness.state_machine
    state_machine.state = GameState.STRATEGY
    context = SimpleNamespace(on_return=None)

    router.start_builder(context=context)
    builder_scene = router_harness.factories["DesignWorkshopScreen"].instances[-1]

    assert context.on_return.__self__ is router
    assert builder_scene.args == (1600, 900, context)
    assert state_machine.pushes[-1] == (GameState.STRATEGY, GameState.BUILDER)
    assert router.active_scene is builder_scene

    router.on_builder_return()

    builder_scene.cleanup.assert_called_once_with()
    router.strategy_scene.handle_resize.assert_called_once_with(1600, 900)
    assert state_machine.transitions[-1] == (GameState.BUILDER, GameState.STRATEGY)
    assert router.active_scene is router.strategy_scene


def test_dialog_and_load_menu_flags_use_menu_manager_callbacks(
    monkeypatch: pytest.MonkeyPatch,
    router_harness: SimpleNamespace,
) -> None:
    router = router_harness.router
    rects: list[tuple[int, int, int, int]] = []

    def fake_centered_rect(w: int, h: int, sw: int, sh: int) -> tuple[int, int, int, int]:
        rect = (w, h, sw, sh)
        rects.append(rect)
        return rect

    monkeypatch.setattr(router_harness.mod, "create_centered_rect", fake_centered_rect)

    router.start_strategy_layer()
    new_game_window = router_harness.factories["NewGameSetupScreen"].instances[-1]
    assert rects[-1] == (650, 600, 1600, 900)
    assert new_game_window.args == ((650, 600, 1600, 900), router.menu_ui_manager)
    assert new_game_window.kwargs["on_start_callback"].__self__ is router
    assert new_game_window.kwargs["on_cancel_callback"].__self__ is router
    assert router.new_game_setup_window is new_game_window
    assert router.showing_new_game_setup is True

    router._on_new_game_cancel()
    assert router.showing_new_game_setup is False

    save_factory = SceneFactory("save_selection")
    monkeypatch.setitem(
        sys.modules,
        "game.ui.screens.save_selection_window",
        SimpleNamespace(SaveSelectionWindow=save_factory),
    )

    router.show_load_menu()
    save_window = save_factory.instances[-1]
    assert rects[-1] == (600, 500, 1600, 900)
    assert save_window.args == ((600, 500, 1600, 900), router.menu_ui_manager)
    assert save_window.kwargs["on_load_callback"].__self__ is router
    assert save_window.kwargs["on_cancel_callback"].__self__ is router
    assert router.save_selection_window is save_window
    assert router.showing_load_menu is True

    router._on_load_cancel()
    assert router.showing_load_menu is False

    race_factory = SceneFactory("race_setup")
    monkeypatch.setitem(
        sys.modules,
        "game.ui.screens.race_setup_screen",
        SimpleNamespace(RaceSetupScreen=race_factory),
    )

    router.start_race_setup()
    race_window = race_factory.instances[-1]
    assert rects[-1] == (1800, 1200, 1600, 900)
    assert race_window.args == ((1800, 1200, 1600, 900), router.menu_ui_manager)
    assert race_window.kwargs["on_complete_callback"].__self__ is router
    assert race_window.kwargs["on_cancel_callback"].__self__ is router
    assert router.race_setup_window is race_window
    assert router.showing_race_setup is True

    router._on_race_setup_cancel()
    assert router.showing_race_setup is False
    assert router.race_setup_window is None


def test_load_game_success_replaces_strategy_scene_and_clears_load_flag(
    monkeypatch: pytest.MonkeyPatch,
    router_harness: SimpleNamespace,
) -> None:
    router = router_harness.router
    router.showing_load_menu = True
    loaded_session = object()

    class FakeAIControllerFactory:
        instances: list["FakeAIControllerFactory"] = []

        def __init__(self) -> None:
            self.instances.append(self)

    class FakeSaveGameService:
        calls: list[dict[str, Any]] = []

        @classmethod
        def load_game(
            cls,
            save_path: Any,
            *,
            turn_number: Any = None,
            ai_factory: Any = None,
        ) -> tuple[Any, str]:
            cls.calls.append(
                {
                    "save_path": save_path,
                    "turn_number": turn_number,
                    "ai_factory": ai_factory,
                }
            )
            return loaded_session, "loaded"

    monkeypatch.setitem(
        sys.modules,
        "game.ai.ai_factory",
        SimpleNamespace(AIControllerFactory=FakeAIControllerFactory),
    )
    monkeypatch.setitem(
        sys.modules,
        "game.strategy.systems.save_game_service",
        SimpleNamespace(SaveGameService=FakeSaveGameService),
    )

    router._on_load_game("save/path", turn_number=7)

    assert FakeSaveGameService.calls == [
        {
            "save_path": "save/path",
            "turn_number": 7,
            "ai_factory": FakeAIControllerFactory.instances[0],
        }
    ]
    strategy_scene = router_harness.factories["StrategyScreen"].instances[-1]
    assert strategy_scene.kwargs == {
        "session": loaded_session,
        "scene_callback": router_harness.callbacks.strategy,
        "input_mapper": router_harness.boot.input_mapper,
    }
    assert router.strategy_scene is strategy_scene
    assert router.showing_load_menu is False
    assert router_harness.state_machine.transitions[-1] == (
        GameState.MENU,
        GameState.STRATEGY,
    )
    assert router.active_scene is strategy_scene


def test_start_battle_delegates_to_controller_and_battle_scene(
    monkeypatch: pytest.MonkeyPatch,
    router_harness: SimpleNamespace,
) -> None:
    router = router_harness.router
    router.battle_scene.screen_width = 800
    router.battle_scene.screen_height = 600
    spec = SimpleNamespace(seed=123, end_condition=object(), absolute_max_ticks=456)
    registry_provider = object()

    class FakeAIControllerFactory:
        instances: list["FakeAIControllerFactory"] = []

        def __init__(self) -> None:
            self.instances.append(self)

    class FakeBattleConfig:
        def __init__(
            self,
            *,
            headless: bool,
            seed: int,
            end_condition: Any,
            absolute_max_ticks: int,
        ) -> None:
            self.headless = headless
            self.seed = seed
            self.end_condition = end_condition
            self.absolute_max_ticks = absolute_max_ticks

    class FakeBattleController:
        instances: list["FakeBattleController"] = []

        def __init__(self) -> None:
            self.start_from_spec = MagicMock(name="start_from_spec")
            self.instances.append(self)

    monkeypatch.setattr(
        router_harness.mod,
        "get_default_registry_provider",
        lambda: registry_provider,
    )
    monkeypatch.setitem(
        sys.modules,
        "game.ai.ai_factory",
        SimpleNamespace(AIControllerFactory=FakeAIControllerFactory),
    )
    monkeypatch.setitem(
        sys.modules,
        "game.simulation.battle_config",
        SimpleNamespace(BattleConfig=FakeBattleConfig),
    )
    monkeypatch.setitem(
        sys.modules,
        "game.simulation.battle_controller",
        SimpleNamespace(BattleController=FakeBattleController),
    )

    router.start_battle(spec, headless=True)

    controller = FakeBattleController.instances[0]
    router.battle_scene.handle_resize.assert_called_once_with(1600, 900)
    controller.start_from_spec.assert_called_once()
    call_kwargs = controller.start_from_spec.call_args.kwargs
    config = call_kwargs["config"]
    assert controller.start_from_spec.call_args.args == (spec,)
    assert call_kwargs["ai_factory"] is FakeAIControllerFactory.instances[0]
    assert call_kwargs["registry_provider"] is registry_provider
    assert config.headless is True
    assert config.seed == spec.seed
    assert config.end_condition is spec.end_condition
    assert config.absolute_max_ticks == spec.absolute_max_ticks
    router.battle_scene.start_battle.assert_called_once_with(controller)
    assert router_harness.state_machine.transitions[-1] == (
        GameState.MENU,
        GameState.BATTLE,
    )
    assert router.active_scene is router.battle_scene
