"""PROJ-411 FacadeSessionState per-turn cache fields.

Asserts that the four caches introduced by Phase 1 Tasks 1.5-1.8 exist
on `FacadeSessionState`, start empty, and are cleared by
`invalidate_all()`.

The four caches are:

* ``designs_by_empire`` — Task 1.5 DesignLibrary scan cache.
* ``planets_for_empire_cache`` — Task 1.6 ``gather_planets`` cache.
* ``stars_cache_new`` — Task 1.6 ``gather_stars`` cache. Named with
  the ``_new`` suffix because the existing ``all_stars_cache`` field
  holds the *DTO list* (StarInfo objects); this new cache holds the
  *raw* star list returned by ``gather_stars(galaxy)``.
* ``empire_economy_snapshot`` — Task 1.7 ``EmpireEconomyService`` cache.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.facade.slices._facade_state import FacadeSessionState


@pytest.fixture
def state() -> FacadeSessionState:
    """Minimal FacadeSessionState bound to a mock session."""
    return FacadeSessionState(session=MagicMock())


def test_designs_by_empire_starts_empty_dict(state: FacadeSessionState) -> None:
    """designs_by_empire field exists and starts as an empty dict."""
    assert state.designs_by_empire == {}


def test_planets_for_empire_cache_starts_empty_dict(state: FacadeSessionState) -> None:
    assert state.planets_for_empire_cache == {}


def test_stars_cache_new_starts_none(state: FacadeSessionState) -> None:
    assert state.stars_cache_new is None


def test_empire_economy_snapshot_starts_empty_dict(state: FacadeSessionState) -> None:
    assert state.empire_economy_snapshot == {}


def test_invalidate_all_clears_designs_by_empire(state: FacadeSessionState) -> None:
    state.designs_by_empire = {0: ["fake design metadata"]}
    state.invalidate_all()
    assert state.designs_by_empire == {}


def test_invalidate_all_clears_planets_for_empire_cache(state: FacadeSessionState) -> None:
    state.planets_for_empire_cache = {0: ["fake planet"]}
    state.invalidate_all()
    assert state.planets_for_empire_cache == {}


def test_invalidate_all_clears_stars_cache_new(state: FacadeSessionState) -> None:
    state.stars_cache_new = ["fake star"]
    state.invalidate_all()
    assert state.stars_cache_new is None


def test_invalidate_all_clears_empire_economy_snapshot(state: FacadeSessionState) -> None:
    state.empire_economy_snapshot = {0: "fake snapshot"}
    state.invalidate_all()
    assert state.empire_economy_snapshot == {}


def test_invalidate_all_preserves_pre_proj411_caches_behavior(
    state: FacadeSessionState,
) -> None:
    """Regression: invalidate_all still clears the original 3 caches
    (planet_index, all_stars_cache, fleets_by_hex_cache).

    Guard against accidentally dropping the existing clears when adding
    the new ones.
    """
    state.planet_index = {1: "fake"}
    state.all_stars_cache = ["fake"]
    state.fleets_by_hex_cache = {(0, 0): []}
    state.invalidate_all()
    assert state.planet_index is None
    assert state.all_stars_cache is None
    assert state.fleets_by_hex_cache is None
