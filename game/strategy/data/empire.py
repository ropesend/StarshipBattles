import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

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

        # Fleet ID generator
        self._next_fleet_id = 10000

        # Ship serial number counters - per design_id
        self._design_serial_counters = {}  # Dict[str, int]

        # Galaxy back-reference for auto fleet registration (PROJ-219)
        self._galaxy: Optional['Galaxy'] = None

        # Empire-wide resource economy (PROJ-75)
        self.resource_pool = {}   # Dict[str, float] - current resource amounts
        self.max_storage = {}     # Dict[str, float] - storage capacity per type

    def add_colony(self, planet):
        if planet not in self.colonies:
            self.colonies.append(planet)
            planet.owner_id = self.id

    def remove_colony(self, planet):
        if planet in self.colonies:
            self.colonies.remove(planet)
            planet.owner_id = None

    def add_fleet(self, fleet):
        """Add fleet to empire and auto-register with galaxy for O(1) lookup.

        PROJ-219: Automatically registers the fleet with the galaxy entity
        registry when a galaxy back-reference is set, eliminating the need
        for separate galaxy.register_fleet() calls at each creation site.
        """
        self.fleets.append(fleet)
        fleet.owner_id = self.id
        if self._galaxy:
            self._galaxy.register_fleet(fleet)

    def remove_fleet(self, fleet):
        """Remove fleet from empire and auto-unregister from galaxy.

        PROJ-219: Automatically unregisters the fleet from the galaxy entity
        registry, preventing ghost fleets from remaining in the registry
        after destruction, merging, or scuttling.

        PROJ-222: Cancels all pursuer orders targeting this fleet and logs
        FLEET_JOIN_CANCELLED events before removal.
        """
        if fleet in self.fleets:
            # PROJ-222: Cancel all pursuer orders before removing fleet
            if hasattr(fleet, 'pursuer_tracker'):
                cancelled = fleet.pursuer_tracker.notify_target_destroyed()
                if cancelled:
                    from game.core.event_logging import log_event
                    from game.strategy.events.event_types import EventType, EventCategory
                    for pursuer in cancelled:
                        log_event(
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

    def get_next_fleet_id(self) -> int:
        """Generate unique sequential fleet ID."""
        fleet_id = self._next_fleet_id
        self._next_fleet_id += 1
        return fleet_id

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

    # --- Resource Economy Methods (PROJ-75) ---

    def add_resources(self, resource_type: str, amount: float) -> float:
        """Add resources to the empire pool.

        Args:
            resource_type: Resource identifier (e.g. "Metals", "Organics").
            amount: Amount to add.

        Returns:
            Overflow amount (0.0 if all fit within storage).
        """
        current = self.resource_pool.get(resource_type, 0.0)
        max_cap = self.max_storage.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            self.resource_pool[resource_type] = max_cap
            return new_total - max_cap
        self.resource_pool[resource_type] = new_total
        return 0.0

    def consume_resources(self, resource_type: str, amount: float) -> bool:
        """Consume resources from the empire pool (all-or-nothing).

        Args:
            resource_type: Resource identifier.
            amount: Amount to consume.

        Returns:
            True if successful, False if insufficient (no deduction made).
        """
        current = self.resource_pool.get(resource_type, 0.0)
        if current >= amount:
            self.resource_pool[resource_type] = current - amount
            return True
        return False

    def has_resources(self, costs: dict) -> bool:
        """Check if the empire has all required resources.

        Args:
            costs: Dict mapping resource_type -> required amount.

        Returns:
            True if all resources are available.
        """
        for resource_type, amount in costs.items():
            if self.resource_pool.get(resource_type, 0.0) < amount:
                return False
        return True

    def get_resource(self, resource_type: str) -> float:
        """Get current amount of a resource type.

        Returns 0.0 if the resource type is not in the pool.
        """
        return self.resource_pool.get(resource_type, 0.0)

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
            'built_ship_designs': list(self.built_ship_designs),
            '_next_fleet_id': self._next_fleet_id,
            '_design_serial_counters': self._design_serial_counters,
            'resource_pool': dict(self.resource_pool),
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

        # Restore fleet ID counter
        empire._next_fleet_id = data.get('_next_fleet_id', 10000)

        # Restore ship serial counters
        empire._design_serial_counters = data.get('_design_serial_counters', {})

        # Restore resource economy (PROJ-75)
        empire.resource_pool = data.get('resource_pool', {})
        empire.max_storage = data.get('max_storage', {})

        # Restore fleets (skip corrupt entries with warning)
        # PROJ-211: Pass registries for DI
        empire.fleets = []
        for i, fleet_data in enumerate(data.get('fleets', [])):
            try:
                fleet = Fleet.from_dict(fleet_data, registries=registries)
                fleet.owner_id = empire.id
                empire.fleets.append(fleet)
            except Exception as e:
                logger.warning(f"Empire {data['id']}: skipping corrupt fleet[{i}]: {e}")

        # Resolve colony references via galaxy
        if galaxy is not None:
            for planet_id in data.get('colony_ids', []):
                planet = galaxy.get_planet_by_id(planet_id)
                if planet:
                    empire.colonies.append(planet)
                    planet.owner_id = empire.id

        return empire
