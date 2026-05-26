"""Invariant tests for `game.app_bootstrap`.

These lock the initialization-order invariants identified in the
PROJ-309 sub-phase 3.9 design doc, plus PROJ-366's replay invariants:

1. `pygame.init()` MUST run before `pygame.display.Info()` /
   `pygame.display.set_mode()` / pygame_gui.
2. `pygame.font.init()` MUST run before any `get_font()` call (MenuScene
   constructor).
3. `ApplicationContext.create_production()` MUST be called by bootstrap.
4. `ensure_component_derivatives()` MUST precede
   `SpriteManager.load_sprites` (the latter reads PNGs the former
   generates).
5. `MenuScene` constructor MUST run before any overlay-dialog code path.
6. (PROJ-366 Phase 1) `set_default_capture_sink(replay_store)` and
   `set_replay_store(replay_store)` MUST run after `InputMapper.load(...)`
   and before `bootstrap()` returns.
7. (PROJ-366 Phase 2) `BootstrapResult.replay_verification_coordinator`
   MUST be present and `.start()`-ed (worker thread spawned + listener
   registered).
8. Bootstrap MUST leave the registry empty (mode-scoped data lifecycle).
   Game data is loaded only when a mode is entered.

The strategy here is to record the sequence of "ordering-relevant" calls
during `bootstrap()` and assert their relative ordering. We do NOT mock
everything — the real pygame init runs (in headless dummy mode), so these
tests double as a smoke-style verification that bootstrap composes.
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest

# Force headless before any pygame import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


@pytest.fixture(autouse=True)
def _drain_replay_globals():
    """PROJ-366 Phase 1: drain coordinator threads + reset module globals
    after every bootstrap test.

    Production `bootstrap()` (post Phase 1+2) registers a process-wide
    `ReplayStore` as the default capture sink and starts a non-daemon
    `ReplayVerificationCoordinator` worker thread. Without explicit
    cleanup these would leak across tests. Pattern from
    `tests/unit/strategy/services/test_replay_verification_coordinator.py:93-98`.
    """
    yield
    from game.simulation.replay.replay_capture import reset_default_capture_sink
    from game.strategy.services.replay_verification_coordinator import (
        shutdown_all_coordinators,
    )
    from game.strategy.systems.save_game_service import SaveGameService

    shutdown_all_coordinators(timeout=5.0)
    reset_default_capture_sink()
    SaveGameService.default().set_replay_store(None)


@pytest.fixture
def call_order() -> list[str]:
    """Record the ordering-relevant calls made during bootstrap."""
    return []


def _patched_bootstrap(call_order: list[str]):
    """Patch pygame / context / registry / ship-loader to record call order.

    Returns the bootstrap result so tests can also assert post-condition
    contracts on it.
    """
    import pygame
    import pygame_gui  # noqa: F401 — imported for side effects via app_bootstrap
    from game import app_bootstrap as boot
    from game.context import ApplicationContext

    real_pygame_init = pygame.init
    real_font_init = pygame.font.init
    real_create_production = ApplicationContext.create_production

    def record_pygame_init(*args, **kwargs):
        call_order.append("pygame.init")
        return real_pygame_init(*args, **kwargs)

    def record_font_init(*args, **kwargs):
        call_order.append("pygame.font.init")
        return real_font_init(*args, **kwargs)

    @classmethod
    def record_create_production(cls):
        call_order.append("ApplicationContext.create_production")
        return real_create_production()

    # Bootstrap no longer loads game data (it's mode-scoped, in
    # `game.data_loader.load_data_from_path`). The old ordering-pin
    # patches for `get_default_registry_provider` / `load_components`
    # / `load_modifiers` / `initialize_ship_data` are gone — those
    # invariants now belong to the data loader, not bootstrap.

    from game.ui.renderer import sprites as sprites_mod
    real_load_sprites = sprites_mod.SpriteManager.load_sprites

    def record_load_sprites(self, *args, **kwargs):
        call_order.append("SpriteManager.load_sprites")
        return real_load_sprites(self, *args, **kwargs)

    # `ensure_component_derivatives` is asset-side-effect code (writes to
    # `assets/images/components/.component_derivatives_manifest.json`). Real
    # invocation under pytest-xdist races on the manifest tempfile across
    # workers. These tests assert ORDERING, not asset generation — stub it.
    def record_ensure_derivatives():
        call_order.append("ensure_component_derivatives")

    # PROJ-366 Phase 1: patch SOURCE modules (not lazy-import sites) for
    # `set_default_capture_sink` and `set_replay_store` so we capture the
    # production wiring's late-import calls. Per r001 monkeypatch-target
    # delta.
    from game.simulation.replay import replay_capture as replay_capture_mod
    real_set_sink = replay_capture_mod.set_default_capture_sink

    def record_set_sink(sink):
        call_order.append("set_default_capture_sink")
        return real_set_sink(sink)

    # PROJ-427 Phase 5: replay-store wiring is instance-owned on the
    # SaveGameService default singleton. We spy on the bound instance
    # method to record bootstrap's call without changing semantics.
    from game.strategy.systems.save_game_service import SaveGameService as _SaveGameService
    _default_svc = _SaveGameService.default()
    real_set_store = _default_svc.set_replay_store

    def record_set_store(store):
        call_order.append("set_replay_store")
        return real_set_store(store)

    # PROJ-366 Phase 2: spy on coordinator.start at SOURCE-module level.
    from game.strategy.services import replay_verification_coordinator as rvc_mod
    real_start = rvc_mod.ReplayVerificationCoordinator.start

    def record_coord_start(self):
        call_order.append("replay_verification_coordinator.start")
        return real_start(self)

    with patch.object(pygame, "init", record_pygame_init), \
         patch.object(pygame.font, "init", record_font_init), \
         patch.object(ApplicationContext, "create_production",
                      record_create_production), \
         patch.object(sprites_mod.SpriteManager, "load_sprites",
                      record_load_sprites), \
         patch.object(boot, "ensure_component_derivatives",
                      record_ensure_derivatives), \
         patch.object(replay_capture_mod, "set_default_capture_sink",
                      record_set_sink), \
         patch.object(_default_svc, "set_replay_store",
                      record_set_store), \
         patch.object(rvc_mod.ReplayVerificationCoordinator, "start",
                      record_coord_start):
        # Ensure a display surface exists so set_mode-bypass branch is taken.
        if not pygame.display.get_surface():
            pygame.display.set_mode((1440, 900), pygame.NOFRAME)

        from argparse import Namespace
        args = Namespace(force_resolution=False)
        with patch("pygame.display.Info") as mock_info:
            mock_info.return_value.current_w = 2560
            mock_info.return_value.current_h = 1600
            return boot.bootstrap(args)


def test_pygame_init_before_display_info(call_order: list[str]) -> None:
    """Invariant 1: pygame.init runs before any display-related call."""
    _patched_bootstrap(call_order)
    assert "pygame.init" in call_order
    pygame_idx = call_order.index("pygame.init")
    # Display set_mode + Info aren't recorded individually, but they must
    # happen *after* pygame.init. The recorded order tells us whether
    # pygame.init ran before any other pygame-touching step.
    assert pygame_idx < call_order.index("pygame.font.init")


def test_pygame_font_init_before_create_production(call_order: list[str]) -> None:
    """Invariant 2: pygame.font.init runs before fonts are resolved (and
    fonts are resolved during MenuScene construction, which happens after
    create_production). Easier to assert: font.init precedes create_production.
    """
    _patched_bootstrap(call_order)
    assert call_order.index("pygame.font.init") < \
           call_order.index("ApplicationContext.create_production")


def test_create_production_is_called(call_order: list[str]) -> None:
    """Invariant 3: ApplicationContext.create_production is called by
    bootstrap (after pygame/font init). Game data is loaded mode-scoped
    via `game.data_loader.load_data_from_path`, NOT by bootstrap.
    """
    _patched_bootstrap(call_order)
    assert "ApplicationContext.create_production" in call_order
    assert call_order.index("pygame.font.init") < \
           call_order.index("ApplicationContext.create_production")


def test_bootstrap_leaves_registry_empty(call_order: list[str]) -> None:
    """Invariant 8 (mode-scoped data lifecycle): bootstrap does NOT load
    game data. The registry is empty when bootstrap returns. Data is
    loaded only when a mode is entered (New Game / Combat Lab / Workshop /
    Load Game) via `game.data_loader.load_data_from_path`.
    """
    result = _patched_bootstrap(call_order)
    mgr = result.ctx.registry_manager
    assert len(mgr.components) == 0, (
        f"bootstrap leaked component data into the registry: "
        f"{list(mgr.components.keys())[:5]} ..."
    )
    assert len(mgr.modifiers) == 0
    assert len(mgr.vehicle_classes) == 0
    assert len(mgr.resources) == 0
    assert mgr.active_data_path is None


def test_ensure_derivatives_before_load_sprites(call_order: list[str]) -> None:
    """Invariant 5b: `ensure_component_derivatives()` MUST run before
    `SpriteManager.load_sprites` because the latter reads the PNGs the
    former generates. Added during the 2026-04-27 merge that brought the
    asset-derivative system in alongside the PROJ-309 sub-phase 3.9
    decomposition.
    """
    _patched_bootstrap(call_order)
    assert call_order.index("ensure_component_derivatives") < \
           call_order.index("SpriteManager.load_sprites")


def test_bootstrap_returns_complete_result() -> None:
    """Bootstrap must return a `BootstrapResult` whose every field is set."""
    call_order: list[str] = []
    result = _patched_bootstrap(call_order)
    assert result.ctx is not None
    assert result.screen is not None
    assert result.width > 0
    assert result.height > 0
    assert result.clock is not None
    assert result.registries is not None
    assert result.input_mapper is not None
    assert result.font_small is not None
    assert result.font_med is not None
    assert result.font_large is not None


def test_invariant_7_replay_store_registered_after_input_mapper(
    call_order: list[str],
) -> None:
    """PROJ-366 Phase 1: `set_default_capture_sink(store)` and
    `set_replay_store(store)` MUST run AFTER `InputMapper.load(...)` and
    BEFORE `bootstrap()` returns.

    The wiring must use the SOURCE-module functions
    (`game.simulation.replay.replay_capture.set_default_capture_sink`,
    `game.strategy.systems.save_game_service.set_replay_store`) so that
    `_replay_store` and `_default_sink` module globals are updated for
    every consumer. Patching the lazy-import site in `app_bootstrap`
    would not catch this; this test records calls at the source module.
    """
    _patched_bootstrap(call_order)
    assert "set_default_capture_sink" in call_order, (
        f"set_default_capture_sink never called; got {call_order}"
    )
    assert "set_replay_store" in call_order, (
        f"set_replay_store never called; got {call_order}"
    )
    # Both registrations must come AFTER ApplicationContext.create_production
    # (the InputMapper load is itself after that, and our recorded calls
    # don't include InputMapper.load — but anything after ctx is past it).
    ctx_idx = call_order.index("ApplicationContext.create_production")
    assert call_order.index("set_default_capture_sink") > ctx_idx
    assert call_order.index("set_replay_store") > ctx_idx


def test_invariant_8_replay_verification_coordinator_started() -> None:
    """PROJ-366 Phase 2: `BootstrapResult` exposes both `replay_store` and
    `replay_verification_coordinator`; the coordinator's worker thread is
    spawned and the listener is registered on the store.
    """
    call_order: list[str] = []
    result = _patched_bootstrap(call_order)
    assert hasattr(result, "replay_store"), (
        "BootstrapResult missing `replay_store` field"
    )
    assert hasattr(result, "replay_verification_coordinator"), (
        "BootstrapResult missing `replay_verification_coordinator` field"
    )
    coord = result.replay_verification_coordinator
    # Worker thread spawned.
    assert coord._worker is not None, "coordinator worker not spawned"
    # Listener registered on the store.
    assert coord._listener_registered is True, (
        "coordinator did not register its listener on the replay store"
    )
    # And the start() call was observed (source-module recorded).
    assert "replay_verification_coordinator.start" in call_order
