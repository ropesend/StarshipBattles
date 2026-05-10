"""Lifecycle tests for PlanetAbilitiesWindow + PlanetAbilitiesRegistrar (BUG-121).

The Planet Abilities Window must clear its slot on
``StrategyWindowManager.planet_abilities_window`` when killed, otherwise
``StrategyEventRouter.has_modal_open()`` returns ``True`` forever and the
strategy mouse-wheel zoom dies for the rest of the session.

Mirrors the lifecycle contract of ``PlanetListWindow`` /
``PlanetListRegistrar`` (the registered ``on_close_callback`` pattern).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _make_window(on_close_callback=None):
    """Construct a PlanetAbilitiesWindow without booting pygame_gui.

    Mirrors the ``__new__`` + ``__init__``-patch technique used in
    ``test_empire_build_queue_window.py`` so we can exercise the kill()
    contract without a live display.
    """
    from game.ui.screens.planet_abilities_window import PlanetAbilitiesWindow

    with patch.object(PlanetAbilitiesWindow, "__init__",
                      lambda self, *a, **kw: None):
        win = PlanetAbilitiesWindow.__new__(PlanetAbilitiesWindow)

    win._on_close_callback = on_close_callback
    return win


class TestPlanetAbilitiesWindowKill:
    """PlanetAbilitiesWindow.kill() must invoke on_close_callback."""

    def test_kill_invokes_close_callback(self) -> None:
        callback = MagicMock()
        win = _make_window(on_close_callback=callback)

        with patch("pygame_gui.elements.UIWindow.kill"):
            win.kill()

        callback.assert_called_once()

    def test_kill_without_callback_does_not_raise(self) -> None:
        win = _make_window(on_close_callback=None)

        with patch("pygame_gui.elements.UIWindow.kill"):
            win.kill()  # Must not raise.

    def test_kill_invokes_super_kill(self) -> None:
        """Subclass kill() must still chain to UIWindow.kill() for cleanup."""
        win = _make_window(on_close_callback=MagicMock())

        with patch("pygame_gui.elements.UIWindow.kill") as super_kill:
            win.kill()

        super_kill.assert_called_once()


class TestPlanetAbilitiesRegistrarLifecycle:
    """PlanetAbilitiesRegistrar must clear the composer slot on close."""

    @pytest.fixture
    def composer(self):
        """A minimal composer stand-in with the slot the registrar mutates."""
        c = MagicMock()
        c.planet_abilities_window = None
        c.width = 2560
        c.height = 1600
        c.scene = MagicMock()
        c.scene.facade = MagicMock()
        c.manager = MagicMock()
        return c

    def test_open_then_close_callback_clears_slot(self, composer) -> None:
        """When the abilities window is killed, the slot returns to None.

        Regression test for BUG-121. The registrar must register an
        ``on_close_callback`` that resets ``composer.planet_abilities_window``
        when the window is killed.
        """
        from game.ui.screens.strategy_windows.planet_abilities_ctrl import (
            PlanetAbilitiesRegistrar,
        )

        registrar = PlanetAbilitiesRegistrar(composer)

        # PlanetAbilitiesWindow is imported locally inside `open()`, so we
        # patch the source module the local import resolves to.
        with patch(
            "game.ui.screens.planet_abilities_window.PlanetAbilitiesWindow"
        ) as window_cls:
            window_cls.return_value = MagicMock()
            # Also stub registry-provider lookup so it doesn't reach for the
            # real component registry.
            with patch(
                "game.core.registry.get_default_registry_provider"
            ) as get_provider:
                get_provider.return_value = MagicMock()
                registrar.open(planet=MagicMock())

        assert window_cls.called, "Registrar must construct PlanetAbilitiesWindow"
        kwargs = window_cls.call_args.kwargs
        assert "on_close_callback" in kwargs, (
            "PlanetAbilitiesRegistrar must register an on_close_callback "
            "so the slot can clear when the window is killed (BUG-121)."
        )

        # Simulate the window invoking its close callback (as kill() will).
        composer.planet_abilities_window = MagicMock()
        kwargs["on_close_callback"]()
        assert composer.planet_abilities_window is None, (
            "on_close_callback must reset composer.planet_abilities_window "
            "to None (BUG-121)."
        )
