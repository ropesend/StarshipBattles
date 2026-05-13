from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.ui.screens.strategy_windows import empire_panel_ctrl


def _composer(*, facade: object | None = None) -> SimpleNamespace:
    scene = SimpleNamespace(
        current_empire=MagicMock(name="empire"),
        session=SimpleNamespace(registries=MagicMock(name="registries")),
        facade=facade,
    )
    return SimpleNamespace(
        width=1000,
        height=800,
        manager=MagicMock(name="ui_manager"),
        scene=scene,
        empire_panel_window=None,
        settings_window=None,
    )


def test_empire_panel_open_passes_registries_and_race_registry() -> None:
    race_registry = MagicMock(name="race_registry")
    facade = SimpleNamespace(get_race_registry=MagicMock(return_value=race_registry))
    composer = _composer(facade=facade)
    registrar = empire_panel_ctrl.EmpirePanelRegistrar(composer)

    with patch.object(empire_panel_ctrl, "EmpirePanelWindow") as window_cls:
        registrar.open()

    rect = window_cls.call_args.args[0]
    assert rect.topleft == (50, 40)
    assert rect.size == (900, 720)
    assert window_cls.call_args.args[1] is composer.manager
    assert window_cls.call_args.args[2] is composer.scene.current_empire
    assert window_cls.call_args.kwargs["window_manager"] is composer
    assert window_cls.call_args.kwargs["on_close_callback"] == registrar._on_closed
    assert window_cls.call_args.kwargs["registries"] is composer.scene.session.registries
    assert window_cls.call_args.kwargs["race_registry"] is race_registry
    assert composer.empire_panel_window is window_cls.return_value


def test_empire_panel_open_reuses_existing_alive_window() -> None:
    """Issue #28: existing alive window is reused via ``open_for_empire``
    (cross-empire rebuild path lives on the window). Kill+reconstruct
    is no longer the registrar's behaviour."""
    composer = _composer()
    existing = MagicMock(name="existing_window")
    existing.alive.return_value = True
    composer.empire_panel_window = existing
    registrar = empire_panel_ctrl.EmpirePanelRegistrar(composer)

    with patch.object(empire_panel_ctrl, "EmpirePanelWindow") as window_cls:
        registrar.open()

    existing.open_for_empire.assert_called_once_with(composer.scene.current_empire)
    window_cls.assert_not_called()
    existing.kill.assert_not_called()


def test_empire_panel_open_constructs_when_dead() -> None:
    """A dead existing window is replaced with a fresh construction."""
    composer = _composer()
    dead = MagicMock(name="dead_window")
    dead.alive.return_value = False
    composer.empire_panel_window = dead
    registrar = empire_panel_ctrl.EmpirePanelRegistrar(composer)

    with patch.object(empire_panel_ctrl, "EmpirePanelWindow") as window_cls:
        registrar.open()

    window_cls.assert_called_once()
    dead.open_for_empire.assert_not_called()


def test_empire_panel_open_without_race_registry_uses_none() -> None:
    composer = _composer(facade=object())
    registrar = empire_panel_ctrl.EmpirePanelRegistrar(composer)

    with patch.object(empire_panel_ctrl, "EmpirePanelWindow") as window_cls:
        registrar.open()

    assert window_cls.call_args.kwargs["race_registry"] is None


def test_empire_panel_on_closed_clears_slot() -> None:
    composer = _composer()
    composer.empire_panel_window = MagicMock(name="window")

    empire_panel_ctrl.EmpirePanelRegistrar(composer)._on_closed()

    assert composer.empire_panel_window is None


def test_settings_open_creates_centered_window() -> None:
    composer = _composer()
    registrar = empire_panel_ctrl.SettingsRegistrar(composer)

    with patch("game.ui.screens.settings_window.SettingsWindow") as window_cls:
        registrar.open()

    rect = window_cls.call_args.args[0]
    assert rect.topleft == (250, 300)
    assert rect.size == (500, 200)
    assert window_cls.call_args.args[1] is composer.manager
    assert window_cls.call_args.kwargs["on_close_callback"] == registrar._on_closed
    assert composer.settings_window is window_cls.return_value


def test_settings_open_kills_existing_window() -> None:
    composer = _composer()
    existing = MagicMock(name="existing_window")
    composer.settings_window = existing
    registrar = empire_panel_ctrl.SettingsRegistrar(composer)

    with patch("game.ui.screens.settings_window.SettingsWindow"):
        registrar.open()

    existing.kill.assert_called_once()


def test_settings_on_closed_clears_slot() -> None:
    composer = _composer()
    composer.settings_window = MagicMock(name="settings_window")

    empire_panel_ctrl.SettingsRegistrar(composer)._on_closed()

    assert composer.settings_window is None
