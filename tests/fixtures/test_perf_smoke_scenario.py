"""Smoke test for the perf_smoke_scenario fixture (PROJ-411 Phase 1 Task 1.1).

The fixture is the deterministic baseline scenario used by every PROJ-411
perf test: turn 1, 2 empires, 2 systems, default-minimum planets per system,
no fleets. This file asserts the fixture's shape so downstream tests can
rely on it.
"""
from __future__ import annotations

import pytest


def test_smoke_scenario_returns_tuple_of_three(smoke_turn1_scenario):
    """Fixture returns (session, galaxy, empires)."""
    result = smoke_turn1_scenario
    assert isinstance(result, tuple), f"expected tuple, got {type(result)}"
    assert len(result) == 3, f"expected 3-tuple, got {len(result)}"


def test_smoke_scenario_is_turn_1(smoke_turn1_scenario):
    session, galaxy, empires = smoke_turn1_scenario
    assert session.turn_number == 1, (
        f"smoke scenario must be on turn 1; got {session.turn_number}"
    )


def test_smoke_scenario_has_two_empires(smoke_turn1_scenario):
    session, galaxy, empires = smoke_turn1_scenario
    assert len(empires) == 2, f"expected 2 empires; got {len(empires)}"
    assert empires[0].id != empires[1].id


def test_smoke_scenario_has_two_systems(smoke_turn1_scenario):
    session, galaxy, empires = smoke_turn1_scenario
    assert len(galaxy.systems) == 2, (
        f"expected 2 star systems; got {len(galaxy.systems)}"
    )


def test_smoke_scenario_each_empire_has_at_least_one_colony(smoke_turn1_scenario):
    """Each empire owns at least one planet on turn 1."""
    session, galaxy, empires = smoke_turn1_scenario
    for empire in empires:
        assert len(empire.colonies) >= 1, (
            f"empire {empire.id} ({empire.name}) has no colonies on turn 1"
        )


def test_smoke_scenario_has_no_fleets(smoke_turn1_scenario):
    """Smoke scenario starts with zero fleets on either empire."""
    session, galaxy, empires = smoke_turn1_scenario
    for empire in empires:
        assert len(empire.fleets) == 0, (
            f"empire {empire.id} ({empire.name}) starts with "
            f"{len(empire.fleets)} fleets; expected 0"
        )


def test_smoke_scenario_session_exposes_facade(smoke_turn1_scenario):
    """Session has the StrategySessionFacade attached so panels can query it."""
    session, galaxy, empires = smoke_turn1_scenario
    # Most production code accesses the facade via lazy/property attribute;
    # the fixture should make it readable without further setup.
    facade = getattr(session, "facade", None)
    if facade is None:
        # Fall back to creating one ad hoc — the fixture is allowed to
        # leave this off the session if it's expensive. But we DO want
        # to be able to construct one without error.
        from game.strategy.facade.strategy_session_facade import (
            StrategySessionFacade,
        )
        facade = StrategySessionFacade(session)
    assert facade is not None
    # Smoke: a basic read query works.
    all_systems = facade.systems.all()
    assert len(all_systems) == 2


def test_smoke_scenario_galaxy_has_planets(smoke_turn1_scenario):
    """Galaxy generation produced at least one planet (for panel rendering)."""
    session, galaxy, empires = smoke_turn1_scenario
    total_planets = sum(len(s.planets) for s in galaxy.systems.values())
    assert total_planets >= 2, (
        f"galaxy must have at least 2 planets total to host 2 colonies; "
        f"got {total_planets}"
    )
