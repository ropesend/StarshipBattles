"""PROJ-372 Phase 0: tests for the habitability-service accessors on
``game.context``.

We exercise the get/set roundtrip and the None-fallback contract that
Phase 2 wiring depends on.
"""
from __future__ import annotations

import pytest

from game import context as ctx_module
from game.context import (
    get_default_planet_habitability_service,
    set_default_planet_habitability_service,
)
from game.strategy.data.galaxy_protocols import IHabitabilityCalculator


@pytest.fixture(autouse=True)
def _reset_habitability_service():
    """Snapshot+restore the module-level slot so tests don't leak state."""
    original = ctx_module._default_planet_habitability_service
    yield
    ctx_module._default_planet_habitability_service = original


def test_default_returns_none_at_phase_0() -> None:
    set_default_planet_habitability_service(None)
    assert get_default_planet_habitability_service() is None


def test_set_then_get_roundtrip() -> None:
    class _Stub:
        def get_cached(self, planet, race_registry, turn: int) -> float:
            return 0.42

    stub = _Stub()
    set_default_planet_habitability_service(stub)
    retrieved = get_default_planet_habitability_service()
    assert retrieved is stub
    assert isinstance(retrieved, IHabitabilityCalculator)
    assert retrieved.get_cached(None, None, 0) == 0.42


def test_clear_via_none() -> None:
    class _Stub:
        def get_cached(self, planet, race_registry, turn: int) -> float:
            return 1.0

    set_default_planet_habitability_service(_Stub())
    assert get_default_planet_habitability_service() is not None
    set_default_planet_habitability_service(None)
    assert get_default_planet_habitability_service() is None
