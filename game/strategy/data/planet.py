from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional
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

    def add_production(self, item_name, turns):
        self.construction_queue.append([item_name, turns])
