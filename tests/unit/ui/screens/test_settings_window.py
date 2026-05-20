"""PROJ-458 Phase 1 (F-C-017): SettingsWindow retrofit characterization.

Locks the post-retrofit behavioural contract of
:class:`game.ui.screens.settings_window.SettingsWindow` after the
Pattern #33 two-stage ``UIWindow`` bypass-init shape lands. Pinned
contracts:

- Stage 1 (above the bypass guard) initialises ``on_close_callback``,
  ``_settings``, ``_ui_builder`` — no widgets, no
  ``self.get_container()``, no asset I/O.
- The bypass guard returns early when ``type(self).bypass_init`` is
  truthy; the bypassed instance still has ``ui_manager``, ``rect`` and
  ``_window_init_bypassed=True`` populated for subsequent test
  inspection.
- Stage 2 (below the guard) calls ``super().__init__(...)`` and
  delegates widget construction to ``self._ui_builder.build(self)``.
- The public positional/keyword-able signature
  ``(rect, manager, on_close_callback=None)`` is preserved; the
  retrofit ADDS a kw-only ``ui_builder`` parameter.
- The brightness-slider live-preview / Reset / Close behaviours
  observable through ``process_event`` and ``update`` are unchanged.
"""
from __future__ import annotations

import inspect
from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.settings_window import (
    DefaultSettingsWindowUiBuilder,
    SettingsWindow,
    SettingsWindowUiBuilder,
)
from game.ui.services.game_settings import GameSettings
from tests.fixtures.ui_widget_factory import bypass_init


def _build_bypassed_window(
    *, ui_builder=None, on_close_callback=None
) -> SettingsWindow:
    """Construct a bypass-init :class:`SettingsWindow` for state-only
    introspection."""
    with bypass_init(SettingsWindow):
        return SettingsWindow(
            pygame.Rect(0, 0, 600, 400),
            MagicMock(name="ui_manager"),
            on_close_callback=on_close_callback,
            ui_builder=ui_builder,
        )


class TestConstruction:
    def test_bypass_init_yields_instance_without_widgets(self) -> None:
        """Under ``bypass_init``, the Stage-2 widget tree is skipped:
        ``_settings`` is populated but the widget handles are not."""
        window = _build_bypassed_window()
        assert isinstance(window._settings, GameSettings)
        assert window._window_init_bypassed is True
        # Widget handles are not constructed under bypass.
        assert not hasattr(window, "_brightness_slider")
        assert not hasattr(window, "_brightness_label")
        assert not hasattr(window, "_btn_reset")
        assert not hasattr(window, "_btn_close")

    def test_bypass_init_invokes_no_ui_builder_widget_construction(self) -> None:
        """Under ``bypass_init``, the ``ui_builder`` is stored on the
        instance but ``build(...)`` is NOT called. This is the
        Pattern #33 contract: Stage 2 (which runs the builder) is the
        branch that the guard skips.
        """
        mock_builder = MagicMock(spec=SettingsWindowUiBuilder)
        window = _build_bypassed_window(ui_builder=mock_builder)
        assert window._ui_builder is mock_builder
        mock_builder.build.assert_not_called()

    def test_production_init_invokes_ui_builder(self) -> None:
        """Production path (no ``bypass_init``) drives the injected
        ``ui_builder.build(window)`` exactly once. We assert via a
        mock builder; the real ``DefaultSettingsWindowUiBuilder`` is
        tested separately."""
        mock_builder = MagicMock(spec=SettingsWindowUiBuilder)
        with pytest.MonkeyPatch.context() as mp:
            # Patch UIWindow.__init__ to a no-op so we don't need a real
            # pygame display for the Stage-2 super() call.
            from pygame_gui.elements import UIWindow as _UIWindow
            mp.setattr(_UIWindow, "__init__", lambda self, *a, **kw: None)
            SettingsWindow(
                pygame.Rect(0, 0, 600, 400),
                MagicMock(name="ui_manager"),
                ui_builder=mock_builder,
            )
        mock_builder.build.assert_called_once()
        built_window = mock_builder.build.call_args.args[0]
        assert isinstance(built_window, SettingsWindow)
        assert built_window._window_init_bypassed is False


