"""
Planet data class.

PlanetaryFacility and SpeciesPopulation extracted to own modules (PROJ-210).
"""

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Any
from typing import TYPE_CHECKING as _TC, Any
from game.core.hex_math import HexCoord, hex_circle_filled
from game.core.validation_helpers import (
    require_keys, validate_enum, validate_positive, validate_non_negative
)

if _TC:
    from game.strategy.data.order_types import Order

# PROJ-210: Import extracted classes for backward compatibility
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.species_population import SpeciesPopulation
# PROJ-284: per-colony per-species config (food allocation slider, etc.)
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
    """
    Represents a planetary body (Planet or Moon).
    Physical properties are grounded in real physics units (SI).
    """
    # Required fields (no defaults)
    name: str
    location: HexCoord # Local system coordinates
    orbit_distance: int # Ring number
    
    # Physical Properties
    mass: float # kg
    radius: float # meters
    surface_area: float # m^2
    density: float # kg/m^3
    surface_gravity: float # m/s^2 (also stored as g's for convenience if needed, but easy to calc)
    
    # Surface Conditions
    surface_pressure: float # Pascals (1 ATM = 101325 Pa)
    surface_temperature: float # Kelvin
    surface_water: float # 0.0 to 1.0 (Percentage of surface covered)
    
    # Internal Properties
    tectonic_activity: float # 0.0 (Dead) to 1.0 (Volcanic Hell)
    magnetic_field: float # Relative to Earth (0.0 to X.0)
    
    # Fields with defaults (must come after non-default fields)
    # Atmosphere: Gas Name -> Partial Pressure (Pa) or Percentage? 
    # Plan said "Percentage/Pressure". Let's store Partial Pressure in Pa for simulation accuracy.
    # Total pressure is sum of these.
    atmosphere: Dict[str, float] = field(default_factory=dict)
    
    # Classification
    planet_type: PlanetType = PlanetType.BARREN
    
    # Hierarchy / Render
    # Parent star is implicit system primary generally, but could be specific star in binary.
    # We will just assume system center for now as per hex logic.
    orbit_parent_name: Optional[str] = None # Name of Star or "Planet I" if strictly modeling hierarchy later, but for now mostly for flavor.
    
    # Empire
    owner_id: Optional[int] = None
    construction_queue: list = field(default_factory=list)

    # Mineral deposits
    # Key: Resource ID (planetary resource from ResourceCatalog) -> {'quantity': int, 'quality': float}
    deposits: Dict[str, dict] = field(default_factory=dict)

    # Local resource stockpile (harvested/stored resources available for construction)
    stockpile: Dict[str, float] = field(default_factory=dict)
    max_stockpile: Dict[str, float] = field(default_factory=dict)

    # Staging Yard: planet-side storage for constructed items (fighters, drop pods)
    staging_yard: List[Dict[str, Any]] = field(default_factory=list)
    max_staging_mass: float = 0.0

    # Planetary Facilities (built complexes)
    facilities: List['PlanetaryFacility'] = field(default_factory=list)

    # Multi-species population tracking
    populations: List['SpeciesPopulation'] = field(default_factory=list)

    # Unique identifier assigned by Galaxy registry (default -1 means unregistered)
    id: int = -1

    # Visual representation (assigned during generation, persisted in saves)
    image_id: str = ""  # Filename from Planets_V3 (e.g., "planet_5_994_1769750020702.png")
    image_rotation: float = 0.0  # Degrees (0.0 to 360.0) for visual variety

    # Multi-hex zone support (PROJ-139)
    # radius_hexes > 0 indicates this is a multi-hex object (e.g., Dyson Sphere)
    radius_hexes: int = 0

    # Energy system (PROJ-237)
    energy: float = 0.0              # Current energy level
    energy_capacity: float = 0.0     # Max (recalculated from batteries each tick)
    energy_generation: float = 0.0   # Rate (recalculated from generators each tick)

    # Atmosphere modification target (gas formula -> target Pa)
    atmosphere_target: Dict[str, float] = field(default_factory=dict)

    # Planet modifier targets (gravity, water, radiation)
    gravity_target: Optional[float] = None       # Target gravity m/s² (None = no modification)
    gravity_original: Optional[float] = None     # Original gravity before modifier (None = unmodified)
    water_target: Optional[float] = None         # Target water level 0.0-1.0 (None = no modification)
    radiation_shielding: float = 0.0             # Active artificial radiation shielding
    radiation_shielding_target: Optional[float] = None  # Target shielding (None = no modification)

    # Order queue (PROJ-238: renamed from planet_orders, unified with Fleet.orders)
    orders: List['Order'] = field(default_factory=list)

    # PROJ-284: Per-colony per-species sliders (food allocation, etc.).
    # Keyed by race_id. Lazy-created via `get_species_config(race_id)`.
    species_configs: Dict[str, ColonySpeciesConfig] = field(default_factory=dict)

    # PROJ-285: Per-turn cache of the population-weighted habitability
    # multiplier. Populated on first read each turn via
    # `get_cached_habitability_multiplier` and reused for subsequent
    # harvest / production lookups within the same turn. NOT serialized
    # — populations may have shifted by the time a save loads, and the
    # cache re-warms on the next turn's first read anyway.
    _cached_habitability_multiplier: Optional[float] = field(
        default=None, init=False, repr=False, compare=False,
    )
    _cached_multiplier_turn: int = field(
        default=-1, init=False, repr=False, compare=False,
    )

    def __eq__(self, other):
        if not isinstance(other, Planet):
            return False
        # Compare identity-defining properties only
        # Name and Location (System-Local) should be unique enough for game logic
        # OR better: Name + Location + OrbitDistance?
        return (self.name == other.name and 
                self.location == other.location and
                self.orbit_distance == other.orbit_distance)

    def __hash__(self):
        return hash((self.name, self.location, self.orbit_distance))

    @property
    def active_abilities(self) -> Dict[str, bool]:
        """Derived summary: ability_name -> True if ANY component with that ability is ACTIVE.

        Scans all facility component_states for ACTIVE phase entries.
        This is the single source of truth — no separate stored field.
        """
        result: Dict[str, bool] = {}
        for facility in self.facilities:
            for _key, state_data in facility.component_states.items():
                if isinstance(state_data, dict) and state_data.get('phase') == 'active':
                    ability_name = state_data.get('ability_name', '')
                    if ability_name:
                        result[ability_name] = True
        return result

    def is_ability_active(self, ability_key: str) -> bool:
        """Check if an activatable strategic ability is active on this planet."""
        return self.active_abilities.get(ability_key, False)

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this planet (PROJ-139 IZoneOccupant).

        For normal planets (radius_hexes <= 0), returns just the planet's location.
        For multi-hex objects like Dyson Spheres (radius_hexes > 0), returns
        all hexes in the zone based on the radius.

        Returns:
            FrozenSet of HexCoord in LOCAL system coordinates
        """
        if self.radius_hexes > 0:
            return hex_circle_filled(self.location, max(0, self.radius_hexes - 1))
        return frozenset({self.location})

    @property
    def total_pressure_atm(self) -> float:
        total_pa = sum(self.atmosphere.values())
        return total_pa / 101325.0

    @property
    def max_population(self) -> int:
        """
        Maximum population capacity based on surface area.

        Formula: surface_area_m2 / 1_000_000 * 100 / 1000
        - Convert m² to km² (divide by 1e6)
        - Apply 100 pop per km² density
        - Convert to units of 1000 people

        Earth (~5.1e14 m²) → ~51 million units → ~51 billion people capacity.
        """
        return int(self.surface_area / 1_000_000 * 100 / 1000)

    @property
    def total_population(self) -> int:
        """Total population across all species on this planet."""
        return sum(p.count for p in self.populations)

    @property
    def has_space_shipyard(self) -> bool:
        """Check if planet has operational space shipyard."""
        return any(facility.is_shipyard for facility in self.facilities)

    def get_cached_habitability_multiplier(self, race_registry, turn: int) -> float:
        """Return the population-weighted habitability multiplier, cached per turn.

        PROJ-285: Populations change only at turn boundaries (population
        growth runs once per turn after the 100-tick loop), so one
        computation per turn is enough — all 100 harvest / production
        ticks within the same turn reuse the cached value.

        Args:
            race_registry: Object implementing `get_race(race_id) -> Optional[RaceConfig]`.
            turn: Current strategic turn number. Cache keys on this —
                a different turn forces a recompute.

        Returns:
            Float in [0, 1]. Uncolonized / degenerate cases return 1.0.
        """
        if self._cached_multiplier_turn != turn:
            # Late import avoids circular: planet.py ← colony_output.py
            # ← habitability.py ← (no planet dependency).
            from game.strategy.formulas.colony_output import planet_habitability_multiplier
            self._cached_habitability_multiplier = planet_habitability_multiplier(
                self, race_registry,
            )
            self._cached_multiplier_turn = turn
        return self._cached_habitability_multiplier

    def get_species_config(self, race_id: str) -> ColonySpeciesConfig:
        """Return the per-species config for `race_id` on this colony.

        PROJ-284: lazy-creates and stores a default `ColonySpeciesConfig`
        if one doesn't exist for this race yet — callers can read or mutate
        the returned object without checking for absence first.
        """
        if race_id not in self.species_configs:
            self.species_configs[race_id] = ColonySpeciesConfig()
        return self.species_configs[race_id]

    @property
    def context_type(self) -> str:
        """Return 'planet' for BuildContext protocol compliance."""
        return "planet"

    # --- Local Stockpile Methods ---

    def add_to_stockpile(self, resource_type: str, amount: float) -> float:
        """Add resources to the local stockpile.

        Args:
            resource_type: Resource identifier (e.g. "metals", "fuel").
            amount: Amount to add.

        Returns:
            Overflow amount (0.0 if all fit within storage).
        """
        current = self.stockpile.get(resource_type, 0.0)
        max_cap = self.max_stockpile.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            self.stockpile[resource_type] = max_cap
            return new_total - max_cap
        self.stockpile[resource_type] = new_total
        return 0.0

    def consume_from_stockpile(self, resource_type: str, amount: float) -> bool:
        """Consume resources from the local stockpile (all-or-nothing).

        Args:
            resource_type: Resource identifier.
            amount: Amount to consume.

        Returns:
            True if successful, False if insufficient (no deduction made).
        """
        current = self.stockpile.get(resource_type, 0.0)
        if current >= amount:
            self.stockpile[resource_type] = current - amount
            return True
        return False

    def has_stockpile(self, costs: dict) -> bool:
        """Check if the planet has all required resources in stockpile.

        Args:
            costs: Dict mapping resource_type -> required amount.

        Returns:
            True if all resources are available.
        """
        for resource_type, amount in costs.items():
            if self.stockpile.get(resource_type, 0.0) < amount:
                return False
        return True

    def get_stockpile(self, resource_type: str) -> float:
        """Get current amount of a resource in the local stockpile.

        Returns 0.0 if the resource type is not in the stockpile.
        """
        return self.stockpile.get(resource_type, 0.0)

    # --- Staging Yard Methods ---

    def get_staging_mass(self) -> float:
        """Get total mass of items currently in the staging yard."""
        return sum(item.get('mass', 0.0) for item in self.staging_yard)

    def add_to_staging_yard(self, item: Dict[str, Any]) -> bool:
        """Add a constructed item to the staging yard.

        Args:
            item: Dict with at minimum 'design_id', 'design_data', 'mass', 'vehicle_type', 'name'.

        Returns:
            True if added, False if insufficient capacity.
        """
        item_mass = item.get('mass', 0.0)
        if self.max_staging_mass > 0 and self.get_staging_mass() + item_mass > self.max_staging_mass:
            return False
        self.staging_yard.append(item)
        return True

    def remove_from_staging_yard(self, index: int) -> Optional[Dict[str, Any]]:
        """Remove an item from the staging yard by index.

        Returns:
            The removed item, or None if index out of range.
        """
        if 0 <= index < len(self.staging_yard):
            return self.staging_yard.pop(index)
        return None

    def can_build_type(self, vehicle_type: str) -> bool:
        """
        Check if this planet can build the given vehicle type.

        Args:
            vehicle_type: Type of vehicle ("ship", "fighter", "satellite", "complex")

        Returns:
            True if this planet can build the given type.
        """
        vehicle_lower = vehicle_type.lower()

        # Complexes can always be built on planets
        if vehicle_lower == "complex":
            return True

        # Ships, fighters, and satellites require a space shipyard
        if vehicle_lower in ("ship", "fighter", "satellite"):
            return self.has_space_shipyard

        return False

    # --- Order Management (PROJ-238: unified with Fleet pattern, IOrderable) ---

    def get_current_order(self) -> Optional['Order']:
        """Get the first order in the planet's order queue."""
        return self.orders[0] if self.orders else None

    def pop_order(self) -> Optional['Order']:
        """Remove and return the first order from the queue."""
        return self.orders.pop(0) if self.orders else None

    def add_order(self, order: 'Order', index: Optional[int] = None) -> None:
        """Add an order to the planet's queue.

        Args:
            order: Order to add.
            index: Optional insertion index. None = append to end.
        """
        if index is not None:
            self.orders.insert(index, order)
        else:
            self.orders.append(order)

    def clear_orders(self) -> None:
        """Remove all orders from the planet's queue."""
        self.orders.clear()

    def add_production(self, design_id: str, turns: int, vehicle_type: str = "ship") -> None:
        """Add item to construction queue.

        Args:
            design_id: The design identifier
            turns: Number of turns to complete
            vehicle_type: "ship", "fighter", "satellite", or "complex" (default: "ship")
        """
        queue_item = {
            "design_id": design_id,
            "type": vehicle_type,
            "turns_remaining": turns
        }
        self.construction_queue.append(queue_item)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize planet to dict for save system.

        Returns:
            Dict with all planet data
        """
        from game.core.hex_math import hex_to_dict

        return {
            'id': self.id,
            'name': self.name,
            'location': hex_to_dict(self.location),
            'orbit_distance': self.orbit_distance,
            'mass': self.mass,
            'radius': self.radius,
            'surface_area': self.surface_area,
            'density': self.density,
            'surface_gravity': self.surface_gravity,
            'surface_pressure': self.surface_pressure,
            'surface_temperature': self.surface_temperature,
            'surface_water': self.surface_water,
            'tectonic_activity': self.tectonic_activity,
            'magnetic_field': self.magnetic_field,
            'atmosphere': self.atmosphere.copy(),
            'planet_type': self.planet_type.name,
            'orbit_parent_name': self.orbit_parent_name,
            'owner_id': self.owner_id,
            'construction_queue': self.construction_queue.copy(),
            'deposits': {k: v.copy() for k, v in self.deposits.items()},
            'stockpile': dict(self.stockpile),
            'max_stockpile': dict(self.max_stockpile),
            'staging_yard': list(self.staging_yard),
            'max_staging_mass': self.max_staging_mass,
            'facilities': [
                f.to_dict() for f in self.facilities
            ],
            'populations': [
                {
                    'race_id': p.race_id,
                    'count': p.count,
                    'happiness': p.happiness
                } for p in self.populations
            ],
            'image_id': self.image_id,
            'image_rotation': self.image_rotation,
            'radius_hexes': self.radius_hexes,
            # PROJ-237: Energy, shield, and planet orders
            'energy': self.energy,
            'energy_capacity': self.energy_capacity,
            'energy_generation': self.energy_generation,
            'atmosphere_target': dict(self.atmosphere_target),
            # Planet modifier targets
            'gravity_target': self.gravity_target,
            'gravity_original': self.gravity_original,
            'water_target': self.water_target,
            'radiation_shielding': self.radiation_shielding,
            'radiation_shielding_target': self.radiation_shielding_target,
            'orders': [o.to_dict() for o in self.orders],
            # PROJ-284: per-colony per-species sliders. `last_food_ratio` is
            # transient and not emitted by ColonySpeciesConfig.to_dict().
            'species_configs': {
                race_id: cfg.to_dict()
                for race_id, cfg in self.species_configs.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Planet':
        """
        Deserialize planet from dict.

        Args:
            data: Dict with planet data

        Returns:
            Reconstructed Planet instance

        Raises:
            PersistenceException: If required keys missing or values invalid
        """
        from game.core.hex_math import hex_from_dict
        from game.core.exceptions import PersistenceException
        from game.core.error_codes import ErrorCode

        # Validate required keys
        require_keys(data, [
            'name', 'location', 'orbit_distance', 'mass', 'radius', 'surface_area',
            'density', 'surface_gravity', 'surface_pressure', 'surface_temperature',
            'surface_water', 'tectonic_activity', 'magnetic_field', 'planet_type'
        ], 'Planet')

        # Validate enum
        planet_type = validate_enum(data['planet_type'], PlanetType, 'planet_type', 'Planet')

        # Validate positive values
        validate_positive(data['mass'], 'mass', 'Planet')
        validate_positive(data['radius'], 'radius', 'Planet')
        validate_positive(data['surface_area'], 'surface_area', 'Planet')
        validate_positive(data['density'], 'density', 'Planet')
        validate_positive(data['surface_gravity'], 'surface_gravity', 'Planet')

        # Validate non-negative values
        validate_non_negative(data['orbit_distance'], 'orbit_distance', 'Planet')
        validate_non_negative(data['surface_pressure'], 'surface_pressure', 'Planet')
        validate_non_negative(data['surface_water'], 'surface_water', 'Planet')

        # Validate location with context
        try:
            location = hex_from_dict(data['location'])
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"Planet: invalid location data - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "Planet",
                    "field": "location",
                    "error_type": type(e).__name__,
                    "error": str(e),
                }
            ) from e

        # PROJ-251: strict=True — corrupt entries fail the load
        from game.core.json_utils import deserialize_list
        parent_name = f"Planet '{data['name']}'"

        facilities = deserialize_list(
            data.get('facilities', []), PlanetaryFacility.from_dict, 'facility', parent_name, strict=True
        )

        populations = deserialize_list(
            data.get('populations', []), SpeciesPopulation.from_dict, 'population', parent_name, strict=True
        )

        return cls(
            name=data['name'],
            location=location,
            orbit_distance=data['orbit_distance'],
            mass=data['mass'],
            radius=data['radius'],
            surface_area=data['surface_area'],
            density=data['density'],
            surface_gravity=data['surface_gravity'],
            surface_pressure=data['surface_pressure'],
            surface_temperature=data['surface_temperature'],
            surface_water=data['surface_water'],
            tectonic_activity=data['tectonic_activity'],
            magnetic_field=data['magnetic_field'],
            atmosphere=data.get('atmosphere', {}),
            planet_type=planet_type,
            orbit_parent_name=data.get('orbit_parent_name'),
            owner_id=data.get('owner_id'),
            construction_queue=data.get('construction_queue', []),
            deposits=data.get('deposits', data.get('resources', {})),
            stockpile=data.get('stockpile', {}),
            max_stockpile=data.get('max_stockpile', {}),
            staging_yard=data.get('staging_yard', []),
            max_staging_mass=data.get('max_staging_mass', 0.0),
            facilities=facilities,
            populations=populations,
            id=data.get('id', -1),
            image_id=data.get('image_id', ''),
            image_rotation=data.get('image_rotation', 0.0),
            radius_hexes=data.get('radius_hexes', 0),
            # PROJ-237: Energy, shield, and planet orders (safe defaults for old saves)
            energy=data.get('energy', 0.0),
            energy_capacity=data.get('energy_capacity', 0.0),
            energy_generation=data.get('energy_generation', 0.0),
            atmosphere_target=data.get('atmosphere_target', {}),
            # Planet modifier targets (safe defaults for old saves)
            gravity_target=data.get('gravity_target'),
            gravity_original=data.get('gravity_original'),
            water_target=data.get('water_target'),
            radiation_shielding=data.get('radiation_shielding', 0.0),
            radiation_shielding_target=data.get('radiation_shielding_target'),
            orders=_deserialize_planet_orders(data.get('orders', data.get('planet_orders', []))),
            # PROJ-284: per-colony per-species sliders. Old saves without
            # the key load with an empty dict; configs lazy-create on
            # first read via `get_species_config(race_id)`.
            species_configs={
                race_id: ColonySpeciesConfig.from_dict(cfg_data)
                for race_id, cfg_data in (data.get('species_configs') or {}).items()
            },
        )


def _deserialize_planet_orders(orders_data: list) -> list:
    """Deserialize planet orders from save data.

    Args:
        orders_data: List of order dicts from save data.

    Returns:
        List of Order instances. Silently skips invalid entries.
    """
    from game.strategy.data.order_types import Order as _Order
    result = []
    for item in orders_data:
        try:
            result.append(_Order.from_dict(item))
        except (KeyError, TypeError, ValueError):
            pass  # Skip malformed orders
    return result
