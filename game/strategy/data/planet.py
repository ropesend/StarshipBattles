"""
Planet data class.

PROJ-372 Phase 2: query/calc methods (active_abilities, is_ability_active,
occupied_hexes, can_build_type) routed through `PlanetQueryService`;
habitability calculator made injectable via `ApplicationContext`.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Any
from typing import TYPE_CHECKING as _TC
from game.core.hex_math import HexCoord

if _TC:
    from game.strategy.data.order_types import Order
    from game.strategy.data.planetary_facility import PlanetaryFacility
    from game.strategy.data.species_population import SpeciesPopulation

# PROJ-284: per-colony per-species config (food allocation slider, etc.).
# Runtime dependency: dataclass field at line 107, return annotation at
# line 187, constructor call at line 190.
from game.strategy.data.colony_species_config import ColonySpeciesConfig

class PlanetType(Enum):
    """
    Broad classification of planetary bodies.
    Derived from physical properties.
    """
    CONTINENTAL = auto() # Earth-like
    ARID = auto()        # Desert
    PELAGIC = auto()     # Ocean World
    MAGMA = auto()       # Volcanic / Lava
    CRYOPLANET = auto()  # Ice Surface
    BARREN = auto()      # Rock / Scorched
    JOVIAN = auto()      # Gas Giant
    ICE_GIANT = auto()   # Uranus/Neptune type
    CHTHONIAN = auto()   # Stripped Giant Core
    ICE_DWARF = auto()   # Pluto type
    PLANETOID = auto()   # Ceres / Large Asteroid
    DYSON_SPHERE = auto()  # Artificial megastructure enclosing a star

@dataclass
class Planet:
    """Represents a planetary body (Planet or Moon). SI units throughout.

    47 dataclass fields preserved verbatim for save-format compatibility
    (PROJ-372 Risk R1). PROJ-285 transient cache fields use
    ``init=False, repr=False, compare=False`` and are NOT serialized.
    """
    # Required (no defaults)
    name: str
    location: HexCoord  # Local system coords
    orbit_distance: int  # Ring number
    # Physical
    mass: float  # kg
    radius: float  # meters
    surface_area: float  # m^2
    density: float  # kg/m^3
    surface_gravity: float  # m/s^2
    # Surface conditions
    surface_pressure: float  # Pa (1 atm = 101325 Pa)
    surface_temperature: float  # K
    surface_water: float  # 0.0 - 1.0 surface coverage fraction
    # Internal
    tectonic_activity: float  # 0.0 (dead) - 1.0 (volcanic)
    magnetic_field: float  # relative to Earth

    # Fields with defaults
    atmosphere: Dict[str, float] = field(default_factory=dict)  # gas -> partial pressure (Pa)
    planet_type: PlanetType = PlanetType.BARREN
    orbit_parent_name: Optional[str] = None
    owner_id: Optional[int] = None
    construction_queue: list = field(default_factory=list)
    # FEAT-17: when True, ProductionEngine skips this colony's planetary-yard
    # base queue. Currently-progressing item retains `resources_consumed`.
    construction_queue_paused: bool = False
    deposits: Dict[str, dict] = field(default_factory=dict)  # res_id -> {quantity, quality}
    stockpile: Dict[str, float] = field(default_factory=dict)
    max_stockpile: Dict[str, float] = field(default_factory=dict)
    staging_yard: List[Dict[str, Any]] = field(default_factory=list)
    max_staging_mass: float = 0.0
    facilities: List['PlanetaryFacility'] = field(default_factory=list)
    populations: List['SpeciesPopulation'] = field(default_factory=list)
    id: int = -1  # -1 = unregistered with Galaxy
    image_id: str = ""
    image_rotation: float = 0.0
    radius_hexes: int = 0  # PROJ-139: > 0 = multi-hex object (Dyson Sphere)
    # PROJ-237: Energy
    energy: float = 0.0
    energy_capacity: float = 0.0
    energy_generation: float = 0.0
    atmosphere_target: Dict[str, float] = field(default_factory=dict)
    # Planet modifier targets — None = no modification active
    gravity_target: Optional[float] = None
    gravity_original: Optional[float] = None
    water_target: Optional[float] = None
    radiation_shielding: float = 0.0
    radiation_shielding_target: Optional[float] = None
    # PROJ-238: order queue (unified with Fleet.orders)
    orders: List['Order'] = field(default_factory=list)
    # PROJ-301: planet intrinsic abilities (rolled at galaxy gen).
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)
    # PROJ-284: per-colony per-species sliders (food allocation etc.).
    species_configs: Dict[str, ColonySpeciesConfig] = field(default_factory=dict)
    # PROJ-285: per-turn cache. NOT serialized — populations shift across
    # save load; cache re-warms on the next turn's first read.
    _cached_habitability_multiplier: Optional[float] = field(
        default=None, init=False, repr=False, compare=False,
    )
    _cached_multiplier_turn: int = field(
        default=-1, init=False, repr=False, compare=False,
    )

    def __eq__(self, other):
        if not isinstance(other, Planet):
            return False
        return (self.name == other.name
                and self.location == other.location
                and self.orbit_distance == other.orbit_distance)

    def __hash__(self):
        return hash((self.name, self.location, self.orbit_distance))

    @property
    def active_abilities(self) -> Dict[str, bool]:
        """ability_name -> True for any facility component in 'active' phase.

        PROJ-372 Phase 2: 1-line facade delegating to PlanetQueryService.
        """
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.active_abilities(self)

    def is_ability_active(self, ability_key: str) -> bool:
        """Check if an activatable strategic ability is active on this planet."""
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.is_ability_active(self, ability_key)

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this planet (PROJ-139 IZoneOccupant)."""
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.occupied_hexes(self)

    @property
    def total_pressure_atm(self) -> float:
        total_pa = sum(self.atmosphere.values())
        return total_pa / 101325.0

    @property
    def max_population(self) -> int:
        """Pop capacity from surface area: m^2 / 1e6 * 100 / 1000 = units of 1000 people.
        Earth (~5.1e14 m^2) -> ~51M units (~51B people)."""
        return int(self.surface_area / 1_000_000 * 100 / 1000)

    @property
    def total_population(self) -> int:
        """Total population across all species on this planet."""
        return sum(p.count for p in self.populations)

    @property
    def has_space_shipyard(self) -> bool:
        """True iff any facility is an operational shipyard."""
        return any(facility.is_shipyard for facility in self.facilities)

    def get_cached_habitability_multiplier(self, race_registry, turn: int) -> float:
        """Population-weighted habitability multiplier, cached per turn.

        PROJ-285 cache invariant preserved: cache fields stay on the planet.
        PROJ-372 Phase 2: 1-line facade delegating to the
        ``IHabitabilityCalculator`` registered on ApplicationContext —
        modders inject custom calculators via
        ``set_default_planet_habitability_service``. Falls back to a
        default ``PlanetHabitabilityService`` when none is registered.
        """
        from game.context import get_default_planet_habitability_service
        svc = get_default_planet_habitability_service()
        if svc is None:
            from game.strategy.services.planet_habitability_service import (
                PlanetHabitabilityService,
            )
            svc = PlanetHabitabilityService()
        return svc.get_cached(self, race_registry, turn)

    def get_species_config(self, race_id: str) -> ColonySpeciesConfig:
        """PROJ-284: lazy-create + return per-species config for `race_id`."""
        if race_id not in self.species_configs:
            self.species_configs[race_id] = ColonySpeciesConfig()
        return self.species_configs[race_id]

    @property
    def context_type(self) -> str:
        """BuildContext protocol: returns 'planet'."""
        return "planet"

    # --- IStockpileHolder protocol (PROJ-372) ---

    def add_to_stockpile(self, resource_type: str, amount: float) -> float:
        """Add resources to the local stockpile; return overflow."""
        current = self.stockpile.get(resource_type, 0.0)
        max_cap = self.max_stockpile.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            self.stockpile[resource_type] = max_cap
            return new_total - max_cap
        self.stockpile[resource_type] = new_total
        return 0.0

    def consume_from_stockpile(self, resource_type: str, amount: float) -> bool:
        """All-or-nothing consume. Return True iff sufficient stockpile."""
        current = self.stockpile.get(resource_type, 0.0)
        if current >= amount:
            self.stockpile[resource_type] = current - amount
            return True
        return False

    def has_stockpile(self, costs: dict) -> bool:
        """True iff every resource->amount in `costs` is satisfied."""
        return all(
            self.stockpile.get(rt, 0.0) >= amt for rt, amt in costs.items()
        )

    def get_stockpile(self, resource_type: str) -> float:
        """Current stockpiled amount, 0.0 if absent."""
        return self.stockpile.get(resource_type, 0.0)

    # --- IStagingYardHolder protocol (PROJ-372) ---

    def get_staging_mass(self) -> float:
        """Total mass of items currently in the staging yard."""
        return sum(item.get('mass', 0.0) for item in self.staging_yard)

    def add_to_staging_yard(self, item: Dict[str, Any]) -> bool:
        """Add an item; return False on insufficient capacity."""
        item_mass = item.get('mass', 0.0)
        if self.max_staging_mass > 0 and self.get_staging_mass() + item_mass > self.max_staging_mass:
            return False
        self.staging_yard.append(item)
        return True

    def remove_from_staging_yard(self, index: int) -> Optional[Dict[str, Any]]:
        """Remove and return the item at `index`, or None if out of range."""
        if 0 <= index < len(self.staging_yard):
            return self.staging_yard.pop(index)
        return None

    def can_build_type(self, vehicle_type: str) -> bool:
        """Check if this planet can build the given vehicle type.

        PROJ-372 Phase 2: 1-line facade delegating to PlanetQueryService.
        """
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.can_build_type(self, vehicle_type)

    # --- IOrderable (PROJ-238 — unified with Fleet) ---

    def get_current_order(self) -> Optional['Order']:
        """First order in the queue, or None."""
        return self.orders[0] if self.orders else None

    def pop_order(self) -> Optional['Order']:
        """Pop and return the first order, or None."""
        return self.orders.pop(0) if self.orders else None

    def add_order(self, order: 'Order', index: Optional[int] = None) -> None:
        """Add `order` at `index` (or append if None)."""
        if index is not None:
            self.orders.insert(index, order)
        else:
            self.orders.append(order)

    def clear_orders(self) -> None:
        """Remove all orders from the planet's queue."""
        self.orders.clear()

    def add_production(self, design_id: str, turns: int, vehicle_type: str = "ship") -> None:
        """Add a build item; vehicle_type in {ship, fighter, satellite, complex}."""
        self.construction_queue.append({
            "design_id": design_id,
            "type": vehicle_type,
            "turns_remaining": turns,
        })

    def to_dict(self) -> Dict[str, Any]:
        """Serialize planet to dict for save system. PROJ-372 Phase 2: facade
        delegating to ``planet_serde.planet_to_dict``."""
        from game.strategy.data.planet_serde import planet_to_dict
        return planet_to_dict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Planet':
        """Deserialize planet from save data. PROJ-372 Phase 2: facade
        delegating to ``planet_serde.planet_from_dict_kwargs``."""
        from game.strategy.data.planet_serde import planet_from_dict_kwargs
        return cls(**planet_from_dict_kwargs(data))
