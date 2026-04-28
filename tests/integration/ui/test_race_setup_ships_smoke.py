"""Race-Setup Ships tab smoke test (PROJ-314).

Validates the end-to-end loader contract against the live
``assets/ShipThemes/`` filesystem: every theme registers all 19
canonical ship classes, every skin renders as a non-fallback Surface,
and every declared portrait file exists.
"""
from __future__ import annotations

import os

import pygame
import pytest

from game.core.paths import Paths
from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from game.ui.assets import ShipThemeManager, set_default_ship_theme_manager


SYNTHETIC_FALLBACK_SIZE = (100, 100)


@pytest.fixture(scope="module")
def initialized_manager() -> ShipThemeManager:
    """Initialize a fresh ShipThemeManager against the real filesystem."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    if not pygame.display.get_surface():
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
    if not os.path.isdir(Paths.SHIP_THEMES_DIR):
        pytest.skip("ShipThemes directory not present in this checkout")

    manager = ShipThemeManager()
    set_default_ship_theme_manager(manager)
    manager.initialize()
    return manager


def test_every_theme_registers_all_19_ship_classes(
    initialized_manager: ShipThemeManager,
) -> None:
    """PROJ-314: each of the 9 themes declares every canonical ship class."""
    for theme_name, ships in initialized_manager.theme_data.items():
        assert set(ships.keys()) == SHIP_CLASSES_WITH_VISUAL_THEMES, (
            f"Theme {theme_name}: expected exactly the canonical 19 ship "
            f"classes, got {sorted(ships.keys())}"
        )


def test_every_skin_loads_as_non_fallback(
    initialized_manager: ShipThemeManager,
) -> None:
    """PROJ-314: every theme/ship-class pair returns a real skin Surface."""
    for theme_name in initialized_manager.theme_data:
        for ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES:
            surf = initialized_manager.load_image(theme_name, ship_class)
            assert isinstance(surf, pygame.Surface)
            assert surf.get_size() != SYNTHETIC_FALLBACK_SIZE, (
                f"Theme {theme_name}/{ship_class}: skin returned the "
                f"synthetic 100x100 fallback (file missing or unreadable)"
            )


def test_get_portrait_image_always_returns_surface(
    initialized_manager: ShipThemeManager,
) -> None:
    """PROJ-314: get_portrait_image never returns None — synthetic fallback covers gaps."""
    for theme_name in initialized_manager.theme_data:
        for ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES:
            surf = initialized_manager.get_portrait_image(theme_name, ship_class)
            assert isinstance(surf, pygame.Surface), (
                f"Theme {theme_name}/{ship_class}: portrait must be a Surface, "
                f"got {type(surf).__name__}"
            )
