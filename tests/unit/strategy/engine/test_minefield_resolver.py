"""PROJ-FMS-B Phase 1 — MinefieldResolver tests.

Coverage:
- p_trigger / P_trigger_pass math (asymptote, > 0 with N >= 1, friendly skip).
- Strategic warhead pass: enemy fleet enters mined hex, mines consumed,
  damage applied via ship.current_hp.
- Bigger ships trigger more often than smaller ships.
- Friendly fleet skips the resolver entirely.
- Mine_group cleanup when inventory hits zero.
"""
from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import MineGroup
from game.strategy.data.fleet import Fleet
from game.strategy.engine.minefield_balance import MinefieldBalance
from game.strategy.engine.minefield_resolver import (
    MinefieldResolver,
    resolve_minefield_entry,
)


# ---------------------------------------------------------------------------
# Stub ship & empire fixtures (avoid pulling the heavy ShipInstance graph).
# ---------------------------------------------------------------------------


class _StubShip:
    """Minimal stand-in for ShipInstance used by the resolver."""

    def __init__(
        self,
        instance_id: str,
        max_hp: float = 200.0,
        size_diameter: float = 160.0,  # destroyer-ish
        accel: float = 30.0,
        turn_speed: float = 90.0,
        total_defense_score: float = 0.5,
    ) -> None:
        self.instance_id = instance_id
        self._max_hp = max_hp
        self.current_hp = int(max_hp)
        self.is_alive = True
        self.is_derelict = False
        # PROJ-431 Phase 1b: stub uses the typed BayInventory substrate.
        self._bay_inventory = BayInventory()
        self._size_diameter = size_diameter
        self._accel = accel
        self._turn_speed = turn_speed
        self._defense = total_defense_score
        self.owner_id = 0

    @property
    def bay_inventory(self) -> BayInventory:
        # Return a fresh projection mirroring ShipInstance.bay_inventory
        # (callers should not mutate the returned lists directly).
        return BayInventory(
            bay=list(self._bay_inventory.bay),
            pods=list(self._bay_inventory.pods),
        )

    def set_bay_inventory(self, bay_inventory: BayInventory) -> None:
        self._bay_inventory = BayInventory(
            bay=list(bay_inventory.bay),
            pods=list(bay_inventory.pods),
        )

    def get_calculated_stats(self):
        return {
            "max_hp": self._max_hp,
            "diameter": self._size_diameter,
            "acceleration_rate": self._accel,
            "turn_speed": self._turn_speed,
            "total_defense_score": self._defense,
        }


def _make_empire(
    empire_id: int,
    fleets=None,
    deployed_groups=None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=empire_id,
        name=f"E{empire_id}",
        fleets=list(fleets or []),
        deployed_groups=list(deployed_groups or []),
    )


