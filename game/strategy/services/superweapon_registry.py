"""SuperweaponRegistry — declarative table for strategic superweapon dispatch.

PROJ-364 Phase 2.

Mirrors the ``stabilizer_registry`` pattern: a frozen dataclass spec, an
immutable tuple registry, and a single lookup function. Adding a new
strategic superweapon becomes a one-row edit — Phase 3 wires the
``SuperweaponOrderProcessor`` to consume this table.

Scope: the 5 strategic superweapons that share a common prologue
(get-order → check-type → resolve-target → check-stabilizer →
find-ability-ship → effect → finalize). ``SELF_DESTRUCT`` is a structural
outlier (no ability check, no stabilizer block, no galaxy mutation) and is
intentionally OUT of this registry.

The ``ability_name`` field is ``None`` for ``STELLERATE_STAR``: that weapon
delegates to ``system_destroyer`` rather than calling
``SuperweaponValidator.find_ship_with_ability`` directly. The Phase 3
dispatcher skips the ability-ship lookup when ``ability_name is None``.
"""
from __future__ import annotations

from dataclasses import dataclass

from game.strategy.data.order_types import OrderType
from game.strategy.events.event_types import EventType


@dataclass(frozen=True)
class SuperweaponSpec:
    """Declarative spec for a strategic superweapon.

    Attributes:
        order_type: The ``OrderType`` this superweapon executes.
        ability_name: Component-ability name to look up via
            ``SuperweaponValidator.find_ship_with_ability``. ``None`` if
            the weapon dispatches via a different path
            (``STELLERATE_STAR`` -> ``system_destroyer``); the dispatcher
            skips the ability-ship lookup in that case.
        target_type: Shape of ``order.target`` — one of:
            - ``'planet'``: target is a ``Planet`` reference (``IMPLODE_PLANET``).
            - ``'dict'``:   target is a parameters dict (``OPEN_WARP_POINT``,
                            ``CLOSE_WARP_POINT``).
            - ``'none'``:   no target resolution; weapon acts on fleet
                            location (``STELLERATE_STAR``,
                            ``CREATE_DYSON_SPHERE``).
        consume_ship: ``True`` if the weapon destroys the carrying ship
            (suicide weapon — ``STELLERATE_STAR`` only). ``False`` for
            non-suicide superweapons whose ship is preserved for reuse.
        event_type: ``EventType`` emitted on success. Drives the Phase 3
            dispatcher's call to ``_finalize_superweapon``.
        stabilizer_blocks: ``OrderType`` values that any blocking
            stabilizer keys on. For all current weapons this is the
            singleton ``(self.order_type,)`` since stabilizers map by
            order type via ``stabilizer_registry``; the field is kept
            explicit for symmetry with the StabilizerSpec pattern and to
            allow future divergence (a single weapon shielded by multiple
            stabilizer order types).
    """
    order_type: OrderType
    ability_name: str | None
    target_type: str  # 'planet' | 'dict' | 'none'
    consume_ship: bool
    event_type: EventType
    stabilizer_blocks: tuple[OrderType, ...]


# Authoritative table. Adding a strategic superweapon = append a row +
# implement the Phase 3 effect closure on SuperweaponOrderProcessor.
SUPERWEAPONS: tuple[SuperweaponSpec, ...] = (
    SuperweaponSpec(
        order_type=OrderType.IMPLODE_PLANET,
        ability_name="DestroyPlanet",
        target_type="planet",
        consume_ship=False,
        event_type=EventType.PLANET_DESTROYED,
        stabilizer_blocks=(OrderType.IMPLODE_PLANET,),
    ),
    SuperweaponSpec(
        order_type=OrderType.STELLERATE_STAR,
        ability_name=None,  # Dispatched via system_destroyer; effect closure handles ship discovery.
        target_type="none",
        consume_ship=True,  # Suicide weapon.
        event_type=EventType.STAR_DESTROYED,
        stabilizer_blocks=(OrderType.STELLERATE_STAR,),
    ),
    SuperweaponSpec(
        order_type=OrderType.OPEN_WARP_POINT,
        ability_name="OpenWarpPoint",
        target_type="dict",
        consume_ship=False,
        event_type=EventType.WARP_POINT_OPENED,
        stabilizer_blocks=(OrderType.OPEN_WARP_POINT,),
    ),
    SuperweaponSpec(
        order_type=OrderType.CLOSE_WARP_POINT,
        ability_name="CloseWarpPoint",
        target_type="dict",
        consume_ship=False,
        event_type=EventType.WARP_POINT_CLOSED,
        stabilizer_blocks=(OrderType.CLOSE_WARP_POINT,),
    ),
    SuperweaponSpec(
        order_type=OrderType.CREATE_DYSON_SPHERE,
        ability_name="CreateDysonSphere",
        target_type="none",
        consume_ship=False,
        event_type=EventType.DYSON_SPHERE_CREATED,
        stabilizer_blocks=(OrderType.CREATE_DYSON_SPHERE,),
    ),
)


def find_superweapon_spec(order_type: OrderType) -> SuperweaponSpec | None:
    """Return the spec for ``order_type``, or ``None`` if not registered.

    Linear scan over ``SUPERWEAPONS`` — only 5 entries; no index needed.
    Returns ``None`` for ``SELF_DESTRUCT`` (intentionally out of registry)
    and for any non-superweapon order type.
    """
    for spec in SUPERWEAPONS:
        if spec.order_type == order_type:
            return spec
    return None


__all__ = [
    "SuperweaponSpec",
    "SUPERWEAPONS",
    "find_superweapon_spec",
]
