"""PROJ-309 Sub-phase 3.1 — Per-tab content factories.

Wires each of the seven tab panels (Summary / Identity / Visuals /
Ships / Environment / Aptitudes / Descriptions) by instantiating the
relevant extracted panel/gallery class from `game/ui/panels/`.

Each factory is a thin, ~5–25 LOC piece of glue: construct the
component, store the reference back on the screen. PROJ-12 / PROJ-44 /
PROJ-66 already extracted the panel classes themselves; this module
only owns their wiring.

PROJ-299: the descriptions factory ALSO constructs and wires the
`RaceDescriptionLLMController` when an LLM provider is available
(falls back gracefully to plain text-entry when not).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui

from game.ui.panels.race_aptitudes_panel import RaceAptitudesPanel
from game.ui.panels.race_description_panel import RaceDescriptionPanel
from game.ui.panels.race_environment_panel import RaceEnvironmentPanel
from game.ui.panels.race_flag_gallery import RaceFlagGallery
from game.ui.panels.race_identity_panel import RaceIdentityPanel
from game.ui.panels.race_portrait_gallery import RacePortraitGallery
from game.ui.panels.race_summary_panel import RaceSummaryPanel
from game.ui.panels.race_theme_gallery import RaceThemeGallery

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen


def create_summary_panel(screen: "RaceSetupScreen", panel) -> None:
    """Summary tab — landing page with master Randomize All button."""
    screen._summary_panel = RaceSummaryPanel(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        asset_loader=screen._asset_loader,
        on_load_race_callback=screen._controller.on_load_race,
        on_randomize_all_callback=screen._controller.randomize_all,
    )
    screen.btn_load = screen._summary_panel.btn_load
    # FEAT-12: master Randomize All button reference.
    screen.btn_randomize_all = screen._summary_panel.btn_randomize_all


def create_identity_panel(screen: "RaceSetupScreen", panel) -> None:
    """Identity tab — race name, government, faction (PROJ-66 Phase 6)."""
    screen._identity_panel = RaceIdentityPanel(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )


def create_visuals_panel(screen: "RaceSetupScreen", panel) -> None:
    """Visuals tab — Flags + Portraits side-by-side."""
    panel_width = panel.get_relative_rect().width - 20
    panel_height = panel.get_relative_rect().height
    y = 10
    col_width = (panel_width - 20) // 2
    gallery_height = panel_height - y - 20

    screen._flag_gallery = RaceFlagGallery(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        x=10,
        y=y,
        width=col_width,
        height=gallery_height,
        asset_loader=screen._asset_loader,
    )

    screen._portrait_gallery = RacePortraitGallery(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        x=15 + col_width,
        y=y,
        width=col_width,
        height=gallery_height,
        asset_loader=screen._asset_loader,
    )


def create_ships_panel(screen: "RaceSetupScreen", panel) -> None:
    """Ships tab — theme list (left) + preview grid (right)."""
    panel_width = panel.get_relative_rect().width - 20
    panel_height = panel.get_relative_rect().height
    y = 10

    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, y, panel_width, 35),
        text="Select Ship Theme",
        manager=screen.ui_manager,
        container=panel,
    )
    y += 45

    # PROJ-96: theme list on left, preview grid on right.
    THEME_LIST_WIDTH = 200
    CONTENT_GAP = 10
    content_y = y
    content_height = panel_height - content_y - 10

    screen._theme_gallery = RaceThemeGallery(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        x=10,
        y=content_y,
        width=THEME_LIST_WIDTH,
        height=content_height,
        on_select_callback=screen._controller.on_theme_selected,
    )

    preview_x = 10 + THEME_LIST_WIDTH + CONTENT_GAP
    preview_width = panel_width - THEME_LIST_WIDTH - CONTENT_GAP
    screen.ship_preview_scroll = pygame_gui.elements.UIScrollingContainer(
        relative_rect=pygame.Rect(preview_x, content_y, preview_width, content_height),
        manager=screen.ui_manager,
        container=panel,
        allow_scroll_x=False,
        allow_scroll_y=True,
    )


def create_environment_panel(screen: "RaceSetupScreen", panel) -> None:
    """Environment tab (PROJ-12 Phase 4: delegates to RaceEnvironmentPanel)."""
    screen._environment_panel = RaceEnvironmentPanel(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )


def create_aptitudes_panel(screen: "RaceSetupScreen", panel) -> None:
    """Aptitudes tab (PROJ-66 Phase 6: point-buy aptitudes)."""
    screen._aptitudes_panel = RaceAptitudesPanel(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )


def create_descriptions_panel(screen: "RaceSetupScreen", panel) -> None:
    """Descriptions tab + PROJ-299 LLM controller wiring."""
    screen._description_panel = RaceDescriptionPanel(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )
    # PROJ-299: best-effort LLM-controller wiring. If no provider is
    # configured (no DEEPSEEK_API_KEY), skip wiring so the tab continues
    # to work as plain text-entry.
    from game.services.llm import get_default_llm_provider
    from game.strategy.data.race_caption_loader import RaceCaptionLoader
    from game.strategy.services.race_description_llm_controller import (
        RaceDescriptionLLMController,
    )

    provider = get_default_llm_provider()
    if provider is not None:
        description_controller = RaceDescriptionLLMController(
            race_config=screen.race_config,
            provider=provider,
            caption_loader=RaceCaptionLoader(),
            on_change=screen._controller.on_description_controller_change,
        )
        screen._controller.attach_description_controller(description_controller)
        screen._description_panel.attach_controller(description_controller)
        screen._description_panel.set_state(description_controller)
