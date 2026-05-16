"""PROJ-FMS-B Phase 5 — ramming E2E integration test.

End-to-end ramming: a fighter with RamTargetAbility + multiple
Warheads is told to ram an enemy frigate. The resolver intercepts,
applies each warhead's damage to the target, and destroys the rammer.
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
        self, name, x=0.0, y=0.0, hp=100.0, radius=10.0,
        has_ram=False, warhead_damages=(), instance_id=None,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.radius = radius
        self.is_alive = True
        self.instance_id = instance_id or name
        comps = []
        if has_ram:
            ram = _StubAbility.make("RamTargetAbility")
            ram.target_id = None
            comps.append(_StubComponent([ram]))
        for d in warhead_damages:
            wh = _StubAbility.make("WarheadAbility")
            wh.damage = d
            comps.append(_StubComponent([wh]))
        self.layers = {"CORE": _StubLayer(comps)}


def test_kamikaze_fighter_rams_frigate_e2e():
    """Fighter w/ 2 warheads + RamTarget rams frigate, both warheads detonate."""
    resolver = RamTargetResolver()
    fighter = _StubShip(
        name="kamikaze_fighter", x=0.0, y=0.0,
        has_ram=True, warhead_damages=(75.0, 60.0), hp=20.0, radius=5.0,
    )
    frigate = _StubShip(
        name="enemy_frigate", x=8.0, y=0.0, hp=300.0, radius=15.0,
    )

    # 1. Set ram target.
    assert resolver.set_ram_target(fighter, frigate) is True

    # 2. Process tick — collision occurs because (5+15)>8.
    events = resolver.process_ramming_tick([fighter])
    assert len(events) == 1
    ev = events[0]
    assert ev["type"] == "ram_collision"
    assert ev["warheads_applied"] == [75.0, 60.0]

    # 3. Frigate took 75+60 = 135 damage.
    assert frigate.hp == 300.0 - 135.0
    # 4. Fighter destroyed.
    assert not fighter.is_alive


def test_target_dies_before_collision_clears_ram_target():
    """If target dies before collision, the rammer reverts to default AI."""
    resolver = RamTargetResolver()
    fighter = _StubShip(
        name="rammer", x=0.0, y=0.0,
        has_ram=True, warhead_damages=(50.0,),
    )
    frigate = _StubShip(name="frigate", x=10000.0, y=0.0, hp=300.0)
    resolver.set_ram_target(fighter, frigate)
    # Mark target dead from other damage.
    frigate.is_alive = False
    events = resolver.process_ramming_tick([fighter])
    assert any(e["type"] == "ram_target_cleared" for e in events)
    assert fighter.ram_target is None


def test_battle_engine_auto_attaches_ram_resolver():
    """PROJ-FMS-B audit Fix 3: every ``BattleEngine`` instance auto-
    instantiates a :class:`RamTargetResolver` and ticks it during
    :meth:`update`. Pre-fix the resolver existed but had no production
    caller, so the player-facing kamikaze flow was non-functional.
    """
    from game.simulation.systems.battle_engine import BattleEngine
    from game.simulation.systems.battle_end_conditions import (
        TeamEliminatedCondition,
    )
    from unittest.mock import patch, Mock

    with patch("game.simulation.systems.battle_engine.BattleLogger"):
        engine = BattleEngine()

    # ram_resolver is wired by default.
    assert engine.ram_resolver is not None
    assert isinstance(engine.ram_resolver, RamTargetResolver)

    # Set up minimal battle state.
    engine.ships = []
    engine.ai_controllers = []
    engine.tick_counter = 0
    engine.end_condition = TeamEliminatedCondition()
    engine.recent_beams = []

    # Place a fighter rammer adjacent to a frigate target. We avoid
    # giving them a real ``position`` attribute so the resolver
    # falls back to (x, y) coords — keeps the test free of pygame
    # Vector2 plumbing that's irrelevant to this fix.
    fighter = _StubShip(
        name="fighter", x=0.0, y=0.0,
        has_ram=True, warhead_damages=(75.0,), hp=20.0, radius=5.0,
    )
    fighter.team_id = 0
    fighter.update = Mock()
    fighter.get_all_components = Mock(return_value=[])
    fighter.just_fired_projectiles = []
    frigate = _StubShip(
        name="frigate", x=8.0, y=0.0, hp=300.0, radius=15.0,
    )
    frigate.team_id = 1
    frigate.update = Mock()
    frigate.get_all_components = Mock(return_value=[])
    frigate.just_fired_projectiles = []
    engine.ships = [fighter, frigate]

    # Action surface: set_ram_target via the engine.
    assert engine.set_ram_target(fighter, frigate) is True
    assert fighter.ram_target is frigate

    # Tick the engine — _run_ramming_tick fires (collision range check
    # passes: 5+15 > 8). Bypass the full tick-phase chain by calling
    # _run_ramming_tick directly so we exercise the wiring without
    # depending on AI / projectile / weapon-fire scaffolding.
    engine._run_ramming_tick()

    # Damage applied + rammer destroyed.
    assert frigate.hp == 300.0 - 75.0
    assert not fighter.is_alive


def test_battle_engine_set_ram_target_rejects_when_no_ram_ability():
    """Action surface returns False (no state mutated) when the rammer
    lacks ``RamTargetAbility``. The rammer remains alive and the
    target's hp is untouched."""
    from game.simulation.systems.battle_engine import BattleEngine
    from unittest.mock import patch

    with patch("game.simulation.systems.battle_engine.BattleLogger"):
        engine = BattleEngine()

    inert = _StubShip(name="inert", has_ram=False, warhead_damages=(50.0,))
    frigate = _StubShip(name="frigate", x=5.0, y=0.0, hp=300.0)

    assert engine.set_ram_target(inert, frigate) is False
    # No ram_target stashed on the inert ship — set_ram_target failed.
    assert getattr(inert, "ram_target", None) is None
    assert frigate.hp == 300.0


def test_fighter_with_warhead_but_no_ram_ability_does_nothing():
    """Inert payload: warhead present, RamTarget absent -> no damage on contact."""
    resolver = RamTargetResolver()
    fighter = _StubShip(
        name="warhead_only", x=0.0, y=0.0,
        has_ram=False, warhead_damages=(50.0,),
    )
    frigate = _StubShip(name="frigate", x=5.0, y=0.0, hp=300.0)
    # set_ram_target should fail.
    assert resolver.set_ram_target(fighter, frigate) is False
    events = resolver.process_ramming_tick([fighter])
    assert events == []
    assert frigate.hp == 300.0
    assert fighter.is_alive
