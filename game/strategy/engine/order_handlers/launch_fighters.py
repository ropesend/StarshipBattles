"""LaunchFightersOrderHandler — PROJ-FMS-C Phase 1.

Executes ``OrderType.LAUNCH_FIGHTERS`` orders: pops N fighters from the
issuing ship's :class:`VehicleBay` and creates a new ``fighter_group``
Fleet for the owner at the target hex. Each launched ``CarriedVehicle``
is converted into a real :class:`ShipInstance` living in the group's
``ships`` list so the existing conflict-resolution / battle-spec
compilation paths see the fighters as combat entities.

Strategic-flow contract mirrors :class:`LayMinesOrderHandler` (PROJ-FMS-B
Phase 1):

    Command -> OrderType.LAUNCH_FIGHTERS -> LaunchFightersOrderHandler

Order ``target`` payload is a dict::

    {
        'ship_instance_id': str,    # The carrier ship in the issuing fleet
        'fighter_design_id': str,   # Specific fighter design to launch
                                    # (or "auto" to take any fighter)
        'count': int,               # How many to launch
        'target_hex': HexCoord,     # Where to launch (default = fleet.location)
    }

PROJ-FMS-C decision: same-hex launches do NOT auto-merge (mirrors
PROJ-FMS-B audit Fix 4 for mine_groups). Each launch action mints its own
fighter_group; the player can recover individual groups via the strategic
:class:`RecoverFightersOrderHandler` action.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.events.event_types import EventCategory, EventType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy


class LaunchFightersOrderHandler(BaseOrderHandler):
    """Handler for :data:`OrderType.LAUNCH_FIGHTERS`."""

    def __init__(
        self,
        *,
        event_bus: Optional[Any] = None,
        planet_mutator: Optional[Any] = None,
        ship_mutator: Optional[Any] = None,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            planet_mutator=planet_mutator,
            ship_mutator=ship_mutator,
        )

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (OrderType.LAUNCH_FIGHTERS,)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        order = fleet.get_current_order()
        if not order or order.type != OrderType.LAUNCH_FIGHTERS:
            return OrderExecutionResult(
                success=False, message="Not a LAUNCH_FIGHTERS order"
            )

        payload = order.target
        if not isinstance(payload, dict):
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message="LAUNCH_FIGHTERS order missing payload"
            )

        ship_instance_id = payload.get("ship_instance_id")
        fighter_design_id = payload.get("fighter_design_id")
        count = int(payload.get("count", 0))
        target_hex = payload.get("target_hex") or fleet.location

        if not ship_instance_id or count <= 0:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message=(
                    "LAUNCH_FIGHTERS order requires ship_instance_id "
                    "and count > 0"
                ),
            )

        carrier = self._find_ship(fleet, ship_instance_id)
        if carrier is None:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message=f"Ship {ship_instance_id} not in fleet"
            )

        # Pop N matching fighters from the carrier's bay.
        popped = self._pop_fighters(carrier, fighter_design_id, count)
        if len(popped) < count:
            for f in popped:
                carrier.carried_items.append(f)
            fleet.pop_order()
            available = self._count_matching_fighters(
                carrier, fighter_design_id
            )
            return OrderExecutionResult(
                success=False,
                message=(
                    f"Insufficient fighters: requested {count} of design "
                    f"{fighter_design_id!r}, available {available}"
                ),
            )

        # Mint a fresh fighter_group Fleet — no auto-merge.
        fighter_group = self._create_fighter_group(
            empire=empire, target_hex=target_hex,
        )

        # Materialise each CarriedVehicle into a deployed ShipInstance.
        registries = getattr(carrier, "_registries", None)
        for raw_item in popped:
            cv = CarriedVehicle.from_any(raw_item)
            if cv is None:
                continue
            ship = self._carried_vehicle_to_ship_instance(
                cv, owner_id=empire.id, registries=registries,
            )
            fighter_group.ships.append(ship)

        fleet.pop_order()

        logger.info(
            "LaunchFightersOrderHandler: %s launched %d fighters of design "
            "%s at %s (group_id=%s)",
            getattr(empire, "name", f"Empire {empire.id}"),
            len(popped),
            fighter_design_id,
            target_hex,
            fighter_group.id,
        )
        try:
            self._emit_event(
                EventType.FACILITY_ACTIVATED,
                category=EventCategory.FLEET_OPERATIONS,
                empire_id=empire.id,
                message=(
                    f"Launched {len(popped)} {fighter_design_id} fighters at "
                    f"{target_hex} (group {fighter_group.id})"
                ),
                fleet_id=fleet.id,
                location_hex=[target_hex.q, target_hex.r],
            )
        except Exception:  # Intentional broad catch: event-bus emission is best-effort; missing event types in older bus configurations must not break the launch action.
            pass

        return OrderExecutionResult(success=True, message="Fighters launched")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_ship(
        fleet: Fleet, ship_instance_id: str
    ) -> Optional[ShipInstance]:
        for ship in fleet.ships:
            if str(ship.instance_id) == str(ship_instance_id):
                return ship
        return None

    @staticmethod
    def _pop_fighters(
        carrier: ShipInstance,
        fighter_design_id: Optional[str],
        count: int,
    ) -> List[Dict[str, Any]]:
        """Pop up to ``count`` matching fighters from ``carried_items``.

        When ``fighter_design_id`` is ``"auto"`` or falsy, any
        ``fighter`` CarriedVehicle matches. Otherwise filters by design.
        """
        popped: List[Dict[str, Any]] = []
        remaining: List[Dict[str, Any]] = []
        for item in carrier.carried_items:
            if len(popped) >= count:
                remaining.append(item)
                continue
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "fighter":
                remaining.append(item)
                continue
            if fighter_design_id and fighter_design_id != "auto":
                if cv.design_id != fighter_design_id:
                    remaining.append(item)
                    continue
            popped.append(item)
        carrier.carried_items = remaining
        return popped

    @staticmethod
    def _count_matching_fighters(
        carrier: ShipInstance, fighter_design_id: Optional[str]
    ) -> int:
        n = 0
        for item in carrier.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "fighter":
                continue
            if fighter_design_id and fighter_design_id != "auto":
                if cv.design_id != fighter_design_id:
                    continue
            n += 1
        return n

    def _create_fighter_group(
        self, *, empire: "Empire", target_hex: HexCoord,
    ) -> Fleet:
        """Mint a new ``fighter_group`` Fleet for this launch action."""
        new_id = self._mint_fleet_id(empire)
        group = Fleet(
            fleet_id=new_id,
            owner_id=empire.id,
            location=target_hex,
            speed=0.0,
            display_name=f"Fighter Wing {new_id}",
            group_kind="fighter_group",
        )
        empire.fleets.append(group)
        return group

    @staticmethod
    def _mint_fleet_id(empire: "Empire") -> int:
        existing = {f.id for f in empire.fleets if isinstance(f.id, int)}
        candidate = 200000  # Distinct namespace from mine_group (100000).
        while candidate in existing:
            candidate += 1
        return candidate

    @staticmethod
    def _carried_vehicle_to_ship_instance(
        cv: CarriedVehicle,
        *,
        owner_id: int,
        registries: Optional[Any],
    ) -> ShipInstance:
        """Build a deployed ShipInstance from a CarriedVehicle entry.

        PROJ-FMS-D audit Fix 1: delegates to the shared
        :func:`carried_vehicle_to_ship_instance` helper so the strategic
        launch path, the strategic satellite launch path, and the
        post-battle overflow path in :mod:`fighter_reboard` all preserve
        the same fields (HP, component_states, alive flags) uniformly.
        """
        from game.strategy.data.carried_vehicle_deploy import (
            carried_vehicle_to_ship_instance,
        )
        return carried_vehicle_to_ship_instance(
            cv, owner_id=owner_id, registries=registries,
        )


__all__ = ["LaunchFightersOrderHandler"]