def _make_mine_dict(design_id: str, damage: float = 50.0, mass: float = 5.0):
    """Build a CarriedVehicle-shaped mine dict with a Warhead component."""
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "vehicle_class": "Mine (Small)",
            "layers": {
                "CORE": {
                    "components": [
                        {
                            "id": "hull_mine_small",
                            "abilities": {"StructuralIntegrity": {"hp": 30}},
                        },
                        {
                            "id": "warhead",
                            "abilities": {"Warhead": {"damage": damage}},
                        },
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": mass,
        "current_hp": 30,
    }


def _make_laserhead_mine(design_id: str, damage: float = 40.0):
    """Mine carrying a Laserhead ability."""
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "vehicle_class": "Mine (Small)",
            "layers": {
                "CORE": {
                    "components": [
                        {
                            "id": "hull_mine_small",
                            "abilities": {"StructuralIntegrity": {"hp": 30}},
                        },
                        {
                            "id": "laserhead",
                            "abilities": {
                                "Laserhead": {
                                    "damage": damage,
                                    "range": 600,
                                    "base_accuracy": 5.0,
                                    "accuracy_falloff": 0.001,
                                    "consume_on_fire": True,
                                },
                            },
                        },
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": 30,
    }


def _make_mine_group_at(
    hex_coord: HexCoord,
    owner_id: int,
    mine_dicts,
    fleet_id: int = 100000,
    sensitivity: str = "MED",
    threshold: float = 0.30,
) -> MineGroup:
    """PROJ-431 Phase 2: build a typed :class:`MineGroup`."""
    group = MineGroup(
        group_id=fleet_id,
        owner_id=owner_id,
        location=hex_coord,
        sensitivity=sensitivity,
        expected_hit_chance_threshold=threshold,
    )
    group.mines = [CarriedVehicle.from_dict(m) for m in mine_dicts]
    return group


def _make_fleet_at(
    hex_coord: HexCoord,
    owner_id: int,
    ships,
    fleet_id: int = 1,
) -> Fleet:
    f = Fleet(
        fleet_id=fleet_id,
        owner_id=owner_id,
        location=hex_coord,
        speed=5.0,
        group_kind="fleet",
    )
    for s in ships:
        f.ships.append(s)
    return f


# ---------------------------------------------------------------------------
# Math invariants
# ---------------------------------------------------------------------------


def test_strategic_damage_routes_through_damage_pipeline_when_registries_given():
    """PROJ-FMS-B audit Fix 1: when ``registries`` is passed, mine damage
    must flow through ``DamageCalculator.apply_damage`` (shields → armor →
    hull) instead of the direct-HP fallback. Pre-fix the production turn
    hook never passed ``registries``, so live mine hits silently bypassed
    shields.
    """
    from game.strategy.engine.minefield_resolver import _apply_strategic_damage

    captured: dict = {}

    class _StubSimShip:
        def __init__(self) -> None:
            self.hp = 100
            self.current_shields = 75

    sim_ship = _StubSimShip()

    class _StubShipInstance:
        instance_id = "s1"
        design_data = {"layers": {}}  # non-empty so the gate triggers

        def __init__(self) -> None:
            self.current_hp = 100
            self.is_alive = True

        def get_calculated_stats(self):
            return {"max_hp": 100}

        def to_ship(self, position, team_id, *, registries):
            captured["to_ship_called_with_registries"] = registries
            return sim_ship

        def invalidate_stats_cache(self) -> None:
            pass

    # Patch DamageCalculator.apply_damage to capture the call.
    import game.simulation.combat.damage_calculator as _dc_mod
    original = _dc_mod.DamageCalculator.apply_damage

    def _capture_apply_damage(self, ship, dmg, *args, **kwargs):
        captured["apply_damage_called"] = (ship, dmg)
        # Drain shields like the real pipeline would.
        absorbed = min(ship.current_shields, dmg)
        ship.current_shields -= absorbed
        remaining = dmg - absorbed
        ship.hp = max(0, ship.hp - remaining)

    _dc_mod.DamageCalculator.apply_damage = _capture_apply_damage
    try:
        sentinel_registries = object()
        applied = _apply_strategic_damage(
            _StubShipInstance(), 50.0, registries=sentinel_registries,
        )
    finally:
        _dc_mod.DamageCalculator.apply_damage = original

    assert captured.get("to_ship_called_with_registries") is sentinel_registries
    assert captured.get("apply_damage_called") is not None, (
        "DamageCalculator.apply_damage must be invoked when registries are passed."
    )
    # Damage absorbed by shields means HP unchanged on the sim_ship.
    assert sim_ship.current_shields == 25  # 75 - 50 absorbed
    assert sim_ship.hp == 100  # No HP loss because shields absorbed all of it
    assert applied == 0.0  # No HP delta — shields ate everything


def test_p_trigger_pass_asymptotes_below_one():
    """P_trigger_pass < 1 for any finite N (the 'never 100%' invariant)."""
    r = MinefieldResolver(rng=random.Random(0))
    for n in (1, 5, 10, 100, 10000):
        p = r.compute_p_trigger_pass(0.3, n)
        assert p < 1.0, f"N={n} gave p_pass={p}"


def test_p_trigger_pass_positive_with_one_mine():
    """N=1 and p_trigger > 0 must give P_pass > 0 ('always some chance')."""
    r = MinefieldResolver()
    assert r.compute_p_trigger_pass(0.1, 1) > 0.0


def test_p_trigger_zero_with_zero_mines():
    """No mines, no chance."""
    r = MinefieldResolver()
    assert r.compute_p_trigger_pass(0.5, 0) == 0.0


def test_p_trigger_bigger_ship_higher_than_smaller():
    """Larger ships trigger more often per the design."""
    r = MinefieldResolver()
    small = _StubShip("small", size_diameter=80.0, accel=30.0, turn_speed=90.0)
    big = _StubShip("big", size_diameter=320.0, accel=30.0, turn_speed=90.0)
    p_small = r.compute_p_trigger(small, "MED")
    p_big = r.compute_p_trigger(big, "MED")
    assert p_big > p_small


def test_p_trigger_sensitivity_scales():
    """LOW < MED < HIGH scaling."""
    r = MinefieldResolver()
    ship = _StubShip("s", size_diameter=160.0)
    p_low = r.compute_p_trigger(ship, "LOW")
    p_med = r.compute_p_trigger(ship, "MED")
    p_high = r.compute_p_trigger(ship, "HIGH")
    assert p_low < p_med < p_high


# ---------------------------------------------------------------------------
# Resolver behavior
# ---------------------------------------------------------------------------


def test_friendly_fleet_does_not_trigger_mines():
    """Mines belonging to the same empire are skipped."""
    hex_c = HexCoord(0, 0)
    mines = [_make_mine_dict("mine_warhead_small") for _ in range(5)]
    mg = _make_mine_group_at(hex_c, owner_id=1, mine_dicts=mines)

    ship = _StubShip("ship_1", max_hp=200)
    fleet = _make_fleet_at(hex_c, owner_id=1, ships=[ship], fleet_id=10)

    emp = _make_empire(1, fleets=[fleet], deployed_groups=[mg])
    r = MinefieldResolver(rng=random.Random(0))
    result = r.resolve_minefield_entry(galaxy=None, empires=[emp], fleet=fleet)
    assert result.detonations == []
    assert len(mg.mines) == 5  # mines untouched


def test_warhead_pass_consumes_one_mine_on_trigger():
    """A single trigger consumes exactly one warhead."""
    hex_c = HexCoord(0, 0)
    mines = [_make_mine_dict("mine_warhead_small", damage=80) for _ in range(5)]
    mg = _make_mine_group_at(hex_c, owner_id=1, mine_dicts=mines, sensitivity="HIGH")

    ship = _StubShip("ship_1", max_hp=400)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy_emp = _make_empire(1, deployed_groups=[mg])
    player_emp = _make_empire(0, fleets=[fleet])

    # rng=0 first call returns ~0.844, but with high sensitivity *
    # 5 mines that's still likely to trigger. To pin behaviour, force
    # a trigger by manipulating rng.
    forced_rng = random.Random()
    forced_rng.random = lambda: 0.0  # always trigger
    forced_rng.randrange = lambda n: 0  # pick first mine

    r = MinefieldResolver(rng=forced_rng)
    result = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy_emp, player_emp], fleet=fleet,
    )
    # In a forced-trigger run with 5 warhead mines the resolver triggers
    # at most once per ship per group.
    assert len([d for d in result.detonations if d.pass_kind == "warhead"]) == 1
    assert len(mg.mines) == 4
    assert ship.current_hp < 400  # damage applied


def test_mine_group_removed_when_emptied():
    """When the last warhead mine is consumed (with no laserheads left),
    the mine_group is pruned from the empire's fleets list."""
    hex_c = HexCoord(0, 0)
    mines = [_make_mine_dict("mine_warhead_small", damage=200)]
    mg = _make_mine_group_at(hex_c, owner_id=1, mine_dicts=mines, sensitivity="HIGH")

    ship = _StubShip("ship_1", max_hp=200)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy_emp = _make_empire(1, deployed_groups=[mg])
    player_emp = _make_empire(0, fleets=[fleet])

    forced_rng = random.Random()
    forced_rng.random = lambda: 0.0
    forced_rng.randrange = lambda n: 0

    r = MinefieldResolver(rng=forced_rng)
    r.resolve_minefield_entry(
        galaxy=None, empires=[enemy_emp, player_emp], fleet=fleet,
    )
    assert mg not in enemy_emp.deployed_groups, "Empty mine_group should be pruned"


def test_module_helper_resolve_minefield_entry():
    """The module-level helper builds a resolver and runs end-to-end."""
    hex_c = HexCoord(0, 0)
    mines = [_make_mine_dict("mine_warhead_small")]
    mg = _make_mine_group_at(hex_c, owner_id=1, mine_dicts=mines)

    ship = _StubShip("ship_1")
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy_emp = _make_empire(1, deployed_groups=[mg])
    player_emp = _make_empire(0, fleets=[fleet])

    # Use a custom balance to drive p_trigger == 0 — no detonations.
    bal = MinefieldBalance()
    bal_no_trigger = MinefieldBalance(
        warhead_trigger=bal.warhead_trigger,
        sensitivity_multipliers={"LOW": 0.0, "MED": 0.0, "HIGH": 0.0},
        scatter=bal.scatter,
        laserhead=bal.laserhead,
        tactical=bal.tactical,
    )
    result = resolve_minefield_entry(
        galaxy=None,
        empires=[enemy_emp, player_emp],
        fleet=fleet,
        balance=bal_no_trigger,
        rng=random.Random(42),
    )
    assert result.detonations == []
    assert ship.is_alive


def test_no_mines_at_hex_is_a_noop():
    """No enemy mine_groups at the hex → no detonations, no errors."""
    hex_c = HexCoord(0, 0)
    ship = _StubShip("ship_1")
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy_emp = _make_empire(1, fleets=[])
    player_emp = _make_empire(0, fleets=[fleet])

    result = resolve_minefield_entry(
        galaxy=None, empires=[enemy_emp, player_emp], fleet=fleet,
    )
    assert result.detonations == []
    assert result.consumed_mine_ids == []


# ---------------------------------------------------------------------------
# Statistical: bigger ships trigger more
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Phase 2: laserhead pass
# ---------------------------------------------------------------------------


def test_laserhead_skipped_below_threshold():
    """Laserhead with expected_hit_chance < threshold does not fire/consume."""
    hex_c = HexCoord(0, 0)
    # Threshold set well above what the mine can compute.
    mines = [_make_laserhead_mine("mine_laserhead_small", damage=40)]
    mg = _make_mine_group_at(
        hex_c, owner_id=1, mine_dicts=mines, threshold=0.999999,
    )
    # Defense score 100.0 ensures the sigmoid net is hugely negative
    # -> expected_hit_chance ~= 0 -> below any practical threshold.
    ship = _StubShip("s", total_defense_score=100.0)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy = _make_empire(1, deployed_groups=[mg])
    player = _make_empire(0, fleets=[fleet])

    r = MinefieldResolver(rng=random.Random(0))
    result = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy, player], fleet=fleet,
    )
    laserhead_detonations = [
        d for d in result.detonations if d.pass_kind == "laserhead"
    ]
    assert laserhead_detonations == []
    # Laserhead NOT consumed.
    assert len(mg.mines) == 1


