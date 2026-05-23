"""PROJ-411 Task 1.7: EmpireEconomyService.get_snapshot() per-turn cache.

When ``facade_state`` is supplied, ``get_snapshot()`` caches its result
in ``facade_state.empire_economy_snapshot[empire.id]`` and reuses it
across calls within the same turn. Cleared by
``FacadeSessionState.invalidate_all()`` at each turn boundary.

Without ``facade_state``, behaviour is unchanged (no caching) so engine-
side and test callers are unaffected.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.facade.slices._facade_state import FacadeSessionState


@pytest.fixture
def fake_state() -> FacadeSessionState:
    return FacadeSessionState(session=MagicMock())


def _build_service(fresh_registries):
    """Helper to build an EmpireEconomyService with minimal deps."""
    from game.strategy.services.empire_economy_service import EmpireEconomyService

    return EmpireEconomyService(registries=fresh_registries)


@pytest.fixture
def economy_test_env(smoke_turn1_scenario, fresh_registries):
    """PROJ-495 T4.3: bundle the ``smoke_turn1_scenario`` unpack +
    ``_build_service(fresh_registries)`` into a single fixture.

    Returns a 4-tuple ``(service, session, galaxy, empires)`` that the four
    cache-behaviour tests below need verbatim.
    """
    session, galaxy, empires = smoke_turn1_scenario
    service = _build_service(fresh_registries)
    return service, session, galaxy, empires


def test_get_snapshot_second_call_returns_cached(
    economy_test_env, fake_state: FacadeSessionState
) -> None:
    """Second ``get_snapshot()`` within the same turn returns the same object."""
    service, _session, _galaxy, empires = economy_test_env

    first = service.get_snapshot(empires[0], facade_state=fake_state)
    second = service.get_snapshot(empires[0], facade_state=fake_state)
    assert second is first, (
        "second get_snapshot() within the same turn should return the cached "
        "snapshot object."
    )


def test_get_snapshot_cache_isolated_per_empire(
    economy_test_env, fake_state: FacadeSessionState
) -> None:
    """Each empire gets its own cache slot."""
    service, _session, _galaxy, empires = economy_test_env

    snap0 = service.get_snapshot(empires[0], facade_state=fake_state)
    snap1 = service.get_snapshot(empires[1], facade_state=fake_state)

    assert fake_state.empire_economy_snapshot[empires[0].id] is snap0
    assert fake_state.empire_economy_snapshot[empires[1].id] is snap1


def test_get_snapshot_invalidate_all_drops_cache(
    economy_test_env, fake_state: FacadeSessionState
) -> None:
    """``invalidate_all()`` clears the cache so the next call rebuilds."""
    service, _session, _galaxy, empires = economy_test_env

    first = service.get_snapshot(empires[0], facade_state=fake_state)
    fake_state.invalidate_all()
    second = service.get_snapshot(empires[0], facade_state=fake_state)
    assert second is not first


def test_get_snapshot_no_facade_state_is_uncached(economy_test_env) -> None:
    """Legacy callers without ``facade_state`` rebuild every call."""
    service, _session, _galaxy, empires = economy_test_env

    first = service.get_snapshot(empires[0])
    second = service.get_snapshot(empires[0])
    assert second is not first
