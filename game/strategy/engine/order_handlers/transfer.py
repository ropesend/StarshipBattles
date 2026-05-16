"""TransferHandler -- handles `OrderType.{TRANSFER, LOAD_POPULATION,
UNLOAD_POPULATION}` (PROJ-368 Phase 3).

The single most complex handler in PROJ-368. Subsumes:
- `OrderProcessor.process_transfer` (114 LOC, 5 implicit branches)
- `OrderProcessor._execute_load`, `_execute_unload`,
  `_execute_fleet_transfer` (legacy private helpers)
- `OrderProcessor._load_pod_from_staging_yard`,
  `_unload_pod_to_staging_yard`

Decomposes the 5 implicit branches in `process_transfer` into 7
**explicit** `_dispatch_*` private methods, exposing the cargo-type
sub-branches the legacy code conflated:

  1. _dispatch_load_planet_resource     (planet, load,   resource cargo)
  2. _dispatch_load_planet_passengers   (planet, load,   passengers)
  3. _dispatch_drop_pod_load            (planet, load,   drop_pod)
  4. _dispatch_unload_planet_resource   (planet, unload, resource cargo)
  5. _dispatch_unload_planet_passengers (planet, unload, passengers)
  6. _dispatch_drop_pod_unload          (planet, unload, drop_pod)
  7. _dispatch_fleet_to_fleet           (fleet target, generic)

Three preserved invariants:
- BUG-70 LOAD_POPULATION auto-resolve at fleet hex.
- PROJ-343 T1.1 target_fleet_id resolution against galaxy.empires
  with empire.fleets fallback (resolver brittleness preserved
  verbatim; the call-site fix lives in handlers/transfer.py).
- BUG-122 fleet-to-fleet co-location validator skip is upstream of
  this handler; the cargo_type == "drop_pod" path skips the location
  check via `skip_location_check`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple
import logging

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.engine.order_handlers.transfer_branches import _TransferDispatchMixin

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy


class TransferHandler(_TransferDispatchMixin, BaseOrderHandler):
    """Handler for the TRANSFER family (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION).

    PROJ-368 review MAJ-001: the seven `_dispatch_*` branches live in
    `transfer_branches._TransferDispatchMixin` to keep this file under the
    500-LOC ceiling ahead of PROJ-370 Phase 3.
    """

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        """Execute a TRANSFER / LOAD_POPULATION / UNLOAD_POPULATION order."""
        from game.strategy.validation import TransferValidator

        order = fleet.get_current_order()
        if not order or order.type not in (
            OrderType.TRANSFER,
            OrderType.LOAD_POPULATION,
            OrderType.UNLOAD_POPULATION,
        ):
            return OrderExecutionResult(
                success=False, message="No TRANSFER order"
            )

        # Extract params from order target dict
        params = order.target
        if not isinstance(params, dict):
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message="Invalid transfer params"
            )

        direction = params.get("direction", "")
        cargo_type = params.get("cargo_type", "")
        amount = params.get("amount", 0)
        planet_id = params.get("planet_id")
        target_fleet_id = params.get("target_fleet_id")
        species_id = params.get("species_id")

        # Resolve target.
        target = None
        if planet_id:
            target = galaxy.get_planet_by_id(planet_id)
        elif (
            not planet_id
            and not target_fleet_id
            and order.type == OrderType.LOAD_POPULATION
        ):
            # BUG-70: Generic LOAD_POPULATION -- auto-resolve colony at fleet's current hex
            planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
            for p in planets_at_hex:
                if (
                    p.owner_id == empire.id
                    and hasattr(p, "populations")
                    and p.populations
                    and p.total_population > 0
                ):
                    target = p
                    logger.debug(
                        f"BUG-70: Auto-resolved colony {p.name} (pop={p.total_population}) at fleet hex {fleet.location}"
                    )
                    break
            if not target:
                # No owned colony at fleet hex -- no-op, continue with next order
                logger.debug(
                    f"BUG-70: No owned colony at fleet hex {fleet.location}, skipping LOAD_POPULATION"
                )
                fleet.pop_order()
                return OrderExecutionResult(
                    success=True,
                    message="No colony at location, skipped",
                )
        elif target_fleet_id:
            target = self._resolve_target_fleet_by_id(target_fleet_id, empire, galaxy)

        # Validate -- skip location check for drop_pod / vehicle (fleet is
        # already at planet via MOVE order).
        skip_loc = cargo_type in ("drop_pod", "vehicle")
        logger.info(
            f"TransferHandler.execute_action_order: fleet={fleet.id} cargo={cargo_type} "
            f"dir={direction} amt={amount} species={species_id} "
            f"target={getattr(target, 'name', target)} skip_loc={skip_loc}"
        )
        validation = TransferValidator.validate(
            galaxy, fleet, target, cargo_type, direction, amount, species_id,
            skip_location_check=skip_loc,
        )

        if not validation.is_valid:
            logger.warning(
                f"TransferHandler: Transfer failed - {validation.message} "
                f"(code={validation.error_code})"
            )
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message=validation.message
            )

        # Dispatch into one of 7 explicit branches.
        from game.core.protocols import is_planet, is_fleet
        transferred = 0

        if is_planet(target):
            if direction == "load":
                logger.info(
                    f"TransferHandler: Executing LOAD {cargo_type} from {target.name}"
                )
                if cargo_type == "drop_pod":
                    transferred = self._dispatch_drop_pod_load(
                        fleet, target, species_id, amount
                    )
                elif cargo_type == "vehicle":
                    # PROJ-FMS-A Phase 3: design-backed carried vehicle.
                    transferred = self._dispatch_carried_vehicle_load(
                        fleet, target, species_id, amount
                    )
                elif cargo_type == "passengers":
                    transferred = self._dispatch_load_planet_passengers(
                        fleet, target, amount, species_id
                    )
                else:
                    transferred = self._dispatch_load_planet_resource(
                        fleet, target, cargo_type, amount
                    )
            else:  # unload
                logger.info(
                    f"TransferHandler: Executing UNLOAD {cargo_type} to {target.name}"
                )
                if cargo_type == "drop_pod":
                    transferred = self._dispatch_drop_pod_unload(
                        fleet, target, species_id, amount
                    )
                elif cargo_type == "vehicle":
                    # PROJ-FMS-A Phase 3: design-backed carried vehicle.
                    transferred = self._dispatch_carried_vehicle_unload(
                        fleet, target, species_id, amount
                    )
                elif cargo_type == "passengers":
                    transferred = self._dispatch_unload_planet_passengers(
                        fleet, target, empire, amount, species_id
                    )
                else:
                    transferred = self._dispatch_unload_planet_resource(
                        fleet, target, cargo_type, amount
                    )
        elif is_fleet(target):
            transferred = self._dispatch_fleet_to_fleet(
                fleet, target, cargo_type, direction, amount, species_id
            )

        fleet.pop_order()
        logger.info(
            f"TransferHandler: Transfer complete. {direction}ed {transferred} {cargo_type}"
        )
        return OrderExecutionResult(
            success=True, amount_transferred=transferred
        )

    # ------------------------------------------------------------------
    # Target resolution
    # ------------------------------------------------------------------

    def _resolve_target_fleet_by_id(
        self,
        target_fleet_id: int,
        empire: "Empire",
        galaxy: "Galaxy",
    ) -> Optional[Fleet]:
        """Find a Fleet by id by searching `galaxy.empires` then `empire.fleets`.

        PROJ-368: brittle. PROJ-343 T1.1 fixed the call-site (handlers/
        transfer.py:108-113); resolver brittleness is future work
        (decisions.md row 11).
        """
        target = None
        # Search all empires for the target fleet
        # NOTE: galaxy may not have 'empires' attr - depends on context
        for emp in getattr(galaxy, "empires", []):
            for f in emp.fleets:
                if f.id == target_fleet_id:
                    target = f
                    break
            if target:
                break

        # If not found in galaxy.empires, try searching the current empire
        if not target:
            for f in empire.fleets:
                if f.id == target_fleet_id:
                    target = f
                    break
        return target
