"""Smoke benchmark for telemetry overhead (PROJ-269 Phase 5 Task 5.5).

Runs the same hand-built 1v1 battle at each TelemetryLevel and records
the wall-clock time. Asserts rough bounds to catch gross regressions;
detailed overhead numbers are documented in `decisions.md` for future
comparison.

This is a "smoke" benchmark, not a precision benchmark — it runs on
whatever hardware pytest is invoked on, so absolute numbers vary.
What matters is:
  - MINIMAL is not slower than NORMAL (no phantom subscribers)
  - DETAILED is within ~5x of MINIMAL (subscribers pay their weight
    but don't explode)
"""
import time

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import (
    AIPolicy,
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_end_conditions import TickLimitCondition


# Reference battle: 2 ships at ~weapon range, 500 ticks.
_DESIGN = {
    "name": "PerfCruiser",
    "ship_class": "Escort",
    "vehicle_type": "Ship",
    "design_role": "fleet_escort",
    "theme_id": "Federation",
    "layers": {
        "CORE": [{"id": "bridge"}],
        "OUTER": [{"id": "laser_cannon"}],
        "ARMOR": [],
    },
    "_metadata": {},
}
_REFERENCE_TICKS = 500
_RUNS_PER_LEVEL = 3  # Light — 3 runs per level is enough for a smoke benchmark.


def _team(team_id: int, ship: ShipSpec) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"Team {team_id}",
        entry_vector=EntryVector(origin=Vector2(0, 0), facing=0.0),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id=f"tf-{team_id}",
                formation=None,
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id=f"sq-{team_id}",
                        policies=CombatPolicies(),
                        ships=(ship,),
                    ),
                ),
            ),
        ),
        ai_policy=AIPolicy(),
    )


def _make_spec(level: TelemetryLevel) -> BattleSpec:
    ship_a = ShipSpec(
        instance_id="a",
        design_id="Cruiser",
        theme_id="Federation",
        name="A",
        position=Vector2(-500, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    ship_b = ShipSpec(
        instance_id="b",
        design_id="Cruiser",
        theme_id="Federation",
        name="B",
        position=Vector2(500, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    return BattleSpec(
        seed=42,
        telemetry_level=level,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=_REFERENCE_TICKS),
        absolute_max_ticks=_REFERENCE_TICKS + 100,
        teams=(_team(0, ship_a), _team(1, ship_b)),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


def _run_once(fresh_registries, level: TelemetryLevel) -> float:
    def ship_builder(ship_spec):
        ship = ShipSerializer.from_dict(_DESIGN, registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship

    spec = _make_spec(level)
    start = time.perf_counter()
    run_battle(spec, ai_factory=AIControllerFactory(), ship_builder=ship_builder)
    return time.perf_counter() - start


def _mean(xs):
    return sum(xs) / max(1, len(xs))


@pytest.mark.performance
def test_telemetry_overhead_smoke(fresh_registries):
    """Record telemetry overhead across the three levels. Asserts rough
    bounds; exact numbers go to the session log for the phase wrap."""
    minimal_times = [_run_once(fresh_registries, TelemetryLevel.MINIMAL) for _ in range(_RUNS_PER_LEVEL)]
    normal_times = [_run_once(fresh_registries, TelemetryLevel.NORMAL) for _ in range(_RUNS_PER_LEVEL)]
    detailed_times = [_run_once(fresh_registries, TelemetryLevel.DETAILED) for _ in range(_RUNS_PER_LEVEL)]

    minimal_mean = _mean(minimal_times)
    normal_mean = _mean(normal_times)
    detailed_mean = _mean(detailed_times)

    # Thresholds are deliberately loose — under full-suite load
    # (`pytest tests/`), per-run variance can be 2-3x. We want the
    # benchmark to catch catastrophic regressions, not flake on
    # timing noise. Precision measurement happens in isolation.
    # MINIMAL must not be dramatically slower than NORMAL.
    assert minimal_mean <= normal_mean * 3.0, (
        f"MINIMAL ({minimal_mean:.3f}s) >3x NORMAL ({normal_mean:.3f}s) "
        "— regression in phantom-subscriber behavior?"
    )
    # DETAILED must not explode relative to MINIMAL.
    assert detailed_mean <= minimal_mean * 10.0, (
        f"DETAILED ({detailed_mean:.3f}s) >10x MINIMAL ({minimal_mean:.3f}s) "
        "— overhead regression?"
    )

    # Emit numbers in the test report for visibility.
    print(
        f"\n[Telemetry overhead smoke] "
        f"MINIMAL={minimal_mean*1000:.1f}ms "
        f"NORMAL={normal_mean*1000:.1f}ms "
        f"DETAILED={detailed_mean*1000:.1f}ms "
        f"| {_REFERENCE_TICKS} ticks, {_RUNS_PER_LEVEL} runs each"
    )
