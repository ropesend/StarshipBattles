"""Transfer Dialog + Cargo Quick Dialog registrar (PROJ-68 / PROJ-100).

Both dialogs are initiated from the same fleet right-click flow but have
different payloads — the quick dialog is the simplified D/L variant.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class TransferDialogRegistrar:
    """Lifecycle for the Transfer Dialog slot (PROJ-68)."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self, source_fleet, hex_coord) -> None:
        """Open the cargo/population transfer dialog.

        Args:
            source_fleet: The fleet initiating the transfer.
            hex_coord: The hex coordinate for the transfer context.
        """
        c = self._composer
        if c.transfer_dialog is not None:
            c.transfer_dialog.kill()
            c.transfer_dialog = None

        # Local import preserved from source.
        from game.ui.screens.transfer_dialog import TransferDialog

        win_w, win_h = 940, 700
        win_rect = pygame.Rect(0, 0, win_w, win_h)
        win_rect.center = (c.width // 2, c.height // 2)

        c.transfer_dialog = TransferDialog(
            relative_rect=win_rect,
            manager=c.manager,
            source_fleet=source_fleet,
            hex_coord=hex_coord,
            scene=c.scene,
            window_manager=c,
            input_mapper=c._mapper,
        )

    def open_quick(self, fleet, hex_coord, direction: str) -> None:
        """Open the quick cargo drop/load dialog (PROJ-100).

        Args:
            fleet: The fleet involved in the transfer.
            hex_coord: The hex coordinate for the transfer.
            direction: 'unload' for dropping cargo, 'load' for loading cargo.
        """
        c = self._composer

        # Local import preserved from source.
        from game.ui.screens.cargo_quick_dialog import CargoQuickDialog

        win_w, win_h = 500, 450
        win_rect = pygame.Rect(0, 0, win_w, win_h)
        win_rect.center = (c.width // 2, c.height // 2)

        c.cargo_quick_dialog = CargoQuickDialog(
            relative_rect=win_rect,
            manager=c.manager,
            fleet=fleet,
            hex_coord=hex_coord,
            direction=direction,
            scene=c.scene,
            window_manager=c,
            input_mapper=c._mapper,
        )
