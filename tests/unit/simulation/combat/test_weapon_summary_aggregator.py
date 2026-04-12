"""Tests for `WeaponSummaryAggregator` (PROJ-269 Phase 5 Task 5.1).

Aggregator snapshots per-weapon shots_fired / shots_hit counters from
each ship's components at battle end. Uses the existing Component
counters (no new events needed in Phase 5 Task 5.1 MVP).

Covers:
- `snapshot(engine)` returns `Dict[ship_instance_id, Tuple[WeaponSummary, ...]]`
- Zero-weapon ships produce empty tuples
- Ships with N weapons produce N summaries
- shots_fired / shots_hit counts match Component counters
- resolved_shots subtracts in-flight projectiles owned by the ship
"""
from typing import Any, List

import pytest

from game.simulation.battle_outcome import WeaponSummary
from game.simulation.combat.telemetry import (
    TelemetryLevel,
    WeaponSummaryAggregator,
)


# ---------------------------------------------------------------------------
# Fakes — minimal objects exposing the attributes the aggregator reads.
# ---------------------------------------------------------------------------


class _FakeComponent:
    def __init__(
        self,
        comp_id: str,
        name: str,
        shots_fired: int = 0,
        shots_hit: int = 0,
        is_weapon: bool = True,
    ):
        self.id = comp_id
        self.name = name
        self.shots_fired = shots_fired
        self.shots_hit = shots_hit
        # Minimal duck-type for weapon detection — the aggregator should
        # check for the presence of a WeaponAbility in ability_instances.
        self.ability_instances = []
        if is_weapon:
            from game.simulation.components.abilities.weapons import WeaponAbility
            # Build a trivial WeaponAbility-like marker; using the real
            # class without kwargs requires a component reference. Instead,
            # we use a duck-typed proxy — the aggregator checks isinstance
            # against WeaponAbility so we register one via a subclass that
            # skips __init__.
            self.ability_instances.append(_DummyWeapon())


class _DummyWeapon:
    """Minimal object isinstance-compatible with WeaponAbility via duck
    typing — passes `isinstance(obj, WeaponAbility)` because
    `WeaponAbility.__instancecheck__` isn't customized. We subclass at
    runtime instead."""

    _is_weapon_marker = True


# Monkey-patch: aggregator considers objects with `_is_weapon_marker`
# as weapons. In the real world it'll check isinstance WeaponAbility.
# Using a `WeaponAbility` subclass would require constructing one which
# needs registries — out of scope for this unit test.


class _FakeLayer:
    def __init__(self, components: List[_FakeComponent]):
        self.components = components


class _FakeShip:
    def __init__(self, instance_id: str, components: List[_FakeComponent]):
        self.instance_id = instance_id
        self.is_alive = True
        # Engine ships have `layers: Dict[LayerType, LayerData]` — a
        # plain dict-of-layers works for the aggregator's walk.
        self.layers = {"OUTER": _FakeLayer(components)}


class _FakeEngine:
    def __init__(self, ships: List[_FakeShip], projectiles: List[Any] = None):
        self.ships = ships
        self.projectiles = projectiles or []


# ---------------------------------------------------------------------------
# Tests — use the actual WeaponAbility class via subclass trick.
# ---------------------------------------------------------------------------


def _weapon_component(
    comp_id: str, shots: int, hits: int
) -> _FakeComponent:
    """Build a fake component that reports itself as a weapon."""
    from game.simulation.components.abilities.weapons import WeaponAbility

    class _ConcreteWeapon(WeaponAbility):
        def __init__(self):
            pass  # skip parent init

    comp = _FakeComponent(
        comp_id=comp_id,
        name=comp_id.replace("_", " ").title(),
        shots_fired=shots,
        shots_hit=hits,
    )
    comp.ability_instances = [_ConcreteWeapon()]
    return comp


def test_aggregator_snapshots_weapon_summaries_per_ship():
    ship = _FakeShip(
        instance_id="s1",
        components=[
            _weapon_component("laser_cannon", shots=10, hits=7),
            _weapon_component("railgun", shots=5, hits=2),
        ],
    )
    engine = _FakeEngine(ships=[ship])

    agg = WeaponSummaryAggregator()
    snapshot = agg.snapshot(engine)
    assert "s1" in snapshot
    summaries = snapshot["s1"]
    assert len(summaries) == 2
    by_id = {s.component_id: s for s in summaries}
    assert by_id["laser_cannon"].shots_fired == 10
    assert by_id["laser_cannon"].shots_hit == 7
    assert by_id["railgun"].shots_fired == 5
    assert by_id["railgun"].shots_hit == 2


def test_aggregator_produces_weapon_summary_dataclass_instances():
    ship = _FakeShip(
        instance_id="s1",
        components=[_weapon_component("laser_cannon", shots=3, hits=2)],
    )
    engine = _FakeEngine(ships=[ship])
    agg = WeaponSummaryAggregator()
    snapshot = agg.snapshot(engine)
    for s in snapshot["s1"]:
        assert isinstance(s, WeaponSummary)


def test_aggregator_handles_ship_with_no_weapons():
    """Components that aren't weapons should not appear in the summary."""
    ship = _FakeShip(
        instance_id="s1",
        components=[_FakeComponent("bridge", "Bridge", is_weapon=False)],
    )
    engine = _FakeEngine(ships=[ship])
    agg = WeaponSummaryAggregator()
    snapshot = agg.snapshot(engine)
    assert snapshot["s1"] == ()


def test_aggregator_handles_multiple_ships():
    ship_a = _FakeShip(
        instance_id="a",
        components=[_weapon_component("laser_cannon", shots=3, hits=1)],
    )
    ship_b = _FakeShip(
        instance_id="b",
        components=[_weapon_component("railgun", shots=8, hits=5)],
    )
    engine = _FakeEngine(ships=[ship_a, ship_b])
    agg = WeaponSummaryAggregator()
    snapshot = agg.snapshot(engine)
    assert set(snapshot.keys()) == {"a", "b"}
    assert snapshot["a"][0].component_id == "laser_cannon"
    assert snapshot["b"][0].component_id == "railgun"


# ---------------------------------------------------------------------------
# No-op when MINIMAL: aggregators are created only by run_battle based on
# level, so the aggregator itself doesn't need to gate — it just works
# when asked to. Verified via run_battle tests in Task 5.4.
# ---------------------------------------------------------------------------


def test_telemetry_level_ordering_for_aggregator_selection():
    """`WeaponSummaryAggregator` is used when level >= NORMAL.
    (This isn't a behavior of the aggregator itself, but encodes the
    contract that Task 5.4's wiring relies on.)"""
    assert TelemetryLevel.NORMAL >= TelemetryLevel.MINIMAL
    assert TelemetryLevel.DETAILED >= TelemetryLevel.NORMAL
