
import random
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any
from typing import FrozenSet
from game.core.hex_math import HexCoord, hex_ring, hex_circle_filled
from game.core.validation_helpers import (
    require_keys, validate_enum, validate_positive, validate_non_negative, safe_from_dict
)

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

    def get_total_output(self) -> float:
        """Calculate total electromagnetic output across all spectrum bands."""
        return (self.gamma_ray + self.xray + self.ultraviolet +
                self.blue + self.green + self.red +
                self.infrared + self.microwave + self.radio)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Spectrum to dict."""
        return {
            'gamma_ray': self.gamma_ray,
            'xray': self.xray,
            'ultraviolet': self.ultraviolet,
            'blue': self.blue,
            'green': self.green,
            'red': self.red,
            'infrared': self.infrared,
            'microwave': self.microwave,
            'radio': self.radio
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Spectrum':
        """Deserialize Spectrum from dict.

        Args:
            data: Dict with spectrum band values

        Returns:
            Spectrum instance

        Raises:
            PersistenceException: If required keys missing or values invalid
        """
        spectrum_keys = [
            'gamma_ray', 'xray', 'ultraviolet', 'blue', 'green',
            'red', 'infrared', 'microwave', 'radio'
        ]
        require_keys(data, spectrum_keys, 'Spectrum')

        # Validate all spectrum values are non-negative
        for key in spectrum_keys:
            validate_non_negative(data[key], key, 'Spectrum')

        return cls(
            gamma_ray=data['gamma_ray'],
            xray=data['xray'],
            ultraviolet=data['ultraviolet'],
            blue=data['blue'],
            green=data['green'],
            red=data['red'],
            infrared=data['infrared'],
            microwave=data['microwave'],
            radio=data['radio']
        )

@dataclass
class Star:
    name: str
    mass: float  # Solar Masses
    radius_hexes: int  # Radius in hexes (1 = center only, 2 = center + ring 1, etc.)
    temperature: float # Kelvin
    luminosity: float # Solar Luminosity
    spectrum: Spectrum
    star_type: StarType
    color: tuple # (R, G, B)
    age: float # Years

    # Location relative to system center (0,0,0)
    location: HexCoord = field(default_factory=lambda: HexCoord(0, 0))

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this star (PROJ-139 IZoneOccupant).

        radius_hexes=1 → center hex only (1 hex)
        radius_hexes=2 → center + ring 1 (7 hexes)
        radius_hexes=N → hex_circle_filled(location, N-1)

        Returns:
            FrozenSet of HexCoord in LOCAL system coordinates
        """
        return hex_circle_filled(self.location, max(0, self.radius_hexes - 1))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Star to dict."""
        from game.core.hex_math import hex_to_dict
        return {
            'name': self.name,
            'mass': self.mass,
            'radius_hexes': self.radius_hexes,
            'temperature': self.temperature,
            'luminosity': self.luminosity,
            'spectrum': self.spectrum.to_dict(),
            'star_type': self.star_type.name,  # Enum to string
            'color': list(self.color),  # Tuple to list for JSON
            'age': self.age,
            'location': hex_to_dict(self.location)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Star':
        """Deserialize Star from dict.

        Args:
            data: Dict with star properties

        Returns:
            Star instance

        Raises:
            PersistenceException: If required keys missing or values invalid
        """
        from game.core.hex_math import hex_from_dict
        from game.core.exceptions import PersistenceException
        from game.core.error_codes import ErrorCode

        # Validate required keys
        require_keys(data, [
            'name', 'mass', 'radius_hexes', 'temperature', 'luminosity',
            'spectrum', 'star_type', 'color', 'age', 'location'
        ], 'Star')

        # Validate enum
        star_type = validate_enum(data['star_type'], StarType, 'star_type', 'Star')

        # Validate positive values
        validate_positive(data['mass'], 'mass', 'Star')
        validate_positive(data['temperature'], 'temperature', 'Star')
        validate_positive(data['luminosity'], 'luminosity', 'Star')

        # Wrap nested from_dict calls with context
        spectrum = safe_from_dict(Spectrum.from_dict, data['spectrum'], 'Star.spectrum')

        # Wrap hex_from_dict with context
        try:
            location = hex_from_dict(data['location'])
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"Star: invalid location data - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "Star",
                    "field": "location",
                    "error_type": type(e).__name__,
                    "error": str(e),
                }
            ) from e

        return cls(
            name=data['name'],
            mass=data['mass'],
            radius_hexes=data['radius_hexes'],
            temperature=data['temperature'],
            luminosity=data['luminosity'],
            spectrum=spectrum,
            star_type=star_type,
            color=tuple(data['color']),
            age=data['age'],
            location=location
        )

class StarGenerator:
    def __init__(self):
        pass

    def _generate_mass(self, is_primary: bool = True, primary_mass: float = None) -> float:
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

    # Star type probabilities for direct-roll selection.
    # Targets per ~57-star galaxy: Blue Giant ~3-4, White Dwarf ~1-2,
    # Brown Dwarf ~1-2, Neutron Star ~1, Black Hole ~1 (rarest).
    _TYPE_WEIGHTS = {
        StarType.MAIN_SEQUENCE: 0.525,
        StarType.RED_DWARF:     0.250,
        StarType.RED_GIANT:     0.070,
        StarType.BLUE_GIANT:    0.060,
        StarType.BROWN_DWARF:   0.030,
        StarType.WHITE_DWARF:   0.030,
        StarType.NEUTRON_STAR:  0.020,
        StarType.BLACK_HOLE:    0.015,
    }

    def _determine_type_and_radius(self, mass: float, age_ratio: float = 0.5) -> tuple:
        """
        Determine star type via weighted roll, then set physical properties.

        Returns (StarType, Radius_Solar, Temperature_K, Luminosity_Solar, Color).
        The generated mass informs properties but does not gate type selection.
        """
        # Roll for type directly using weighted probabilities
        star_type = self._roll_star_type()

        # Set properties based on type, using mass as a seed for variation
        if star_type == StarType.BLUE_GIANT:
            # Massive hot stars — override mass upward if needed
            mass = max(mass, random.uniform(8, 50))
            luminosity = mass ** 3.5 * random.uniform(1.5, 5.0)
            radius = mass ** 0.8 * random.uniform(5, 20)
            temperature = max(10000, random.uniform(15000, 40000))
            color = self._kelvin_to_rgb(temperature)

        elif star_type == StarType.RED_GIANT:
            mass = max(mass, random.uniform(0.8, 5.0))
            radius = mass ** 0.8 * random.uniform(10, 100)
            temperature = random.uniform(3000, 4500)
            luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)
            color = (255, 60, 60)

        elif star_type == StarType.RED_DWARF:
            mass = min(mass, random.uniform(0.08, 0.5))
            luminosity = mass ** 3.5
            radius = mass ** 0.8
            t_ratio = (luminosity / (radius ** 2)) ** 0.25
            temperature = t_ratio * SOLAR_TEMP_K
            color = (255, 100, 100)

        elif star_type == StarType.BROWN_DWARF:
            mass = random.uniform(0.01, 0.08)
            radius = random.uniform(0.08, 0.15)  # Jupiter-sized
            temperature = random.uniform(500, 2500)
            luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)
            color = (140, 60, 40)

        elif star_type == StarType.WHITE_DWARF:
            mass = max(mass, random.uniform(0.5, 1.4))
            radius = 0.01  # Earth-sized
            temperature = random.uniform(8000, 40000)
            luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)
            color = (220, 220, 255)

        elif star_type == StarType.NEUTRON_STAR:
            mass = max(mass, random.uniform(1.4, 3.0))
            radius = 0.00002
            temperature = 1000000
            luminosity = 0.01
            color = (200, 200, 255)

        elif star_type == StarType.BLACK_HOLE:
            mass = max(mass, random.uniform(5, 50))
            radius = 0.0001
            temperature = 0  # Event horizon
            luminosity = 0.001  # Accretion disk
            color = (20, 0, 40)

        else:
            # MAIN_SEQUENCE — standard mass-luminosity-radius relations
            luminosity = mass ** 3.5
            radius = mass ** 0.8
            t_ratio = (luminosity / (radius ** 2)) ** 0.25
            temperature = t_ratio * SOLAR_TEMP_K
            color = self._kelvin_to_rgb(temperature)

        return star_type, radius, temperature, luminosity, color

    def _roll_star_type(self) -> StarType:
        """Select star type using weighted random roll."""
        roll = random.random()
        cumulative = 0.0
        for star_type, weight in self._TYPE_WEIGHTS.items():
            cumulative += weight
            if roll < cumulative:
                return star_type
        return StarType.MAIN_SEQUENCE

    def _kelvin_to_rgb(self, temp: float) -> tuple:
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

    def _map_solar_radius_to_hex_radius(self, radius_sol: float, star_type: StarType) -> int:
        """Map solar radius to hex radius (1-6).

        1 = center hex only (compact/small stars)
        2 = center + ring 1 (medium stars, 7 hexes)
        3 = center + 2 rings (large stars, 19 hexes)
        4 = center + 3 rings (giant stars, 37 hexes)
        5 = center + 4 rings (supergiant stars, 61 hexes)
        6 = center + 5 rings (largest giants/Dyson Spheres, 91 hexes)
        """
        if star_type in (StarType.NEUTRON_STAR, StarType.BLACK_HOLE, StarType.WHITE_DWARF):
            return 1  # Compact remnants occupy center hex only

        if radius_sol < 0.8:
            return 1
        if radius_sol < 2.0:
            return 2
        if radius_sol < 5.0:
            return 2

        # Giants and supergiants: logarithmic scaling
        log_r = math.log10(radius_sol)
        hex_radius = 1.73 * log_r + 0.8  # Adjusted coefficients for radius scale
        hex_radius = min(6, max(1, int(round(hex_radius))))
        return hex_radius

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

    def generate_system_stars(self, system_name, blueprint=None):
        """
        Generate stars for a system.

        Args:
            system_name: Name of the star system.
            blueprint: Optional blueprint dict from system_blueprints.json.
                      If None, uses default random generation.

        Returns:
            List of Star objects.
        """
        if blueprint is not None:
            return self.generate_from_blueprint(system_name, blueprint)

        return self._generate_random_stars(system_name)

    def _generate_companions(
        self,
        count: int,
        primary: 'Star',
        system_name: str,
        mass_fn,
    ) -> list:
        """Generate companion stars for a system.

        Shared logic for both blueprint and random star generation.
        Handles type/radius determination, spectrum generation, and
        collision-safe placement.

        Args:
            count: Number of companions to generate.
            primary: The primary star (for age).
            system_name: System name for star naming.
            mass_fn: Callable(index) -> float that generates companion mass.

        Returns:
            List of companion Star objects.
        """
        companions = []
        suffixes = ['B', 'C', 'D']
        min_dist_hex = primary.radius_hexes + 2
        occupied_hexes = {HexCoord(0, 0)}

        for i in range(count):
            c_mass = mass_fn(i)
            c_type, c_rad, c_temp, c_lum, c_col = self._determine_type_and_radius(c_mass)
            c_hex = self._map_solar_radius_to_hex_radius(c_rad, c_type)
            c_spec = self._generate_spectrum(c_temp, c_lum)

            target_ring = min_dist_hex + (i * 10) + random.randint(2, 8)
            potential_coords = hex_ring(target_ring)

            if not potential_coords:
                loc = HexCoord(target_ring, 0)
            else:
                loc = random.choice(potential_coords)
                while loc in occupied_hexes and len(occupied_hexes) < 100:
                    target_ring += 1
                    potential_coords = hex_ring(target_ring)
                    loc = random.choice(potential_coords)

            occupied_hexes.add(loc)

            companion = Star(
                name=f"{system_name} {suffixes[i]}",
                mass=c_mass,
                radius_hexes=c_hex,
                temperature=c_temp,
                luminosity=c_lum,
                spectrum=c_spec,
                star_type=c_type,
                color=c_col,
                age=primary.age,
                location=loc
            )
            companions.append(companion)

        return companions

    def generate_from_blueprint(self, system_name, blueprint):
        """
        Generate stars based on a system blueprint.

        Args:
            system_name: Name of the star system.
            blueprint: Blueprint dict containing star_count and star_mass constraints.

        Returns:
            List of Star objects.
        """
        stars = []

        # 1. Determine Count from blueprint
        star_count_spec = blueprint.get("star_count", 1)
        if isinstance(star_count_spec, int):
            count = star_count_spec
        elif isinstance(star_count_spec, dict):
            if "min" in star_count_spec:
                count = random.randint(star_count_spec["min"], star_count_spec.get("max", star_count_spec["min"]))
            elif "distribution" in star_count_spec:
                # Weighted distribution
                dist = star_count_spec["distribution"]
                total = sum(dist.values())
                r = random.random() * total
                cumulative = 0
                count = 1
                for k, v in dist.items():
                    cumulative += v
                    if r <= cumulative:
                        count = int(k)
                        break
            else:
                count = 1
        else:
            count = 1

        count = max(1, min(4, count))

        # 2. Get mass constraints from blueprint
        mass_spec = blueprint.get("star_mass", {})
        mass_min = mass_spec.get("min", 0.1)
        mass_max = mass_spec.get("max", 100.0)

        # 3. Generate Primary
        p_mass = self._generate_mass_constrained(mass_min, mass_max)
        p_type, p_rad, p_temp, p_lum, p_col = self._determine_type_and_radius(p_mass)
        p_hex = self._map_solar_radius_to_hex_radius(p_rad, p_type)
        p_spec = self._generate_spectrum(p_temp, p_lum)

        primary = Star(
            name=f"{system_name} A",
            mass=p_mass,
            radius_hexes=p_hex,
            temperature=p_temp,
            luminosity=p_lum,
            spectrum=p_spec,
            star_type=p_type,
            color=p_col,
            age=random.uniform(0.1, 10.0) * 1e9,
            location=HexCoord(0, 0)
        )
        stars.append(primary)

        # 4. Generate Companions
        c_mass_max = min(mass_max, p_mass * 0.99)
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass_constrained(mass_min, c_mass_max),
        )
        stars.extend(companions)

        return stars

    def _generate_random_stars(self, system_name):
        """
        Generate stars using default random probabilities.
        """
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
        p_hex = self._map_solar_radius_to_hex_radius(p_rad, p_type)
        p_spec = self._generate_spectrum(p_temp, p_lum)

        primary = Star(
            name=f"{system_name} A",
            mass=p_mass,
            radius_hexes=p_hex,
            temperature=p_temp,
            luminosity=p_lum,
            spectrum=p_spec,
            star_type=p_type,
            color=p_col,
            age=random.uniform(0.1, 10.0) * 1e9,
            location=HexCoord(0, 0)
        )
        stars.append(primary)

        # 3. Generate Companions
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass(is_primary=False, primary_mass=p_mass),
        )
        stars.extend(companions)

        return stars

    def _generate_mass_constrained(self, mass_min, mass_max):
        """
        Generate star mass within specified constraints.

        Args:
            mass_min: Minimum mass in solar masses.
            mass_max: Maximum mass in solar masses.

        Returns:
            Mass in solar masses within the constraints.
        """
        # Use log-normal distribution centered in the constraint range
        log_min = math.log(mass_min)
        log_max = math.log(mass_max)
        log_center = (log_min + log_max) / 2
        log_sigma = (log_max - log_min) / 4  # ~95% within range

        for _ in range(100):  # Max attempts
            mass = random.lognormvariate(log_center, max(0.1, log_sigma))
            if mass_min <= mass <= mass_max:
                return mass

        # Fallback to uniform in log space
        return math.exp(random.uniform(log_min, log_max))
