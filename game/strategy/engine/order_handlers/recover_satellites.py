"""RecoverSatellitesOrderHandler — PROJ-FMS-D Phase 2.

Executes ``OrderType.RECOVER_SATELLITES`` orders. Mirrors
:class:`RecoverFightersOrderHandler` (PROJ-FMS-C Phase 3) but:

- Acts on ``satellite_group`` Fleets only.
- Pops :class:`CarriedVehicle`s back into a satellite-capable bay (the
  ``allowed_types`` filter on :class:`VehicleBayAbility` enforces this
  per-bay).
- The recovering ship must mount :class:`RecoverSatellitesAbility` —
  enforced by the ability-lookup gating wired on the command spec.

Order ``target`` payload is a dict::

    {
        'ship_instance_id': str,             # Recovering ship in the issuing fleet
        'satellite_group_id': int | None,    # Specific group, or None for first
                                             # owner-owned group at hex
        'count': int | None,                 # How many to recover, or None for all
    }
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple

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


class RecoverSatellitesOrderHandler(BaseOrderHandler):
    """Handler for :data:`OrderType.RECOVER_SATELLITES`."""

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
        return (OrderType.RECOVER_SATELLITES,)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        order = fleet.get_current_order()
        if not order or order.type != OrderType.RECOVER_SATELLITES:
            return OrderExecutionResult(
                success=False, message="Not a RECOVER_SATELLITES order"
            )

        payload = order.target
        if not isinstance(payload, dict):
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message="RECOVER_SATELLITES order missing payload",
            )

        ship_instance_id = payload.get("ship_instance_id")
        satellite_group_id = payload.get("satellite_group_id")
        count = payload.get("count")  # None => recover all

        if not ship_instance_id:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message="RECOVER_SATELLITES order requires ship_instance_id",
            )

        carrier = self._find_ship(fleet, ship_instance_id)
        if carrier is None:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message=f"Ship {ship_instance_id} not in fleet"
            )

        source = self._find_satellite_group(
            empire,
            hex_=fleet.location,
            satellite_group_id=satellite_group_id,
        )
        if source is None:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message=(
                    f"No matching satellite_group at {fleet.location} "
                    f"(group_id={satellite_group_id})"
                ),
            )
        if not source.ships:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message=f"Satellite group {source.id} is empty",
            )

        available = len(source.ships)
        if count is None or int(count) <= 0:
            requested = available
        else:
            requested = min(int(count), available)

        recovered = 0
        not_recovered: List[ShipInstance] = []
        for ship in list(source.ships[:requested]):
            cv = self._satellite_ship_to_carried_vehicle(ship)
            if cv is None:
                not_recovered.append(ship)
                continue
            if carrier._cargo_mgr is None:
                not_recovered.append(ship)
                continue
            ok = carrier._cargo_mgr.load_vehicle(cv)
            if not ok:
                not_recovered.append(ship)
                continue
            source.ships.remove(ship)
            recovered += 1

        # Prune empty satellite_group from empire's fleets list.
        if not source.ships:
            try:
                empire.fleets.remove(source)
            except ValueError:
                pass

        fleet.pop_order()

        logger.info(
            "RecoverSatellitesOrderHandler: %s recovered %d satellite(s) "
            "into %s from group %s (left in group: %d)",
            getattr(empire, "name", f"Empire {empire.id}"),
            recovered,
            carrier.instance_id,
            source.id,
            len(source.ships),
        )
        try:
            self._emit_event(
                EventType.FACILITY_ACTIVATED,
                category=EventCategory.FLEET_OPERATIONS,
                empire_id=empire.id,
                message=(
                    f"Recovered {recovered} satellite(s) into "
                    f"{carrier.instance_id} from group {source.id}"
                ),
                fleet_id=fleet.id,
            )
        except Exception:  # Intentional broad catch: event-bus emission is best-effort; missing event types in older bus configurations must not break the recovery action.
            pass

        if recovered == 0:
            return OrderExecutionResult(
                success=False,
                message=(
                    "Failed to recover any satellites — bay capacity may be "
                    "full or no bay accepts satellites."
                ),
            )

        return OrderExecutionResult(
            success=True,
            message=f"Recovered {recovered} satellite(s)",
        )

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
    def _find_satellite_group(
        empire: "Empire",
        *,
        hex_: Any,
        satellite_group_id: Optional[int],
    ) -> Optional[Fleet]:
        """Locate a satellite_group at ``hex_`` owned by ``empire``."""
        for f in empire.fleets:
            if getattr(f, "group_kind", "fleet") != "satellite_group":
                continue
            if satellite_group_id is not None:
                if f.id != satellite_group_id:
                    continue
            if f.location != hex_:
                continue
            return f
        return None

    @staticmethod
    def _satellite_ship_to_carried_vehicle(
        ship: ShipInstance,
    ) -> Optional[CarriedVehicle]:
        """Convert a deployed satellite ShipInstance back into a CarriedVehicle."""
        design = ship.design_data or {}
        mass = 0.0
        try:
            stats = ship.get_calculated_stats()
            m = stats.get("mass")
            if m is not None:
                mass = float(m)
        except Exception:  # Intentional broad catch: stats path raises for ships built without registries; fall back to design_data mass when available.
            mass = float(design.get("mass", 0.0) or 0.0)
        if mass <= 0:
            mass = float(design.get("mass", 0.0) or 0.0)

        hp_value = ship.current_hp if ship.current_hp is not None else 0
        if hp_value < 0:
            hp_value = 0

        component_states = dict(ship.components) if ship.components else None

        try:
            return CarriedVehicle(
                design_id=ship.design_id,
                design_data=dict(design),
                vehicle_type="satellite",
                mass=mass,
                current_hp=int(hp_value),
                component_states=component_states,
            )
        except ValueError:
            return None


__all__ = ["RecoverSatellitesOrderHandler"]
