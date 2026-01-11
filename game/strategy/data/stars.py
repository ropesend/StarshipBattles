
import random
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from game.strategy.data.hex_math import HexCoord, hex_ring

# Constants
SOLAR_MASS_KG = 1.989e30
SOLAR_RADIUS_M = 6.957e8
SOLAR_LUMINOSITY_W = 3.828e26
SOLAR_TEMP_K = 5778

class StarType(Enum):
    MAIN_SEQUENCE = auto()
    RED_GIANT = auto()
    BLUE_GIANT = auto()
    WHITE_DWARF = auto()
    RED_DWARF = auto()
    NEUTRON_STAR = auto()
    BLACK_HOLE = auto()
    BROWN_DWARF = auto()

@dataclass
class Spectrum:
    """
    Represents the electromagnetic spectrum intensity of a star.
    Values are relative to a standard Sol-like baseline or absolute flux W/m^2 (simplified).
    """
    gamma_ray: float            # < 10 pm
    xray: float                 # 10 pm - 10 nm
    ultraviolet: float          # 10 nm - 400 nm
    blue: float                 # 400 nm - 500 nm (Visible)
    green: float                # 500 nm - 600 nm (Visible)
    red: float                  # 600 nm - 700 nm (Visible)
    infrared: float             # 700 nm - 1 mm
    microwave: float            # 1 mm - 1 m
    radio: float                # > 1 m

    def get_total_output(self):
        return (self.gamma_ray + self.xray + self.ultraviolet + 
                self.blue + self.green + self.red + 
                self.infrared + self.microwave + self.radio)

@dataclass
class Star:
    name: str
    mass: float  # Solar Masses
    diameter_hexes: float # Diameter in Hexes
    temperature: float # Kelvin
    luminosity: float # Solar Luminosity
    spectrum: Spectrum
    star_type: StarType
    color: tuple # (R, G, B)
    age: float # Years
    
    # Location relative to system center (0,0,0)
    location: HexCoord = field(default_factory=lambda: HexCoord(0, 0))

