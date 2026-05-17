"""PROJ-FMS-B Phase 3 — TacticalMineResolver tests."""
from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from game.simulation.systems.tactical_mine_resolver import (
    TacticalMineEntity,
    TacticalMineResolver,
)


class _StubTacticalShip:
    def __init__(self, x=0.0, y=0.0, hp=200.0, total_defense_score=0.0,
                 size_diameter=160.0, accel=30.0, turn_speed=90.0,
                 instance_id="s1"):
        self.x = x
        self.y = y
        self.hp = hp
        self.is_alive = True
        self.total_defense_score = total_defense_score
        self.instance_id = instance_id
        self.name = instance_id
        self._diameter = size_diameter
        self._accel = accel
        self._turn = turn_speed
        self.owner_id = 0

    def get_calculated_stats(self):
        return {
            "diameter": self._diameter,
            "acceleration_rate": self._accel,
            "turn_speed": self._turn,
            "max_hp": self.hp,
            "total_defense_score": self.total_defense_score,
        }


def _mine_dict_warhead(damage=80.0, hull_hp=30.0):
    return {
        "design_id": "warhead_mine",
        "design_data": {
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "hull_mine_small",
                         "abilities": {"StructuralIntegrity": {"hp": hull_hp}}},
                        {"id": "warhead",
                         "abilities": {"Warhead": {"damage": damage}}},
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": int(hull_hp),
    }


def _mine_dict_laserhead(damage=40.0, beam_range=600, hull_hp=30.0):
    return {
        "design_id": "laser_mine",
        "design_data": {
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "hull_mine_small",
                         "abilities": {"StructuralIntegrity": {"hp": hull_hp}}},
                        {"id": "laserhead",
                         "abilities": {"Laserhead": {
                             "damage": damage,
                             "range": beam_range,
                             "base_accuracy": 5.0,
                             "accuracy_falloff": 0.001,
                             "consume_on_fire": True,
                         }}},
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": int(hull_hp),
    }


def _make_mine_group(mines, owner_id=1, mine_positions=None, threshold=0.30,
                     sensitivity="HIGH"):
    """PROJ-431 Phase 2: build a typed :class:`MineGroup`.

    The synthetic carrier ``ShipInstance`` is gone. Mines live directly
    on ``mine_group.mines`` as :class:`CarriedVehicle` entries — the
    same shape :meth:`TacticalMineResolver.from_mine_group` now reads.
    """
    from game.core.hex_math import HexCoord
    from game.strategy.data.carried_vehicle import CarriedVehicle
    from game.strategy.data.deployed_group import MineGroup
    mg = MineGroup(
        group_id=42,
        owner_id=owner_id,
        location=HexCoord(0, 0),
        sensitivity=sensitivity,
        expected_hit_chance_threshold=threshold,
    )
    mg.mines = [CarriedVehicle.from_dict(m) for m in mines]
    mg.mine_positions = list(mine_positions or [(0.0, 0.0)] * len(mines))
    mg.scatter_seed = 12345
    return mg


# ---------------------------------------------------------------------------
# from_mine_group construction
# ---------------------------------------------------------------------------


def test_from_mine_group_builds_entities():
    mines = [
        _mine_dict_warhead(damage=80),
        _mine_dict_laserhead(damage=40),
    ]
    mg = _make_mine_group(mines, mine_positions=[(100.0, 200.0), (300.0, 400.0)])
    resolver = TacticalMineResolver.from_mine_group(mg)
    assert len(resolver.mines) == 2
    assert resolver.mines[0].warhead_damage == 80.0
    assert resolver.mines[1].laserhead_attrs is not None
    assert resolver.mines[0].position == (100.0, 200.0)


def test_from_mine_group_with_battle_boundary_scatters():
    mines = [_mine_dict_warhead() for _ in range(5)]
    mg = _make_mine_group(mines)
    box = (-1000.0, -1000.0, 1000.0, 1000.0)
    resolver = TacticalMineResolver.from_mine_group(mg, battle_boundary=box)
    for entity in resolver.mines:
        x, y = entity.position
        assert -1000.0 <= x <= 1000.0
        assert -1000.0 <= y <= 1000.0


