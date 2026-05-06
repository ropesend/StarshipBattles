"""PROJ-372 Phase 3: GalaxyState dataclass tests.

These intentionally avoid constructing a real ``Galaxy()`` (which
loads naming registries from disk) — proving the value of extracting
state from the heavy facade.
"""
from __future__ import annotations

from game.strategy.data.galaxy_state import GalaxyState


def test_default_dicts_are_empty() -> None:
    state = GalaxyState(radius=100)
    assert state.systems == {}
    assert state.name_map == {}
    assert state.planets_by_id == {}
    assert state.fleets_by_id == {}
    assert state.planet_to_system == {}
    assert state.global_hex_planets == {}
    assert state.global_hex_zones == {}
    assert state.global_hex_warp_points == {}
    assert state.zone_to_system == {}


def test_default_id_counters_start_at_one() -> None:
    state = GalaxyState(radius=10)
    assert state.next_planet_id == 1
    assert state.next_fleet_id == 1


def test_radius_required() -> None:
    state = GalaxyState(radius=42)
    assert state.radius == 42


def test_dicts_are_independent_per_instance() -> None:
    a = GalaxyState(radius=10)
    b = GalaxyState(radius=20)
    a.systems["x"] = "foo"
    assert b.systems == {}
