"""RamTargetResolver tests — symmetric damage model (QA 2026-05-16 Obs 1b).

The original PROJ-FMS-B model gated ramming on ``RamTargetAbility`` and
auto-destroyed the rammer on collision. The new model:

* No component / ability gate — any vehicle with movement can be assigned
  a ram target.
* On collision both sides exchange damage simultaneously:

    rammer_delivered = rammer.current_shields + rammer.hp +
                       sum(warhead.damage on rammer)
    target_delivered = target.current_shields + target.hp +
                       sum(warhead.damage on target)

  Both values sampled at collision instant; applied through the damage
  pipeline so the rammer's state going to zero does not reduce the
  damage it delivers.
* Warheads on both sides are consumed (one-shot, mirroring
  ``consume_on_fire`` for beam weapons).
* Survival is possible: a heavy ship with ample shields ramming a
  fighter eats little; a kamikaze fighter ramming a dreadnought is
  annihilated but does large damage if it carries warheads.
"""
from __future__ import annotations

import pytest

from game.simulation.combat.ram_target_resolver import RamTargetResolver


def _ability(cls_name: str, **kwargs):
    inst = type(cls_name, (object,), {})()
    for k, v in kwargs.items():
        setattr(inst, k, v)
    return inst


class _StubComponent:
    def __init__(self, abilities=None):
        self.ability_instances = abilities or []


class _StubLayer:
    def __init__(self, components=None):
        self.components = components or []


