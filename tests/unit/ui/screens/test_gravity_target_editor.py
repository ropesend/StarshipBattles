"""PROJ-458 Phase 3 (F-C-017): GravityTargetEditor retrofit characterization."""
from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame

from game.ui.screens.gravity_target_editor import (
    DefaultGravityTargetEditorUiBuilder,
    GravityTargetEditor,
    GravityTargetEditorUiBuilder,
    G_TO_MS2,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _stub_planet(name: str = "P1", surface_gravity: float = 9.81) -> SimpleNamespace:
    return SimpleNamespace(id=1, name=name, surface_gravity=surface_gravity)


def _build_bypassed(
    *, ui_builder=None, on_apply_callback=None, on_close_callback=None,
    race_config=None, surface_gravity: float = 9.81,
) -> GravityTargetEditor:
    with bypass_init(GravityTargetEditor):
        return GravityTargetEditor(
            pygame.Rect(0, 0, 600, 400),
            MagicMock(name="ui_manager"),
            _stub_planet(surface_gravity=surface_gravity),
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
            on_apply_callback=cb_apply,
            on_close_callback=cb_close,
            surface_gravity=19.62,  # 2g
        )
        assert window.planet.name == "P1"
        assert window.on_apply_callback is cb_apply
        assert window.on_close_callback is cb_close
        assert window._species_dropdown is None
        assert window._default_race_id is None
        # Stage 1 should compute current_g from surface_gravity / G_TO_MS2
        assert window.current_g == 19.62 / G_TO_MS2
        assert window._window_init_bypassed is True

    def test_bypass_init_does_not_invoke_ui_builder(self) -> None:
        mock_builder = MagicMock(spec=GravityTargetEditorUiBuilder)
        window = _build_bypassed(ui_builder=mock_builder)
        assert window._ui_builder is mock_builder
        mock_builder.build.assert_not_called()

    def test_default_ui_builder_is_thin_wrapper_around_build_ui(self) -> None:
        window = _build_bypassed()
        window._build_ui = MagicMock(name="_build_ui")
        DefaultGravityTargetEditorUiBuilder().build(window)
        window._build_ui.assert_called_once()


class TestCharacterization:
    def test_constructor_signature_preserved(self) -> None:
        sig = inspect.signature(GravityTargetEditor.__init__)
        params = list(sig.parameters.values())
        assert params[0].name == "self"
        assert params[1].name == "rect"
        assert params[2].name == "manager"
        assert params[3].name == "planet"
        kw_only = {
            p.name: p for p in params if p.kind is inspect.Parameter.KEYWORD_ONLY
        }
        for kw in ("window_manager", "on_apply_callback", "on_close_callback", "race_config"):
            assert kw in kw_only

    def test_constructor_accepts_keyword_only_ui_builder(self) -> None:
        sig = inspect.signature(GravityTargetEditor.__init__)
        ui_builder = sig.parameters.get("ui_builder")
        assert ui_builder is not None
        assert ui_builder.kind is inspect.Parameter.KEYWORD_ONLY
        assert ui_builder.default is None