def test_laserhead_fires_above_threshold():
    """Laserhead with expected_hit_chance >= threshold fires and is consumed."""
    hex_c = HexCoord(0, 0)
    # base_accuracy=5.0 + 0 sensor - 0 defense gives sigmoid(5) ~= 0.993
    mines = [_make_laserhead_mine("mine_laserhead_small", damage=40)]
    mg = _make_mine_group_at(
        hex_c, owner_id=1, mine_dicts=mines, threshold=0.30,
    )
    ship = _StubShip("s", total_defense_score=0.0)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy = _make_empire(1, deployed_groups=[mg])
    player = _make_empire(0, fleets=[fleet])

    # Force standard beam roll to hit.
    rng = random.Random()
    rng.random = lambda: 0.0  # always-hit
    rng.randrange = lambda n: 0

    r = MinefieldResolver(rng=rng)
    result = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy, player], fleet=fleet,
    )
    laserhead_detonations = [
        d for d in result.detonations if d.pass_kind == "laserhead"
    ]
    assert len(laserhead_detonations) == 1
    assert laserhead_detonations[0].hit
    # Laserhead consumed.
    assert len(mg.mines) == 0


def test_laserhead_threshold_zero_always_fires():
    """Threshold 0.0 => every laserhead with a positive hit chance fires."""
    hex_c = HexCoord(0, 0)
    mines = [_make_laserhead_mine("m1"), _make_laserhead_mine("m2")]
    mg = _make_mine_group_at(
        hex_c, owner_id=1, mine_dicts=mines, threshold=0.0,
    )
    ship = _StubShip("s", total_defense_score=0.0)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy = _make_empire(1, deployed_groups=[mg])
    player = _make_empire(0, fleets=[fleet])

    rng = random.Random()
    rng.random = lambda: 0.0
    rng.randrange = lambda n: 0

    r = MinefieldResolver(rng=rng)
    result = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy, player], fleet=fleet,
    )
    lh = [d for d in result.detonations if d.pass_kind == "laserhead"]
    assert len(lh) == 2
    assert len(mg.mines) == 0  # both consumed


