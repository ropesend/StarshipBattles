"""ProductionSpawner - Handles spawning of completed production items.

PROJ-233: Extracted from ProductionEngine to separate spawn logic from
queue processing logic. Handles ship spawning (new fleets at planets,
added to existing fleets) and facility spawning (complexes on planets).
"""

import logging
import uuid
from typing import Optional, Any, Dict, List, Mapping, Tuple, TYPE_CHECKING

from game.strategy.data.bay_inventory import DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle, VALID_VEHICLE_TYPES
from game.strategy.data.fleet import Fleet
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.ship_instance import ShipInstance

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.planet import Planet
    from game.strategy.systems.design_catalog import DesignCatalog
from game.strategy.events.event_types import EventType, EventCategory

logger = logging.getLogger(__name__)


class ProductionSpawner:
    """Handles spawning of completed production items (ships, complexes).

    PROJ-233: Extracted from ProductionEngine. Owns all entity creation,
    design loading, and event logging for completed construction items.
    """

    def __init__(
        self,
        *,
        registries: 'GameRegistries',
        event_bus=None,
        planet_mutator=None,
        design_catalogs_by_empire: "Optional[Mapping[int, DesignCatalog]]" = None,
    ):
        """Initialize the spawner.

        PROJ-382 Phase 3 (Pattern #3 strategy-layer DI tightening):
        ``registries`` is now a required keyword-only argument.  Callers
        that previously passed None (and relied on later ship-creation
        paths to silently skip mass calculation) must now thread the
        session's GameRegistries through explicitly — this matches the
        approach already taken by the ``TurnEngineConfig.create_default``
        composition path.

        Args:
            registries: GameRegistries for ship creation (required).
            event_bus: Optional EventBus for structured event logging.
            planet_mutator: PROJ-370 IPlanetMutator. Eager-defaulted to
                ``PlanetWriteService()`` when None — the previous
                lazy-fallback walked the same code path on first access
                anyway, so the eager default is a no-op behavior change
                that surfaces construction-time failures.
        """
        if registries is None:
            raise TypeError(
                "ProductionSpawner requires registries= (PROJ-382 Phase 3). "
                "Pass session.registries (or a real GameRegistries) at "
                "construction time."
            )
        self._registries = registries
        self._event_bus = event_bus
        if planet_mutator is None:
            from game.strategy.services.planet_write_service import (
                PlanetWriteService,
            )
            planet_mutator = PlanetWriteService()
        self._planet_mutator = planet_mutator
        # PROJ-427 Phase 3: per-empire DesignCatalog map for in-memory
        # design lookup during a production tick. None means "not yet
        # wired" — callers should set this via
        # ``set_design_catalogs_by_empire(...)`` before any spawn occurs.
        # Spawn paths that hit a missing catalog log a warning and skip
        # (same observable shape as the legacy "missing save_path" path).
        self._design_catalogs_by_empire: "Mapping[int, DesignCatalog]" = (
            design_catalogs_by_empire or {}
        )

    def set_design_catalogs_by_empire(
        self, catalogs: "Mapping[int, DesignCatalog]"
    ) -> None:
        """PROJ-427 Phase 3: install the per-empire ``DesignCatalog`` map.

        Called by ``SessionBootstrap`` / ``SessionPersistenceAdapter``
        after empire IDs are known and catalogs have been populated from
        disk. Mutates in place — no rewrap needed because
        ``ProductionSpawner`` is not a frozen dataclass.
        """
        self._design_catalogs_by_empire = catalogs

    def _get_catalog(self, empire: 'Empire') -> "Optional[DesignCatalog]":
        """Return the ``DesignCatalog`` for ``empire`` or ``None`` if missing."""
        return self._design_catalogs_by_empire.get(empire.id)

    def _get_planet_mutator(self) -> Any:
        # PROJ-382 Phase 3: kept as a thin accessor; the lazy-fallback
        # has been collapsed into eager construction-time defaulting
        # above, so this just returns the field.
        return self._planet_mutator

    def spawn_completed_item(self, item: Dict, empire: 'Empire',
                             colony_or_fleet: Any, galaxy: Optional['Galaxy'],
                             tick: int) -> None:
        """Dispatch to appropriate spawn method based on item type and context.

        Args:
            item: The completed queue item dict.
            empire: Empire that owns the production.
            colony_or_fleet: Build context (Planet or Fleet).
            galaxy: Galaxy for location resolution.
            tick: Current tick number (for logging).
        """
        design_id = item['design_id']
        vehicle_type = item.get('type', 'ship').lower().replace(' ', '_')

        # PROJ-FMS-A Phase 4: output normalisation. Small-craft
        # (mine / fighter / satellite) follow the unified bay-or-staging
        # rule; capital ships continue to spawn as full ShipInstance
        # entries. See PROJ-FMS-A decisions.md for the chosen flagship-
        # first-then-canonical-fleet-order bay-selection rule.
        if isinstance(colony_or_fleet, Fleet):
            if vehicle_type in ('complex', 'planetary_complex'):
                target_planet_id = item.get('target_planet_id')
                self._spawn_fleet_complex(
                    colony_or_fleet, design_id, empire, galaxy,
                    target_planet_id=target_planet_id
                )
            elif vehicle_type in ('mine', 'fighter', 'satellite'):
                self._spawn_fleet_carried_vehicle(
                    colony_or_fleet, design_id, item, empire,
                )
            else:
                self._spawn_fleet_ship(colony_or_fleet, design_id, empire)
        else:
            # Colony/planet
            if vehicle_type in ('complex', 'planetary_complex'):
                self._create_and_place_facility(
                    colony_or_fleet, design_id, empire, galaxy,
                )
            elif vehicle_type in ('drop_pod', 'fighter', 'satellite', 'mine'):
                self._spawn_to_staging_yard(
                    colony_or_fleet, design_id, item, empire,
                )
            else:
                self._spawn_ship(colony_or_fleet, design_id, empire, galaxy)

    # --- Location Resolution ---

    def _resolve_planet_location(
        self, planet: 'Planet', galaxy: Optional['Galaxy']
    ) -> Tuple[Optional[List], str, Optional[List]]:
        """Resolve event logging location info for a planet.

        PROJ-233: Extracted from duplicated blocks in _create_and_place_facility
        and _spawn_ship.

        Returns:
            Tuple of (location_hex, system_name, local_hex) where each may be
            None/empty if galaxy context is unavailable.
        """
        location_hex = None
        system_name = ""
        local_hex = None
        if galaxy and hasattr(galaxy, 'get_system_of_planet'):
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                system_name = parent_sys.name
                if hasattr(planet, 'location') and planet.location is not None:
                    loc = parent_sys.global_location + planet.location
                    location_hex = [loc.q, loc.r]
                    local_hex = [planet.location.q, planet.location.r]
        return location_hex, system_name, local_hex

    # --- Design Loading (PROJ-427 Phase 3: in-memory catalog only) ---

    def _load_design(self, design_id: str, empire: 'Empire') -> dict:
        """Look up design data from the per-empire ``DesignCatalog``.

        PROJ-427 Phase 3: pure in-memory access. No filesystem call, no
        JSON parse. The catalog is seeded once at session bootstrap from
        ``DesignRepository``; runtime production never re-reads disk.

        Args:
            design_id: Design to look up.
            empire: Empire owning the design.

        Returns:
            Design data dict, or empty dict on failure / missing catalog.
        """
        catalog = self._get_catalog(empire)
        if catalog is None:
            logger.warning(
                f"No DesignCatalog wired for empire {empire.id} - creating "
                f"empty data for {design_id}"
            )
            return {}
        data = catalog.lookup_data(design_id)
        if data is None:
            logger.warning(
                f"Could not look up design '{design_id}' in catalog for "
                f"empire {empire.id}"
            )
            return {}
        return data

    def _load_and_create_ship(
        self, design_id: str, empire: 'Empire'
    ) -> Optional[ShipInstance]:
        """Look up design and create a ship instance.

        PROJ-427 Phase 3: design data resolved via the per-empire
        ``DesignCatalog`` (in-memory). Built-count increment is recorded
        in the catalog's pending map; ``SaveGameService`` flushes it to
        disk at save time (Phase 4), so no mid-tick disk write occurs.

        Args:
            design_id: ID of the ship design.
            empire: Empire that owns the design.

        Returns:
            ShipInstance if successful, None on failure.
        """
        catalog = self._get_catalog(empire)
        if catalog is None:
            logger.warning(
                f"Cannot spawn {design_id}: no DesignCatalog wired for "
                f"empire {empire.id}"
            )
            return None

        data = catalog.lookup_data(design_id)
        if data is None:
            logger.warning(
                f"Cannot spawn {design_id}: not present in catalog for "
                f"empire {empire.id}"
            )
            return None

        ship_instance = ShipInstance.create(
            design_id=design_id,
            design_data=data,
            owner_id=empire.id,
            name=data.get("name", design_id),
            empire=empire,
            registries=self._registries,
        )

        # PROJ-427 Phase 4 prep: defer the disk-write. The increment is
        # captured in the catalog's in-memory pending map and flushed
        # through DesignRepository when the save runs.
        catalog.record_built(design_id)
        return ship_instance

    # --- Spawn Methods ---

    def _create_and_place_facility(
        self, planet: 'Planet', design_id: str, empire: 'Empire',
        galaxy: Optional['Galaxy'] = None,
        log_prefix: str = ""
    ) -> None:
        """Create a facility and place it on a planet.

        Shared by colony complex production and fleet complex production.
        Handles design loading, facility creation, placement, and event logging.

        Args:
            planet: Planet to add facility to.
            design_id: ID of the complex design.
            empire: Empire that owns the production.
            galaxy: Galaxy for location calculation.
            log_prefix: Optional prefix for log messages (e.g., "Fleet 5 ").
        """
        design_data = self._load_design(design_id, empire)

        facility = PlanetaryFacility(
            instance_id=str(uuid.uuid4()),
            design_id=design_id,
            name=design_data.get("name", design_id),
            design_data=design_data,
            is_operational=True
        )

        # PROJ-370 Phase 3: route through IPlanetMutator.
        # PROJ-412 Phase 5: pass empire so HarvestingEngine's per-turn
        # storage/booster caches see the new facility mid-turn.
        self._get_planet_mutator().add_facility(planet, facility, empire=empire)
        logger.info(f"{log_prefix}Built {facility.name} on {planet.name}")

        # Compute location info for event logging (PROJ-233: shared helper)
        location_hex, system_name, local_hex = self._resolve_planet_location(
            planet, galaxy
        )

        suffix = " (fleet yard)" if log_prefix else ""
        if self._event_bus:
            self._event_bus.log_event(
                EventType.COMPLEX_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Built {facility.name} on {planet.name}{suffix}",
                design_id=design_id,
                planet_id=planet.id,
                location_name=planet.name,
                location_hex=location_hex,
                system_name=system_name,
                local_hex=local_hex,
            )

    def _spawn_to_staging_yard(
        self,
        planet: 'Planet',
        design_id: str,
        item: Dict,
        empire: 'Empire',
    ) -> None:
        """Spawn a completed drop pod or fighter to the planet's staging yard.

        Args:
            planet: Planet where the item was built.
            design_id: Design identifier.
            item: Queue item dict with design_data.
            empire: Empire that owns the production.
        """
        design_data = item.get('design_data')
        if not design_data:
            design_data = self._load_design(design_id, empire)
        if not design_data:
            logger.warning(f"Cannot spawn to staging yard: design '{design_id}' not found")
            return

        # Calculate mass from design using simulation Ship (single source of truth)
        total_mass = 0.0
        max_hp = 0
        if self._registries:
            from game.simulation.entities.ship_design_stats import calculate_design_stats
            stats = calculate_design_stats(design_data, self._registries)
            total_mass = stats.get('mass', 0.0)
            max_hp = int(stats.get('max_hp', 0))

        vehicle_type = item.get('type', 'drop_pod').lower()
        item_name = design_data.get('name', design_id)
        # PROJ-450 Phase 2: construct typed staging entries directly.
        # CarriedVehicle covers mines / fighters / satellites (carries
        # per-instance HP for transfer round-trips); everything else
        # (e.g. drop_pod) goes to DropPod with owner_id + name + type
        # stashed in payload so the existing UI / transfer-branches
        # readers continue to find them via the dict-projection bridge.
        staging_entry: "CarriedVehicle | DropPod"
        if vehicle_type in VALID_VEHICLE_TYPES:
            staging_entry = CarriedVehicle(
                design_id=design_id,
                design_data=design_data,
                vehicle_type=vehicle_type,
                mass=total_mass,
                current_hp=max_hp,
            )
        else:
            staging_entry = DropPod(
                design_id=design_id,
                design_data=design_data,
                mass=total_mass,
                payload={
                    'name': item_name,
                    'vehicle_type': vehicle_type,
                    'owner_id': empire.id,
                },
            )

        if planet.add_to_staging_yard(staging_entry):
            logger.info(
                f"Spawned {vehicle_type} '{item_name}' "
                f"to staging yard on {planet.name} (mass: {total_mass:.0f})"
            )
            # QA-OBS-4: emit a SHIP_BUILT event so the in-game event log
            # surfaces fighter / mine / satellite / drop-pod production.
            # Without this, the staging-yard spawn path was the only
            # production output that produced zero user-visible feedback.
            if self._event_bus:
                self._event_bus.log_event(
                    EventType.SHIP_BUILT,
                    category=EventCategory.PRODUCTION,
                    empire_id=empire.id,
                    message=(
                        f"Built {vehicle_type} "
                        f"{item_name} on {planet.name} (staging yard)"
                    ),
                    design_id=design_id,
                    planet_id=planet.id,
                    location_name=planet.name,
                    vehicle_type=vehicle_type,
                )
        else:
            logger.warning(
                f"Staging yard full on {planet.name}: cannot store "
                f"'{item_name}' (mass: {total_mass:.0f})"
            )
            # QA-OBS-4: failure path also needs a visible event so the
            # player learns the output was discarded (mirrors the
            # fleet-bay-full pattern in _spawn_fleet_carried_vehicle).
            if self._event_bus:
                self._event_bus.log_event(
                    EventType.SHIP_BUILT,
                    category=EventCategory.PRODUCTION,
                    empire_id=empire.id,
                    message=(
                        f"Cannot store {vehicle_type} "
                        f"{item_name} on {planet.name} - "
                        f"staging yard full (output discarded)"
                    ),
                    design_id=design_id,
                    planet_id=planet.id,
                    location_name=planet.name,
                    vehicle_type=vehicle_type,
                )

    def _spawn_ship(
        self,
        planet: 'Planet',
        design_id: str,
        empire: 'Empire',
        galaxy: Optional['Galaxy'],
    ) -> None:
        """Spawn ship/satellite/fighter as fleet with ShipInstance.

        Args:
            planet: Planet where ship spawns.
            design_id: ID of the ship design.
            empire: Empire that owns the ship.
            galaxy: Galaxy for location calculation.
        """
        ship_instance = self._load_and_create_ship(design_id, empire)
        if ship_instance is None:
            return

        # Calculate spawn location (PROJ-233: uses shared helper for event fields)
        spawn_loc = planet.location
        system_name = ""
        local_hex = None
        if galaxy:
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                spawn_loc = parent_sys.global_location + planet.location
                system_name = parent_sys.name
                local_hex = [planet.location.q, planet.location.r]

        # Create fleet with globally unique ID from Galaxy
        fleet_id = galaxy.get_next_fleet_id() if galaxy else 0
        display_name = f"Fleet {empire.get_next_fleet_display_number()}"
        new_fleet = Fleet(fleet_id, empire.id, spawn_loc, display_name=display_name)
        new_fleet.add_ship(ship_instance)
        empire.add_fleet(new_fleet)  # PROJ-219: Auto-registers via empire._galaxy

        logger.info(f"Spawned {ship_instance.name} at {spawn_loc} (Fleet {new_fleet.id})")
        if self._event_bus:
            self._event_bus.log_event(
                EventType.SHIP_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Built {ship_instance.name} at {planet.name}",
                design_id=design_id,
                planet_id=planet.id,
                fleet_id=new_fleet.id,
                location_name=planet.name,
                location_hex=[spawn_loc.q, spawn_loc.r],
                system_name=system_name,
                local_hex=local_hex,
            )

    def _spawn_fleet_carried_vehicle(
        self,
        fleet: Fleet,
        design_id: str,
        item: Dict,
        empire: 'Empire',
    ) -> None:
        """PROJ-FMS-A Phase 4: fleet-yard-built mine / fighter / satellite.

        Bay-selection rule (decisions.md):
            1. Try the flagship's VehicleBay first.
            2. Otherwise walk ``fleet.ships`` in canonical order and
               deposit into the first ship whose VehicleBay has capacity
               and accepts this vehicle type.
            3. If no ship has compatible bay capacity, log a clear
               "no bay capacity" error and surface a UI event so the
               player can clear queue or add bays.

        The vehicle is stored as a :class:`CarriedVehicle` (typed) — its
        ``to_dict()`` form is appended to the receiving ship's
        ``carried_items`` list by the cargo manager.
        """
        from game.strategy.data.carried_vehicle import CarriedVehicle

        design_data = item.get('design_data') or self._load_design(
            design_id, empire
        )
        if not design_data:
            logger.warning(
                f"Cannot spawn carried vehicle: design '{design_id}' not found"
            )
            return

        # Calculate mass from design via the single-source-of-truth
        # ShipStatsCalculator path. Without registries we cannot accurately
        # gate bay capacity — abort cleanly.
        if self._registries is None:
            logger.warning(
                f"ProductionSpawner: missing registries; cannot spawn "
                f"carried vehicle '{design_id}'."
            )
            return
        from game.simulation.entities.ship_design_stats import calculate_design_stats
        stats = calculate_design_stats(design_data, self._registries)
        total_mass = float(stats.get('mass', 0.0))
        max_hp = int(stats.get('max_hp', 0))

        vehicle_type = item.get('type', 'fighter').lower()
        if vehicle_type == 'drop_pod':
            # Drop pods stay on the legacy pod-storage path.
            self._spawn_fleet_ship(fleet, design_id, empire)
            return
        if vehicle_type not in ("mine", "fighter", "satellite"):
            # Unknown small-craft type — fall back to full ship spawn.
            self._spawn_fleet_ship(fleet, design_id, empire)
            return

        cv = CarriedVehicle(
            design_id=design_id,
            design_data=design_data,
            vehicle_type=vehicle_type,
            mass=total_mass,
            current_hp=max_hp,
        )

        # Flagship-first; fall back to canonical fleet order.
        ordered_ships = list(fleet.ships)
        # ``fleet.flagship`` may not be exposed; treat fleet.ships[0] as the
        # flagship per existing fleet-hierarchy convention.
        # No re-ordering needed — fleet.ships[0] is already the flagship.
        for ship in ordered_ships:
            cargo_mgr = getattr(ship, "_cargo_mgr", None)
            if cargo_mgr is None:
                continue
            if cargo_mgr.can_accept_vehicle(cv):
                if cargo_mgr.load_vehicle(cv):
                    logger.info(
                        f"Fleet {fleet.id}: loaded {vehicle_type} "
                        f"'{design_id}' into {ship.name}'s VehicleBay "
                        f"(mass={total_mass:.0f})"
                    )
                    if self._event_bus:
                        self._event_bus.log_event(
                            EventType.SHIP_BUILT,
                            category=EventCategory.PRODUCTION,
                            empire_id=empire.id,
                            message=f"Fleet {fleet.id} built {vehicle_type} '{design_id}' "
                                    f"into bay on {ship.name}",
                            design_id=design_id,
                            fleet_id=fleet.id,
                            is_fleet_production=True,
                            location_hex=[fleet.location.q, fleet.location.r],
                        )
                    return
        # No bay capacity in any fleet ship.
        logger.warning(
            f"Fleet {fleet.id}: no VehicleBay capacity for {vehicle_type} "
            f"'{design_id}' (mass={total_mass:.0f}); production output dropped."
        )
        if self._event_bus:
            self._event_bus.log_event(
                EventType.SHIP_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Fleet {fleet.id}: no bay capacity for "
                        f"{vehicle_type} '{design_id}' — output discarded",
                design_id=design_id,
                fleet_id=fleet.id,
                is_fleet_production=True,
                location_hex=[fleet.location.q, fleet.location.r],
            )

    def _spawn_fleet_ship(
        self,
        fleet: Fleet,
        design_id: str,
        empire: 'Empire',
    ) -> None:
        """Spawn ship/satellite/fighter and add to the building fleet.

        PROJ-67 Phase 3: Ships built by fleet yards join the fleet directly.

        Args:
            fleet: Fleet building the ship.
            design_id: ID of the ship design.
            empire: Empire that owns the fleet.
        """
        ship_instance = self._load_and_create_ship(design_id, empire)
        if ship_instance is None:
            return

        fleet.add_ship(ship_instance)

        logger.info(f"Fleet {fleet.id} built {ship_instance.name}")
        if self._event_bus:
            self._event_bus.log_event(
                EventType.SHIP_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Fleet {fleet.id} built {ship_instance.name}",
                design_id=design_id,
                fleet_id=fleet.id,
                is_fleet_production=True,
                location_hex=[fleet.location.q, fleet.location.r],
                system_name="",
                local_hex=None,
            )

    def _spawn_fleet_complex(
        self,
        fleet: Fleet,
        design_id: str,
        empire: 'Empire',
        galaxy: Optional['Galaxy'],
        target_planet_id: Optional[int] = None
    ) -> None:
        """Spawn complex on planet at fleet's location.

        PROJ-67 Phase 3: Fleet yards can build complexes when at a planet hex.
        PROJ-79 Phase 4: Uses target_planet_id when specified.

        Args:
            fleet: Fleet building the complex.
            design_id: ID of the complex design.
            empire: Empire that owns the fleet.
            galaxy: Galaxy for planet lookup.
            target_planet_id: Specific planet ID to receive the complex (PROJ-79).
        """
        # Find planet at fleet's location
        if galaxy is None:
            logger.warning(f"Cannot spawn complex {design_id}: no galaxy provided")
            return

        planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        if not planets_at_hex:
            logger.warning(f"Cannot spawn complex {design_id}: fleet not at planet hex")
            return

        # PROJ-79: Use target_planet_id if specified, otherwise fall back to first planet
        if target_planet_id is not None:
            planet = next(
                (p for p in planets_at_hex if p.id == target_planet_id),
                planets_at_hex[0]
            )
        else:
            planet = planets_at_hex[0]

        self._create_and_place_facility(
            planet, design_id, empire, galaxy,
            log_prefix=f"Fleet {fleet.id} "
        )
