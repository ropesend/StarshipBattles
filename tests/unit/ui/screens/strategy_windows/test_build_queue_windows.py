from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.ui.screens.strategy_windows import build_queue_windows


def _composer() -> SimpleNamespace:
    scene = SimpleNamespace(
        current_empire=MagicMock(name="empire"),
        galaxy=MagicMock(name="galaxy"),
        on_navigate_to_hex_build=MagicMock(name="on_navigate_to_hex_build"),
        session=SimpleNamespace(
            registries=MagicMock(name="registries"),
            empires=[MagicMock(name="empire_1")],
        ),
        facade=MagicMock(name="facade"),
    )
    return SimpleNamespace(
        width=1000,
        height=800,
        manager=MagicMock(name="ui_manager"),
        _mapper=MagicMock(name="input_mapper"),
        scene=scene,
        build_queue_list_window=None,
        empire_build_queue_window=None,
    )


def test_build_queue_list_open_creates_centered_window() -> None:
    composer = _composer()
    registrar = build_queue_windows.BuildQueueListRegistrar(composer)

    with patch.object(build_queue_windows, "BuildQueueListWindow") as window_cls:
        registrar.open()

    rect = window_cls.call_args.args[0]
    assert rect.topleft == (150, 150)
    assert rect.size == (700, 500)
    assert window_cls.call_args.args[1] is composer.manager
    assert window_cls.call_args.args[2] is composer.scene.current_empire
    assert window_cls.call_args.kwargs["window_manager"] is composer
    assert window_cls.call_args.kwargs["on_close_callback"] == registrar._on_closed
    assert window_cls.call_args.kwargs["input_mapper"] is composer._mapper
    assert composer.build_queue_list_window is window_cls.return_value


def test_build_queue_list_open_kills_existing_window() -> None:
    composer = _composer()
    existing = MagicMock(name="existing_window")
    composer.build_queue_list_window = existing
    registrar = build_queue_windows.BuildQueueListRegistrar(composer)

    with patch.object(build_queue_windows, "BuildQueueListWindow"):
        registrar.open()

    existing.kill.assert_called_once()


def test_build_queue_list_on_closed_clears_slot() -> None:
    composer = _composer()
    composer.build_queue_list_window = MagicMock(name="window")

    build_queue_windows.BuildQueueListRegistrar(composer)._on_closed()

    assert composer.build_queue_list_window is None


def test_empire_build_queue_open_wires_scene_dependencies() -> None:
    composer = _composer()
    registrar = build_queue_windows.EmpireBuildQueueRegistrar(composer)

    with patch.object(build_queue_windows, "EmpireBuildQueueWindow") as window_cls:
        registrar.open()

    rect = window_cls.call_args.args[0]
    assert rect.topleft == (50, 40)
    assert rect.size == (900, 720)
    assert window_cls.call_args.args[1] is composer.manager
    assert window_cls.call_args.args[2] is composer.scene.current_empire
    assert window_cls.call_args.args[3] is composer.scene.galaxy
    assert window_cls.call_args.kwargs["window_manager"] is composer
    assert window_cls.call_args.kwargs["on_close_callback"] == registrar._on_closed
    assert (
        window_cls.call_args.kwargs["on_navigate_to_hex"]
        is composer.scene.on_navigate_to_hex_build
    )
    # PROJ-382 Phase 1: session= kwarg removed; facade is the sole DI handle.
    assert "session" not in window_cls.call_args.kwargs
    assert window_cls.call_args.kwargs["facade"] is composer.scene.facade
    assert composer.empire_build_queue_window is window_cls.return_value


def test_empire_build_queue_open_kills_existing_window() -> None:
    composer = _composer()
    existing = MagicMock(name="existing_window")
    composer.empire_build_queue_window = existing
    registrar = build_queue_windows.EmpireBuildQueueRegistrar(composer)

    with patch.object(build_queue_windows, "EmpireBuildQueueWindow"):
        registrar.open()

    existing.kill.assert_called_once()


def test_empire_build_queue_close_kills_and_clears_slot() -> None:
    composer = _composer()
    existing = MagicMock(name="existing_window")
    composer.empire_build_queue_window = existing
    registrar = build_queue_windows.EmpireBuildQueueRegistrar(composer)

    registrar.close()

    existing.kill.assert_called_once()
    assert composer.empire_build_queue_window is None


def test_empire_build_queue_on_closed_clears_slot() -> None:
    composer = _composer()
    composer.empire_build_queue_window = MagicMock(name="window")

    build_queue_windows.EmpireBuildQueueRegistrar(composer)._on_closed()

    assert composer.empire_build_queue_window is None
