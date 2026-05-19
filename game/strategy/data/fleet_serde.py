"""Save/load helpers for ``Fleet``.

The serialization shape, validation, ship/order deserialization, and
hierarchy-restoration helpers live here. ``Fleet.to_dict`` /
``Fleet.from_dict`` are 1-line facades that call into this module.

PROJ-459 Phase 1 extracted these from ``game/strategy/data/fleet.py``,
mirroring the ``planet_serde.py`` precedent (PROJ-372). Save format is
byte-identical to pre-extraction output.

``resolve_order_references`` stays as a method on ``Fleet`` because it
mutates ``self.orders`` and is invoked late (post-load, after the galaxy
is fully constructed) rather than during deserialization. It already
delegates to ``OrderSerializer.resolve_order_references``; promoting it
into this module would only relocate a 2-line shim.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from game.core.error_codes import ErrorCode
from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord
from game.core.validation_helpers import require_keys
from game.strategy.data.ship_instance import ShipInstance

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.order_types import Order


__all__ = [
    "fleet_to_dict",
    "fleet_from_dict_kwargs",
    "_deserialize_fleet_ships",
    "_deserialize_fleet_orders",
]


def fleet_to_dict(fleet: "Fleet") -> Dict[str, Any]:
    """Serialize a ``Fleet`` to its save-system dict.

    Body lifted verbatim from the pre-extraction ``Fleet.to_dict``; save
    format is byte-identical.
    """
    ships_data = [s.to_dict() for s in fleet.ships]

    location_data: Any = None
    if isinstance(fleet.location, HexCoord):
        location_data = {"q": fleet.location.q, "r": fleet.location.r}
    elif isinstance(fleet.location, tuple):
        location_data = list(fleet.location)

    data: Dict[str, Any] = {
        "id": fleet.id,
        "owner_id": fleet.owner_id,
        "location": location_data,
        "speed": fleet.speed,
        "display_name": fleet.display_name,
        "ships": ships_data,
        "orders": [o.to_dict() for o in fleet.orders],
        "path": [
            {"q": p.q, "r": p.r} if isinstance(p, HexCoord)
            else list(p) if isinstance(p, tuple)
            else p
            for p in fleet.path
        ],
        "construction_queue": fleet.construction_queue,
        "construction_queue_paused": fleet.construction_queue_paused,
    }

    # PROJ-431 Phase 2: minefield runtime state moved to ``MineGroup``.
    # Real fleets no longer carry sensitivity / threshold / mine_positions
    # / scatter_seed fields.

    # Serialize hierarchy (only when non-empty, to preserve save-shape).
    if fleet._task_forces:
        data["task_forces"] = [tf.to_dict() for tf in fleet._task_forces]

    fleet_policy_data = fleet.fleet_policy.to_dict()
    if fleet_policy_data:
        data["fleet_policy"] = fleet_policy_data

    return data


def fleet_from_dict_kwargs(
    data: Dict[str, Any],
    registries: Optional["GameRegistries"] = None,
) -> Dict[str, Any]:
    """Validate save data and return kwargs ready for ``Fleet(**kwargs)``.

    Returns ONLY the kwargs accepted by ``Fleet.__init__``: ``fleet_id``,
    ``owner_id``, ``location``, ``speed``, ``component_registry``,
    ``display_name``. Post-construction hydration (``ships``, ``orders``,
    ``task_forces``, ``fleet_policy``, ``path``, ``construction_queue``)
    happens in ``Fleet.from_dict`` AFTER ``Fleet(**kwargs)`` returns.

    Raises:
        PersistenceException: required key missing.
    """
    require_keys(data, ["id", "owner_id"], "Fleet")

    location = data.get("location")
    if isinstance(location, dict) and "q" in location and "r" in location:
        location = HexCoord(location["q"], location["r"])
    elif isinstance(location, list):
        location = HexCoord(location[0], location[1])

    # PROJ-211: Extract component_registry from registries for DI.
    component_registry = registries.components if registries else None

    # PROJ-431 Phase 3: ``group_kind`` field deleted from Fleet. Any
    # value in a save predating Phase 3 is silently ignored — saves are
    # disposable per CLAUDE.md (no migration shim).
    return dict(
        fleet_id=data["id"],
        owner_id=data["owner_id"],
        location=location,
        speed=data.get("speed", 5.0),
        component_registry=component_registry,
        display_name=data.get("display_name", ""),
    )


def _deserialize_fleet_ships(
    ship_data_list: List[Dict[str, Any]],
    registries: Optional["GameRegistries"],
    fleet_id: Any = None,
) -> List[ShipInstance]:
    """Deserialize a Fleet's ship list from save data.

    PROJ-251: strict deserialization — a corrupt ship entry fails the
    load with a wrapped ``PersistenceException`` carrying the offending
    index.
    """
    ships: List[ShipInstance] = []
    for i, ship_data in enumerate(ship_data_list):
        try:
            ship = ShipInstance.from_dict(ship_data, registries=registries)
            ships.append(ship)
        except (PersistenceException, KeyError, TypeError, ValueError) as e:
            raise PersistenceException(
                f"Corrupt ship data at index {i} in fleet '{fleet_id if fleet_id is not None else '?'}'",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "fleet_id": fleet_id,
                    "ship_index": i,
                    "original_error": str(e),
                },
            ) from e
    return ships


def _deserialize_fleet_orders(
    orders_data: List[Dict[str, Any]],
    fleet_id: Any,
) -> List["Order"]:
    """Deserialize a Fleet's order queue from save data.

    Delegates to the long-standing ``OrderSerializer.deserialize_orders``
    helper (PROJ-210); kept as a thin module-level wrapper so the
    ``Fleet.from_dict`` facade has a single serde surface to import.
    """
    from game.strategy.data.order_serializer import OrderSerializer

    return OrderSerializer.deserialize_orders(orders_data, fleet_id)
