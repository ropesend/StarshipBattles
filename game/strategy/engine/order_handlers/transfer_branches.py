"""Transfer-handler dispatch branches (PROJ-368 review MAJ-001).

Split out of `transfer.py` to keep the parent file under the 500-LOC ceiling
ahead of PROJ-370 Phase 3, which will route Planet/Ship writes through
`IPlanetMutator` / `IShipInstanceMutator` against this exact file. The
seven `_dispatch_*` methods are mixed into `TransferHandler` via
`_TransferDispatchMixin`; call sites in
`TransferHandler.execute_action_order` remain unchanged.

Each `_dispatch_*` method is effectively pure (no `self.X` reads), but
they remain instance methods so the mixin pattern preserves the call
shape and so PROJ-370 has a single place per branch to inject its
mutator dependencies.

Branch numbering matches the docstring header in `transfer.py`:

  1. _dispatch_load_planet_resource     (planet, load,   resource cargo)
  2. _dispatch_load_planet_passengers   (planet, load,   passengers)
  3. _dispatch_drop_pod_load            (planet, load,   drop_pod)
  4. _dispatch_unload_planet_resource   (planet, unload, resource cargo)
  5. _dispatch_unload_planet_passengers (planet, unload, passengers)
  6. _dispatch_drop_pod_unload          (planet, unload, drop_pod)
  7. _dispatch_fleet_to_fleet           (fleet target, generic)
"""
from __future__ import annotations

from typing import Any, List, Optional, TYPE_CHECKING
import logging

from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle, VALID_VEHICLE_TYPES
from game.strategy.data.fleet import Fleet

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet


def _is_carried_vehicle_dict(item: Any) -> bool:
    """Return True iff ``item`` is a staging-yard dict shaped like a
    :class:`CarriedVehicle` (mine/fighter/satellite). PROJ-431 Phase 1d:
    explicit dict-shape probe that replaces the legacy runtime
    ``CarriedVehicle.from_any()`` discriminator at the staging-yard
    boundary, which still holds dicts.
    """
    if isinstance(item, CarriedVehicle):
        return True
    if not isinstance(item, dict):
        return False
    return str(item.get("vehicle_type", "")).lower() in VALID_VEHICLE_TYPES


def _pod_from_dict(item: Any) -> DropPod:
    """Promote a legacy drop-pod-shaped dict to a typed
    :class:`DropPod`. Mirrors the shape ``ShipInstance.bay_inventory``
    uses when projecting the legacy ``carried_items`` substrate.
    Extra dict keys land in :attr:`DropPod.payload`.
    """
    if isinstance(item, DropPod):
        return item
    if not isinstance(item, dict):
        return DropPod(design_id="", design_data={}, mass=0.0, payload={})
    return DropPod(
        design_id=str(item.get("design_id", "")),
        design_data=dict(item.get("design_data", {})),
        mass=float(item.get("mass", 0.0)),
        payload={
            k: v for k, v in item.items()
            if k not in {"design_id", "design_data", "mass"}
        },
    )


def _staging_yard_carried_vehicle(item: Any) -> Optional[CarriedVehicle]:
    """Promote a staging-yard dict to a typed :class:`CarriedVehicle`
    when it is shaped like one. Returns ``None`` for drop-pod-shaped
    entries (which lack a recognised ``vehicle_type``).
    """
    if isinstance(item, CarriedVehicle):
        return item
    if not isinstance(item, dict):
        return None
    if str(item.get("vehicle_type", "")).lower() not in VALID_VEHICLE_TYPES:
        return None
    return CarriedVehicle.from_dict(item)


