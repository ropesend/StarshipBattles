"""Tests for the shared lazy registries cache helper (PROJ-420).

Covers the single source of truth for the lazy-init ``GameRegistries``
container that wraps ``get_default_registry_provider()``. Three modules in
``game/ui/`` previously each owned a private copy of the same pattern;
PROJ-420 consolidates them through this helper.
"""
from __future__ import annotations

import pytest

from game.core.registry import (
    GameRegistries,
    RegistryManager,
    clear_registry,
    set_default_registry_manager,
)


@pytest.fixture(autouse=True)
def _reset_cache_between_tests():
    """Each test starts and ends with a cleared cache."""
    from game.core import registry_cache
    registry_cache.reset_cached_registries()
    yield
    registry_cache.reset_cached_registries()


class TestGetCachedRegistries:
    """Behaviour of get_cached_registries()."""

    def test_returns_game_registries_instance(self):
        from game.core.registry_cache import get_cached_registries

        result = get_cached_registries()

        assert isinstance(result, GameRegistries)

    def test_caches_between_calls(self):
        """Second call returns the same object (single source of truth)."""
        from game.core.registry_cache import get_cached_registries

        first = get_cached_registries()
        second = get_cached_registries()

        assert first is second

    def test_wraps_default_registry_provider(self):
        """Cached registries delegate to the default registry provider."""
        from game.core.registry_cache import get_cached_registries
        from game.core.registry import get_default_registry_provider

        registries = get_cached_registries()
        provider = get_default_registry_provider()

        # Identity check on the underlying dicts — the helper must not
        # deep-copy; the dicts are shared with the provider so registry
        # hydration (which updates dicts in-place) is visible.
        assert registries.components is provider.get_components()
        assert registries.modifiers is provider.get_modifiers()
        assert registries.vehicle_classes is provider.get_vehicle_classes()
        assert registries.resources is provider.get_resources()


class TestResetCachedRegistries:
    """Behaviour of reset_cached_registries()."""

    def test_reset_forces_fresh_instance(self):
        """After reset, get_cached_registries() returns a new instance."""
        from game.core.registry_cache import (
            get_cached_registries,
            reset_cached_registries,
        )

        first = get_cached_registries()
        reset_cached_registries()
        second = get_cached_registries()

        assert first is not second

    def test_reset_is_idempotent(self):
        """Calling reset twice in a row is a no-op on the second call."""
        from game.core.registry_cache import (
            get_cached_registries,
            reset_cached_registries,
        )

        get_cached_registries()
        reset_cached_registries()
        reset_cached_registries()  # must not raise
        # Cache is empty — next access rebuilds.
        rebuilt = get_cached_registries()
        assert isinstance(rebuilt, GameRegistries)


class TestRegistryInvalidationHooks:
    """set_default_registry_manager() and clear_registry() must invalidate the cache."""

    def test_set_default_registry_manager_invalidates_cache(self):
        """Swapping the manager must clear the cached GameRegistries.

        Without this, the cache would keep references to dicts from the
        previous manager and miss data hydrated into the new manager.
        """
        from game.core.registry_cache import get_cached_registries

        before = get_cached_registries()

        # Swap in a fresh RegistryManager (mimics conftest.py reset_game_state).
        set_default_registry_manager(RegistryManager())

        after = get_cached_registries()
        assert before is not after

    def test_clear_registry_invalidates_cache(self):
        """clear_registry() must drop the cached GameRegistries.

        Even though the manager identity is preserved, the cached
        GameRegistries dataclass instance is frozen — its
        ``resource_catalog`` field may have been set by ``__post_init__``
        from stale data. After clear, callers should see a fresh
        snapshot.
        """
        from game.core.registry_cache import get_cached_registries

        before = get_cached_registries()
        clear_registry()
        after = get_cached_registries()

        assert before is not after
