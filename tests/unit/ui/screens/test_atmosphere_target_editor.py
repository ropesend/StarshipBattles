"""PROJ-458 Phase 2 (F-C-017): AtmosphereTargetEditor retrofit characterization.

Locks the post-retrofit two-stage ``UIWindow`` bypass-init shape on
:class:`game.ui.screens.atmosphere_target_editor.AtmosphereTargetEditor`.
"""
from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.atmosphere_target_editor import (
    AtmosphereTargetEditor,
    AtmosphereTargetEditorUiBuilder,
    DefaultAtmosphereTargetEditorUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _stub_planet(name: str = "P1") -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        name=name,
        atmosphere={"N2": 78000.0, "O2": 21000.0},
        atmosphere_target={},
    )


def _build_bypassed(
    *, ui_builder=None, on_apply_callback=None, on_close_callback=None,
    race_config=None,
) -> AtmosphereTargetEditor:
    with bypass_init(AtmosphereTargetEditor):
        return AtmosphereTargetEditor(
            pygame.Rect(0, 0, 800, 600),
            MagicMock(name="ui_manager"),
            _stub_planet(),
            window_manager=MagicMock(name="window_manager"),
            on_apply_callback=on_apply_callback,
            on_close_callback=on_close_callback,
            race_config=race_config,
            ui_builder=ui_builder,
        )


class TestConstruction:
    def test_bypass_init_yields_instance_with_stage_one_state(self) -> None:
        cb_apply = MagicMock(name="on_apply")
        cb_close = MagicMock(name="on_close")
        window = _build_bypassed(
            on_apply_callback=cb_apply, on_close_callback=cb_close,
        )
        assert window.planet.name == "P1"
        assert window.on_apply_callback is cb_apply
        assert window.on_close_callback is cb_close
        assert window._species_dropdown is None
        assert window._default_race_id is None
        # Stage 1 should populate the gas/slider dicts (empty pre-build)
        # and the gases list (computed from planet state).
        assert isinstance(window.sliders, dict)
        assert window.sliders == {}
        assert isinstance(window.value_labels, dict)
        assert window.value_labels == {}
        assert isinstance(window.current_labels, dict)
        assert window.current_labels == {}
        assert "N2" in window.gases
        assert "O2" in window.gases
        assert window._window_init_bypassed is True

    def test_bypass_init_does_not_invoke_ui_builder(self) -> None:
        mock_builder = MagicMock(spec=AtmosphereTargetEditorUiBuilder)
        window = _build_bypassed(ui_builder=mock_builder)
        assert window._ui_builder is mock_builder
        mock_builder.build.assert_not_called()

    def test_default_ui_builder_is_thin_wrapper_around_build_ui(self) -> None:
        """``DefaultAtmosphereTargetEditorUiBuilder`` calls
        ``window._build_ui()`` exactly once. Test under bypass so we
        avoid running the real widget tree; the assertion is on the
        builder-to-method bridge, not on the widget construction.
        """
        window = _build_bypassed()
        window._build_ui = MagicMock(name="_build_ui")
        DefaultAtmosphereTargetEditorUiBuilder().build(window)
        window._build_ui.assert_called_once()


class TestCharacterization:
    def test_constructor_signature_preserved(self) -> None:
        """Pre-retrofit positional/keyword-able signature unchanged."""
        sig = inspect.signature(AtmosphereTargetEditor.__init__)
        params = list(sig.parameters.values())
        assert params[0].name == "self"
        assert params[1].name == "rect"
        assert params[2].name == "manager"
        assert params[3].name == "planet"
        # window_manager / on_apply_callback / on_close_callback / race_config
        # are kw-only with defaults.
        kw_only = {
            p.name: p for p in params if p.kind is inspect.Parameter.KEYWORD_ONLY
        }
        assert "window_manager" in kw_only
        assert "on_apply_callback" in kw_only
        assert kw_only["on_apply_callback"].default is None
        assert "on_close_callback" in kw_only
        assert kw_only["on_close_callback"].default is None
        assert "race_config" in kw_only
        assert kw_only["race_config"].default is None

    def test_constructor_accepts_keyword_only_ui_builder(self) -> None:
        sig = inspect.signature(AtmosphereTargetEditor.__init__)
        ui_builder = sig.parameters.get("ui_builder")
        assert ui_builder is not None
        assert ui_builder.kind is inspect.Parameter.KEYWORD_ONLY
        assert ui_builder.default is None