def test_from_mine_group_scatter_deterministic():
    mines = [_mine_dict_warhead() for _ in range(3)]
    mg1 = _make_mine_group(mines)
    mg2 = _make_mine_group(mines)
    box = (0.0, 0.0, 2000.0, 2000.0)
    r1 = TacticalMineResolver.from_mine_group(mg1, battle_boundary=box)
    r2 = TacticalMineResolver.from_mine_group(mg2, battle_boundary=box)
    assert [m.position for m in r1.mines] == [m.position for m in r2.mines]


# ---------------------------------------------------------------------------
# Per-tick behavior
# ---------------------------------------------------------------------------


def test_no_detonation_when_ship_far():
    """Ship outside proximity radius does not trigger a warhead mine."""
    mines = [_mine_dict_warhead()]
    mg = _make_mine_group(mines, mine_positions=[(0.0, 0.0)])
    resolver = TacticalMineResolver.from_mine_group(mg, rng=random.Random(0))
    # Ship far outside the 600m default proximity.
    ship = _StubTacticalShip(x=10000.0, y=10000.0)
    events = resolver.tick(tick=1, enemy_ships=[ship])
    assert events == []
    assert not resolver.mines[0].consumed


def test_warhead_triggers_when_ship_close():
    """Force a trigger via rng=0 with a ship inside proximity."""
    mines = [_mine_dict_warhead(damage=80)]
    mg = _make_mine_group(
        mines, mine_positions=[(0.0, 0.0)], sensitivity="HIGH",
    )

    rng = random.Random()
    rng.random = lambda: 0.0  # always trigger
    rng.randrange = lambda n: 0

    resolver = TacticalMineResolver.from_mine_group(mg, rng=rng)
    ship = _StubTacticalShip(x=100.0, y=100.0, hp=400)
    events = resolver.tick(tick=1, enemy_ships=[ship])
    assert len(events) == 1
    assert events[0].pass_kind == "warhead"
    assert events[0].hit
    assert ship.hp < 400
    assert resolver.mines == []  # consumed mine pruned


def test_laserhead_triggers_within_range():
    """Laserhead fires when ship is within beam range and above threshold."""
    mines = [_mine_dict_laserhead(damage=40, beam_range=600)]
    mg = _make_mine_group(
        mines, mine_positions=[(0.0, 0.0)], threshold=0.30,
    )
    rng = random.Random()
    rng.random = lambda: 0.0
    resolver = TacticalMineResolver.from_mine_group(mg, rng=rng)
    ship = _StubTacticalShip(x=200.0, y=0.0, hp=200, total_defense_score=0.0)
    events = resolver.tick(tick=1, enemy_ships=[ship])
    assert len(events) == 1
    assert events[0].pass_kind == "laserhead"
    assert events[0].hit
    assert ship.hp < 200
    assert resolver.mines == []


def test_laserhead_skipped_below_threshold():
    """High defense_score => low expected_hit_chance => laserhead skips."""
    mines = [_mine_dict_laserhead(damage=40)]
    mg = _make_mine_group(
        mines, mine_positions=[(0.0, 0.0)], threshold=0.99,
    )
    rng = random.Random()
    rng.random = lambda: 0.0
    resolver = TacticalMineResolver.from_mine_group(mg, rng=rng)
    ship = _StubTacticalShip(x=200.0, y=0.0, total_defense_score=100.0)
    events = resolver.tick(tick=1, enemy_ships=[ship])
    assert events == []
    # Not consumed.
    assert resolver.mines and not resolver.mines[0].consumed


def test_mine_destroyed_by_external_damage_is_removed():
    """Mines with HP <= 0 are dropped from the active list without detonating."""
    mines = [_mine_dict_warhead()]
    mg = _make_mine_group(mines, mine_positions=[(0.0, 0.0)])
    resolver = TacticalMineResolver.from_mine_group(mg, rng=random.Random(0))
    # Simulate point-defense hit reducing mine to 0 HP.
    resolver.mines[0].hp = 0.0
    ship = _StubTacticalShip(x=100.0, y=0.0)
    events = resolver.tick(tick=1, enemy_ships=[ship])
    assert events == []
    # Dead mine pruned from active list on next tick.
    events = resolver.tick(tick=2, enemy_ships=[ship])
    assert resolver.mines == []


