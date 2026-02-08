"""
FleetOrderProcessor - Centralized order lifecycle management.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.
STRAT-006: Centralize order lifecycle management.

Responsibilities:
- Order completion (pop_order in single location)
- Order cancellation (with reason tracking)
- JOIN_FLEET processing (instant and end-of-turn)
- COLONIZE processing
- Instant order processing during ticks
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING

from game.core.logger import log_debug, log_warning, log_info
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord

if TYPE_CHECKING:
    pass


@dataclass
class JoinFleetResult:
    """Result of a JOIN_FLEET operation."""
    merged: bool
    cancelled: bool = False


@dataclass
class ColonizeResult:
    """Result of a COLONIZE operation."""
    colonized: bool
    planet_name: Optional[str] = None


@dataclass
class TransferResult:
    """Result of a TRANSFER operation."""
    success: bool
    amount_transferred: int = 0
    message: str = ""


class FleetOrderProcessor:
    """
    Processor for fleet order lifecycle management.

    Centralizes order state management:
    - complete_order() - mark order as done
    - cancel_order() - cancel with reason
    - process_join_fleet() - handle JOIN_FLEET orders
    - process_colonize() - handle COLONIZE orders
    - process_instant_orders() - tick-based instant orders
    - process_end_turn_orders() - end-of-turn orders
    """

    def __init__(self):
        """Initialize the fleet order processor."""
        pass

    def complete_order(self, fleet: Fleet) -> Optional[FleetOrder]:
        """
        Complete the current order for a fleet.

        Pops the order from the queue, centralizing order completion logic.

        Args:
            fleet: Fleet whose order completed

        Returns:
            The completed order, or None if no order
        """
        order = fleet.get_current_order()
        if not order:
            return None

        fleet.pop_order()
        return order

    def cancel_order(self, fleet: Fleet, reason: str = "") -> Optional[FleetOrder]:
        """
        Cancel the current order for a fleet.

        Pops the order and logs the cancellation reason.

        Args:
            fleet: Fleet whose order is cancelled
            reason: Reason for cancellation (for logging)

        Returns:
            The cancelled order, or None if no order
        """
        order = fleet.get_current_order()
        if not order:
            return None

        log_debug(f"Fleet {fleet.id} order cancelled: {reason}")
        fleet.pop_order()
        return order

    def cancel_all_orders(self, fleet: Fleet, reason: str = "") -> None:
        """
        Cancel all orders for a fleet.

        Clears the entire order queue.

        Args:
            fleet: Fleet whose orders are cancelled
            reason: Reason for cancellation (for logging)
        """
        log_debug(f"Fleet {fleet.id} all orders cancelled: {reason}")
        fleet.clear_orders()

    def process_join_fleet(
        self,
        fleet: Fleet,
        empire,
        galaxy
    ) -> JoinFleetResult:
        """
        Process a JOIN_FLEET order.

        Merges fleet into target if at same location.

        Args:
            fleet: Fleet with JOIN_FLEET order
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation

        Returns:
            JoinFleetResult with merge status
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.JOIN_FLEET:
            return JoinFleetResult(merged=False)

        target_fleet = order.target

        # Validation
        if not target_fleet or not hasattr(target_fleet, 'location'):
            log_warning("FleetOrderProcessor: Join Fleet failed - Target invalid/destroyed.")
            fleet.pop_order()
            return JoinFleetResult(merged=False, cancelled=True)

        if fleet.location == target_fleet.location:
            log_debug(f"FleetOrderProcessor: Fleet {fleet.id} merging into {target_fleet.id}")
            fleet.merge_with(target_fleet)
            empire.remove_fleet(fleet)
            return JoinFleetResult(merged=True)
        else:
            # Not at location yet
            log_warning("FleetOrderProcessor: Join Fleet failed - Not at same location.")
            fleet.pop_order()
            return JoinFleetResult(merged=False)

    def process_colonize(
        self,
        fleet: Fleet,
        empire,
        galaxy,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ColonizeResult:
        """
        Process a COLONIZE order.

        PROJ-36: Uses ColonizeValidator for validation.
        PROJ-55: When component_registry is provided, removes only the colony
                 ship instead of the entire fleet.

        Claims a planet for the empire if valid.

        Args:
            fleet: Fleet with COLONIZE order
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet lookup
            component_registry: Optional component registry for pod lookup.
                               When provided, only the colony ship is removed.
                               When None, entire fleet is removed (legacy behavior).

        Returns:
            ColonizeResult with colonization status
        """
        from game.strategy.validation import ColonizeValidator

        order = fleet.get_current_order()
        if not order or order.type != OrderType.COLONIZE:
            return ColonizeResult(colonized=False)

        target_planet = order.target

        # PROJ-36: Use centralized validation
        validation = ColonizeValidator.validate(galaxy, fleet, target_planet)
        if not validation.is_valid:
            log_warning(f"FleetOrderProcessor: Colonize failed - {validation.message}")
            fleet.pop_order()
            return ColonizeResult(colonized=False)

        # Determine final planet (for "Any" case, pick first valid candidate)
        if target_planet is not None:
            final_planet = target_planet
        else:
            planets_at_loc = galaxy.get_planets_at_global_hex(fleet.location)
            valid_candidates = [p for p in planets_at_loc if p.owner_id is None]
            final_planet = valid_candidates[0]

        # Execute colonization
        empire.add_colony(final_planet)
        fleet.pop_order()

        # PROJ-68: Transfer passengers from fleet to colony as founding population
        self._transfer_founding_population(fleet, final_planet, empire)

        # PROJ-55: Remove only colony ship when registry is provided
        if component_registry is not None:
            planet_type_str = final_planet.planet_type.name
            colony_ship = ColonizeValidator.find_ship_with_colony_pod(
                fleet, planet_type_str, component_registry
            )

            if colony_ship is not None:
                fleet.remove_ship(colony_ship)
                log_debug(f"FleetOrderProcessor: Removed colony ship '{colony_ship.name}' from fleet")

            # If fleet now empty, remove it
            if len(fleet.ships) == 0:
                empire.remove_fleet(fleet)
                log_debug(f"FleetOrderProcessor: Fleet {fleet.id} removed (no ships remaining)")
        else:
            # Legacy behavior: remove entire fleet
            empire.remove_fleet(fleet)

        log_info(f"FleetOrderProcessor: Colonization successful. {empire.name} claimed {final_planet.name}")
        return ColonizeResult(colonized=True, planet_name=final_planet.name)

    def process_transfer(
        self,
        fleet: Fleet,
        empire,
        galaxy
    ) -> TransferResult:
        """
        Process a TRANSFER order.

        PROJ-68: Transfers cargo between fleet and colony.

        Args:
            fleet: Fleet with TRANSFER order
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet lookup

        Returns:
            TransferResult with transfer status
        """
        from game.strategy.validation import TransferValidator
        from game.strategy.data.planet import SpeciesPopulation

        order = fleet.get_current_order()
        if not order or order.type != OrderType.TRANSFER:
            return TransferResult(success=False, message="No TRANSFER order")

        # Extract params from order target dict
        params = order.target
        if not isinstance(params, dict):
            fleet.pop_order()
            return TransferResult(success=False, message="Invalid transfer params")

        direction = params.get('direction', '')
        cargo_type = params.get('cargo_type', '')
        amount = params.get('amount', 0)
        planet_id = params.get('planet_id')
        species_id = params.get('species_id')

        # Resolve planet
        planet = galaxy.get_planet_by_id(planet_id) if planet_id else None

        # Validate
        validation = TransferValidator.validate(
            galaxy, fleet, planet, cargo_type, direction, amount, species_id
        )

        if not validation.is_valid:
            log_warning(f"FleetOrderProcessor: Transfer failed - {validation.message}")
            fleet.pop_order()
            return TransferResult(success=False, message=validation.message)

        # Execute transfer
        transferred = 0

        if direction == "load":
            transferred = self._execute_load(fleet, planet, cargo_type, amount, empire, species_id)
        else:  # unload
            transferred = self._execute_unload(fleet, planet, cargo_type, amount, empire, species_id)

        fleet.pop_order()
        log_info(f"FleetOrderProcessor: Transfer complete. {direction}ed {transferred} {cargo_type}")
        return TransferResult(success=True, amount_transferred=transferred)

    def _execute_load(
        self,
        fleet: Fleet,
        planet,
        cargo_type: str,
        amount: int,
        empire,
        species_id: str = None
    ) -> int:
        """Execute a load operation (colony → fleet)."""
        from game.strategy.data.planet import SpeciesPopulation

        if cargo_type == "passengers":
            # Determine how much to load
            capacity = fleet.get_fleet_cargo_capacity("passengers")
            current = fleet.get_fleet_cargo_current("passengers")
            available_space = capacity - current

            # If amount is 0, load as much as possible
            to_load = amount if amount > 0 else available_space

            # Cap by available space
            to_load = min(to_load, available_space)

            # Cap by colony population
            if planet.populations:
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
                fleet.load_cargo_to_fleet("passengers", to_load)

                return to_load

        return 0

    def _execute_unload(
        self,
        fleet: Fleet,
        planet,
        cargo_type: str,
        amount: int,
        empire,
        species_id: str = None
    ) -> int:
        """Execute an unload operation (fleet → colony)."""
        from game.strategy.data.planet import SpeciesPopulation

        if cargo_type == "passengers":
            # Determine how much to unload
            current_cargo = fleet.get_fleet_cargo_current("passengers")

            # If amount is 0, unload all
            to_unload = amount if amount > 0 else current_cargo

            # Cap by what we actually have
            to_unload = min(to_unload, current_cargo)

            if to_unload <= 0:
                return 0

            # Unload from fleet
            actual_unloaded = fleet.unload_cargo_from_fleet("passengers", to_unload)

            # Add to colony population
            # Use provided species_id or empire's race_id
            race_id = species_id or (empire.race_config.race_id if empire.race_config else "default")

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

        return 0

    def _transfer_founding_population(
        self,
        fleet: Fleet,
        planet,
        empire
    ) -> int:
        """
        Transfer passengers from fleet to colony as founding population.

        PROJ-68: When colonizing, passengers become the founding population.
        If no passengers but empire has race_config, seed minimum 100 units.

        Args:
            fleet: Fleet that colonized the planet
            planet: Newly colonized planet
            empire: Empire that owns the colony

        Returns:
            Number of population units seeded.
        """
        from game.strategy.data.planet import SpeciesPopulation

        # Get passengers from fleet
        # Wrap in try/except for mock compatibility in tests
        try:
            passengers = fleet.get_fleet_cargo_current("passengers")
        except (AttributeError, TypeError):
            passengers = 0

        # Determine founding population
        founding_pop = passengers if isinstance(passengers, int) else 0

        # If no passengers but empire has race_config, seed minimum
        race_config = getattr(empire, 'race_config', None)
        # Check for actual RaceConfig (not MagicMock) - RaceConfig has race_id attribute
        has_race_config = (
            race_config is not None
            and hasattr(race_config, 'race_id')
            and isinstance(getattr(race_config, 'race_id', None), str)
        )

        if founding_pop == 0 and has_race_config:
            founding_pop = 100  # Minimum seed: 100K people

        if founding_pop <= 0:
            return 0

        # Unload passengers from fleet (if any)
        if passengers > 0:
            try:
                fleet.unload_cargo_from_fleet("passengers", passengers)
            except (AttributeError, TypeError):
                pass  # Mock fleet, skip unload

        # Determine race_id from empire
        race_id = empire.race_config.race_id if empire.race_config else "default"

        # Create founding population on planet
        species_pop = SpeciesPopulation(
            race_id=race_id,
            count=founding_pop,
            happiness=0.5  # Neutral starting happiness
        )
        planet.populations.append(species_pop)

        log_debug(f"Colonization: Seeded {founding_pop} {race_id} on {planet.name}")
        return founding_pop

    def process_end_turn_orders(
        self,
        fleet: Fleet,
        empire,
        galaxy,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Process static orders at end of turn (COLONIZE, JOIN_FLEET, TRANSFER).

        PROJ-55: Added component_registry for colony pod ship removal.
        PROJ-68: Added TRANSFER order processing.

        Args:
            fleet: Fleet to process
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation
            component_registry: Optional component registry for colony pod lookup.
                               When provided, only the colony ship is removed.

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise
        """
        order = fleet.get_current_order()
        if not order:
            return False

        if order.type == OrderType.BUILD:
            # BUILD order persists until construction_queue is empty
            # It does not "complete" in the traditional sense - it auto-pops when queue empties
            if not fleet.construction_queue:
                # Queue is empty, auto-complete the BUILD order
                fleet.pop_order()
                log_debug(f"Fleet {fleet.id} BUILD order completed - queue empty")
            # BUILD does not consume the fleet
            return False

        elif order.type == OrderType.COLONIZE:
            # PROJ-55: Pass component registry for ship removal
            result = self.process_colonize(
                fleet, empire, galaxy, component_registry=component_registry
            )
            return result.colonized

        elif order.type == OrderType.JOIN_FLEET:
            result = self.process_join_fleet(fleet, empire, galaxy)
            return result.merged

        elif order.type == OrderType.TRANSFER:
            # PROJ-68: Process cargo transfer
            self.process_transfer(fleet, empire, galaxy)
            # TRANSFER does not consume the fleet
            return False

        return False

    def process_instant_orders(
        self,
        empires: List
    ) -> List[Tuple]:
        """
        Process instant orders during tick (JOIN_FLEET when co-located).

        This processes JOIN_FLEET orders for any fleets that are already
        co-located with their target. Happens every subtick.

        Args:
            empires: List of Empire objects

        Returns:
            List of (empire, fleet) tuples for removed fleets
        """
        fleets_to_remove = []

        for empire in empires:
            for fleet in list(empire.fleets):  # Copy list since we may modify it
                order = fleet.get_current_order()
                if order and order.type == OrderType.JOIN_FLEET:
                    target_fleet = order.target
                    if target_fleet and hasattr(target_fleet, 'location'):
                        if fleet.location == target_fleet.location:
                            log_debug(f"FleetOrderProcessor [Instant]: Fleet {fleet.id} merging into {target_fleet.id}")
                            fleet.merge_with(target_fleet)
                            fleets_to_remove.append((empire, fleet))

        # Remove merged fleets
        for empire, fleet in fleets_to_remove:
            empire.remove_fleet(fleet)

        return fleets_to_remove
