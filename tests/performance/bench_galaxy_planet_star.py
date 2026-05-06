"""PROJ-372: perf baseline bench for galaxy/planet/star hot paths.

Captures the pre-decomposition performance of:
- ``find_path_interstellar`` (3 random routes)
- ``Galaxy.get_system_at_location`` (1000 random hex lookups)
- ``Planet.get_cached_habitability_multiplier`` (1000 calls)

Phase 0 records the baseline as JSON pinned next to this file. Phase 5
re-runs the bench and asserts each metric is within +-5% of the
recorded baseline.

Scale: 50 systems / ~125 planets is a deliberate compromise — full 150
systems with the real PlanetGenerator pulls in the entire registry data
load and adds 10+ seconds to test boot. 50 is enough to make the perf
delta observable while staying inside CI test budgets (<30s).

Run as a normal pytest test::

    pytest tests/performance/bench_galaxy_planet_star.py -v -s
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Callable, Dict

import pytest

from game.core.hex_math import HexCoord


_HERE = Path(__file__).resolve().parent
_BASELINE_FILE = _HERE / "bench_galaxy_planet_star_baseline.json"

# Phase 0 baseline scale.
_NUM_SYSTEMS = 50
_NUM_LOOKUPS = 1000
_NUM_HABITABILITY = 1000
_NUM_PATHS = 3
_RUNS_PER_BENCH = 5  # min-of-N to suppress jitter


def _build_synthetic_galaxy(seed: int = 42):
    from game.strategy.data.galaxy import Galaxy

    random.seed(seed)
    galaxy = Galaxy(radius=100)
    galaxy.generate_systems(count=_NUM_SYSTEMS, min_dist=8)
    for system in list(galaxy.systems.values()):
        try:
            galaxy.generate_planets(system)
        except Exception:  # Intentional broad catch: synthetic-galaxy bench is best-effort; if PlanetGenerator fails on a synthetic system we keep the system without planets rather than aborting the entire bench.
            pass
    galaxy.generate_warp_lanes()
    return galaxy


def _measure_min(label: str, fn: Callable[[], None], runs: int = _RUNS_PER_BENCH) -> float:
    times: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return min(times)


@pytest.fixture(scope="module")
def synthetic_galaxy():
    return _build_synthetic_galaxy(seed=42)


def _bench_pathfinding(galaxy) -> float:
    from game.strategy.data.pathfinding import find_path_interstellar

    systems = list(galaxy.systems.values())
    if len(systems) < 2:
        return 0.0
    random.seed(7)
    pairs = [
        (random.choice(systems), random.choice(systems))
        for _ in range(_NUM_PATHS)
    ]

    def run():
        for a, b in pairs:
            if a is b:
                continue
            find_path_interstellar(a, b, galaxy)

    return _measure_min("pathfinding", run)


def _bench_spatial(galaxy) -> float:
    random.seed(11)
    hexes = [
        HexCoord(random.randint(-100, 100), random.randint(-100, 100))
        for _ in range(_NUM_LOOKUPS)
    ]

    def run():
        for h in hexes:
            galaxy.get_system_at_location(h)

    return _measure_min("spatial", run)


def _bench_habitability(galaxy) -> float:
    # Collect all planets across the synthetic galaxy.
    planets: list[Any] = []
    for system in galaxy.systems.values():
        planets.extend(system.planets)
    if not planets:
        return 0.0

    # Stub race_registry — fast path returns None and the calculator
    # short-circuits to 1.0 on uncolonized planets.
    class _StubRaceReg:
        def get_race(self, race_id):
            return None

    race_registry = _StubRaceReg()

    # Repeat through planets to reach _NUM_HABITABILITY calls.
    cycle = []
    while len(cycle) < _NUM_HABITABILITY:
        cycle.extend(planets)
    cycle = cycle[:_NUM_HABITABILITY]

    def run():
        # Vary turn so the cache invalidates each call (matches the
        # turn-cache semantics of multiple turns of strategic play).
        for i, p in enumerate(cycle):
            p.get_cached_habitability_multiplier(race_registry, turn=i)

    return _measure_min("habitability", run)


def test_capture_or_assert_baseline(synthetic_galaxy) -> None:
    """If no baseline JSON is present, capture one. Otherwise just verify
    bench code runs (Phase 5 asserts within +-5%).

    Phase 0 expectation: the JSON is created on first run and committed
    by the implementer."""
    metrics: Dict[str, float] = {
        "pathfinding_min_seconds": _bench_pathfinding(synthetic_galaxy),
        "spatial_min_seconds": _bench_spatial(synthetic_galaxy),
        "habitability_min_seconds": _bench_habitability(synthetic_galaxy),
        "scale": {
            "num_systems": _NUM_SYSTEMS,
            "num_lookups": _NUM_LOOKUPS,
            "num_habitability": _NUM_HABITABILITY,
            "num_paths": _NUM_PATHS,
            "runs_per_bench": _RUNS_PER_BENCH,
        },
    }

    if not _BASELINE_FILE.exists():
        _BASELINE_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        pytest.skip(
            f"Captured PROJ-372 perf baseline to {_BASELINE_FILE.name}. "
            "Re-run to assert against it."
        )

    # Baseline exists — sanity-check the bench code is still wired right.
    # Phase 5 will swap this for a +-5% tolerance assertion.
    baseline = json.loads(_BASELINE_FILE.read_text(encoding="utf-8"))
    assert "pathfinding_min_seconds" in baseline
    assert "spatial_min_seconds" in baseline
    assert "habitability_min_seconds" in baseline
    # Smoke check: current run produced finite numbers (>= 0).
    for key in (
        "pathfinding_min_seconds",
        "spatial_min_seconds",
        "habitability_min_seconds",
    ):
        assert metrics[key] >= 0.0
