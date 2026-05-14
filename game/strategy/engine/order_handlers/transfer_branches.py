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

from typing import Optional, TYPE_CHECKING
import logging

from game.strategy.data.fleet import Fleet

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet


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
                # PROJ-370 Phase 5: route through IShipInstanceMutator.
                self._get_ship_mutator().add_carried_item(target_ship, removed)
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

    def _dispatch_drop_pod_unload(
        self,
        fleet: Fleet,
        planet: "Planet",
        pod_name: Optional[str] = None,
        amount: int = 0,
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
                    # PROJ-370 Phase 5: route through IShipInstanceMutator.
                    self._get_ship_mutator().pop_carried_item(ship, i)
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
