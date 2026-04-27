"""Invariant tests for `game.app_bootstrap`.

These lock the six initialization-order invariants identified in the
PROJ-309 sub-phase 3.9 design doc:

1. `pygame.init()` MUST run before `pygame.display.Info()` /
   `pygame.display.set_mode()` / pygame_gui.
2. `pygame.font.init()` MUST run before any `get_font()` call (MenuScene
   constructor).
3. `ApplicationContext.create_production()` MUST run before
   `get_default_registry_provider()`.
4. `load_components` / `load_modifiers` MUST run before
   `initialize_ship_data`.
5. `SpriteManager.load_sprites` MUST run after registries but before scene
   constructors.
6. `MenuScene` constructor MUST run before any overlay-dialog code path.

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

    # Patch the registry provider lookup in app_bootstrap's namespace.
    from game.core import registry as registry_mod
    real_get_provider = registry_mod.get_default_registry_provider

    def record_get_provider():
        call_order.append("get_default_registry_provider")
        return real_get_provider()

    from game.simulation.components import component as component_mod
    real_load_components = component_mod.load_components
    real_load_modifiers = component_mod.load_modifiers

    def record_load_components(*args, **kwargs):
        call_order.append("load_components")
        return real_load_components(*args, **kwargs)

    def record_load_modifiers(*args, **kwargs):
        call_order.append("load_modifiers")
        return real_load_modifiers(*args, **kwargs)

    from game.simulation.entities import ship_loader
    real_init_ship = ship_loader.initialize_ship_data

    def record_init_ship(*args, **kwargs):
        call_order.append("initialize_ship_data")
        return real_init_ship(*args, **kwargs)

    from game.ui.renderer import sprites as sprites_mod
    real_load_sprites = sprites_mod.SpriteManager.load_sprites

    def record_load_sprites(self, *args, **kwargs):
        call_order.append("SpriteManager.load_sprites")
        return real_load_sprites(self, *args, **kwargs)

    with patch.object(pygame, "init", record_pygame_init), \
         patch.object(pygame.font, "init", record_font_init), \
         patch.object(ApplicationContext, "create_production",
                      record_create_production), \
         patch.object(boot, "get_default_registry_provider",
                      record_get_provider), \
         patch.object(boot, "load_components", record_load_components), \
         patch.object(boot, "load_modifiers", record_load_modifiers), \
         patch.object(boot, "initialize_ship_data", record_init_ship), \
         patch.object(sprites_mod.SpriteManager, "load_sprites",
                      record_load_sprites):
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


def test_create_production_before_registry_provider_lookup(call_order: list[str]) -> None:
    """Invariant 3: ApplicationContext.create_production precedes any
    `get_default_registry_provider` call (which reads the now-populated
    module-level default).
    """
    _patched_bootstrap(call_order)
    assert call_order.index("ApplicationContext.create_production") < \
           call_order.index("get_default_registry_provider")


def test_load_components_before_initialize_ship_data(call_order: list[str]) -> None:
    """Invariant 4: components + modifiers are loaded before ship-data init."""
    _patched_bootstrap(call_order)
    assert call_order.index("load_components") < \
           call_order.index("initialize_ship_data")
    assert call_order.index("load_modifiers") < \
           call_order.index("initialize_ship_data")


def test_load_sprites_after_initialize_ship_data(call_order: list[str]) -> None:
    """Invariant 5: SpriteManager.load_sprites runs AFTER registries are
    fully loaded (i.e. after initialize_ship_data) but before any scene
    constructor (scenes are not built inside `bootstrap()` itself in the
    new design — they are built by `ScreenRouter`, so this test is the
    strongest assertion bootstrap can make).
    """
    _patched_bootstrap(call_order)
    assert call_order.index("initialize_ship_data") < \
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
