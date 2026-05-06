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

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.planet import Planet


class TransferHandler(BaseOrderHandler):
    """Handler for the TRANSFER family (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION)."""

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

        # Validate -- skip location check for drop_pod (fleet is already at planet via MOVE order).
        skip_loc = cargo_type == "drop_pod"
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

    # ------------------------------------------------------------------
    # 7 explicit dispatch branches
    # ------------------------------------------------------------------

    def _dispatch_load_planet_resource(
        self,
        fleet: Fleet,
        planet: "Planet",
        cargo_type: str,
        amount: int,
    ) -> int:
        """Branch 1: planet -> fleet, resource cargo (metals, fuel, etc.)."""
        capacity = fleet.resources.get_fleet_cargo_capacity(cargo_type)
        current = fleet.resources.get_fleet_cargo_current(cargo_type)
        available_space = capacity - current

        to_load = amount if amount > 0 else available_space
        to_load = min(to_load, available_space)

        # Cap by planet stockpile (convert to int for cargo API)
        planet_available = int(round(planet.get_stockpile(cargo_type)))
        to_load = min(to_load, planet_available)

        if to_load <= 0:
            return 0

        # Subtract from planet stockpile
        planet.consume_from_stockpile(cargo_type, float(to_load))
        # Add to fleet cargo
        fleet.resources.load_cargo_to_fleet(cargo_type, to_load)
        return to_load

    def _dispatch_load_planet_passengers(
        self,
        fleet: Fleet,
        planet: "Planet",
        amount: int,
        species_id: Optional[str] = None,
    ) -> int:
        """Branch 2: planet -> fleet, passengers."""
        capacity = fleet.resources.get_fleet_cargo_capacity("passengers")
        current = fleet.resources.get_fleet_cargo_current("passengers")
        available_space = capacity - current

        # If amount is 0, load as much as possible
        to_load = amount if amount > 0 else available_space
        to_load = min(to_load, available_space)

        # Cap by colony population
        if not planet.populations:
            return 0

        # If species_id provided, find that specific species
        if species_id:
            pop = next((p for p in planet.populations if p.race_id == species_id), None)
            if not pop:
                return 0
        else:
            # Legacy/Default: use first species
            pop = planet.populations[0]

        to_load = min(to_load, pop.count)

        # Subtract from colony
        pop.count -= to_load

        # Add to fleet cargo
        # TODO: If we ever track species in fleet cargo, use species_id here
        fleet.resources.load_cargo_to_fleet("passengers", to_load)

        return to_load

    def _dispatch_drop_pod_load(
        self,
        fleet: Fleet,
        planet: "Planet",
        pod_name: Optional[str],
        amount: int,
    ) -> int:
        """Branch 3: planet -> fleet, drop_pod (load from staging yard).

        Lifted verbatim from `OrderProcessor._load_pod_from_staging_yard`.
        Staging yard iterated in reverse so `pop` removals are safe.
        """
        logger.info(
            f"_dispatch_drop_pod_load: planet={planet.name} pod_name={pod_name!r} "
            f"amount={amount} staging_count={len(planet.staging_yard)} "
            f"fleet_ships={len(fleet.ships)}"
        )
        loaded = 0
        to_load = amount if amount > 0 else len(planet.staging_yard)

        # Iterate staging yard in reverse so we can remove items safely
        for i in range(len(planet.staging_yard) - 1, -1, -1):
            if loaded >= to_load:
                break
            item = planet.staging_yard[i]
            if pod_name and item.get("name") != pod_name:
                logger.debug(
                    f"  Skipping staging item {i}: name={item.get('name')!r} != {pod_name!r}"
                )
                continue
            pod_mass = item.get("mass", 0.0)
            # Find a ship that can carry this pod
            target_ship = None
            for ship in fleet.ships:
                capacity = ship.get_pod_storage_capacity()
                used = ship.get_pod_storage_used()
                can = ship.can_carry_pod(pod_mass)
                logger.debug(
                    f"  Ship {ship.name}: pod_capacity={capacity} used={used} "
                    f"can_carry({pod_mass})={can}"
                )
                if can:
                    target_ship = ship
                    break
            if target_ship is None:
                logger.warning(
                    f"  No ship can carry pod '{item.get('name')}' (mass={pod_mass})"
                )
                continue  # No ship has capacity
            removed = planet.remove_from_staging_yard(i)
            if removed:
                target_ship.carried_items.append(removed)
                loaded += 1

        return loaded

    def _dispatch_unload_planet_resource(
        self,
        fleet: Fleet,
        planet: "Planet",
        cargo_type: str,
        amount: int,
    ) -> int:
        """Branch 4: fleet -> planet, resource cargo."""
        current_cargo = fleet.resources.get_fleet_cargo_current(cargo_type)
        to_unload = amount if amount > 0 else current_cargo
        to_unload = min(to_unload, current_cargo)

        if to_unload <= 0:
            return 0

        actual_unloaded = fleet.resources.unload_cargo_from_fleet(cargo_type, to_unload)
        planet.add_to_stockpile(cargo_type, float(actual_unloaded))
        return actual_unloaded

    def _dispatch_unload_planet_passengers(
        self,
        fleet: Fleet,
        planet: "Planet",
        empire: "Empire",
        amount: int,
        species_id: Optional[str] = None,
    ) -> int:
        """Branch 5: fleet -> planet, passengers."""
        from game.strategy.data.planet import SpeciesPopulation

        current_cargo = fleet.resources.get_fleet_cargo_current("passengers")

        # If amount is 0, unload all
        to_unload = amount if amount > 0 else current_cargo

        # Cap by what we actually have
        to_unload = min(to_unload, current_cargo)

        if to_unload <= 0:
            return 0

        # Unload from fleet
        actual_unloaded = fleet.resources.unload_cargo_from_fleet("passengers", to_unload)

        # Add to colony population
        # Use provided species_id or empire's race_id
        race_id = species_id or (
            empire.race_config.race_id if empire.race_config else "default"
        )

        # Find or create SpeciesPopulation for this race
        species_pop = None
        for pop in planet.populations:
            if pop.race_id == race_id:
                species_pop = pop
                break

        if species_pop is None:
            # Create new species population
            species_pop = SpeciesPopulation(race_id=race_id, count=0, happiness=0.5)
            planet.populations.append(species_pop)

        species_pop.count += actual_unloaded
        return actual_unloaded

    def _dispatch_drop_pod_unload(
        self,
        fleet: Fleet,
        planet: "Planet",
        pod_name: Optional[str],
        amount: int,
    ) -> int:
        """Branch 6: fleet -> planet, drop_pod (unload to staging yard).

        Lifted verbatim from `OrderProcessor._unload_pod_to_staging_yard`.
        """
        unloaded = 0
        to_unload = amount if amount > 0 else sum(
            len(getattr(s, "carried_items", [])) for s in fleet.ships
        )

        for ship in fleet.ships:
            if unloaded >= to_unload:
                break
            for i in range(len(ship.carried_items) - 1, -1, -1):
                if unloaded >= to_unload:
                    break
                item = ship.carried_items[i]
                if pod_name and item.get("name") != pod_name:
                    continue
                if planet.add_to_staging_yard(item):
                    ship.carried_items.pop(i)
                    unloaded += 1

        return unloaded

    def _dispatch_fleet_to_fleet(
        self,
        fleet: Fleet,
        target_fleet: Fleet,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: Optional[str] = None,
    ) -> int:
        """Branch 7: fleet -> fleet (generic, any cargo type).

        Lifted verbatim from `OrderProcessor._execute_fleet_transfer`.
        """
        source = fleet if direction == "unload" else target_fleet
        dest = target_fleet if direction == "unload" else fleet

        current_cargo = source.resources.get_fleet_cargo_current(cargo_type)
        capacity = dest.resources.get_fleet_cargo_capacity(cargo_type)
        current_dest = dest.resources.get_fleet_cargo_current(cargo_type)
        available_space = capacity - current_dest

        to_transfer = amount if amount > 0 else current_cargo
        to_transfer = min(to_transfer, current_cargo, available_space)

        if to_transfer <= 0:
            return 0

        actual_transferred = source.resources.unload_cargo_from_fleet(cargo_type, to_transfer)
        dest.resources.load_cargo_to_fleet(cargo_type, actual_transferred)

        return actual_transferred
