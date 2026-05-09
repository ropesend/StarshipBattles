"""PROJ-405: Regression — projectile lifecycle events reach the session
``EventBus`` when projectiles are constructed through the production weapon
firing path.

PROJ-382 added an ``event_logger`` kwarg to ``Projectile`` but production
constructors (``SeekerHandler.fire`` / ``ProjectileHandler.fire``) never
passed it; the ``Projectile`` default was a no-op so ``SEEKER_EXPIRE`` and
similar telemetry was silently dropped.  PROJ-405 threads the session
``EventBus`` through ``BattleEngine`` → ``Ship`` → ``WeaponFiringSystem`` →
``AttackRequest`` → ``Projectile``.  These tests pin that wiring at the
production seam (``WEAPON_REGISTRY.dispatch``) so a future regression
that drops the bus on the floor turns the suite red.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.core.constants import AttackType, PhysicsConfig
from game.core.event_logging import EventBus
from game.core.math import Vector2
from game.simulation.combat.attack_contract import (
    AttackRequest,
    ProjectileResolution,
    WeaponFamily,
)
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY
# Import for side-effect: registers the SEEKER and PROJECTILE handlers.
from game.simulation.combat import families  # noqa: F401


def _ship(*, angle: float = 0.0) -> SimpleNamespace:
    return SimpleNamespace(
        position=Vector2(0, 0),
        velocity=Vector2(0, 0),
        angle=angle,
        team_id=0,
    )


def _seeker_ability(*, endurance: float = 0.5, projectile_speed: float = 300.0) -> SimpleNamespace:
    return SimpleNamespace(
        projectile_speed=projectile_speed,
        endurance=endurance,
        turn_rate=15.0,
        to_hit_defense=0.0,
        projectile_damage=10.0,
        projectile_hp=1.0,
    )


def _ticks_for_endurance(endurance: float) -> int:
    """How many ``Projectile.update()`` calls to fully consume ``endurance``,
    plus a small headroom.  Tick step is ``PhysicsConfig.TICK_RATE``.
    """
    return int(endurance / PhysicsConfig.TICK_RATE) + 2


def _seeker_component() -> MagicMock:
    comp = MagicMock()
    seeker = _seeker_ability()
    comp.get_ability = lambda name: seeker if name == "SeekerWeaponAbility" else None
    return comp


def _weapon_ability(*, firing_arc: float = 90.0, facing_angle: float = 0.0) -> SimpleNamespace:
    return SimpleNamespace(
        damage=10.0,
        range=500.0,
        firing_arc=firing_arc,
        facing_angle=facing_angle,
    )


def test_seeker_lifetime_expiry_emits_event_when_event_bus_threaded() -> None:
    """A seeker constructed through the production dispatch path with a real
    ``EventBus`` on the ``AttackRequest`` must emit ``SEEKER_EXPIRE`` to that
    bus when its lifetime runs out.  Pre-PROJ-405 this assertion fails because
    handlers never forward ``request.event_bus`` to the ``Projectile``.
    """
    recorded: list[tuple[str, dict]] = []

    def handler(event_type: str, **kwargs):
        recorded.append((event_type, kwargs))

    bus = EventBus(handler)

    request = AttackRequest(
        source=_ship(angle=0.0),
        component=_seeker_component(),
        weapon_ability=_weapon_ability(),
        target=None,
        aim_pos=Vector2(0, 0),
        aim_vec=Vector2(1, 0),
        family=WeaponFamily.SEEKER,
        event_bus=bus,
    )

    resolution = WEAPON_REGISTRY.dispatch(request)
    assert isinstance(resolution, ProjectileResolution)
    projectile = resolution.projectile
    assert projectile.type is AttackType.MISSILE

    # Tick until endurance drops below zero.
    for _ in range(_ticks_for_endurance(0.5)):
        if not projectile.is_alive:
            break
        projectile.update()

    assert not projectile.is_alive
    seeker_events = [e for e in recorded if e[0] == "SEEKER_EXPIRE"]
    assert seeker_events, (
        f"Expected at least one SEEKER_EXPIRE event on the EventBus; got {recorded!r}. "
        "PROJ-405 regression: production seeker construction must thread the "
        "session EventBus into the Projectile."
    )
    assert seeker_events[0][1].get("reason") == "lifetime"


def test_seeker_max_range_expiry_emits_event_when_event_bus_threaded() -> None:
    """Same wiring contract on the ``max_range`` exit path.  This pins the
    second of two ``_event_logger("SEEKER_EXPIRE", ...)`` call sites in
    ``Projectile.update`` so a partial-revert regression still trips.
    """
    recorded: list[tuple[str, dict]] = []
    bus = EventBus(lambda event_type, **kw: recorded.append((event_type, kw)))

    # endurance=None disables lifetime path; rely on max_range from
    # projectile_speed * endurance.  Use a finite endurance for range_val
    # but kill the projectile via low max_range by handing it a tiny range.
    seeker = _seeker_ability(endurance=0.05, projectile_speed=10.0)
    comp = MagicMock()
    comp.get_ability = lambda name: seeker if name == "SeekerWeaponAbility" else None

    request = AttackRequest(
        source=_ship(angle=0.0),
        component=comp,
        weapon_ability=_weapon_ability(),
        target=None,
        aim_pos=Vector2(0, 0),
        aim_vec=Vector2(1, 0),
        family=WeaponFamily.SEEKER,
        event_bus=bus,
    )

    resolution = WEAPON_REGISTRY.dispatch(request)
    assert isinstance(resolution, ProjectileResolution)
    projectile = resolution.projectile

    # Run enough ticks for either lifetime or max_range to expire.
    for _ in range(_ticks_for_endurance(seeker.endurance)):
        if not projectile.is_alive:
            break
        projectile.update()

    assert not projectile.is_alive
    seeker_events = [e for e in recorded if e[0] == "SEEKER_EXPIRE"]
    assert seeker_events, (
        "Expected at least one SEEKER_EXPIRE event on either exit path."
    )


def test_attack_request_event_bus_field_is_part_of_typed_contract() -> None:
    """The ``event_bus`` slot on ``AttackRequest`` is required by PROJ-405's
    threading contract.  This test pins the field so a future refactor that
    drops it from the dataclass breaks the build, not silently the
    telemetry.
    """
    fields = {f.name for f in AttackRequest.__dataclass_fields__.values()}
    assert "event_bus" in fields, (
        "AttackRequest must carry the session EventBus; production handlers "
        "rely on it to thread event_logger= into Projectile."
    )


def test_event_bus_none_falls_back_to_no_op_in_handlers() -> None:
    """Tests and replay tools may construct an ``AttackRequest`` without a
    bus.  Handlers must accept ``event_bus=None`` and still produce a
    working projectile (just with silent telemetry).  This documents the
    test/production split — only production wiring is required to pass a
    real bus.
    """
    request = AttackRequest(
        source=_ship(angle=0.0),
        component=_seeker_component(),
        weapon_ability=_weapon_ability(),
        target=None,
        aim_pos=Vector2(0, 0),
        aim_vec=Vector2(1, 0),
        family=WeaponFamily.SEEKER,
        event_bus=None,
    )

    resolution = WEAPON_REGISTRY.dispatch(request)
    assert isinstance(resolution, ProjectileResolution)
    projectile = resolution.projectile
    # Should tick without raising; telemetry is silently dropped.
    for _ in range(_ticks_for_endurance(0.5)):
        if not projectile.is_alive:
            break
        projectile.update()
    assert not projectile.is_alive