def test_laserhead_threshold_one_never_fires():
    """Threshold 1.0 => no laserhead ever fires (hit chance < 1 in practice)."""
    hex_c = HexCoord(0, 0)
    mines = [_make_laserhead_mine("m1"), _make_laserhead_mine("m2")]
    mg = _make_mine_group_at(
        hex_c, owner_id=1, mine_dicts=mines, threshold=1.0,
    )
    ship = _StubShip("s", total_defense_score=0.0)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy = _make_empire(1, deployed_groups=[mg])
    player = _make_empire(0, fleets=[fleet])

    r = MinefieldResolver(rng=random.Random(0))
    result = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy, player], fleet=fleet,
    )
    lh = [d for d in result.detonations if d.pass_kind == "laserhead"]
    assert lh == []
    # Nothing consumed.
    assert len(mg.mines) == 2


def test_per_ship_interleaving_warhead_then_laserhead():
    """Per-ship pass order: warhead first, then laserhead."""
    hex_c = HexCoord(0, 0)
    mines = [
        _make_mine_dict("warhead", damage=10),
        _make_laserhead_mine("laser", damage=10),
    ]
    mg = _make_mine_group_at(
        hex_c, owner_id=1, mine_dicts=mines, sensitivity="HIGH",
        threshold=0.0,
    )
    ship = _StubShip("s", max_hp=400, total_defense_score=0.0)
    fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=10)
    enemy = _make_empire(1, deployed_groups=[mg])
    player = _make_empire(0, fleets=[fleet])

    rng = random.Random()
    rng.random = lambda: 0.0
    rng.randrange = lambda n: 0

    r = MinefieldResolver(rng=rng)
    result = r.resolve_minefield_entry(
        galaxy=None, empires=[enemy, player], fleet=fleet,
    )
    kinds = [d.pass_kind for d in result.detonations]
    assert kinds == ["warhead", "laserhead"]


