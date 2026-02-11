from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from game.core.constants import ResourceType
from game.core.hex_math import HexCoord

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
class PlanetaryFacility:
    """Represents a built complex on a planet."""
    instance_id: str          # Unique ID (uuid)
    design_id: str            # Reference to design file
    name: str                 # Facility name
    design_data: Dict[str, Any]  # Full complex design (from JSON)
    is_operational: bool = True
    construction_queue: List[Dict[str, Any]] = field(default_factory=list)
    resource_levels: Dict[str, float] = field(default_factory=dict)

    def get_fuel_storage(self) -> float:
        """Get current fuel level in this facility."""
        return self.resource_levels.get(ResourceType.FUEL, 0.0)

    def get_max_fuel_storage(self, registries) -> float:
        """Calculate max fuel capacity from design_data components.

        Scans all components in the facility's design_data for ResourceStorage
        abilities with resource type 'fuel' and sums their amounts.

        Args:
            registries: GameRegistries with component definitions.

        Returns:
            Total fuel storage capacity.
        """
        total = 0.0
        for layer_data in self.design_data.get("layers", {}).values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                comp_id = comp.get("id") if isinstance(comp, dict) else comp
                comp_def = registries.components.get(comp_id)
                if not comp_def:
                    continue
                abilities = getattr(comp_def, 'abilities', {}) or {}
                for storage in (abilities.get('ResourceStorage') or []):
                    if isinstance(storage, dict) and storage.get('resource') == ResourceType.FUEL:
                        total += storage.get('amount', 0)
        return total

    def add_fuel(self, amount: float, registries) -> float:
        """Add fuel up to max capacity.

        Args:
            amount: Amount of fuel to add.
            registries: GameRegistries for max capacity lookup.

        Returns:
            Overflow amount that could not be stored.
        """
        max_storage = self.get_max_fuel_storage(registries)
        current = self.get_fuel_storage()
        space = max_storage - current
        added = min(amount, space)
        self.resource_levels[ResourceType.FUEL] = current + added
        return amount - added

    def withdraw_fuel(self, amount: float) -> float:
        """Withdraw fuel from this facility.

        Args:
            amount: Amount of fuel to withdraw.

        Returns:
            Actual amount withdrawn (may be less than requested).
        """
        current = self.get_fuel_storage()
        withdrawn = min(amount, current)
        self.resource_levels[ResourceType.FUEL] = current - withdrawn
        return withdrawn


@dataclass
class SpeciesPopulation:
    """
    Represents a population of a single species on a planet.

    Population is tracked in units of 1,000 people for manageable numbers.
    Happiness affects growth rate and productivity.
    """
    race_id: str  # References RaceConfig.race_id
    count: int = 0  # Population units (1 unit = 1,000 people)
    happiness: float = 0.5  # 0.0 (miserable) to 1.0 (ecstatic)


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

    # Resources
    # Key: Resource Name (from PLANET_RESOURCES) -> {'quantity': int, 'quality': float}
    resources: Dict[str, dict] = field(default_factory=dict)

    # Planetary Facilities (built complexes)
    facilities: List['PlanetaryFacility'] = field(default_factory=list)

    # Multi-species population tracking
    populations: List['SpeciesPopulation'] = field(default_factory=list)

    # Unique identifier assigned by Galaxy registry (default -1 means unregistered)
    id: int = -1

    # Visual representation (assigned during generation, persisted in saves)
    image_id: str = ""  # Filename from Planets_V3 (e.g., "planet_5_994_1769750020702.png")
    image_rotation: float = 0.0  # Degrees (0.0 to 360.0) for visual variety


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
        for facility in self.facilities:
            if not facility.is_operational:
                continue
            # Check design_data for space_shipyard component
            # Design JSON uses direct list format: layers[layer_name] = [comp1, comp2, ...]
            for layer_data in facility.design_data.get("layers", {}).values():
                if not isinstance(layer_data, list):
                    continue
                for comp in layer_data:
                    if isinstance(comp, dict):
                        # Check component id (real saved designs)
                        if comp.get("id") == "space_shipyard":
                            return True
                        # Check abilities dict (test fixtures)
                        if "SpaceShipyard" in comp.get("abilities", {}):
                            return True
        return False

    @property
    def context_type(self) -> str:
        """Return 'planet' for BuildContext protocol compliance."""
        return "planet"

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

    def add_production(self, design_id: str, turns: int, vehicle_type: str = "ship"):
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

    def to_dict(self) -> dict:
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
            'resources': {k: v.copy() for k, v in self.resources.items()},
            'facilities': [
                {
                    'instance_id': f.instance_id,
                    'design_id': f.design_id,
                    'name': f.name,
                    'design_data': f.design_data,
                    'is_operational': f.is_operational,
                    'construction_queue': list(f.construction_queue),
                    'resource_levels': f.resource_levels.copy()
                } for f in self.facilities
            ],
            'populations': [
                {
                    'race_id': p.race_id,
                    'count': p.count,
                    'happiness': p.happiness
                } for p in self.populations
            ],
            'image_id': self.image_id,
            'image_rotation': self.image_rotation
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Planet':
        """
        Deserialize planet from dict.

        Args:
            data: Dict with planet data

        Returns:
            Reconstructed Planet instance
        """
        from game.core.hex_math import hex_from_dict

        location = hex_from_dict(data['location'])
        planet_type = PlanetType[data['planet_type']]

        facilities = [
            PlanetaryFacility(
                instance_id=f['instance_id'],
                design_id=f['design_id'],
                name=f['name'],
                design_data=f['design_data'],
                is_operational=f.get('is_operational', True),
                construction_queue=f.get('construction_queue', []),
                resource_levels=f.get('resource_levels', {})
            ) for f in data.get('facilities', [])
        ]

        # Deserialize populations (default empty for backward compat)
        populations = [
            SpeciesPopulation(
                race_id=p['race_id'],
                count=p['count'],
                happiness=p.get('happiness', 0.5)
            ) for p in data.get('populations', [])
        ]

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
            resources=data.get('resources', {}),
            facilities=facilities,
            populations=populations,
            id=data.get('id', -1),
            image_id=data.get('image_id', ''),
            image_rotation=data.get('image_rotation', 0.0)
        )
