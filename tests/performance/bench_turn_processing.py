"""PROJ-412 Phase 1: turn-processing perf benchmark.

Captures per-phase wall-clock from `TurnEngine._phase_times` plus total
turn duration on a fixed-seed tiny scenario (2 empires, 2 systems / 2
colonised planets via `make_smoke_turn1_scenario`). The baseline JSON
sibling pins the *current* numbers; later phases of PROJ-412 re-run this
bench to measure deltas.

Goals:

* Fast enough for CI (<30 s budget).
* Manual mode runs more turns / more runs-per-bench for stable profiling
  data; flip via env var.
* Surfaces both the named-phase buckets (which are what TURN PERF logs)
  and the *unaccounted overhead* (total - sum(phases)) — the latter is
  PROJ-412's second-biggest optimization target.

Run as a normal pytest test::

    pytest tests/performance/bench_turn_processing.py -v -s

Manual / profiling mode (more turns, slower)::

    PROJ_412_BENCH_MODE=manual pytest tests/performance/bench_turn_processing.py -v -s
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from game.strategy.data.planetary_facility import PlanetaryFacility
from tests.fixtures.perf_smoke_scenario import make_smoke_turn1_scenario


_HERE = Path(__file__).resolve().parent
_BASELINE_FILE = _HERE / "bench_turn_processing.baseline.json"

# Resources whose harvesters we install on every colony in the bench
# scenario, to give harvesting realistic work. The smoke fixture has
# zero facilities by default (PROJ-411 panel-load fixture); without
# facilities the harvesting bucket is essentially zero and the bench
# fails to exercise the hot path PROJ-412 is targeting.
_BENCH_RESOURCES = ("metals", "organics", "vapors", "radioactives", "exotics")
_BENCH_HARVEST_RATE = 100.0
_BENCH_STORAGE_CAPACITY = 50000.0


def _make_harvester_facility(resource: str, idx: int) -> PlanetaryFacility:
    """Synthetic harvester facility for one resource type.

    Inline harvester ability (no registry lookup needed) so the bench
    runs without depending on registry data files.
    """
    return PlanetaryFacility(
        instance_id=f"bench-h-{resource}-{idx}",
        design_id=f"{resource}_harvester_complex",
        name=f"{resource.title()} Harvester {idx}",
        design_data={
            "layers": {
                "core": [
                    {
                        "id": f"{resource}_harvester",
                        "abilities": {
                            "ResourceHarvester": {
                                "resource_type": resource,
                                "base_harvest_rate": _BENCH_HARVEST_RATE,
                            }
                        },
                    }
                ]
            }
        },
    )


def _make_storage_facility(resource: str, idx: int) -> PlanetaryFacility:
    """Synthetic local-storage facility for one resource type."""
    return PlanetaryFacility(
        instance_id=f"bench-s-{resource}-{idx}",
        design_id=f"{resource}_storage_complex",
        name=f"{resource.title()} Storage {idx}",
        design_data={
            "layers": {
                "core": [
                    {
                        "id": f"{resource}_storage",
                        "abilities": {
                            "LocalStorage": {
                                "resource_type": resource,
                                "capacity": _BENCH_STORAGE_CAPACITY,
                            }
                        },
                    }
                ]
            }
        },
    )


def _populate_bench_scenario(session) -> None:
    """Add a realistic harvester + storage footprint to each colony.

    Adds one harvester and one storage facility per resource type on
    every colony, so the harvest hot path (facility scan, booster
    scope query, storage aggregation) gets the same shape of work it
    sees in the user's reported tiny-game baseline (~3.9 s in the
    harvesting bucket).
    """
    for empire in session.empires:
        for colony in empire.colonies:
            for idx, resource in enumerate(_BENCH_RESOURCES):
                colony.facilities.append(_make_harvester_facility(resource, idx))
                colony.facilities.append(_make_storage_facility(resource, idx))
            # Ensure deposits exist for every harvester so harvest fires.
            for resource in _BENCH_RESOURCES:
                if resource not in colony.deposits:
                    colony.deposits[resource] = {"quantity": 1_000_000.0, "quality": 1.0}
                else:
                    # Bump quantity high enough that we don't deplete inside the bench.
                    colony.deposits[resource]["quantity"] = max(
                        colony.deposits[resource].get("quantity", 0.0), 1_000_000.0
                    )

# CI defaults: low turn count to fit < 30 s budget at ~7.5 s/turn observed today.
# Manual defaults: long enough to stabilise variance for profiling work.
_CI_TURNS = 2
_CI_RUNS = 3
_MANUAL_TURNS = 10
_MANUAL_RUNS = 5


def _bench_settings() -> tuple[int, int]:
    """Return ``(turns_per_run, runs_per_bench)`` from env var.

    ``PROJ_412_BENCH_MODE=manual`` flips to the heavier scale. Default
    is CI.
    """
    if os.environ.get("PROJ_412_BENCH_MODE", "").lower() == "manual":
        return _MANUAL_TURNS, _MANUAL_RUNS
    return _CI_TURNS, _CI_RUNS


def _run_bench_once(turns_per_run: int) -> dict[str, float]:
    """Run ``turns_per_run`` turns on a fresh scenario; return per-turn averages.

    Each call rebuilds the scenario so per-run state is independent.
    Returned values are **per-turn averages** so the result is comparable
    across different `turns_per_run` settings (CI vs manual mode).
    """
    session, _galaxy, _empires = make_smoke_turn1_scenario()
    _populate_bench_scenario(session)
    engine = session.turn_engine

    total_wall = 0.0
    phase_sums: dict[str, float] = {}

    for _ in range(turns_per_run):
        t0 = time.perf_counter()
        session.process_turn()
        total_wall += time.perf_counter() - t0
        # Snapshot per-phase times for this turn before the engine resets them
        # on the next turn. `_reset_phase_times` runs at the top of each
        # process_turn call, so the post-call dict still holds the turn we
        # just ran.
        for key, val in engine._phase_times.items():
            phase_sums[key] = phase_sums.get(key, 0.0) + val

    # Normalise to per-turn so CI (2 turns/run) and manual (10 turns/run)
    # produce comparable numbers.
    return {
        "total": total_wall / turns_per_run,
        **{k: v / turns_per_run for k, v in phase_sums.items()},
    }


def _measure_min_of_runs(turns_per_run: int, runs_per_bench: int) -> dict:
    """Run the bench ``runs_per_bench`` times; return min / mean / max per metric.

    Reports the min as the headline value (consistent with
    ``bench_galaxy_planet_star.py`` convention — suppresses jitter).
    """
    runs: list[dict[str, float]] = []
    for _ in range(runs_per_bench):
        runs.append(_run_bench_once(turns_per_run))

    keys = sorted({k for r in runs for k in r.keys()})
    metrics: dict = {"per_phase": {}}
    for key in keys:
        values = [r.get(key, 0.0) for r in runs]
        block = {
            "min": min(values),
            "mean": sum(values) / len(values),
            "max": max(values),
        }
        if key == "total":
            metrics["total"] = block
        else:
            metrics["per_phase"][key] = block
    return metrics


def test_capture_or_assert_baseline() -> None:
    """Phase 1 captures baseline; later phases re-run to measure deltas.

    First run: writes ``bench_turn_processing.baseline.json`` and skips.
    Subsequent runs: compares each per-phase + total metric against the
    baseline and prints the deltas. We do NOT fail on regression in this
    bench — it's a measurement tool, not a gate. A separate (future)
    test in the PROJ-412 final phase will assert the agreed reduction.
    """
    turns_per_run, runs_per_bench = _bench_settings()
    mode = "manual" if turns_per_run == _MANUAL_TURNS else "ci"

    metrics = _measure_min_of_runs(turns_per_run, runs_per_bench)
    metrics["scale"] = {
        "turns_per_run": turns_per_run,
        "runs_per_bench": runs_per_bench,
        "mode": mode,
        "scenario": "smoke_turn1 (2 empires, 2 systems)",
    }

    if not _BASELINE_FILE.exists():
        _BASELINE_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        pytest.skip(
            f"Captured PROJ-412 turn-processing baseline to {_BASELINE_FILE.name} "
            f"(mode={mode}, turns_per_run={turns_per_run}, runs={runs_per_bench}). "
            "Re-run to compare."
        )

    baseline = json.loads(_BASELINE_FILE.read_text(encoding="utf-8"))

    total_baseline = baseline["total"]["min"]
    total_current = metrics["total"]["min"]
    delta_pct = 100.0 * (total_current - total_baseline) / max(total_baseline, 1e-9)
    print(
        f"\n[PROJ-412 bench] mode={mode} turns_per_run={turns_per_run} "
        f"runs={runs_per_bench}\n"
        f"  total: baseline_min={total_baseline:.3f}s "
        f"current_min={total_current:.3f}s delta={delta_pct:+.1f}%"
    )

    baseline_phases = baseline.get("per_phase", {})
    current_phases = metrics["per_phase"]
    phase_keys = sorted(set(baseline_phases) | set(current_phases))
    for key in phase_keys:
        b = baseline_phases.get(key, {}).get("min", 0.0)
        c = current_phases.get(key, {}).get("min", 0.0)
        if b < 1e-6 and c < 1e-6:
            continue
        d_pct = 100.0 * (c - b) / max(b, 1e-9) if b > 1e-9 else float("inf")
        print(f"  {key:30s} baseline_min={b:.4f}s current_min={c:.4f}s delta={d_pct:+.1f}%")

    # Always assert that no per-phase or total time exploded (>5x baseline) —
    # that would indicate a real regression caused by an unrelated change.
    # We don't gate on tighter tolerances; this bench is a measurement
    # tool, not a perf gate.
    blowups: list[str] = []
    if total_baseline > 1e-6 and total_current > 5.0 * total_baseline:
        blowups.append(
            f"total: {total_baseline:.3f}s -> {total_current:.3f}s (>5x)"
        )
    for key in phase_keys:
        b = baseline_phases.get(key, {}).get("min", 0.0)
        c = current_phases.get(key, {}).get("min", 0.0)
        if b > 1e-6 and c > 5.0 * b:
            blowups.append(f"{key}: {b:.4f}s -> {c:.4f}s (>5x)")
    assert not blowups, "Severe PROJ-412 bench regression:\n  " + "\n  ".join(blowups)
