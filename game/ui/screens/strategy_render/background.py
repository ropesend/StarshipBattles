"""Background galaxy image layer (PROJ-309 sub-phase 3.2).

``BackgroundLayer`` owns a scaled-surface cache that is rebuilt only when
the viewport size or brightness changes.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

if TYPE_CHECKING:
    from game.assets.asset_manager import AssetManager


class BackgroundLayer:
    """Static galaxy bg image: load once, scale + dim cache, blit."""

    def __init__(self, asset_manager: Any) -> None:
        self._asset_manager = asset_manager
        self._bg_image: Any = None
        self._bg_scaled: Any = None
        self._bg_scaled_size: tuple[int, int] = (0, 0)
        self._bg_brightness: float = -1.0  # force rebuild on first draw
        self._load_background()

    def _load_background(self) -> None:
        """Load the galaxy background image from the asset manifest."""
        img = self._asset_manager.load_image('backgrounds', 'strategy_map')
        if isinstance(img, pygame.Surface) and img != self._asset_manager.get_missing_texture():
            self._bg_image = img

    def draw(self, screen: Any, viewport_rect: pygame.Rect, brightness: float) -> None:
        """Draw the static background image scaled to fill the viewport.

        Applies brightness dimming from game settings.
        """
        if self._bg_image is None:
            return

        target_size = (viewport_rect.width, viewport_rect.height)

        # Rebuild scaled surface if size or brightness changed
        if (self._bg_scaled is None
                or self._bg_scaled_size != target_size
                or self._bg_brightness != brightness):
            scaled = pygame.transform.smoothscale(self._bg_image, target_size)
            if brightness < 1.0:
                # Dim by blitting a semi-transparent black overlay
                dim = pygame.Surface(target_size)
                dim.fill((0, 0, 0))
                dim.set_alpha(int((1.0 - brightness) * 255))
                scaled.blit(dim, (0, 0))
            self._bg_scaled = scaled
            self._bg_scaled_size = target_size
            self._bg_brightness = brightness

        screen.blit(self._bg_scaled, viewport_rect.topleft)
