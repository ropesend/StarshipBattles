"""
Planet generation system for star systems.

Generates planetary bodies with realistic physical properties including
mass distribution, moons, atmospheres, and resources.
"""
import logging
import random
import math
from typing import List, Dict

logger = logging.getLogger(__name__)

from game.strategy.data.planet import Planet
from game.strategy.generation.planet_image_registry import PlanetImageRegistry
from game.core.hex_math import HexCoord, hex_ring, hex_circle_filled
from game.strategy.data.physics import calculate_incident_radiation
from game.strategy.data.stars import Star
from game.strategy.data.planet_physics import (
    MASS_CERES, MASS_JUPITER,
    calculate_radius_density_from_mass, calculate_escape_velocity,
    calculate_surface_gravity, calculate_surface_area, calculate_blackbody_temperature
)
from game.strategy.data.planet_atmosphere import generate_atmosphere
from game.strategy.data.planet_naming import assign_body_names
from game.strategy.data.planet_gen_surface import (
    determine_planet_type,
    generate_resources,
    generate_surface_flags,
)


class PlanetGenerator:
    """Generator for creating planetary bodies within star systems."""

    def __init__(self, image_registry: PlanetImageRegistry):
        """Initialize PlanetGenerator with dependencies.

        Args:
            image_registry: Registry for assigning planet images based on type.
        """
        self._image_registry = image_registry

    def generate_system_bodies(
        self,
        system_name: str,
        stars: List[Star],
        blueprint: Dict = None
    ) -> List[Planet]:
        """
        Generate all planetary bodies for a system.

        Args:
            system_name: Name of the star system
            stars: List of stars in the system
            blueprint: Optional blueprint dict with planet_count, planet_mass constraints

        Returns:
            List of Planet objects with assigned names
        """
        bodies = []

        # Determine orbital slots and their masses using blueprint constraints
        occupied_slots = self._generate_orbital_slots(stars, blueprint)

        # Generate moons for each primary body
        # If blueprint specifies max_planets, limit total body count
        if blueprint:
            planet_count_spec = blueprint.get("planet_count", {})
            if isinstance(planet_count_spec, dict):
                max_planets = planet_count_spec.get("max", 20)
            elif isinstance(planet_count_spec, int):
                max_planets = planet_count_spec
            else:
                max_planets = 20
            # Only generate moons if we have room for more bodies
            current_count = sum(len(masses) for masses in occupied_slots.values())
            if current_count < max_planets:
                self._generate_moons(occupied_slots, max_total=max_planets)
        else:
            self._generate_moons(occupied_slots)

        # Create Planet objects for each mass
        bodies = self._create_planet_objects(occupied_slots, stars)

        # Assign names based on distance and mass
        assign_body_names(bodies, system_name)

        return bodies

    def _generate_orbital_slots(
        self,
        stars: List[Star],
        blueprint: Dict = None
    ) -> Dict[HexCoord, List[float]]:
        """
        Generate primary orbital slots with masses.

        Args:
            stars: List of stars in the system
            blueprint: Optional blueprint dict with planet_count, planet_mass,
                      orbital_spacing, and orbital_zones constraints

        Returns dict mapping location to list of masses at that location.
        """
        from game.strategy.data.orbital_generation_config import get_orbital_generation_config
        cfg = get_orbital_generation_config()

        primary = stars[0]
        safe_start = primary.radius_hexes + cfg.safe_start_offset
        max_dist = cfg.max_orbital_distance

        # Get planet count from blueprint or use default
        if blueprint:
            planet_count_spec = blueprint.get("planet_count", {})
            if isinstance(planet_count_spec, int):
                primary_count = planet_count_spec
            elif isinstance(planet_count_spec, dict):
                min_count = planet_count_spec.get("min", cfg.default_planet_min)
                max_count = planet_count_spec.get("max", cfg.default_planet_max)
                primary_count = random.randint(min_count, max_count)
            else:
                primary_count = random.randint(cfg.default_planet_min, cfg.default_planet_max)

            # Apply orbital spacing factor if specified
            spacing_spec = blueprint.get("orbital_spacing", {})
            if isinstance(spacing_spec, dict):
                spacing_factor = spacing_spec.get("factor", 1.0)
                max_dist = int(max_dist * spacing_factor)
                max_dist = max(safe_start + 2, max_dist)
        else:
            primary_count = random.randint(cfg.default_planet_min, cfg.default_planet_max)

        # Handle 0 planet case
        if primary_count == 0:
            return {}

        # Collect exclusion zones for all stars (occupied hexes + buffer)
        occupied_locations = self._collect_star_exclusion_zones(stars)
        occupied_slots = {}

        # Get mass constraints from blueprint
        mass_spec = blueprint.get("planet_mass", {}) if blueprint else {}
        mass_bias = mass_spec.get("bias", None)
        mass_min = mass_spec.get("min", MASS_CERES)
        mass_max = mass_spec.get("max", MASS_JUPITER)

        # Check if hot zone is required (hot_jupiter blueprint)
        orbital_zones = blueprint.get("orbital_zones", {}) if blueprint else {}
        hot_required = orbital_zones.get("hot_required", False)
        hot_zone_placed = False

        for i in range(primary_count):
            for attempt in range(cfg.max_placement_attempts):
                if hot_required and not hot_zone_placed and i == 0:
                    dist = random.randint(safe_start, safe_start + 1)
                    dist = max(cfg.hot_jupiter_orbit_min, min(dist, cfg.hot_jupiter_orbit_max))
                else:
                    mode = safe_start + (max_dist - safe_start) * cfg.orbital_distribution_mode
                    dist = int(random.triangular(safe_start, max_dist, mode))

                ring_coords = hex_ring(dist)
                if not ring_coords:
                    continue
                loc = random.choice(ring_coords)
                if loc not in occupied_locations:
                    occupied_locations.add(loc)

                    if hot_required and not hot_zone_placed and i == 0:
                        hot_mass = 10 ** random.uniform(
                            cfg.hot_jupiter_log_mass_min, cfg.hot_jupiter_log_mass_max
                        )
                        occupied_slots[loc] = [hot_mass]
                        hot_zone_placed = True
                    else:
                        mass = self._generate_mass_constrained(mass_min, mass_max, mass_bias)
                        occupied_slots[loc] = [mass]
                    break

        return occupied_slots

    def _collect_star_exclusion_zones(self, stars: List[Star]) -> set:
        """Collect hexes that planets cannot occupy due to star presence.

        For each secondary star (stars[1:]), excludes the star's occupied hexes
        plus a buffer zone of 2 hexes around it, matching the primary star's
        safe_start convention (radius_hexes + 2).

        Args:
            stars: List of stars in the system.

        Returns:
            Set of HexCoord that planets must not occupy.
        """
        excluded = set()
        for star in stars[1:]:
            buffer_radius = star.radius_hexes + 1  # +1 because hex_circle_filled is inclusive
            excluded.update(hex_circle_filled(star.location, buffer_radius))
        return excluded

    def _generate_mass_constrained(
        self,
        mass_min: float,
        mass_max: float,
        bias: str = None
    ) -> float:
        """
        Generate planet mass with constraints and optional bias.

        Args:
            mass_min: Minimum mass in kg
            mass_max: Maximum mass in kg
            bias: Optional bias - "small" for rocky planets, "large" for gas giants

        Returns:
            Mass in kg within constraints
        """
        from game.strategy.data.orbital_generation_config import get_orbital_generation_config
        cfg = get_orbital_generation_config()

        if bias == "small":
            log_mu = cfg.small_bias_mu
            log_sigma = cfg.small_bias_sigma
        elif bias == "large":
            log_mu = cfg.large_bias_mu
            log_sigma = cfg.large_bias_sigma
        else:
            log_mu = cfg.default_mu
            log_sigma = cfg.default_sigma

        log_min = math.log10(mass_min)
        log_max = math.log10(mass_max)

        for _ in range(cfg.mass_max_iterations):
            log_val = random.gauss(log_mu, log_sigma)
            if log_min <= log_val <= log_max:
                return 10 ** log_val

        # Fallback: uniform in log space within constraints
        return 10 ** random.uniform(log_min, log_max)

    def _generate_moons(
        self,
        occupied_slots: Dict[HexCoord, List[float]],
        max_total: int = None
    ) -> None:
        """
        Generate moons/co-orbitals for each primary body.

        Larger primaries have higher chance of additional bodies.
        Moon mass is normally distributed around 10% of primary mass.

        Args:
            occupied_slots: Dict mapping location to list of masses
            max_total: Optional maximum total body count across all slots
        """
        for loc, masses in occupied_slots.items():
            primary_mass = masses[0]

            # Calculate chance based on primary mass (log interpolation)
            chance = self._calculate_moon_chance(primary_mass)

            # Keep rolling for additional moons
            from game.strategy.data.orbital_generation_config import get_orbital_generation_config
            cfg_moons = get_orbital_generation_config()
            while random.random() < chance:
                if len(masses) > cfg_moons.max_moons_per_body:
                    break

                # Check max_total constraint
                if max_total is not None:
                    current_total = sum(len(m) for m in occupied_slots.values())
                    if current_total >= max_total:
                        return  # Stop all moon generation

                moon_mass = self._generate_moon_mass(primary_mass)
                masses.append(moon_mass)

    def _calculate_moon_chance(self, primary_mass: float) -> float:
        """
        Calculate per-roll probability of adding another moon.

        Each moon is an independent roll; the chain continues until a roll
        fails.  Larger bodies get much higher chances, producing rich moon
        systems around gas giants while small bodies rarely have any.

        Targets (geometric distribution, chance^N for N+ moons):
          Jupiter+ (>1e27): 88% -> ~46% have 6+, ~88% have 1+
          Neptune  (~1e26): 75% -> ~18% have 6+, ~75% have 1+
          Super-Earth:      55% -> ~3% have 6+
          Earth:            35% -> 35% have 1+
          Mars:             15% -> 15% have 1+
          Ceres:             2% -> rarely any
        """
        from game.strategy.data.orbital_generation_config import get_orbital_generation_config
        cfg = get_orbital_generation_config()

        log_m = math.log10(primary_mass)

        if log_m >= cfg.jupiter_threshold_log:
            chance = cfg.jupiter_chance
        elif log_m >= cfg.earth_threshold_log:
            t = (log_m - cfg.earth_threshold_log) / (cfg.jupiter_threshold_log - cfg.earth_threshold_log)
            chance = cfg.earth_chance + t * (cfg.jupiter_chance - cfg.earth_chance)
        elif log_m >= cfg.ceres_threshold_log:
            t = (log_m - cfg.ceres_threshold_log) / (cfg.earth_threshold_log - cfg.ceres_threshold_log)
            chance = cfg.ceres_chance + t * (cfg.earth_chance - cfg.ceres_chance)
        else:
            chance = cfg.ceres_chance

        return max(0.0, min(cfg.max_chance_cap, chance))

    def _generate_moon_mass(self, primary_mass: float) -> float:
        """
        Generate moon mass (log-uniform from 0.001% to 5% of primary).

        Real moons are tiny relative to their parent: Ganymede is 0.008%
        of Jupiter's mass. Log-uniform distribution gives most moons at
        the small end with rare larger ones.
        """
        from game.strategy.data.orbital_generation_config import get_orbital_generation_config
        cfg = get_orbital_generation_config()

        log_min = math.log10(primary_mass * cfg.mass_ratio_min)
        log_max = math.log10(primary_mass * cfg.mass_ratio_max)

        moon_mass = 10 ** random.uniform(log_min, log_max)

        # Floor at dwarf planet size
        return max(moon_mass, MASS_CERES)

    def _create_planet_objects(
        self,
        occupied_slots: Dict[HexCoord, List[float]],
        stars: List[Star]
    ) -> List[Planet]:
        """
        Create Planet objects from mass distributions.
        """
        bodies = []

        for loc, masses in occupied_slots.items():
            masses.sort(reverse=True)
            orbit_dist = max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))

            # Calculate radiation and temperature for this location
            incident_spec = calculate_incident_radiation(loc, stars)
            total_flux = incident_spec.get_total_output()
            base_temp = calculate_blackbody_temperature(total_flux)

            for mass in masses:
                planet = self._create_single_planet(
                    loc, orbit_dist, mass, base_temp, total_flux
                )
                bodies.append(planet)

        return bodies

    def _create_single_planet(
        self,
        loc: HexCoord,
        orbit_dist: int,
        mass: float,
        base_temp: float,
        total_flux: float
    ) -> Planet:
        """
        Create a single Planet object with all physical properties.
        """
        from game.strategy.data.planet_physics import validate_planet_parameters

        # Physical properties
        radius, density = calculate_radius_density_from_mass(mass)
        gravity = calculate_surface_gravity(mass, radius)
        surface_area = calculate_surface_area(radius)

        # Validate physical parameters
        warnings = validate_planet_parameters(mass, radius, density)
        for warning in warnings:
            logger.warning(f"Planet at orbit {orbit_dist}: {warning}")

        # Atmosphere
        escape_vel = calculate_escape_velocity(mass, radius)
        atmosphere, pressure, final_temp = generate_atmosphere(
            mass, escape_vel, base_temp, total_flux
        )

        # Surface conditions
        water, activity, mag_field = generate_surface_flags(mass, final_temp)

        # Classification
        p_type = determine_planet_type(
            mass, final_temp, pressure, water, atmosphere, activity
        )

        # Assign persistent image from registry
        image_id = self._image_registry.get_random_image(p_type)
        image_rotation = self._image_registry.get_random_rotation()

        return Planet(
            name="TEMP",  # Assigned later by naming pass
            location=loc,
            orbit_distance=orbit_dist,
            mass=mass,
            radius=radius,
            surface_area=surface_area,
            density=density,
            surface_gravity=gravity,
            surface_pressure=pressure,
            surface_temperature=final_temp,
            atmosphere=atmosphere,
            planet_type=p_type,
            surface_water=water,
            tectonic_activity=activity,
            magnetic_field=mag_field,
            deposits=generate_resources(mass, p_type),
            image_id=image_id,
            image_rotation=image_rotation
        )

    # PROJ-459 Phase 2 (F-A-009): the surface / classification / resource
    # cluster moved to ``planet_gen_surface.py`` as module-level pure
    # functions. See decisions.md 2026-05-19. The three functions are
    # called by ``_create_single_planet`` below.

    # ``_determine_type`` and ``_generate_resources`` extracted to
    # ``planet_gen_surface.py`` as module-level pure functions.
