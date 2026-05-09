"""Strategy-map renderer composer (PROJ-309 sub-phase 3.2).

This module hosts ``StrategyRenderer``, the orchestrator class that owns
per-frame rendering state (background cache, hex-outline cache, animation
clock) and composes the layer modules in ``game.ui.screens.strategy_render``
in the documented draw order:

    background -> grid -> hex-outlines -> warp-lanes -> systems
        -> fleets -> move-preview / ghost-hex / hover-hex -> border

Each ``_draw_*`` method is a thin delegator to its layer module — kept on
the class so existing tests that monkey-patch instance attributes (e.g.
``renderer._draw_grid = MagicMock()``) continue to work.

Public API: ``StrategyRenderer(scene)``, ``update(dt)``, ``draw(screen)``,
``draw_processing_overlay(screen)``. ``WARP_POINT_ROTATION_SPEED`` re-exported
for back-compat with ``test_strategy_renderer_animation.py``.
"""
from __future__ import annotations

import logging
from typing import Any

import pygame

from game.ui.config import UIConfig
from game.ui.colors import COLORS
from game.ui.fonts import get_font

from game.ui.screens.strategy_render.background import BackgroundLayer
from game.ui.screens.strategy_render.context import hex_radius_to_screen
from game.ui.screens.strategy_render.cursor import (
    draw_ghost_hex as _layer_draw_ghost_hex,
    draw_hover_hex as _layer_draw_hover_hex,
    draw_move_preview as _layer_draw_move_preview,
)
from game.ui.screens.strategy_render.fleets import (
    draw_fleet_path as _layer_draw_fleet_path,
    draw_fleets as _layer_draw_fleets,
)
from game.ui.screens.strategy_render.grid import GridLayer
from game.ui.screens.strategy_render.hex_outlines import (
    HexOutlineLayer,
    draw_inner_hex as _layer_draw_inner_hex,
)
from game.ui.screens.strategy_render.overlay import (
    draw_processing_overlay as _layer_draw_processing_overlay,
)
from game.ui.screens.strategy_render.systems import (
    WARP_POINT_ROTATION_SPEED,
    draw_colony_marker as _layer_draw_colony_marker,
    draw_star as _layer_draw_star,
    draw_system_details as _layer_draw_system_details,
    draw_systems as _layer_draw_systems,
)
from game.ui.screens.strategy_render.dyson_spheres import (
    draw_dyson_spheres as _layer_draw_dyson_spheres,
)
from game.ui.screens.strategy_render.planets import (
    draw_planet_sprite as _layer_draw_planet_sprite,
)
from game.ui.screens.strategy_render.storms import (
    draw_storms as _layer_draw_storms,
    draw_storms_low_detail as _layer_draw_storms_low_detail,
)
from game.ui.screens.strategy_render.warp_lanes import (
    draw_warp_lanes as _layer_draw_warp_lanes,
)

logger = logging.getLogger(__name__)

# Re-exported for backwards compatibility with test_strategy_renderer_animation.py.
__all__ = ["StrategyRenderer", "WARP_POINT_ROTATION_SPEED"]


