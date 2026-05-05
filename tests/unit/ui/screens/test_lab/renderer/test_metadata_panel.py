from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.test_lab import theme
from game.ui.screens.test_lab.renderer.metadata_panel import MetadataPanel


def _font() -> MagicMock:
    font = MagicMock(name="font")
    font.render.return_value = pygame.Surface((12, 8), pygame.SRCALPHA)
    return font


def _make_panel() -> MetadataPanel:
    return MetadataPanel(
        header_font=_font(),
        body_font=_font(),
        small_font=_font(),
        header_color=(1, 2, 3),
        text_color=(4, 5, 6),
        panel_bg=(7, 8, 9),
        border_color=(10, 11, 12),
        category_width=200,
        test_list_width=300,
        metadata_width=500,
        header_height=100,
        validation_panel=MagicMock(name="validation_panel"),
    )


def _draw_colors(panel: MetadataPanel, *, mouse_pos, is_comparison: bool):
    screen = MagicMock(name="screen")
    registry = MagicMock(name="registry")
    registry.get_by_id.return_value = {"is_comparison": is_comparison}
    viewmodel = SimpleViewModel()

    with (
        patch("pygame.mouse.get_pos", return_value=mouse_pos),
        patch("pygame.draw.rect") as draw_rect,
    ):
        panel._draw_run_buttons(
            screen,
            x=100,
            y=50,
            selected_test_id="scenario-a",
            registry=registry,
            viewmodel=viewmodel,
        )

    return [call.args[1] for call in draw_rect.call_args_list], viewmodel


class SimpleViewModel:
    run_test_btn_rect: pygame.Rect | None = None
    run_headless_btn_rect: pygame.Rect | None = None
    run_baseline_btn_rect: pygame.Rect | None = None


def test_visual_run_hover_uses_hover_color_and_sets_button_rects() -> None:
    panel = _make_panel()

    colors, viewmodel = _draw_colors(
        panel,
        mouse_pos=(381, 43),
        is_comparison=True,
    )

    assert colors[0] == theme.BUTTON_RUN_HOVER
    assert colors[2] == theme.BUTTON_HEADLESS_BG
    assert colors[4] == theme.BUTTON_BASELINE_BG
    assert viewmodel.run_test_btn_rect == pygame.Rect(380, 42, 90, 26)
    assert viewmodel.run_headless_btn_rect == pygame.Rect(480, 42, 100, 26)
    assert viewmodel.run_baseline_btn_rect == pygame.Rect(380, 72, 120, 26)


def test_headless_run_hover_uses_headless_hover_color() -> None:
    panel = _make_panel()

    colors, _viewmodel = _draw_colors(
        panel,
        mouse_pos=(481, 43),
        is_comparison=True,
    )

    assert colors[0] == theme.BUTTON_RUN_BG
    assert colors[2] == theme.BUTTON_HEADLESS_HOVER
    assert colors[4] == theme.BUTTON_BASELINE_BG


def test_visual_baseline_hover_uses_baseline_hover_color() -> None:
    panel = _make_panel()

    colors, _viewmodel = _draw_colors(
        panel,
        mouse_pos=(381, 73),
        is_comparison=True,
    )

    assert colors[0] == theme.BUTTON_RUN_BG
    assert colors[2] == theme.BUTTON_HEADLESS_BG
    assert colors[4] == theme.BUTTON_BASELINE_HOVER


def test_non_comparison_scenario_clears_baseline_button_rect() -> None:
    panel = _make_panel()

    colors, viewmodel = _draw_colors(
        panel,
        mouse_pos=(381, 73),
        is_comparison=False,
    )

    assert colors == [
        theme.BUTTON_RUN_BG,
        theme.BUTTON_RUN_BORDER,
        theme.BUTTON_HEADLESS_BG,
        theme.BUTTON_HEADLESS_BORDER,
    ]
    assert viewmodel.run_baseline_btn_rect is None