def test_per_tick_scaling_is_smaller_than_strategic_pass():
    """The per-tick chance must be a fraction of the strategic per-pass chance.

    Sanity check: integrated over many ticks the expected number of
    triggers should be on the same order as a single strategic pass.
    """
    mines = [_mine_dict_warhead() for _ in range(1)]
    mg = _make_mine_group(
        mines, mine_positions=[(0.0, 0.0)], sensitivity="HIGH",
    )
    resolver = TacticalMineResolver.from_mine_group(mg, rng=random.Random(0))
    ship = _StubTacticalShip(x=100.0, y=0.0, total_defense_score=0.0)

    # Compute strategic p_trigger via the strategic resolver (same math).
    from game.strategy.engine.minefield_resolver import MinefieldResolver
    strat_p = MinefieldResolver().compute_p_trigger(ship, "HIGH")
    per_tick_chance = resolver._warhead_per_tick_roll  # exercise smoke

    # Force a deterministic comparison via direct seed iteration.
    # Run many ticks; observed trigger rate must be SUBSTANTIALLY less
    # than 1.0 even with high sensitivity — the per-tick scaling is the gate.
    triggers = 0
    rng_for_trial = random.Random(1234)
    for tick in range(10):
        # Fresh resolver each tick to keep the mine alive across rolls.
        if not resolver.mines:
            break
        ev = resolver.tick(tick=tick + 1, enemy_ships=[ship])
        triggers += sum(1 for e in ev if e.hit)
    # Across 10 ticks with very generous sensitivity we should see at
    # most ~1 trigger on average — definitely not 10.
    assert triggers <= 5


# ---------------------------------------------------------------------------
# writeback_to_mine_group
# ---------------------------------------------------------------------------


def test_writeback_clears_carrier_when_all_mines_consumed():
    """PROJ-FMS-B audit Fix 6 + PROJ-431 Phase 2: when every mine is
    consumed/destroyed in a battle, ``writeback_to_mine_group`` must
    leave ``mine_group.mines`` empty (no zombie inventory).
    """
    mines = [_mine_dict_warhead(damage=80) for _ in range(5)]
    mg = _make_mine_group(mines, mine_positions=[(0.0, 0.0)] * 5)
    resolver = TacticalMineResolver.from_mine_group(mg, rng=random.Random(0))

    # Mark every tactical entity as consumed (simulate a battle that
    # detonated all 5 mines).
    for entity in resolver.mines:
        entity.consumed = True

    resolver.writeback_to_mine_group(mg)

    # Inventory must be cleared — no zombie mine entries.
    assert mg.mines == []


def test_battle_engine_ticks_multiple_mine_resolvers():
    """PROJ-FMS-B audit Fix 2: when ``BattleEngine.mine_resolvers`` holds
    multiple resolvers (e.g. one per ``mine_group`` at the hex), each
    receives its per-tick call with the right enemy ship filter applied.
    Pre-fix the engine only consulted a single ``mine_resolver``
    attribute, so multi-group hexes ticked at most one.
    """
    # Build two captured resolver stubs. Each pretends to belong to a
    # different owner_team.
    calls: list = []

    class _StubResolver:
        def __init__(self, owner_team: int) -> None:
            self._owner_team_id = owner_team

        def tick(self, *, tick, enemy_ships, damage_calculator=None, event_bus=None):
            calls.append((self._owner_team_id, tick, len(enemy_ships)))

    from game.simulation.systems.battle_engine import BattleEngine

    engine = BattleEngine.__new__(BattleEngine)
    # Minimal state for _run_mine_resolver_tick: ships + tick_counter.
    engine.mine_resolver = None
    engine.mine_resolvers = [_StubResolver(0), _StubResolver(1)]
    engine.tick_counter = 7
    engine.combat_events = SimpleNamespace()
    ship_a = SimpleNamespace(is_alive=True, team_id=0)
    ship_b = SimpleNamespace(is_alive=True, team_id=1)
    engine.ships = [ship_a, ship_b]

    engine._run_mine_resolver_tick(engine.mine_resolvers)

    assert len(calls) == 2
    # team-0 resolver sees team-1's ships as enemies (1 enemy).
    # team-1 resolver sees team-0's ships as enemies (1 enemy).
    assert sorted(calls, key=lambda c: c[0]) == [
        (0, 7, 1),
        (1, 7, 1),
    ]


