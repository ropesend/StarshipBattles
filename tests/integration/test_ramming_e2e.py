"""Ramming E2E integration test — symmetric universal model.

QA 2026-05-16 Obs 1b: the original PROJ-FMS-B model gated ramming on
``RamTargetAbility`` and auto-destroyed the rammer. The new model:

* Any ship can be assigned a ram target (no component gate).
* Collision exchanges damage symmetrically (shields+HP+warheads on
  both sides, sampled at collision instant).
* All warheads on both sides are consumed (one-shot).
* Survival is possible: a heavy target with ample absorption survives
  a kamikaze ram; the kamikaze is annihilated by the target's mass.
"""
from __future__ import annotations

from game.simulation.combat.ram_target_resolver import RamTargetResolver


class _StubAbility:
    """A simple ability instance whose class name matches the lookup."""

    @classmethod
    def make(cls, ability_class_name: str, **kwargs):
        t = type(ability_class_name, (object,), {})
        inst = t()
        for k, v in kwargs.items():
            setattr(inst, k, v)
        return inst


class _StubComponent:
    def __init__(self, abilities):
        self.ability_instances = abilities


class _StubLayer:
    def __init__(self, components):
        self.components = components


class _StubShip:
    def __init__(
        self,
        name,
        x=0.0,
        y=0.0,
        hp=100.0,
        current_shields=0.0,
        radius=10.0,
        warhead_damages=(),
        instance_id=None,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.current_shields = current_shields
        self.radius = radius
        self.is_alive = True
        self.instance_id = instance_id or name
        comps = []
        for d in warhead_damages:
            wh = _StubAbility.make("WarheadAbility", damage=d, consumed=False)
            comps.append(_StubComponent([wh]))
        self.layers = {"CORE": _StubLayer(comps)}


def test_kamikaze_fighter_rams_frigate_e2e():
    """Fighter w/ 2 warheads rams frigate — fighter destroyed, frigate
    chipped. No ``RamTargetAbility`` needed (Obs 1b)."""
    resolver = RamTargetResolver()
    fighter = _StubShip(
        name="kamikaze_fighter", x=0.0, y=0.0,
        warhead_damages=(75.0, 60.0),
        hp=20.0, current_shields=0.0, radius=5.0,
    )
    frigate = _StubShip(
        name="enemy_frigate", x=8.0, y=0.0,
        hp=300.0, current_shields=0.0, radius=15.0,
    )

    assert resolver.set_ram_target(fighter, frigate) is True

    events = resolver.process_ramming_tick([fighter])
    assert len(events) == 1
    ev = events[0]
    assert ev["type"] == "ram_collision"

    # Fighter delivered shields + HP + warheads = 0 + 20 + 75 + 60 = 155.
    assert ev["rammer_delivered"] == 155.0
    # Frigate delivered 0 + 300 + 0 = 300. Fighter only had 20 HP -> dead.
    assert ev["target_delivered"] == 300.0

    # Frigate absorbed 155 of its 300 HP -> 145 left.
    assert frigate.hp == 300.0 - 155.0
    assert frigate.is_alive
    # Fighter wiped.
    assert fighter.hp == 0.0
    assert not fighter.is_alive


def test_target_dies_before_collision_clears_ram_target():
    """If target dies before collision, the rammer reverts to default AI."""
    resolver = RamTargetResolver()
    fighter = _StubShip(name="rammer", x=0.0, y=0.0, warhead_damages=(50.0,))
    frigate = _StubShip(name="frigate", x=10000.0, y=0.0, hp=300.0)
    resolver.set_ram_target(fighter, frigate)
    frigate.is_alive = False
    events = resolver.process_ramming_tick([fighter])
    assert any(e["type"] == "ram_target_cleared" for e in events)
    assert fighter.ram_target is None


def test_battle_engine_auto_attaches_ram_resolver():
    """``BattleEngine`` auto-instantiates ``RamTargetResolver`` and
    ticks it during :meth:`update`. The action surface
    ``engine.set_ram_target(...)`` routes through the resolver."""
    from game.simulation.systems.battle_engine import BattleEngine
    from game.simulation.systems.battle_end_conditions import (
        TeamEliminatedCondition,
    )
    from unittest.mock import patch, Mock

    with patch("game.simulation.systems.battle_engine.BattleLogger"):
        engine = BattleEngine()

    assert engine.ram_resolver is not None
    assert isinstance(engine.ram_resolver, RamTargetResolver)

    engine.ships = []
    engine.ai_controllers = []
    engine.tick_counter = 0
    engine.end_condition = TeamEliminatedCondition()
    engine.recent_beams = []

    fighter = _StubShip(
        name="fighter", x=0.0, y=0.0,
        warhead_damages=(75.0,),
        hp=20.0, current_shields=0.0, radius=5.0,
    )
    fighter.team_id = 0
    fighter.update = Mock()
    fighter.get_all_components = Mock(return_value=[])
    fighter.just_fired_projectiles = []
    frigate = _StubShip(
        name="frigate", x=8.0, y=0.0,
        hp=300.0, current_shields=0.0, radius=15.0,
    )
    frigate.team_id = 1
    frigate.update = Mock()
    frigate.get_all_components = Mock(return_value=[])
    frigate.just_fired_projectiles = []
    engine.ships = [fighter, frigate]

    assert engine.set_ram_target(fighter, frigate) is True
    assert fighter.ram_target is frigate

    engine._run_ramming_tick()

    # Symmetric exchange: fighter delivered 0+20+75 = 95; frigate
    # delivered 0+300 = 300. Both sides eat the other's delivery.
    assert frigate.hp == 300.0 - 95.0
    assert frigate.is_alive
    assert fighter.hp == 0.0
    assert not fighter.is_alive


def test_battle_engine_set_ram_target_succeeds_on_any_ship():
    """Obs 1b: ramming is no longer gated on ``RamTargetAbility`` —
    any alive ship can be assigned a ram target via the engine action
    surface."""
    from game.simulation.systems.battle_engine import BattleEngine
    from unittest.mock import patch

    with patch("game.simulation.systems.battle_engine.BattleLogger"):
        engine = BattleEngine()

    rammer = _StubShip(name="any_ship", warhead_damages=())
    target = _StubShip(name="frigate", x=5.0, y=0.0, hp=300.0)

    assert engine.set_ram_target(rammer, target) is True
    assert rammer.ram_target is target


def test_fighter_with_warhead_kinetic_only_still_collides():
    """A fighter with no warhead still rams for shields+HP kinetic
    damage. Obs 1b removed the inert-payload edge case (which under
    the old model required RamTargetAbility to even attempt a ram)."""
    resolver = RamTargetResolver()
    fighter = _StubShip(
        name="warhead_only", x=0.0, y=0.0,
        warhead_damages=(),
        hp=30.0, current_shields=10.0,
    )
    frigate = _StubShip(name="frigate", x=5.0, y=0.0, hp=300.0, current_shields=0.0)

    assert resolver.set_ram_target(fighter, frigate) is True
    events = resolver.process_ramming_tick([fighter])
    assert len(events) == 1
    # Fighter kinetic = 10 shields + 30 hp = 40 delivered.
    assert events[0]["rammer_delivered"] == 40.0
    assert frigate.hp == 300.0 - 40.0
