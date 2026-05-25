"""Integration tests for the mode-scoped data lifecycle.

Pins the contract introduced to fix the Combat-Lab→New-Game registry-pollution
bug: data is loaded into the global registry when a mode is entered and cleared
when the mode is exited. The default game data path and the combat_lab data
path are treated symmetrically — no path is privileged. The same hook supports
future mod data paths.

Key invariants:
- `load_data_from_path(p)` hydrates components/modifiers/vehicle_classes/
  resources from `p` and records `p` as the registry's active data path.
- `unload_data()` clears the registry and forgets the active path.
- Both operations invalidate downstream module-level JSON caches.
- Switching paths fully refreshes contents (Combat Lab → stock restores
  the harvester components that combat_lab/data omits).
"""
from __future__ import annotations

import pytest

from game.core.paths import Paths


# The lifecycle tests do not want the autouse reset_game_state fixture's
# session-cache hydration to mask whether load_data_from_path actually
# populated the registry. Mark each test with @pytest.mark.use_custom_data
# so the fixture's "skip production hydration" branch runs.


@pytest.mark.use_custom_data
def test_load_data_from_path_populates_components_from_stock():
    """Stock path populates the global registry."""
    from game.data_loader import load_data_from_path, unload_data
    from game.core.registry import get_default_registry_manager

    mgr = get_default_registry_manager()
    assert mgr is not None
    try:
        load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
        assert len(mgr.components) > 0
        assert "metal_harvester" in mgr.components, (
            "Stock components.json must define metal_harvester; "
            "this is the canary that the harvest bug is fixed."
        )
        assert mgr.active_data_path == Paths.DEFAULT_GAME_DATA_DIR
    finally:
        unload_data()


@pytest.mark.use_custom_data
def test_load_data_from_path_populates_components_from_combat_lab():
    """Combat-Lab path populates the global registry with test fixtures."""
    from game.data_loader import load_data_from_path, unload_data
    from game.core.registry import get_default_registry_manager

    mgr = get_default_registry_manager()
    try:
        load_data_from_path(Paths.COMBAT_LAB_DATA_DIR)
        assert len(mgr.components) > 0
        # combat_lab/data/components.json contains only test_* fixtures —
        # the asymmetry that made the bug visible.
        assert "metal_harvester" not in mgr.components
        assert any(k.startswith("test_") for k in mgr.components)
        assert mgr.active_data_path == Paths.COMBAT_LAB_DATA_DIR
    finally:
        unload_data()


@pytest.mark.use_custom_data
def test_unload_data_clears_registry_and_forgets_path():
    from game.data_loader import load_data_from_path, unload_data
    from game.core.registry import get_default_registry_manager

    mgr = get_default_registry_manager()
    load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
    assert mgr.active_data_path == Paths.DEFAULT_GAME_DATA_DIR
    assert len(mgr.components) > 0

    unload_data()
    assert mgr.active_data_path is None
    assert len(mgr.components) == 0
    assert len(mgr.modifiers) == 0
    assert len(mgr.vehicle_classes) == 0
    assert len(mgr.resources) == 0


@pytest.mark.use_custom_data
def test_combat_lab_then_stock_restores_harvesters():
    """Regression test for the original bug.

    Sequence:
      1. Run a Combat Lab scenario (loads combat_lab/data/, no harvesters).
      2. Exit Combat Lab (unload).
      3. Start a new game (loads stock data/).
      4. Harvester components must be present so colony harvest can succeed.
    """
    from game.data_loader import load_data_from_path, unload_data
    from game.core.registry import get_default_registry_manager

    mgr = get_default_registry_manager()
    try:
        # 1. Combat Lab loads its data set.
        load_data_from_path(Paths.COMBAT_LAB_DATA_DIR)
        assert "metal_harvester" not in mgr.components

        # 2. Exit Combat Lab.
        unload_data()
        assert mgr.active_data_path is None

        # 3. New Game loads stock data.
        load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)

        # 4. Harvester components MUST be present.
        assert "metal_harvester" in mgr.components, (
            "Combat Lab data pollution bug: harvester components missing "
            "after returning to stock data."
        )
    finally:
        unload_data()


@pytest.mark.use_custom_data
def test_load_data_invalidates_production_rates_cache():
    """The module-level _production_rates_cache must reset on data-load."""
    from game.data_loader import load_data_from_path, unload_data
    from game.strategy.data import build_queue_source

    # Prime the cache via the public accessor.
    load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
    try:
        build_queue_source.get_default_production_rates("planetary_yard")
        assert build_queue_source._production_rates_cache is not None

        # A second load should invalidate the cache.
        load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
        assert build_queue_source._production_rates_cache is None
    finally:
        unload_data()


@pytest.mark.use_custom_data
def test_unload_data_invalidates_production_rates_cache():
    from game.data_loader import load_data_from_path, unload_data
    from game.strategy.data import build_queue_source

    load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
    build_queue_source.get_default_production_rates("planetary_yard")
    assert build_queue_source._production_rates_cache is not None

    unload_data()
    assert build_queue_source._production_rates_cache is None


@pytest.mark.use_custom_data
def test_register_data_cache_invalidator_runs_on_load():
    """Custom invalidators registered via the public hook fire on load."""
    from game import data_loader
    from game.data_loader import (
        load_data_from_path,
        register_data_cache_invalidator,
        unload_data,
    )

    call_count = {"n": 0}

    def invalidator() -> None:
        call_count["n"] += 1

    register_data_cache_invalidator(invalidator)
    try:
        load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
        assert call_count["n"] >= 1
        unload_data()
        assert call_count["n"] >= 2
    finally:
        # Remove just our custom invalidator — leave production ones
        # registered by other module imports intact for sibling tests.
        try:
            data_loader._cache_invalidators.remove(invalidator)
        except ValueError:
            pass
        unload_data()


@pytest.mark.use_custom_data
def test_default_paths_resolve_to_existing_directories():
    """Sanity check: the path constants point at real directories."""
    import os

    assert os.path.isdir(Paths.DEFAULT_GAME_DATA_DIR)
    assert os.path.isdir(Paths.COMBAT_LAB_DATA_DIR)