class StarGenerator:
    def __init__(self):
        pass

    def _generate_mass(self, is_primary=True, primary_mass=None):
        """
        Generates mass using a log-normal distribution.
        If not primary, ensures mass < primary_mass.
        """
        # Log-normal distribution centered around 1.0 (log(1)=0)
        # Sigma controls the spread. Sigma=1.0 gives a long tail.
        
        while True:
            # Shifted log-normal to allow for smaller stars
            mass = random.lognormvariate(0, 0.8)
            
            # Constraints
            if mass < 0.1: continue
            if mass > 100.0: continue
            
            if not is_primary and primary_mass is not None:
                if mass >= primary_mass:
                    continue # Retry
            
            return mass

    def _determine_type_and_radius(self, mass, age_ratio=0.5):
        """
        Determine type and radius based on mass and random evolution factor.
        Returns (StarType, Radius_Solar, Temperature_K, Luminosity_Solar, Color)
        Simplified astrophysics model.
        """
        # Mass-Luminosity Relation (Approximation for Main Sequence)
        # L ~ M^3.5
        luminosity = mass ** 3.5
        
        # Stefan-Boltzmann Law: L = 4 * PI * R^2 * Sigma * T^4
        # We need to determine T or R to find the other.
        # Main Sequence Relation: R ~ M^0.8 (approx)
        radius = mass ** 0.8
        
        # Calculate T from L and R
        # (L/L_sol) = (R/R_sol)^2 * (T/T_sol)^4
        # T/T_sol = ((L/L_sol) / (R/R_sol)^2)^(1/4)
        t_ratio = (luminosity / (radius ** 2)) ** 0.25
        temperature = t_ratio * SOLAR_TEMP_K
        
        star_type = StarType.MAIN_SEQUENCE
        color = self._kelvin_to_rgb(temperature)

        # Evolution / Giants Logic (Random chance based on mass)
        # High mass stars evolve faster.
        evolution_roll = random.random()
        
        if mass > 8 and evolution_roll > 0.9:
            # Blue Giant or Supergiant
            star_type = StarType.BLUE_GIANT
            radius *= random.uniform(5, 20) # Significantly larger
            luminosity *= random.uniform(1.5, 5.0) # Brighter
            # Temp stays high or cools slightly? Blue Giants are hot.
            temperature = max(10000, temperature * 0.8) 
            
        elif mass > 0.8 and evolution_roll > 0.85:
            # Red Giant phase
            star_type = StarType.RED_GIANT
            radius *= random.uniform(10, 100) # Huge expansion
            temperature = random.uniform(3000, 4500) # Cool down
            # Luminosity increases due to size: L ~ R^2 * T^4
            luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)
            color = (255, 60, 60)

        elif mass < 0.5:
             star_type = StarType.RED_DWARF
             color = (255, 100, 100)
             
        elif mass > 1.4 and evolution_roll > 0.98:
            # Remnants (Rare)
            roll = random.random()
            if roll > 0.8 and mass > 20: 
                star_type = StarType.BLACK_HOLE
                radius = 0.0001 # Tiny
                luminosity = 0.001 # Accretion disk?
                temperature = 0 # Event horizon
                color = (20, 0, 40)
            elif roll > 0.5 and mass > 8:
                star_type = StarType.NEUTRON_STAR
                radius = 0.00002 # Tiny
                luminosity = 0.01 
                temperature = 1000000 
                color = (200, 200, 255)
            else:
                 star_type = StarType.WHITE_DWARF
                 radius = 0.01 # Earth size
                 temperature = random.uniform(8000, 40000)
                 color = (220, 220, 255)
                 luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)

        return star_type, radius, temperature, luminosity, color

    def _kelvin_to_rgb(self, temp):
        """Approximate RGB from Kelvin."""
        temp = temp / 100
        
        # Red
        if temp <= 66:
            r = 255
        else:
            r = temp - 60
            r = 329.698727446 * (r ** -0.1332047592)
            if r < 0: r = 0
            if r > 255: r = 255
            
        # Green
        if temp <= 66:
            g = temp
            g = 99.4708025861 * math.log(g) - 161.1195681661
            if g < 0: g = 0
            if g > 255: g = 255
        else:
            g = temp - 60
            g = 288.1221695283 * (g ** -0.0755148492)
            if g < 0: g = 0
            if g > 255: g = 255
            
        # Blue
        if temp >= 66:
            b = 255
        else:
            if temp <= 19:
                b = 0
            else:
                b = temp - 10
                b = 138.5177312231 * math.log(b) - 305.0447927307
                if b < 0: b = 0
                if b > 255: b = 255
                
        return (int(r), int(g), int(b))

    def _map_radius_to_hexes(self, radius_sol, star_type):
        """
        Map solar radius to hex diameter (1-11).
        Small/Med stars -> 1-3 Hexes.
        Giants -> Scale up to 11.
        """
        if star_type in (StarType.NEUTRON_STAR, StarType.BLACK_HOLE, StarType.WHITE_DWARF):
             return 0.5 # Sub-hex visual
        
        if radius_sol < 0.8: return 1.0
        if radius_sol < 2.0: return 2.0 # Slightly larger
        if radius_sol < 5.0: return 3.0
        
        import  math
        log_r = math.log10(radius_sol)
        hex_diam = 3.46 * log_r + 0.61
        hex_diam = min(11.0, max(1.0, hex_diam))
        
        return float(int(hex_diam)) if hex_diam > 3 else hex_diam

    def _generate_spectrum(self, temp, luminosity):
        """
        Generate spectrum based on Black Body radiation logic.
        Refined to 9 bands including 3 visible split bands.
        """
        b = 2.898e-3
        peak_wavelength = b / temp if temp > 0 else 1e99
        
        def intensity_at(target_wl):
             if peak_wavelength <= 0: return 0
             # Log-space distance for distribution width
             dist = math.log10(target_wl) - math.log10(peak_wavelength)
             sigma = 0.5 # Tighter peaks for better differentiation
             # Planck's law is asymmetrical, but log-gaussian is a usable approx for games
             return math.exp(-(dist**2) / (2*sigma**2))

        # Representative Wavelengths (Meters)
        wl_gamma = 1e-12    # Gamma
        wl_xray = 1e-9      # X-Ray
        wl_uv = 1e-7        # UV
        wl_blue = 4.5e-7    # Blue (450nm)
        wl_green = 5.5e-7   # Green (550nm)
        wl_red = 6.5e-7     # Red (650nm)
        wl_ir = 1e-5        # Infrared
        wl_micro = 1e-2     # Microwave
        wl_radio = 10       # Radio
        
        s_gamma = intensity_at(wl_gamma)
        s_xray = intensity_at(wl_xray)
        s_uv = intensity_at(wl_uv)
        s_blue = intensity_at(wl_blue)
        s_green = intensity_at(wl_green)
        s_red = intensity_at(wl_red)
        s_ir = intensity_at(wl_ir)
        s_micro = intensity_at(wl_micro)
        s_radio = intensity_at(wl_radio)
        
        total = (s_gamma + s_xray + s_uv + 
                 s_blue + s_green + s_red + 
                 s_ir + s_micro + s_radio)
                 
        scale = luminosity / total if total > 0 else 0
        
        def jitter(val):
            return val * scale * random.uniform(0.9, 1.1)
        
        return Spectrum(
            gamma_ray=jitter(s_gamma),
            xray=jitter(s_xray),
            ultraviolet=jitter(s_uv),
            blue=jitter(s_blue),
            green=jitter(s_green),
            red=jitter(s_red),
            infrared=jitter(s_ir),
            microwave=jitter(s_micro),
            radio=jitter(s_radio)
        )

    def generate_system_stars(self, system_name):
        stars = []
        
        # 1. Determine Count
        roll = random.random()
        if roll < 0.001: count = 4
        elif roll < 0.011: count = 3
        elif roll < 0.111: count = 2
        else: count = 1
        
        # 2. Generate Primary
        p_mass = self._generate_mass(is_primary=True)
        p_type, p_rad, p_temp, p_lum, p_col = self._determine_type_and_radius(p_mass)
        p_hex = self._map_radius_to_hexes(p_rad, p_type)
        p_spec = self._generate_spectrum(p_temp, p_lum)
        
        primary = Star(
            name=f"{system_name} A",
            mass=p_mass,
            diameter_hexes=p_hex,
            temperature=p_temp,
            luminosity=p_lum,
            spectrum=p_spec,
            star_type=p_type,
            color=p_col,
            age=random.uniform(0.1, 10.0) * 1e9, 
            location=HexCoord(0, 0) # Primary always at center
        )
        stars.append(primary)
        
        # 3. Generate Companions
        suffixes = ['B', 'C', 'D']
        min_dist_hex = int(p_hex * 2) + 2 
        
        occupied_hexes = {HexCoord(0, 0)}
        
        for i in range(count - 1):
            c_mass = self._generate_mass(is_primary=False, primary_mass=p_mass)
            c_type, c_rad, c_temp, c_lum, c_col = self._determine_type_and_radius(c_mass)
            c_hex = self._map_radius_to_hexes(c_rad, c_type)
            c_spec = self._generate_spectrum(c_temp, c_lum)
            
            # Use Hex Rings instead of arbitrary polar angle
            # Ensure unique position
            
            target_ring = min_dist_hex + (i * 10) + random.randint(2, 8)
            potential_coords = hex_ring(target_ring)
            
            if not potential_coords:
                 # Fallback if ring 0? Shouldn't happen.
                 loc = HexCoord(target_ring, 0)
            else:
                 # Pick random slot
                 loc = random.choice(potential_coords)
                 
                 # Ensure not colliding with existing (unlikely at these distances but good practice)
                 while loc in occupied_hexes and len(occupied_hexes) < 100:
                     target_ring += 1
                     potential_coords = hex_ring(target_ring)
                     loc = random.choice(potential_coords)
            
            occupied_hexes.add(loc)
            
            companion = Star(
                 name=f"{system_name} {suffixes[i]}",
                 mass=c_mass,
                 diameter_hexes=c_hex,
                 temperature=c_temp,
                 luminosity=c_lum,
                 spectrum=c_spec,
                 star_type=c_type,
                 color=c_col,
                 age=primary.age, 
                 location=loc
            )
            stars.append(companion)
            
        return stars