def test_statistical_dread_triggers_more_than_destroyer():
    """Over many trials, dreadnought triggers more than destroyer."""
    hex_c = HexCoord(0, 0)
    trials = 200

    def trigger_rate(ship_factory):
        triggers = 0
        for seed in range(trials):
            mines = [_make_mine_dict("m", damage=10) for _ in range(10)]
            mg = _make_mine_group_at(
                hex_c, owner_id=1, mine_dicts=mines, fleet_id=1000 + seed,
            )
            ship = ship_factory(f"s_{seed}")
            fleet = _make_fleet_at(hex_c, owner_id=0, ships=[ship], fleet_id=seed + 1)
            enemy_emp = _make_empire(1, deployed_groups=[mg])
            player_emp = _make_empire(0, fleets=[fleet])
            r = MinefieldResolver(rng=random.Random(seed))
            res = r.resolve_minefield_entry(
                galaxy=None, empires=[enemy_emp, player_emp], fleet=fleet,
            )
            if res.detonations:
                triggers += 1
        return triggers / trials

    destroyer_rate = trigger_rate(
        lambda i: _StubShip(i, size_diameter=120.0, accel=30.0, turn_speed=90.0)
    )
    dread_rate = trigger_rate(
        lambda i: _StubShip(i, size_diameter=400.0, accel=10.0, turn_speed=30.0)
    )
    assert dread_rate > destroyer_rate, (
        f"dread={dread_rate} should exceed destroyer={destroyer_rate}"
    )
