"""Shared lazy cache for the default ``GameRegistries`` snapshot.

PROJ-420: Three modules (``ship_io.py``, ``strategy_build_queue_manager.py``,
``setup_data_io.py``) previously each owned a private ``global`` lazy-init
of the same ``GameRegistries`` wrapper around
``get_default_registry_provider()``. This helper consolidates them.

Usage::

    from game.core.registry_cache import get_cached_registries

    registries = get_cached_registries()  # idempotent — same instance on repeat

Lifecycle::

    from game.core.registry_cache import reset_cached_registries

    reset_cached_registries()  # called by registry-manager swaps and test reset

Layer position: Core layer. Cannot import UI; consumers that need a
``ShipFactory`` construct it inline at the call site using the registries
returned from this module. This is intentional — the helper stays narrow
and direct-import only (no ``__init__`` re-export).

PROJ-258 (ApplicationContext) will eventually delete-and-replace all four
call sites; this helper is a focused consolidation step, not a transitional
API.
"""
from __future__ import annotations

from typing import Optional

from game.core.registry import (
    GameRegistries,
    get_default_registry_provider,
)


__all__ = ["get_cached_registries", "reset_cached_registries"]


_cached_registries: Optional[GameRegistries] = None


def get_cached_registries() -> GameRegistries:
    """Return the cached ``GameRegistries`` snapshot, building it on first call.

    The returned container shares dict references with
    ``get_default_registry_provider()`` so in-place hydration by the
    ``RegistryManager`` (the canonical post-PROJ-258 pattern) is visible
    to callers without rebuilding the cache.

    Returns:
        Cached ``GameRegistries`` instance (same object on every call until
        ``reset_cached_registries()`` is invoked).
    """
    global _cached_registries
    if _cached_registries is None:
        provider = get_default_registry_provider()
        _cached_registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
            resource_catalog=provider.get_resource_catalog(),
        )
    return _cached_registries


def reset_cached_registries() -> None:
    """Drop the cached snapshot so the next call rebuilds it.

    Called by:
        * ``set_default_registry_manager()`` — manager identity changed,
          dict refs the cache holds now point at the previous manager.
        * ``clear_registry()`` — the cached ``resource_catalog`` snapshot
          may be stale after a clear/reload cycle.
        * ``conftest.py::reset_game_state`` — test isolation.

    Idempotent — safe to call when the cache is already empty.
    """
    global _cached_registries
    _cached_registries = None