class StrategyRenderer:
    """Composer that holds per-frame state and orchestrates layer modules."""

    def __init__(self, scene):
        """Initialize renderer with a scene reference.

        Args:
            scene: StrategyScreen instance providing camera, galaxy, empires, etc.
        """
        self.scene = scene

        # Cache asset manager reference
        from game.assets.asset_manager import get_asset_manager
        self._asset_manager = get_asset_manager()

        # Background layer (owns its scaled-surface cache)
        self._background = BackgroundLayer(self._asset_manager)

        # Settings reference
        from game.ui.services.game_settings import GameSettings
        self._settings = GameSettings()

        # Animation state
        self._elapsed_time = 0.0

        # Hex outline layer (owns its turn-keyed cache)
        self._hex_outlines = HexOutlineLayer()

        # Grid layer (owns its property-keyed surface cache, PROJ-374)
        self._grid = GridLayer()

    # -- Back-compat shims for tests that read these as instance attributes --
    @property
    def _bg_image(self) -> Any:
        return self._background._bg_image

    @property
    def _bg_scaled(self) -> Any:
        return self._background._bg_scaled

    @property
    def _bg_scaled_size(self) -> Any:
        return self._background._bg_scaled_size

    @property
    def _bg_brightness(self) -> Any:
        return self._background._bg_brightness

    @property
    def _hex_outline_cache(self) -> Any:
        return self._hex_outlines._hex_outline_cache

    @property
    def _hex_outline_cache_turn(self) -> Any:
        return self._hex_outlines._hex_outline_cache_turn

    def update(self, dt: float) -> None:
        """Update animation state.

        Args:
            dt: Delta time in seconds since last frame.
        """
        self._elapsed_time += dt

    def _get_font(self, size, bold=False) -> Any:
        """Get a cached font by size and style (uses central font cache)."""
        return get_font(size, bold=bold)

    # --- Property Accessors (delegate to scene) ---
    @property
    def camera(self) -> Any:
        return self.scene.camera

    @property
    def galaxy(self) -> Any:
        return self.scene.galaxy

    @property
    def systems(self) -> Any:
        return self.scene.systems

    @property
    def empires(self) -> Any:
        return self.scene.empires

    @property
    def hex_size(self) -> Any:
        return self.scene.hex_size

    @property
    def screen_width(self) -> Any:
        return self.scene.screen_width

    @property
    def screen_height(self) -> Any:
        return self.scene.screen_height

    @property
    def SIDEBAR_WIDTH(self) -> Any:
        return UIConfig.STRATEGY_SIDEBAR_WIDTH

    @property
    def TOP_BAR_HEIGHT(self) -> Any:
        return self.scene.TOP_BAR_HEIGHT

    @property
    def empire_assets(self) -> Any:
        return self.scene.empire_assets

    def _hex_radius_to_screen(self, radius_hexes: float) -> int:
        """Convert a hex-space radius to screen pixels (BUG-94 power curve)."""
        return hex_radius_to_screen(radius_hexes, self.hex_size, self.camera.zoom)

    # --- Layer wrappers (kept on the class so tests can monkey-patch) ---
    def _draw_background(self, screen, viewport_rect: pygame.Rect) -> None:
        self._background.draw(screen, viewport_rect, self._settings.background_brightness)

    def _draw_grid(self, screen) -> None:
        self._grid.draw(self, screen)

    def _draw_hex_outlines(self, screen) -> None:
        self._hex_outlines.draw(self, screen)

    def _build_hex_outline_data(self) -> Any:
        return self._hex_outlines.build_data(self)

    def _get_hex_outline_data(self) -> Any:
        return self._hex_outlines.get_data(self)

    def _draw_inner_hex(self, screen, cx, cy, scale, color) -> None:
        _layer_draw_inner_hex(self, screen, cx, cy, scale, color)

    def _draw_warp_lanes(self, screen) -> None:
        _layer_draw_warp_lanes(self, screen)

    def _draw_systems(self, screen) -> None:
        _layer_draw_systems(self, screen)

    def _draw_colony_marker(self, screen, sys, world_pos) -> None:
        _layer_draw_colony_marker(self, screen, sys, world_pos)

    def _draw_star(self, screen, star, system_center, system_name, is_primary, is_selected_system) -> None:
        _layer_draw_star(self, screen, star, system_center, system_name, is_primary, is_selected_system)

    def _draw_system_details(self, screen, sys, sys_world_pos) -> None:
        _layer_draw_system_details(self, screen, sys, sys_world_pos)

    def _draw_dyson_spheres(self, screen, sys, sys_world_pos) -> None:
        _layer_draw_dyson_spheres(self, screen, sys, sys_world_pos)

    def _draw_storms(self, screen, sys, sys_world_pos) -> None:
        _layer_draw_storms(self, screen, sys, sys_world_pos)

    def _draw_storms_low_detail(self, screen, sys, sys_world_pos) -> None:
        _layer_draw_storms_low_detail(self, screen, sys, sys_world_pos)

    def _draw_planet_sprite(self, screen, planet, center_pos, size) -> None:
        _layer_draw_planet_sprite(self, screen, planet, center_pos, size)

    def _draw_fleets(self, screen) -> None:
        _layer_draw_fleets(self, screen)

    def _draw_fleet_path(self, screen, fleet, fleet_screen_pos) -> None:
        _layer_draw_fleet_path(self, screen, fleet, fleet_screen_pos)

    def _draw_move_preview(self, screen) -> None:
        _layer_draw_move_preview(self, screen)

    def _draw_ghost_hex(self, screen, ghost_hex) -> None:
        _layer_draw_ghost_hex(self, screen, ghost_hex)

    def _draw_hover_hex(self, screen) -> None:
        _layer_draw_hover_hex(self, screen)

    # --- Public draw orchestration ---
    def draw(self, screen) -> None:
        """Main draw entry point for the galaxy map."""
        viewport_w = self.screen_width - self.SIDEBAR_WIDTH
        viewport_h = self.screen_height - self.TOP_BAR_HEIGHT

        if viewport_w > 0 and viewport_h > 0:
            viewport_rect = pygame.Rect(0, self.TOP_BAR_HEIGHT, viewport_w, viewport_h)
            screen.set_clip(viewport_rect)
            screen.fill(COLORS['bg_deep'], viewport_rect)
            self._draw_background(screen, viewport_rect)
        else:
            screen.fill(COLORS['bg_deep'])

        # Draw Galaxy Elements (Clipped)
        if self.camera.zoom >= 0.4:
            self._draw_grid(screen)

        # Hex occupancy outlines (behind all objects)
        if self.camera.zoom >= 0.5:
            self._draw_hex_outlines(screen)

        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen)

        # Move/Warp/Colonize Line Preview
        if self.scene.input_mode in ('MOVE', 'WARP_TARGET', 'COLONIZE_TARGET', 'EDIT_MOVE') and self.scene.selected_fleet:
            self._draw_move_preview(screen)

        # EDIT_MOVE ghost hex: outline of old destination
        if self.scene.input_mode == 'EDIT_MOVE' and self.scene._edit_move_ghost_hex:
            self._draw_ghost_hex(screen, self.scene._edit_move_ghost_hex)

        # Hover Highlight
        if self.scene.hover_hex and self.camera.zoom >= 0.5:
            self._draw_hover_hex(screen)

        # Remove Clip for UI
        screen.set_clip(None)

        # Draw Border around Galaxy Viewport
        if viewport_w > 0 and viewport_h > 0:
            viewport_rect = pygame.Rect(0, self.TOP_BAR_HEIGHT, viewport_w, viewport_h)
            pygame.draw.rect(screen, COLORS['border_normal'], viewport_rect, 2)

    def draw_processing_overlay(
        self,
        screen,
        message: str = "PROCESSING TURN...",
        *,
        current_tick: int | None = None,
        total_ticks: int | None = None,
    ) -> None:
        """Draw a modal overlay for turn processing.

        FEAT-20: optional ``message`` lets ``run_n_turns`` show progress text.
        Issue #7: optional ``current_tick`` / ``total_ticks`` render a smaller
        secondary "Tick N / M" line below the main label.
        """
        _layer_draw_processing_overlay(
            screen, self._get_font, message,
            current_tick=current_tick, total_ticks=total_ticks,
        )
