"""Fleet Report Window registrar.

Builds a ``split_fleet_callback`` closure that dispatches
``SplitFleetCommand`` through the facade. The closure captures ``facade``
and ``fleet_owner_id`` as locals to guarantee stable references.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from game.ui.screens.fleet_report_window import FleetReportWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class FleetReportRegistrar:
    """Lifecycle for the Fleet Report Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self, fleet) -> None:
        c = self._composer
        if c.fleet_report_window:
            c.fleet_report_window.kill()

        # Match PlanetListWindow size (90% of screen)
        w, h = c.width * 0.9, c.height * 0.9
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        # PROJ-208 Phase 1: Create callback closure for SplitFleetCommand dispatch
        # PROJ-208 Phase 3: Route through facade (not session) for CQRS consistency
        facade = c.scene.facade
        fleet_owner_id = fleet.owner_id

        def split_fleet_callback(fleet_id: int, ship_instance_ids: list) -> Any:
            """Dispatch SplitFleetCommand through facade command pipeline."""
            from game.strategy.engine.commands import SplitFleetCommand
            cmd = SplitFleetCommand(
                fleet_id=fleet_id,
                ship_instance_ids=ship_instance_ids,
                empire_id=fleet_owner_id,
            )
            return facade.handle_command(cmd)

        empire = c.scene.current_empire
        c.fleet_report_window = FleetReportWindow(
            rect,
            c.manager,
            fleet,
            empire=empire,
            window_manager=c,
            on_close_callback=self._on_closed,
            split_fleet_callback=split_fleet_callback,
        )

    def _on_closed(self) -> None:
        self._composer.fleet_report_window = None
