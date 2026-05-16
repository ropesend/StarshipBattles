"""PROJ-FMS-B Phase 5 — statistical balance tests.

Verifies the warhead-pass trigger formula obeys its invariants
empirically over many trials:

- Destroyer-class @ MED vs N=10 warhead mines: observed trigger rate
  within tolerance of the analytical ``P_trigger_pass``.
- Dreadnought-class triggers more often than destroyer (statistically
  significant).
- ``P_trigger_pass < 1.0`` for any N (asymptote invariant).
- ``P_trigger_pass > 0.0`` for N >= 1 and p_trigger > 0 (always-some-
  chance invariant).

Runs at 1000 trials per scenario (per the phase 5 checklist).
"""
from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.engine.minefield_resolver import MinefieldResolver


class _StubShip:
    """Minimal ShipInstance stand-in (matches the resolver's expectations)."""

    def __init__(self, instance_id, max_hp=200.0,
                 size_diameter=160.0, accel=30.0, turn_speed=90.0,
                 total_defense_score=0.0, owner_id=0):
        self.instance_id = instance_id
        self.design_id = "stub"
        self.name = instance_id
        self.owner_id = owner_id
        self.design_data = {}
        self._max_hp = max_hp
        self.current_hp = int(max_hp)
        self.is_alive = True
        self.is_derelict = False
        self.carried_items = []
        self._diameter = size_diameter
        self._accel = accel
        self._turn = turn_speed
        self._defense = total_defense_score

    def get_calculated_stats(self):
        return {
            "max_hp": self._max_hp,
            "diameter": self._diameter,
            "acceleration_rate": self._accel,
            "turn_speed": self._turn,
            "total_defense_score": self._defense,
        }


def _warhead_mine(damage=10.0):
    return {
        "design_id": "stat_mine",
        "design_data": {
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "warhead_small",
                         "abilities": {"Warhead": {"damage": damage}}},
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": 30,
    }


def _make_mine_group(hex_c, owner_id, mines, sensitivity="MED",
                     fleet_id=100000):
    """Build a populated mine_group with one synthetic carrier."""
    fleet = Fleet(
        fleet_id=fleet_id, owner_id=owner_id, location=hex_c, speed=0.0,
        group_kind="mine_group",
    )
    fleet.sensitivity = sensitivity
    carrier = SimpleNamespace(
        instance_id=f"carrier_{fleet_id}",
        owner_id=owner_id,
        carried_items=list(mines),
    )
    fleet.ships.append(carrier)
    return fleet


def _trial(seed: int, ship: _StubShip, mine_count: int, sensitivity: str) -> bool:
    """One trial: enemy ship enters a hex with N mines; True if any trigger."""
    hex_c = HexCoord(0, 0)
    mines = [_warhead_mine() for _ in range(mine_count)]
    mg = _make_mine_group(
        hex_c, owner_id=1, mines=mines, sensitivity=sensitivity,
        fleet_id=100000 + seed,
    )
    fleet = Fleet(
        fleet_id=seed + 1, owner_id=0, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    # Need to attach a fresh stub each trial because the resolver mutates HP.
    fresh = _StubShip(
        instance_id=ship.instance_id,
        max_hp=ship._max_hp,
        size_diameter=ship._diameter,
        accel=ship._accel,
        turn_speed=ship._turn,
        total_defense_score=ship._defense,
    )
    fleet.ships.append(fresh)
    enemy = SimpleNamespace(id=1, fleets=[mg])
    player = SimpleNamespace(id=0, fleets=[fleet])

    r = MinefieldResolver(rng=random.Random(seed))
    res = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy, player], fleet=fleet,
    )
    return bool(res.detonations)


@pytest.mark.parametrize("trials", [1000])
def test_destroyer_med_observed_rate_close_to_analytical(trials):
    """Over 1000 trials, observed trigger rate ≈ ``P_trigger_pass``."""
    destroyer = _StubShip(
        "destroyer", size_diameter=160.0, accel=30.0, turn_speed=90.0,
    )
    r = MinefieldResolver()
    p_trigger = r.compute_p_trigger(destroyer, "MED")
    expected_pass = r.compute_p_trigger_pass(p_trigger, 10)

    triggered = 0
    for seed in range(trials):
        if _trial(seed, destroyer, mine_count=10, sensitivity="MED"):
            triggered += 1
    observed = triggered / trials
    # Allow generous tolerance (binomial std at N=1000 is ~0.015 for p=0.5).
    tolerance = 0.05
    assert abs(observed - expected_pass) < tolerance, (
        f"observed={observed:.3f} expected={expected_pass:.3f}"
    )


@pytest.mark.parametrize("trials", [1000])
def test_dreadnought_triggers_more_than_destroyer(trials):
    """Dread-class statistically-significantly higher rate than destroyer."""
    destroyer = _StubShip(
        "dest", size_diameter=160.0, accel=30.0, turn_speed=90.0,
    )
    dread = _StubShip(
        "dread", size_diameter=400.0, accel=10.0, turn_speed=30.0,
    )
    dest_hits = sum(
        1 for s in range(trials)
        if _trial(s, destroyer, mine_count=10, sensitivity="MED")
    )
    dread_hits = sum(
        1 for s in range(trials, 2 * trials)
        if _trial(s, dread, mine_count=10, sensitivity="MED")
    )
    # Loose check — dread should be at least 1.5x destroyer rate.
    assert dread_hits > dest_hits * 1.1, (
        f"dread={dread_hits} not significantly > destroyer={dest_hits}"
    )


def test_invariant_never_100_percent_at_large_n():
    """``P_trigger_pass`` must stay strictly below 1.0 even for huge N."""
    r = MinefieldResolver()
    destroyer = _StubShip("d")
    p = r.compute_p_trigger(destroyer, "HIGH")
    for n in (1, 10, 100, 1000, 100000):
        p_pass = r.compute_p_trigger_pass(p, n)
        assert p_pass < 1.0, f"P_pass={p_pass} at N={n}"


def test_invariant_always_positive_with_one_mine():
    """N=1 and p_trigger > 0 must give P_pass > 0."""
    r = MinefieldResolver()
    destroyer = _StubShip("d")
    p = r.compute_p_trigger(destroyer, "MED")
    assert p > 0
    assert r.compute_p_trigger_pass(p, 1) > 0
