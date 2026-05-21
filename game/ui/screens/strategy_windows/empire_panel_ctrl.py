"""Empire Panel + Settings Window registrars.

Both are centered modals with no command closures, so they live together.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game.ui.screens.empire_panel_window import EmpirePanelWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class EmpirePanelRegistrar:
    """Lifecycle for the Empire Panel Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self) -> None:
        c = self._composer

        empire = c.scene.current_empire

        w, h = int(c.width * 0.9), int(c.height * 0.9)
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        # PROJ-290: pass the session-scoped race_registry so the Treasury
        # tab's Population Upkeep row has its habitability-multiplier dep.
        race_registry = None
        facade = getattr(c.scene, "facade", None)
        if facade is not None and hasattr(facade, "economy"):
            race_registry = facade.economy.race_registry()

        # Issue #28 (extends PROJ-411 Task 2.3): full window reuse, including
        # cross-empire. ``open_for_empire`` now rebuilds Treasury snapshot +
        # Population content when the empire differs (formerly deferred to
        # kill+reconstruct). The central ``PerPlayerUiState`` swap at turn
        # rotation has a live instance to ``apply_view_state`` against
        # (saved tab index).
        existing = c.empire_panel_window
        if existing is not None and existing.alive():
            existing.open_for_empire(empire)
            return

        # PROJ-411 Phase 1: pass facade_state so EmpireEconomyService.get_snapshot
        # reuses its per-turn cache across Treasury-tab toggles. Use getattr
        # because the facade attribute may be a test stub that lacks the
        # `facade_state` property (e.g. SimpleNamespace test doubles).
        facade_state = getattr(facade, "facade_state", None) if facade is not None else None
        c.empire_panel_window = EmpirePanelWindow(
            rect,
            c.manager,
            empire,
            window_manager=c,
            on_close_callback=self._on_closed,
            registries=c.scene.session.registries,  # PROJ-211: Pass registries for DI
            race_registry=race_registry,
            facade_state=facade_state,
        )

    def _on_closed(self) -> None:
        self._composer.empire_panel_window = None


class SettingsRegistrar:
    """Lifecycle for the Settings Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self) -> None:
        c = self._composer
        if c.settings_window:
            c.settings_window.kill()

        # Local import preserved from source: SettingsWindow has historically
        # been imported at method scope to avoid an import cycle. Keep it
        # deferred here until the cycle is independently verified absent.
        from game.ui.screens.settings_window import SettingsWindow

        w, h = 500, 200
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        c.settings_window = SettingsWindow(
            rect,
            c.manager,
            window_manager=c,
            on_close_callback=self._on_closed,
        )

    def _on_closed(self) -> None:
        self._composer.settings_window = None
