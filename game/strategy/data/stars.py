from __future__ import annotations

import random
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List
from typing import FrozenSet
from game.core.hex_math import HexCoord, hex_ring, hex_circle_filled
from game.core.validation_helpers import (
    require_keys, validate_enum, validate_positive, validate_non_negative, safe_from_dict
)

# Solar reference constants
SOLAR_MASS_KG = 1.989e30
SOLAR_RADIUS_M = 6.957e8
SOLAR_LUMINOSITY_W = 3.828e26
SOLAR_TEMP_K = 5778

# Kelvin-to-RGB approximation coefficients (Tanner Helland's algorithm)
# Source: tannerhelland.com/2012/09/18/convert-temperature-rgb-algorithm-code
_KELVIN_RED_COEFF = 329.698727446
_KELVIN_RED_EXP = -0.1332047592
_KELVIN_GREEN_LOW_COEFF = 99.4708025861
_KELVIN_GREEN_LOW_OFFSET = -161.1195681661
_KELVIN_GREEN_HIGH_COEFF = 288.1221695283
_KELVIN_GREEN_HIGH_EXP = -0.0755148492
_KELVIN_BLUE_COEFF = 138.5177312231
_KELVIN_BLUE_OFFSET = -305.0447927307
_KELVIN_WARM_COOL_BOUNDARY = 66   # temp/100 dividing warm and cool formulas
_KELVIN_BLUE_FLOOR = 19           # temp/100 below which blue channel = 0

# Wien's displacement law constant (meters * Kelvin)
WIEN_DISPLACEMENT_CONSTANT = 2.898e-3
_SPECTRUM_SIGMA = 0.5             # log-gaussian width for Planck approximation
_SPECTRUM_JITTER_RANGE = (0.9, 1.1)

# Representative wavelengths (meters) for 9-band spectrum model
_WAVELENGTHS = {
    'gamma': 1e-12, 'xray': 1e-9, 'uv': 1e-7,
    'blue': 4.5e-7, 'green': 5.5e-7, 'red': 6.5e-7,
    'ir': 1e-5, 'microwave': 1e-2, 'radio': 10,
}

# Hex radius mapping coefficients (solar radii → hex radius 1-6)
_HEX_RADIUS_LOG_COEFF = 1.73
_HEX_RADIUS_LOG_OFFSET = 0.8
_HEX_RADIUS_MIN = 1
_HEX_RADIUS_MAX = 6

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

    # Visual representation (assigned during generation, persisted in saves)
    image_id: str = ""  # Filename from star assets (e.g., "StarBlueVariant_3.png")

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
            'location': hex_to_dict(self.location),
            'image_id': self.image_id,
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
        # Temperature can be 0 for BLACK_HOLE stars (event horizon has no observable temperature)
        validate_non_negative(data['temperature'], 'temperature', 'Star')
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
            location=location,
            image_id=data.get('image_id', ''),
        )