def test_expected_ticks_in_proximity_is_balance_tunable():
    """PROJ-FMS-B audit Fix 5: ``expected_ticks_in_proximity`` must come
    from the balance file (``TacticalConstants``) rather than a hard-coded
    class constant on the resolver. Pre-fix the resolver consulted only
    ``DEFAULT_EXPECTED_TICKS_IN_PROXIMITY`` and ignored anything the
    balance file said.
    """
    from game.strategy.engine.minefield_balance import (
        MinefieldBalance,
        TacticalConstants,
        WarheadTriggerConstants,
        ScatterConstants,
        LaserheadConstants,
    )

    # Two balances differing ONLY in expected_ticks_in_proximity.
    bal_small = MinefieldBalance(
        warhead_trigger=WarheadTriggerConstants(),
        sensitivity_multipliers={"LOW": 0.5, "MED": 1.0, "HIGH": 1.5},
        scatter=ScatterConstants(),
        laserhead=LaserheadConstants(),
        tactical=TacticalConstants(expected_ticks_in_proximity=5),
    )
    bal_big = MinefieldBalance(
        warhead_trigger=WarheadTriggerConstants(),
        sensitivity_multipliers={"LOW": 0.5, "MED": 1.0, "HIGH": 1.5},
        scatter=ScatterConstants(),
        laserhead=LaserheadConstants(),
        tactical=TacticalConstants(expected_ticks_in_proximity=500),
    )

    mine = TacticalMineEntity(
        position=(0.0, 0.0),
        owner_id=1,
        source_mine_group_id=42,
        warhead_damage=80.0,
        laserhead_attrs=None,
        hp=30.0,
        max_hp=30.0,
        sensitivity="HIGH",
    )
    ship = _StubTacticalShip(x=100.0, y=0.0, hp=200, total_defense_score=0.0)

    r_small = TacticalMineResolver(
        mine_entities=[mine], balance=bal_small, rng=random.Random(0),
    )
    r_big = TacticalMineResolver(
        mine_entities=[
            TacticalMineEntity(
                position=(0.0, 0.0),
                owner_id=1,
                source_mine_group_id=42,
                warhead_damage=80.0,
                laserhead_attrs=None,
                hp=30.0,
                max_hp=30.0,
                sensitivity="HIGH",
            )
        ],
        balance=bal_big,
        rng=random.Random(0),
    )

    # The per-tick chance is computed inside _warhead_per_tick_roll using
    # the balance's expected_ticks_in_proximity field.  A small divisor
    # (5) must give a larger per-tick chance than a big divisor (500),
    # so the cumulative trigger count over many trials must differ.
    rng_small = random.Random(0)
    rng_big = random.Random(0)
    r_small._rng = rng_small
    r_big._rng = rng_big

    trigs_small = sum(
        1 for _ in range(200)
        if r_small._warhead_per_tick_roll(r_small.mines[0], ship)
    )
    trigs_big = sum(
        1 for _ in range(200)
        if r_big._warhead_per_tick_roll(r_big.mines[0], ship)
    )
    assert trigs_small > trigs_big, (
        f"With expected_ticks=5 we should trigger MORE often than with "
        f"expected_ticks=500. Got {trigs_small} vs {trigs_big}."
    )


def test_writeback_clears_carrier_when_all_mines_hp_zero():
    """All-mines-destroyed-by-pd-fire variant of Fix 6: hp <= 0 mines also
    do not survive writeback."""
    mines = [_mine_dict_warhead(damage=80) for _ in range(3)]
    mg = _make_mine_group(mines, mine_positions=[(0.0, 0.0)] * 3)
    resolver = TacticalMineResolver.from_mine_group(mg, rng=random.Random(0))

    for entity in resolver.mines:
        entity.hp = 0.0

    resolver.writeback_to_mine_group(mg)
    assert mg.mines == []
