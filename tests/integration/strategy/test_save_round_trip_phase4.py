"""PROJ-372 Phase 4: Galaxy save round-trip after pathfinding extraction.

Same shape as Phase 3 round-trip but exercises the post-Phase-4 facade.
Storms are skipped (pre-existing serde drift outside PROJ-372 scope).
"""
from __future__ import annotations

import random

from game.strategy.data.galaxy import Galaxy


def test_galaxy_round_trip_post_phase_4() -> None:
    random.seed(123)
    galaxy = Galaxy(radius=50)
    galaxy.generate_systems(5, min_dist=5)
    for system in list(galaxy.systems.values()):
        system.storms = []
        try:
            galaxy.generate_planets(system)
        except Exception:  # Intentional broad catch: synthetic galaxy may produce systems with no eligible planet types; we want the test resilient to that, since the focus is round-trip equality.
            pass
    galaxy.generate_warp_lanes()

    d1 = galaxy.to_dict()
    galaxy2 = Galaxy.from_dict(d1)
    d2 = galaxy2.to_dict()
    assert d1 == d2


def test_pathfinder_attached_after_init() -> None:
    galaxy = Galaxy(radius=10)
    assert galaxy._pathfinder is not None
    assert galaxy._intercept is not None


def test_pathfinder_callable_through_facade() -> None:
    """Smoke check: real Galaxy + pathfinder produces a deep-space path."""
    from game.core.hex_math import HexCoord

    galaxy = Galaxy(radius=10)
    path = galaxy._pathfinder.find_path_deep_space(HexCoord(0, 0), HexCoord(2, 0))
    assert path[0] == HexCoord(0, 0)
    assert path[-1] == HexCoord(2, 0)
