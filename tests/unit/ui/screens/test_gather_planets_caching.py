"""PROJ-411 Task 1.6: per-turn cache for ``gather_planets`` and ``gather_stars``.

The galaxy is per-turn-static under current architecture, so walking it
once per turn per empire is enough. Both ``gather_planets`` and
``gather_stars`` accept an optional ``facade_state`` kwarg; when supplied,
the result is cached on ``FacadeSessionState`` and returned by identity
on subsequent calls within the same turn.

Without ``facade_state``, behaviour is unchanged (no caching).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.facade.slices._facade_state import FacadeSessionState
from game.ui.screens.planet_list_filters import gather_planets
from game.ui.screens.star_list_filters import gather_stars
from game.ui.screens.strategy_world_access import StrategyWorldAccess


def _world(session):
    # PROJ-477 Phase 4: gather_* take the scene.world live seam.
    return StrategyWorldAccess(lambda: session)


@pytest.fixture
def fake_state() -> FacadeSessionState:
    return FacadeSessionState(session=MagicMock())


# --------------------------------------------------------------------------
# gather_planets
# --------------------------------------------------------------------------

def test_gather_planets_second_call_returns_cached_list(
    smoke_turn1_scenario, fake_state: FacadeSessionState
) -> None:
    """Second call within the same turn returns the same list object."""
    session, galaxy, empires = smoke_turn1_scenario
    empire = empires[0]

    first = gather_planets(_world(session), empire, facade_state=fake_state)
    second = gather_planets(_world(session), empire, facade_state=fake_state)

    assert second is first, (
        "second gather_planets() within the same turn should return the "
        "cached list object, not a fresh galaxy walk."
    )


def test_gather_planets_cache_isolated_per_empire(
    smoke_turn1_scenario, fake_state: FacadeSessionState
) -> None:
    """Each empire gets its own cache slot."""
    session, galaxy, empires = smoke_turn1_scenario
    e0_planets = gather_planets(_world(session), empires[0], facade_state=fake_state)
    e1_planets = gather_planets(_world(session), empires[1], facade_state=fake_state)

    assert fake_state.planets_for_empire_cache[empires[0].id] is e0_planets
    assert fake_state.planets_for_empire_cache[empires[1].id] is e1_planets


def test_gather_planets_invalidate_all_drops_cache(
    smoke_turn1_scenario, fake_state: FacadeSessionState
) -> None:
    """``invalidate_all()`` clears the cache so the next call walks the galaxy."""
    session, galaxy, empires = smoke_turn1_scenario
    first = gather_planets(_world(session), empires[0], facade_state=fake_state)
    fake_state.invalidate_all()
    second = gather_planets(_world(session), empires[0], facade_state=fake_state)
    assert second is not first


def test_gather_planets_no_facade_state_is_uncached(
    smoke_turn1_scenario,
) -> None:
    """Legacy callers that omit ``facade_state`` get the original behaviour."""
    session, galaxy, empires = smoke_turn1_scenario
    first = gather_planets(_world(session), empires[0])
    second = gather_planets(_world(session), empires[0])
    assert second is not first


# --------------------------------------------------------------------------
# gather_stars
# --------------------------------------------------------------------------

def test_gather_stars_second_call_returns_cached_list(
    smoke_turn1_scenario, fake_state: FacadeSessionState
) -> None:
    """Second call within the same turn returns the same list object."""
    session, galaxy, empires = smoke_turn1_scenario
    first = gather_stars(_world(session), facade_state=fake_state)
    second = gather_stars(_world(session), facade_state=fake_state)
    assert second is first


def test_gather_stars_invalidate_all_drops_cache(
    smoke_turn1_scenario, fake_state: FacadeSessionState
) -> None:
    session, galaxy, empires = smoke_turn1_scenario
    first = gather_stars(_world(session), facade_state=fake_state)
    fake_state.invalidate_all()
    second = gather_stars(_world(session), facade_state=fake_state)
    assert second is not first


def test_gather_stars_no_facade_state_is_uncached(
    smoke_turn1_scenario,
) -> None:
    session, galaxy, empires = smoke_turn1_scenario
    first = gather_stars(_world(session))
    second = gather_stars(_world(session))
    assert second is not first