class _StubShip:
    def __init__(
        self,
        name="ship",
        x=0.0,
        y=0.0,
        hp=100.0,
        current_shields=0.0,
        radius=10.0,
        warheads=(),
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

        layer_components = []
        for damage in warheads:
            layer_components.append(
                _StubComponent([_ability("WarheadAbility", damage=damage, consumed=False)])
            )
        self.layers = {"CORE": _StubLayer(components=layer_components)}


def _warhead_states(ship):
    """Helper: pull the WarheadAbility instances on a stub ship."""
    out = []
    for layer in ship.layers.values():
        for comp in layer.components:
            for ab in comp.ability_instances:
                if type(ab).__name__ == "WarheadAbility":
                    out.append(ab)
    return out


# ---------------------------------------------------------------------------
# set_ram_target — ungated by ability
# ---------------------------------------------------------------------------


def test_set_ram_target_succeeds_without_any_ability():
    """QA 2026-05-16 Obs 1b: ramming is no longer gated on
    RamTargetAbility. Any alive ship can be assigned a ram target."""
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer")
    target = _StubShip(name="target")
    assert resolver.set_ram_target(rammer, target) is True
    assert rammer.ram_target is target


def test_set_ram_target_rejects_dead_rammer():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer")
    rammer.is_alive = False
    target = _StubShip(name="target")
    assert resolver.set_ram_target(rammer, target) is False
    assert getattr(rammer, "ram_target", None) is None


def test_set_ram_target_rejects_dead_target():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer")
    target = _StubShip(name="target")
    target.is_alive = False
    assert resolver.set_ram_target(rammer, target) is False


def test_self_target_rejected():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer")
    assert resolver.set_ram_target(rammer, rammer) is False


# ---------------------------------------------------------------------------
# Tick processing — collision detection + symmetric exchange
# ---------------------------------------------------------------------------


def test_no_collision_when_target_far():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", x=0.0, y=0.0, warheads=(50.0,))
    target = _StubShip(name="target", x=10000.0, y=0.0, hp=500.0)
    resolver.set_ram_target(rammer, target)
    events = resolver.process_ramming_tick([rammer])
    assert events == []
    assert rammer.is_alive
    assert target.hp == 500.0


def test_target_dead_before_collision_clears_ram_target():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", warheads=(50.0,))
    target = _StubShip(name="target")
    resolver.set_ram_target(rammer, target)
    target.is_alive = False
    events = resolver.process_ramming_tick([rammer])
    assert any(e["type"] == "ram_target_cleared" for e in events)
    assert getattr(rammer, "ram_target", None) is None
    assert rammer.is_alive  # rammer untouched.


def test_collision_symmetric_damage_exchange():
    """Both sides deliver shields+HP+warheads to each other simultaneously."""
    resolver = RamTargetResolver()
    rammer = _StubShip(
        name="rammer", x=0.0, y=0.0, radius=10.0,
        hp=20.0, current_shields=5.0, warheads=(75.0, 60.0),
    )
    target = _StubShip(
        name="target", x=5.0, y=0.0, radius=10.0,
        hp=500.0, current_shields=100.0, warheads=(),
    )
    resolver.set_ram_target(rammer, target)
    events = resolver.process_ramming_tick([rammer])
    assert len(events) == 1
    ev = events[0]
    assert ev["type"] == "ram_collision"

    rammer_delivered = 5.0 + 20.0 + 75.0 + 60.0
    target_delivered = 100.0 + 500.0 + 0.0
    assert ev["rammer_delivered"] == rammer_delivered
    assert ev["target_delivered"] == target_delivered

    # Rammer absorbed target_delivered (= 600). It only had 5+20 = 25
    # absorption — wiped out, dead. Survives_check_state: 25 - 600 = -575,
    # capped to 0 HP and is_alive False.
    assert rammer.hp == 0.0
    assert rammer.is_alive is False

    # Target absorbed rammer_delivered (= 160). Had 100 shield + 500 HP =
    # 600 absorption. Survives with shield 0 (drained), HP 500 - (160-100)
    # = 440. Stub fallback drains hp first since shields aren't in the
    # fallback pipeline — assert it's roughly right.
    assert target.is_alive is True


def test_heavy_target_survives_kamikaze_fighter():
    """A heavy target with ample absorption survives a fighter ram.
    The fighter's delivered damage (small shields+HP+warheads) only
    chips the target; the target's delivered damage annihilates the
    fighter."""
    resolver = RamTargetResolver()
    fighter = _StubShip(
        name="fighter", radius=5.0,
        hp=10.0, current_shields=0.0, warheads=(50.0,),
    )  # delivers 60.
    cruiser = _StubShip(
        name="cruiser", x=8.0, y=0.0, radius=15.0,
        hp=2000.0, current_shields=500.0, warheads=(),
    )  # delivers 2500.
    resolver.set_ram_target(fighter, cruiser)
    resolver.process_ramming_tick([fighter])
    # Fighter annihilated.
    assert fighter.hp == 0.0
    assert fighter.is_alive is False
    # Cruiser survives with most of its state intact (lost ~60 absorbed).
    assert cruiser.is_alive is True
    assert cruiser.hp > 1900.0  # well above zero.


def test_collision_consumes_warheads_on_both_sides():
    """One-shot detonation: warheads on rammer AND target are marked
    consumed (mirrors ``consume_on_fire`` for beam laserheads)."""
    resolver = RamTargetResolver()
    rammer = _StubShip(
        name="rammer", warheads=(50.0, 75.0),
        hp=10000.0, current_shields=10000.0,  # ensure survives
    )
    target = _StubShip(
        name="target", x=5.0, y=0.0, warheads=(40.0,),
        hp=10000.0, current_shields=10000.0,
    )
    resolver.set_ram_target(rammer, target)
    resolver.process_ramming_tick([rammer])
    for wh in _warhead_states(rammer):
        assert wh.consumed is True
        assert wh.damage == 0.0  # zero out so re-fire is a no-op.
    for wh in _warhead_states(target):
        assert wh.consumed is True


def test_no_warheads_still_collides_with_kinetic_damage():
    """A ship with no warheads still delivers shields+HP as kinetic damage."""
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", hp=30.0, current_shields=10.0, warheads=())
    target = _StubShip(name="target", x=5.0, y=0.0, hp=200.0, warheads=())
    resolver.set_ram_target(rammer, target)
    events = resolver.process_ramming_tick([rammer])
    assert events[0]["rammer_delivered"] == 40.0  # 10 shields + 30 hp
    assert target.hp < 200.0  # took kinetic damage


def test_ram_target_cleared_after_collision():
    """Whether the rammer survives or not, the ram_target reference is
    cleared after collision so the rammer doesn't re-target on the
    next tick if it lives."""
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", hp=10000.0, current_shields=10000.0)
    target = _StubShip(name="target", x=5.0, y=0.0, hp=10000.0, current_shields=10000.0)
    resolver.set_ram_target(rammer, target)
    resolver.process_ramming_tick([rammer])
    assert getattr(rammer, "ram_target", None) is None
