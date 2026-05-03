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
from PIL import Image

from game.core.paths import Paths
from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from game.ui.assets import ShipThemeManager, set_default_ship_theme_manager


SYNTHETIC_FALLBACK_SIZE = (100, 100)
TARGET_SIZE = (Paths.SHIP_THEMES_TARGET_SIZE, Paths.SHIP_THEMES_TARGET_SIZE)

# Known gaps the user is expected to fill via
# `python -m Tools.regenerate_ship_portraits.cli ...`.
# As portraits are generated, remove entries from this set.
EXPECTED_PORTRAIT_GAPS: frozenset[tuple[str, str]] = frozenset({
    *(("Aetherwake", cls) for cls in SHIP_CLASSES_WITH_VISUAL_THEMES),
    ("Atlantians", "Light Cruiser"),
})

# Current tracked portraits predate the 2048x2048 target size in these
# themes. This is intentionally exact: if any allowlisted portrait is
# regenerated to the target size, the test fails until the allowlist shrinks.
EXPECTED_PORTRAIT_SIZE_MISMATCH_THEMES: frozenset[str] = frozenset({
    "Atlantians",
    "Federation",
    "Klingons",
    "Ossivine",
    "Prismsteel",
    "Romulans",
    "Thoraliens",
    "Voidforged",
})
EXPECTED_PORTRAIT_SIZE_MISMATCHES: frozenset[tuple[str, str]] = frozenset(
    (theme, cls)
    for theme in EXPECTED_PORTRAIT_SIZE_MISMATCH_THEMES
    for cls in SHIP_CLASSES_WITH_VISUAL_THEMES
    if (theme, cls) not in EXPECTED_PORTRAIT_GAPS
)


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


def test_every_skin_is_2048x2048(
    initialized_manager: ShipThemeManager,
) -> None:
    """Every Race Setup skin asset must match the canonical target size."""
    for theme_name, ships in initialized_manager.theme_data.items():
        for ship_class, entry in ships.items():
            skin_path = entry["skin_path"]
            with Image.open(skin_path) as img:
                assert img.size == TARGET_SIZE, (
                    f"Theme {theme_name}/{ship_class}: skin size {img.size}, "
                    f"expected {TARGET_SIZE}"
                )
                assert img.mode in {"RGB", "RGBA"}, (
                    f"Theme {theme_name}/{ship_class}: skin mode {img.mode}, "
                    "expected RGB or RGBA"
                )


# PROJ-323 Task 5.9: split single test into two: allowlist-drift detection
# and target-sized portrait verification.

def test_allowlisted_portrait_size_mismatches_remain_non_target(
    initialized_manager: ShipThemeManager,
) -> None:
    """Allowlisted size-mismatch portraits must still be non-target-sized.

    Drift detection: if an allowlist entry is now target-sized, it should
    be removed from EXPECTED_PORTRAIT_SIZE_MISMATCHES.
    """
    for theme_name in initialized_manager.theme_data:
        for ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES:
            pair = (theme_name, ship_class)
            if pair in EXPECTED_PORTRAIT_GAPS:
                continue
            if pair not in EXPECTED_PORTRAIT_SIZE_MISMATCHES:
                continue

            portrait_path = initialized_manager.get_portrait_path(theme_name, ship_class)
            assert portrait_path is not None
            with Image.open(portrait_path) as img:
                assert img.size != TARGET_SIZE, (
                    f"Theme {theme_name}/{ship_class}: allowlist entry is "
                    "now target-sized; remove it from EXPECTED_PORTRAIT_SIZE_MISMATCHES"
                )
                assert img.mode in {"RGB", "RGBA"}


def test_every_non_allowlisted_portrait_is_target_sized(
    initialized_manager: ShipThemeManager,
) -> None:
    """Non-allowlisted portraits must be target-sized and have valid mode."""
    for theme_name in initialized_manager.theme_data:
        for ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES:
            pair = (theme_name, ship_class)
            if pair in EXPECTED_PORTRAIT_GAPS:
                continue
            if pair in EXPECTED_PORTRAIT_SIZE_MISMATCHES:
                continue

            portrait_path = initialized_manager.get_portrait_path(theme_name, ship_class)
            assert portrait_path is not None, (
                f"Theme {theme_name}/{ship_class}: missing portrait path; "
                "add to EXPECTED_PORTRAIT_GAPS only for known deferred work"
            )
            with Image.open(portrait_path) as img:
                assert img.size == TARGET_SIZE, (
                    f"Theme {theme_name}/{ship_class}: portrait size {img.size}, "
                    f"expected {TARGET_SIZE}"
                )
                assert img.mode in {"RGB", "RGBA"}, (
                    f"Theme {theme_name}/{ship_class}: portrait mode {img.mode}, "
                    "expected RGB or RGBA"
                )


def test_every_portrait_is_real_or_in_allowlist(
    initialized_manager: ShipThemeManager,
) -> None:
    """Portrait Surfaces must not be synthetic fallback outside known gaps."""
    for theme_name in initialized_manager.theme_data:
        for ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES:
            pair = (theme_name, ship_class)
            surf = initialized_manager.get_portrait_image(theme_name, ship_class)
            if pair in EXPECTED_PORTRAIT_GAPS:
                assert surf.get_size() == SYNTHETIC_FALLBACK_SIZE, (
                    f"Theme {theme_name}/{ship_class}: allowlist entry now "
                    "returns a real portrait; remove it from EXPECTED_PORTRAIT_GAPS"
                )
            else:
                assert surf.get_size() != SYNTHETIC_FALLBACK_SIZE, (
                    f"Theme {theme_name}/{ship_class}: portrait returned the "
                    "synthetic fallback but is not allowlisted"
                )
