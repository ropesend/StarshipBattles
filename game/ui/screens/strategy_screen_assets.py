"""Strategy screen asset loading and resolution helper (PROJ-330).

Extracted from ``strategy_screen.py`` as part of the LOC decomposition.
Owns:

- ``focus_on_player_home``: initial camera centering on the active empire's
  first colony.
- ``load_assets``: bulk asset manifest load + per-empire asset resolution.
- ``get_object_asset``: per-object asset lookup (star/planet/warp-point/fleet).

Each helper takes the screen as a parameter; no new MVVM seam.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pygame

from game.core.hex_math import hex_to_pixel
from game.core.protocols import is_star, is_planet, is_fleet, is_warp_point

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen

logger = logging.getLogger(__name__)


def focus_on_player_home(screen: "StrategyScreen") -> None:
    """Focus camera on player's home colony at startup.

    PROJ-475 Phase 3: the ``screen.active_empire`` pass-through was retired.
    The live home-colony focus needs the live ``Planet`` objects (it identity-
    matches them against the live systems' ``.planets``), so it resolves the
    active empire from the live ``scene.world`` seam keyed by
    ``screen.active_empire_id`` (PROJ-477 Phase 4).
    """
    active_id = screen.active_empire_id
    active_empire = next(
        (e for e in screen.world.iter_empires() if e.id == active_id), None
    )
    if active_empire is not None and active_empire.colonies:
        home_colony = active_empire.colonies[0]
        home_sys = next(
            (s for s in screen.world.iter_systems() if home_colony in s.planets),
            None,
        )
        if home_sys:
            target_hex = home_sys.global_location + home_colony.location
            fx, fy = hex_to_pixel(target_hex, 10)
            screen.camera.position = pygame.math.Vector2(fx, fy)


def load_assets(screen: "StrategyScreen") -> None:
    """Load visual assets using AssetManager and RaceAssetLoader."""
    from game.assets.asset_manager import get_default_asset_manager

    am = get_default_asset_manager()
    am.load_manifest()

    for emp in screen.world.iter_empires():
        screen.empire_assets[emp.id] = screen._race_loader.load_all_empire_assets(emp)


def get_object_asset(screen: "StrategyScreen", obj) -> Any:
    """Resolve the visual asset for a data object."""
    from game.assets.asset_manager import get_default_asset_manager

    am = get_default_asset_manager()

    if is_star(obj):
        if obj.image_id:
            img = am.load_star_image(obj.image_id, requested_size=512)
            if img and img != am.get_missing_texture():
                return img
        return None

    if is_planet(obj):
        if obj.image_id:
            try:
                # PROJ-54 Phase 10: AssetManager handles fallback chain + cache
                img = am.load_planet_image(obj.image_id, requested_size=512)
                if img and img != am.get_missing_texture():
                    if obj.image_rotation and obj.image_rotation != 0.0:
                        img = pygame.transform.rotate(img, obj.image_rotation)
                    return img
            except (FileNotFoundError, OSError, pygame.error, AttributeError) as e:
                logger.warning(f"Could not load planet image {obj.image_id}: {e}")
        return None  # PlanetReportPanel will create gradient placeholder

    if is_warp_point(obj):
        return am.get_random_from_group("warp_points", "default", seed_id=id(obj))

    if is_fleet(obj):
        emp_assets = screen.empire_assets.get(obj.owner_id)
        if emp_assets and "fleet" in emp_assets:
            return emp_assets["fleet"]

    return None
