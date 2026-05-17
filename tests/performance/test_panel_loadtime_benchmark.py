"""PROJ-411 Task 1.10: Scalene-friendly benchmark for the 5 strategy panels.

Loops the module-level instrumented functions under the smoke scenario
enough times for Scalene to gather meaningful samples (the default
sampling rate is 1ms; the bare test_strategy_panel_spans.py runs in
<1s and Scalene reports "did not run for long enough").

Each function is exercised in BOTH modes so the profile shows the
before/after cost in one run:

* ``without`` — no ``facade_state``; legacy uncached path; this is the
  PROJ-411 BEFORE state.
* ``with`` — ``facade_state`` supplied; PROJ-411 AFTER state. Should
  be ~zero work after the first call per turn.

Run with:

    python Tools/profiling/run_scalene.py pytest --mode cpu \
        --pytest-target tests/performance/test_panel_loadtime_benchmark.py
"""
from __future__ import annotations

import os
import tempfile

import pytest

from game.core.profiling import (
    Profiler,
    get_default_profiler,
    set_default_profiler,
)


_ITERATIONS = 50  # ~50× 7 functions × 2 modes ≈ 700 invocations


@pytest.fixture
def active_profiler():
    profiler = Profiler()
    profiler.start()
    previous = get_default_profiler()
    set_default_profiler(profiler)
    yield profiler
    profiler.stop()
    set_default_profiler(previous)


def test_benchmark_open_paths_legacy_uncached(
    smoke_turn1_scenario, active_profiler
) -> None:
    """BEFORE-state: loop the open-path functions with no ``facade_state``.

    Each iteration triggers the full work — galaxy walk for gather_*,
    full JSON parse for scan_designs, full image load for load_resource_icons.
    The Profiler records each named span's individual duration so the
    test prints per-span medians at the end.
    """
    from game.ui.screens.planet_list_filters import (
        compute_planet_effect_keys,
        gather_planets,
    )
    from game.ui.screens.planet_list_window import build_effect_columns
    from game.ui.screens.star_list_filters import (
        compute_star_ranges,
        gather_stars,
    )
    from game.ui.panels.empire_treasury_panel import load_resource_icons
    from game.strategy.systems.design_repository import DesignRepository

    session, galaxy, empires = smoke_turn1_scenario
    empire = empires[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_0"), exist_ok=True)
        for _ in range(_ITERATIONS):
            planets = list(gather_planets(galaxy, empire))
            keys = compute_planet_effect_keys(planets)
            build_effect_columns(keys)
            stars = list(gather_stars(galaxy))
            compute_star_ranges(stars)
            load_resource_icons()
            # PROJ-434 Phase 2: BEFORE-state measurement now uses
            # DesignRepository (disk-bound scan) since DesignLibrary is gone.
            DesignRepository(tmpdir, empire_id=0).scan_designs()

    # Print per-span median (informational; this is the BEFORE state).
    _print_span_medians(active_profiler, "BEFORE (uncached)")


def test_benchmark_open_paths_with_facade_cache(
    smoke_turn1_scenario, active_profiler
) -> None:
    """AFTER-state: same loop with ``facade_state`` supplied.

    First iteration does real work; subsequent iterations hit the cache.
    Per-span durations should collapse to near-zero after iteration 1.
    """
    from game.ui.screens.planet_list_filters import (
        compute_planet_effect_keys,
        gather_planets,
    )
    from game.ui.screens.planet_list_window import build_effect_columns
    from game.ui.screens.star_list_filters import (
        compute_star_ranges,
        gather_stars,
    )
    from game.ui.panels.empire_treasury_panel import load_resource_icons
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository
    from game.strategy.facade.slices._facade_state import FacadeSessionState

    session, galaxy, empires = smoke_turn1_scenario
    empire = empires[0]
    state = FacadeSessionState(session=session)

    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_0"), exist_ok=True)
        # PROJ-434 Phase 2: AFTER-state uses DesignCatalog (in-memory
        # list view; scan_designs() reads the cached list rather than
        # globbing disk each iteration).
        catalog = DesignCatalog(empire_id=0)
        catalog.repopulate_from(DesignRepository(tmpdir, empire_id=0))
        for _ in range(_ITERATIONS):
            planets = list(gather_planets(galaxy, empire, facade_state=state))
            keys = compute_planet_effect_keys(planets)
            build_effect_columns(keys)
            stars = list(gather_stars(galaxy, facade_state=state))
            compute_star_ranges(stars)
            load_resource_icons()
            catalog.scan_designs()

    _print_span_medians(active_profiler, "AFTER (cached)")


def _print_span_medians(profiler: Profiler, label: str) -> None:
    """Print median + max duration per span name."""
    from collections import defaultdict
    from statistics import median

    by_name: dict[str, list[float]] = defaultdict(list)
    for r in profiler.records:
        by_name[r["name"]].append(r["duration_ms"])

    print(f"\n--- {label} ({len(profiler.records)} records) ---")
    for name in sorted(by_name):
        durations = by_name[name]
        print(
            f"  {name:48s}  n={len(durations):3d}  "
            f"median={median(durations):8.3f} ms  "
            f"max={max(durations):8.3f} ms  "
            f"total={sum(durations):9.2f} ms"
        )
