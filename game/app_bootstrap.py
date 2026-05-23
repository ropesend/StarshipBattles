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
5. `ensure_component_derivatives()` BEFORE `SpriteManager.load_sprites` (the
   manager reads PNGs derived in this step), and the latter AFTER registries
   but BEFORE scene constructors.
6. `MenuScene` constructor BEFORE any overlay-dialog code path. (Scenes are
   constructed by `ScreenRouter` after `bootstrap()` returns; the rule is
   thereby enforced by composition order in `Game.__init__`.)
"""
from __future__ import annotations

import argparse
import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterator

import pygame

from game.assets.component_derivatives import ensure_component_derivatives
from game.context import ApplicationContext
from game.core.config import DisplayConfig
from game.core.paths import Paths
from game.core.registry import GameRegistries, get_default_registry_provider
from game.core.resources import ResourceCatalog
from game.simulation.components.component import load_components, load_modifiers
from game.simulation.entities.ship_loader import initialize_ship_data
from game.ui.fonts import get_font
from game.ui.services.input_mapper import InputMapper

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.strategy.services.replay_store import ReplayStore
    from game.strategy.services.replay_verification_coordinator import (
        ReplayVerificationCoordinator,
    )

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
    # PROJ-366 Phase 2: replay sink + verification coordinator. Forward-string
    # types so module-level imports stay minimal — concrete imports live
    # inside `bootstrap()` per the existing late-import pattern.
    replay_store: "ReplayStore"
    replay_verification_coordinator: "ReplayVerificationCoordinator"


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


@contextmanager
def _timed_phase(name: str, profiler: Any) -> Iterator[None]:
    """Time a bootstrap sub-phase, record into profiler, log a `[startup]` line.

    FEAT-22: bypasses `Profiler.is_active()` gating because bootstrap timing
    is unconditional — we want diagnostic visibility every launch, even when
    the on-screen profiler HUD is off.
    """
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = time.perf_counter() - t0
        profiler.records.append({
            "name": f"startup: {name}",
            "duration_ms": dt * 1000.0,
            "timestamp": time.time(),
            "metadata": {},
        })
        logger.info(f"[startup] {name}: {dt:.2f}s")


def bootstrap(args: argparse.Namespace | None = None) -> BootstrapResult:
    """Run the entire app initialisation sequence in deterministic order.

    Single linear function — no conditional branches that could re-order
    the six invariants documented at the top of this module. Returns a
    fully-wired `BootstrapResult` for `Game` to consume.

    FEAT-22: instruments 14 sub-phases. Each emits a `[startup] <name>: X.XXs`
    log line and an entry in `ctx.profiler.records`. Timings are flushed via
    `ctx.profiler.save_history()` before returning so a crash mid-game does
    not lose launch diagnostics. A final `[startup] total bootstrap: X.XXs`
    line summarises wall-clock cost.
    """
    t_total_start = time.perf_counter()

    # The first two phases run BEFORE the profiler exists (pygame.init runs
    # before ApplicationContext, and create_production() *constructs* the
    # profiler). Time them with raw perf_counter and back-fill the records
    # into the real profiler once it's available.
    t_pygame_init = time.perf_counter()
    pygame.init()
    dt_pygame_init = time.perf_counter() - t_pygame_init
    logger.info(f"[startup] pygame.init: {dt_pygame_init:.2f}s")

    # Invariant 3: ApplicationContext before any registry provider lookup.
    t_ctx = time.perf_counter()
    ctx = ApplicationContext.create_production()
    dt_ctx = time.perf_counter() - t_ctx
    logger.info(f"[startup] ctx.create_production: {dt_ctx:.2f}s")

    # Back-fill the two pre-profiler timings into the real profiler.
    now = time.time()
    ctx.profiler.records.append({
        "name": "startup: pygame.init",
        "duration_ms": dt_pygame_init * 1000.0,
        "timestamp": now,
        "metadata": {},
    })
    ctx.profiler.records.append({
        "name": "startup: ctx.create_production",
        "duration_ms": dt_ctx * 1000.0,
        "timestamp": now,
        "metadata": {},
    })

    # Invariant 2: font subsystem initialised BEFORE any `get_font(...)`
    # call. MenuScene's constructor pulls fonts; constructed in
    # ScreenRouter — but our own three font handles below also require it.
    with _timed_phase("font.init", ctx.profiler):
        pygame.font.init()
    with _timed_phase("font.preload", ctx.profiler):
        font_small = get_font(12)
        font_med = get_font(20)
        font_large = get_font(32)

    # Monitor detection + resolution selection.
    with _timed_phase("display.detect_resolution", ctx.profiler):
        info = pygame.display.Info()
        width, height = _detect_resolution(args, info.current_w, info.current_h)

    # Surface acquisition. Reuse existing display surface if the host
    # already created one (test path). Otherwise create with RESIZABLE.
    with _timed_phase("display.set_mode", ctx.profiler):
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
    with _timed_phase("registry.load_components", ctx.profiler):
        load_components(Paths.COMPONENTS_FILE, registry_provider=provider)
    with _timed_phase("registry.load_modifiers", ctx.profiler):
        load_modifiers(Paths.MODIFIERS_FILE, registry_provider=provider)

    # Hydrate the resources registry from the canonical ResourceCatalog.
    # PROJ-309 §6: ResourceCatalog.from_json() was called twice in the
    # original `app.py`; hold a single instance and reuse for both
    # registry hydration and `GameRegistries`.
    with _timed_phase("registry.load_resources", ctx.profiler):
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

    with _timed_phase("registry.initialize_ship_data", ctx.profiler):
        initialize_ship_data(Paths.ROOT_DIR, registry_provider=provider)

    # Build the GameRegistries DI container (PROJ-38 / PROJ-181). Reuses
    # the already-loaded catalog rather than calling `from_json()` again.
    with _timed_phase("registry.build_game_registries", ctx.profiler):
        registry_mgr = ctx.registry_manager
        registries = GameRegistries(
            components=registry_mgr.components,
            modifiers=registry_mgr.modifiers,
            vehicle_classes=registry_mgr.vehicle_classes,
            resources=registry_mgr.resources,
            resource_catalog=catalog,
        )

    # Generated component resolutions are derived from tracked 1024px masters.
    # Must precede sprite loading because the sprite manager reads the
    # files generated by this step.
    with _timed_phase("assets.ensure_component_derivatives", ctx.profiler):
        ensure_component_derivatives()

    # Invariant 5: sprites loaded AFTER registries (some sprite metadata
    # may resolve registry IDs) and AFTER component-derivative generation
    # (the manager reads the just-derived PNGs), but BEFORE scene
    # constructors (which build rendering pipelines).
    with _timed_phase("assets.load_sprites", ctx.profiler):
        sprite_mgr = ctx.sprite_manager
        sprite_mgr.load_sprites(Paths.ROOT_DIR)

    # Centralised keybindings (PROJ-71).
    with _timed_phase("input.load_keybindings", ctx.profiler):
        input_mapper = InputMapper()
        input_mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE, Paths.USER_KEYBINDINGS_FILE)

    # PROJ-366 Phase 1: construct the replay store and register it as the
    # process-wide capture sink + save-lifecycle store. The same
    # `replay_settings` instance is reused by Phase 2's coordinator so a
    # single file read serves both consumers (per r001 shared-settings
    # delta). Lazy imports match the existing late-import pattern in this
    # module.
    with _timed_phase("replay.construct_store", ctx.profiler):
        from game.simulation.replay.replay_capture import set_default_capture_sink
        from game.strategy.services.replay_store import ReplayStore, load_replay_settings
        from game.strategy.systems.save_game_service import SaveGameService

        replay_settings = load_replay_settings()
        replay_store = ReplayStore(settings=replay_settings)
        set_default_capture_sink(replay_store)
        # PROJ-427 Phase 5: replay-store wiring is instance-owned by the
        # SaveGameService default singleton (module-globals removed).
        SaveGameService.default().set_replay_store(replay_store)

    # PROJ-366 Phase 2: construct the verification coordinator with the
    # Combat Lab fallback adapter and start its worker thread.
    #
    # The coordinator's `fallback_ship_builder` parameter expects shape
    # `(ShipSpec, int) -> Ship`. `combat_lab.design_loader.load_combat_lab_design`
    # has shape `(design_id: str) -> Dict` — we wrap it via
    # `DesignOnlyMaterializer` (which Combat Lab itself uses for tests) to
    # bridge the signatures. Per Codex r001 (CRIT 2): the import path is
    # `combat_lab.design_loader`, not `game.combat_lab.design_loader`.
    with _timed_phase("replay.start_coordinator", ctx.profiler):
        from combat_lab.design_loader import load_combat_lab_design
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.services.ship_materializer import DesignOnlyMaterializer
        from game.strategy.services.replay_verification_coordinator import (
            ReplayVerificationCoordinator,
        )

        _cl_materializer = DesignOnlyMaterializer(design_loader=load_combat_lab_design)

        def _replay_combat_lab_fallback(ship_spec, team_id) -> "Ship":
            return _cl_materializer.materialize(ship_spec, team_id, registries)

        replay_verification_coordinator = ReplayVerificationCoordinator(
            replay_store=replay_store,
            ai_factory=AIControllerFactory(),
            registry_provider=provider,
            settings=replay_settings,
            fallback_ship_builder=_replay_combat_lab_fallback,
        )
        replay_verification_coordinator.start()

    dt_total = time.perf_counter() - t_total_start
    logger.info(f"[startup] total bootstrap: {dt_total:.2f}s")

    # Eager flush so launch diagnostics survive an in-game crash.
    ctx.profiler.save_history()

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
        replay_store=replay_store,
        replay_verification_coordinator=replay_verification_coordinator,
    )


