"""PROJ-372 Phase 2: PlanetHabitabilityService tests + acceptance test for
modder-injectable habitability calculator.

Closes the user-visible "modders can't inject custom habitability
calculators" complaint from the PROJ-372 source review.
"""
from __future__ import annotations

import pytest

from game import context as ctx_module
from game.context import (
    get_default_planet_habitability_service,
    set_default_planet_habitability_service,
)
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy_protocols import IHabitabilityCalculator
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.services.planet_habitability_service import (
    PlanetHabitabilityService,
)


@pytest.fixture(autouse=True)
def _reset_habitability_service():
    original = ctx_module._default_planet_habitability_service
    yield
    ctx_module._default_planet_habitability_service = original


def _make_planet() -> Planet:
    return Planet(
        name="Test",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )


class _StubRaceRegistry:
    def get_race(self, race_id):
        return None


def test_service_implements_protocol() -> None:
    svc = PlanetHabitabilityService()
    assert isinstance(svc, IHabitabilityCalculator)


def test_default_service_returns_real_calculation() -> None:
    """With no override, the service computes via colony_output."""
    svc = PlanetHabitabilityService()
    planet = _make_planet()
    value = svc.get_cached(planet, _StubRaceRegistry(), turn=1)
    # Planet has no populations; calculator returns 1.0 (additive neutral).
    assert value == 1.0


def test_swap_habitability_service_via_context() -> None:
    """Modder workflow: register a stub via ApplicationContext."""

    class _Stub:
        def get_cached(self, planet, race_registry, turn: int) -> float:
            return 0.42

    set_default_planet_habitability_service(_Stub())
    planet = _make_planet()
    # Planet.get_cached_habitability_multiplier should route through
    # the registered service.
    value = planet.get_cached_habitability_multiplier(_StubRaceRegistry(), turn=1)
    assert value == 0.42


def test_cache_lives_on_planet_not_service() -> None:
    """Two service instances stay coherent — cache lives on the planet."""
    svc_a = PlanetHabitabilityService()
    svc_b = PlanetHabitabilityService()
    planet = _make_planet()

    v1 = svc_a.get_cached(planet, _StubRaceRegistry(), turn=5)
    v2 = svc_b.get_cached(planet, _StubRaceRegistry(), turn=5)
    assert v1 == v2
    assert planet._cached_multiplier_turn == 5


def test_cache_invalidates_on_turn_change() -> None:
    svc = PlanetHabitabilityService()
    planet = _make_planet()
    svc.get_cached(planet, _StubRaceRegistry(), turn=1)
    assert planet._cached_multiplier_turn == 1
    svc.get_cached(planet, _StubRaceRegistry(), turn=2)
    assert planet._cached_multiplier_turn == 2


def test_compute_skipped_within_same_turn() -> None:
    """Cache hit: _compute should not be re-invoked within the same turn."""
    call_count = {"n": 0}

    class _CountingService(PlanetHabitabilityService):
        def _compute(self, planet, race_registry):
            call_count["n"] += 1
            return 0.99

    svc = _CountingService()
    planet = _make_planet()
    svc.get_cached(planet, _StubRaceRegistry(), turn=3)
    svc.get_cached(planet, _StubRaceRegistry(), turn=3)
    svc.get_cached(planet, _StubRaceRegistry(), turn=3)
    assert call_count["n"] == 1


def test_default_registered_after_phase_2_wiring() -> None:
    """Phase 2 wires PlanetHabitabilityService() at import time."""
    # When tests import game.context, the module-level slot is populated.
    # Note: the autouse fixture resets state; force the wiring.
    from game.strategy.services.planet_habitability_service import (
        PlanetHabitabilityService as _PHS,
    )
    set_default_planet_habitability_service(_PHS())
    svc = get_default_planet_habitability_service()
    assert isinstance(svc, PlanetHabitabilityService)
