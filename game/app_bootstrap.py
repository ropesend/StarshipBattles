"""Bootstrap + services wiring for the game application.

PROJ-309 sub-phase 3.9: extracted from `game/app.py` so the entry point
becomes a slim orchestrator. This module owns the *deterministic* init
sequence — everything from `pygame.init()` through registry hydration,
ship-data loading, sprite loading, and font construction.

Six initialization-order invariants enforced by `bootstrap()` (see also
`tests/unit/test_app_bootstrap_invariants.py`):

1. `pygame.init()` BEFORE `pygame.display.Info()` / `set_mode()` / pygame_gui.
2. `pygame.font.init()` BEFORE any `get_font()` call (MenuScene constructor).
3. `ApplicationContext.create_production()` BEFORE
   `get_default_registry_provider()`.
4. `load_components` / `load_modifiers` BEFORE `initialize_ship_data`.
5. `SpriteManager.load_sprites` AFTER registries but BEFORE scene constructors.
6. `MenuScene` constructor BEFORE any overlay-dialog code path. (Scenes are
   constructed by `ScreenRouter` after `bootstrap()` returns; the rule is
   thereby enforced by composition order in `Game.__init__`.)
"""
from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from typing import Any

import pygame

from game.context import ApplicationContext
from game.core.config import DisplayConfig
from game.core.paths import Paths
from game.core.registry import GameRegistries, get_default_registry_provider
from game.core.resources import ResourceCatalog
from game.simulation.components.component import load_components, load_modifiers
from game.simulation.entities.ship_loader import initialize_ship_data
from game.ui.fonts import get_font
from game.ui.renderer.sprites import get_default_sprite_manager
from game.ui.services.input_mapper import InputMapper

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Set up application logging. Called once at app startup."""
    os.makedirs(os.path.dirname(Paths.BATTLE_LOG), exist_ok=True)

    root_logger = logging.getLogger("game")
    root_logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(Paths.BATTLE_LOG, mode='w')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Starship Battles")
    parser.add_argument('--force-resolution', action='store_true',
                        help='Force 2560x1600 resolution regardless of monitor size')
    args, _ = parser.parse_known_args()
    return args


@dataclass(frozen=True)
class BootstrapResult:
    """Aggregate output of `bootstrap()`.

    Field list IS the post-bootstrap contract: every consumer (Game,
    ScreenRouter, RunLoop) reads from this dataclass instead of touching
    pygame / registries directly.
    """
    ctx: ApplicationContext
    screen: pygame.Surface
    width: int
    height: int
    clock: pygame.time.Clock
    registries: GameRegistries
    input_mapper: InputMapper
    font_small: Any
    font_med: Any
    font_large: Any


def _detect_resolution(args: argparse.Namespace,
                       monitor_w: int, monitor_h: int) -> tuple[int, int]:
    """Return (width, height) given CLI args + detected monitor size.

    Pure / unit-testable in isolation.
    """
    force_resolution = args.force_resolution if args else False
    if force_resolution:
        return DisplayConfig.default_resolution()
    if monitor_w >= 3840 and monitor_h >= 2160:
        return 3840, 2160
    if monitor_w >= 2560 and monitor_h >= 1600:
        return 2560, 1600
    return int(monitor_w * 0.9), int(monitor_h * 0.9)


def bootstrap(args: argparse.Namespace | None = None) -> BootstrapResult:
    """Run the entire app initialisation sequence in deterministic order.

    Single linear function — no conditional branches that could re-order
    the six invariants documented at the top of this module. Returns a
    fully-wired `BootstrapResult` for `Game` to consume.
    """
    # Invariant 1: pygame.init() FIRST. All subsequent pygame calls
    # (display.Info, set_mode, font.init, pygame_gui.UIManager) require
    # the SDL subsystems to be live.
    pygame.init()

    # DI container. Must precede `get_default_registry_provider()` (which
    # reads module-level `_default_*` accessors populated by
    # `ApplicationContext.create_production()`).
    # Invariant 3.
    ctx = ApplicationContext.create_production()

    # Invariant 2: font subsystem initialised BEFORE any `get_font(...)`
    # call. MenuScene's constructor pulls fonts; constructed in
    # ScreenRouter — but our own three font handles below also require it.
    pygame.font.init()
    font_small = get_font(12)
    font_med = get_font(20)
    font_large = get_font(32)

    # Monitor detection + resolution selection.
    info = pygame.display.Info()
    width, height = _detect_resolution(args, info.current_w, info.current_h)

    # Surface acquisition. Reuse existing display surface if the host
    # already created one (test path). Otherwise create with RESIZABLE.
    if not pygame.display.get_surface():
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    else:
        screen = pygame.display.get_surface()

    pygame.display.set_caption(f"Starship Battles ({width}x{height})")

    clock = pygame.time.Clock()

    # Invariant 4: components + modifiers BEFORE ship-data. The ship loader
    # resolves component refs against the registry — a flipped order yields
    # silent ref misses.
    # PROJ-211: pass registry_provider explicitly (no fallback).
    provider = get_default_registry_provider()
    load_components(Paths.COMPONENTS_FILE, registry_provider=provider)
    load_modifiers(Paths.MODIFIERS_FILE, registry_provider=provider)

    # Hydrate the resources registry from the canonical ResourceCatalog.
    # PROJ-309 §6: ResourceCatalog.from_json() was called twice in the
    # original `app.py`; hold a single instance and reuse for both
    # registry hydration and `GameRegistries`.
    catalog = ResourceCatalog.from_json(Paths.RESOURCES_FILE)
    resources_registry = ctx.registry_manager.resources
    for defn in catalog.all_definitions():
        resources_registry[defn.id] = {
            'id': defn.id,
            'name': defn.name,
            'description': defn.description,
            'display_group': defn.display_group,
            'has_quality': defn.has_quality,
        }

    initialize_ship_data(Paths.ROOT_DIR, registry_provider=provider)

    # Build the GameRegistries DI container (PROJ-38 / PROJ-181). Reuses
    # the already-loaded catalog rather than calling `from_json()` again.
    registry_mgr = ctx.registry_manager
    registries = GameRegistries(
        components=registry_mgr.components,
        modifiers=registry_mgr.modifiers,
        vehicle_classes=registry_mgr.vehicle_classes,
        resources=registry_mgr.resources,
        resource_catalog=catalog,
    )

    # Invariant 5: sprites loaded AFTER registries (some sprite metadata
    # may resolve registry IDs) but BEFORE scene constructors (which build
    # rendering pipelines).
    sprite_mgr = get_default_sprite_manager()
    sprite_mgr.load_sprites(Paths.ROOT_DIR)

    # Centralised keybindings (PROJ-71).
    input_mapper = InputMapper()
    input_mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE, Paths.USER_KEYBINDINGS_FILE)

    return BootstrapResult(
        ctx=ctx,
        screen=screen,
        width=width,
        height=height,
        clock=clock,
        registries=registries,
        input_mapper=input_mapper,
        font_small=font_small,
        font_med=font_med,
        font_large=font_large,
    )
