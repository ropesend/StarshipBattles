"""PROJ-477 Phase 2 Task 2.4 — SpatialSlice.contents_at_hex tests.

``facade.spatial.contents_at_hex(hex)`` returns grouped planet/zone membership
at a global hex, INCLUDING multi-hex zones (Dyson Spheres) whose CENTER is not
the queried hex — proving it does not collapse to the exact-center semantics of
``planets.at_hex`` (``planet_slice.get_planets_at_hex``). Projection to a summary
DTO is acceptable here (cold, summary-only callers); live-object zone consumers
use ``scene.world.zones_at_hex`` instead (decisions.md EXECUTION deviation).
"""
from types import SimpleNamespace

from game.core.hex_math import HexCoord
from game.strategy.facade.slices.spatial_slice import SpatialSlice


def test_contents_at_hex_groups_planets_and_zones_multi_hex_aware() -> None:
    """A multi-hex zone registered at the queried hex (but centered elsewhere)
    is included — proving multi-hex membership is preserved."""
    target = HexCoord(7, 7)

    planet = SimpleNamespace(name="Terra", owner_id=3)
    # Dyson Sphere: a zone whose CENTER is elsewhere but which OCCUPIES `target`
    # (the spatial index registers every occupied hex, so the lookup returns it).
    dyson = SimpleNamespace(name="Dyson Alpha")

    def planets_at(h):
        return [planet] if h == target else []

    def zones_at(h):
        return [dyson] if h == target else []

    galaxy = SimpleNamespace(
        get_planets_at_global_hex=planets_at,
        get_zones_at_global_hex=zones_at,
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))

    contents = SpatialSlice(state).contents_at_hex(target)

    assert contents.planet_names == ("Terra",)
    assert contents.zone_names == ("Dyson Alpha",)
    assert contents.hex == target


def test_contents_at_hex_empty_when_nothing_present() -> None:
    galaxy = SimpleNamespace(
        get_planets_at_global_hex=lambda h: [],
        get_zones_at_global_hex=lambda h: [],
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))

    contents = SpatialSlice(state).contents_at_hex(HexCoord(0, 0))

    assert contents.planet_names == ()
    assert contents.zone_names == ()


def test_contents_at_hex_handles_galaxy_without_zone_index() -> None:
    """Galaxy stubs without a zone index degrade gracefully to empty zones."""
    galaxy = SimpleNamespace(get_planets_at_global_hex=lambda h: [])
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))

    contents = SpatialSlice(state).contents_at_hex(HexCoord(1, 1))

    assert contents.planet_names == ()
    assert contents.zone_names == ()
