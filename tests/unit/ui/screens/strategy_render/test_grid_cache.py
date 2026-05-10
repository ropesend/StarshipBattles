"""Cache tests for the strategy-screen hex-grid layer (PROJ-374).

The grid layer caches its rendered surface keyed by quantized camera
state. These tests verify:

- Cache hit on idle camera (single render across repeated draws).
- Cache miss when each individual key input changes beyond tolerance.
- Sub-quantum jitter does NOT invalidate the cache.
- Surface is allocated once and reused across misses.
- Viewport resize re-allocates the surface.
- Zoom < 0.4 short-circuits before any cache work.
- The cache surface is created with SRCALPHA.
- Blit target is the screen passed into ``draw``.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.strategy_render.grid import GridLayer


def _make_renderer(
    *,
    zoom: float = 1.0,
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    screen_width: int = 800,
    screen_height: int = 600,
    hex_size: int = 10,
) -> SimpleNamespace:
    """Build a minimal renderer stub matching ``StrategyRenderer`` surface.

    NOTE on camera-dimension fidelity (PROJ-374 review MIN-1): production
    ``StrategyScreen`` constructs ``Camera`` with ``width = screen_width -
    SIDEBAR_WIDTH``, ``height = screen_height - TOP_BAR_HEIGHT``, and
    ``offset_y = TOP_BAR_HEIGHT``. This stub uses full-screen dimensions and
    zero offsets because every cache test mocks ``_render_grid_to_surface``
    — the cache key does not read ``camera.width/height/offset_*``, so the
    stub's divergence from production is insulated. If a future test
    exercises the un-mocked render path, parameterise these values to match
    production.
    """
    camera = SimpleNamespace(
        zoom=zoom,
        width=screen_width,
        height=screen_height,
        offset_x=0,
        offset_y=0,
        position=pygame.math.Vector2(pos_x, pos_y),
        screen_to_world=MagicMock(return_value=pygame.math.Vector2(0, 0)),
        world_to_screen=lambda v: pygame.math.Vector2(v.x, v.y),
    )
    return SimpleNamespace(
        camera=camera,
        hex_size=hex_size,
        screen_width=screen_width,
        screen_height=screen_height,
    )


def _patch_inner_draw():
    """Patch the per-column drawing primitives so tests don't need a display.

    Returns the context manager to be used in a ``with`` block.
    """
    return patch.multiple(
        "game.ui.screens.strategy_render.grid",
        pixel_to_hex=MagicMock(return_value=SimpleNamespace(q=0, r=0)),
    )


class TestGridCacheKey:
    """Verify the cache key reflects every input that affects the bitmap."""

    def test_idle_camera_produces_single_render(self) -> None:
        renderer = _make_renderer()
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            layer.draw(renderer, screen)
            layer.draw(renderer, screen)

        assert render.call_count == 1, (
            "Idle camera must produce exactly one underlying render across "
            "multiple draws."
        )
        # screen.blit called every frame (3x).
        assert screen.blit.call_count == 3

    def test_position_x_change_beyond_tolerance_invalidates(self) -> None:
        renderer = _make_renderer(pos_x=0.0)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.camera.position = pygame.math.Vector2(0.2, 0.0)
            layer.draw(renderer, screen)

        assert render.call_count == 2

    def test_position_x_change_within_tolerance_hits(self) -> None:
        renderer = _make_renderer(pos_x=0.0)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            # Sub-quantum jitter (< 0.05 stays in the 0.0 bucket).
            renderer.camera.position = pygame.math.Vector2(0.04, 0.0)
            layer.draw(renderer, screen)

        assert render.call_count == 1

    def test_position_y_change_beyond_tolerance_invalidates(self) -> None:
        renderer = _make_renderer(pos_y=0.0)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.camera.position = pygame.math.Vector2(0.0, 0.2)
            layer.draw(renderer, screen)

        assert render.call_count == 2

    def test_zoom_change_beyond_tolerance_invalidates(self) -> None:
        renderer = _make_renderer(zoom=1.0)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.camera.zoom = 1.02
            layer.draw(renderer, screen)

        assert render.call_count == 2

    def test_zoom_change_within_tolerance_hits(self) -> None:
        renderer = _make_renderer(zoom=1.0)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.camera.zoom = 1.001
            layer.draw(renderer, screen)

        assert render.call_count == 1

    def test_viewport_width_resize_invalidates(self) -> None:
        renderer = _make_renderer(screen_width=800)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.screen_width = 1024
            layer.draw(renderer, screen)

        assert render.call_count == 2

    def test_viewport_height_resize_invalidates(self) -> None:
        renderer = _make_renderer(screen_height=600)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.screen_height = 768
            layer.draw(renderer, screen)

        assert render.call_count == 2

    def test_hex_size_change_invalidates(self) -> None:
        renderer = _make_renderer(hex_size=10)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            renderer.hex_size = 12
            layer.draw(renderer, screen)

        assert render.call_count == 2


class TestGridCacheCutoff:
    """Verify zoom < 0.4 short-circuits before any cache work."""

    def test_zoom_below_cutoff_is_noop(self) -> None:
        renderer = _make_renderer(zoom=0.3)
        screen = MagicMock()
        layer = GridLayer()

        with patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)

        render.assert_not_called()
        screen.blit.assert_not_called()
        assert layer._cache_surface is None
        assert layer._cache_key is None

    def test_zoom_at_cutoff_renders(self) -> None:
        renderer = _make_renderer(zoom=0.4)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)

        assert render.call_count == 1

    def test_zoom_cutoff_round_trip_preserves_cache(self) -> None:
        """Zoom across the cutoff boundary must not invalidate the cache.

        Sequence: render at zoom=0.5 (populate cache) → draw at zoom=0.3
        (early return, no render, cache untouched) → draw at zoom=0.5 again
        (must hit the populated cache, no second render). This locks in the
        invariant that the early return at the start of GridLayer.draw
        preserves cache state — a future refactor that moved the cutoff
        check below _compute_key would silently break it.
        """
        renderer = _make_renderer(zoom=0.5)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)
            populated_surface = layer._cache_surface
            populated_key = layer._cache_key
            assert render.call_count == 1
            assert populated_surface is not None
            assert populated_key is not None

            renderer.camera.zoom = 0.3
            layer.draw(renderer, screen)
            assert render.call_count == 1, "no render below cutoff"
            assert layer._cache_surface is populated_surface, "cache surface preserved"
            assert layer._cache_key == populated_key, "cache key preserved"

            renderer.camera.zoom = 0.5
            layer.draw(renderer, screen)
            assert render.call_count == 1, (
                "round-trip back across the cutoff must hit the existing cache"
            )
            assert layer._cache_surface is populated_surface


class TestGridCacheSurface:
    """Verify surface allocation, reuse, and SRCALPHA flag."""

    def test_cache_surface_reused_across_misses(self) -> None:
        renderer = _make_renderer()
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ):
            layer.draw(renderer, screen)
            first_surface = layer._cache_surface
            assert first_surface is not None

            for i in range(5):
                renderer.camera.position = pygame.math.Vector2(i + 1.0, 0.0)
                layer.draw(renderer, screen)

            assert layer._cache_surface is first_surface, (
                "Surface object must be reused across cache misses; "
                "no allocation per miss."
            )

    def test_cache_surface_uses_srcalpha(self) -> None:
        renderer = _make_renderer()
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ):
            layer.draw(renderer, screen)

        assert layer._cache_surface is not None
        # SRCALPHA surfaces report 32-bit-depth and have per-pixel alpha.
        assert layer._cache_surface.get_flags() & pygame.SRCALPHA

    def test_viewport_resize_reallocates_surface(self) -> None:
        renderer = _make_renderer(screen_width=800, screen_height=600)
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ):
            layer.draw(renderer, screen)
            first_surface = layer._cache_surface
            assert first_surface.get_size() == (800, 600)

            renderer.screen_width = 1024
            renderer.screen_height = 768
            layer.draw(renderer, screen)

            assert layer._cache_surface is not first_surface
            assert layer._cache_surface.get_size() == (1024, 768)

    def test_blit_target_is_passed_in_screen(self) -> None:
        renderer = _make_renderer()
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ):
            layer.draw(renderer, screen)

        screen.blit.assert_called_once()
        blit_args = screen.blit.call_args.args
        # First positional arg is the cache surface; second is the dest.
        assert blit_args[0] is layer._cache_surface
        assert blit_args[1] == (0, 0)


class TestGridCacheRenderDispatch:
    """Verify the underlying render is dispatched to the cache surface."""

    def test_render_target_is_cache_surface_not_screen(self) -> None:
        renderer = _make_renderer()
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ) as render:
            layer.draw(renderer, screen)

        assert render.call_count == 1
        target = render.call_args.args[1]
        assert target is layer._cache_surface
        assert target is not screen

    def test_cache_clears_to_transparent_on_miss(self) -> None:
        """Each miss must fill(0,0,0,0) before redrawing — no leftover pixels."""
        renderer = _make_renderer()
        screen = MagicMock()
        layer = GridLayer()

        with _patch_inner_draw(), patch(
            "game.ui.screens.strategy_render.grid._render_grid_to_surface"
        ):
            layer.draw(renderer, screen)
            # Mark the surface — write a non-zero pixel.
            layer._cache_surface.fill((255, 0, 0, 255))
            # Force a miss.
            renderer.camera.position = pygame.math.Vector2(5.0, 0.0)
            layer.draw(renderer, screen)

        # After the second draw the surface should have been cleared
        # (transparent corner pixel since _render_grid_to_surface is mocked).
        corner = layer._cache_surface.get_at((0, 0))
        assert corner == (0, 0, 0, 0)
