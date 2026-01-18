from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from game.strategy.data.hex_math import HexCoord

# Global Resource Definition
PLANET_RESOURCES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]

class PlanetType(Enum):
    """
    Broad classification of planetary bodies.
    Derived from physical properties.
    """
    GAS_GIANT = auto()
    ICE_GIANT = auto()
    TERRESTRIAL = auto() # Earth-like, Mars-like, Venus-like
    BARREN = auto() # Moon-like, Mercury-like
    ICE_WORLD = auto() # Europa, Pluto
    LAVA = auto() # Hot, molten surface
    ASTEROID = auto() # Small bodies

@dataclass
class PlanetaryFacility:
    """Represents a built complex on a planet."""
    instance_id: str          # Unique ID (uuid)
    design_id: str            # Reference to design file
    name: str                 # Facility name
    design_data: Dict[str, Any]  # Full complex design (from JSON)
    is_operational: bool = True

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

    # Unique identifier assigned by Galaxy registry (default -1 means unregistered)
    id: int = -1


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
    def has_space_shipyard(self) -> bool:
        """Check if planet has operational space shipyard."""
        for facility in self.facilities:
            if not facility.is_operational:
                continue
            # Check design_data for SpaceShipyard component
            for layer_data in facility.design_data.get("layers", {}).values():
                for comp in layer_data.get("components", []):
                    if "SpaceShipyard" in comp.get("abilities", {}):
                        return True
        return False

    def add_production(self, item_name, turns=None, vehicle_type=None):
        """Add item to construction queue.

        Supports two formats:
        - Legacy: add_production("Colony Ship", 5) -> ["Colony Ship", 5]
        - New: add_production("design_id", turns=5, vehicle_type="complex") -> dict
        """
        if vehicle_type is not None:
            # New dict format
            queue_item = {
                "design_id": item_name,
                "type": vehicle_type,
                "turns_remaining": turns
            }
            self.construction_queue.append(queue_item)
        else:
            # Legacy list format
            self.construction_queue.append([item_name, turns])

    def to_dict(self) -> dict:
        """
        Serialize planet to dict for save system.

        Returns:
            Dict with all planet data
        """
        from game.strategy.data.hex_math import hex_to_dict

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
                    'is_operational': f.is_operational
                } for f in self.facilities
            ]
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
        from game.strategy.data.hex_math import hex_from_dict

        location = hex_from_dict(data['location'])
        planet_type = PlanetType[data['planet_type']]

        facilities = [
            PlanetaryFacility(
                instance_id=f['instance_id'],
                design_id=f['design_id'],
                name=f['name'],
                design_data=f['design_data'],
                is_operational=f.get('is_operational', True)
            ) for f in data.get('facilities', [])
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
            id=data.get('id', -1)
        )
