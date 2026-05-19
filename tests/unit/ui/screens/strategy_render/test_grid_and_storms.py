from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

import pygame

from game.core.hex_math import HexCoord
from game.ui.colors import COLORS
from game.ui.screens.strategy_render.grid import GridLayer
from game.ui.screens.strategy_render.storms import draw_storms
from game.ui.screens.strategy_render.storms import draw_storms_low_detail


def _camera(*, zoom: float = 1.0) -> SimpleNamespace:
    return SimpleNamespace(
        zoom=zoom,
        width=800,
        height=600,
        offset_x=0,
        offset_y=0,
        position=pygame.math.Vector2(0, 0),
        screen_to_world=MagicMock(return_value=pygame.math.Vector2(0, 0)),
        world_to_screen=lambda pos: pygame.math.Vector2(pos.x, pos.y),
    )


def _renderer(*, zoom: float = 1.0) -> SimpleNamespace:
    return SimpleNamespace(
        camera=_camera(zoom=zoom),
        hex_size=10,
        screen_width=800,
        screen_height=600,
    )


def test_grid_culls_large_viewport_before_drawing() -> None:
    renderer = _renderer()
    screen = MagicMock()
    hexes = [
        SimpleNamespace(q=-200, r=-200),
        SimpleNamespace(q=200, r=-200),
        SimpleNamespace(q=-200, r=200),
        SimpleNamespace(q=200, r=200),
    ]

    with (
        patch("game.ui.screens.strategy_render.grid.pixel_to_hex", side_effect=hexes),
        patch("game.ui.screens.strategy_render.grid.pygame.draw.line") as draw_line,
        patch("game.ui.screens.strategy_render.grid.pygame.draw.lines") as draw_lines,
    ):
        GridLayer().draw(renderer, screen)

    draw_line.assert_not_called()
    draw_lines.assert_not_called()


def test_grid_draws_visible_snake_lines_and_top_edges() -> None:
    renderer = _renderer()
    screen = MagicMock()

    with (
        patch(
            "game.ui.screens.strategy_render.grid.pixel_to_hex",
            return_value=SimpleNamespace(q=0, r=0),
        ),
        patch("game.ui.screens.strategy_render.grid.pygame.draw.line") as draw_line,
        patch("game.ui.screens.strategy_render.grid.pygame.draw.lines") as draw_lines,
    ):
        GridLayer().draw(renderer, screen)

    assert draw_line.call_count > 0
    assert draw_lines.call_count > 0
    assert draw_line.call_args.args[1] == COLORS["border_subtle"]
    assert draw_lines.call_args.args[1] == COLORS["border_subtle"]


def test_storms_low_zoom_dispatches_low_detail_renderer() -> None:
    renderer = _renderer(zoom=0.2)
    system = SimpleNamespace(storms=[SimpleNamespace()])

    with patch("game.ui.screens.strategy_render.storms.draw_storms_low_detail") as low_detail:
        draw_storms(renderer, MagicMock(), system, pygame.math.Vector2(0, 0))

    low_detail.assert_called_once()


def test_storms_low_detail_skips_offscreen_hexes() -> None:
    renderer = _renderer(zoom=0.2)
    renderer.hex_size = 20
    renderer.screen_width = 100
    renderer.screen_height = 100
    storm = SimpleNamespace(
        storm_type="ion_storm",
        occupied_hexes=[HexCoord(0, 0), HexCoord(1, 0)],
    )
    system = SimpleNamespace(storms=[storm])

    with (
        patch(
            "game.ui.screens.strategy_render.storms.hex_to_pixel",
            side_effect=[(0, 0), (999, 0)],
        ),
        patch("game.ui.screens.strategy_render.storms.pygame.draw.circle") as draw_circle,
    ):
        draw_storms_low_detail(renderer, MagicMock(), system, pygame.math.Vector2(0, 0))

    draw_circle.assert_called_once()
    assert draw_circle.call_args.args[2] == (0, 0)
    assert draw_circle.call_args.args[3] == 2
