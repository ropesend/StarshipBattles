from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Set, TYPE_CHECKING

from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode
from game.core.validation_helpers import require_keys, safe_from_dict

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.galaxy import Galaxy

logger = logging.getLogger(__name__)


class Empire:
    """
    Represents a player or AI faction.
    """
    def __init__(self, empire_id, name, color, theme_path=None, empire_theme_id="Federation",
                 flag_id: str = "", portrait_id: str = "", race_config=None):
        self.id = empire_id
        self.name = name
        self.color = color
        self.theme_path = theme_path
        self.empire_theme_id = empire_theme_id  # Ship theme for this empire's designs
        # Race visual identity (from RaceConfig selection during game setup)
        self.flag_id = flag_id  # Custom flag directory (e.g., "flag_2fl0bh2fl0bh2fl0")
        self.portrait_id = portrait_id  # Race portrait filename
        # Full race configuration for habitability/growth calculations
        self.race_config = race_config  # RaceConfig or None

        self.colonies = [] # List[Planet]
        self.fleets = [] # List[Fleet]

        # Design library tracking (Phase 3)
        self.designed_ships = []  # List[DesignMetadata] - cached design list
        self.built_ship_designs = set()  # Set of design_ids that were ever built

        # Fleet display number generator (per-empire sequential, cosmetic only)
        self._next_fleet_display_number = 1

        # Ship serial number counters - per design_id
        self._design_serial_counters = {}  # Dict[str, int]

        # Galaxy back-reference for auto fleet registration (PROJ-219)
        self._galaxy: Optional['Galaxy'] = None

        # Empire-wide resource economy
        # resource_pool is now a read-only aggregate of colony stockpiles (see property below).
        # _fleet_resource_pool is temporary storage for fleet construction until Phase 6 (fleet cargo).
        self._fleet_resource_pool = {}  # Dict[str, float] - fleet construction resources
        self.max_storage = {}     # Dict[str, float] - aggregate storage capacity (set by HarvestingEngine)

    def is_eliminated(self) -> bool:
        """Return True when this empire owns no fleets and no colonies.

        Pure read; no side effects. Used by the hot-seat turn-start hook
        (issue #25) to detect defeat, remove the empire from the rotation,
        and fire a one-shot defeat modal. AI/non-human empires use the
        same predicate.
        """
        return len(self.fleets) == 0 and len(self.colonies) == 0

    def add_colony(self, planet) -> None:
        if planet not in self.colonies:
            self.colonies.append(planet)
            planet.owner_id = self.id

    def remove_colony(self, planet) -> bool:
        """Remove a planet from this empire's colonies.

        PROJ-370 Phase 4: data-class-internal helper symmetric with
        ``add_colony``. Does NOT clear ``planet.owner_id`` — that's the
        caller's responsibility (PlanetWriteService.set_owner_id).

        Returns True if the planet was in the colony list and removed.
        """
        if planet in self.colonies:
            self.colonies.remove(planet)
            return True
        return False

    def add_fleet(self, fleet) -> None:
        """Add fleet to empire and auto-register with galaxy for O(1) lookup.

        PROJ-219: Automatically registers the fleet with the galaxy entity
        registry when a galaxy back-reference is set, eliminating the need
        for separate galaxy.register_fleet() calls at each creation site.
        """
        self.fleets.append(fleet)
        fleet.owner_id = self.id
        if self._galaxy:
            self._galaxy.register_fleet(fleet)

    def remove_fleet(self, fleet, event_bus=None) -> None:
        """Remove fleet from empire and auto-unregister from galaxy.

        PROJ-219: Automatically unregisters the fleet from the galaxy entity
        registry, preventing ghost fleets from remaining in the registry
        after destruction, merging, or scuttling.

        PROJ-222: Cancels all pursuer orders targeting this fleet and logs
        FLEET_JOIN_CANCELLED events before removal.

        Args:
            fleet: Fleet to remove.
            event_bus: Optional EventBus for structured event logging.
        """
        if fleet in self.fleets:
            # PROJ-222: Cancel all pursuer orders before removing fleet
            # PROJ-382 Phase 2 (Pattern #10): emit only via injected event_bus.
            if hasattr(fleet, 'pursuer_tracker'):
                cancelled = fleet.pursuer_tracker.notify_target_destroyed()
                if cancelled and event_bus is not None:
                    from game.strategy.events.event_types import EventType, EventCategory
                    for pursuer in cancelled:
                        event_bus.log_event(
                            EventType.FLEET_JOIN_CANCELLED,
                            category=EventCategory.FLEET_OPERATIONS,
                            empire_id=pursuer.owner_id,
                            message=f"Fleet {pursuer.id} join order cancelled: target Fleet {fleet.id} destroyed",
                            fleet_id=pursuer.id,
                            target_fleet_id=fleet.id,
                        )

            self.fleets.remove(fleet)
            if self._galaxy:
                self._galaxy.unregister_fleet(fleet)

    def get_next_fleet_display_number(self) -> int:
        """Generate per-empire sequential display number for fleet naming.

        This is cosmetic only — used for auto-naming fleets ("Fleet 1",
        "Fleet 2") without leaking information about other empires' fleet
        counts. The actual fleet identity is the globally unique ID from
        Galaxy.get_next_fleet_id().
        """
        num = self._next_fleet_display_number
        self._next_fleet_display_number += 1
        return num

    def get_next_serial(self, design_id: str) -> int:
        """
        Generate unique sequential serial number for a ship design.

        Each design_id has its own counter starting at 1.

        Args:
            design_id: The ship design identifier

        Returns:
            Next serial number for this design (1, 2, 3, ...)
        """
        current = self._design_serial_counters.get(design_id, 0)
        next_serial = current + 1
        self._design_serial_counters[design_id] = next_serial
        return next_serial

    def set_galaxy(self, galaxy: 'Galaxy') -> None:
        """Set galaxy reference for auto fleet registration/unregistration.

        Call after construction when galaxy is available later
        (e.g., during deserialization).
        """
        self._galaxy = galaxy

    # --- Resource Economy Methods ---

    @property
    def resource_pool(self) -> Dict[str, float]:
        """Read-only aggregate of all colony stockpiles.

        Returns the sum of stockpile values across all colonies.
        Used for UI display and economy reporting.
        """
        totals: Dict[str, float] = {}
        for colony in self.colonies:
            for res, amount in colony.stockpile.items():
                totals[res] = totals.get(res, 0.0) + amount
        # Include fleet resource pool (temporary, until Phase 6 fleet cargo)
        for res, amount in self._fleet_resource_pool.items():
            totals[res] = totals.get(res, 0.0) + amount
        return totals

    @resource_pool.setter
    def resource_pool(self, value: Dict[str, float]) -> None:
        """Setter for backward compatibility (used by deserialization).

        Distributes resources to first colony's stockpile if colonies exist,
        otherwise stores in fleet resource pool.
        """
        if self.colonies:
            # Distribute to first colony (for save game loading)
            self.colonies[0].stockpile = dict(value)
        else:
            self._fleet_resource_pool = dict(value)

    def add_resources(self, resource_type: str, amount: float) -> float:
        """Add resources to the fleet resource pool.

        Used for fleet construction resources. For planet resources,
        use planet.add_to_stockpile() directly.

        Args:
            resource_type: Resource identifier (e.g. "metals", "organics").
            amount: Amount to add.

        Returns:
            Overflow amount (0.0 if all fit within storage).
        """
        current = self._fleet_resource_pool.get(resource_type, 0.0)
        max_cap = self.max_storage.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            self._fleet_resource_pool[resource_type] = max_cap
            return new_total - max_cap
        self._fleet_resource_pool[resource_type] = new_total
        return 0.0

    def consume_resources(self, resource_type: str, amount: float) -> bool:
        """Consume resources from the fleet resource pool (all-or-nothing).

        Used for fleet construction. For planet resources,
        use planet.consume_from_stockpile() directly.

        Args:
            resource_type: Resource identifier.
            amount: Amount to consume.

        Returns:
            True if successful, False if insufficient (no deduction made).
        """
        current = self._fleet_resource_pool.get(resource_type, 0.0)
        if current >= amount:
            self._fleet_resource_pool[resource_type] = current - amount
            return True
        return False

    def has_resources(self, costs: dict) -> bool:
        """Check if the empire has all required resources (aggregate).

        Checks across all colony stockpiles plus fleet resource pool.

        Args:
            costs: Dict mapping resource_type -> required amount.

        Returns:
            True if all resources are available.
        """
        pool = self.resource_pool  # computed aggregate
        for resource_type, amount in costs.items():
            if pool.get(resource_type, 0.0) < amount:
                return False
        return True

    def get_resource(self, resource_type: str) -> float:
        """Get current amount of a resource type (aggregate).

        Returns 0.0 if the resource type is not in the pool.
        """
        return self.resource_pool.get(resource_type, 0.0)

    # --- Population Queries (PROJ-287) ---

    def resident_species(self) -> Set[str]:
        """Return the set of race_ids with count >= 1 anywhere in this
        empire's colonies (PROJ-287).

        Canonical "species living in this empire" set — consumed by UI
        that iterates per-species (e.g. PROJ-290's uncolonized-habitability
        display). A species is included if ANY colony has at least one
        population unit; species with count=0 on every colony are excluded
        as extinct.

        Not cached — empires have O(10-100) colonies × O(1-5) species, so
        the iteration is cheap compared to the invalidation complexity a
        cache would require (population growth, extinction, colonization).
        """
        species: Set[str] = set()
        for colony in self.colonies:
            for pop in colony.populations:
                if pop.count >= 1:
                    species.add(pop.race_id)
        return species

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize Empire to dict.

        Stores colony IDs only (not full Planet objects) to avoid circular references.
        Planets will be resolved during load via galaxy.get_planet_by_id().
        """
        data = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'theme_path': self.theme_path,
            'empire_theme_id': self.empire_theme_id,
            'colony_ids': [p.id for p in self.colonies],  # Store IDs only
            'fleets': [f.to_dict() for f in self.fleets],
            'built_ship_designs': sorted(self.built_ship_designs),
            '_next_fleet_display_number': self._next_fleet_display_number,
            '_design_serial_counters': self._design_serial_counters,
            'resource_pool': dict(self._fleet_resource_pool),
            'max_storage': dict(self.max_storage),
        }
        # Include race visual identity if set (optional fields)
        if self.flag_id:
            data['flag_id'] = self.flag_id
        if self.portrait_id:
            data['portrait_id'] = self.portrait_id
        # Include full race config if set
        if self.race_config is not None:
            data['race_config'] = self.race_config.to_dict()
        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
        galaxy=None,
        registries: Optional['GameRegistries'] = None
    ) -> 'Empire':
        """
        Deserialize Empire from dict.

        Args:
            data: Saved empire data
            galaxy: Galaxy instance for resolving planet references (required)
            registries: Optional GameRegistries for DI. If provided, fleets
                and ships will use these registries.

        Returns:
            Reconstructed Empire with colonies resolved

        Raises:
            PersistenceException: If required keys missing
        """
        require_keys(data, ['id', 'name', 'color'], 'Empire')

        from game.strategy.data.fleet import Fleet
        from game.strategy.data.race_config import RaceConfig

        # Deserialize race_config if present (with error handling)
        race_config = None
        if 'race_config' in data:
            race_config = safe_from_dict(RaceConfig.from_dict, data['race_config'], 'Empire.race_config')

        empire = cls(
            empire_id=data['id'],
            name=data['name'],
            color=data['color'],
            theme_path=data.get('theme_path'),
            empire_theme_id=data.get('empire_theme_id', 'Federation'),
            flag_id=data.get('flag_id', ''),
            portrait_id=data.get('portrait_id', ''),
            race_config=race_config
        )

        # Restore built_ship_designs set
        empire.built_ship_designs = set(data.get('built_ship_designs', []))

        # Restore fleet display number counter
        empire._next_fleet_display_number = data.get('_next_fleet_display_number', 1)

        # Restore ship serial counters
        empire._design_serial_counters = data.get('_design_serial_counters', {})

        # Restore resource economy
        # For old saves: resources stored at empire level go to _fleet_resource_pool
        # (colonies loaded below will have their own stockpiles in new saves)
        empire._fleet_resource_pool = data.get('resource_pool', {})
        empire.max_storage = data.get('max_storage', {})

        # PROJ-251: Strict deserialization — corrupt fleets fail the load
        # PROJ-211: Pass registries for DI
        empire.fleets = []
        for i, fleet_data in enumerate(data.get('fleets', [])):
            try:
                fleet = Fleet.from_dict(fleet_data, registries=registries)
                fleet.owner_id = empire.id
                empire.fleets.append(fleet)
            except (PersistenceException, KeyError, TypeError, ValueError) as e:
                raise PersistenceException(
                    f"Corrupt fleet data at index {i} in empire '{data.get('id', '?')}'",
                    code=ErrorCode.CORRUPT_DATA.value,
                    context={"empire_id": data.get('id'), "fleet_index": i, "original_error": str(e)}
                ) from e

        # Resolve colony references via galaxy
        if galaxy is not None:
            for planet_id in data.get('colony_ids', []):
                planet = galaxy.get_planet_by_id(planet_id)
                if planet:
                    empire.colonies.append(planet)
                    planet.owner_id = empire.id

        return empire