class TestBrightnessSlider:
    def test_slider_initial_value_matches_settings_via_default_builder(
        self, monkeypatch
    ) -> None:
        """``DefaultSettingsWindowUiBuilder`` constructs the slider with
        ``start_value=settings.background_brightness``.

        Uses a duck-typed fake ``window`` (SimpleNamespace) because the
        real ``SettingsWindow.rect`` setter routes through pygame_gui's
        ``UIWindow`` machinery (``blit_data[1] = ...``), which requires
        a fully-constructed pygame_gui sprite — out of reach under
        ``bypass_init``. The builder only reads ``window.rect``,
        ``window.ui_manager``, ``window._settings`` and writes the
        widget-handle slots, so a stub is sufficient.
        """
        from types import SimpleNamespace

        captured = {}

        def _capture_slider(**kwargs):
            captured["start_value"] = kwargs.get("start_value")
            return MagicMock(name="slider")

        def _capture_misc(**kwargs):
            return MagicMock(name="widget")

        import game.ui.screens.settings_window as sw_module
        monkeypatch.setattr(sw_module, "UIHorizontalSlider", _capture_slider)
        monkeypatch.setattr(sw_module, "UILabel", _capture_misc)
        monkeypatch.setattr(sw_module, "UIButton", _capture_misc)

        fake_window = SimpleNamespace(
            rect=pygame.Rect(0, 0, 600, 400),
            ui_manager=MagicMock(name="ui_manager"),
            _settings=GameSettings(),
        )
        DefaultSettingsWindowUiBuilder().build(fake_window)

        assert captured["start_value"] == fake_window._settings.background_brightness

    def test_slider_update_writes_to_settings(self) -> None:
        """``update(dt)`` syncs the slider's current value into
        ``_settings.background_brightness`` and refreshes the label."""
        window = _build_bypassed_window()
        # Stub the widgets the update() method touches.
        slider = MagicMock(name="slider")
        slider.has_moved_recently = True
        slider.get_current_value.return_value = 0.42
        window._brightness_slider = slider
        window._brightness_label = MagicMock(name="label")
        # Stub the UIWindow.update super-call so it doesn't need a real shell.
        with pytest.MonkeyPatch.context() as mp:
            from pygame_gui.elements import UIWindow as _UIWindow
            mp.setattr(_UIWindow, "update", lambda self, dt: None)
            window.update(0.016)

        assert window._settings.background_brightness == pytest.approx(0.42)
        window._brightness_label.set_text.assert_called_once_with("42%")


class TestResetButton:
    def test_reset_button_resets_settings_to_defaults(self) -> None:
        """UI_BUTTON_PRESSED with ``ui_element == _btn_reset`` calls
        ``_settings.reset_to_defaults()`` and refreshes slider + label."""
        window = _build_bypassed_window()
        window._settings = MagicMock(name="settings")
        window._settings.background_brightness = 0.30
        window._brightness_slider = MagicMock(name="slider")
        window._brightness_label = MagicMock(name="label")
        window._btn_close = object()
        window._btn_reset = object()

        from pygame_gui import UI_BUTTON_PRESSED
        event = MagicMock()
        event.type = UI_BUTTON_PRESSED
        event.ui_element = window._btn_reset

        with pytest.MonkeyPatch.context() as mp:
            from pygame_gui.elements import UIWindow as _UIWindow
            mp.setattr(_UIWindow, "process_event", lambda self, e: False)
            # SettingsWindow.process_event guards with
            # `event.type == pygame.event.custom_type()`. custom_type()
            # draws from the same pygame user-event pool as
            # UI_BUTTON_PRESSED and its live counter can collide with it
            # under heavy parallel sharding — pin it to a sentinel that
            # can never equal a real event type so the guard is
            # deterministic.
            mp.setattr(pygame.event, "custom_type", lambda: -1)
            handled = window.process_event(event)

        assert handled is True
        window._settings.reset_to_defaults.assert_called_once()
        window._brightness_slider.set_current_value.assert_called_once_with(0.30)
        window._brightness_label.set_text.assert_called_once_with("30%")


class TestCloseButton:
    def test_close_button_invokes_on_close_callback(self) -> None:
        cb = MagicMock(name="on_close_callback")
        window = _build_bypassed_window(on_close_callback=cb)
        window._btn_close = object()
        window._btn_reset = object()

        from pygame_gui import UI_BUTTON_PRESSED
        event = MagicMock()
        event.type = UI_BUTTON_PRESSED
        event.ui_element = window._btn_close

        with pytest.MonkeyPatch.context() as mp:
            from pygame_gui.elements import UIWindow as _UIWindow
            mp.setattr(_UIWindow, "process_event", lambda self, e: False)
            mp.setattr(_UIWindow, "kill", lambda self: None)
            # See test_reset_button_resets_settings_to_defaults: pin
            # custom_type() so the process_event guard is deterministic
            # under parallel sharding.
            mp.setattr(pygame.event, "custom_type", lambda: -1)
            handled = window.process_event(event)

        assert handled is True
        cb.assert_called_once()

    def test_kill_without_callback_does_not_raise(self) -> None:
        window = _build_bypassed_window(on_close_callback=None)
        with pytest.MonkeyPatch.context() as mp:
            from pygame_gui.elements import UIWindow as _UIWindow
            mp.setattr(_UIWindow, "kill", lambda self: None)
            window.kill()


class TestCharacterization:
    def test_constructor_positional_signature_preserved(self) -> None:
        """The pre-retrofit positional/keyword-able signature
        ``(rect, manager, on_close_callback=None)`` is unchanged."""
        sig = inspect.signature(SettingsWindow.__init__)
        params = list(sig.parameters.values())
        # 0: self, 1: rect, 2: manager, 3: on_close_callback, 4: ui_builder (kw-only)
        assert params[0].name == "self"
        assert params[1].name == "rect"
        assert params[2].name == "manager"
        assert params[3].name == "on_close_callback"
        assert params[3].default is None
        # Positional/keyword-able portion of the signature is unchanged.
        for p in params[1:4]:
            assert p.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
            )

    def test_constructor_accepts_keyword_only_ui_builder(self) -> None:
        """Pattern #33 retrofit ADDS a kw-only ``ui_builder`` parameter
        defaulting to ``None``."""
        sig = inspect.signature(SettingsWindow.__init__)
        ui_builder = sig.parameters.get("ui_builder")
        assert ui_builder is not None
        assert ui_builder.kind is inspect.Parameter.KEYWORD_ONLY
        assert ui_builder.default is None
