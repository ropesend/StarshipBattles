"""``StarGenerator`` — random / blueprint-driven star generation.

PROJ-372 Phase 1 split: extracted from ``stars.py`` (which re-exports
``StarGenerator`` for compat). Pure-math helpers moved to
``game/core/spectrum_math.py``; ``_map_solar_radius_to_hex_radius`` stays
here as it encodes a game-design choice (PROJ-372 decisions.md D6).

PROJ-473: physics draws use an injected ``rng`` (the dedicated
``physics_rng`` — H7 S4); star ``image_id`` uses a SEPARATE ``image_rng``
stream (H7 S6) so image draws never shift the physics sequence (which would
move S9 warp geometry). Both default to module-level ``random`` when ``None``
(back-compat for tool/test callers).
"""
from __future__ import annotations

import math
import random
from typing import List, Optional

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

    def _get_image_id(
        self, star_type: StarType, image_rng: Optional[random.Random] = None
    ) -> str:
        """Get an image_id for a star type from the registry.

        PROJ-473 H7 S6: draws from the separate ``image_rng``, not the physics
        rng. Returns empty string if no registry is available.
        """
        if self._image_registry is None:
            return ""
        return self._image_registry.get_random_image(star_type, rng=image_rng)

    def _generate_mass(
        self,
        is_primary: bool = True,
        primary_mass: float = None,
        rng: random.Random = random,
    ) -> float:
        """Generates mass using a log-normal distribution.

        If not primary, ensures mass < primary_mass.
        """
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        for _ in range(cfg.mass_max_attempts):
            mass = rng.lognormvariate(0, cfg.mass_sigma)

            if mass < cfg.mass_min:
                continue
            if mass > cfg.mass_max:
                continue

            if not is_primary and primary_mass is not None:
                if mass >= primary_mass:
                    continue

            return mass

        # Fallback: uniform in log space
        return math.exp(rng.uniform(
            math.log(cfg.mass_min), math.log(cfg.mass_max)
        ))

    # Star types that use the Stefan-Boltzmann luminosity formula:
    # luminosity = radius^2 * (temperature / SOLAR_TEMP_K)^4
    _SB_TYPES = frozenset({StarType.RED_GIANT, StarType.BROWN_DWARF, StarType.WHITE_DWARF})

    def _determine_type_and_radius(
        self, mass: float, rng: random.Random = random
    ) -> tuple:
        """Determine star type via weighted roll, then set physical properties.

        Returns (StarType, Mass_Solar, Radius_Solar, Temperature_K, Luminosity_Solar, Color).
        Mass may be adjusted to be consistent with the rolled type.
        """
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        star_type = self._roll_star_type(rng=rng)

        # Stefan-Boltzmann types: RED_GIANT, BROWN_DWARF, WHITE_DWARF
        if star_type in self._SB_TYPES:
            mass, radius, temperature, luminosity, color = (
                self._compute_stefan_boltzmann_type(star_type, mass, cfg, rng=rng)
            )

        elif star_type == StarType.BLUE_GIANT:
            mass = max(mass, rng.uniform(3, 50))
            luminosity = mass ** 3.5 * rng.uniform(1.5, 5.0)
            radius = mass ** 0.8 * rng.uniform(5, 20)
            temperature = max(10000, rng.uniform(15000, 40000))
            color = kelvin_to_rgb(temperature)

        elif star_type == StarType.RED_DWARF:
            mass = min(mass, rng.uniform(0.08, 0.5))
            luminosity = mass ** 3.5
            radius = mass ** 0.8
            t_ratio = (luminosity / (radius ** 2)) ** 0.25
            temperature = t_ratio * SOLAR_TEMP_K
            color = (255, 100, 100)

        elif star_type == StarType.NEUTRON_STAR:
            mass = max(mass, rng.uniform(1.4, 3.0))
            radius = 0.00002
            temperature = 1000000
            luminosity = 0.01
            color = (200, 200, 255)

        elif star_type == StarType.BLACK_HOLE:
            mass = max(mass, rng.uniform(5, 50))
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
        self, star_type: "StarType", mass: float, cfg, rng: random.Random = random
    ) -> tuple:
        """Compute properties for Stefan-Boltzmann types (RED_GIANT,
        BROWN_DWARF, WHITE_DWARF). Shared formula:
        luminosity = radius^2 * (temperature / SOLAR_TEMP_K)^4.

        Returns ``(mass, radius, temperature, luminosity, color)``.
        """
        props = cfg.stefan_boltzmann_types[star_type.name]

        # Adjust mass per type's mode
        mode = props["mass_mode"]
        if mode == "max":
            mass = max(mass, rng.uniform(*props["mass_range"]))
        elif mode == "replace":
            mass = rng.uniform(*props["mass_range"])
        elif mode == "clamp":
            mass = min(mass, props["mass_clamp_upper"])
            mass = max(mass, props["mass_clamp_lower"])

        # Compute radius
        if "radius_fixed" in props:
            radius = props["radius_fixed"]
        elif props.get("radius_power") is not None:
            radius = mass ** props["radius_power"] * rng.uniform(
                *props["radius_multiplier_range"]
            )
        else:
            radius = rng.uniform(*props["radius_range"])

        # Temperature from range
        temperature = rng.uniform(*props["temp_range"])

        # Stefan-Boltzmann luminosity
        luminosity = stefan_boltzmann_luminosity(radius, temperature)

        color = tuple(props["color"])

        return mass, radius, temperature, luminosity, color

    def _roll_star_type(self, rng: random.Random = random) -> StarType:
        """Select star type using weighted random roll."""
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        roll = rng.random()
        cumulative = 0.0
        for type_name, weight in cfg.type_weights.items():
            cumulative += weight
            if roll < cumulative:
                return StarType[type_name]
        return StarType.MAIN_SEQUENCE

    def _kelvin_to_rgb(self, temp: float) -> tuple:
        """Compat wrapper (tests call ``generator._kelvin_to_rgb``). Prefer
        ``game.core.spectrum_math.kelvin_to_rgb``."""
        return kelvin_to_rgb(temp)

    def _map_solar_radius_to_hex_radius(self, radius_sol: float, star_type: StarType) -> int:
        """Map solar radius to hex radius (1-6).

        Decision D6: stays here (game design choice). 1 = center hex only
        (compact/small); 2 = +ring 1 (medium, 7 hexes); 3 = +2 rings (large,
        19); 4 = +3 rings (giant, 37); 5 = +4 rings (supergiant, 61);
        6 = +5 rings (largest/Dyson Spheres, 91 hexes).
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

    def _generate_spectrum(self, temp, luminosity, rng: random.Random = random) -> Spectrum:
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
            return val * scale * rng.uniform(jitter_min, jitter_max)

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

    def generate_system_stars(
        self, system_name, blueprint=None,
        rng: Optional[random.Random] = None,
        image_rng: Optional[random.Random] = None,
    ) -> List[Star]:
        """Generate stars for a system; uses blueprint if provided, else random.

        Args:
            system_name: System name (used for star naming).
            blueprint: Optional system blueprint dict.
            rng: PROJ-473 H7 S4 — physics rng for all star physics draws
                (module-level ``random`` when None).
            image_rng: PROJ-473 H7 S6 — SEPARATE stream for ``image_id``, kept
                distinct from ``rng`` so image draws never shift the physics
                sequence (unseeded ``Random()`` when None).
        """
        if rng is None:
            # PROJ-473 Task 3.3: fresh per-instance Random(), NOT module random,
            # so no generation draw escapes to global state.
            rng = random.Random()
        if blueprint is not None:
            return self.generate_from_blueprint(
                system_name, blueprint, rng=rng, image_rng=image_rng
            )
        return self._generate_random_stars(system_name, rng=rng, image_rng=image_rng)

    def _generate_companions(
        self, count: int, primary: "Star", system_name: str, mass_fn,
        rng: random.Random = random, image_rng: Optional[random.Random] = None,
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
            c_type, c_mass, c_rad, c_temp, c_lum, c_col = self._determine_type_and_radius(c_mass, rng=rng)
            c_hex = self._map_solar_radius_to_hex_radius(c_rad, c_type)
            c_spec = self._generate_spectrum(c_temp, c_lum, rng=rng)

            target_ring = (min_dist_hex
                           + (i * cfg.companion_ring_multiplier)
                           + rng.randint(cfg.companion_jitter_min, cfg.companion_jitter_max))
            potential_coords = hex_ring(target_ring)

            if not potential_coords:
                loc = HexCoord(target_ring, 0)
            else:
                loc = rng.choice(potential_coords)
                while loc in occupied_hexes and len(occupied_hexes) < cfg.companion_collision_limit:
                    target_ring += 1
                    potential_coords = hex_ring(target_ring)
                    loc = rng.choice(potential_coords)

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
                image_id=self._get_image_id(c_type, image_rng=image_rng),
            )
            companions.append(companion)

        return companions

    def generate_from_blueprint(
        self, system_name, blueprint, rng: random.Random = random,
        image_rng: Optional[random.Random] = None,
    ) -> List[Star]:
        """Generate stars based on a system blueprint dict."""
        stars = []

        # 1. Determine Count from blueprint
        star_count_spec = blueprint.get("star_count", 1)
        if isinstance(star_count_spec, int):
            count = star_count_spec
        elif isinstance(star_count_spec, dict):
            if "min" in star_count_spec:
                count = rng.randint(star_count_spec["min"], star_count_spec.get("max", star_count_spec["min"]))
            elif "distribution" in star_count_spec:
                # Weighted distribution
                dist = star_count_spec["distribution"]
                total = sum(dist.values())
                r = rng.random() * total
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

        p_mass = self._generate_mass_constrained(mass_min, mass_max, rng=rng)
        p_type, p_mass, p_rad, p_temp, p_lum, p_col = self._determine_type_and_radius(p_mass, rng=rng)
        p_hex = self._map_solar_radius_to_hex_radius(p_rad, p_type)
        p_spec = self._generate_spectrum(p_temp, p_lum, rng=rng)

        primary = Star(
            name=f"{system_name} A",
            mass=p_mass,
            radius_hexes=p_hex,
            temperature=p_temp,
            luminosity=p_lum,
            spectrum=p_spec,
            star_type=p_type,
            color=p_col,
            age=rng.uniform(cfg.age_min, cfg.age_max) * cfg.age_unit,
            location=HexCoord(0, 0),
            image_id=self._get_image_id(p_type, image_rng=image_rng),
        )
        stars.append(primary)

        # 4. Generate Companions
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass_constrained(mass_min, mass_max, rng=rng),
            rng=rng,
            image_rng=image_rng,
        )
        stars.extend(companions)

        return stars

    def _generate_random_stars(
        self, system_name, rng: random.Random = random,
        image_rng: Optional[random.Random] = None,
    ) -> List[Star]:
        """Generate stars using default random probabilities."""
        from game.strategy.data.star_generation_config import get_star_generation_config
        cfg = get_star_generation_config()

        stars = []

        # 1. Determine Count from probability thresholds
        roll = rng.random()
        count = cfg.system_default_count
        for entry in cfg.system_count_thresholds:
            if roll < entry["cumulative"]:
                count = entry["count"]
                break

        # 2. Generate Primary
        p_mass = self._generate_mass(is_primary=True, rng=rng)
        p_type, p_mass, p_rad, p_temp, p_lum, p_col = self._determine_type_and_radius(p_mass, rng=rng)
        p_hex = self._map_solar_radius_to_hex_radius(p_rad, p_type)
        p_spec = self._generate_spectrum(p_temp, p_lum, rng=rng)

        primary = Star(
            name=f"{system_name} A",
            mass=p_mass,
            radius_hexes=p_hex,
            temperature=p_temp,
            luminosity=p_lum,
            spectrum=p_spec,
            star_type=p_type,
            color=p_col,
            age=rng.uniform(cfg.age_min, cfg.age_max) * cfg.age_unit,
            location=HexCoord(0, 0),
            image_id=self._get_image_id(p_type, image_rng=image_rng),
        )
        stars.append(primary)

        # 3. Generate Companions
        companions = self._generate_companions(
            count=count - 1,
            primary=primary,
            system_name=system_name,
            mass_fn=lambda _i: self._generate_mass(is_primary=True, rng=rng),
            rng=rng,
            image_rng=image_rng,
        )
        stars.extend(companions)

        return stars

    def _generate_mass_constrained(
        self, mass_min, mass_max, rng: random.Random = random
    ) -> float:
        """Generate star mass within specified solar-mass constraints."""
        # Use log-normal distribution centered in the constraint range
        log_min = math.log(mass_min)
        log_max = math.log(mass_max)
        log_center = (log_min + log_max) / 2
        log_sigma = (log_max - log_min) / 4  # ~95% within range

        for _ in range(100):  # Max attempts
            mass = rng.lognormvariate(log_center, max(0.1, log_sigma))
            if mass_min <= mass <= mass_max:
                return mass

        # Fallback to uniform in log space
        return math.exp(rng.uniform(log_min, log_max))
