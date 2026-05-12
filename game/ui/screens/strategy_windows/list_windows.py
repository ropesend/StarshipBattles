"""Planet-list + star-list registrars + shared camera-nav helper.

Both list windows share the 90%-screen rect, the navigate-and-close idiom,
and the camera-centering callback — so they live together.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game.ui.screens.planet_list_window import PlanetListWindow
from game.ui.screens.star_list_window import StarListWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


def navigate_camera_to(scene, global_hex) -> None:
    """Center the strategy camera on a hex coordinate.

    Shared by planet- and star-list navigation callbacks.
    """
    if hasattr(scene, "_camera_nav"):
        scene._camera_nav.center_on_hex(global_hex)


class PlanetListRegistrar:
    """Lifecycle for the Planet List Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self) -> None:
        c = self._composer
        w, h = c.width * 0.9, c.height * 0.9
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        empire = c.scene.current_empire
        galaxy = c.scene.galaxy

        # PROJ-290: thread the session race_registry so the planet detail
        # panel can render uncolonized-planet habitability for the
        # viewing empire's species.
        race_registry = None
        facade = getattr(c.scene, "facade", None)
        if facade is not None and hasattr(facade, "get_race_registry"):
            race_registry = facade.get_race_registry()

        c.planet_list_window = PlanetListWindow(
            rect,
            c.manager,
            galaxy,
            empire,
            window_manager=c,
            on_close_callback=self._on_closed,
            asset_resolver=c._asset_resolver,
            empires=c.scene.session.empires,  # PROJ-198: Pass empires for owner name lookup
            registries=c.scene.session.registries,  # PROJ-211: Pass registries for DI
            on_navigate_callback=self._on_navigate,
            race_registry=race_registry,  # PROJ-290
            facade=facade,  # PROJ-292 H1: enables per-species sub-block on colonized planets
        )

    def _on_closed(self) -> None:
        self._composer.planet_list_window = None

    def _on_navigate(self, global_hex) -> None:
        c = self._composer
        if c.planet_list_window:
            c.planet_list_window.kill()
        navigate_camera_to(c.scene, global_hex)


class StarListRegistrar:
    """Lifecycle for the Star List Window slot (PROJ-231)."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self) -> None:
        c = self._composer
        if c.star_list_window:
            c.star_list_window.kill()

        w, h = c.width * 0.9, c.height * 0.9
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        # PROJ-411 Phase 1: pass facade_state so gather_stars uses the
        # per-turn cache instead of re-walking the galaxy on every open.
        # Use getattr to tolerate test stubs that lack `facade_state`.
        _facade = getattr(c.scene, "facade", None)
        _facade_state = getattr(_facade, "facade_state", None) if _facade is not None else None
        c.star_list_window = StarListWindow(
            rect,
            c.manager,
            c.scene.galaxy,
            window_manager=c,
            on_close_callback=self._on_closed,
            on_navigate_callback=self._on_navigate,
            facade_state=_facade_state,
        )

    def _on_closed(self) -> None:
        self._composer.star_list_window = None

    def _on_navigate(self, global_hex) -> None:
        c = self._composer
        if c.star_list_window:
            c.star_list_window.kill()
        navigate_camera_to(c.scene, global_hex)