class StarGenerator:
    def __init__(self, image_registry=None):
        """Initialize the star generator.

        Args:
            image_registry: Optional StarImageRegistry for assigning images.
                When None, stars get empty image_id (useful for tests).
        """
        self._image_registry = image_registry

    def _get_image_id(self, star_type: StarType) -> str:
        """Get an image_id for a star type from the registry.

        Returns empty string if no registry is available.
        """
        if self._image_registry is None:
            return ""
        return self._image_registry.get_random_image(star_type)

    def _generate_mass(self, is_primary: bool = True, primary_mass: float = None) -> float:
        """
        Generates mass using a log-normal distribution.
        If not primary, ensures mass < primary_mass.
        """
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        for _ in range(cfg.mass_max_attempts):
            mass = random.lognormvariate(0, cfg.mass_sigma)

            if mass < cfg.mass_min:
                continue
            if mass > cfg.mass_max:
                continue

            if not is_primary and primary_mass is not None:
                if mass >= primary_mass:
                    continue

            return mass

        # Fallback: uniform in log space
        return math.exp(random.uniform(
            math.log(cfg.mass_min), math.log(cfg.mass_max)
        ))

    # Star types that use the Stefan-Boltzmann luminosity formula:
    # luminosity = radius^2 * (temperature / SOLAR_TEMP_K)^4
    _SB_TYPES = frozenset({StarType.RED_GIANT, StarType.BROWN_DWARF, StarType.WHITE_DWARF})

    def _determine_type_and_radius(self, mass: float, age_ratio: float = 0.5) -> tuple:
        """
        Determine star type via weighted roll, then set physical properties.

        Returns (StarType, Mass_Solar, Radius_Solar, Temperature_K, Luminosity_Solar, Color).
        Mass may be adjusted to be consistent with the rolled type.
        """
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        star_type = self._roll_star_type()

        # Stefan-Boltzmann types: RED_GIANT, BROWN_DWARF, WHITE_DWARF
        # These share: luminosity = radius^2 * (temperature / SOLAR_TEMP_K)^4
        if star_type in self._SB_TYPES:
            mass, radius, temperature, luminosity, color = (
                self._compute_stefan_boltzmann_type(star_type, mass, cfg)
            )

        elif star_type == StarType.BLUE_GIANT:
            # Massive hot stars — includes B-type main sequence (3-8 Msol)
            # through to true supergiants (50+ Msol)
            mass = max(mass, random.uniform(3, 50))
            luminosity = mass ** 3.5 * random.uniform(1.5, 5.0)
            radius = mass ** 0.8 * random.uniform(5, 20)
            temperature = max(10000, random.uniform(15000, 40000))
            color = self._kelvin_to_rgb(temperature)

        elif star_type == StarType.RED_DWARF:
            mass = min(mass, random.uniform(0.08, 0.5))
            luminosity = mass ** 3.5
            radius = mass ** 0.8
            t_ratio = (luminosity / (radius ** 2)) ** 0.25
            temperature = t_ratio * SOLAR_TEMP_K
            color = (255, 100, 100)

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

        return star_type, mass, radius, temperature, luminosity, color

    def _compute_stefan_boltzmann_type(
        self, star_type: 'StarType', mass: float, cfg
    ) -> tuple:
        """
        Compute properties for Stefan-Boltzmann types (RED_GIANT, BROWN_DWARF, WHITE_DWARF).

        These types share the luminosity formula:
            luminosity = radius^2 * (temperature / SOLAR_TEMP_K)^4

        Args:
            star_type: The star type (must be in _SB_TYPES).
            mass: Input mass in solar masses.
            cfg: StarGenerationConfig instance.

        Returns:
            (mass, radius, temperature, luminosity, color) tuple.
        """
        props = cfg.stefan_boltzmann_types[star_type.name]

        # Adjust mass per type's mode
        mode = props["mass_mode"]
        if mode == "max":
            mass = max(mass, random.uniform(*props["mass_range"]))
        elif mode == "replace":
            mass = random.uniform(*props["mass_range"])
        elif mode == "clamp":
            mass = min(mass, props["mass_clamp_upper"])
            mass = max(mass, props["mass_clamp_lower"])

        # Compute radius
        if "radius_fixed" in props:
            radius = props["radius_fixed"]
        elif props.get("radius_power") is not None:
            radius = mass ** props["radius_power"] * random.uniform(
                *props["radius_multiplier_range"]
            )
        else:
            radius = random.uniform(*props["radius_range"])

        # Temperature from range
        temperature = random.uniform(*props["temp_range"])

        # Stefan-Boltzmann luminosity
        luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)

        color = tuple(props["color"])

        return mass, radius, temperature, luminosity, color

    def _roll_star_type(self) -> StarType:
        """Select star type using weighted random roll."""
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        roll = random.random()
        cumulative = 0.0
        for type_name, weight in cfg.type_weights.items():
            cumulative += weight
            if roll < cumulative:
                return StarType[type_name]
        return StarType.MAIN_SEQUENCE

    def _kelvin_to_rgb(self, temp: float) -> tuple:
        """Approximate RGB from Kelvin using Tanner Helland's algorithm."""
        temp = temp / 100

        # Red channel
        if temp <= _KELVIN_WARM_COOL_BOUNDARY:
            r = 255
        else:
            r = temp - 60
            r = _KELVIN_RED_COEFF * (r ** _KELVIN_RED_EXP)
            if r < 0: r = 0
            if r > 255: r = 255

        # Green channel
        if temp <= _KELVIN_WARM_COOL_BOUNDARY:
            g = temp
            g = _KELVIN_GREEN_LOW_COEFF * math.log(g) + _KELVIN_GREEN_LOW_OFFSET
            if g < 0: g = 0
            if g > 255: g = 255
        else:
            g = temp - 60
            g = _KELVIN_GREEN_HIGH_COEFF * (g ** _KELVIN_GREEN_HIGH_EXP)
            if g < 0: g = 0
            if g > 255: g = 255

        # Blue channel
        if temp >= _KELVIN_WARM_COOL_BOUNDARY:
            b = 255
        else:
            if temp <= _KELVIN_BLUE_FLOOR:
                b = 0
            else:
                b = temp - 10
                b = _KELVIN_BLUE_COEFF * math.log(b) + _KELVIN_BLUE_OFFSET
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
        hex_radius = _HEX_RADIUS_LOG_COEFF * log_r + _HEX_RADIUS_LOG_OFFSET
        hex_radius = min(_HEX_RADIUS_MAX, max(_HEX_RADIUS_MIN, int(round(hex_radius))))
        return hex_radius

    def _generate_spectrum(self, temp, luminosity) -> Spectrum:
        """
        Generate spectrum based on Black Body radiation logic.
        Refined to 9 bands including 3 visible split bands.
        Uses Wien's displacement law with log-gaussian approximation.
        """
        peak_wavelength = WIEN_DISPLACEMENT_CONSTANT / temp if temp > 0 else 1e99

        def intensity_at(target_wl) -> float:
            if peak_wavelength <= 0:
                return 0
            dist = math.log10(target_wl) - math.log10(peak_wavelength)
            return math.exp(-(dist ** 2) / (2 * _SPECTRUM_SIGMA ** 2))

        wl = _WAVELENGTHS
        intensities = {band: intensity_at(wavelength) for band, wavelength in wl.items()}

        total = sum(intensities.values())
        scale = luminosity / total if total > 0 else 0

        jitter_min, jitter_max = _SPECTRUM_JITTER_RANGE

        def jitter(val) -> float:
            return val * scale * random.uniform(jitter_min, jitter_max)

        return Spectrum(
            gamma_ray=jitter(intensities['gamma']),
            xray=jitter(intensities['xray']),
            ultraviolet=jitter(intensities['uv']),
            blue=jitter(intensities['blue']),
            green=jitter(intensities['green']),
            red=jitter(intensities['red']),
            infrared=jitter(intensities['ir']),
            microwave=jitter(intensities['microwave']),
            radio=jitter(intensities['radio']),
        )

    def generate_system_stars(self, system_name, blueprint=None) -> List[Star]:
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
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        companions = []
        suffixes = ['B', 'C', 'D']
        min_dist_hex = primary.radius_hexes + cfg.companion_min_offset
        occupied_hexes = {HexCoord(0, 0)}

        for i in range(count):
            c_mass = mass_fn(i)
            c_type, c_mass, c_rad, c_temp, c_lum, c_col = self._determine_type_and_radius(c_mass)
            c_hex = self._map_solar_radius_to_hex_radius(c_rad, c_type)
            c_spec = self._generate_spectrum(c_temp, c_lum)

            target_ring = (min_dist_hex
                           + (i * cfg.companion_ring_multiplier)
                           + random.randint(cfg.companion_jitter_min, cfg.companion_jitter_max))
            potential_coords = hex_ring(target_ring)

            if not potential_coords:
                loc = HexCoord(target_ring, 0)
            else:
                loc = random.choice(potential_coords)
                while loc in occupied_hexes and len(occupied_hexes) < cfg.companion_collision_limit:
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
                location=loc,
                image_id=self._get_image_id(c_type),
            )
            companions.append(companion)

        return companions

    def generate_from_blueprint(self, system_name, blueprint) -> List[Star]:
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
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        p_mass = self._generate_mass_constrained(mass_min, mass_max)
        p_type, p_mass, p_rad, p_temp, p_lum, p_col = self._determine_type_and_radius(p_mass)
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
            age=random.uniform(cfg.age_min, cfg.age_max) * cfg.age_unit,
            location=HexCoord(0, 0),
            image_id=self._get_image_id(p_type),
        )
        stars.append(primary)

        # 4. Generate Companions
        # With type-first generation, companion mass is set by its rolled type,
        # so we use the full blueprint mass range rather than constraining to
        # below primary mass.
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass_constrained(mass_min, mass_max),
        )
        stars.extend(companions)

        return stars

    def _generate_random_stars(self, system_name) -> List[Star]:
        """
        Generate stars using default random probabilities.
        """
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        stars = []

        # 1. Determine Count from probability thresholds
        roll = random.random()
        count = cfg.system_default_count
        for entry in cfg.system_count_thresholds:
            if roll < entry["cumulative"]:
                count = entry["count"]
                break

        # 2. Generate Primary
        p_mass = self._generate_mass(is_primary=True)
        p_type, p_mass, p_rad, p_temp, p_lum, p_col = self._determine_type_and_radius(p_mass)
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
            age=random.uniform(cfg.age_min, cfg.age_max) * cfg.age_unit,
            location=HexCoord(0, 0),
            image_id=self._get_image_id(p_type),
        )
        stars.append(primary)

        # 3. Generate Companions
        # With type-first generation, companion mass is set by its rolled type,
        # so we don't constrain it by primary mass (which may be small if the
        # primary rolled RED_DWARF or BROWN_DWARF).
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass(is_primary=True),
        )
        stars.extend(companions)

        return stars

    def _generate_mass_constrained(self, mass_min, mass_max) -> float:
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
