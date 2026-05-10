"""Modal selection prompts: planet, system (PROJ-138), fleet (FEAT-08).

Three nearly-identical "modal selector" prompts. Each centers a window of
window-class-specific dimensions and stores the resulting window into the
matching composer slot.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame

from game.ui.screens.fleet_selection_window import FleetSelectionWindow
from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.system_selection_window import SystemSelectionWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class SelectionPromptRegistrar:
    """Lifecycle for the planet / system / fleet selection-prompt slots."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def prompt_planet(self, planets, on_select: Callable) -> None:
        """Open a modal window to select a planet.

        Args:
            planets: List of planets to choose from.
            on_select: Callback called with the selected planet.
        """
        c = self._composer
        # Large window to fit full planet report (matches strategy UI detail panel)
        width = 950
        height = 650
        x = (c.width - width) / 2
        y = (c.height - height) / 2

        rect = pygame.Rect(x, y, width, height)
        # PROJ-54: PlanetSelectionWindow uses PlanetReportPanel internally.
        # PROJ-397 Phase 3 Task 3.2: pass the strategy facade so the
        # internal planet detail panel can fetch ColonyDemographicView
        # for colonized planets (replaces the deleted legacy
        # `view=None` branch in format_planet_info).
        c.planet_selection_window = PlanetSelectionWindow(
            rect, c.manager, planets, on_select,
            window_manager=c,
            facade=c.scene.facade,
        )

    def open_system(self, systems, current_system, on_selected: Callable) -> None:
        """Open a modal window to select a star system (PROJ-138).

        Args:
            systems: List of StarSystem objects to choose from.
            current_system: Current StarSystem (for distance display).
            on_selected: Callback called with selected system name string.
        """
        c = self._composer
        width = 450
        height = 500
        x = (c.width - width) / 2
        y = (c.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        c.system_selection_window = SystemSelectionWindow(
            rect, c.manager, systems, current_system, on_selected,
            window_manager=c,
        )

    def prompt_fleet(self, fleets, on_select: Callable) -> None:
        """Open a modal window to select a fleet to join (FEAT-08).

        Args:
            fleets: List of FleetInfo DTOs to choose from.
            on_select: Callback called with the selected FleetInfo.
        """
        c = self._composer
        width = 450
        height = 400
        x = (c.width - width) / 2
        y = (c.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        c.fleet_selection_window = FleetSelectionWindow(
            rect, c.manager, fleets, on_select,
            window_manager=c,
        )
