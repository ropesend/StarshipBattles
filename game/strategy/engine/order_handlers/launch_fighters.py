"""LaunchFightersOrderHandler — PROJ-FMS-C Phase 1 + QA Observation B.

Executes ``OrderType.LAUNCH_FIGHTERS`` orders. Now polymorphic across
both fleet- and planet-issued FMS orders through :class:`IIssuerAdapter`
(see ``issuer_adapter.py``).

Strategic-flow contract::

    Command -> OrderType.LAUNCH_FIGHTERS -> LaunchFightersOrderHandler

Order ``target`` payload is a dict::

    {
        'ship_instance_id': str,    # Carrier ship in the issuing fleet
                                    # (omit / None for planet-issued).
        'fighter_design_id': str,   # Specific fighter design to launch
                                    # (or "auto" to take any fighter)
        'count': int,               # How many to launch
        'target_hex': HexCoord,     # Where to launch (default = issuer.location)
    }
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.issuer_adapter import (
    FleetShipIssuerAdapter,
    IIssuerAdapter,
)
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
    # Execution — fleet entry point
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
        carrier = self._find_ship(fleet, ship_instance_id) if ship_instance_id else None
        if carrier is None:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message=f"Ship {ship_instance_id} not in fleet"
            )

        issuer = FleetShipIssuerAdapter(fleet, carrier)
        return self._run_with_issuer(
            issuer=issuer,
            order_owner=fleet,
            empire=empire,
            galaxy=galaxy,
            payload=payload,
            registries=getattr(carrier, "_registries", None),
        )

    # ------------------------------------------------------------------
    # Polymorphic core
    # ------------------------------------------------------------------

    def execute_for_issuer(
        self,
        *,
        issuer: IIssuerAdapter,
        order_owner: Any,
        empire: "Empire",
        galaxy: "Galaxy",
        registries: Optional[Any] = None,
    ) -> OrderExecutionResult:
        """Run the handler against any IIssuerAdapter (planet or fleet)."""
        order = order_owner.get_current_order()
        if not order or order.type != OrderType.LAUNCH_FIGHTERS:
            return OrderExecutionResult(
                success=False, message="Not a LAUNCH_FIGHTERS order"
            )
        payload = order.target
        if not isinstance(payload, dict):
            order_owner.pop_order()
            return OrderExecutionResult(
                success=False, message="LAUNCH_FIGHTERS order missing payload"
            )
        return self._run_with_issuer(
            issuer=issuer,
            order_owner=order_owner,
            empire=empire,
            galaxy=galaxy,
            payload=payload,
            registries=registries,
        )

    def _run_with_issuer(
        self,
        *,
        issuer: IIssuerAdapter,
        order_owner: Any,
        empire: "Empire",
        galaxy: "Galaxy",
        payload: Dict[str, Any],
        registries: Optional[Any],
    ) -> OrderExecutionResult:
        fighter_design_id = payload.get("fighter_design_id")
        count_raw = payload.get("count", 0)
        try:
            count = int(count_raw) if count_raw is not None else 0
        except (TypeError, ValueError):
            count = 0
        target_hex = payload.get("target_hex") or issuer.location

        if count <= 0:
            order_owner.pop_order()
            return OrderExecutionResult(
                success=False,
                message="LAUNCH_FIGHTERS order requires count > 0",
            )

        popped = issuer.pop_carried("fighter", fighter_design_id, count)
        if len(popped) < count:
            issuer.append_carried(popped)
            order_owner.pop_order()
            available = issuer.count_carried("fighter", fighter_design_id)
            return OrderExecutionResult(
                success=False,
                message=(
                    f"Insufficient fighters: requested {count} of design "
                    f"{fighter_design_id!r}, available {available}"
                ),
            )

        fighter_group = self._create_fighter_group(
            empire=empire, target_hex=target_hex,
        )

        # PROJ-431 Phase 1c: ``pop_carried`` now returns typed
        # ``CarriedVehicle`` instances from the fleet bay (planet adapter
        # still yields dicts pending 1d), so we accept both shapes.
        for raw_item in popped:
            cv = (
                raw_item
                if isinstance(raw_item, CarriedVehicle)
                else CarriedVehicle.from_dict(raw_item)
                if isinstance(raw_item, dict)
                else None
            )
            if cv is None:
                continue
            ship = self._carried_vehicle_to_ship_instance(
                cv, owner_id=empire.id, registries=registries,
            )
            fighter_group.ships.append(ship)

        order_owner.pop_order()

        logger.info(
            "LaunchFightersOrderHandler: %s launched %d fighters of design "
            "%s at %s (group_id=%s)",
            issuer.display_label,
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
                    f"{target_hex} from {issuer.display_label} "
                    f"(group {fighter_group.id})"
                ),
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
        candidate = 200000
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
        """Build a deployed ShipInstance from a CarriedVehicle entry."""
        from game.strategy.data.carried_vehicle_deploy import (
            carried_vehicle_to_ship_instance,
        )
        return carried_vehicle_to_ship_instance(
            cv, owner_id=owner_id, registries=registries,
        )


__all__ = ["LaunchFightersOrderHandler"]
