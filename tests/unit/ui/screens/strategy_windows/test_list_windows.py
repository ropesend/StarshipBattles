from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.ui.screens.strategy_windows import list_windows


def _composer() -> SimpleNamespace:
    scene = SimpleNamespace(
        current_empire=MagicMock(name="empire"),
        galaxy=MagicMock(name="galaxy"),
        session=SimpleNamespace(
            empires=[MagicMock(name="empire_1")],
            registries=MagicMock(name="registries"),
        ),
        facade=SimpleNamespace(
            economy=SimpleNamespace(race_registry=MagicMock(return_value=None)),
        ),
        _camera_nav=MagicMock(name="camera_nav"),
    )
    return SimpleNamespace(
        width=1000,
        height=800,
        manager=MagicMock(name="ui_manager"),
        _asset_resolver=MagicMock(name="asset_resolver"),
        scene=scene,
        planet_list_window=None,
        star_list_window=None,
    )


def test_navigate_camera_to_centers_scene_camera() -> None:
    scene = SimpleNamespace(_camera_nav=MagicMock(name="camera_nav"))
    target = MagicMock(name="hex")

    list_windows.navigate_camera_to(scene, target)

    scene._camera_nav.center_on_hex.assert_called_once_with(target)


def test_navigate_camera_to_tolerates_scene_without_camera_nav() -> None:
    scene = SimpleNamespace()

    list_windows.navigate_camera_to(scene, MagicMock(name="hex"))


def test_star_list_open_creates_centered_window() -> None:
    composer = _composer()
    registrar = list_windows.StarListRegistrar(composer)

    with patch.object(list_windows, "StarListWindow") as window_cls:
        registrar.open()

    rect = window_cls.call_args.args[0]
    assert rect.topleft == (50, 40)
    assert rect.size == (900, 720)
    assert window_cls.call_args.args[1] is composer.manager
    assert window_cls.call_args.args[2] is composer.scene.galaxy
    assert window_cls.call_args.kwargs["window_manager"] is composer
    assert window_cls.call_args.kwargs["on_close_callback"] == registrar._on_closed
    assert window_cls.call_args.kwargs["on_navigate_callback"] == registrar._on_navigate
    assert composer.star_list_window is window_cls.return_value


def test_star_list_open_reuses_alive_existing_window() -> None:
    """PROJ-411 Task 2.2: reuse path — call ``open_for_galaxy`` instead of kill+construct."""
    composer = _composer()
    existing = MagicMock(name="existing_window")
    existing.alive.return_value = True
    composer.star_list_window = existing
    registrar = list_windows.StarListRegistrar(composer)

    with patch.object(list_windows, "StarListWindow") as window_cls:
        registrar.open()

    existing.kill.assert_not_called()
    window_cls.assert_not_called()
    existing.open_for_galaxy.assert_called_once_with(
        composer.scene.galaxy, composer.scene.current_empire
    )


def test_star_list_open_constructs_fresh_when_slot_empty() -> None:
    """PROJ-411 Task 2.2: empty slot still goes down the construction path."""
    composer = _composer()
    composer.star_list_window = None
    registrar = list_windows.StarListRegistrar(composer)

    with patch.object(list_windows, "StarListWindow") as window_cls:
        registrar.open()

    window_cls.assert_called_once()


def test_star_list_on_closed_clears_slot() -> None:
    composer = _composer()
    composer.star_list_window = MagicMock(name="window")

    list_windows.StarListRegistrar(composer)._on_closed()

    assert composer.star_list_window is None


def test_star_list_navigate_kills_window_and_centers_camera() -> None:
    composer = _composer()
    existing = MagicMock(name="star_window")
    target = MagicMock(name="hex")
    composer.star_list_window = existing

    list_windows.StarListRegistrar(composer)._on_navigate(target)

    existing.kill.assert_called_once()
    composer.scene._camera_nav.center_on_hex.assert_called_once_with(target)


def test_planet_list_open_threads_detail_dependencies() -> None:
    composer = _composer()
    race_registry = MagicMock(name="race_registry")
    composer.scene.facade.economy.race_registry.return_value = race_registry
    registrar = list_windows.PlanetListRegistrar(composer)

    with patch.object(list_windows, "PlanetListWindow") as window_cls:
        registrar.open()

    assert window_cls.call_args.args[2] is composer.scene.galaxy
    assert window_cls.call_args.args[3] is composer.scene.current_empire
    assert window_cls.call_args.kwargs["asset_resolver"] is composer._asset_resolver
    assert window_cls.call_args.kwargs["empires"] is composer.scene.session.empires
    assert window_cls.call_args.kwargs["registries"] is composer.scene.session.registries
    assert window_cls.call_args.kwargs["race_registry"] is race_registry
    assert window_cls.call_args.kwargs["facade"] is composer.scene.facade
    assert window_cls.call_args.kwargs["on_navigate_callback"] == registrar._on_navigate
    assert composer.planet_list_window is window_cls.return_value


def test_planet_list_navigate_kills_window_and_centers_camera() -> None:
    composer = _composer()
    existing = MagicMock(name="planet_window")
    target = MagicMock(name="hex")
    composer.planet_list_window = existing

    list_windows.PlanetListRegistrar(composer)._on_navigate(target)

    existing.kill.assert_called_once()
    composer.scene._camera_nav.center_on_hex.assert_called_once_with(target)
