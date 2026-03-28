from typing import TYPE_CHECKING, List

from game.strategy.data.stars import Spectrum
from game.core.hex_math import HexCoord, hex_distance

if TYPE_CHECKING:
    from game.strategy.data.stars import Star
    from game.strategy.data.star_system import StarSystem


# Flux calibration: converts spectrum luminosity units to W/m² flux.
# Spectrum total_output = luminosity in solar units (~1.0 for Sun-like star).
# Blackbody temperature needs W/m². This constant bridges the gap.
# Calibrated so a 1-Lsol star at orbit distance 5 produces ~288K.
FLUX_SCALE = 11500.0

# Radiation falloff exponent. Pure inverse-square would be 2.0.
# Slightly below 2.0 broadens the habitable zone for gameplay balance.
FALLOFF_EXPONENT = 1.95


class SectorEnvironment:
    """
    Represents the environmental conditions of a specific sector (Hex) in a system.
    """

    def __init__(self, local_hex: HexCoord, system: 'StarSystem') -> None:
        self.local_hex: HexCoord = local_hex
        self.system: 'StarSystem' = system

    def calculate_radiation(self) -> Spectrum:
        """
        Calculate total incident radiation from all stars in the system.
        """
        return calculate_incident_radiation(self.local_hex, self.system.stars)

def calculate_incident_radiation(target_local_hex: HexCoord, stars: List['Star']) -> Spectrum:
    """
    Calculate the total incident radiation at a target hex from a list of stars.

    Physics Model:
    - Falloff: FLUX_SCALE / r^1.95 (near inverse-square with slight broadening)
    - FLUX_SCALE bridges spectrum luminosity units to W/m² flux, calibrated so
      a 1-solar-luminosity star at orbit distance 5 produces ~288K blackbody temp.
    - Distance Unit: 1 Hex
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

        # Falloff Factor: FLUX_SCALE / r^1.95
        falloff = FLUX_SCALE / (r ** FALLOFF_EXPONENT)

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
