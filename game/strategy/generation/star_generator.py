"""``StarGenerator`` — random / blueprint-driven star generation.

PROJ-372 Phase 1 split: extracted from ``stars.py`` for the file-LOC
budget. Pure-math helpers (``kelvin_to_rgb``, Stefan-Boltzmann,
Wien's law) moved to ``game/core/spectrum_math.py``;
``_map_solar_radius_to_hex_radius`` stays here as a private method
because it encodes a game-design choice (Decision D6 in PROJ-372
decisions.md).

Backwards compat: ``stars.py`` re-exports ``StarGenerator`` so the
``galaxy.py`` and ``galaxy_system_generator.py`` import paths
keep working (the canonical importers are migrated in Task 1.7).
"""
from __future__ import annotations

import math
import random
from typing import List

from game.core.hex_math import HexCoord, hex_ring
from game.core.spectrum_math import (
    SOLAR_TEMP_K,
    WIEN_DISPLACEMENT_CONSTANT,
    _HEX_RADIUS_LOG_COEFF,
    _HEX_RADIUS_LOG_OFFSET,
    _HEX_RADIUS_MAX,
    _HEX_RADIUS_MIN,
    _SPECTRUM_JITTER_RANGE,
    _SPECTRUM_SIGMA,
    _WAVELENGTHS,
    kelvin_to_rgb,
    stefan_boltzmann_luminosity,
)
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType


__all__ = ["StarGenerator"]


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
        """Generates mass using a log-normal distribution.

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

    def _determine_type_and_radius(self, mass: float) -> tuple:
        """Determine star type via weighted roll, then set physical properties.

        Returns (StarType, Mass_Solar, Radius_Solar, Temperature_K, Luminosity_Solar, Color).
        Mass may be adjusted to be consistent with the rolled type.
        """
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        star_type = self._roll_star_type()

        # Stefan-Boltzmann types: RED_GIANT, BROWN_DWARF, WHITE_DWARF
        if star_type in self._SB_TYPES:
            mass, radius, temperature, luminosity, color = (
                self._compute_stefan_boltzmann_type(star_type, mass, cfg)
            )

        elif star_type == StarType.BLUE_GIANT:
            mass = max(mass, random.uniform(3, 50))
            luminosity = mass ** 3.5 * random.uniform(1.5, 5.0)
            radius = mass ** 0.8 * random.uniform(5, 20)
            temperature = max(10000, random.uniform(15000, 40000))
            color = kelvin_to_rgb(temperature)

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
            color = kelvin_to_rgb(temperature)

        return star_type, mass, radius, temperature, luminosity, color

    def _compute_stefan_boltzmann_type(
        self, star_type: "StarType", mass: float, cfg
    ) -> tuple:
        """Compute properties for Stefan-Boltzmann types.

        Types: RED_GIANT, BROWN_DWARF, WHITE_DWARF.
        Shared formula: luminosity = radius^2 * (temperature / SOLAR_TEMP_K)^4.

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
        luminosity = stefan_boltzmann_luminosity(radius, temperature)

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
        """Backwards-compat wrapper. Prefer ``game.core.spectrum_math.kelvin_to_rgb``.

        Retained as a method because existing tests call
        ``generator._kelvin_to_rgb(...)`` directly.
        """
        return kelvin_to_rgb(temp)

    def _map_solar_radius_to_hex_radius(self, radius_sol: float, star_type: StarType) -> int:
        """Map solar radius to hex radius (1-6).

        Decision D6: stays here (game design choice — compact remnants
        always 1, supergiants 6, etc.) rather than moving to ``core/``.

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
        """Generate spectrum based on Black Body radiation logic.

        Refined to 9 bands including 3 visible split bands. Uses Wien's
        displacement law with log-gaussian approximation.
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
        """Generate stars for a system; uses blueprint if provided, else random."""
        if blueprint is not None:
            return self.generate_from_blueprint(system_name, blueprint)
        return self._generate_random_stars(system_name)

    def _generate_companions(
        self, count: int, primary: "Star", system_name: str, mass_fn,
    ) -> list:
        """Generate companion stars for a system. Shared logic for both
        blueprint and random star generation."""
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
        """Generate stars based on a system blueprint dict."""
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
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass_constrained(mass_min, mass_max),
        )
        stars.extend(companions)

        return stars

    def _generate_random_stars(self, system_name) -> List[Star]:
        """Generate stars using default random probabilities."""
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
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass(is_primary=True),
        )
        stars.extend(companions)

        return stars

    def _generate_mass_constrained(self, mass_min, mass_max) -> float:
        """Generate star mass within specified solar-mass constraints."""
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
