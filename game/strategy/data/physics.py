import math
from game.strategy.data.stars import Spectrum
from game.strategy.data.hex_math import HexCoord, hex_distance

class SectorEnvironment:
    """
    Represents the environmental conditions of a specific sector (Hex) in a system.
    """
    def __init__(self, local_hex, system):
        self.local_hex = local_hex # HexCoord (Local)
        self.system = system # StarSystem
        
    def calculate_radiation(self):
        """
        Calculate total incident radiation from all stars in the system.
        """
        return calculate_incident_radiation(self.local_hex, self.system.stars)

def calculate_incident_radiation(target_local_hex, stars):
    """
    Calculate the total incident radiation at a target hex from a list of stars.
    
    Physics Model:
    - Falloff: 1 / r^3 (Inverse Cube Law per user request)
    - Distance Unit: 1 Hex (Orbit of Mercury equivalent)
    - r < 1.0 is clamped to 1.0 to reflect surface/interior intensity maximums.
    """
    
    # Initialize zero spectrum
    total_spec = Spectrum(0,0,0,0,0,0,0,0,0)
    
    for star in stars:
        # Distance calc
        # Star location is local to system center. Target is local to system center.
        dist = hex_distance(star.location, target_local_hex)
        
        # Clamp distance to avoid division by zero or infinite energy
        # Assuming r=1 is the reference "surface" or close orbit intensity.
        r = max(dist, 1.0)
        
        # Falloff Factor (1/r^3)
        falloff = 1.0 / (r ** 3)
        
        # Add contributions
        s = star.spectrum
        total_spec.gamma_ray += s.gamma_ray * falloff
        total_spec.xray += s.xray * falloff
        total_spec.ultraviolet += s.ultraviolet * falloff
        total_spec.blue += s.blue * falloff
        total_spec.green += s.green * falloff
        total_spec.red += s.red * falloff
        total_spec.infrared += s.infrared * falloff
        total_spec.microwave += s.microwave * falloff
        total_spec.radio += s.radio * falloff
        
    return total_spec
