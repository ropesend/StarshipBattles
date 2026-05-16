"""PROJ-FMS-B Phase 4 — RamTargetResolver tests."""
from __future__ import annotations

import pytest

from game.simulation.combat.ram_target_resolver import RamTargetResolver


class _StubAbility:
    """Stand-in for an ability instance that exposes the class name."""

    def __init__(self, cls_name: str, **kwargs):
        self.__class__ = type(cls_name, (object,), {})
        # Set attributes
        for k, v in kwargs.items():
            setattr(self, k, v)


class _StubComponent:
    def __init__(self, abilities=None):
        self.ability_instances = abilities or []


class _StubLayer:
    def __init__(self, components=None):
        self.components = components or []


class _StubShip:
    def __init__(self, name="ship", x=0.0, y=0.0, hp=100.0,
                 radius=10.0, has_ram=False, warheads=(),
                 instance_id=None):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.radius = radius
        self.is_alive = True
        self.instance_id = instance_id or name

        layer_components = []
        if has_ram:
            # Build a RamTargetAbility-like instance whose class name matches.
            ram = type("RamTargetAbility", (object,), {})()
            ram.target_id = None
            layer_components.append(_StubComponent(abilities=[ram]))
        for damage in warheads:
            wh = type("WarheadAbility", (object,), {})()
            wh.damage = damage
            layer_components.append(_StubComponent(abilities=[wh]))
        self.layers = {"CORE": _StubLayer(components=layer_components)}


def test_set_ram_target_requires_ram_ability():
    resolver = RamTargetResolver()
    no_ram = _StubShip(name="rammer", has_ram=False)
    target = _StubShip(name="target")
    assert resolver.set_ram_target(no_ram, target) is False
    assert getattr(no_ram, "ram_target", None) is None


def test_set_ram_target_with_ability_succeeds():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", has_ram=True, warheads=(50.0,))
    target = _StubShip(name="target")
    assert resolver.set_ram_target(rammer, target) is True
    assert rammer.ram_target is target


def test_ram_target_cleared_when_target_dies():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", has_ram=True, warheads=(50.0,))
    target = _StubShip(name="target")
    resolver.set_ram_target(rammer, target)
    target.is_alive = False
    events = resolver.process_ramming_tick([rammer])
    assert any(e["type"] == "ram_target_cleared" for e in events)
    assert getattr(rammer, "ram_target", None) is None


def test_collision_applies_all_warheads():
    """Multiple warheads on rammer => each applies separately."""
    resolver = RamTargetResolver()
    rammer = _StubShip(
        name="rammer", x=0.0, y=0.0, has_ram=True, warheads=(50.0, 75.0), radius=10.0,
    )
    target = _StubShip(name="target", x=5.0, y=0.0, hp=500.0, radius=10.0)
    resolver.set_ram_target(rammer, target)
    events = resolver.process_ramming_tick([rammer])
    assert len(events) == 1
    assert events[0]["type"] == "ram_collision"
    assert events[0]["warheads_applied"] == [50.0, 75.0]
    assert target.hp == 500.0 - 125.0
    # Rammer destroyed.
    assert rammer.hp == 0.0
    assert not rammer.is_alive


def test_no_collision_when_target_far():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", x=0.0, y=0.0, has_ram=True, warheads=(50.0,))
    target = _StubShip(name="target", x=10000.0, y=0.0, hp=500.0)
    resolver.set_ram_target(rammer, target)
    events = resolver.process_ramming_tick([rammer])
    assert events == []
    assert rammer.is_alive
    assert target.hp == 500.0


def test_design_without_ram_ability_does_not_collide():
    """Even adjacent ships without RamTargetAbility don't auto-detonate."""
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", has_ram=False, warheads=(50.0,))
    target = _StubShip(name="target", x=5.0, y=0.0, hp=500.0)
    # set_ram_target should fail without the ability.
    assert resolver.set_ram_target(rammer, target) is False
    events = resolver.process_ramming_tick([rammer])
    assert events == []
    assert target.hp == 500.0


def test_self_target_rejected():
    resolver = RamTargetResolver()
    rammer = _StubShip(name="rammer", has_ram=True, warheads=(50.0,))
    assert resolver.set_ram_target(rammer, rammer) is False
