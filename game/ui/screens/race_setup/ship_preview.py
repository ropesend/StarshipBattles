"""PROJ-309 Sub-phase 3.1 — ShipPreviewBuilder.

Constructs the 3x3 grid of (top-down skin, portrait) image pairs for the
Ships tab. Extracted from `RaceSetupRenderer` per design §4 to give
renderer a single concern (modal construction) and ship-preview its own
testable module.

Reads from the active `ShipThemeManager`; writes pygame_gui widgets
into the screen's `ship_preview_scroll` container. Holds its own
widget references so it can clear them on theme change.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List

import pygame
import pygame_gui

from game.ui.assets import get_default_ship_theme_manager

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen

logger = logging.getLogger(__name__)


class ShipPreviewBuilder:
    """Build + refresh the Ships-tab preview grid."""

    def __init__(self, *, screen: "RaceSetupScreen") -> None:
        self._screen = screen
        self._elements: List = []

    def refresh(self, theme_id: str) -> None:
        """Clear the grid, then rebuild for `theme_id`."""
        screen = self._screen
        logger.debug(f"refresh_ship_preview called with theme_id: {theme_id}")

        # Clear existing previews.
        for elem in self._elements:
            elem.kill()
        self._elements = []

        if screen.ship_preview_scroll is None:
            logger.debug("ship_preview_scroll not found, returning")
            return

        container = screen.ship_preview_scroll
        container_width = container.get_relative_rect().width - 30
        logger.debug(f"Container width: {container_width}")

        # Representative ship classes (3x3 grid = 9 ships).
        ship_classes = [
            "Fighter (Medium)", "Satellite (Medium)", "Escort",
            "Frigate", "Cruiser", "Heavy Cruiser",
            "Battleship", "Dreadnought", "Superdreadnought",
        ]

        theme_manager = get_default_ship_theme_manager()
        theme_manager.initialize()

        # Layout: 3 columns; each cell shows top-down + portrait pair.
        num_cols = 3
        portrait_size = 160
        image_gap = 5
        col_width = container_width // num_cols
        row_height = portrait_size + 35  # label(25) + gap(5) + image + bottom_pad(5)
        row_spacing = 10

        # Set scrollable area BEFORE adding elements.
        total_rows = (len(ship_classes) + num_cols - 1) // num_cols
        scroll_height = 10 + total_rows * (row_height + row_spacing) + 20
        screen.ship_preview_scroll.set_scrollable_area_dimensions(
            (container_width, scroll_height)
        )

        y = 10

        for i, ship_class in enumerate(ship_classes):
            col = i % num_cols
            if col == 0 and i > 0:
                y += row_height + row_spacing

            x = 10 + col * col_width

            # Ship class label - centered above image pair.
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, col_width - 10, 25),
                text=ship_class,
                manager=screen.ui_manager,
                container=container,
            )
            self._elements.append(label)

            # Top-down (skin) image with smart scaling using visible bounds.
            skin_surf = theme_manager.load_image(theme_id, ship_class)
            scaled_skin = None
            logger.debug(f"Ship {ship_class}: skin_surf={skin_surf is not None}")
            if skin_surf:
                img_width, img_height = skin_surf.get_size()
                metrics = theme_manager.get_image_metrics(theme_id, ship_class)

                if metrics and metrics.width > 0 and metrics.height > 0:
                    scale_factor = portrait_size / max(metrics.width, metrics.height)
                    scale_factor = min(scale_factor, 3.0)  # Cap to prevent blowup
                else:
                    scale_factor = portrait_size / max(img_width, img_height)

                new_w = max(1, int(img_width * scale_factor))
                new_h = max(1, int(img_height * scale_factor))
                scaled_skin = pygame.transform.smoothscale(skin_surf, (new_w, new_h))

                # Crop to visible area if metrics available.
                if metrics and metrics.width > 0 and metrics.height > 0:
                    crop_x = max(0, int(metrics.x * scale_factor))
                    crop_y = max(0, int(metrics.y * scale_factor))
                    crop_w = min(int(metrics.width * scale_factor), new_w - crop_x)
                    crop_h = min(int(metrics.height * scale_factor), new_h - crop_y)
                    if crop_w > 0 and crop_h > 0:
                        cropped = scaled_skin.subsurface(
                            pygame.Rect(crop_x, crop_y, crop_w, crop_h)
                        )
                        scaled_skin = cropped

            # Portrait image.
            portrait_surf = theme_manager.get_portrait_image(theme_id, ship_class)
            scaled_portrait = None
            logger.debug(
                f"Ship {ship_class}: portrait_surf={portrait_surf is not None}"
            )
            if portrait_surf:
                p_w, p_h = portrait_surf.get_size()
                p_scale = min(portrait_size / p_w, portrait_size / p_h)
                scaled_portrait = pygame.transform.smoothscale(
                    portrait_surf, (int(p_w * p_scale), int(p_h * p_scale))
                )

            # Centered positions for the image pair.
            topdown_w = scaled_skin.get_width() if scaled_skin else 0
            topdown_h = scaled_skin.get_height() if scaled_skin else 0
            portrait_w = scaled_portrait.get_width() if scaled_portrait else 0
            pair_width = topdown_w + image_gap + portrait_w
            pair_x = x + (col_width - pair_width) // 2

            if scaled_skin:
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(pair_x, y + 30, topdown_w, topdown_h),
                    image_surface=scaled_skin,
                    manager=screen.ui_manager,
                    container=container,
                )
                self._elements.append(img)

            if scaled_portrait:
                portrait_x = pair_x + topdown_w + image_gap
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(portrait_x, y + 30, portrait_w, portrait_size),
                    image_surface=scaled_portrait,
                    manager=screen.ui_manager,
                    container=container,
                )
                self._elements.append(img)
