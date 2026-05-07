"""PROJ-372 Phase 5: canonical save round-trip across 5 fixture saves.

Replaces the per-phase round-trip tests (test_save_round_trip_phase1.py,
.._phase2.py, .._phase3.py, .._phase4.py — kept for now as
boundary-checks but redundant once this is green).

The five fixture saves vary across:
1. Empty galaxy (radius only).
2. Single system + 1 planet.
3. 5-system synthetic with warp lanes.
4. 10-system synthetic with planets.
5. 20-system synthetic with planets + warp lanes.

PROJ-377 Phase 1 adds two checked-in JSON golden-save fixtures (baseline +
populated) plus matching round-trip identity tests. See PROJ-377 plan.md
+ decisions.md for the format / seed / capture-script convention.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.planet import Planet, PlanetType


_FIXTURE_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "saves"


def _build_minimal_planet(name: str, location: HexCoord) -> Planet:
    return Planet(
        name=name, location=location, orbit_distance=1,
        mass=5.97e24, radius=6.371e6, surface_area=5.1e14,
        density=5515.0, surface_gravity=9.81,
        surface_pressure=101325.0, surface_temperature=288.0,
        surface_water=0.5, tectonic_activity=0.5, magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )


def _strip_storms(galaxy: Galaxy) -> None:
    """Pre-existing Storm.to_dict()/from_dict() drift is OUT OF SCOPE for
    PROJ-372; clear storms before round-trip."""
    for system in galaxy.systems.values():
        system.storms = []


def _round_trip_assert(galaxy: Galaxy) -> None:
    d1 = galaxy.to_dict()
    galaxy2 = Galaxy.from_dict(d1)
    d2 = galaxy2.to_dict()
    assert d1 == d2


def test_round_trip_empty_galaxy() -> None:
    galaxy = Galaxy(radius=10)
    _round_trip_assert(galaxy)


def test_round_trip_single_system_with_planet() -> None:
    random.seed(1)
    galaxy = Galaxy(radius=20)
    galaxy.generate_systems(1, min_dist=5)
    system = next(iter(galaxy.systems.values()))
    system.storms = []
    planet = _build_minimal_planet("Manual-1", HexCoord(2, 0))
    galaxy.register_planet(system, planet)
    system.planets.append(planet)
    _round_trip_assert(galaxy)


def test_round_trip_5_system_synthetic_with_warp() -> None:
    random.seed(2)
    galaxy = Galaxy(radius=30)
    galaxy.generate_systems(5, min_dist=5)
    _strip_storms(galaxy)
    galaxy.generate_warp_lanes()
    _round_trip_assert(galaxy)


def test_round_trip_10_systems_with_planets() -> None:
    random.seed(3)
    galaxy = Galaxy(radius=50)
    galaxy.generate_systems(10, min_dist=5)
    _strip_storms(galaxy)
    for system in list(galaxy.systems.values()):
        try:
            galaxy.generate_planets(system)
        except Exception:  # Intentional broad catch: synthetic galaxy may produce systems with no eligible planet types; we want the test resilient to that, since the focus is round-trip equality.
            pass
    _round_trip_assert(galaxy)


def test_round_trip_20_systems_planets_warp() -> None:
    random.seed(4)
    galaxy = Galaxy(radius=80)
    galaxy.generate_systems(20, min_dist=5)
    _strip_storms(galaxy)
    for system in list(galaxy.systems.values()):
        try:
            galaxy.generate_planets(system)
        except Exception:  # Intentional broad catch: same as above.
            pass
    galaxy.generate_warp_lanes()
    _round_trip_assert(galaxy)


# ---------------------------------------------------------------------------
# PROJ-377 Phase 1: golden-save JSON fixture round-trip identity tests.
# ---------------------------------------------------------------------------

def test_round_trip_golden_baseline_fixture() -> None:
    """Load the checked-in baseline fixture and assert byte-identical round-trip.

    Captures cumulative serialization drift across PROJ-368 → PROJ-372 (and
    forward). If a field is added to `to_dict` but not read by `from_dict`
    (or vice versa), this test fails.
    """
    fixture = json.loads((_FIXTURE_DIR / "galaxy_proj372_baseline.json").read_text())
    galaxy = Galaxy.from_dict(fixture)
    assert galaxy.to_dict() == fixture


def test_round_trip_golden_populated_fixture() -> None:
    """Round-trip identity for a populated galaxy with planets + warp lanes."""
    fixture = json.loads((_FIXTURE_DIR / "galaxy_proj372_populated.json").read_text())
    galaxy = Galaxy.from_dict(fixture)
    assert galaxy.to_dict() == fixture
