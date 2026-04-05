"""
OrderProcessor - Centralized order lifecycle management.

PROJ-238: Renamed from FleetOrderProcessor.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.
STRAT-006: Centralize order lifecycle management.
PROJ-187: execute_action_order() called by ActionExecutionEngine during ticks.
PROJ-226: Removed backward compat alias process_end_turn_orders.

Responsibilities:
- Order completion (pop_order in single location)
- Order cancellation (with reason tracking)
- JOIN_FLEET processing (instant during ticks)
- COLONIZE processing (via ActionExecutionEngine)
- TRANSFER processing (via ActionExecutionEngine)
- Superweapon processing (via ActionExecutionEngine)
- Instant order processing during ticks (JOIN_FLEET when co-located)
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
import logging

from game.core.event_logging import log_event
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.interfaces.engines import IOrderProcessor

logger = logging.getLogger(__name__)
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy

from game.strategy.data.planet import Planet


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


class OrderProcessor(IOrderProcessor):
    """
    Processor for fleet order lifecycle management.

    Centralizes order state management:
    - complete_order() - mark order as done
    - cancel_order() - cancel with reason
    - process_join_fleet() - handle JOIN_FLEET orders
    - process_colonize() - handle COLONIZE orders
    - process_instant_orders() - tick-based instant orders
    - execute_action_order() - execute action orders (COLONIZE, TRANSFER, superweapons)
    """

    def __init__(self):
        """Initialize the fleet order processor."""
        # Lazy import to avoid circular dependency
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
        self._superweapon_processor = SuperweaponOrderProcessor()

    def _execute_fleet_merge(self, fleet: Fleet, target_fleet: Fleet, empire: 'Empire') -> None:
        """Merge fleet into target and log the event.

        Shared logic for both single-fleet processing (process_join_fleet)
        and batch processing (process_instant_orders).

        Args:
            fleet: Fleet being merged (will be removed).
            target_fleet: Fleet receiving the merged ships.
            empire: Empire that owns both fleets.
        """
        fleet.merge_with(target_fleet)
        empire.remove_fleet(fleet)
        from game.core.event_logging import log_event
        from game.strategy.events.event_types import EventType, EventCategory
        log_event(
            EventType.FLEET_JOINED,
            category=EventCategory.FLEET_OPERATIONS,
            empire_id=empire.id,
            message=f"Fleet {fleet.id} joined Fleet {target_fleet.id}",
            fleet_id=fleet.id,
            target_fleet_id=target_fleet.id,
            ship_count=len(target_fleet.ships),
        )

    def process_join_fleet(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: 'Galaxy'
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

        # Validation: target must be a valid Fleet (Fleet always has location)
        if target_fleet is None:
            logger.warning("OrderProcessor: Join Fleet failed - Target invalid/destroyed.")
            fleet.pop_order()
            return JoinFleetResult(merged=False, cancelled=True)

        if fleet.location == target_fleet.location:
            logger.debug(f"OrderProcessor: Fleet {fleet.id} merging into {target_fleet.id}")
            self._execute_fleet_merge(fleet, target_fleet, empire)
            return JoinFleetResult(merged=True)
        else:
            # Not at location yet
            logger.warning("OrderProcessor: Join Fleet failed - Not at same location.")
            fleet.pop_order()
            return JoinFleetResult(merged=False)

    def process_colonize(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: 'Galaxy',
        component_registry: Dict[str, Any]
    ) -> ColonizeResult:
        """
        Process a COLONIZE order.

        Phase 2 Rework: Colony pods are cargo items. The pod is consumed from
        fleet cargo, but the ship is reusable and stays in the fleet.

        Args:
            fleet: Fleet with COLONIZE order
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet lookup
            component_registry: Kept for API compatibility. Pod lookup is now
                               cargo-based.

        Returns:
            ColonizeResult with colonization status
        """
        from game.strategy.validation import ColonizeValidator

        order = fleet.get_current_order()
        if not order or order.type != OrderType.COLONIZE:
            return ColonizeResult(colonized=False)

        # Extract target planet (may be a plain Planet or a dict with planet key)
        raw_target = order.target
        if isinstance(raw_target, dict):
            target_planet = raw_target.get('planet')
        else:
            target_planet = raw_target

        # Validate (skip chain check — we're executing, not adding)
        validation = ColonizeValidator.validate(
            galaxy, fleet, target_planet, component_registry, skip_chain_check=True
        )
        if not validation.is_valid:
            logger.warning(f"OrderProcessor: Colonize failed - {validation.message}")
            fleet.pop_order()
            return ColonizeResult(colonized=False)

        # Determine final planet (for "Any" case, pick first unowned)
        if target_planet is not None:
            final_planet = target_planet
        else:
            planets_at_loc = galaxy.get_planets_at_global_hex(fleet.location)
            valid_candidates = [p for p in planets_at_loc if p.owner_id is None]
            final_planet = valid_candidates[0] if valid_candidates else None

            if final_planet is None:
                logger.warning("OrderProcessor: No candidate planet for colonization")
                fleet.pop_order()
                return ColonizeResult(colonized=False)

        # Pre-check drop pod availability BEFORE any mutation
        if not ColonizeValidator.fleet_has_drop_pod(fleet):
            logger.warning("OrderProcessor: No drop pod in fleet")
            fleet.pop_order()
            return ColonizeResult(colonized=False)

        # Execute colonization — claim planet and deploy pod only.
        # Population and cargo transfer is handled by TRANSFER orders queued after COLONIZE.
        empire.add_colony(final_planet)
        fleet.pop_order()

        # Deploy drop pod as facility on the new colony
        self._deploy_drop_pod(fleet, final_planet)

        logger.info(f"OrderProcessor: Colonization successful. {empire.name} claimed {final_planet.name}")

        # Look up system name and local hex for granular event log columns
        system_name = ""
        local_hex = None
        if galaxy and hasattr(galaxy, 'get_system_of_planet'):
            sys = galaxy.get_system_of_planet(final_planet)
            if sys:
                system_name = sys.name
                if hasattr(final_planet, 'location') and final_planet.location is not None:
                    local_hex = [final_planet.location.q, final_planet.location.r]

        log_event(
            EventType.COLONY_FOUNDED,
            category=EventCategory.COLONIES,
            empire_id=empire.id,
            message=f"Founded colony on {final_planet.name}",
            planet_id=final_planet.id,
            planet_name=final_planet.name,
            fleet_id=fleet.id,
            location_name=final_planet.name,
            location_hex=[fleet.location.q, fleet.location.r],
            system_name=system_name,
            local_hex=local_hex,
        )
        return ColonizeResult(colonized=True, planet_name=final_planet.name)

    def process_transfer(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: 'Galaxy'
    ) -> TransferResult:
        """
        Process a TRANSFER order.

        PROJ-68: Transfers cargo between fleet and colony.
        PROJ-NEW: Transfers cargo between two fleets.

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
        if not order or order.type not in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
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
        target_fleet_id = params.get('target_fleet_id')
        species_id = params.get('species_id')

        # Resolve target
        target = None
        if planet_id:
            target = galaxy.get_planet_by_id(planet_id)
        elif not planet_id and not target_fleet_id and order.type == OrderType.LOAD_POPULATION:
            # BUG-70: Generic LOAD_POPULATION — auto-resolve colony at fleet's current hex
            planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
            for p in planets_at_hex:
                if p.owner_id == empire.id and hasattr(p, 'populations') and p.populations and p.total_population > 0:
                    target = p
                    logger.debug(f"BUG-70: Auto-resolved colony {p.name} (pop={p.total_population}) at fleet hex {fleet.location}")
                    break
            if not target:
                # No owned colony at fleet hex — no-op, continue with next order
                logger.debug(f"BUG-70: No owned colony at fleet hex {fleet.location}, skipping LOAD_POPULATION")
                fleet.pop_order()
                return TransferResult(success=True, message="No colony at location, skipped")
        elif target_fleet_id:
            # Need to find fleet by ID. OrderProcessor doesn't have session access here usually,
            # but we can look through the empire's fleets or all empires.
            from game.core.protocols import is_planet, is_fleet
            # Search all empires for the target fleet
            # NOTE: galaxy may not have 'empires' attr - depends on context
            for emp in getattr(galaxy, 'empires', []):
                for f in emp.fleets:
                    if f.id == target_fleet_id:
                        target = f
                        break
                if target: break
            
            # If not found in galaxy.empires, try searching the current empire
            if not target:
                for f in empire.fleets:
                    if f.id == target_fleet_id:
                        target = f
                        break

        # Validate — skip location check for drop_pod (fleet is already at planet via MOVE order)
        skip_loc = cargo_type == "drop_pod"
        logger.info(
            f"OrderProcessor.process_transfer: fleet={fleet.id} cargo={cargo_type} "
            f"dir={direction} amt={amount} species={species_id} "
            f"target={getattr(target, 'name', target)} skip_loc={skip_loc}"
        )
        validation = TransferValidator.validate(
            galaxy, fleet, target, cargo_type, direction, amount, species_id,
            skip_location_check=skip_loc
        )

        if not validation.is_valid:
            logger.warning(
                f"OrderProcessor: Transfer failed - {validation.message} "
                f"(code={validation.error_code})"
            )
            fleet.pop_order()
            return TransferResult(success=False, message=validation.message)

        # Execute transfer
        transferred = 0
        from game.core.protocols import is_planet, is_fleet

        if is_planet(target):
            if direction == "load":
                logger.info(f"OrderProcessor: Executing LOAD {cargo_type} from {target.name}")
                transferred = self._execute_load(fleet, target, cargo_type, amount, empire, species_id)
            else:  # unload
                logger.info(f"OrderProcessor: Executing UNLOAD {cargo_type} to {target.name}")
                transferred = self._execute_unload(fleet, target, cargo_type, amount, empire, species_id)
        elif is_fleet(target):
            transferred = self._execute_fleet_transfer(fleet, target, cargo_type, direction, amount, species_id)

        fleet.pop_order()
        logger.info(f"OrderProcessor: Transfer complete. {direction}ed {transferred} {cargo_type}")
        return TransferResult(success=True, amount_transferred=transferred)

    def _execute_fleet_transfer(
        self,
        fleet: Fleet,
        target_fleet: Fleet,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: str = None
    ) -> int:
        """Execute a transfer between two fleets.

        Works for all cargo types: passengers, resources (metals, fuel, etc.).
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

    def _execute_load(
        self,
        fleet: Fleet,
        planet: 'Planet',
        cargo_type: str,
        amount: int,
        empire: 'Empire',
        species_id: str = None
    ) -> int:
        """Execute a load operation (colony → fleet)."""
        from game.strategy.data.planet import SpeciesPopulation

        if cargo_type == "drop_pod":
            return self._load_pod_from_staging_yard(fleet, planet, species_id, amount)

        if cargo_type == "passengers":
            # Determine how much to load
            capacity = fleet.resources.get_fleet_cargo_capacity("passengers")
            current = fleet.resources.get_fleet_cargo_current("passengers")
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
                fleet.resources.load_cargo_to_fleet("passengers", to_load)

                return to_load

        # Resource cargo (metals, organics, fuel, etc.)
        # Load from planet stockpile → fleet cargo
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

    def _execute_unload(
        self,
        fleet: Fleet,
        planet: 'Planet',
        cargo_type: str,
        amount: int,
        empire: 'Empire',
        species_id: str = None
    ) -> int:
        """Execute an unload operation (fleet → colony)."""
        from game.strategy.data.planet import SpeciesPopulation

        if cargo_type == "drop_pod":
            return self._unload_pod_to_staging_yard(fleet, planet, species_id, amount)

        if cargo_type == "passengers":
            # Determine how much to unload
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

        # Resource cargo (metals, organics, fuel, etc.)
        # Unload from fleet cargo → planet stockpile
        current_cargo = fleet.resources.get_fleet_cargo_current(cargo_type)
        to_unload = amount if amount > 0 else current_cargo
        to_unload = min(to_unload, current_cargo)

        if to_unload <= 0:
            return 0

        actual_unloaded = fleet.resources.unload_cargo_from_fleet(cargo_type, to_unload)
        planet.add_to_stockpile(cargo_type, float(actual_unloaded))
        return actual_unloaded

    def _load_pod_from_staging_yard(
        self, fleet: Fleet, planet, pod_name: str = None, amount: int = 0
    ) -> int:
        """Load drop pod(s) from planet staging yard to ship carried_items.

        Args:
            fleet: Fleet to load pods onto.
            planet: Planet with staging yard.
            pod_name: Name of pod to load (from species_id field). If None, load any.
            amount: Number of pods to load (0 = load all that fit).
        """
        logger.info(
            f"_load_pod_from_staging_yard: planet={planet.name} pod_name={pod_name!r} "
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
            if pod_name and item.get('name') != pod_name:
                logger.debug(
                    f"  Skipping staging item {i}: name={item.get('name')!r} != {pod_name!r}"
                )
                continue
            pod_mass = item.get('mass', 0.0)
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

    def _unload_pod_to_staging_yard(
        self, fleet: Fleet, planet, pod_name: str = None, amount: int = 0
    ) -> int:
        """Unload drop pod(s) from ship carried_items to planet staging yard.

        Args:
            fleet: Fleet to unload pods from.
            planet: Planet to receive pods.
            pod_name: Name of pod to unload. If None, unload any.
            amount: Number of pods to unload (0 = unload all).
        """
        unloaded = 0
        to_unload = amount if amount > 0 else sum(
            len(getattr(s, 'carried_items', [])) for s in fleet.ships
        )

        for ship in fleet.ships:
            if unloaded >= to_unload:
                break
            for i in range(len(ship.carried_items) - 1, -1, -1):
                if unloaded >= to_unload:
                    break
                item = ship.carried_items[i]
                if pod_name and item.get('name') != pod_name:
                    continue
                if planet.add_to_staging_yard(item):
                    ship.carried_items.pop(i)
                    unloaded += 1

        return unloaded

    def _deploy_drop_pod(self, fleet: Fleet, planet) -> None:
        """Deploy a drop pod from fleet cargo as a facility on the planet.

        Finds the first drop pod in any ship's carried_items, removes it,
        and creates a PlanetaryFacility from its design_data. The full
        design (all components the player chose) becomes the facility.
        """
        from uuid import uuid4
        from game.strategy.data.planet import PlanetaryFacility
        from game.strategy.validation.colonize_validator import ColonizeValidator

        ship, item_index = ColonizeValidator.find_ship_with_drop_pod(fleet)
        if ship is None:
            logger.warning("_deploy_drop_pod: No drop pod found in fleet")
            return

        # Remove the drop pod from the ship
        drop_pod = ship.carried_items.pop(item_index)
        design_data = drop_pod.get('design_data', {})

        facility = PlanetaryFacility(
            instance_id=uuid4().hex,
            design_id=drop_pod.get('design_id', 'drop_pod'),
            name=drop_pod.get('name', 'Colony Drop Pod'),
            design_data=design_data,
            is_operational=True,
        )
        planet.facilities.append(facility)

        # Seed planet stockpile from design's initial_stockpile if present
        initial_stock = design_data.get("initial_stockpile", {})
        for resource, amount in initial_stock.items():
            planet.add_to_stockpile(resource, float(amount))

        logger.info(f"Deployed drop pod '{facility.name}' on {planet.name}")


    def execute_action_order(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: 'Galaxy',
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List['Empire']] = None
    ) -> bool:
        """
        Execute the fleet's current action order (COLONIZE, TRANSFER, superweapons).

        PROJ-207: Renamed from process_end_turn_orders. Uses handler registry.
        Called by ActionExecutionEngine when action progress reaches action_time.

        Args:
            fleet: Fleet to process
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation
            component_registry: Component registry for colony pod lookup.
                               Required for COLONIZE orders.
            empires: Optional list of all empires (needed for STELLERATE_STAR).

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise
        """
        order = fleet.get_current_order()
        if not order:
            return False

        # Note: BUILD orders are handled by ActionExecutionEngine.execute_tick()
        # which auto-pops them when construction_queue is empty. They never reach here.
        # Note: JOIN_FLEET is handled ONLY by process_instant_orders() when co-located.

        # COLONIZE handler
        if order.type == OrderType.COLONIZE:
            if component_registry is None:
                logger.error("OrderProcessor: COLONIZE order requires component_registry")
                fleet.pop_order()
                return False
            result = self.process_colonize(
                fleet, empire, galaxy, component_registry=component_registry
            )
            return result.colonized

        # TRANSFER/LOAD/UNLOAD handlers (all map to process_transfer)
        if order.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
            self.process_transfer(fleet, empire, galaxy)
            return False  # TRANSFER does not consume the fleet

        # Superweapon handlers
        proc = self._superweapon_processor
        superweapon_handlers = {
            OrderType.IMPLODE_PLANET: lambda: proc.process_implode_planet(
                fleet, empire, galaxy, empires or [], component_registry
            ),
            OrderType.STELLERATE_STAR: lambda: proc.process_stellerate_star(
                fleet, empire, galaxy, empires or [], component_registry
            ),
            OrderType.OPEN_WARP_POINT: lambda: proc.process_open_warp_point(
                fleet, empire, galaxy, empires or [], component_registry
            ),
            OrderType.CLOSE_WARP_POINT: lambda: proc.process_close_warp_point(
                fleet, empire, galaxy, empires or [], component_registry
            ),
            OrderType.CREATE_DYSON_SPHERE: lambda: proc.process_create_dyson_sphere(
                fleet, empire, galaxy, empires or [], component_registry
            ),
            OrderType.SELF_DESTRUCT: lambda: proc.process_self_destruct(
                fleet, empire, galaxy
            ),
        }

        handler = superweapon_handlers.get(order.type)
        if handler:
            result = handler()
            return result.fleet_consumed

        return False

    def process_instant_orders(
        self,
        empires: List['Empire']
    ) -> List[Tuple['Empire', Fleet]]:
        """
        Process instant orders during tick (JOIN_FLEET when co-located).

        This processes JOIN_FLEET orders for any fleets that are already
        co-located with their target. Happens every subtick.

        Args:
            empires: List of Empire objects

        Returns:
            List of (empire, fleet) tuples for removed fleets
        """
        fleets_to_merge = []

        for empire in empires:
            for fleet in list(empire.fleets):  # Copy list since we may modify it
                order = fleet.get_current_order()
                if order and order.type == OrderType.JOIN_FLEET:
                    target_fleet = order.target
                    if target_fleet is not None and fleet.location == target_fleet.location:
                        logger.debug(f"FleetOrderProcessor [Instant]: Fleet {fleet.id} merging into {target_fleet.id}")
                        fleets_to_merge.append((empire, fleet, target_fleet))

        # Execute merges (deferred to avoid modifying lists during iteration)
        result = []
        for empire, fleet, target_fleet in fleets_to_merge:
            self._execute_fleet_merge(fleet, target_fleet, empire)
            result.append((empire, fleet))

        return result