class _TransferDispatchMixin:
    """Seven explicit transfer dispatch branches.

    Mixed into ``TransferHandler``; not intended for instantiation on its
    own. The methods are pure with respect to ``self`` (no instance state
    reads or writes); ``self`` is preserved only so the mixin pattern
    keeps call sites in ``TransferHandler.execute_action_order``
    unchanged across the PROJ-368 review MAJ-001 split.
    """

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

        # PROJ-393: species_id is now required; the legacy
        # 'default to first species' fallback is gone. UI surfaces a
        # species selection in the cargo dialog, and the order serializer
        # requires it.
        if not species_id:
            logger.warning(
                "TransferHandler: passenger LOAD on %s missing species_id; "
                "no transfer performed (legacy first-species fallback removed in PROJ-393)",
                planet.name,
            )
            return 0

        pop = next((p for p in planet.populations if p.race_id == species_id), None)
        if not pop:
            return 0

        to_load = min(to_load, pop.count)

        # Subtract from colony
        pop.count -= to_load

        # Add to fleet cargo. Cargo system tracks "passengers" as a single
        # bucket; species_id is consumed here for source-side accounting only.
        fleet.resources.load_cargo_to_fleet("passengers", to_load)

        return to_load

    def _dispatch_drop_pod_load(
        self,
        fleet: Fleet,
        planet: "Planet",
        pod_name: Optional[str] = None,
        amount: int = 0,
    ) -> int:
        """Branch 3: planet -> fleet, drop_pod (load from staging yard).

        Lifted verbatim from `OrderProcessor._load_pod_from_staging_yard`.
        Staging yard iterated in reverse so `pop` removals are safe.
        PROJ-FMS-A: skips ``CarriedVehicle``-shaped entries — those go
        through the dedicated carried-vehicle branch.

        PROJ-431 Phase 1d: fleet-side deposit goes through
        ``ship.set_bay_inventory(...)`` (typed write-through), and the
        staging-yard dict-shape probe uses an explicit ``vehicle_type``
        check instead of the legacy ``CarriedVehicle.from_any()``
        discriminator. The staging yard itself remains on the dict
        substrate (migration deferred).
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
            if _is_carried_vehicle_dict(item):
                continue
            if pod_name and item.get("name") != pod_name:
                logger.debug(
                    f"  Skipping staging item {i}: name={item.get('name')!r} != {pod_name!r}"
                )
                continue
            pod_mass = item.get("mass", 0.0)
            # Find a ship that can carry this pod
            target_ship = None
            for ship in fleet.ships:
                capacity = ship._cargo_mgr.get_pod_storage_capacity()
                used = ship._cargo_mgr.get_pod_storage_used()
                can = ship._cargo_mgr.can_carry_pod(pod_mass)
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
                # PROJ-431 Phase 1d: typed write-through.
                current_bay = target_ship.bay_inventory
                new_pods = list(current_bay.pods)
                new_pods.append(_pod_from_dict(removed))
                target_ship.set_bay_inventory(
                    BayInventory(bay=list(current_bay.bay), pods=new_pods)
                )
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
        from game.strategy.data.species_population import SpeciesPopulation

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
            # Create new species population.
            # PROJ-370 Phase 3: route through IPlanetMutator.
            species_pop = SpeciesPopulation(race_id=race_id, count=0, happiness=0.5)
            self._get_planet_mutator().add_species_population(planet, species_pop)

        species_pop.count += actual_unloaded
        return actual_unloaded

    def _dispatch_carried_vehicle_load(
        self,
        fleet: Fleet,
        planet: "Planet",
        design_id: Optional[str] = None,
        amount: int = 0,
    ) -> int:
        """PROJ-FMS-A Phase 3: planet -> fleet, carried vehicle.

        Generalised drop-pod load path for design-backed carried vehicles
        (mines / fighters / satellites). Loads from ``planet.staging_yard``
        into the first ship whose ``VehicleBay`` has compatible capacity.
        Staging yard iterated in reverse so ``pop`` removals are safe.

        ``design_id`` may be passed via the legacy ``species_id`` slot in
        the order target dict — the order serializer treats the slot as
        a generic per-order discriminator.

        PROJ-431 Phase 1d: staging-yard dict probe uses an explicit
        ``vehicle_type`` shape check instead of the legacy
        ``CarriedVehicle.from_any()`` discriminator. The staging yard
        is still on the dict substrate.
        """
        loaded = 0
        to_load = amount if amount > 0 else len(planet.staging_yard)

        for i in range(len(planet.staging_yard) - 1, -1, -1):
            if loaded >= to_load:
                break
            item = planet.staging_yard[i]
            cv = _staging_yard_carried_vehicle(item)
            if cv is None:
                continue
            if design_id and cv.design_id != design_id:
                continue
            target_ship = None
            for ship in fleet.ships:
                if ship._cargo_mgr.can_accept_vehicle(cv):
                    target_ship = ship
                    break
            if target_ship is None:
                continue
            removed = planet.remove_from_staging_yard(i)
            if removed and target_ship._cargo_mgr.load_vehicle(cv):
                loaded += 1
            elif removed:
                # Restore: load failed unexpectedly. Put it back at end of staging.
                planet.staging_yard.append(removed)
        return loaded

    def _dispatch_carried_vehicle_unload(
        self,
        fleet: Fleet,
        planet: "Planet",
        design_id: Optional[str] = None,
        amount: int = 0,
    ) -> int:
        """PROJ-FMS-A Phase 3: fleet -> planet, carried vehicle.

        Mirror of :meth:`_dispatch_carried_vehicle_load`. Moves matching
        ``CarriedVehicle`` entries from ship bays into the planet's
        staging yard.
        """
        from game.strategy.data.carried_vehicle import CarriedVehicle

        unloaded = 0
        total_count = sum(len(s._cargo_mgr.get_carried_vehicles()) for s in fleet.ships)
        to_unload = amount if amount > 0 else total_count
        for ship in fleet.ships:
            if unloaded >= to_unload:
                break
            carried = ship._cargo_mgr.get_carried_vehicles()
            # Walk indices in reverse so unload_vehicle pops are stable.
            for idx in range(len(carried) - 1, -1, -1):
                if unloaded >= to_unload:
                    break
                cv: CarriedVehicle = carried[idx]
                if design_id and cv.design_id != design_id:
                    continue
                # add_to_staging_yard returns False if planet capacity exceeded.
                if planet.add_to_staging_yard(cv.to_dict()):
                    ship._cargo_mgr.unload_vehicle(idx)
                    unloaded += 1
        return unloaded

    def _dispatch_drop_pod_unload(
        self,
        fleet: Fleet,
        planet: "Planet",
        pod_name: Optional[str] = None,
        amount: int = 0,
    ) -> int:
        """Branch 6: fleet -> planet, drop_pod (unload to staging yard).

        PROJ-431 Phase 1d: pods read from ``ship.bay_inventory.pods``
        (typed slot — exclusively drop pods by construction) and the
        consumed pod is removed by rebuilding the bay inventory and
        writing back via ``ship.set_bay_inventory(...)``. The planet
        staging yard still consumes legacy dict shape, so the typed
        ``DropPod`` is flattened to a dict at the boundary.
        """
        unloaded = 0
        # Count drop-pod entries via the typed slot; CarriedVehicle
        # entries belong to a different transfer branch.
        to_unload = amount if amount > 0 else sum(
            len(s.bay_inventory.pods) for s in fleet.ships
        )

        for ship in fleet.ships:
            if unloaded >= to_unload:
                break
            current_bay = ship.bay_inventory
            # Walk a snapshot so we can rebuild the typed pod list
            # without index churn across mutations.
            kept_pods: List[DropPod] = []
            for pod in current_bay.pods:
                if unloaded >= to_unload:
                    kept_pods.append(pod)
                    continue
                if pod_name and pod.payload.get("name") != pod_name:
                    kept_pods.append(pod)
                    continue
                # Flatten the typed pod back to the dict shape the
                # planet's staging yard still expects.
                pod_dict = dict(pod.payload)
                pod_dict["design_id"] = pod.design_id
                pod_dict["design_data"] = pod.design_data
                pod_dict["mass"] = pod.mass
                if planet.add_to_staging_yard(pod_dict):
                    unloaded += 1
                    # pod consumed -- do not append to kept_pods
                else:
                    kept_pods.append(pod)
            if len(kept_pods) != len(current_bay.pods):
                ship.set_bay_inventory(
                    BayInventory(bay=list(current_bay.bay), pods=kept_pods)
                )

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
