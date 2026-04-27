"""Planet Abilities Window + planet-editor dispatch.

The abilities window is opened from a right-click on a planet; clicking an
editor button (atmosphere / gravity / water / radiation / food) routes back
to the strategy event router, which owns each editor's lifecycle.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class PlanetAbilitiesRegistrar:
    """Lifecycle for the Planet Abilities Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self, planet) -> None:
        """Open the planet abilities management window."""
        c = self._composer
        # Local import preserved from source.
        from game.ui.screens.planet_abilities_window import PlanetAbilitiesWindow
        from game.core.registry import get_default_registry_provider

        component_registry = None
        try:
            provider = get_default_registry_provider()
            component_registry = provider.get_components()
        except Exception:  # Intentional broad catch: registry provider may be uninitialized; abilities window opens without registry-backed lookups
            pass

        width = 540
        height = 300
        x = (c.width - width) / 2
        y = (c.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        c.planet_abilities_window = PlanetAbilitiesWindow(
            rect, c.manager, planet, c.scene.facade, component_registry,
            on_open_editor=self.open_editor,
        )

    def open_editor(self, editor_type: str, planet) -> None:
        """Dispatch a planet-environment editor request to the event router.

        Args:
            editor_type: One of 'atmosphere', 'gravity', 'water', 'radiation', 'food'.
            planet: Planet object.
        """
        c = self._composer
        # Local import preserved from source.
        from game.ui.screens.strategy_event_router import StrategyEventRouter
        # Delegate to the event router which has all editor opening methods.
        router = getattr(c.scene, "_event_router", None)
        if router is None:
            # Build a temporary router if not available on scene
            router = StrategyEventRouter(c.scene.ui)
        editor_map = {
            "atmosphere": router._open_atmosphere_editor,
            "gravity": router._open_gravity_editor,
            "water": router._open_water_editor,
            "radiation": router._open_radiation_shield_editor,
            # PROJ-284 Phase 4: per-colony per-species food allocation.
            "food": router._open_food_allocation_editor,
        }
        opener = editor_map.get(editor_type)
        if opener:
            opener(planet)
